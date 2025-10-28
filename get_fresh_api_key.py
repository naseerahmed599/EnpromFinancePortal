"""
Generate a fresh API key using authentication
"""

from flowwer_api_client import FlowwerAPIClient

# Initialize without API key
client = FlowwerAPIClient(api_key=None)

print("🔐 Authenticating to get fresh API key...")
print()

# Authenticate to get new API key
success = client.authenticate("o.heinke@enprom.com", "MasterHuman_2025")

if success:
    print()
    print("=" * 60)
    print("✅ SUCCESS!")
    print("=" * 60)
    print(f"New API Key: {client.api_key}")
    print("=" * 60)
    print()
    print("Now testing with the new key...")
    print()

    # Test with new key
    companies = client.get_companies_with_flows()

    if companies:
        print(f"\n✅ API key works! Found {len(companies)} company/flow combinations")
    else:
        print("\n❌ API key doesn't work")
else:
    print("\n❌ Authentication failed")
