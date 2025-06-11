import os

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai

print("ENV PROCESSOR_W2_ID  =", os.getenv("PROCESSOR_W2_ID"))
print("ENV PROCESSOR_W2_NAME=", os.getenv("PROCESSOR_W2_NAME"))
print("ENV PROJECT_ID      =", os.getenv("PROJECT_ID"))
print("Building processor name from:", project_id, location, processor)
project_id = "763352790729"
location = "us"
processor = "b07131aef3b46c45"
name = f"projects/{project_id}/locations/{location}/processors/{processor}"

client_opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
client = documentai.DocumentProcessorServiceClient(client_options=client_opts)

with open("data/raw_documents/W2-Sample1.pdf", "rb") as pdf:
    raw_doc = {"content": pdf.read(), "mime_type": "application/pdf"}

request = documentai.ProcessRequest(name=name, raw_document=raw_doc)
result = client.process_document(request=request)
print("Success:", result)  # you'll see your parsed fields here
