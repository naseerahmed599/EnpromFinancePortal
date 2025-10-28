"""
Quick test script to verify the Flowwer API client works with direct API key
"""

from flowwer_api_client import FlowwerAPIClient

# Initialize client with API key (just like Postman)
client = FlowwerAPIClient()

print("🔑 API Key:", client.api_key[:20] + "...")
print("🌐 Base URL:", client.base_url)
print()

# Test 1: Get Companies and Flows
print("=" * 60)
print("TEST 1: Getting Companies and Flows")
print("=" * 60)
companies = client.get_companies_with_flows()

if companies:
    print(f"\n✅ Success! Found {len(companies)} company/flow combinations:")
    for i, comp in enumerate(companies[:3], 1):  # Show first 3
        print(
            f"\n{i}. Company: {comp.get('companyName')} (ID: {comp.get('companyId')})"
        )
        print(f"   Flow: {comp.get('flowName')} (ID: {comp.get('flowId')})")
else:
    print("\n❌ Failed to get companies")

# Test 2: Get All Documents
print("\n" + "=" * 60)
print("TEST 2: Getting All Documents (unprocessed)")
print("=" * 60)
documents = client.get_all_documents(include_processed=False, include_deleted=False)

if documents:
    print(f"\n✅ Success! Found {len(documents)} documents")
    print(f"\nFirst document:")
    if len(documents) > 0:
        doc = documents[0]
        print(f"  - ID: {doc.get('documentId')}")
        print(f"  - Name: {doc.get('simpleName')}")
        print(f"  - Company: {doc.get('companyName')}")
        print(f"  - Stage: {doc.get('currentStage')}")
        print(f"  - Total: {doc.get('totalGross')} {doc.get('currencyCode')}")
else:
    print("\n❌ Failed to get documents")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
