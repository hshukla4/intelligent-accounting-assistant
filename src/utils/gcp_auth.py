# src/utils/gcp_auth.py

from config.settings import GCP_PROJECT_ID, GCP_REGION
from google.cloud import storage, bigquery, documentai_v1beta3 as documentai, aiplatform
from google.api_core.client_options import ClientOptions
from config.settings import GCP_PROJECT_ID, GCP_REGION # <--- Ensure GCP_REGION is imported
from src.utils.logger import get_logger

logger = get_logger(__name__)

    
def get_storage_client():
    try:
        return storage.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        logger.error(f"Error getting Cloud Storage client: {e}")
        raise

def get_bigquery_client():
    try:
        return bigquery.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        logger.error(f"Error getting BigQuery client: {e}")
        raise

def get_document_ai_client():
    try:
        return documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=f"{GCP_REGION}-documentai.googleapis.com")
        )
    except Exception as e:
        logger.error(f"Error getting Document AI client: {e}")
        raise

def get_aiplatform_endpoint_client():
    """Client for calling deployed Vertex AI Endpoints."""
    try:
        return aiplatform.gapic.PredictionServiceClient(client_options={"api_endpoint": f"{GCP_REGION}-aiplatform.googleapis.com"})
    except Exception as e:
        logger.error(f"Error getting Vertex AI Prediction Service client: {e}")
        raise

def get_aiplatform_model_client():
    """Client for managing Vertex AI Models (e.g., deploying)."""
    try:
        return aiplatform.gapic.ModelServiceClient(client_options={"api_endpoint": f"{GCP_REGION}-aiplatform.googleapis.com"})
    except Exception as e:
        logger.error(f"Error getting Vertex AI Model Service client: {e}")
        raise

# Initialize Vertex AI SDK
def init_vertex_ai_sdk():
    try:
        aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        logger.info(f"Vertex AI SDK initialized for project '{GCP_PROJECT_ID}' in region '{GCP_REGION}'")
    except Exception as e:
        logger.error(f"Error initializing Vertex AI SDK: {e}")
        raise

# Initialize Vertex AI SDK
def init_vertex_ai_sdk():
    try:
        # --- ADD THESE DEBUG PRINTS ---
        logger.info(f"DEBUG: Attempting to initialize Vertex AI with Project ID: '{GCP_PROJECT_ID}'")
        logger.info(f"DEBUG: Attempting to initialize Vertex AI with Region: '{GCP_REGION}'")
        # --- END DEBUG PRINTS ---

        aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        logger.info(f"Vertex AI SDK initialized for project '{GCP_PROJECT_ID}' in region '{GCP_REGION}'")
    except Exception as e:
        logger.error(f"Error initializing Vertex AI SDK: {e}")
        raise
