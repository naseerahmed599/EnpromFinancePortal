# ENPROM Finance Portal

Professional Business Intelligence and Document Management system for ENPROM GmbH, integrated with the Flowwer REST API.

## 🌟 Overview

The **ENPROM Finance Portal** is a sophisticated Streamlit application designed to streamline financial workflows. It provides the ENPROM team with real-time insights into document processing, advanced analytics, and seamless integration with accounting standards like DATEV.

### Key Capabilities

*   **Financial Analytics**: Real-time dashboards for monitoring KPIs and spending patterns.
*   **Workflow Management**: Centralized view of document stages, approvals, and signable items.
*   **Data Integrity**: Advanced comparison tools for reconciling Flowwer data with external accounting records.
*   **Multi-Language Support**: Fully localized in English, German, and Polish.

---

## 🚀 Quick Start

### 1. Installation

Ensure you have Python 3.9+ installed, then run:

```bash
pip install -r requirements.txt
```

### 2. Configuration

You will need a valid Flowwer API key. You can provide this through the application interface upon startup, or set it as an environment variable:

```bash
export FLOWWER_API_KEY="your-api-key-here"
```

### 3. Launching the Portal

Start the application using:

```bash
streamlit run enprom_financial_app.py
```

---

## 📖 Documentation

For a deep dive into the system architecture, folder structure, and development standards, please refer to the full **[DOCUMENTATION.md](DOCUMENTATION.md)**.

## 🛠️ API Client Usage

If you are using the underlying `FlowwerAPIClient` for standalone scripts:

```python
from flowwer_api_client import FlowwerAPIClient

# Initialize the client
client = FlowwerAPIClient(api_key="your-key")

# Get documents
documents = client.get_all_documents()
```

For more details on the API client specifically, see the original technical guide or explore the code in [flowwer_api_client.py](flowwer_api_client.py).

---

© 2025 ENPROM GmbH | Made by the ENPROM Team

Quick steps:
1. Import the collection from POSTMAN_GUIDE.md
2. The API key is already configured
3. Start testing endpoints!

##  Document Stages

Documents in Flowwer go through various stages:
- `Draft` - Initial upload
- `Stage1` - `Stage5` - Approval stages
- `Rejected` - Document rejected
- `Approved` - Document approved
- `Processed` - Document processed
- `DeletedAfterRejection` - Deleted after rejection

##  Payment States

- `Unset` - Not set
- `ToBePaid` - Needs payment
- `TransferIsPrepared` - Transfer prepared
- `Transferred` - Payment transferred
- `Paid` - Payment completed
- `DoneWithoutPayment` - No payment needed
- `ToBePaidExternal` - External payment

##  FTP Access (Optional)

For automated file uploads via FTP:

```
Host: ftp.flowwer.de
Username: enprom-gmbh+ApiKeyUser
Password: [Use your API key]
```

##  Example: Get and Export Documents

```python
from flowwer_api_client import FlowwerAPIClient, DocumentHelper
import os

# Setup
client = FlowwerAPIClient()
client.api_key = os.getenv("FLOWWER_API_KEY")
client.session.headers.update({'X-FLOWWER-ApiKey': client.api_key})

# Get all unprocessed documents
documents = client.get_all_documents(include_processed=False)

# Filter by date range
filtered = DocumentHelper.filter_documents_by_date(
    documents, 
    "2024-01-01", 
    "2024-12-31"
)

# Export to CSV
DocumentHelper.export_to_csv(filtered, "invoices_2024.csv")

# Print summary of each
for doc in filtered[:10]:
    DocumentHelper.print_document_summary(doc)
```

##  Example: Download Invoices

```python
from flowwer_api_client import FlowwerAPIClient
import os

client = FlowwerAPIClient()
client.api_key = os.getenv("FLOWWER_API_KEY")
client.session.headers.update({'X-FLOWWER-ApiKey': client.api_key})

# Get document details
doc = client.get_document(123456)

if doc:
    unique_id = doc.get('uniqueId')
    filename = doc.get('simpleName', 'document.pdf')
    
    # Download the PDF
    client.download_document(123456, unique_id, filename)
```

## Error Handling

Common response codes:
- `200` - Success
- `401` - Unauthorized (check API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `503` - Service unavailable

## Troubleshooting

### Code Changes Not Taking Effect (Python Cache Issue)

If you've modified code (especially `flowwer_api_client.py`) but changes aren't being picked up by Streamlit:

**Quick Fix:**
```bash
# Run the clear cache script
./clear_cache.sh

# Or manually:
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true
```

**Then restart Streamlit:**
1. Stop the current process (Ctrl+C)
2. Run: `streamlit run enprom_financial_app.py`

**Why this happens:**
- Python stores compiled bytecode (`.pyc` files) in `__pycache__` directories
- Streamlit may not always reload all modules on code changes
- Restarting forces Python to reload all modules from source

**When to use:**
- After modifying `flowwer_api_client.py` or other imported modules
- When API calls behave unexpectedly after code changes
- When you see old error messages or old behavior persisting

##  Support

For API support, contact: support@flowwer.de

##  Files

- `flowwer_api_client.py` - Main API client library
- `test_flowwer_api.py` - Interactive test script
- `POSTMAN_GUIDE.md` - Postman testing guide
- `README.md` - This file
