# Intelligent Accounting Assistant (IAA)

This project leverages Google Cloud's AI services (specifically Vertex AI with Gemini models and Document AI) to automate and enhance key accounting processes for small to medium-sized businesses (SMBs).

## Core Features:
- **Document Processing & Data Extraction:** Automated data entry from financial documents (invoices, receipts).
- **Transaction Categorization & Reconciliation:** Intelligent categorization and reconciliation assistance.
- **Financial Reporting & Analysis:** Generate insights and reports.
- **Anomaly Detection:** Identify unusual patterns in financial transactions.

## Setup & Running:

1.  **Google Cloud Setup:**
    - Create a GCP Project.
    - Enable required APIs (Vertex AI, Document AI, BigQuery, Cloud Storage, Cloud Functions/Run, Logging, Monitoring).
    - Create necessary GCS buckets (for raw docs, processed docs, model artifacts).
    - Create Document AI processors (Invoice Parser, Receipt Parser) in your chosen region.
    - Set up a Service Account with appropriate roles for the application.

2.  **Local Environment Setup:**
    ```bash
    # Navigate to the project root
    cd intelligent-accounting-assistant

    # Set up Python virtual environment
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    - Create a `.env` file in the project root and fill in your GCP project details, processor IDs, etc. (See `.env.example` or `config/settings.py` for variables). **DO NOT COMMIT THIS FILE TO GIT.**

4.  **Authentication:**
    - For local development, authenticate your `gcloud` CLI:
      ```bash
      gcloud auth application-default login
      ```

5.  **Run (Example):**
    ```bash
    python src/main.py
    ```

## Project Structure:

- `config/`: Configuration settings.
- `src/`: Main application source code.
    - `document_processing/`: Handlers for Document AI.
    - `transaction_ai/`: Logic for categorization and reconciliation.
    - `anomaly_detection/`: Logic for anomaly detection.
    - `data_storage/`: Handlers for GCS and BigQuery.
    - `utils/`: Utility functions (logger, GCP auth).
    - `api/`: (Optional) REST API definitions.
- `notebooks/`: Jupyter notebooks for experimentation and model training.
- `data/`: Placeholder for raw, processed, and training data.
- `models/`: Placeholder for saved model artifacts.
- `deployment/`: Configuration and scripts for deploying to GCP services (Cloud Functions, Cloud Run).
