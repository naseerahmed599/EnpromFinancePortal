"""
Flowwer API Client
A Python client for interacting with the Flowwer REST API
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime
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

        headers = {"username": username, "password": password}

        try:
            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                self.api_key = response.text.strip('"')  # Remove quotes from response
                self.session.headers.update({"X-FLOWWER-ApiKey": self.api_key})
                print(f"Authentication successful!")
                print(f"🔑 API Key: {self.api_key[:20]}...")
                return True
            else:
                print(f"Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"Error during authentication: {e}")
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

        url = f"{self.base_url}/api/v1/receiptsplittingreport/report"

        # Build filter payload
        payload = {}
        if cost_center:
            payload["costCenter"] = cost_center
        if account:
            payload["account"] = account
        if min_date:
            payload["minDate"] = min_date
        if max_date:
            payload["maxDate"] = max_date
        if company:
            payload["company"] = company

        try:
            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                report = response.json()
                print(f"Retrieved {len(report)} receipt splitting report entries")
                return report
            else:
                print(f"Failed to get receipt splitting report: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting receipt splitting report: {e}")
            return None

    def get_all_cost_centers(self) -> Optional[List[str]]:
        """
        Get a list of all cost centers from documents

        Returns:
            List of cost center strings or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/receiptsplittingreport/costcenters"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                cost_centers = response.json()
                print(f"Retrieved {len(cost_centers)} cost centers")
                return cost_centers
            else:
                print(f"Failed to get cost centers: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting cost centers: {e}")
            return None

    def get_all_accounts(self) -> Optional[List[str]]:
        """
        Get a list of all accounts from documents

        Returns:
            List of account strings or None if failed
        """
        if not self.api_key:
            print("No API key set. Please set api_key or call authenticate().")
            return None

        url = f"{self.base_url}/api/v1/receiptsplittingreport/accounts"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                accounts = response.json()
                print(f"Retrieved {len(accounts)} accounts")
                return accounts
            else:
                print(f"Failed to get accounts: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error getting accounts: {e}")
            return None

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
