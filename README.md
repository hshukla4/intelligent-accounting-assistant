# Intelligent Accounting Assistant

## Purpose

Intelligent Accounting Assistant is a command-line tool designed to automate the extraction and analysis of financial document data (e.g., W2s, invoices, receipts). It streamlines the processing of raw PDFs into structured spreadsheets, significantly reducing manual data entry and enabling faster financial insights.

## Functional Description

The application ingests raw financial documents from a local directory or Cloud Storage bucket and processes each file based on its specified type (e.g., `w2`, `invoice`, `receipt`). Key features include:

- **Document Type Parsing**: Uses GCP Document AI and custom parsers to extract fields such as company/vendor name, address, contact number, and line-item details.
- **Output Generation**: Produces detailed and summary Excel spreadsheets for each document with embedded timestamp and naming conventions for traceability.
- **Console Summary**: At the end of each run, prints a summary table showing:
  - **Timestamp**: Processing timestamp (YYYYMMDDHHMMSS)
  - **Input File Name**: Original document name
  - **Input Directory**: Source directory or bucket
  - **Document Type**: Type identifier (e.g., `w2`)
  - **Detailed Output File**: Name of the spreadsheet with all extracted fields
  - **Summary Output File**: Name of the spreadsheet with key summary metrics

Filename conventions ensure each output file includes both the processing timestamp and, for invoices/receipts, the vendor or company name (e.g., `20250610115337_ACME_Corp_Invoice.xlsx`).

## Summary on Console

Example summary printed after processing:

```
| Timestamp      | Input File       | Doc Type | Detailed Output File                  | Summary Output File              |
|----------------|------------------|----------|---------------------------------------|----------------------------------|
| 20250610115337 | W2-Sample1.pdf   | w2       | 20250610115337_W2-Sample1_Detail.xlsx | 20250610115337_W2_Summary.xlsx   |
```

## Project Structure

```
intelligent-accounting-assistant/
├── src/
│   ├── main.py
│   ├── pipeline/
│   │   └── pipeline_controller.py
│   ├── data_storage/
│   │   └── gcs_handler.py
│   └── parsers/
│       └── w2_parser.py
├── scripts/
│   └── parse_all.sh
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.12+
- Google Cloud SDK (authenticated via `gcloud auth login`)
- GCP project with Document AI and Cloud Storage APIs enabled
- Service account with Storage Admin and Document AI roles
- Python dependencies: install via `pip install -r requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<org>/intelligent-accounting-assistant.git
   cd intelligent-accounting-assistant
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## GCP Setup

1. Set environment variables:
   ```bash
   export GCP_PROJECT=<your-gcp-project-id>
   export GCP_REGION=us-central1
   export CLOUDSDK_PYTHON=$(which python3.12)
   ```
2. Create Cloud Storage buckets:
   ```bash
   gsutil mb -l $GCP_REGION gs://$GCP_PROJECT-raw-docs
   gsutil mb -l $GCP_REGION gs://$GCP_PROJECT-processed-docs
   gsutil mb -l $GCP_REGION gs://$GCP_PROJECT-model-artifacts
   ```
3. Enable required APIs:
   ```bash
   gcloud services enable storage.googleapis.com \
       documentai.googleapis.com
   ```

## Usage

- **Process a single document**:
  ```bash
  python -m src.main data/raw_documents/W2-Sample1.pdf w2
  ```
- **Batch process all documents**:
  ```bash
  bash scripts/parse_all.sh data/raw_documents output_directory
  ```

## Technology Stack

- **Language**: Python 3.12
- **Cloud**: Google Cloud Platform (Storage, Document AI)
- **Libraries**: `google-cloud-storage`, `google-cloud-documentai`, `pandas`, `openpyxl`

## Contribution

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

