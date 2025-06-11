# File: src/main.py
import sys
import os
import csv

from datetime import datetime
from src.pipeline.pipeline_controller import run_pipeline
import logging
import google.cloud.logging
from google.cloud.logging.handlers import StructuredLogHandler

# 1) Basic console/file logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger()  # grab the root logger

# 2) Cloud logging setup (sync)
client = google.cloud.logging.Client()
handler = StructuredLogHandler()            # or StructuredLogHandler(client=client)
logger.addHandler(handler)


# Output directories and filenames
OUTPUT_DIR = os.path.join("data", "output")
DETAILS_SUBDIR = "details"
CSV_FILENAMES = {
    "invoice":          "Invoice-List.csv",
    "receipt":          "Receipt-List.csv",
    "w2":               "W2-List.csv",
    "seller-statement": "Seller-Statement.csv",
}

# Summary fields per document type
SUMMARY_FIELDS = {
    "invoice":          ["invoice_number", "total_amount"],
    "receipt":          ["merchant_name", "total_amount"],
    "w2":               ["WagesTipsOtherCompensation", "SocialSecurityTaxWithheld"],
    "seller-statement": ["Gross Amount Due to Seller", "Net to Seller"],
}


def write_detail_csv(rows, document_name, doc_type):
    """
    Write detailed extraction rows to a per-document CSV under data/output/<doc_type>/details/ with timestamp.
    Returns the filepath.
    """
    detail_dir = os.path.join(OUTPUT_DIR, doc_type, DETAILS_SUBDIR)
    os.makedirs(detail_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{ts}_{document_name}_{doc_type}.csv"
    path = os.path.join(detail_dir, filename)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["field", "value", "page", "line_number"])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "field":       r.get("field", ""),
                "value":       r.get("value", ""),
                "page":        r.get("page", 0),
                "line_number": r.get("line_number", ""),
            })
    return path


def write_summary_csv(detail_path, document_name, doc_type, rows):
    """
    Append a summary row for this document into the per-type CSV list file.
    Columns: filename, insert_timestamp, <summary fields...>, detail_link
    """
    summary_file = os.path.join(OUTPUT_DIR, CSV_FILENAMES[doc_type])
    os.makedirs(os.path.dirname(summary_file), exist_ok=True)
    write_header = not os.path.exists(summary_file)
    ts = datetime.utcnow().isoformat()

    # Build summary data
    summary = {
        "filename":         document_name,
        "insert_timestamp": ts,
    }
    for key in SUMMARY_FIELDS.get(doc_type, []):
        val = ""
        for r in rows:
            if r.get("field") == key:
                val = r.get("value", "")
                break
        summary[key] = val
    # clickable file link
    abs_path = os.path.abspath(detail_path)
    summary["detail_link"] = f"file://{abs_path}"

    with open(summary_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ["filename", "insert_timestamp"] + SUMMARY_FIELDS.get(doc_type, []) + ["detail_link"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(summary)

    return summary_file


def main():
    if len(sys.argv) != 3:
        print("Usage: python -m src.main <local-pdf-path> <doc-type>")
        sys.exit(1)

    local_path    = sys.argv[1]
    doc_type      = sys.argv[2].lower().strip()
    document_name = os.path.splitext(os.path.basename(local_path))[0]

    try:
        rows = run_pipeline(local_path, doc_type)
        logger.info(f"Parsed {len(rows)} rows for {document_name} ({doc_type})")

        detail_path = write_detail_csv(rows, document_name, doc_type)
        logger.info(f"Detail CSV written: {detail_path}")

        summary_path = write_summary_csv(detail_path, document_name, doc_type, rows)
        logger.info(f"Summary CSV updated: {summary_path}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()