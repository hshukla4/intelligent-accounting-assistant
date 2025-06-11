# deployment/cloud_functions/document_trigger.py
import os

import functions_framework
from google.cloud import storage

# Assume the main processing logic is in a module that can be imported
# For a Cloud Function, all your source code (except main.py) needs to be in the same deployment package
# or you need to structure your deployment for imports.
# For simplicity here, we'll imagine importing process_new_financial_document
# from a deployed src/ folder.
# In a real CF, you'd deploy your whole src/ directory or build a container.

# Example of how you would trigger the main logic from a Cloud Function
# Ensure all necessary modules (document_processing, data_storage, etc.) are available in the Cloud Function deployment
# For this example, we're not actually calling the function directly due to import complexity in shell script.

# @functions_framework.cloud_event
# def process_gcs_document(cloud_event):
#     data = cloud_event.data
#
#     bucket_name = data["bucket"]
#     file_name = data["name"]
#     mime_type = data["contentType"]
#
#     # Determine document type (e.g., based on filename convention or initial content scan)
#     document_type = "invoice" # Default, or infer from file_name/metadata
#     if "receipt" in file_name.lower():
#         document_type = "receipt"
#
#     gcs_uri = f"gs://{bucket_name}/{file_name}"
#
#     # This part would call your core processing logic
#     # from src.main import process_new_financial_document
#     # try:
#     #    processed_data = process_new_financial_document_from_gcs_uri(gcs_uri, document_type)
#     #    print(f"Successfully processed {file_name}: {processed_data.get('document_id')}")
#     # except Exception as e:
#     #    print(f"Error processing {file_name}: {e}")
#
#     print(f"Cloud Function triggered for file: {file_name} in bucket: {bucket_name}")
#     print(f"This function would now call the core processing logic for {gcs_uri} as type {document_type}.")


# A minimal example for actual deployment
@functions_framework.cloud_event
def process_gcs_document(cloud_event):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         cloud_event (google.cloud.functions.Context): The CloudEvent object.
    Returns:
        None; the function terminates after execution.
    """
    from src.main import (  # This import assumes src is deployed with the function
        process_new_financial_document,
    )
    from src.utils.logger import get_logger

    logger = get_logger("cloud_function_logger")  # Re-initialize logger for CF context

    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]
    # mime_type = data["contentType"] # Not directly used by process_new_financial_document, inferred by DocAI

    if not file_name.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
        logger.info(f"Skipping non-document file: {file_name}")
        return

    # Create a local temporary path for the file (Cloud Functions run in a temp dir)
    local_temp_file_path = f"/tmp/{file_name}"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        logger.info(
            f"Downloading {file_name} from gs://{bucket_name} to {local_temp_file_path}"
        )
        blob.download_to_filename(local_temp_file_path)

        # Determine document type (simple heuristic for example)
        document_type = "invoice"
        if "receipt" in file_name.lower() or "receipt" in file_name.lower():
            document_type = "receipt"

        logger.info(f"Calling core processing for {file_name} as {document_type}")
        processed_data = process_new_financial_document(
            local_temp_file_path, document_type
        )
        logger.info(
            f"Successfully processed document {file_name}. Document ID: {processed_data.get('document_id')}"
        )

    except Exception as e:
        logger.error(f"Error processing document {file_name}: {e}")
        # Consider logging the error to Stackdriver and/or sending to an error reporting service
    finally:
        # Clean up the local temporary file
        if os.path.exists(local_temp_file_path):
            os.remove(local_temp_file_path)
