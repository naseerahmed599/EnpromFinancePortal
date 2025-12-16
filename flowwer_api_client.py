"""
Flowwer API Client
A Python client for interacting with the Flowwer REST API
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import json


class FlowwerAPIClient:
    """Main client for interacting with Flowwer API"""

    def __init__(
        self,
        base_url: str = "https://enprom-gmbh.flowwer.de",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Flowwer API client

        Args:
            base_url: The base URL for the Flowwer instance
            api_key: The API key for authentication (default: pre-configured key)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()

        # Set API key in headers if provided
        if self.api_key:
            self.session.headers.update({"X-FLOWWER-ApiKey": self.api_key})

    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate and get API key

        Args:
            username: Flowwer username
            password: Flowwer password

        Returns:
            bool: True if authentication successful
        """
        url = f"{self.base_url}/api/v1/auth/token"

        # Reset last auth error info
        self.last_auth_status = None
        self.last_auth_response = None

        try:
            # Attempt 1: Headers (per Postman guide)
            resp = requests.post(
                url, headers={"username": username, "password": password}
            )
            if resp.status_code == 200:
                self.api_key = resp.text.strip('"')
                self.session.headers.update({"X-FLOWWER-ApiKey": self.api_key})
                return True

            # Attempt 2: JSON body
            resp = requests.post(
                url,
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code == 200:
                self.api_key = resp.text.strip('"')
                self.session.headers.update({"X-FLOWWER-ApiKey": self.api_key})
                return True

            # Attempt 3: Form encoded
            resp = requests.post(
                url,
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code == 200:
                self.api_key = resp.text.strip('"')
                self.session.headers.update({"X-FLOWWER-ApiKey": self.api_key})
                return True

            # Record last error
            self.last_auth_status = resp.status_code
            # Keep short snippet to avoid logging secrets
            self.last_auth_response = (resp.text or "").strip()[:500]
            return False

        except Exception as e:
            self.last_auth_status = -1
            self.last_auth_response = str(e)
            return False

    def get_all_documents(
        self, include_processed: bool = False, include_deleted: bool = False
    ) -> Optional[List[Dict]]:
        """
        Get all documents

        Args:
            include_processed: Include processed documents
            include_deleted: Include deleted documents

        Returns:
            List of document dictionaries or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/documents/all"
        params = {
            "includeProcessed": include_processed,
            "includeDeleted": include_deleted,
        }

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                documents = response.json()
                print(f"Retrieved {len(documents)} documents")
                return documents
            else:
                print(f"Failed to get documents: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting documents: {e}")
            return None

    def get_document(self, document_id: int) -> Optional[Dict]:
        """
        Get details of a single document

        Args:
            document_id: The ID of the document

        Returns:
            Document dictionary or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/documents/{document_id}"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                document = response.json()
                print(f"Retrieved document {document_id}")
                return document
            else:
                print(f"Failed to get document: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting document: {e}")
            return None

    def get_companies_with_flows(self) -> Optional[List[Dict]]:
        """
        Get all active companies with valid flows

        Returns:
            List of company/flow dictionaries or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/companies/activeflows/reduced"

        try:
            response = self.session.get(url)

            # Debug: print request headers
            print(f"🔍 Debug - Request URL: {url}")
            print(f"🔍 Debug - Headers: {dict(self.session.headers)}")
            print(f"🔍 Debug - Response Status: {response.status_code}")

            if response.status_code == 200:
                companies = response.json()
                print(f"Retrieved {len(companies)} company/flow combinations")
                return companies
            else:
                print(f"Failed to get companies: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting companies: {e}")
            return None

    def download_document(
        self, document_id: int, unique_id: str, output_path: str
    ) -> bool:
        """
        Download a document PDF

        Args:
            document_id: The ID of the document
            unique_id: The unique UUID for the document
            output_path: Path to save the downloaded file

        Returns:
            bool: True if download successful
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return False

        url = f"{self.base_url}/api/v1/download/{document_id}/download/document.pdf"
        params = {"uniqueId": unique_id}

        try:
            response = self.session.get(url, params=params, stream=True)

            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Document downloaded to {output_path}")
                return True
            else:
                print(f"Failed to download document: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error downloading document: {e}")
            return False

    def upload_document(
        self,
        file_path: str,
        flow_id: Optional[int] = None,
        company_id: Optional[int] = None,
        filename: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Upload a document to Flowwer

        Args:
            file_path: Path to the file to upload
            flow_id: Optional Flow ID to assign document to
            company_id: Optional Company ID to assign document to
            filename: Optional filename (defaults to original filename)

        Returns:
            Upload result dictionary or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/upload"
        params = {}

        if flow_id:
            params["FlowwId"] = flow_id
        if company_id:
            params["CompanyId"] = company_id
        if filename:
            params["Filename"] = filename

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            headers = {"Content-Type": "application/octet-stream"}
            response = self.session.post(
                url, params=params, data=file_content, headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                print(f"Document uploaded successfully!")
                print(f"Document ID: {result.get('elementId')}")
                print(f"Name: {result.get('name')}")
                return result
            else:
                print(f"Failed to upload document: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error uploading document: {e}")
            return None

    def get_receipt_splits(self, document_id: int) -> Optional[List[Dict]]:
        """
        Get receipt splits (Belegaufteilung) for a document

        This returns accounting details like Cost Center, Cost Unit, Booking Text, etc.

        Args:
            document_id: The ID of the document

        Returns:
            List of split dictionaries or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/documents/{document_id}/receiptsplits"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                splits = response.json()
                
                if isinstance(splits, str):
                    try:
                        splits = json.loads(splits)
                    except (json.JSONDecodeError, ValueError):
                        print(f"Warning: Receipt splits endpoint returned unexpected string: {splits}")
                        return None
                
                if isinstance(splits, dict):
                    if "documentReceiptSplits" in splits:
                        splits = splits["documentReceiptSplits"]
                    elif "splits" in splits:
                        splits = splits["splits"]
                    elif "data" in splits:
                        splits = splits["data"]
                    elif "receiptSplits" in splits:
                        splits = splits["receiptSplits"]
                    else:
                        print(f"Warning: Receipt splits response is a dict without expected keys: {list(splits.keys())}")
                        return None
                
                if not isinstance(splits, list):
                    print(f"Warning: Receipt splits response is not a list: {type(splits)}")
                    return None
                
                print(
                    f"Retrieved {len(splits)} receipt split(s) for document {document_id}"
                )
                return splits
            else:
                print(f"Failed to get receipt splits: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting receipt splits: {e}")
            return None

    def approve_document(
        self, document_id: int, at_stage: str, nominees: Optional[List[str]] = None
    ) -> bool:
        """
        Approve a document

        Args:
            document_id: The ID of the document to approve
            at_stage: Current stage (e.g., "Stage1", "Stage2", etc.)
            nominees: Optional list of nominee user GUIDs

        Returns:
            bool: True if approval successful
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return False

        url = f"{self.base_url}/api/v1/documents/{document_id}/approve"

        payload: Dict[str, Any] = {"atStage": at_stage}

        if nominees:
            payload["nominees"] = nominees

        try:
            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                print(f"Document {document_id} approved at {at_stage}")
                return True
            else:
                print(f"Failed to approve document: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error approving document: {e}")
            return False

    def get_receipt_splitting_report(
        self,
        cost_center: Optional[str] = None,
        account: Optional[str] = None,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Optional[List[Dict]]:
        """
        Generate receipt splitting report with filters

        This is a powerful endpoint that returns comprehensive accounting data
        filtered by various criteria.

        Args:
            cost_center: Filter by cost center
            account: Filter by account
            min_date: Minimum date (YYYY-MM-DD format)
            max_date: Maximum date (YYYY-MM-DD format)
            company: Filter by company name

        Returns:
            List of receipt splitting report entries or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        today = date.today()
        if not min_date:
            min_date = date(today.year, today.month, 1).isoformat()
        if not max_date:
            max_date = date(today.year, today.month, 1).isoformat()

        paths = self._build_month_paths(min_date, max_date)
        if not paths:
            print("No valid date range supplied for receipt splitting report.")
            return None

        try:
            rows: List[Dict[str, Any]] = []
            for path in paths:
                docs = self._find_documents_with_receipt_splits(path)
                if docs is None:
                    continue
                for doc in docs:
                    base_doc = {k: v for k, v in doc.items() if k != "documentReceiptSplits"}
                    splits = doc.get("documentReceiptSplits") or []
                    for split in splits:
                        merged = {**base_doc, **split}
                        rows.append(merged)

            if cost_center:
                rows = [
                    r for r in rows if str(r.get("costCenter", "")) == str(cost_center)
                ]
            if account:
                rows = [r for r in rows if str(r.get("account", "")) == str(account)]
            if company:
                rows = [
                    r
                    for r in rows
                    if str(r.get("supplierName", "")).lower()
                    == str(company).lower()
                ]

            print(f"Retrieved {len(rows)} receipt splitting report entries")
            return rows
        except Exception as e:
            print(f"Error getting receipt splitting report: {e}")
            return None

    def get_all_cost_centers(
        self, months_back: int = 6, min_date: Optional[str] = None, max_date: Optional[str] = None
    ) -> Optional[List[str]]:
        """
        Get a list of all cost centers from documents

        Returns:
            List of cost center strings or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        try:
            if min_date and max_date:
                return self.get_cost_centers_for_range(min_date, max_date)

            paths = self._recent_month_paths(months_back)
            if not paths:
                return []

            cost_centers: set[str] = set()
            for path in paths:
                docs = self._find_documents_with_receipt_splits(path)
                if not docs:
                    continue
                for doc in docs:
                    splits = doc.get("documentReceiptSplits") or []
                    for split in splits:
                        cc = split.get("costCenter")
                        if cc not in [None, "", "None", "nan"]:
                            cost_centers.add(str(cc))

            sorted_cc = sorted(cost_centers)
            print(f"Retrieved {len(sorted_cc)} cost centers (via Find API)")
            return sorted_cc
        except Exception as e:
            print(f"Error getting cost centers: {e}")
            return None

    def get_cost_centers_for_range(
        self, min_date: str, max_date: str
    ) -> Optional[List[str]]:
        """Get cost centers for an explicit date range using Find API."""
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        try:
            paths = self._build_month_paths(min_date, max_date)
            if not paths:
                return []

            cost_centers: set[str] = set()
            for path in paths:
                docs = self._find_documents_with_receipt_splits(path)
                if not docs:
                    continue
                for doc in docs:
                    splits = doc.get("documentReceiptSplits") or []
                    for split in splits:
                        cc = split.get("costCenter")
                        if cc not in [None, "", "None", "nan"]:
                            cost_centers.add(str(cc))

            sorted_cc = sorted(cost_centers)
            print(
                f"Retrieved {len(sorted_cc)} cost centers (via Find API, {min_date} to {max_date})"
            )
            return sorted_cc
        except Exception as e:
            print(f"Error getting cost centers for range: {e}")
            return None

    def get_all_accounts(self, months_back: int = 6) -> Optional[List[str]]:
        """
        Get a list of all accounts from documents

        Returns:
            List of account strings or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        try:
            paths = self._recent_month_paths(months_back)
            if not paths:
                return []

            accounts: set[str] = set()
            for path in paths:
                docs = self._find_documents_with_receipt_splits(path)
                if not docs:
                    continue
                for doc in docs:
                    splits = doc.get("documentReceiptSplits") or []
                    for split in splits:
                        acct = split.get("account")
                        if acct not in [None, "", "None", "nan"]:
                            accounts.add(str(acct))

            sorted_accounts = sorted(accounts)
            print(f"Retrieved {len(sorted_accounts)} accounts (via Find API)")
            return sorted_accounts
        except Exception as e:
            print(f"Error getting accounts: {e}")
            return None

    def _find_documents_with_receipt_splits(
        self, path: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Internal: call Find API for documents + receipt splits for a path."""
        url = f"{self.base_url}/api/v1/find/path/documents/receipt-splits"
        try:
            resp = self.session.get(url, params={"Path": path})
            if resp.status_code == 200:
                data = resp.json()
                # API returns {"documents": [...]} or a raw list depending on impl
                if isinstance(data, dict) and "documents" in data:
                    return data.get("documents", [])
                if isinstance(data, list):
                    return data
                return []
            else:
                print(
                    f"Find API path {path} failed: {resp.status_code} - {resp.text[:200]}"
                )
                return None
        except Exception as e:
            print(f"Error calling Find API for path {path}: {e}")
            return None

    def _build_month_paths(
        self, min_date: str, max_date: str
    ) -> List[str]:
        """Build list of CreationDate-Months/<YYYY-MM> paths inclusive."""
        try:
            start = datetime.fromisoformat(min_date).date()
            end = datetime.fromisoformat(max_date).date()
        except Exception:
            return []

        if start > end:
            start, end = end, start

        paths: List[str] = []
        current = date(start.year, start.month, 1)
        end_marker = date(end.year, end.month, 1)

        while current <= end_marker:
            paths.append(f"CreationDate-Months/{current.strftime('%Y-%m')}")
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        return paths

    def _recent_month_paths(self, months_back: int) -> List[str]:
        """Helper to get a list of recent month paths (inclusive of current month)."""
        months_back = max(1, months_back)
        today = date.today()
        paths: List[str] = []
        year, month = today.year, today.month
        for _ in range(months_back):
            paths.append(f"CreationDate-Months/{year:04d}-{month:02d}")
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        return paths

    def get_approved_documents(
        self, flow_id: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        Get a list of all approved documents

        Args:
            flow_id: Optional - restrict to documents in this flow

        Returns:
            List of approved documents or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/documents/approved"

        params = {}
        if flow_id:
            params["flowwid"] = flow_id

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                documents = response.json()
                print(f"Retrieved {len(documents)} approved documents")
                return documents
            else:
                print(f"Failed to get approved documents: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting approved documents: {e}")
            return None

    def get_signable_documents(self, backup_list: bool = False) -> Optional[List[Dict]]:
        """
        Get a list of documents waiting for signature (approval)

        Args:
            backup_list: If True, gets backup signable documents

        Returns:
            List of signable documents or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/documents/signable"

        params = {"backupList": backup_list}

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                documents = response.json()
                print(f"Retrieved {len(documents)} signable documents")
                return documents
            else:
                print(f"Failed to get signable documents: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting signable documents: {e}")
            return None


class DocumentHelper:
    """Helper class for working with document data"""

    @staticmethod
    def print_document_summary(document: Dict) -> None:
        """Print a summary of a document"""
        print("\n" + "=" * 60)
        print(f"📄 Document ID: {document.get('documentId')}")
        print(f"📝 Name: {document.get('simpleName')}")
        print(f"🏢 Company: {document.get('companyName')}")
        print(f"📊 Flow: {document.get('flowName')}")
        print(f"   Stage: {document.get('currentStage')}")
        print(f"📅 Invoice Date: {document.get('invoiceDate')}")
        print(f"🔢 Invoice Number: {document.get('invoiceNumber')}")
        print(
            f"💰 Total Gross: {document.get('totalGross')} {document.get('currencyCode')}"
        )
        print(
            f"💳 Total Net: {document.get('totalNet')} {document.get('currencyCode')}"
        )
        print(f"🏪 Supplier: {document.get('supplierName')}")
        print(f"📤 Upload Time: {document.get('uploadTime')}")
        print(f"💳 Payment State: {document.get('paymentState')}")
        print("=" * 60 + "\n")

    @staticmethod
    def filter_documents_by_date(
        documents: List[Dict], start_date: str, end_date: str
    ) -> List[Dict]:
        """
        Filter documents by invoice date range

        Args:
            documents: List of documents
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Filtered list of documents
        """
        filtered = []
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        for doc in documents:
            if doc.get("invoiceDate"):
                inv_date = datetime.fromisoformat(
                    doc["invoiceDate"].replace("Z", "+00:00")
                )
                if start <= inv_date <= end:
                    filtered.append(doc)

        return filtered

    @staticmethod
    def filter_documents_by_company(
        documents: List[Dict], company_name: str
    ) -> List[Dict]:
        """Filter documents by company name"""
        return [doc for doc in documents if doc.get("companyName") == company_name]

    @staticmethod
    def filter_documents_by_stage(documents: List[Dict], stage: str) -> List[Dict]:
        """Filter documents by current stage"""
        return [doc for doc in documents if doc.get("currentStage") == stage]

    @staticmethod
    def export_to_csv(documents: List[Dict], output_path: str) -> None:
        """Export documents to CSV"""
        import csv

        if not documents:
            print("No documents to export")
            return

        # Define fields to export
        fields = [
            "documentId",
            "simpleName",
            "companyName",
            "flowName",
            "currentStage",
            "invoiceDate",
            "invoiceNumber",
            "totalGross",
            "totalNet",
            "currencyCode",
            "supplierName",
            "paymentState",
        ]

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(documents)

            print(f"Exported {len(documents)} documents to {output_path}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
