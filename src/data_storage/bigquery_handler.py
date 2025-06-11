# src/data_storage/bigquery_handler.py
from google.cloud import bigquery

from config.settings import (
    BQ_DATASET_ID,
    GCP_PROJECT_ID,
)
from src.utils.gcp_auth import get_bigquery_client
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_dataset_if_not_exists():
    """Creates the BigQuery dataset if it doesn't exist."""
    client = get_bigquery_client()
    dataset_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}"
    dataset = bigquery.Dataset(dataset_id)
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        logger.info(f"Dataset {dataset.project}.{dataset.dataset_id} created.")
    except Exception as e:
        if "Already Exists" in str(e):
            logger.info(f"Dataset {dataset_id} already exists.")
        else:
            logger.error(f"Error creating dataset {dataset_id}: {e}")
            raise


def load_data_to_bigquery(data: list, table_id: str, schema: list = None):
    """Loads a list of dictionaries into a BigQuery table.
    If the table does not exist and a schema is provided, it will create the table.
    """
    if not data:
        logger.warning(f"No data to load to BigQuery table {table_id}.")
        return

    client = get_bigquery_client()
    table_ref = client.dataset(BQ_DATASET_ID).table(table_id)

    try:
        client.get_table(table_ref)  # Check if table exists
    except Exception as e:
        if "Not found" in str(e) and schema:
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            logger.info(f"Table {table_id} created with provided schema.")
        else:
            logger.error(f"Error getting table {table_id}: {e}")
            raise

    # Transform data for BigQuery, especially BIGNUMERIC which requires string
    # and ensuring dates are in 'YYYY-MM-DD' format if not already
    rows_to_insert = []
    for row in data:
        processed_row = row.copy()
        if "amount" in processed_row and processed_row["amount"] is not None:
            processed_row["amount"] = str(
                processed_row["amount"]
            )  # BIGNUMERIC expects string
        if (
            "transaction_date" in processed_row
            and processed_row["transaction_date"] is not None
        ):
            # Ensure date is a string in 'YYYY-MM-DD' format
            if isinstance(processed_row["transaction_date"], datetime.date):
                processed_row["transaction_date"] = processed_row[
                    "transaction_date"
                ].isoformat()
            elif not isinstance(processed_row["transaction_date"], str):
                logger.warning(
                    f"Unexpected date type for transaction_date: {type(processed_row['transaction_date'])}"
                )
                processed_row["transaction_date"] = None  # Or attempt conversion

        rows_to_insert.append(processed_row)

    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        logger.error(
            f"Errors occurred during BigQuery insert for table {table_id}: {errors}"
        )
        raise ValueError(f"BigQuery insert errors: {errors}")
    else:
        logger.info(f"{len(rows_to_insert)} rows loaded to BigQuery table {table_id}.")


# --- Refined Schema for TRANSACTIONS_TABLE ---
# This schema aligns with the parsed data from Document AI
TRANSACTIONS_SCHEMA = [
    bigquery.SchemaField(
        "document_id",
        "STRING",
        mode="REQUIRED",
        description="Unique ID generated for the processed document.",
    ),
    bigquery.SchemaField(
        "original_file_path",
        "STRING",
        description="GCS URI of the original document file.",
    ),
    bigquery.SchemaField(
        "document_type",
        "STRING",
        description="Type of document (e.g., 'invoice', 'receipt').",
    ),
    bigquery.SchemaField(
        "vendor_name", "STRING", description="Name of the vendor/merchant."
    ),
    bigquery.SchemaField(
        "total_amount",
        "BIGNUMERIC",
        description="Total amount extracted from the document.",
    ),
    bigquery.SchemaField(
        "currency",
        "STRING",
        description="Currency of the transaction (e.g., 'USD', 'EUR').",
    ),
    bigquery.SchemaField(
        "transaction_date", "DATE", description="Date of the transaction."
    ),
    bigquery.SchemaField(
        "invoice_id", "STRING", description="Invoice number (if applicable)."
    ),
    bigquery.SchemaField(
        "description", "STRING", description="A general description of the transaction."
    ),
    bigquery.SchemaField(
        "categorization_ai_suggested",
        "STRING",
        description="AI-suggested accounting category.",
    ),
    bigquery.SchemaField(
        "categorization_user_confirmed",
        "STRING",
        description="User-confirmed accounting category.",
    ),
    bigquery.SchemaField(
        "is_anomaly",
        "BOOLEAN",
        description="Flag indicating if the transaction is detected as an anomaly.",
    ),
    bigquery.SchemaField(
        "anomaly_score", "FLOAT", description="Confidence score for anomaly detection."
    ),
    bigquery.SchemaField(
        "timestamp_processed",
        "TIMESTAMP",
        description="Timestamp when the document was processed by IAA.",
    ),
]
