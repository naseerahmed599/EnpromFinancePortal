import msal
import requests
import pandas as pd
import streamlit as st
import os

class DataverseClient:
    def __init__(self, resource_url, tenant_id=None, client_id=None, client_secret=None):
        """
        Initialize the Dataverse Client.
        
        Args:
            resource_url: The base URL of the Dataverse environment (e.g., https://orgXXXXXXXX.crm4.dynamics.com)
            tenant_id: Azure AD Tenant ID
            client_id: Azure App Registration Client ID
            client_secret: Azure App Registration Client Secret
        """
        self.resource_url = resource_url.rstrip('/')
        self.api_url = f"{self.resource_url}/api/data/v9.2"
        self.tenant_id = tenant_id or os.getenv("DATAVERSE_TENANT_ID")
        self.client_id = client_id or os.getenv("DATAVERSE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("DATAVERSE_CLIENT_SECRET")
        self.token = None

    def _get_access_token(self):
        """Authenticate and get an access token using MSAL."""
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            st.error("Dataverse credentials missing. Please check your configuration.")
            return None

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )
        
        scope = [f"{self.resource_url}/.default"]
        
        result = app.acquire_token_for_client(scopes=scope)
        
        if result and "access_token" in result:
            return result["access_token"]
        else:
            error_desc = result.get('error_description', 'Unknown error') if result else 'No response from auth service'
            st.error(f"Failed to acquire token: {error_desc}")
            return None

    def get_table_data(self, logical_name, select_fields=None, filter_query=None):
        """
        Fetch data from a Dataverse table.
        """
        if not self.token:
            self.token = self._get_access_token()
            
        if not self.token:
            return pd.DataFrame()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Prefer": "odata.include-annotations=\"*\""
        }

        names_to_try = [logical_name, f"{logical_name}s"]
        
        last_error = None
        for name in names_to_try:
            url = f"{self.api_url}/{name}"
            params = {}
            if select_fields:
                params["$select"] = ",".join(select_fields)
            if filter_query:
                params["$filter"] = filter_query

            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if 'value' in data:
                        return pd.DataFrame(data['value'])
                else:
                    last_error = f"{response.status_code} {response.reason} for {url}"
            except Exception as e:
                last_error = str(e)

        st.error(f"Failed to find table data. Last error: {last_error}")
        self.list_available_tables()
        return pd.DataFrame()

    def list_available_tables(self):
        """Helper to list available entity sets for debugging name issues."""
        if not self.token:
            self.token = self._get_access_token()
        
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        try:
            response = requests.get(self.api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                entities = sorted([e['name'] for e in data.get('value', [])])
                
                st.markdown("### 🔍 Technical Help: Find the correct Table Name")
                st.write("We couldn't find the table with the name you provided. Please look for your table in the list below and copy the exact name shown.")
                
                relevant = [e for e in entities if "konto" in e.lower() or "finance" in e.lower()]
                if relevant:
                    st.success(f"Suggested matches found: `{', '.join(relevant)}`")
                
                with st.expander("Show all available table names"):
                    st.write(entities)
            else:
                st.error(f"Could not retrieve table list from API. Status: {response.status_code}")
        except Exception as e:
            st.error(f"Error listing tables: {e}")
