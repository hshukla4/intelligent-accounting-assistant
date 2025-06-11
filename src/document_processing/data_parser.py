# src/document_processing/data_parser.py
from google.cloud.documentai_v1beta3 import Document
import uuid
import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)

def _get_entity_value(document: Document, entity_type: str, default_value=None, return_type=str):
    """Helper to extract value from a Document AI entity by type."""
    for entity in document.entities:
        if entity.type == entity_type:
            value_text = entity.mention_text
            if entity_type in ["total_amount", "net_amount", "tax_amount", "amount"]:
                try:
                    # Document AI often gives currency symbol or spaces, clean for float
                    value_text = value_text.replace("$", "").replace("€", "").replace(",", "").strip()
                    return return_type(value_text)
                except ValueError:
                    logger.warning(f"Could not convert {entity_type} '{value_text}' to {return_type}.")
                    return default_value
            if entity_type == "date":
                # Prioritize normalized_value if available and parseable as date
                if entity.normalized_value and entity.normalized_value.date:
                    try:
                        return datetime.date.fromisoformat(entity.normalized_value.date)
                    except ValueError:
                        pass # Fallback to mention_text
                # Try to parse mention_text as a date
                try:
                    return datetime.datetime.strptime(value_text, "%Y-%m-%d").date() # Common format
                except ValueError:
                    try:
                        return datetime.datetime.strptime(value_text, "%m/%d/%Y").date() # Another common format
                    except ValueError:
                        pass # Keep trying or fallback
            return return_type(value_text)
    return default_value

def parse_document_ai_output(document: Document, original_gcs_uri: str, doc_type: str) -> dict:
    """
    Parses the Document AI Document object into a structured dictionary for BigQuery.
    This now extracts more specific fields.
    """
    data = {
        "document_id": str(uuid.uuid4()),
        "original_file_path": original_gcs_uri,
        "document_type": doc_type.lower(),
        "vendor_name": _get_entity_value(document, "vendor_name"),
        "total_amount": _get_entity_value(document, "total_amount", return_type=float),
        "currency": _get_entity_value(document, "currency"), # Often attached to total_amount entity
        "transaction_date": _get_entity_value(document, "date", return_type=datetime.date),
        "invoice_id": _get_entity_value(document, "invoice_id"),
        "description": _get_entity_value(document, "description") or _get_entity_value(document, "vendor_name") or "General Transaction",
        "categorization_ai_suggested": None,
        "categorization_user_confirmed": None,
        "is_anomaly": False,
        "anomaly_score": None,
        "timestamp_processed": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    # If currency wasn't extracted with total_amount, try to find it elsewhere
    if not data["currency"]:
        # Look for a top-level currency entity if available
        data["currency"] = _get_entity_value(document, "currency")
        # Fallback to common symbols on the page text
        if not data["currency"] and data["total_amount"] is not None:
            if "$" in document.text: data["currency"] = "USD"
            elif "€" in document.text: data["currency"] = "EUR"
            elif "£" in document.text: data["currency"] = "GBP"

    # Post-process description if still generic
    if data["description"] == "General Transaction":
        data["description"] = f"{data['document_type'].capitalize()} from {data['vendor_name'] or 'Unknown Vendor'}"
        if data["total_amount"]:
            data["description"] += f" for {data['total_amount']}"

    return data