# Flowwer API Client

Python client for interacting with the Flowwer REST API.

##  API Credentials

- **Account Name:** `enprom-gmbh`
- **API Key:** `[Contact repository owner for API key]`
- **Base URL:** `https://enprom-gmbh.flowwer.de`
- **API Documentation:** `https://enprom-gmbh.flowwer.de/swagger`

> **Note:** For security reasons, the API key is not included in this repository. 
> Store your API key in an environment variable or a `.env` file (not committed to git).

##  Quick Start

### 1. Install Requirements

```bash
pip install requests
```

### 2. Run the Interactive Test Script

```bash
python test_flowwer_api.py
```

The script will automatically use the pre-configured API key.

### 3. Use in Your Own Code

```python
from flowwer_api_client import FlowwerAPIClient, DocumentHelper
import os

# Initialize client with API key from environment variable
client = FlowwerAPIClient()
client.api_key = os.getenv("FLOWWER_API_KEY")  # Set this in your environment
client.session.headers.update({'X-FLOWWER-ApiKey': client.api_key})

# Get all documents
documents = client.get_all_documents()

# Get specific document
doc = client.get_document(123456)

# Get companies and flows
companies = client.get_companies_with_flows()

# Download a document
client.download_document(doc_id, unique_id, "output.pdf")

# Upload a document
result = client.upload_document("invoice.pdf", flow_id=5, company_id=1)
```

**Setting up the API key:**

```bash
# On macOS/Linux
export FLOWWER_API_KEY="your-api-key-here"

# On Windows
set FLOWWER_API_KEY=your-api-key-here
```

Or create a `.env` file (add to `.gitignore`):
```
FLOWWER_API_KEY=your-api-key-here
```

##  Available Methods

### FlowwerAPIClient

#### Authentication
- `authenticate(username, password)` - Generate a new API key (optional, you can use the pre-configured key)

#### Read Operations
- `get_all_documents(include_processed, include_deleted)` - Get all documents
- `get_document(document_id)` - Get single document details
- `get_companies_with_flows()` - Get all companies with active flows
- `download_document(document_id, unique_id, output_path)` - Download document PDF

#### Write Operations
- `upload_document(file_path, flow_id, company_id, filename)` - Upload a document
- `approve_document(document_id, at_stage, nominees)` - Approve a document

### DocumentHelper

- `print_document_summary(document)` - Print formatted document info
- `filter_documents_by_date(documents, start_date, end_date)` - Filter by date range
- `filter_documents_by_company(documents, company_name)` - Filter by company
- `filter_documents_by_stage(documents, stage)` - Filter by stage
- `export_to_csv(documents, output_path)` - Export documents to CSV

##  Testing with Postman

See [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) for complete Postman testing instructions.

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
