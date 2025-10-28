"""
Test script for Flowwer API Client
"""

from flowwer_api_client import FlowwerAPIClient, DocumentHelper


def main():
    # Initialize the client
    client = FlowwerAPIClient()

    # Credentials
    # Option 1: Use pre-generated API key (recommended)
    USE_API_KEY = True
    API_KEY = "MXrKdv77r3lTlPzdc8N8mjdT5YzA87iL"

    # Option 2: Generate new API key via authentication
    USERNAME = "o.heinke@enprom.com"
    PASSWORD = "MasterHuman_2025"

    if USE_API_KEY:
        print("🔑 Using pre-generated API key...")
        client.api_key = API_KEY
        client.session.headers.update({"X-FLOWWER-ApiKey": API_KEY})
        print(f"✅ API Key set: {API_KEY[:20]}...")
    else:
        print("🔐 Authenticating to generate new API key...")
        if not client.authenticate(USERNAME, PASSWORD):
            print("❌ Authentication failed. Exiting.")
            return

    print("\n" + "=" * 60)
    print("FLOWWER API CLIENT - INTERACTIVE MENU")
    print("=" * 60)

    while True:
        print("\nWhat would you like to do?")
        print("1. Get all documents")
        print("2. Get specific document by ID")
        print("3. Get companies and flows")
        print("4. Filter documents by date range")
        print("5. Filter documents by company")
        print("6. Filter documents by stage")
        print("7. Export documents to CSV")
        print("8. Download a document PDF")
        print("9. Upload a document")
        print("0. Exit")

        choice = input("\nEnter your choice (0-9): ").strip()

        if choice == "1":
            print("\n📋 Fetching all documents...")
            include_processed = (
                input("Include processed documents? (y/n): ").lower() == "y"
            )
            include_deleted = input("Include deleted documents? (y/n): ").lower() == "y"

            documents = client.get_all_documents(include_processed, include_deleted)

            if documents:
                print(f"\n✅ Found {len(documents)} documents")
                show_details = input("Show details for first 5? (y/n): ").lower() == "y"

                if show_details:
                    for doc in documents[:5]:
                        DocumentHelper.print_document_summary(doc)

        elif choice == "2":
            doc_id = input("\nEnter document ID: ").strip()
            try:
                doc_id = int(doc_id)
                document = client.get_document(doc_id)
                if document:
                    DocumentHelper.print_document_summary(document)
            except ValueError:
                print("❌ Invalid document ID")

        elif choice == "3":
            print("\n🏢 Fetching companies and flows...")
            companies = client.get_companies_with_flows()

            if companies:
                print(f"\n✅ Found {len(companies)} company/flow combinations:")
                for comp in companies:
                    print(
                        f"  • Company: {comp.get('companyName')} (ID: {comp.get('companyId')})"
                    )
                    print(
                        f"    Flow: {comp.get('flowName')} (ID: {comp.get('flowId')})"
                    )
                    print()

        elif choice == "4":
            print("\n📅 Filter documents by date range")
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()

            documents = client.get_all_documents(include_processed=True)
            if documents:
                filtered = DocumentHelper.filter_documents_by_date(
                    documents, start_date, end_date
                )
                print(f"\n✅ Found {len(filtered)} documents in date range")

                for doc in filtered[:10]:  # Show first 10
                    print(f"  • {doc.get('simpleName')} - {doc.get('invoiceDate')}")

        elif choice == "5":
            print("\n🏢 Filter documents by company")
            company_name = input("Company name: ").strip()

            documents = client.get_all_documents(include_processed=True)
            if documents:
                filtered = DocumentHelper.filter_documents_by_company(
                    documents, company_name
                )
                print(f"\n✅ Found {len(filtered)} documents for {company_name}")

                for doc in filtered[:10]:
                    print(f"  • {doc.get('simpleName')} - {doc.get('invoiceNumber')}")

        elif choice == "6":
            print("\n   Filter documents by stage")
            print(
                "Available stages: Draft, Stage1, Stage2, Stage3, Stage4, Stage5, Rejected, Approved, Processed"
            )
            stage = input("Stage name: ").strip()

            documents = client.get_all_documents(include_processed=True)
            if documents:
                filtered = DocumentHelper.filter_documents_by_stage(documents, stage)
                print(f"\n✅ Found {len(filtered)} documents at {stage}")

                for doc in filtered[:10]:
                    print(f"  • {doc.get('simpleName')} - {doc.get('currentStage')}")

        elif choice == "7":
            print("\n💾 Export documents to CSV")
            output_path = input("Output file path (e.g., documents.csv): ").strip()
            include_processed = (
                input("Include processed documents? (y/n): ").lower() == "y"
            )

            documents = client.get_all_documents(include_processed=include_processed)
            if documents:
                DocumentHelper.export_to_csv(documents, output_path)

        elif choice == "8":
            print("\n  Download document PDF")
            doc_id = input("Document ID: ").strip()

            try:
                doc_id = int(doc_id)
                # First get the document to retrieve uniqueId
                document = client.get_document(doc_id)
                if document:
                    unique_id = document.get("uniqueId")
                    output_path = input("Output path (e.g., document.pdf): ").strip()
                    client.download_document(doc_id, unique_id, output_path)
            except ValueError:
                print("❌ Invalid document ID")

        elif choice == "9":
            print("\n📤 Upload document")
            file_path = input("File path to upload: ").strip()
            flow_id = input("Flow ID (optional, press Enter to skip): ").strip()
            company_id = input("Company ID (optional, press Enter to skip): ").strip()

            flow_id = int(flow_id) if flow_id else None
            company_id = int(company_id) if company_id else None

            result = client.upload_document(
                file_path, flow_id=flow_id, company_id=company_id
            )

        elif choice == "0":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
