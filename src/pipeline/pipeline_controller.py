# File: src/pipeline/pipeline_controller.py
import os
import re
import logging
from datetime import datetime

from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineController:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location   = os.getenv("GCP_REGION", "us")
        self.raw_bucket = os.getenv("GCS_RAW_DOCUMENTS_BUCKET")

        self.processor_map = {
            "invoice":           os.getenv("DOCUMENT_AI_INVOICE_PROCESSOR_ID"),
            "receipt":           os.getenv("DOCUMENT_AI_RECEIPT_PROCESSOR_ID"),
            "w2":                os.getenv("DOCUMENT_AI_W2_PROCESSOR_ID"),
            "seller-statement":  os.getenv("DOCUMENT_AI_SELLER_STATEMENT_PROCESSOR_ID"),
        }
        self.processor_name_map = {}
        for dt, pid in self.processor_map.items():
            if not pid or pid.startswith("your-"):
                raise RuntimeError(f"Processor ID for '{dt}' is not set or invalid.")
            self.processor_name_map[dt] = (
                f"projects/{self.project_id}"
                f"/locations/{self.location}"
                f"/processors/{pid}"
            )
            logger.info(f"{dt.capitalize()} Processor: {self.processor_name_map[dt]}")

        self.storage_client = storage.Client()
        self.docai_client   = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
        )

    def _get_text(self, text_anchor, full_text: str) -> str:
        return "".join(
            full_text[s.start_index:s.end_index] for s in text_anchor.text_segments
        )

    def _clean_value(self, text: str) -> str:
        text = text.replace("☐", "✓")
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text).strip()
        cleaned = re.sub(r"[^0-9,\.\-]", "", text)
        # remove commas in numbers
        numeric = cleaned.replace(",", "")
        if re.match(r"^-?\d+(?:\.\d+)?$", numeric):
            return numeric
        return cleaned

    def run(self, local_path: str, doc_type: str) -> list:
        dt = doc_type.lower().strip()
        if dt == "sellers-statement":
            dt = "seller-statement"
        if dt not in self.processor_name_map:
            raise ValueError(f"Unsupported doc_type: {doc_type}")
        return self._process_generic(local_path, self.processor_name_map[dt], dt)

    def _process_generic(self, local_path: str, processor_name: str, category: str) -> list:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        blob_name = f"raw_documents/{category}/{ts}_{os.path.basename(local_path)}"
        bucket    = self.storage_client.bucket(self.raw_bucket)
        bucket.blob(blob_name).upload_from_filename(local_path)
        logger.info(f"Uploaded file → gs://{self.raw_bucket}/{blob_name}")

        with open(local_path, "rb") as f:
            content = f.read()
        request = documentai.ProcessRequest(
            name=processor_name,
            raw_document=documentai.RawDocument(content=content, mime_type="application/pdf")
        )
        result = self.docai_client.process_document(request=request)
        logger.info(f"Document AI inline for '{category}' succeeded.")

        document_name = os.path.splitext(os.path.basename(local_path))[0]
        full_text     = result.document.text or ""
        rows          = []

        if category == "seller-statement":
            for page in result.document.pages:
                for ff in page.form_fields:
                    raw_name = self._get_text(ff.field_name.text_anchor, full_text).strip()
                    m = re.match(r"^(\d+)\.\s*(.*)$", raw_name)
                    if m:
                        ln, fname = m.group(1), m.group(2)
                    else:
                        ln, fname = "", raw_name
                    rawv = self._get_text(ff.field_value.text_anchor, full_text).strip()
                    val  = self._clean_value(rawv)
                    rows.append({
                        "document_name": document_name,
                        "doc_type":      category,
                        "field":         fname,
                        "value":         val,
                        "page":          page.page_number,
                        "line_number":   ln,
                    })
                for table in page.tables:
                    headers = [
                        self._get_text(c.layout.text_anchor, full_text).strip()
                        for c in table.header_rows[0].cells
                    ]
                    for body in table.body_rows:
                        cells = [
                            self._get_text(c.layout.text_anchor, full_text).strip()
                            for c in body.cells
                        ]
                        entry = dict(zip(headers, cells))
                        for h,v in entry.items():
                            rows.append({
                                "document_name": document_name,
                                "doc_type":      category,
                                "field":         h,
                                "value":         self._clean_value(v),
                                "page":          page.page_number,
                                "line_number":   ""
                            })
        elif category == "receipt":
            # Specialized receipt fields
            if hasattr(result, 'receipts') and result.receipts:
                rec = result.receipts[0]
                # Merchant info
                for key in ['merchant_name', 'merchant_address', 'merchant_phone_number', 'transaction_date', 'total_amount']:
                    val = getattr(rec, key, None)
                    if val:
                        rows.append({
                            "document_name": document_name,
                            "doc_type":      category,
                            "field":         key,
                            "value":         self._clean_value(str(val)),
                            "page":          0,
                            "line_number":   ""
                        })
                for li in rec.line_items:
                    desc = li.description or ""
                    price = str(li.price)
                    rows.append({
                        "document_name": document_name,
                        "doc_type":      category,
                        "field":         "line_item",
                        "value":         self._clean_value(f"{desc}: {price}"),
                        "page":          0,
                        "line_number":   ""
                    })
        else:
            # Generic entity extraction for invoice, w2
            for ent in result.document.entities:
                rows.append({
                    "document_name": document_name,
                    "doc_type":      category,
                    "field":         ent.type_,
                    "value":         self._clean_value(ent.mention_text),
                    "page":          ent.page_anchor.page_refs[0].page,
                    "line_number":   ""
                })
        return rows

# Exposed entrypoint for src/main.py

def run_pipeline(local_path: str, doc_type: str) -> list:
    controller = PipelineController()
    return controller.run(local_path, doc_type)