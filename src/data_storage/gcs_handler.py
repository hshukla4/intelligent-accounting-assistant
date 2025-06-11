# src/data_storage/gcs_handler.py
from google.cloud import storage
from config.settings import GCS_RAW_DOCUMENTS_BUCKET, GCS_PROCESSED_DOCUMENTS_BUCKET
from src.utils.gcp_auth import get_storage_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

def upload_blob(source_file_path, destination_blob_name, bucket_name):
    """Uploads a file to the bucket."""
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    public_url = f"gs://{bucket_name}/{destination_blob_name}"
    logger.info(f"File {source_file_path} uploaded to {public_url}.")
    return public_url

def download_blob(source_blob_name, destination_file_path, bucket_name):
    """Downloads a blob from the bucket."""
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_path)
    logger.info(f"Blob {source_blob_name} downloaded to {destination_file_path}.")

def get_blob_as_bytes(blob_name, bucket_name):
    """Reads a blob's content as bytes."""
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()

def get_blob_uri(bucket_name, blob_name):
    """Constructs the GCS URI for a blob."""
    return f"gs://{bucket_name}/{blob_name}"
