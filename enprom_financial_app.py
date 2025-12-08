"""
ENPROM Finance Portal - Business Intelligence
Interactive portal for financial document workflows
"""

# ============================================================================
# CONFIGURATION: Toggle Features for Testing/Development
# ============================================================================
#
# IN_PRODUCTION: Controls visibility of the Data Comparison page
#   - Set to True: Compare Data section appears in Tools menu, enables DATEV comparison
#   - Set to False: Compare Data section is hidden from navigation and disabled
#   - Use Case: Enable for development/testing, disable for production
#
IN_PRODUCTION = False

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
from pages_modules.data_comparison import render_data_comparison_page


@st.cache_data(ttl=86400)
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
        url = f"https://api.frankfurter.app/{date_str}?from=EUR&to=PLN"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            rate = data.get("rates", {}).get("PLN")
            if rate:
                return float(rate)

        return 4.23
    except Exception as e:
        return 4.23


def to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel file bytes"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return output.getvalue()


def to_csv_semicolon(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV with semicolon delimiter (European format)"""
    return df.to_csv(index=False, sep=";", decimal=",", encoding="utf-8-sig")


st.set_page_config(
    page_title="ENPROM Finance Portal",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_languages():
    """Load language translations from JSON file"""
    try:
        import os

        script_dir = os.path.dirname(os.path.abspath(__file__))
        languages_path = os.path.join(script_dir, "languages.json")

        with open(languages_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading languages: {e}")
        return None


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


apply_custom_css()


def get_languages(version=2):
    return load_languages()


languages = get_languages()

if "client" not in st.session_state:
    api_key = st.secrets.get("flowwer", {}).get("api_key") or os.environ.get(
        "FLOWWER_API_KEY"
    )
    st.session_state.client = FlowwerAPIClient(api_key=api_key)

if "documents" not in st.session_state:
    st.session_state.documents = None

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if "language" not in st.session_state:
    st.session_state.language = "en"


def t(key):
    """Get translation for current language"""
    if languages and st.session_state.language in languages:
        keys = key.split(".")
        value = languages[st.session_state.language]
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key
        return value
    return key


if not st.session_state.client.api_key:
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
            stored_api_key = st.secrets.get("flowwer", {}).get(
                "api_key"
            ) or os.environ.get("FLOWWER_API_KEY")

            new_api_key_clean = new_api_key.strip()
            stored_api_key_clean = stored_api_key.strip() if stored_api_key else None

            if stored_api_key_clean and new_api_key_clean == stored_api_key_clean:
                st.session_state.client.api_key = new_api_key_clean
                st.session_state.client.session.headers.update(
                    {"X-FLOWWER-ApiKey": new_api_key_clean}
                )
                st.success(
                    t("messages.api_key_updated") if callable(t) else "API key saved."
                )
                st.rerun()
            else:
                st.error(
                    "Invalid API key. Please check your credentials and try again."
                )

    st.stop()


with st.sidebar:
    st.image(
        "https://enprom.com/wp-content/uploads/2020/12/xlogo-poziome.png.pagespeed.ic.jXuMlmU90u.webp",
        use_container_width=True,
    )

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    st.title("ENPROM Finance Portal")

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

    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.session_state.current_page = None
        st.rerun()

    st.markdown("---")

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

    st.markdown(f"### 📁 {t('nav_sections.documents')}")

    if "current_page" not in st.session_state or st.session_state.current_page is None:
        st.session_state.current_page = "📈 " + t("pages.analytics")

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
        get_section_header_styles,
        to_excel,
    )

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
# PAGE: COMPARE DATA (DATEV vs Flowwer)
# ============================================================================
elif page == "🧪 " + t("pages.test"):
    render_data_comparison_page(
        st.session_state.client,
        t,
        get_page_header_indigo,
        get_action_bar_styles,
        to_excel,
        get_pln_eur_rate,
        IN_PRODUCTION,
    )

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
