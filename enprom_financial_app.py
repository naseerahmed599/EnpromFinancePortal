"""
ENPROM Finance Portal - Business Intelligence
Interactive portal for financial document workflows
"""

# ============================================================================
# CONFIGURATION: Toggle Features for Testing/Development
# ============================================================================
#
# ENABLE_PRODUCTION: Controls visibility of the Test/Comparison page
#   - Set to True: Test section appears in Tools menu, enables data comparison
#   - Set to False: Test section is hidden from navigation and disabled
#   - Use Case: Enable for development/testing, disable for production
#
ENABLE_PRODUCTION = True  # Set to True to enable Comparison section

# ============================================================================

import streamlit as st
import pandas as pd
from flowwer_api_client import FlowwerAPIClient, DocumentHelper
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
import openpyxl
from io import BytesIO
import requests
import os
from styles import (
    get_all_document_page_styles,
    get_page_header_purple,
    get_page_header_cyan,
    get_page_header_rose,
    get_page_header_teal,
    get_page_header_indigo,
    get_page_header_green,
    get_page_header_amber,
    get_page_header_slate,
    get_action_bar_styles,
    get_export_bar_styles,
    get_info_box_styles,
    get_alert_box_styles,
    get_card_styles,
    get_metric_styles,
    get_tab_styles,
    get_theme_text_styles,
    get_section_header_styles,
)
from pages_modules.companies import render_companies_page
from pages_modules.settings import render_settings_page
from pages_modules.download import render_download_page
from pages_modules.upload import render_upload_page
from pages_modules.data_explorer import render_data_explorer_page
from pages_modules.receipt_report import render_receipt_report_page
from pages_modules.approved_docs import render_approved_docs_page
from pages_modules.signable_docs import render_signable_docs_page
from pages_modules.analytics import render_analytics_page
from pages_modules.all_documents import render_all_documents_page
from pages_modules.single_document import render_single_document_page
from pages_modules.data_explorer import render_data_explorer_page


# Helper function to get PLN to EUR exchange rate for a specific date
@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_pln_eur_rate(date_str):
    """
    Get PLN to EUR exchange rate for a specific date using European Central Bank API.
    Falls back to 4.23 if API fails.

    Args:
        date_str: Date string in format YYYY-MM-DD

    Returns:
        float: Exchange rate (PLN per 1 EUR)
    """
    try:
        # ECB API provides EUR as base currency
        # We need PLN/EUR rate (how many PLN for 1 EUR)
        url = f"https://api.frankfurter.app/{date_str}?from=EUR&to=PLN"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            rate = data.get("rates", {}).get("PLN")
            if rate:
                return float(rate)

        # Fallback to default rate
        return 4.23
    except Exception as e:
        # If any error, use fallback rate
        return 4.23


# Helper function to convert DataFrame to Excel
def to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel file bytes"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return output.getvalue()


# Page config
st.set_page_config(
    page_title="ENPROM Finance Portal",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load language file
def load_languages():
    """Load language translations from JSON file"""
    try:
        import os

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        languages_path = os.path.join(script_dir, "languages.json")

        with open(languages_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading languages: {e}")
        return None


# Custom CSS for styling
def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Hide footer */
        footer {visibility: hidden;}
        # header {visibility: hidden;}
        
        /* Modern Sidebar Styling - Works for both light and dark themes */
        [data-testid="stSidebar"] {
            background: linear-gradient(165deg, #2563a8 0%, #1a4d7a 50%, #0f2944 100%);
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
            position: relative !important;
            width: 300px !important;
            height: auto !important;
            box-sizing: border-box !important;
            flex-shrink: 0 !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
            width: 330 !important;
        }
        
        /* Sidebar text colors */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #e8f1ff;
        }
        
        /* App Title Styling */
        [data-testid="stSidebar"] h1 {
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 1.5rem !important;
            padding: 0.5rem 0 0.8rem 0 !important;
            margin-bottom: 0.5rem !important;
            border-bottom: 2px solid rgba(255, 255, 255, 0.15);
            letter-spacing: -0.02em;
        }
        
        /* Section Headers (h3) */
        [data-testid="stSidebar"] h3 {
            color: #7ec8ff !important;
            font-size: 0.7rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            margin-top: 1.8rem !important;
            margin-bottom: 0.8rem !important;
            padding-left: 0.3rem !important;
            opacity: 0.9;
        }
        
        /* Navigation Buttons - Modern Card Style */
        [data-testid="stSidebar"] button {
            border-radius: 10px !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            padding: 0.65rem 1rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: none !important;
            margin-bottom: 0.4rem !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Secondary buttons (inactive) */
        [data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #d4e6f7 !important;
            backdrop-filter: blur(10px);
        }
        
        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.15) !important;
            color: #ffffff !important;
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Primary buttons (active page) */
        [data-testid="stSidebar"] button[kind="primary"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
            border-left: 3px solid #60a5fa !important;
        }
        
        [data-testid="stSidebar"] button[kind="primary"]:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5) !important;
        }
        
        /* Dividers */
        [data-testid="stSidebar"] hr {
            margin: 1.5rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(255, 255, 255, 0.2) 50%, 
                transparent 100%);
        }
        
        /* Quick Stats Panel - Glassmorphism */
        .quick-stats {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0 1.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .quick-stats-title {
            color: #93c5fd;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .quick-stats-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            color: #e0f2fe;
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .quick-stats-item:last-child {
            border-bottom: none;
        }
        
        .quick-stats-value {
            font-weight: 700;
            font-size: 1rem;
            color: #ffffff;
            background: rgba(59, 130, 246, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 8px;
            min-width: 40px;
            text-align: center;
        }
        
        /* Connection Status */
        [data-testid="stSidebar"] .element-container:has(.stSuccess) {
            margin-top: 0.5rem;
        }
        
        [data-testid="stSidebar"] .stSuccess {
            background: rgba(34, 197, 94, 0.15) !important;
            border-left: 3px solid #22c55e !important;
            color: #86efac !important;
            padding: 0.5rem 0.8rem !important;
            border-radius: 8px !important;
            font-size: 0.85rem !important;
        }
        
        /* Common styles for both themes */
        [data-testid="stSidebar"] {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        }
        
        /* Smooth scrolling */
        [data-testid="stSidebar"] > div {
            overflow-y: auto;
            scroll-behavior: smooth;
        }
        
        /* Custom scrollbar for sidebar */
        [data-testid="stSidebar"] > div::-webkit-scrollbar {
            width: 6px;
        }
        
        [data-testid="stSidebar"] > div::-webkit-scrollbar-track {
            background: transparent;
        }
        
        [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }
        
        [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* ====================================================================
           PREMIUM GLOSSY BUTTON STYLING
           ==================================================================== */
        
        /* Primary Buttons - Glossy Blue with 3D effect */
        .stButton > button {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(37, 99, 235, 0.95) 100%) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.75rem !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35),
                        0 2px 4px rgba(0, 0, 0, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button::before {
            content: '' !important;
            position: absolute !important;
            top: -50% !important;
            left: -50% !important;
            width: 200% !important;
            height: 200% !important;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%) !important;
            opacity: 0 !important;
            transition: opacity 0.3s ease !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.95) 0%, rgba(29, 78, 216, 0.95) 100%) !important;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.45),
                        0 4px 8px rgba(0, 0, 0, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        .stButton > button:hover::before {
            opacity: 1 !important;
        }
        
        .stButton > button:active {
            transform: translateY(0px) !important;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        }
        
        /* Download Buttons - Lighter Blue/Gray Color */
        .stDownloadButton > button {
            background: linear-gradient(135deg, rgba(100, 116, 139, 0.85) 0%, rgba(71, 85, 105, 0.85) 100%) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.75rem !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 16px rgba(100, 116, 139, 0.25),
                        0 2px 4px rgba(0, 0, 0, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stDownloadButton > button::before {
            content: '' !important;
            position: absolute !important;
            top: -50% !important;
            left: -50% !important;
            width: 200% !important;
            height: 200% !important;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%) !important;
            opacity: 0 !important;
            transition: opacity 0.3s ease !important;
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, rgba(71, 85, 105, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%) !important;
            box-shadow: 0 8px 24px rgba(100, 116, 139, 0.35),
                        0 4px 8px rgba(0, 0, 0, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        .stDownloadButton > button:hover::before {
            opacity: 1 !important;
        }
        
        .stDownloadButton > button:active {
            transform: translateY(0px) !important;
            box-shadow: 0 2px 8px rgba(100, 116, 139, 0.25),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        }
        
        /* Enhanced Input Styling - Theme Adaptive */
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid rgba(226, 232, 240, 0.8) !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
        }
        
        /* Light theme inputs */
        @media (prefers-color-scheme: light) {
            .stNumberInput > div > div > input,
            .stTextInput > div > div > input {
                background: rgba(255, 255, 255, 0.8) !important;
                border-color: rgba(226, 232, 240, 0.8) !important;
                color: #1e293b !important;
            }
        }
        
        /* Dark theme inputs */
        @media (prefers-color-scheme: dark) {
            .stNumberInput > div > div > input,
            .stTextInput > div > div > input {
                background: rgba(30, 41, 59, 0.8) !important;
                border-color: rgba(71, 85, 105, 0.6) !important;
                color: #e2e8f0 !important;
            }
        }
        
        .stNumberInput > div > div > input:focus,
        .stTextInput > div > div > input:focus {
            border-color: rgba(59, 130, 246, 0.8) !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15),
                        inset 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        }
        
        @media (prefers-color-scheme: light) {
            .stNumberInput > div > div > input:focus,
            .stTextInput > div > div > input:focus {
                background: rgba(255, 255, 255, 0.95) !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .stNumberInput > div > div > input:focus,
            .stTextInput > div > div > input:focus {
                background: rgba(30, 41, 59, 0.95) !important;
            }
        }
        
        /* Date Input Styling - Theme Adaptive */
        .stDateInput > div > div > div > input,
        .stDateInput input,
        div[data-baseweb="input"] input {
            border-radius: 12px !important;
            border: 2px solid rgba(226, 232, 240, 0.8) !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(8px) !important;
            background: rgba(255, 255, 255, 0.8) !important;
            color: #1e293b !important;
        }
        
        .stDateInput > div > div > div > input:focus,
        .stDateInput input:focus,
        div[data-baseweb="input"] input:focus {
            border-color: rgba(59, 130, 246, 0.8) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            outline: none !important;
        }
        
        /* Dark theme date inputs */
        @media (prefers-color-scheme: dark) {
            .stDateInput > div > div > div > input,
            .stDateInput input,
            div[data-baseweb="input"] input {
                background: rgba(30, 41, 59, 0.8) !important;
                border-color: rgba(71, 85, 105, 0.6) !important;
                color: #e2e8f0 !important;
            }
            
            .stDateInput > div > div > div > input:focus,
            .stDateInput input:focus,
            div[data-baseweb="input"] input:focus {
                border-color: rgba(96, 165, 250, 0.8) !important;
                box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15) !important;
            }
        }
        
        /* File Uploader Styling */
        .stDateInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid rgba(226, 232, 240, 0.8) !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
        }
        
        @media (prefers-color-scheme: light) {
            .stDateInput > div > div > input {
                background: rgba(255, 255, 255, 0.8) !important;
                border-color: rgba(226, 232, 240, 0.8) !important;
                color: #1e293b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .stDateInput > div > div > input {
                background: rgba(30, 41, 59, 0.8) !important;
                border-color: rgba(71, 85, 105, 0.6) !important;
                color: #e2e8f0 !important;
            }
        }
        
        .stDateInput > div > div > input:focus {
            border-color: rgba(59, 130, 246, 0.8) !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15),
                        inset 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        }
        
        @media (prefers-color-scheme: light) {
            .stDateInput > div > div > input:focus {
                background: rgba(255, 255, 255, 0.95) !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .stDateInput > div > div > input:focus {
                background: rgba(30, 41, 59, 0.95) !important;
            }
        }
        
        /* File Uploader Styling - Theme Adaptive */
        .stFileUploader > div {
            border-radius: 12px !important;
            border: 2px dashed rgba(226, 232, 240, 0.8) !important;
            padding: 1.5rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
        }
        
        @media (prefers-color-scheme: light) {
            .stFileUploader > div {
                background: rgba(248, 250, 252, 0.8) !important;
                border-color: rgba(226, 232, 240, 0.8) !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .stFileUploader > div {
                background: rgba(30, 41, 59, 0.5) !important;
                border-color: rgba(71, 85, 105, 0.6) !important;
            }
        }
        
        .stFileUploader > div:hover {
            border-color: rgba(59, 130, 246, 0.6) !important;
        }
        
        /* Checkbox Enhancement */
        .stCheckbox {
            padding: 0.5rem 0 !important;
        }
        
        .stCheckbox > label {
            font-weight: 500 !important;
            color: #334155 !important;
        }
        
        /* Select Box Styling - Theme Adaptive */
        .stSelectbox > div > div {
            border-radius: 12px !important;
            border: 2px solid rgba(226, 232, 240, 0.8) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            transition: all 0.3s ease !important;
        }
        
        /* Light theme select box */
        @media (prefers-color-scheme: light) {
            .stSelectbox > div > div {
                background: rgba(255, 255, 255, 0.8) !important;
                border-color: rgba(226, 232, 240, 0.8) !important;
            }
        }
        
        /* Dark theme select box */
        @media (prefers-color-scheme: dark) {
            .stSelectbox > div > div {
                background: rgba(30, 41, 59, 0.8) !important;
                border-color: rgba(71, 85, 105, 0.6) !important;
            }
            
            .stSelectbox > div > div input,
            .stSelectbox > div > div div {
                color: #e2e8f0 !important;
            }
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: rgba(59, 130, 246, 0.8) !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


# Apply custom styling
apply_custom_css()


# Load languages - no caching to allow updates
def get_languages(version=2):  # Increment version to force reload
    return load_languages()


# Clear cache and reload if needed
languages = get_languages()

# Initialize session state
if "client" not in st.session_state:
    # Initialize with API key from secrets (works locally and in Streamlit Cloud)
    api_key = st.secrets.get("flowwer", {}).get("api_key") or os.environ.get(
        "FLOWWER_API_KEY"
    )
    st.session_state.client = FlowwerAPIClient(api_key=api_key)

if "documents" not in st.session_state:
    st.session_state.documents = None

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if "language" not in st.session_state:
    st.session_state.language = "en"  # Default to English


# Get current language translations
def t(key):
    """Get translation for current language"""
    if languages and st.session_state.language in languages:
        keys = key.split(".")
        value = languages[st.session_state.language]
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key  # Return key if translation not found
        return value
    return key


# Early authentication gate: require API key before rendering the app
if not st.session_state.client.api_key:
    # Branded, professional login hero
    st.markdown(
        """
        <style>
            .auth-container{
                max-width: 520px;
                margin: 10vh auto 2rem auto;
                text-align: center;
            }
            .auth-logo-section{
                margin-bottom: 2rem;
                animation: fadeInDown 0.6s ease-out;
            }
            .auth-logo-wrapper{
                display: inline-block;
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                padding: 2.5rem;
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3),
                            0 8px 16px rgba(0, 0, 0, 0.1),
                            inset 0 1px 0 rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.15);
                position: relative;
                overflow: hidden;
            }
            .auth-logo-wrapper::before{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                animation: shimmer 3s infinite;
            }
            .auth-logo-inner{
                background: #ffffff;
                border-radius: 16px;
                padding: 1.5rem 2rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
            }
            .auth-logo-inner img{
                height: 48px;
                max-width: 200px;
                object-fit: contain;
                display: block;
            }
            .auth-title-section{
                margin-top: 1.5rem;
                animation: fadeInUp 0.6s ease-out 0.2s both;
            }
            .auth-main-title{
                font-size: 2.25rem;
                font-weight: 800;
                background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0 0 0.5rem 0;
                letter-spacing: -0.5px;
            }
            .auth-subtitle{
                font-size: 1rem;
                color: #64748b;
                font-weight: 500;
                margin: 0;
            }
            .auth-divider{
                height: 1px;
                background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
                margin: 2rem 0 1.5rem 0;
            }
            @keyframes fadeInDown{
                from{opacity: 0; transform: translateY(-20px);}
                to{opacity: 1; transform: translateY(0);}
            }
            @keyframes fadeInUp{
                from{opacity: 0; transform: translateY(20px);}
                to{opacity: 1; transform: translateY(0);}
            }
            @keyframes shimmer{
                0%{left: -100%;}
                100%{left: 100%;}
            }
        </style>
        <div class="auth-container">
            <div class="auth-logo-section">
                <div class="auth-logo-wrapper">
                    <div class="auth-logo-inner">
                        <img src="https://enprom.com/wp-content/uploads/2020/12/xlogo-poziome.png.pagespeed.ic.jXuMlmU90u.webp" alt="ENPROM" />
                    </div>
                </div>
            </div>
            <div class="auth-title-section">
                <h1 class="auth-main-title">Finance Portal</h1>
                <p class="auth-subtitle">Secure authentication required</p>
            </div>
            <div class="auth-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Additional scoped styles for centered input and primary button color
    st.markdown(
        """
        <style>
            /* Beautiful gradient background for login page */
            .stApp {
                background: linear-gradient(135deg, 
                    #f8fafc 0%, 
                    #f1f5f9 25%, 
                    #e0e7ff 50%, 
                    #ede9fe 75%, 
                    #faf5ff 100%) !important;
                background-attachment: fixed !important;
            }
            
            /* Centered layout helpers */
            .block-container{
                padding-top: 2rem;
                background: transparent !important;
            }
            
            /* Remove red border from input on focus */
            input[type="password"]:focus,
            input[type="text"]:focus,
            div[data-baseweb="input"] input:focus{
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 1px #6366f1 !important;
                outline: none !important;
            }
            
            /* Style input container */
            div[data-baseweb="input"]{
                border-radius: 12px !important;
                border: 2px solid #e2e8f0 !important;
                transition: all 0.2s ease !important;
                background: white !important;
            }
            
            div[data-baseweb="input"]:focus-within{
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
            }
            
            /* Primary button theme to match app - indigo/purple gradient */
            div.stButton > button[kind="primary"],
            div.stButton > button[data-testid="baseButton-primary"]{
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
                color: #fff !important; 
                border: 0 !important;
                box-shadow: 0 8px 18px rgba(79,70,229,.25) !important;
                font-weight: 600 !important;
                border-radius: 12px !important;
                padding: 0.75rem 2rem !important;
                transition: all 0.2s ease !important;
            }
            div.stButton > button[kind="primary"]:hover,
            div.stButton > button[data-testid="baseButton-primary"]:hover{
                transform: translateY(-1px);
                box-shadow: 0 12px 28px rgba(79,70,229,.35) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Centered input
    input_cols = st.columns([1, 2, 1])
    with input_cols[1]:
        new_api_key = st.text_input(
            "API Key",
            value="",
            type="password",
            placeholder="Paste your Flowwer API key",
            key="startup_api_key",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Centered primary button
    btn_cols = st.columns([1.5, 1, 1.5])
    with btn_cols[1]:
        submit = st.button(
            "Access",
            type="primary",
            key="btn_startup_save_key",
            use_container_width=True,
        )

    if submit:
        if not new_api_key:
            st.warning("Please enter a valid API key.")
        else:
            st.session_state.client.api_key = new_api_key
            st.session_state.client.session.headers.update(
                {"X-FLOWWER-ApiKey": new_api_key}
            )
            st.success(
                t("messages.api_key_updated") if callable(t) else "API key saved."
            )
            st.rerun()

    st.stop()


# Sidebar for navigation
with st.sidebar:
    # Company logo
    st.image(
        "https://enprom.com/wp-content/uploads/2020/12/xlogo-poziome.png.pagespeed.ic.jXuMlmU90u.webp",
        use_container_width=True,
    )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # App title and branding
    st.title("ENPROM Finance Portal")

    # Language selector - elegant selectbox
    current_lang = st.session_state.language
    lang_options = {"en": "🇬🇧 English", "de": "🇩🇪 Deutsch", "pl": "🇵🇱 Polski"}

    selected_lang = st.selectbox(
        "Language / Sprache / Język",
        options=["en", "de", "pl"],
        format_func=lambda x: lang_options[x],
        index=0 if current_lang == "en" else (1 if current_lang == "de" else 2),
        key="language_selector",
        label_visibility="collapsed",
    )

    # Update language if changed
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.session_state.current_page = None
        st.rerun()

    st.markdown("---")

    # Quick stats panel
    if "documents" in st.session_state and st.session_state.documents:
        docs = st.session_state.documents
        stage_counts = {}
        for doc in docs:
            stage = doc.get("currentStage", "Unknown")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

        # Calculate counts based on actual stage values
        approved_count = stage_counts.get("Approved", 0)
        # Pending includes Stage1 through Stage5
        pending_count = sum(stage_counts.get(f"Stage{i}", 0) for i in range(1, 6))
        unstarted_count = stage_counts.get("Draft", 0)

        st.markdown(
            """
        <div class="quick-stats">
            <div class="quick-stats-title">{}</div>
            <div class="quick-stats-item">
                <span>{}</span>
                <span class="quick-stats-value">{}</span>
            </div>
            <div class="quick-stats-item">
                <span>{}</span>
                <span class="quick-stats-value">{}</span>
            </div>
            <div class="quick-stats-item">
                <span>{}</span>
                <span class="quick-stats-value">{}</span>
            </div>
            <div class="quick-stats-item">
                <span>{}</span>
                <span class="quick-stats-value">{}</span>
            </div>
        </div>
        """.format(
                t("quick_stats.title"),
                t("quick_stats.total_documents"),
                len(docs),
                t("quick_stats.approved"),
                approved_count,
                t("quick_stats.pending_review"),
                pending_count,
                t("quick_stats.in_draft"),
                unstarted_count,
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")

    # Navigation with grouped sections
    st.markdown(f"### 📁 {t('nav_sections.documents')}")

    # Initialize page selection state with current language
    if "current_page" not in st.session_state or st.session_state.current_page is None:
        st.session_state.current_page = "📋 " + t("pages.all_documents")

    # Documents section - rebuild options with current language
    doc_options = [
        ("all_documents", "📋 " + t("pages.all_documents"), t("pages.all_documents")),
        (
            "single_document",
            "🔎 " + t("pages.single_document"),
            t("pages.single_document"),
        ),
        ("approved_docs", "✅ " + t("pages.approved_docs"), t("pages.approved_docs")),
        ("signable_docs", "⏳ " + t("pages.signable_docs"), t("pages.signable_docs")),
    ]

    for key, page_key, label in doc_options:
        if st.button(
            label,
            use_container_width=True,
            type=(
                "primary" if st.session_state.current_page == page_key else "secondary"
            ),
            key=f"nav_doc_{key}_{st.session_state.language}",
        ):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown(f"### 📊 {t('nav_sections.reports_analytics')}")

    # Reports section - rebuild options with current language
    report_options = [
        (
            "receipt_report",
            "📑 " + t("pages.receipt_report"),
            t("pages.receipt_report"),
        ),
        ("analytics", "📈 " + t("pages.analytics"), t("pages.analytics")),
        ("data_explorer", "📊 " + t("pages.data_explorer"), t("pages.data_explorer")),
    ]

    for key, page_key, label in report_options:
        if st.button(
            label,
            use_container_width=True,
            type=(
                "primary" if st.session_state.current_page == page_key else "secondary"
            ),
            key=f"nav_report_{key}_{st.session_state.language}",
        ):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown(f"### 🔧 {t('nav_sections.tools')}")

    # Tools section - rebuild options with current language
    tool_options = [
        ("companies", "🏢 " + t("pages.companies"), t("pages.companies")),
        ("download", "  " + t("pages.download"), t("pages.download")),
        ("upload", "📤 " + t("pages.upload"), t("pages.upload")),
        ("test", "🧪 " + t("pages.test"), t("pages.test")),
        ("settings", "⚙️ " + t("pages.settings"), t("pages.settings")),
    ]

    for key, page_key, label in tool_options:
        if st.button(
            label,
            use_container_width=True,
            type=(
                "primary" if st.session_state.current_page == page_key else "secondary"
            ),
            key=f"nav_tool_{key}_{st.session_state.language}",
        ):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown("---")

    # API Status
    if st.session_state.client.api_key:
        st.success("🔐 " + t("messages.connected"))
        if st.button("Log out", key="btn_logout", use_container_width=True):
            st.session_state.client.api_key = None
            try:
                st.session_state.client.session.headers.pop("X-FLOWWER-ApiKey", None)
            except Exception:
                pass
            st.rerun()
    else:
        st.error("🔐 Not Connected")

# Get the current page
page = st.session_state.current_page

# ============================================================================
# PAGE: ALL DOCUMENTS
# ============================================================================
if page == "📋 " + t("pages.all_documents"):
    render_all_documents_page(
        st.session_state.client, t, get_all_document_page_styles, to_excel
    )
# PAGE: SINGLE DOCUMENT
# ============================================================================
elif page == "🔎 " + t("pages.single_document"):
    render_single_document_page(
        st.session_state.client,
        t,
        get_page_header_purple,
        get_action_bar_styles,
        get_info_box_styles,
        get_card_styles,
        get_metric_styles,
        get_tab_styles,
        get_theme_text_styles,
        to_excel,
    )

    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-purple" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(139, 92, 246, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(139, 92, 246, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">🔎</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('single_document_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">View detailed information about a specific document</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Search panel
    st.markdown("### Search by Document ID or Invoice Number")

    col1, col2 = st.columns(2)

    with col1:
        search_type = st.radio(
            "Search by:",
            options=["Document ID", "Invoice Number"],
            horizontal=True,
            help="Choose whether to search by Document ID or Invoice Number",
        )

    with col2:
        pass  # Empty for spacing

    col1, col2 = st.columns([4, 1])

    with col1:
        if search_type == "Document ID":
            search_value = st.number_input(
                "Document ID",
                min_value=1,
                step=1,
                value=1,
                help="Enter the unique document ID to retrieve details",
            )
        else:
            search_value = st.text_input(
                "Invoice Number",
                placeholder="Enter invoice number...",
                help="Enter the invoice number to search for the document",
            )

    with col2:
        # Align button with input field
        st.markdown('<div style="margin-top: 1.85rem;"></div>', unsafe_allow_html=True)
        if st.button(
            "Search",
            type="primary",
            use_container_width=True,
            key="btn_get_document_details",
        ):
            with st.spinner("🔍 Searching..."):
                doc = None

                if search_type == "Document ID":
                    doc = st.session_state.client.get_document(int(search_value))
                    doc_id = int(search_value)
                else:
                    # Search by invoice number - get all documents and filter
                    if search_value:
                        all_docs = st.session_state.client.get_all_documents(
                            include_processed=True
                        )
                        if all_docs:
                            matching_docs = [
                                d
                                for d in all_docs
                                if d.get("invoiceNumber") == search_value
                            ]
                            if matching_docs:
                                doc = matching_docs[0]  # Take first match
                                doc_id = doc.get("documentId")
                            else:
                                st.error(
                                    f"❌ No document found with invoice number: {search_value}"
                                )
                        else:
                            st.error("❌ Failed to retrieve documents")
                    else:
                        st.warning("⚠️ Please enter an invoice number")

                if doc:
                    st.session_state.selected_document = doc
                    # Also get receipt splits (Belegaufteilung)
                    if "doc_id" in locals() and doc_id:
                        splits = st.session_state.client.get_receipt_splits(int(doc_id))
                        st.session_state.receipt_splits = splits if splits else []
                    else:
                        st.session_state.receipt_splits = []

                    if search_type == "Document ID":
                        st.success(f"✅ Document #{doc_id} loaded successfully")
                    else:
                        st.success(
                            f"✅ Document found! (ID: {doc_id}, Invoice: {search_value})"
                        )
                elif search_type == "Document ID":
                    st.error(f"❌ Document #{search_value} not found")

    if st.session_state.selected_document:
        doc = st.session_state.selected_document
        splits = st.session_state.get("receipt_splits", [])

        # Show receipt splits if available
        if splits:
            st.markdown(
                f"""
                <div class="info-box-green">
                    <span style="font-size: 1.25rem;">✅</span>
                    <span style="font-weight: 600;">
                        Found {len(splits)} receipt split(s) (Belegaufteilung) for this document
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander(
                "📊 Receipt Splits / Belegaufteilung - Click to expand", expanded=True
            ):
                for idx, split in enumerate(splits, 1):
                    st.markdown(
                        f"""
                        <div class="info-box-yellow">
                            <h3 style="margin: 0;">📊 Split #{idx}</h3>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        # Try multiple possible field names for cost center
                        cost_center = (
                            split.get("costCenter")
                            or split.get("costcenter")
                            or split.get("CostCenter")
                            or split.get("cost_center")
                            or "N/A"
                        )
                        st.metric("Cost Center", cost_center)
                        st.metric("Net Value", f"€{split.get('netValue', 0):,.2f}")

                    with col2:
                        # Try multiple possible field names for cost unit
                        cost_unit = (
                            split.get("costUnit")
                            or split.get("costunit")
                            or split.get("CostUnit")
                            or split.get("cost_unit")
                            or "N/A"
                        )
                        st.metric("Cost Unit", cost_unit)
                        st.metric("Gross Value", f"€{split.get('grossValue', 0):,.2f}")

                    with col3:
                        st.metric("Tax %", f"{split.get('taxPercent', 0):.1f}%")
                        st.write("**Booking Text:**")
                        st.info(split.get("name", "N/A"))

                    with col4:
                        st.write(
                            "**Invoice Number:**", split.get("invoiceNumber", "N/A")
                        )
                        st.write("**Invoice Date:**", split.get("invoiceDate", "N/A"))
                        st.write("**Payment State:**", split.get("paymentState", "N/A"))

                    # Show all split fields
                    with st.expander(f"🔍 All fields for split #{idx}"):
                        split_df = pd.DataFrame(
                            [
                                {"Field": key, "Value": value}
                                for key, value in split.items()
                            ]
                        )
                        st.dataframe(
                            split_df, use_container_width=True, hide_index=True
                        )

                    if idx < len(splits):
                        st.markdown("---")

                # Download splits
                splits_df = pd.DataFrame(splits)

                col1, col2 = st.columns(2)

                with col1:
                    csv_splits = splits_df.to_csv(index=False)
                    st.download_button(
                        label=t("common.download_csv"),
                        data=csv_splits,
                        file_name=f"document_{doc.get('documentId', 'unknown')}_splits.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with col2:
                    excel_splits = to_excel(splits_df)
                    st.download_button(
                        label=t("common.download_excel"),
                        data=excel_splits,
                        file_name=f"document_{doc.get('documentId', 'unknown')}_splits.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
        else:
            st.markdown(
                f"""
                <div class="info-box-blue" style="
                    background: linear-gradient(135deg, 
                        rgba(255, 255, 255, 0.9) 0%, 
                        rgba(255, 255, 255, 0.7) 50%,
                        rgba(59, 130, 246, 0.06) 100%) !important;
                    backdrop-filter: blur(16px) saturate(180%) !important;
                    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                    border: 1px solid rgba(59, 130, 246, 0.3) !important;
                    border-radius: 16px !important;
                    padding: 1rem !important;
                    margin-bottom: 1rem !important;
                    box-shadow: 
                        0 4px 16px rgba(59, 130, 246, 0.1),
                        0 2px 8px rgba(0, 0, 0, 0.04),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
                ">
                    <span style="font-size: 1.25rem;">ℹ️</span>
                    <span style="color: #1e40af; font-weight: 500;">
                        {t('single_document_page.no_receipt_splits')}
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Document Overview with modern header
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="section-header">
                <div class="section-icon">📋</div>
                <h3>{t('single_document_page.overview')}</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Document ID", doc.get("documentId"))
            st.metric("Stage", doc.get("currentStage", "N/A"))

        with col2:
            st.metric(
                "Total Gross",
                f"{doc.get('totalGross', 0):.2f} {doc.get('currencyCode', 'EUR')}",
            )
            st.metric(
                "Total Net",
                f"{doc.get('totalNet', 0):.2f} {doc.get('currencyCode', 'EUR')}",
            )

        with col3:
            st.metric("Company", doc.get("companyName", "N/A"))
            st.metric("Flow", doc.get("flowName", "N/A"))

        with col4:
            st.metric("Payment State", doc.get("paymentState", "N/A"))
            st.metric("Supplier", doc.get("supplierName", "N/A"))

        # Detailed Information with modern header
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="section-header">
                <h3>Detailed Information</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📋 All Fields", "💰 Financial", "📅 Dates", "👤 Parties", "🔧 Raw JSON"]
        )

        with tab1:
            # Show ALL available fields dynamically from the API response
            st.markdown("**Complete Document Details**")

            def flatten_value(value, indent=0):
                """Flatten nested dictionaries and lists into readable text"""
                if value is None:
                    return "N/A"
                elif isinstance(value, bool):
                    return "✅ Yes" if value else "❌ No"
                elif isinstance(value, dict):
                    # Format dictionary as bullet points
                    items = []
                    for k, v in value.items():
                        if isinstance(v, (dict, list)):
                            items.append(f"  • {k}: {flatten_value(v, indent+1)}")
                        else:
                            items.append(f"  • {k}: {v}")
                    return "\n" + "\n".join(items)
                elif isinstance(value, list):
                    if not value:
                        return "[]"
                    # Format list items
                    items = []
                    for i, item in enumerate(value, 1):
                        if isinstance(item, (dict, list)):
                            items.append(f"  [{i}] {flatten_value(item, indent+1)}")
                        else:
                            items.append(f"  • {item}")
                    return "\n" + "\n".join(items)
                elif isinstance(value, (int, float)):
                    return f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    return str(value)

            # Get ALL keys from the document and display them
            all_fields = {}
            nested_fields = {}  # Store complex fields separately

            for key, value in doc.items():
                # Format the key to be more readable
                readable_key = key.replace("_", " ").replace("  ", " ").title()

                # Check if this is a complex nested field
                if isinstance(value, (dict, list)) and value:
                    nested_fields[readable_key] = value
                    all_fields[readable_key] = flatten_value(value)
                else:
                    all_fields[readable_key] = flatten_value(value)

            # Convert to DataFrame for better display
            df_details = pd.DataFrame(
                [
                    {"Field": key, "Value": value}
                    for key, value in sorted(all_fields.items())
                ]
            )

            st.dataframe(
                df_details, use_container_width=True, hide_index=True, height=600
            )

            st.info(
                f" Showing {len(all_fields)} fields returned by the API ({len(nested_fields)} complex/nested fields)"
            )

            # Show expanded view of complex fields
            if nested_fields:
                with st.expander(
                    f"🔍 Expand Complex Fields ({len(nested_fields)} fields with nested data)"
                ):
                    for field_name, field_value in sorted(nested_fields.items()):
                        st.markdown(f"**{field_name}:**")
                        if isinstance(field_value, dict):
                            # Display as a neat table
                            nested_df = pd.DataFrame(
                                [
                                    {"Property": k, "Value": v}
                                    for k, v in field_value.items()
                                ]
                            )
                            st.dataframe(
                                nested_df, use_container_width=True, hide_index=True
                            )
                        elif isinstance(field_value, list):
                            if field_value and isinstance(field_value[0], dict):
                                # List of dictionaries - show as table
                                st.dataframe(
                                    pd.DataFrame(field_value),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                # Simple list - show as bullet points
                                for item in field_value:
                                    st.write(f"  • {item}")
                        st.markdown("---")

            # Export option
            col1, col2 = st.columns(2)

            with col1:
                csv_data = df_details.to_csv(index=False)
                st.download_button(
                    label=t("common.download_csv"),
                    data=csv_data,
                    file_name=f"document_{doc.get('documentId', 'unknown')}_all_fields.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                excel_data = to_excel(df_details)
                st.download_button(
                    label=t("common.download_excel"),
                    data=excel_data,
                    file_name=f"document_{doc.get('documentId', 'unknown')}_all_fields.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            # Show raw field names for debugging
            with st.expander("🔍 View Raw Field Names (for debugging)"):
                st.code(", ".join(sorted(doc.keys())), language="text")

        with tab2:
            st.markdown("**💰 Financial Information**")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Gross", f"€{doc.get('totalGross', 0):,.2f}")
                st.metric("Total Net", f"€{doc.get('totalNet', 0):,.2f}")
                st.metric("Tax Amount", f"€{doc.get('taxAmount', 0):,.2f}")
                st.write("**Currency:**", doc.get("currencyCode", "EUR"))

            with col2:
                st.metric("Discount Amount", f"€{doc.get('discountAmount', 0):,.2f}")
                st.metric("Discount Rate", f"{doc.get('discountRate', 0):.2f}%")
                st.write("**Payment State:**", doc.get("paymentState", "N/A"))
                st.write("**Payment Method:**", doc.get("paymentMethod", "N/A"))

            st.markdown("---")
            st.write("**Accounting Details:**")

            # First try to get from document object
            cost_center = (
                doc.get("costCenter")
                or doc.get("costcenter")
                or doc.get("CostCenter")
                or doc.get("cost_center")
                or doc.get("kost1")
                or doc.get("KOST1")
            )

            cost_unit = (
                doc.get("costUnit")
                or doc.get("costunit")
                or doc.get("CostUnit")
                or doc.get("cost_unit")
                or doc.get("kost2")
                or doc.get("KOST2")
            )

            booking_text = (
                doc.get("bookingText")
                or doc.get("bookingtext")
                or doc.get("BookingText")
                or doc.get("booking_text")
                or doc.get("name")
            )

            # If not found in document, try to get from first receipt split
            if not cost_center and splits:
                first_split = splits[0]
                cost_center = (
                    first_split.get("costCenter")
                    or first_split.get("costcenter")
                    or first_split.get("CostCenter")
                    or first_split.get("cost_center")
                )

            if not cost_unit and splits:
                first_split = splits[0]
                cost_unit = (
                    first_split.get("costUnit")
                    or first_split.get("costunit")
                    or first_split.get("CostUnit")
                    or first_split.get("cost_unit")
                )

            if not booking_text and splits:
                first_split = splits[0]
                booking_text = (
                    first_split.get("bookingText")
                    or first_split.get("name")
                    or first_split.get("BookingText")
                    or first_split.get("booking_text")
                )

            # Display with indicator if from splits
            if splits and (cost_center or cost_unit or booking_text):
                st.info(" Accounting details from Receipt Splits (Belegaufteilung)")

            st.write("- **Cost Center:**", cost_center or "N/A")
            st.write("- **Cost Unit (KOST2):**", cost_unit or "N/A")
            st.write("- **Booking Text:**", booking_text or "N/A")

            # If there are multiple splits, show a note
            if splits and len(splits) > 1:
                st.warning(
                    f"⚠️ This document has {len(splits)} receipt splits. Values shown are from the first split. Check the Receipt Splits section for all values."
                )

        with tab3:
            st.markdown("**📅 Date Information**")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Invoice Date:**", doc.get("invoiceDate", "N/A"))
                st.write(
                    "**Receipt Date:**",
                    doc.get("receiptDate", doc.get("uploadTime", "N/A")),
                )
                st.write("**Upload Time:**", doc.get("uploadTime", "N/A"))
                st.write("**Due Date:**", doc.get("dueDate", "N/A"))

            with col2:
                st.write("**Payment Date:**", doc.get("paymentDate", "N/A"))
                st.write("**Service Start:**", doc.get("serviceStartDate", "N/A"))
                st.write("**Service End:**", doc.get("serviceEndDate", "N/A"))
                st.write(
                    "**Discount Period End:**", doc.get("discountPeriodEnd", "N/A")
                )

        with tab4:
            st.markdown("**👤 Parties Information**")

            st.write("### Supplier Details")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Name:**", doc.get("supplierName", "N/A"))
                st.write("**VAT ID:**", doc.get("supplierVATId", "N/A"))
                st.write("**Street:**", doc.get("supplierStreet", "N/A"))
                st.write("**City:**", doc.get("supplierCity", "N/A"))

            with col2:
                st.write("**Postal Code:**", doc.get("supplierPostalCode", "N/A"))
                st.write("**Country:**", doc.get("supplierCountry", "N/A"))
                st.write("**IBAN:**", doc.get("iban", "N/A"))
                st.write("**BIC:**", doc.get("bic", "N/A"))

            st.markdown("---")
            st.write("### Company Details")
            st.write("**Company:**", doc.get("companyName", "N/A"))
            st.write("**Flow:**", doc.get("flowName", "N/A"))

        with tab5:
            st.markdown("**🔧 Complete Raw JSON Data**")

            # Show count of fields
            st.info(f"📊 Total fields in API response: {len(doc)}")

            # Search functionality
            search_term = st.text_input(
                "🔍 Search in JSON data:", placeholder="e.g., booking, cost, date"
            )

            if search_term:
                filtered_doc = {
                    k: v
                    for k, v in doc.items()
                    if search_term.lower() in k.lower()
                    or (isinstance(v, str) and search_term.lower() in v.lower())
                }
                st.write(f"Found {len(filtered_doc)} matching fields:")
                st.json(filtered_doc)
            else:
                st.json(doc)

# ============================================================================
# PAGE: COMPANIES & FLOWS
# ============================================================================
elif page == "🏢 " + t("pages.companies"):
    render_companies_page(
        st.session_state.client,
        t,
        get_card_styles,
        get_theme_text_styles,
        get_section_header_styles,
    )

# ============================================================================
# PAGE: DOWNLOAD DOCUMENT
# ============================================================================
elif page == "  " + t("pages.download"):
    render_download_page(
        st.session_state.client,
        t,
        get_page_header_cyan,
        get_action_bar_styles,
        get_info_box_styles,
    )

# ============================================================================
# PAGE: UPLOAD DOCUMENT
# ============================================================================
elif page == "📤 " + t("pages.upload"):
    render_upload_page(
        st.session_state.client, t, get_page_header_rose, get_alert_box_styles
    )

# ============================================================================
# PAGE: DATA EXPLORER
# ============================================================================
elif page == "📊 " + t("pages.data_explorer"):
    render_data_explorer_page(
        st.session_state.client,
        t,
        get_page_header_teal,
        get_export_bar_styles,
        get_card_styles,
        get_action_bar_styles,
        to_excel,
    )

# ============================================================================
# PAGE: RECEIPT SPLITTING REPORT
# ============================================================================
elif page == "📑 " + t("pages.receipt_report"):
    render_receipt_report_page(
        st.session_state.client,
        t,
        get_page_header_indigo,
        get_action_bar_styles,
        get_card_styles,
        to_excel,
    )

# ============================================================================
# PAGE: APPROVED DOCUMENTS
# ============================================================================
elif page == "✅ " + t("pages.approved_docs"):
    render_approved_docs_page(
        st.session_state.client,
        t,
        get_page_header_green,
        get_action_bar_styles,
        to_excel,
    )

# ============================================================================
# PAGE: SIGNABLE DOCUMENTS (PENDING APPROVALS)
# ============================================================================
elif page == "⏳ " + t("pages.signable_docs"):
    render_signable_docs_page(
        st.session_state.client,
        t,
        get_page_header_amber,
        get_action_bar_styles,
        to_excel,
    )

# ============================================================================
# PAGE: ANALYTICS DASHBOARD
# ============================================================================
elif page == "📈 " + t("pages.analytics"):
    render_analytics_page(
        st.session_state.client,
        t,
        get_page_header_amber,
        get_action_bar_styles,
        get_card_styles,
        get_tab_styles,
        get_metric_styles,
        get_theme_text_styles,
        get_section_header_styles,
        to_excel,
    )

# ============================================================================
# PAGE: SETTINGS
# ============================================================================
elif page == "⚙️ " + t("pages.settings"):
    render_settings_page(
        st.session_state.client, t, get_page_header_slate, get_card_styles
    )

# ============================================================================
# PAGE: DATA COMPARISON
# ============================================================================
elif page == "🧪 " + t("pages.test"):
    st.markdown(get_page_header_indigo(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-indigo" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.9) 0%, rgba(79, 70, 229, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 16px rgba(79, 70, 229, 0.25);
            ">
                📊
            </div>
            <div style="flex: 1;">
                <h1 style="margin: 0; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    {t('test_page.title')}
                </h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.7; font-size: 1rem;">
                    {t('test_page.subtitle')}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Step 1: Date Range Selection
    st.markdown(
        """
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">DATE RANGE</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Month and Year selection
    col1, col2, col3, col4 = st.columns(4)

    current_year = datetime.now().year
    current_month = datetime.now().month

    with col1:
        from_month = st.selectbox(
            "From Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=0,
            key="from_month",
        )

    with col2:
        from_year = st.selectbox(
            "From Year",
            options=list(range(2020, current_year + 1)),
            index=3,  # Default to 2023
            key="from_year",
        )

    with col3:
        to_month = st.selectbox(
            "To Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=current_month - 1,
            key="to_month",
        )

    with col4:
        to_year = st.selectbox(
            "To Year",
            options=list(range(2020, current_year + 1)),
            index=len(list(range(2020, current_year + 1)))
            - 1,  # Default to current year
            key="to_year",
        )

    # Convert month/year to dates
    from_date = datetime(from_year, from_month, 1)
    # Get last day of to_month
    if to_month == 12:
        to_date = datetime(to_year, 12, 31)
    else:
        to_date = datetime(to_year, to_month + 1, 1) - timedelta(days=1)

    st.caption(
        f"Selected: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}"
    )

    # Step 2: Load Both Datasets
    st.markdown(
        """
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">LOAD DATA</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # DATEV file path - check if exists locally (for development)
    excel_file_path = "../Financial_Dashboard_Latest.xlsx"

    # File upload option (only visible when ENABLE_PRODUCTION is True for production)
    uploaded_file = None
    if ENABLE_PRODUCTION:
        st.markdown("#### 📁 Data Source")
        uploaded_file = st.file_uploader(
            "Upload DATEV Excel file (or use default file if available)",
            type=["xlsx"],
            help="Upload your DATEV exported Excel file with 'Booking General' sheet",
        )

    # Determine which file to use
    file_to_use = None
    file_source = None

    if uploaded_file is not None:
        file_to_use = uploaded_file
        file_source = "uploaded"
        st.info(f"📤 Using uploaded file: **{uploaded_file.name}**")
    elif os.path.exists(excel_file_path):
        file_to_use = excel_file_path
        file_source = "local"
        st.info(f"📂 Using local file: **{excel_file_path}**")
    else:
        warning_msg = "⚠️ **No Data File Available**\n\n"
        if ENABLE_PRODUCTION:
            warning_msg += (
                "Please upload a DATEV Excel file above, or for local development, "
            )
        else:
            warning_msg += "For local development, "
        warning_msg += f"place `{excel_file_path}` in:\n`{os.getcwd()}`"
        st.warning(warning_msg)

    if st.button(
        "Load Both Datasets",
        key="btn_load_both",
        type="primary",
        use_container_width=True,
        disabled=file_to_use is None,
    ):
        # Clear previous data
        if "excel_data" in st.session_state:
            del st.session_state.excel_data
        if "flowwer_data" in st.session_state:
            del st.session_state.flowwer_data
        if "comparison_results" in st.session_state:
            del st.session_state.comparison_results

        datev_success = False
        flowwer_success = False

        # Step 1: Load DATEV Data
        status_placeholder = st.empty()

        try:
            with st.spinner("Loading DATEV data..."):
                # Load from uploaded file or local file
                if file_source == "uploaded":
                    df_excel = pd.read_excel(
                        uploaded_file,
                        sheet_name="Booking General",
                        engine="openpyxl",
                        header=1,
                    )
                else:  # file_source == "local"
                    df_excel = pd.read_excel(
                        excel_file_path,
                        sheet_name="Booking General",
                        engine="openpyxl",
                        header=1,
                    )

                # Filter by date range
                df_excel["Belegdatum"] = pd.to_datetime(
                    df_excel["Belegdatum"], errors="coerce"
                )
                df_excel = df_excel[
                    (df_excel["Belegdatum"] >= from_date)
                    & (df_excel["Belegdatum"] <= to_date)
                ]
                st.session_state.excel_data = df_excel
                datev_success = True
        except Exception as e:
            status_placeholder.error(f"Error loading DATEV file: {e}")
            datev_success = False

        # Step 2: Load Flowwer API Data (only if DATEV succeeded)
        if datev_success:
            try:
                with st.spinner("Fetching data from Flowwer API..."):
                    report = st.session_state.client.get_receipt_splitting_report(
                        min_date=from_date.isoformat(), max_date=to_date.isoformat()
                    )
                    if report:
                        df_flowwer = pd.DataFrame(report)

                        # Fetch currency codes for all unique documents
                        unique_doc_ids = df_flowwer["documentId"].unique()
                        currency_map = {}

                        with st.spinner(f"Fetching currency information..."):
                            progress_bar = st.progress(0)
                            for i, doc_id in enumerate(unique_doc_ids):
                                try:
                                    doc_details = st.session_state.client.get_document(
                                        doc_id
                                    )
                                    if doc_details and "currencyCode" in doc_details:
                                        currency_map[doc_id] = doc_details[
                                            "currencyCode"
                                        ]
                                    else:
                                        currency_map[doc_id] = "EUR"  # Default to EUR
                                except:
                                    currency_map[doc_id] = (
                                        "EUR"  # Default to EUR on error
                                    )

                                # Update progress every 10 documents
                                if i % 10 == 0:
                                    progress_bar.progress((i + 1) / len(unique_doc_ids))

                            progress_bar.progress(1.0)
                            progress_bar.empty()

                        # Add currency code to dataframe
                        df_flowwer["currencyCode"] = df_flowwer["documentId"].map(
                            currency_map
                        )

                        st.session_state.flowwer_data = df_flowwer

                        # Extract unique cost centers
                        unique_cost_centers = sorted(
                            df_flowwer["costCenter"].dropna().unique().tolist()
                        )
                        st.session_state.available_cost_centers = unique_cost_centers

                        # Show currency breakdown
                        currency_counts = df_flowwer["currencyCode"].value_counts()

                        # Single consolidated success message
                        status_placeholder.success(
                            f"Data loaded: {len(df_excel):,} DATEV rows • "
                            f"{len(df_flowwer):,} Flowwer rows • "
                            f"{len(unique_cost_centers)} cost centers • "
                            f"Currencies: {', '.join([f'{curr} ({count})' for curr, count in currency_counts.items()])}"
                        )
                        flowwer_success = True
                    else:
                        status_placeholder.error("Failed to load data from Flowwer API")
                        flowwer_success = False
            except Exception as e:
                status_placeholder.error(f"Error loading Flowwer data: {e}")
                flowwer_success = False
        else:
            status_placeholder.error(
                "Failed to load data. Please check your settings and try again."
            )

    # Step 4: Select Cost Center (if Flowwer data is loaded)
    if (
        "flowwer_data" in st.session_state
        and st.session_state.flowwer_data is not None
        and "available_cost_centers" in st.session_state
    ):
        st.markdown(
            """
            <div style="
                border-left: 3px solid #6366f1;
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                margin: 2rem 0 1rem 0;
                background: rgba(99, 102, 241, 0.03);
            ">
                <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">FILTER (OPTIONAL)</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_cost_center = st.selectbox(
                "Filter by Cost Center",
                options=["All Cost Centers"] + st.session_state.available_cost_centers,
                key="selected_cost_center",
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if selected_cost_center != "All Cost Centers":
                st.info(f"Filtering: {selected_cost_center}")

    # Step 5: Compare Data
    if (
        "excel_data" in st.session_state
        and st.session_state.excel_data is not None
        and "flowwer_data" in st.session_state
        and st.session_state.flowwer_data is not None
    ):

        st.markdown(
            """
            <div style="
                border-left: 3px solid #6366f1;
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                margin: 2rem 0 1rem 0;
                background: rgba(99, 102, 241, 0.03);
            ">
                <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">COMPARISON</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_excel = st.session_state.excel_data
        df_flowwer = st.session_state.flowwer_data

        # Apply cost center filter if selected
        if (
            "selected_cost_center" in st.session_state
            and st.session_state.selected_cost_center != "All Cost Centers"
        ):
            df_flowwer = df_flowwer[
                df_flowwer["costCenter"] == st.session_state.selected_cost_center
            ].copy()

        # Show data overview
        col1, col2 = st.columns(2)
        with col1:
            st.caption("DATEV Data")
            st.metric("Rows", f"{len(df_excel):,}")

        with col2:
            st.caption("Flowwer Data")
            st.metric("Rows", f"{len(df_flowwer):,}")
            cost_center_filter = st.session_state.get(
                "selected_cost_center", "All Cost Centers"
            )
            if cost_center_filter != "All Cost Centers":
                st.metric("🏢 Filtered CC", cost_center_filter)

        # Comparison button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🔍 Cross-Check Data",
            key="btn_compare",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Cross-checking data..."):
                # Prepare DATEV data - filter out invalid invoice numbers
                df_excel_clean = df_excel.copy()

                # Store in session state for inspector
                st.session_state.df_excel_clean_for_inspector = df_excel_clean.copy()
                df_excel_clean["Invoice_Number"] = (
                    df_excel_clean["Belegfeld 1"].astype(str).str.strip()
                )
                df_excel_clean["Invoice_Date"] = pd.to_datetime(
                    df_excel_clean["Belegdatum"], errors="coerce"
                )
                # Convert cost center to integer to remove .0, then to string
                df_excel_clean["Cost_Center"] = (
                    pd.to_numeric(
                        df_excel_clean["KOST1 - Kostenstelle"], errors="coerce"
                    )
                    .fillna(0)
                    .astype(int)
                    .astype(str)
                    .str.replace("^0$", "", regex=True)
                )

                # Handle Amount column - convert parentheses notation to negative values
                # (182.44) -> -182.44
                # Keep all rows with valid invoice numbers, even if amount is missing
                df_excel_clean["Amount"] = df_excel_clean["Amount"].astype(str)
                # Remove parentheses and make negative if they existed
                df_excel_clean["Amount"] = df_excel_clean["Amount"].apply(
                    lambda x: (
                        -float(
                            x.replace("(", "").replace(")", "").replace(",", "").strip()
                        )
                        if "(" in str(x) and ")" in str(x)
                        else (
                            float(str(x).replace(",", "").strip())
                            if str(x).strip() and str(x) != "nan" and str(x) != "None"
                            else 0
                        )
                    )
                )

                # Only filter out rows WITHOUT a valid invoice number
                # Keep ALL rows that have a valid invoice number, even if other fields are missing
                df_excel_clean = df_excel_clean[
                    (df_excel_clean["Invoice_Number"] != "")
                    & (df_excel_clean["Invoice_Number"] != "0")
                    & (df_excel_clean["Invoice_Number"] != "nan")
                    & (df_excel_clean["Invoice_Number"] != "None")
                    & (df_excel_clean["Invoice_Number"].notna())
                ]

                # Apply cost center filter to DATEV data (same as Flowwer filter)
                if (
                    "selected_cost_center" in st.session_state
                    and st.session_state.selected_cost_center != "All Cost Centers"
                ):
                    df_excel_clean = df_excel_clean[
                        df_excel_clean["Cost_Center"]
                        == st.session_state.selected_cost_center
                    ].copy()

                # Aggregate DATEV data by Invoice Number only
                # Sum ALL amounts for the same invoice, regardless of date/cost center variations
                df_excel_aggregated = (
                    df_excel_clean.groupby(
                        ["Invoice_Number"],
                        as_index=False,
                        dropna=False,
                    )
                    .agg(
                        {
                            "Invoice_Date": "first",  # Take first date
                            "Cost_Center": "first",  # Take first cost center
                            "Amount": "sum",  # Sum all amounts (respects +/-)
                        }
                    )
                    .copy()
                )

                # Prepare Flowwer data
                df_flowwer_clean = df_flowwer.copy()

                # Store original for inspector (before further processing)
                st.session_state.df_flowwer_clean_for_inspector = (
                    df_flowwer_clean.copy()
                )

                # Filter only processed documents
                if "currentStage" in df_flowwer_clean.columns:
                    df_flowwer_clean = df_flowwer_clean[
                        df_flowwer_clean["currentStage"] == "Processed"
                    ].copy()

                df_flowwer_clean["Invoice_Number"] = (
                    df_flowwer_clean["invoiceNumber"].astype(str).str.strip()
                )
                # Parse invoice date from Flowwer (format: DD.MM.YYYY)
                df_flowwer_clean["Invoice_Date"] = pd.to_datetime(
                    df_flowwer_clean["invoiceDate"], format="%d.%m.%Y", errors="coerce"
                )
                df_flowwer_clean["Cost_Center"] = (
                    df_flowwer_clean["costCenter"].astype(str).str.strip()
                )
                df_flowwer_clean["Amount"] = pd.to_numeric(
                    df_flowwer_clean["grossValue"], errors="coerce"
                )

                # Convert PLN to EUR using date-specific exchange rates
                if "currencyCode" in df_flowwer_clean.columns:
                    # Check for both "PL" and "PLN" currency codes
                    pln_mask = (
                        df_flowwer_clean["currencyCode"].str.upper().isin(["PL", "PLN"])
                    )

                    # Apply conversion with date-specific rates
                    for idx in df_flowwer_clean[pln_mask].index:
                        invoice_date = df_flowwer_clean.loc[idx, "Invoice_Date"]
                        if pd.notna(invoice_date):
                            # Convert to datetime if needed and format as string
                            if isinstance(invoice_date, pd.Timestamp):
                                date_str = invoice_date.strftime("%Y-%m-%d")
                            else:
                                date_str = pd.to_datetime(invoice_date).strftime("%Y-%m-%d")  # type: ignore

                            rate = get_pln_eur_rate(date_str)
                            current_amount = float(df_flowwer_clean.loc[idx, "Amount"])  # type: ignore
                            df_flowwer_clean.loc[idx, "Amount"] = current_amount / rate

                # Filter out invalid invoice numbers
                df_flowwer_clean = df_flowwer_clean[
                    (df_flowwer_clean["Invoice_Number"] != "")
                    & (df_flowwer_clean["Invoice_Number"] != "0")
                    & (df_flowwer_clean["Invoice_Number"] != "nan")
                    & (df_flowwer_clean["Invoice_Number"].notna())
                ]

                # Aggregate Flowwer data by Invoice Number only
                df_flowwer_aggregated = (
                    df_flowwer_clean.groupby(
                        ["Invoice_Number"],
                        as_index=False,
                        dropna=False,
                    )
                    .agg(
                        {
                            "Invoice_Date": "first",
                            "Cost_Center": "first",
                            "Amount": "sum",
                        }
                    )
                    .copy()
                )

                st.markdown("### Cross-Check Results")

                # Show filtered data counts
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.info(f"Excel: {len(df_excel_clean):,} raw records")
                with col2:
                    st.info(f"Excel: {len(df_excel_aggregated):,} unique invoices")
                with col3:
                    st.info(f"Flowwer: {len(df_flowwer_clean):,} raw records")
                with col4:
                    st.info(f"Flowwer: {len(df_flowwer_aggregated):,} unique invoices")

                # Cross-check: For each Flowwer record, check if it exists in Excel with same amount and cost center
                st.markdown("### Cross-Checking Flowwer Records Against Excel")

                results = []
                for idx, flowwer_row in df_flowwer_aggregated.iterrows():
                    invoice_num = flowwer_row["Invoice_Number"]
                    flowwer_date = flowwer_row["Invoice_Date"]
                    flowwer_cc = flowwer_row["Cost_Center"]
                    flowwer_amount = flowwer_row["Amount"]

                    # Find matching invoice in aggregated Excel data
                    excel_matches = df_excel_aggregated[
                        df_excel_aggregated["Invoice_Number"] == invoice_num
                    ]

                    if len(excel_matches) == 0:
                        # Not found in DATEV
                        results.append(
                            {
                                "Invoice_Number": invoice_num,
                                "Status": "Not in DATEV",
                                "Flowwer_Date": flowwer_date,
                                "DATEV_Date": None,
                                "Date_Match": False,
                                "Flowwer_CC": flowwer_cc,
                                "DATEV_CC": "",
                                "CC_Match": False,
                                "Flowwer_Amount": flowwer_amount,
                                "DATEV_Amount": None,
                                "Amount_Match": False,
                                "Amount_Diff": None,
                            }
                        )
                    else:
                        # Found in Excel - check if any aggregated row matches date, cost center and amount
                        exact_match = False
                        best_match = None

                        for _, excel_row in excel_matches.iterrows():
                            excel_date = excel_row["Invoice_Date"]
                            excel_cc = excel_row["Cost_Center"]
                            excel_amount = excel_row["Amount"]

                            # Check if Excel amount is zero (invoice was paid, status not updated)
                            excel_is_paid = (
                                abs(excel_amount) <= 0.01
                                if pd.notna(excel_amount)
                                else False
                            )

                            # Compare absolute values for amounts
                            amount_diff = (
                                abs(abs(flowwer_amount) - abs(excel_amount))
                                if pd.notna(excel_amount)
                                else None
                            )

                            # Compare dates (only date part, ignore time)
                            date_match = False
                            if pd.notna(flowwer_date) and pd.notna(excel_date):
                                date_match = flowwer_date.date() == excel_date.date()

                            cc_match = str(flowwer_cc) == str(excel_cc)
                            amount_match = (
                                amount_diff is not None and amount_diff <= 0.01
                            )

                            # If DATEV amount is zero (paid), consider it a match regardless of Flowwer amount
                            # (invoice was paid, status not updated yet in Flowwer)
                            # Otherwise, only require amount to match - date and cost center can differ
                            # (cost center may change after payment is processed)
                            if excel_is_paid or amount_match:
                                exact_match = True
                                # Update best_match with this match
                                best_match = {
                                    "datev_date": excel_date,
                                    "datev_cc": excel_cc,
                                    "datev_amount": excel_amount,
                                    "date_match": date_match,
                                    "cc_match": cc_match,
                                    "amount_match": amount_match,
                                    "amount_diff": amount_diff,
                                }
                                break

                            # Keep track of best match (even if not exact)
                            if best_match is None:
                                best_match = {
                                    "datev_date": excel_date,
                                    "datev_cc": excel_cc,
                                    "datev_amount": excel_amount,
                                    "datev_is_paid": excel_is_paid,
                                    "date_match": date_match,
                                    "cc_match": cc_match,
                                    "amount_match": amount_match,
                                    "amount_diff": amount_diff,
                                }

                        if exact_match:
                            # Determine status based on whether invoice was paid
                            status = (
                                "Paid (DATEV)"
                                if best_match and best_match.get("datev_is_paid", False)
                                else "Match"
                            )

                            results.append(
                                {
                                    "Invoice_Number": invoice_num,
                                    "Status": status,
                                    "Flowwer_Date": flowwer_date,
                                    "DATEV_Date": excel_date if best_match else None,
                                    "Date_Match": (
                                        best_match["date_match"]
                                        if best_match
                                        else False
                                    ),
                                    "Flowwer_CC": flowwer_cc,
                                    "DATEV_CC": (
                                        best_match["datev_cc"] if best_match else ""
                                    ),
                                    "CC_Match": (
                                        best_match["cc_match"] if best_match else False
                                    ),
                                    "Flowwer_Amount": flowwer_amount,
                                    "DATEV_Amount": (
                                        best_match["datev_amount"]
                                        if best_match
                                        else None
                                    ),
                                    "Amount_Match": (
                                        best_match["amount_match"]
                                        if best_match
                                        else False
                                    ),
                                    "Amount_Diff": (
                                        best_match["amount_diff"]
                                        if best_match
                                        else None
                                    ),
                                }
                            )
                        elif best_match is not None:
                            # Mismatch
                            results.append(
                                {
                                    "Invoice_Number": invoice_num,
                                    "Status": "Mismatch",
                                    "Flowwer_Date": flowwer_date,
                                    "DATEV_Date": best_match["datev_date"],
                                    "Date_Match": best_match["date_match"],
                                    "Flowwer_CC": flowwer_cc,
                                    "DATEV_CC": best_match["datev_cc"],
                                    "CC_Match": best_match["cc_match"],
                                    "Flowwer_Amount": flowwer_amount,
                                    "DATEV_Amount": best_match["datev_amount"],
                                    "Amount_Match": best_match["amount_match"],
                                    "Amount_Diff": best_match["amount_diff"],
                                }
                            )
                        else:
                            # Found in DATEV but couldn't create best_match (shouldn't happen)
                            results.append(
                                {
                                    "Invoice_Number": invoice_num,
                                    "Status": "Mismatch",
                                    "Flowwer_Date": flowwer_date,
                                    "DATEV_Date": None,
                                    "Date_Match": False,
                                    "Flowwer_CC": flowwer_cc,
                                    "DATEV_CC": "",
                                    "CC_Match": False,
                                    "Flowwer_Amount": flowwer_amount,
                                    "DATEV_Amount": None,
                                    "Amount_Match": False,
                                    "Amount_Diff": None,
                                }
                            )

                # Create results dataframe
                df_results = pd.DataFrame(results)

                # Store results in session state so they persist across reruns
                st.session_state.comparison_results = df_results
                st.session_state.df_excel_aggregated = df_excel_aggregated
                st.session_state.df_flowwer_aggregated = df_flowwer_aggregated

        # Display results if they exist in session state (persists across reruns)
        if (
            "comparison_results" in st.session_state
            and st.session_state.comparison_results is not None
        ):
            df_results = st.session_state.comparison_results

            # Calculate statistics with enhanced categorization
            total_checked = len(df_results)
            exact_matches = len(df_results[df_results["Status"] == "Match"])
            paid_invoices = len(df_results[df_results["Status"] == "Paid (DATEV)"])
            mismatches = len(df_results[df_results["Status"] == "Mismatch"])
            not_in_datev = len(df_results[df_results["Status"] == "Not in DATEV"])

            # Display summary statistics
            st.markdown(
                """
                <div style="
                    border-left: 3px solid #6366f1;
                    padding: 0.75rem 1.25rem;
                    border-radius: 8px;
                    margin: 2rem 0 1rem 0;
                    background: rgba(99, 102, 241, 0.03);
                ">
                    <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">RESULTS</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Exact Matches",
                    f"{exact_matches:,}",
                    delta=f"{(exact_matches/total_checked*100):.1f}%",
                )
            with col2:
                st.metric(
                    "Paid (DATEV)",
                    f"{paid_invoices:,}",
                    delta=f"{(paid_invoices/total_checked*100):.1f}%",
                    help="Invoices with zero balance in DATEV (payment completed)",
                )
            with col3:
                st.metric(
                    "Mismatches",
                    f"{mismatches:,}",
                    delta=f"{(mismatches/total_checked*100):.1f}%",
                    delta_color="inverse",
                )
            with col4:
                st.metric(
                    "Not in DATEV",
                    f"{not_in_datev:,}",
                    delta=f"{(not_in_datev/total_checked*100):.1f}%",
                    delta_color="inverse",
                )

            # Detailed breakdown of mismatches
            st.markdown(
                """
                <div style="
                    border-left: 3px solid #f59e0b;
                    padding: 0.75rem 1.25rem;
                    border-radius: 8px;
                    margin: 2rem 0 1rem 0;
                    background: rgba(245, 158, 11, 0.03);
                ">
                    <h3 style="margin: 0; color: #f59e0b; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">MISMATCHES</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            mismatch_df = df_results[df_results["Status"] == "Mismatch"]

            if len(mismatch_df) > 0:
                date_only_mismatch = len(
                    mismatch_df[
                        ~mismatch_df["Date_Match"]
                        & mismatch_df["CC_Match"]
                        & mismatch_df["Amount_Match"]
                    ]
                )
                cc_only_mismatch = len(
                    mismatch_df[
                        mismatch_df["Date_Match"]
                        & ~mismatch_df["CC_Match"]
                        & mismatch_df["Amount_Match"]
                    ]
                )
                amount_only_mismatch = len(
                    mismatch_df[
                        mismatch_df["Date_Match"]
                        & mismatch_df["CC_Match"]
                        & ~mismatch_df["Amount_Match"]
                    ]
                )
                multiple_mismatch = len(
                    mismatch_df[
                        ~(
                            mismatch_df["Date_Match"]
                            & mismatch_df["CC_Match"]
                            & mismatch_df["Amount_Match"]
                        )
                        & ~(
                            ~mismatch_df["Date_Match"]
                            & mismatch_df["CC_Match"]
                            & mismatch_df["Amount_Match"]
                        )
                        & ~(
                            mismatch_df["Date_Match"]
                            & ~mismatch_df["CC_Match"]
                            & mismatch_df["Amount_Match"]
                        )
                        & ~(
                            mismatch_df["Date_Match"]
                            & mismatch_df["CC_Match"]
                            & ~mismatch_df["Amount_Match"]
                        )
                    ]
                )

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Date Only", f"{date_only_mismatch:,}")
                with col2:
                    st.metric("Cost Center Only", f"{cc_only_mismatch:,}")
                with col3:
                    st.metric("Amount Only", f"{amount_only_mismatch:,}")
                with col4:
                    st.metric("Multiple Fields", f"{multiple_mismatch:,}")

                # Add drill-down inspector for specific invoices
                st.markdown(
                    """
                    <div style="
                        border-left: 3px solid #6366f1;
                        padding: 0.75rem 1.25rem;
                        border-radius: 8px;
                        margin: 2rem 0 1rem 0;
                        background: rgba(99, 102, 241, 0.03);
                    ">
                        <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">INSPECTOR</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns([3, 1])
                with col1:
                    inspect_invoice = st.text_input(
                        "Invoice Number to Inspect",
                        placeholder="e.g., 121/2025 or 00238/25",
                        key="inspect_invoice",
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    inspect_button = st.button("🔎 Inspect", type="primary")

                if inspect_button and inspect_invoice:
                    inspect_invoice = inspect_invoice.strip()

                    # Process Excel data for inspector
                    if "df_excel_clean_for_inspector" in st.session_state:
                        df_excel_inspect = (
                            st.session_state.df_excel_clean_for_inspector.copy()
                        )

                        # Apply same transformations
                        df_excel_inspect["Invoice_Number"] = (
                            df_excel_inspect["Belegfeld 1"].astype(str).str.strip()
                        )
                        df_excel_inspect["Invoice_Date"] = pd.to_datetime(
                            df_excel_inspect["Belegdatum"], errors="coerce"
                        )
                        df_excel_inspect["Cost_Center"] = (
                            pd.to_numeric(
                                df_excel_inspect["KOST1 - Kostenstelle"],
                                errors="coerce",
                            )
                            .fillna(0)
                            .astype(int)
                            .astype(str)
                            .str.replace("^0$", "", regex=True)
                        )

                        # Handle Amount column
                        df_excel_inspect["Amount"] = df_excel_inspect["Amount"].astype(
                            str
                        )
                        df_excel_inspect["Amount"] = df_excel_inspect["Amount"].apply(
                            lambda x: (
                                -float(
                                    x.replace("(", "")
                                    .replace(")", "")
                                    .replace(",", "")
                                    .strip()
                                )
                                if "(" in str(x) and ")" in str(x)
                                else (
                                    float(str(x).replace(",", "").strip())
                                    if str(x).strip()
                                    and str(x) != "nan"
                                    and str(x) != "None"
                                    else 0
                                )
                            )
                        )

                        excel_raw_records = df_excel_inspect[
                            df_excel_inspect["Invoice_Number"] == inspect_invoice
                        ]
                    else:
                        excel_raw_records = pd.DataFrame()

                    # Process Flowwer data for inspector
                    if "df_flowwer_clean_for_inspector" in st.session_state:
                        df_flowwer_inspect = (
                            st.session_state.df_flowwer_clean_for_inspector.copy()
                        )

                        # Filter processed only
                        if "currentStage" in df_flowwer_inspect.columns:
                            df_flowwer_inspect = df_flowwer_inspect[
                                df_flowwer_inspect["currentStage"] == "Processed"
                            ].copy()

                        df_flowwer_inspect["Invoice_Number"] = (
                            df_flowwer_inspect["invoiceNumber"].astype(str).str.strip()
                        )
                        df_flowwer_inspect["Invoice_Date"] = pd.to_datetime(
                            df_flowwer_inspect["invoiceDate"],
                            format="%d.%m.%Y",
                            errors="coerce",
                        )
                        df_flowwer_inspect["Cost_Center"] = (
                            df_flowwer_inspect["costCenter"].astype(str).str.strip()
                        )
                        df_flowwer_inspect["Amount"] = pd.to_numeric(
                            df_flowwer_inspect["grossValue"], errors="coerce"
                        )

                        # Convert PLN to EUR using date-specific exchange rates
                        if "currencyCode" in df_flowwer_inspect.columns:
                            # Check for both "PL" and "PLN" currency codes
                            pln_mask = (
                                df_flowwer_inspect["currencyCode"]
                                .str.upper()
                                .isin(["PL", "PLN"])
                            )

                            # Apply conversion with date-specific rates
                            for idx in df_flowwer_inspect[pln_mask].index:
                                invoice_date = df_flowwer_inspect.loc[
                                    idx, "Invoice_Date"
                                ]
                                if pd.notna(invoice_date):
                                    # Convert to datetime if needed and format as string
                                    if isinstance(invoice_date, pd.Timestamp):
                                        date_str = invoice_date.strftime("%Y-%m-%d")
                                    else:
                                        date_str = pd.to_datetime(invoice_date).strftime("%Y-%m-%d")  # type: ignore

                                    rate = get_pln_eur_rate(date_str)
                                    current_amount = float(df_flowwer_inspect.loc[idx, "Amount"])  # type: ignore
                                    df_flowwer_inspect.loc[idx, "Amount"] = (
                                        current_amount / rate
                                    )

                        flowwer_raw_records = df_flowwer_inspect[
                            df_flowwer_inspect["Invoice_Number"] == inspect_invoice
                        ]
                    else:
                        flowwer_raw_records = pd.DataFrame()

                    if len(excel_raw_records) > 0 or len(flowwer_raw_records) > 0:
                        st.markdown(f"### Invoice Breakdown: `{inspect_invoice}`")
                        st.caption(
                            "Comparing all transaction records from both systems"
                        )

                        # Summary metrics first
                        if len(excel_raw_records) > 0 and len(flowwer_raw_records) > 0:
                            excel_sum = excel_raw_records["Amount"].sum()
                            flowwer_sum = flowwer_raw_records["Amount"].sum()
                            difference = abs(excel_sum - flowwer_sum)

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("DATEV Records", len(excel_raw_records))
                            with col2:
                                st.metric("DATEV Total", f"€{excel_sum:,.2f}")
                            with col3:
                                st.metric("Flowwer Records", len(flowwer_raw_records))
                            with col4:
                                st.metric("Flowwer Total", f"€{flowwer_sum:,.2f}")

                            # Status message
                            if difference <= 0.01:
                                st.success(
                                    f"**Amounts Match** - Both systems show the same total (difference: €{difference:,.2f})"
                                )
                            elif abs(excel_sum) <= 0.01:
                                st.info(
                                    "**Invoice Paid** - DATEV shows zero balance (payment completed with offsetting entries)"
                                )
                            else:
                                st.warning(
                                    f"**Amounts Differ** - Difference of €{difference:,.2f} between systems"
                                )

                        st.markdown("---")

                        # Side by side data tables
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("DATEV Records", divider="gray")
                            if len(excel_raw_records) > 0:
                                excel_display = excel_raw_records[
                                    ["Invoice_Date", "Cost_Center", "Amount"]
                                ].copy()
                                excel_display.columns = [
                                    "Date",
                                    "Cost Center",
                                    "Amount (EUR)",
                                ]
                                excel_display["Date"] = pd.to_datetime(
                                    excel_display["Date"]
                                ).dt.strftime("%Y-%m-%d")

                                # Format amount column
                                excel_display["Amount (EUR)"] = excel_display[
                                    "Amount (EUR)"
                                ].apply(
                                    lambda x: (
                                        f"€{x:,.2f}" if x >= 0 else f"-€{abs(x):,.2f}"
                                    )
                                )

                                st.dataframe(
                                    excel_display,
                                    use_container_width=True,
                                    height=300,
                                    hide_index=True,
                                )

                                total = excel_raw_records["Amount"].sum()
                                st.caption(
                                    f"**Total of {len(excel_raw_records)} records:** €{total:,.2f}"
                                )
                            else:
                                st.info("No records found in DATEV for this invoice")

                        with col2:
                            st.subheader("Flowwer Records", divider="gray")
                            if len(flowwer_raw_records) > 0:
                                flowwer_display = flowwer_raw_records[
                                    ["Invoice_Date", "Cost_Center", "Amount"]
                                ].copy()
                                flowwer_display.columns = [
                                    "Date",
                                    "Cost Center",
                                    "Amount (EUR)",
                                ]
                                flowwer_display["Date"] = pd.to_datetime(
                                    flowwer_display["Date"]
                                ).dt.strftime("%Y-%m-%d")

                                # Format amount column
                                flowwer_display["Amount (EUR)"] = flowwer_display[
                                    "Amount (EUR)"
                                ].apply(
                                    lambda x: (
                                        f"€{x:,.2f}" if x >= 0 else f"-€{abs(x):,.2f}"
                                    )
                                )

                                st.dataframe(
                                    flowwer_display,
                                    use_container_width=True,
                                    height=300,
                                    hide_index=True,
                                )

                                total = flowwer_raw_records["Amount"].sum()
                                st.caption(
                                    f"**Total of {len(flowwer_raw_records)} records:** €{total:,.2f}"
                                )
                            else:
                                st.info("No records found in Flowwer for this invoice")

                        # Analysis section - only if there's a difference
                        if len(excel_raw_records) > 0 and len(flowwer_raw_records) > 0:
                            excel_sum = excel_raw_records["Amount"].sum()
                            flowwer_sum = flowwer_raw_records["Amount"].sum()
                            difference = abs(excel_sum - flowwer_sum)

                            if difference > 0.01:
                                st.markdown("---")
                                st.markdown("#### Why Do the Amounts Differ?")

                                reasons = []
                                if len(excel_raw_records) != len(flowwer_raw_records):
                                    reasons.append(
                                        f"Different number of transaction records: Excel has {len(excel_raw_records)}, Flowwer has {len(flowwer_raw_records)}"
                                    )

                                if abs(excel_sum) <= 0.01:
                                    reasons.append(
                                        "Excel balance is zero - invoice has been paid with offsetting credit/debit entries"
                                    )

                                if len(excel_raw_records) > len(flowwer_raw_records):
                                    reasons.append(
                                        "DATEV contains additional correction or reversal entries that haven't been synchronized to Flowwer yet"
                                    )
                                elif len(flowwer_raw_records) > len(excel_raw_records):
                                    reasons.append(
                                        "Flowwer contains additional line items or cost center splits not yet in DATEV"
                                    )

                                # Check for cost center differences
                                excel_ccs = set(
                                    excel_raw_records["Cost_Center"].unique()
                                )
                                flowwer_ccs = set(
                                    flowwer_raw_records["Cost_Center"].unique()
                                )
                                if excel_ccs != flowwer_ccs:
                                    reasons.append(
                                        f"Different cost centers used: DATEV has {len(excel_ccs)} unique, Flowwer has {len(flowwer_ccs)} unique"
                                    )

                                for i, reason in enumerate(reasons, 1):
                                    st.write(f"{i}. {reason}")

                                if not reasons:
                                    st.write(
                                        "The records exist in both systems but the calculated totals differ. This may require manual investigation."
                                    )
                    else:
                        st.error(
                            f"Invoice number `{inspect_invoice}` was not found in either Excel or Flowwer system"
                        )

                # Show detailed mismatches in tabs
                st.markdown("---")
                st.markdown("### View Side-by-Side Comparison")

                tab1, tab2, tab3, tab4 = st.tabs(
                    [
                        "All Mismatches",
                        "Date Issues",
                        "Cost Center Issues",
                        "Amount Issues",
                    ]
                )

                with tab1:
                    # Show side-by-side comparison
                    display_df = (
                        mismatch_df[
                            [
                                "Invoice_Number",
                                "Flowwer_Date",
                                "DATEV_Date",
                                "Date_Match",
                                "Flowwer_CC",
                                "DATEV_CC",
                                "CC_Match",
                                "Flowwer_Amount",
                                "DATEV_Amount",
                                "Amount_Diff",
                                "Amount_Match",
                            ]
                        ]
                        .head(100)
                        .copy()
                    )

                    # Format dates for better display
                    display_df["Flowwer_Date"] = pd.to_datetime(
                        display_df["Flowwer_Date"]
                    ).dt.strftime("%Y-%m-%d")
                    display_df["DATEV_Date"] = pd.to_datetime(
                        display_df["DATEV_Date"]
                    ).dt.strftime("%Y-%m-%d")

                    # Format amounts to 2 decimal places
                    display_df["Flowwer_Amount"] = display_df["Flowwer_Amount"].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else ""
                    )
                    display_df["DATEV_Amount"] = display_df["DATEV_Amount"].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else ""
                    )
                    display_df["Amount_Diff"] = display_df["Amount_Diff"].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else ""
                    )

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=400,
                    )

                with tab2:
                    date_issues = mismatch_df[~mismatch_df["Date_Match"]]
                    if len(date_issues) > 0:
                        display_date_df = (
                            date_issues[
                                [
                                    "Invoice_Number",
                                    "Flowwer_Date",
                                    "DATEV_Date",
                                    "Flowwer_CC",
                                    "Flowwer_Amount",
                                ]
                            ]
                            .head(100)
                            .copy()
                        )
                        display_date_df["Flowwer_Date"] = pd.to_datetime(
                            display_date_df["Flowwer_Date"]
                        ).dt.strftime("%Y-%m-%d")
                        display_date_df["DATEV_Date"] = pd.to_datetime(
                            display_date_df["DATEV_Date"]
                        ).dt.strftime("%Y-%m-%d")

                        # Format amounts to 2 decimal places
                        display_date_df["Flowwer_Amount"] = display_date_df[
                            "Flowwer_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                        st.dataframe(
                            display_date_df,
                            use_container_width=True,
                            height=400,
                        )
                    else:
                        st.success("All Invoice Dates match!")

                with tab3:
                    cc_issues = mismatch_df[~mismatch_df["CC_Match"]]
                    if len(cc_issues) > 0:
                        display_cc_df = (
                            cc_issues[
                                [
                                    "Invoice_Number",
                                    "Flowwer_CC",
                                    "DATEV_CC",
                                    "Flowwer_Amount",
                                    "DATEV_Amount",
                                ]
                            ]
                            .head(100)
                            .copy()
                        )

                        # Format amounts to 2 decimal places
                        display_cc_df["Flowwer_Amount"] = display_cc_df[
                            "Flowwer_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                        display_cc_df["DATEV_Amount"] = display_cc_df[
                            "DATEV_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                        st.dataframe(
                            display_cc_df,
                            use_container_width=True,
                            height=400,
                        )
                    else:
                        st.success("All Cost Centers match!")

                with tab4:
                    amount_issues = mismatch_df[~mismatch_df["Amount_Match"]]
                    if len(amount_issues) > 0:
                        display_amount_df = (
                            amount_issues[
                                [
                                    "Invoice_Number",
                                    "Flowwer_Amount",
                                    "DATEV_Amount",
                                    "Amount_Diff",
                                    "Flowwer_CC",
                                ]
                            ]
                            .head(100)
                            .copy()
                        )

                        # Format amounts to 2 decimal places
                        display_amount_df["Flowwer_Amount"] = display_amount_df[
                            "Flowwer_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                        display_amount_df["DATEV_Amount"] = display_amount_df[
                            "DATEV_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                        display_amount_df["Amount_Diff"] = display_amount_df[
                            "Amount_Diff"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                        st.dataframe(
                            display_amount_df,
                            use_container_width=True,
                            height=400,
                        )
                    else:
                        st.success("All Amounts match!")
            else:
                st.success("Perfect! All Flowwer records match DATEV exactly!")

            # Show records not found in DATEV
            not_in_datev_df = df_results[df_results["Status"] == "Not in DATEV"]
            if len(not_in_datev_df) > 0:
                st.markdown(
                    """
                    <div style="
                        border-left: 3px solid #ef4444;
                        padding: 0.75rem 1.25rem;
                        border-radius: 8px;
                        margin: 2rem 0 1rem 0;
                        background: rgba(239, 68, 68, 0.03);
                    ">
                        <h3 style="margin: 0; color: #ef4444; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">NOT IN DATEV</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                display_not_found_df = (
                    not_in_datev_df[
                        [
                            "Invoice_Number",
                            "Flowwer_Date",
                            "Flowwer_CC",
                            "Flowwer_Amount",
                        ]
                    ]
                    .head(50)
                    .copy()
                )
                display_not_found_df["Flowwer_Date"] = pd.to_datetime(
                    display_not_found_df["Flowwer_Date"]
                ).dt.strftime("%Y-%m-%d")

                # Format amounts to 2 decimal places
                display_not_found_df["Flowwer_Amount"] = display_not_found_df[
                    "Flowwer_Amount"
                ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                st.dataframe(
                    display_not_found_df,
                    use_container_width=True,
                    height=300,
                )

                # Export full results
                st.markdown("### Export Complete Cross-Check Report")

                col1, col2 = st.columns(2)

                with col1:
                    csv_full = df_results.to_csv(index=False)
                    st.download_button(
                        label="CSV - Complete Report",
                        data=csv_full,
                        file_name=f"crosscheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with col2:
                    excel_full = to_excel(df_results)
                    st.download_button(
                        label="Excel - Complete Report",
                        data=excel_full,
                        file_name=f"crosscheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

    elif "excel_data" in st.session_state and st.session_state.excel_data is not None:
        st.info("Load Flowwer data to enable comparison")
    elif (
        "flowwer_data" in st.session_state and st.session_state.flowwer_data is not None
    ):
        st.info("Load Excel data to enable comparison")
    else:
        st.info("Load both Excel and Flowwer data to start comparison")

# footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 20px; color: #888;'>
        <p style='font-size: 14px; margin: 0;'>
            <strong>Flowwer API Explorer</strong> | ENPROM Finance Portal
        </p>
        <p style='font-size: 12px; margin: 5px 0 0 0;'>
            © 2025 ENPROM GmbH | Made by ENPROM Team
        </p>
    </div>
""",
    unsafe_allow_html=True,
)
