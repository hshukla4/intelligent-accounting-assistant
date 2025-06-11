import os
import sys
import json
import logging
from datetime import datetime

from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineController:
    def __init__(self):
        # --- Load config from ENV ---
        self.project_id       = os.getenv("GCP_PROJECT_ID")
        self.location         = os.getenv("GCP_REGION", "us")
        self.raw_bucket       = os.getenv("GCS_RAW_DOCUMENTS_BUCKET")
        self.processed_bucket = os.getenv("GCS_PROCESSED_DOCUMENTS_BUCKET")
        w2_id = os.getenv("DOCUMENT_AI_W2_PROCESSOR_ID")
        if not w2_id:
            raise RuntimeError("DOCUMENT_AI_W2_PROCESSOR_ID is not set in environment")
        # Full resource path for your prebuilt W-2 parser
        self.w2_processor_name = (
            f"projects/{self.project_id}"
            f"/locations/{self.location}"
            f"/processors/{w2_id}"
        )
        logger.info(f"W-2 Processor Name: {self.w2_processor_name}")

        # --- Initialize clients ---
        self.storage_client = storage.Client()
        self.docai_client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
        )

    def run(self, local_path: str, doc_type: str):
        """
        Entry point: select processor based on doc_type and return parsed output.
        """
        if doc_type.lower() == "w2":
            return self._process_w2(local_path)
        else:
            raise ValueError(f"Unsupported doc_type: {doc_type}")

    def _process_w2(self, local_path: str) -> dict:
        """
        Process a W2 form: upload to GCS, run Document AI, parse entities, and return a dict.
        """
        # 1) Upload PDF to GCS
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        blob_name = f"raw_documents/w2/{timestamp}_{os.path.basename(local_path)}"
        bucket = self.storage_client.bucket(self.raw_bucket)
        blob   = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)
        gcs_input_uri = f"gs://{self.raw_bucket}/{blob_name}"
        logger.info(f"Uploaded PDF → {gcs_input_uri}")

        # 2) Call Document AI inline
        with open(local_path, "rb") as pdf_file:
            content = pdf_file.read()

        request = documentai.ProcessRequest(
            name=self.w2_processor_name,
            raw_document=documentai.RawDocument(
                content=content,
                mime_type="application/pdf"
            )
        )
        result = self.docai_client.process_document(request=request)
        logger.info("Document AI inline processing succeeded.")

        # 3) Parse entities into a structured dict
        output = {}
        for ent in result.document.entities:
            field = ent.type_
            entry = {
                "value": ent.mention_text,
                "page": ent.page_anchor.page_refs[0].page
            }
            output.setdefault(field, []).append(entry)
            logger.info(f"Field: {field} | Value: {entry['value']} | Page: {entry['page']}")
        return output

# Exposed entrypoint for src/main.py

def run_pipeline(local_path: str, doc_type: str) -> dict:
    controller = PipelineController()
    return controller.run(local_path, doc_type)
