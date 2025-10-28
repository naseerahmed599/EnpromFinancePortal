# Flowwer API - Postman Testing Guide

## API Credentials

**Account Name:** `[Your Account Name]`

**API Key:** `[Your API Key - Contact repository owner]`

**API Documentation:** `https://[your-account].flowwer.de/swagger`

**HTTP Header for API Key:** `X-FLOWWER-ApiKey`

> **Security Note:** This guide uses placeholder values. Replace `[Your API Key]` and `[your-account]` with your actual credentials. Never commit actual API keys to version control.

---

## Setup

### 1. Create a New Collection in Postman
- Name: "Flowwer API"
- Base URL: `https://[your-account].flowwer.de`

### 2. Option A: Use Your API Key (Recommended)

Add your API key to all requests as a header:
```
X-FLOWWER-ApiKey: [Your API Key]
```

### 3. Option B: Generate New API Key via Authentication (Optional)

**Request Name:** Authenticate and Get API Key

**Method:** `POST`

**URL:** `https://[your-account].flowwer.de/api/v1/auth/token`

**Headers:**
```
username: [your-username]
password: [your-password]
```

**Expected Response:**
```
"your-new-api-key-here"
```

**Postman Test Script (to auto-save the API key):**
```javascript
// Save the API key to collection variable
pm.collectionVariables.set("apiKey", pm.response.text().replace(/"/g, ''));
```

---

## Collection Variables

Set these in your collection:

- `apiKey` - `[Your API Key]` (or auto-set from authentication response)
- `baseUrl` - `https://[your-account].flowwer.de`

---

## 📖 How to Create Requests in Postman

### Step-by-Step Guide

#### Setting Up Authentication/Headers

**Option 1: Using Headers Tab (Recommended for Individual Requests)**
1. In your request, click the **"Headers"** tab
2. Add a new header:
   - **Key:** `X-FLOWWER-ApiKey`
   - **Value:** `{{apiKey}}` (or your actual API key)
3. Make sure the checkbox next to the header is ✅ checked

**Option 2: Using Auth Tab (For Collection-Level Auth)**
1. Go to your **Collection** settings (click on the collection name)
2. Click the **"Authorization"** tab
3. **Type:** Select `API Key` from dropdown
4. Configure:
   - **Key:** `X-FLOWWER-ApiKey`
   - **Value:** `[Your API Key]`
   - **Add to:** `Header`
5. Save the collection
6. For each request: In the **"Authorization"** tab, select **"Inherit auth from parent"**

**Note:** For Flowwer API, we'll use the Headers tab approach as it's more straightforward for this guide.

#### Setting Up Headers
1. In your request, click the **"Headers"** tab
2. Add a new header by clicking in the fields:
   - In the **"Key"** field, enter: `X-FLOWWER-ApiKey` (without "Key:" prefix)
   - In the **"Value"** field, enter: `[Your API Key]` (without "Value:" prefix)
3. Make sure the checkbox next to the header is ✅ checked

**Important:** Don't type "Key:" or "Value:" - these are just labels in the guide. Postman has separate columns/fields for Key and Value.

#### Setting Up Query Parameters (for GET requests)
1. In your request, click the **"Params"** tab
2. Add parameters in the "Query Params" section:
   - In the **"Key"** field: `includeProcessed` | In the **"Value"** field: `false`
   - In the **"Key"** field: `includeDeleted` | In the **"Value"** field: `false`
3. Postman will automatically add these to the URL with `?` and `&`

**Important:** Just enter the text itself - no colons or prefixes needed.

#### Setting Up Body (for POST requests)
1. Click the **"Body"** tab
2. For JSON data:
   - Select **"raw"**
   - Choose **"JSON"** from the dropdown
   - Enter your JSON data
3. For file upload:
   - Select **"binary"**
   - Click "Select File" to choose a file

#### Using Variables
- Collection variables: `{{variableName}}`
- Example: `{{apiKey}}`, `{{baseUrl}}`
- Set in Collection → Variables tab

---

## API Requests

### 1. Get All Documents

**Method:** `GET`

**URL:** `{{baseUrl}}/api/v1/documents/all`

Or directly: `https://[your-account].flowwer.de/api/v1/documents/all`

#### In Postman:
1. **Method:** Select `GET` from dropdown
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/documents/all`
3. **Authorization Tab:** Select `No Auth` (we'll use Headers instead)
4. **Headers Tab:** Add one row:
   - Key field: `X-FLOWWER-ApiKey`
   - Value field: `[Your API Key]`
5. **Params Tab:** Add two rows:
   - Row 1 → Key: `includeProcessed` | Value: `false`
   - Row 2 → Key: `includeDeleted` | Value: `false`
6. Click **"Send"**

💡 **Tip:** Just type the values directly - don't include "Key:" or "Value:" text!

**Note:** After adding params, your URL will automatically become:
```
https://[your-account].flowwer.de/api/v1/documents/all?includeProcessed=false&includeDeleted=false
```

**Expected Response:** Array of document objects

---

### 2. Get Single Document

**Method:** `GET`

**URL:** `{{baseUrl}}/api/v1/documents/{documentId}`

Replace `{documentId}` with actual ID, e.g., `123456`

Or directly: `https://[your-account].flowwer.de/api/v1/documents/123456`

#### In Postman:
1. **Method:** Select `GET`
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/documents/123456`
   - Replace `123456` with an actual document ID
3. **Authorization Tab:** Select `No Auth`
4. **Headers Tab:**
   - Key: `X-FLOWWER-ApiKey`
   - Value: `[Your API Key]`
5. **Params Tab:** Leave empty (no query parameters needed)
6. Click **"Send"**

**Expected Response:** Single document object with full details

**Example Response Structure:**
```json
{
  "documentId": 123456,
  "simpleName": "Invoice_2024.pdf",
  "companyName": "Your Company Name",
  "flowName": "Standard Invoice Flow",
  "currentStage": "Stage1",
  "invoiceDate": "2024-10-15T00:00:00Z",
  "invoiceNumber": "INV-001",
  "totalGross": 1190.00,
  "totalNet": 1000.00,
  "currencyCode": "EUR",
  "supplierName": "Supplier XYZ",
  "paymentState": "ToBePaid"
}
```

---

### 3. Get Companies with Active Flows

**Method:** `GET`

**URL:** `{{baseUrl}}/api/v1/companies/activeflows/reduced`

Or directly: `https://[your-account].flowwer.de/api/v1/companies/activeflows/reduced`

#### In Postman:
1. **Method:** Select `GET`
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/companies/activeflows/reduced`
3. **Authorization Tab:** Select `No Auth`
4. **Headers Tab:**
   - Key: `X-FLOWWER-ApiKey`
   - Value: `[Your API Key]`
5. **Params Tab:** Leave empty
6. Click **"Send"**

**Expected Response:**
```json
[
  {
    "companyId": 1,
    "companyName": "Your Company Name",
    "flowId": 5,
    "flowName": "Invoice Approval Flow"
  }
]
```

---

### 4. Get Flows for Specific Company

**Method:** `GET`

**URL:** `{{baseUrl}}/api/v1/companies/{companyId}/activeflows/reduced`

Replace `{companyId}` with actual ID, e.g., `1`

Or directly: `https://[your-account].flowwer.de/api/v1/companies/1/activeflows/reduced`

#### In Postman:
1. **Method:** Select `GET`
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/companies/1/activeflows/reduced`
3. **Authorization Tab:** Select `No Auth`
4. **Headers Tab:**
   - Key: `X-FLOWWER-ApiKey`
   - Value: `[Your API Key]`
5. Click **"Send"**

---

### 5. Download Document PDF

**Method:** `GET`

**URL:** `{{baseUrl}}/api/v1/download/{documentId}/download/document.pdf`

Or directly: `https://[your-account].flowwer.de/api/v1/download/123456/download/document.pdf`

#### In Postman:
1. **Method:** Select `GET`
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/download/123456/download/document.pdf`
   - Replace `123456` with actual document ID
3. **Authorization Tab:** Select `No Auth`
4. **Headers Tab:**
   - Key: `X-FLOWWER-ApiKey`
   - Value: `[Your API Key]`
5. **Params Tab:**
   - Key: `uniqueId`
   - Value: `[UUID from document details]` (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
6. Click **"Send"**
7. Click **"Save Response"** → **"Save to a file"** to download the PDF

**Query Parameters:**
- `uniqueId` (required): UUID from document details (get from Get Document request first)

**Note:** To get the `uniqueId`, first call "Get Single Document" and extract the `uniqueId` field from the response.

---

### 6. Upload Document

**Method:** `POST`

**URL:** `{{baseUrl}}/api/v1/upload`

Or directly: `https://[your-account].flowwer.de/api/v1/upload`

#### In Postman:
1. **Method:** Select `POST`
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/upload`
3. **Authorization Tab:** Select `No Auth`
4. **Headers Tab:**
   - Key: `X-FLOWWER-ApiKey`
   - Value: `[Your API Key]`
   - Key: `Content-Type`
   - Value: `application/octet-stream`
5. **Params Tab (Optional):**
   - Key: `FlowwId` | Value: `5` (your flow ID)
   - Key: `CompanyId` | Value: `1` (your company ID)
   - Key: `Filename` | Value: `test_invoice.pdf`
6. **Body Tab:**
   - Select **"binary"**
   - Click **"Select File"**
   - Choose a PDF file from your computer
7. Click **"Send"**

**Query Parameters (Optional):**
- `FlowwId` (optional): e.g., `5`
- `CompanyId` (optional): e.g., `1`
- `Filename` (optional): e.g., `test_invoice.pdf`

**Body:**
- Type: `binary`
- Select a PDF file from your computer

**Expected Response:**
```json
{
  "elementId": 123457,
  "name": "test_invoice.pdf"
}
```

---

### 7. Approve Document

**Method:** `POST`

**URL:** `{{baseUrl}}/api/v1/documents/{documentId}/approve`

Or directly: `https://[your-account].flowwer.de/api/v1/documents/123456/approve`

#### In Postman:
1. **Method:** Select `POST`
2. **URL:** Enter `https://[your-account].flowwer.de/api/v1/documents/123456/approve`
   - Replace `123456` with actual document ID
3. **Authorization Tab:** Select `No Auth`
4. **Headers Tab:**
   - Key: `X-FLOWWER-ApiKey`
   - Value: `[Your API Key]`
   - Key: `Content-Type`
   - Value: `application/json`
5. **Body Tab:**
   - Select **"raw"**
   - Select **"JSON"** from the dropdown
   - Enter the JSON:
   ```json
   {
     "atStage": "Stage1"
   }
   ```
6. Click **"Send"**

**Body (JSON):**
```json
{
  "atStage": "Stage1"
}
```

**Optional Body with Nominees:**
```json
{
  "atStage": "Stage1",
  "nominees": ["user-guid-1", "user-guid-2"]
}
```

---

## Common Response Codes

- `200` - Success
- `401` - Unauthorized (check your API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `503` - Service unavailable

---

## Postman Collection JSON

You can import this JSON into Postman (remember to replace placeholder values with your actual credentials):

```json
{
  "info": {
    "name": "Flowwer API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://[your-account].flowwer.de"
    },
    {
      "key": "apiKey",
      "value": "[Your API Key]"
    }
  ],
  "item": [
    {
      "name": "1. Authenticate",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.collectionVariables.set('apiKey', pm.response.text().replace(/\"/g, ''));"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "username",
            "value": "[your-username]"
          },
          {
            "key": "password",
            "value": "[your-password]"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/api/v1/auth/token",
          "host": ["{{baseUrl}}"],
          "path": ["api", "v1", "auth", "token"]
        }
      }
    },
    {
      "name": "2. Get All Documents",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "X-FLOWWER-ApiKey",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/api/v1/documents/all?includeProcessed=false&includeDeleted=false",
          "host": ["{{baseUrl}}"],
          "path": ["api", "v1", "documents", "all"],
          "query": [
            {
              "key": "includeProcessed",
              "value": "false"
            },
            {
              "key": "includeDeleted",
              "value": "false"
            }
          ]
        }
      }
    },
    {
      "name": "3. Get Single Document",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "X-FLOWWER-ApiKey",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/api/v1/documents/123456",
          "host": ["{{baseUrl}}"],
          "path": ["api", "v1", "documents", "123456"]
        }
      }
    },
    {
      "name": "4. Get Companies with Flows",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "X-FLOWWER-ApiKey",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/api/v1/companies/activeflows/reduced",
          "host": ["{{baseUrl}}"],
          "path": ["api", "v1", "companies", "activeflows", "reduced"]
        }
      }
    }
  ]
}
```

---

## Testing Workflow

### Quick Start (Using Your API Key)

1. **Import Collection:** Import the JSON collection above into Postman
2. **Set Your Credentials:** Replace `[Your API Key]` and `[your-account]` with your actual values
3. **Test Read Operations:**
   - Get All Documents
   - Get Companies with Flows
   - Get Single Document (use a document ID from step 3a)
4. **Test Download:** Use document ID and uniqueId from Get Single Document
5. **Test Upload:** Upload a test PDF file
6. **Test Approve:** Approve a document that's in Stage1

### Alternative Workflow (Generate New API Key)

1. **First:** Run "Authenticate" request to get a new API key
2. **Verify:** Check that `{{apiKey}}` variable is set in collection
3. **Continue:** Follow steps 3-6 above

---

## FTP Access (Optional)

For automated file uploads via FTP:

**Host:** `ftp.flowwer.de`  
**Username:** `[your-account]+ApiKeyUser`  
**Password:** `[Your API Key]`

---

## Tips

1. **Security:** Replace all `[Your API Key]` and `[your-account]` placeholders with your actual credentials
2. Use collection variables (`{{apiKey}}`, `{{baseUrl}}`) for reusability
3. To find a valid document ID, first call "Get All Documents" and pick one
4. The `uniqueId` for downloads must match the document - get it from document details first
5. API Documentation is available at: `https://[your-account].flowwer.de/swagger`
