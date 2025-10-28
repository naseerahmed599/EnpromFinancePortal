# Flowwer API Usage Guide

## 🎯 Best Practices for Using the Flowwer API

### 1. Understanding the API Structure

The Flowwer API provides document management and accounting integration. Key endpoints:

```
Base URL: https://enprom-gmbh.flowwer.de
Authentication: X-FLOWWER-ApiKey header
```

### 2. Common Use Cases

#### A. List All Documents (Dashboard View)
```python
from flowwer_api_client import FlowwerAPIClient

client = FlowwerAPIClient(api_key="YOUR_API_KEY")

# Get unprocessed documents only (active work)
docs = client.get_all_documents(
    include_processed=False,
    include_deleted=False
)

# Get all documents including completed ones
all_docs = client.get_all_documents(
    include_processed=True,
    include_deleted=False
)
```

**When to use:**
- Dashboard overviews
- Document lists
- Quick status checks
- Filtering by company/stage/payment state

**Data you get:**
- Document ID, Name, Type
- Current Stage, Flow, Company
- Invoice Number, Invoice Date
- Supplier Name
- Payment State
- Total Gross, Total Net
- Upload Time, Due Date

---

#### B. Get Detailed Document Information
```python
# Get specific document
doc = client.get_document(47796)

# Available fields:
print(doc['currentStage'])        # e.g., "Stage1"
print(doc['paymentState'])        # e.g., "ToBePaidExternal"
print(doc['invoiceNumber'])       # e.g., "RE-EN-096-2025"
print(doc['totalGross'])          # Total amount
print(doc['supplierName'])        # Supplier name
print(doc['documentType'])        # e.g., "Ausgangrechnung"
```

**When to use:**
- Viewing single document details
- Before downloading a document
- Checking document status
- Getting complete document metadata

**Data you get:**
- All fields from list view PLUS:
- Unique ID (for downloads)
- Stage timestamps
- Flow details (object)
- Company details (object)
- Uploader information
- File size, PDF status
- Envelope status
- Stage signers/nominees
- Extra data per stage

---

#### C. Get Accounting Details (Receipt Splits / Belegaufteilung)
```python
# Get receipt splits for a document
splits = client.get_receipt_splits(47796)

# Each split contains:
for split in splits:
    print(split['costCenter'])      # e.g., "551000"
    print(split['costUnit'])        # KOST2 value
    print(split['name'])            # Booking text (Ware/Leistung)
    print(split['netValue'])        # Net amount for this split
    print(split['grossValue'])      # Gross amount for this split
    print(split['taxPercent'])      # Tax percentage
```

**When to use:**
- Exporting to accounting systems (DATEV, SAP, etc.)
- Cost center reporting
- Detailed financial analysis
- Splitting invoices across departments

**Data you get:**
- Cost Center (Kostenstelle)
- Cost Unit / KOST2
- Booking Text (Ware/Leistung)
- Net/Gross values per split
- Tax percentage
- Invoice Number, Date
- Payment State
- Supplier Name
- Document ID, Name

**Important Notes:**
- ⚠️ Not all documents have splits (returns empty array if not split)
- One document can have multiple splits (one row per split)
- Split amounts should sum to document total

---

### 3. Efficient Data Loading Strategies

#### Strategy 1: Load on Demand (Fast Initial Load)
```python
# Step 1: Load document list only
docs = client.get_all_documents(include_processed=True)

# Step 2: Load splits only for documents you need to view/export
selected_doc_id = 47796
splits = client.get_receipt_splits(selected_doc_id)
```

**Pros:** Fast initial load, minimal API calls  
**Cons:** Need to fetch splits individually  
**Best for:** Interactive UI, document browsing

---

#### Strategy 2: Bulk Load with Caching (Complete Data)
```python
import time

docs = client.get_all_documents(include_processed=True)
all_data = []

for idx, doc in enumerate(docs):
    doc_id = doc.get('documentId')
    
    # Get splits for each document
    splits = client.get_receipt_splits(doc_id)
    
    if splits:
        # Merge document + split data
        for split in splits:
            merged = {**doc, **split}  # Combine dictionaries
            all_data.append(merged)
    else:
        # No splits, add document alone
        all_data.append(doc)
    
    # Rate limiting (be nice to the API)
    if idx % 100 == 0:
        time.sleep(0.5)  # Small delay every 100 requests
    
    # Progress tracking
    if idx % 50 == 0:
        print(f"Processed {idx}/{len(docs)} documents...")

# Save to file for reuse
import json
with open('flowwer_data_export.json', 'w') as f:
    json.dump(all_data, f, indent=2)
```

**Pros:** Complete data in one pass, can work offline after  
**Cons:** Slower initial load, many API calls  
**Best for:** Reports, exports, data analysis

---

#### Strategy 3: Filtered Load (Targeted Data)
```python
# Only load documents from specific company
docs = client.get_all_documents(include_processed=True)

# Filter by company
target_company = "Enprom GmbH"
filtered_docs = [d for d in docs if d.get('companyName') == target_company]

# Only get splits for filtered documents
data_with_splits = []
for doc in filtered_docs:
    splits = client.get_receipt_splits(doc['documentId'])
    if splits:
        for split in splits:
            data_with_splits.append({**doc, **split})
```

**Pros:** Faster than bulk load, focused dataset  
**Cons:** Need to know filter criteria upfront  
**Best for:** Company-specific reports, filtered exports

---

### 4. API Rate Limiting & Performance

**Best Practices:**
```python
import time
from datetime import datetime

def safe_bulk_load(client, max_requests_per_second=10):
    """Load all documents with splits, respecting rate limits"""
    docs = client.get_all_documents(include_processed=True)
    all_data = []
    
    delay = 1.0 / max_requests_per_second  # e.g., 0.1s for 10 req/s
    
    for doc in docs:
        doc_id = doc.get('documentId')
        if doc_id:
            splits = client.get_receipt_splits(doc_id)
            
            if splits:
                for split in splits:
                    all_data.append({**doc, **split})
            else:
                all_data.append(doc)
            
            time.sleep(delay)  # Rate limiting
    
    return all_data
```

---

### 5. Error Handling

```python
def get_document_safely(client, doc_id):
    """Get document with proper error handling"""
    try:
        doc = client.get_document(doc_id)
        if doc:
            return doc
        else:
            print(f"❌ Document {doc_id} not found")
            return None
    except Exception as e:
        print(f"❌ Error fetching document {doc_id}: {e}")
        return None

def get_splits_safely(client, doc_id):
    """Get receipt splits with error handling"""
    try:
        splits = client.get_receipt_splits(doc_id)
        return splits if splits else []
    except Exception as e:
        print(f"⚠️ Warning: Could not get splits for {doc_id}: {e}")
        return []
```

---

### 6. Recommended Export Workflow

For exporting data to accounting systems or Excel:

```python
from flowwer_api_client import FlowwerAPIClient
import pandas as pd
from datetime import datetime

def export_flowwer_data():
    """Complete export workflow"""
    client = FlowwerAPIClient(api_key="YOUR_API_KEY")
    
    # Step 1: Load all documents
    print("  Loading documents...")
    docs = client.get_all_documents(include_processed=True)
    print(f"✅ Loaded {len(docs)} documents")
    
    # Step 2: Merge with receipt splits
    print("📊 Loading receipt splits...")
    export_data = []
    
    for idx, doc in enumerate(docs):
        doc_id = doc.get('documentId')
        if not doc_id:
            continue
        
        splits = client.get_receipt_splits(doc_id)
        
        if splits:
            # One row per split
            for split in splits:
                row = {
                    'Document ID': doc_id,
                    'Display Name': doc.get('simpleName'),
                    'Document Status': doc.get('currentStage'),
                    'Booking Text': split.get('name'),
                    'Cost Center': split.get('costCenter'),
                    'Cost Unit (KOST2)': split.get('costUnit'),
                    'Invoice Date': doc.get('invoiceDate'),
                    'Invoice Number': doc.get('invoiceNumber'),
                    'Gross': split.get('grossValue'),
                    'Net': split.get('netValue'),
                    'Tax %': split.get('taxPercent'),
                    'Company': doc.get('companyName'),
                    'Supplier': doc.get('supplierName'),
                    'Payment State': doc.get('paymentState'),
                    'Currency': doc.get('currencyCode'),
                    'Document Type': doc.get('documentType'),
                }
                export_data.append(row)
        else:
            # No splits - document level only
            row = {
                'Document ID': doc_id,
                'Display Name': doc.get('simpleName'),
                'Document Status': doc.get('currentStage'),
                'Booking Text': '',
                'Cost Center': '',
                'Cost Unit (KOST2)': '',
                'Invoice Date': doc.get('invoiceDate'),
                'Invoice Number': doc.get('invoiceNumber'),
                'Gross': doc.get('totalGross'),
                'Net': doc.get('totalNet'),
                'Tax %': '',
                'Company': doc.get('companyName'),
                'Supplier': doc.get('supplierName'),
                'Payment State': doc.get('paymentState'),
                'Currency': doc.get('currencyCode'),
                'Document Type': doc.get('documentType'),
            }
            export_data.append(row)
        
        # Progress
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(docs)} documents...")
    
    # Step 3: Create DataFrame and export
    df = pd.DataFrame(export_data)
    
    # Export to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'flowwer_export_{timestamp}.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
    
    print(f"✅ Exported {len(export_data)} rows to {csv_filename}")
    
    # Also save as Excel
    excel_filename = f'flowwer_export_{timestamp}.xlsx'
    df.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"✅ Exported to {excel_filename}")
    
    return df

# Run export
df = export_flowwer_data()
```

---

### 7. Available Fields Reference

#### From Document API (`/api/v1/documents/{id}`):
- `documentId` - Unique document identifier
- `simpleName` - Document file name
- `currentStage` - Current approval stage (Stage1, Stage2, etc.)
- `nextSequentialStage` - Next stage in workflow
- `flowName` - Workflow name
- `companyName` - Company name
- `invoiceNumber` - Invoice number
- `invoiceDate` - Invoice date (ISO 8601)
- `totalGross` - Total gross amount
- `totalNet` - Total net amount
- `currencyCode` - Currency (EUR, USD, etc.)
- `supplierName` - Supplier name
- `supplierVATId` - Supplier VAT ID
- `paymentState` - Payment status
- `paymentDate` - Payment date
- `paymentMethod` - Payment method
- `documentType` - Document type (Ausgangsrechnung, Eingangsrechnung, etc.)
- `uploadTime` - Upload timestamp
- `dueDate` - Due date
- `purchaseOrderNumber` - PO number
- `stageTimestamp` - When current stage was entered
- `uniqueId` - UUID for downloads

#### From Receipt Splits API (`/api/v1/documents/{id}/receiptsplits`):
- `costCenter` - Cost center (Kostenstelle)
- `costUnit` - Cost unit / KOST2
- `name` - Booking text (Ware/Leistung)
- `netValue` - Net amount for this split
- `grossValue` - Gross amount for this split
- `taxPercent` - Tax percentage
- `invoiceNumber` - Invoice number (same as document)
- `invoiceDate` - Invoice date (same as document)
- `paymentState` - Payment state (can differ per split)
- `currentStage` - Current stage (can differ per split)
- `supplierName` - Supplier name (same as document)
- `documentId` - Document ID reference
- `documentName` - Document name reference

---

### 8. Common Pitfalls to Avoid

❌ **Don't do this:**
```python
# Loading all documents with splits in UI without pagination
docs = get_all_documents()  # Could be 18,000+ documents
for doc in docs:
    splits = get_receipt_splits(doc['documentId'])  # 18,000+ API calls!
```

✅ **Do this instead:**
```python
# Load list first, then load splits on demand
docs = get_all_documents()  # Fast
# Show list in UI
# Only fetch splits when user clicks on a document
selected_doc = docs[user_selection]
splits = get_receipt_splits(selected_doc['documentId'])  # One API call
```

---

❌ **Don't do this:**
```python
# Assuming all documents have receipt splits
splits = get_receipt_splits(doc_id)
cost_center = splits[0]['costCenter']  # Could crash if splits is empty!
```

✅ **Do this instead:**
```python
# Check if splits exist
splits = get_receipt_splits(doc_id)
if splits and len(splits) > 0:
    cost_center = splits[0]['costCenter']
else:
    cost_center = ''  # Or handle accordingly
```

---

### 9. Your Current Implementation Analysis

**What you're doing right in your Streamlit app:**

✅ **On-demand loading in Document Details page:**
```python
# Only fetch splits when user clicks "Get Document"
if st.button("Get Document"):
    doc = client.get_document(doc_id)
    splits = client.get_receipt_splits(doc_id)  # ✅ Good!
```

✅ **Progress bar for bulk operations:**
```python
progress_bar = st.progress(0)
for idx, doc in enumerate(docs):
    # ... process ...
    progress_bar.progress((idx + 1) / len(docs))  # ✅ Good!
```

✅ **Null checking:**
```python
if doc_id is None:
    continue  # ✅ Good!
```

**Recommendations for improvement:**

1. **Add caching for API responses:**
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_documents_cached(include_processed, include_deleted):
    return client.get_all_documents(include_processed, include_deleted)
```

2. **Add retry logic for API calls:**
```python
def get_with_retry(func, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1 * (attempt + 1))  # Exponential backoff
```

3. **Add option to limit number of documents loaded:**
```python
max_docs = st.number_input("Max documents to load", min_value=10, value=100)
docs_to_process = docs[:max_docs]
```

---

### 10. Summary - Quick Reference

| Task | Endpoint | API Calls | Speed | Use Case |
|------|----------|-----------|-------|----------|
| List documents | `/documents/all` | 1 | Fast | Dashboard, filtering |
| View one document | `/documents/{id}` | 1 | Fast | Document details |
| Get accounting data | `/documents/{id}/receiptsplits` | 1 per doc | Medium | Accounting export |
| Full export | Both | 1 + N | Slow | Complete data dump |

**Golden Rule:** 
> Load document lists first (fast), then fetch splits only for documents you need (selective loading).

---

## 🎓 Next Steps

1. **For interactive UI:** Use on-demand loading (current approach is good!)
2. **For reports/exports:** Use bulk loading with progress indicators
3. **For production:** Add caching, retry logic, and rate limiting
4. **For accounting integration:** Focus on receipt splits endpoint

**Questions to ask yourself:**
- Do I need ALL documents or just recent/active ones?
- Do I need ALL fields or just specific accounting data?
- Is this for real-time viewing or batch export?
- How often will this run?

Choose your loading strategy based on these answers!
