# config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (for local development)
load_dotenv()

# --- GCP Project Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id") # Replace with your project ID or set env var
GCP_REGION = os.getenv("GCP_REGION", "us") # Choose your preferred region

# --- Cloud Storage Buckets ---
GCS_RAW_DOCUMENTS_BUCKET = os.getenv("GCS_RAW_DOCUMENTS_BUCKET", f"gs://{GCP_PROJECT_ID}-iaa-raw-docs")
GCS_PROCESSED_DOCUMENTS_BUCKET = os.getenv("GCS_PROCESSED_DOCUMENTS_BUCKET", f"gs://{GCP_PROJECT_ID}-iaa-processed-docs")
GCS_MODEL_ARTIFACTS_BUCKET = os.getenv("GCS_MODEL_ARTIFACTS_BUCKET", f"gs://{GCP_PROJECT_ID}-iaa-model-artifacts")

# --- BigQuery Configuration ---
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "accounting_data")
BQ_TRANSACTIONS_TABLE = os.getenv("BQ_TRANSACTIONS_TABLE", "transactions")
BQ_RECONCILIATION_TABLE = os.getenv("BQ_RECONCILIATION_TABLE", "reconciliation_status")
BQ_ANOMALY_TABLE = os.getenv("BQ_ANOMALY_TABLE", "anomalies")

# --- Document AI Processors ---
DOCUMENT_AI_INVOICE_PROCESSOR_ID = os.getenv("DOCUMENT_AI_INVOICE_PROCESSOR_ID", "your-invoice-processor-id")
DOCUMENT_AI_RECEIPT_PROCESSOR_ID = os.getenv("DOCUMENT_AI_RECEIPT_PROCESSOR_ID", "your-receipt-processor-id")
# You'll need to create these processors in Google Cloud Console Document AI service

# --- Vertex AI Endpoints ---
VERTEX_AI_CATEGORIZATION_ENDPOINT_ID = os.getenv("VERTEX_AI_CATEGORIZATION_ENDPOINT_ID", "your-cat-endpoint-id")
VERTEX_AI_ANOMALY_ENDPOINT_ID = os.getenv("VERTEX_AI_ANOMALY_ENDPOINT_ID", "your-anomaly-endpoint-id")

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

print(f"[DEBUG] GCP_REGION from env = {os.getenv('GCP_REGION')}")
print(f"[DEBUG] GCP_REGION in code = {GCP_REGION}")

# Define paths relative to the project root (optional, for local development)
# This is less common for cloud-native apps but useful for managing local data/models
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(PROJECT_ROOT, "data")
# MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
