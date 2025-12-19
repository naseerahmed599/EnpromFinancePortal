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
import time
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
        
        /* ====================================================================
           SIDEBAR (Glassmorphic) — keep width exactly the same
           ==================================================================== */
        [data-testid="stSidebar"] {
            position: relative !important;
            width: 300px !important;
            height: auto !important;
            box-sizing: border-box !important;
            flex-shrink: 0 !important;

            /* True glass panel */
            background: rgba(15, 23, 42, 0.38) !important;
            backdrop-filter: blur(18px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
            border-right: 1px solid rgba(148, 163, 184, 0.18) !important;
            box-shadow:
                10px 0 40px rgba(0, 0, 0, 0.14),
                2px 0 10px rgba(0, 0, 0, 0.06) !important;
            overflow: hidden !important;
        }

        /* Decorative gradient + vignette overlay (doesn't affect layout) */
        [data-testid="stSidebar"]::before{
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(900px 520px at 20% 0%,
                    rgba(59, 130, 246, 0.42),
                    transparent 60%),
                radial-gradient(800px 540px at 90% 20%,
                    rgba(14, 165, 233, 0.28),
                    transparent 60%),
                linear-gradient(165deg,
                    rgba(15, 29, 51, 0.15) 0%,
                    rgba(12, 33, 58, 0.42) 55%,
                    rgba(8, 29, 52, 0.62) 100%);
            opacity: 0.90;
            pointer-events: none;
        }

        [data-testid="stSidebar"]::after{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(255,255,255,0.10), transparent 24%, transparent 76%, rgba(0,0,0,0.16));
            opacity: 0.45;
            pointer-events: none;
        }

        /* Ensure sidebar content sits above overlays */
        [data-testid="stSidebar"] > div:first-child{
            position: relative;
            z-index: 1;
            padding: 2rem 1.1rem 1.5rem 1.1rem !important;
        }
        
        /* Sidebar text colors */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: rgba(226, 232, 240, 0.92);
        }
        
        /* App Title Styling */
        [data-testid="stSidebar"] h1 {
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 1.5rem !important;
            padding: 0.5rem 0 0.8rem 0 !important;
            margin-bottom: 0.5rem !important;
            border-bottom: 1px solid rgba(148, 163, 184, 0.22);
            letter-spacing: -0.02em;
        }
        
        /* Section Headers (h3) */
        [data-testid="stSidebar"] h3 {
            color: rgba(191, 219, 254, 0.95) !important;
            font-size: 0.7rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            margin-top: 1.8rem !important;
            margin-bottom: 0.8rem !important;
            padding-left: 0.3rem !important;
            opacity: 0.9;
        }
        
        /* Navigation Buttons - Glass pills */
        [data-testid="stSidebar"] button {
            border-radius: 999px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.68rem 0.95rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            margin-bottom: 0.4rem !important;
            box-shadow:
                0 10px 28px rgba(0, 0, 0, 0.22),
                inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(14px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
        }

        [data-testid="stSidebar"] button:focus{
            outline: none !important;
            box-shadow:
                0 0 0 3px rgba(59, 130, 246, 0.28),
                0 10px 28px rgba(0, 0, 0, 0.22),
                inset 0 1px 0 rgba(255, 255, 255, 0.10) !important;
        }
        
        /* Secondary buttons (inactive) */
        [data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.06) !important;
            color: rgba(226, 232, 240, 0.90) !important;
        }
        
        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.10) !important;
            color: #ffffff !important;
            transform: translateX(3px);
            border-color: rgba(59, 130, 246, 0.28) !important;
            box-shadow:
                0 14px 34px rgba(0, 0, 0, 0.26),
                0 6px 16px rgba(59, 130, 246, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.10) !important;
        }
        
        /* Primary buttons (active page) */
        [data-testid="stSidebar"] button[kind="primary"] {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.96) 0%, rgba(37, 99, 235, 0.96) 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-color: rgba(59, 130, 246, 0.55) !important;
            box-shadow:
                0 18px 44px rgba(37, 99, 235, 0.35),
                0 6px 18px rgba(0, 0, 0, 0.18),
                inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
        }
        
        [data-testid="stSidebar"] button[kind="primary"]:hover {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.98) 0%, rgba(29, 78, 216, 0.98) 100%) !important;
            box-shadow:
                0 22px 56px rgba(37, 99, 235, 0.42),
                0 8px 22px rgba(0, 0, 0, 0.22),
                inset 0 1px 0 rgba(255, 255, 255, 0.26) !important;
        }
        
        /* Dividers */
        [data-testid="stSidebar"] hr {
            margin: 1.5rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg,
                transparent 0%,
                rgba(148, 163, 184, 0.28) 50%,
                transparent 100%);
        }
        
        /* Quick Stats Panel - Glassmorphism */
        .quick-stats {
            background: rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(18px) saturate(160%);
            -webkit-backdrop-filter: blur(18px) saturate(160%);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0 1.5rem 0;
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: 0 16px 44px rgba(0, 0, 0, 0.22);
        }
        
        .quick-stats-title {
            color: rgba(191, 219, 254, 0.95);
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.16);
        }
        
        .quick-stats-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            color: rgba(226, 232, 240, 0.92);
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.10);
        }
        
        .quick-stats-item:last-child {
            border-bottom: none;
        }
        
        .quick-stats-value {
            font-weight: 700;
            font-size: 1rem;
            color: #ffffff;
            background: rgba(59, 130, 246, 0.32);
            padding: 0.2rem 0.6rem;
            border-radius: 8px;
            min-width: 40px;
            text-align: center;
        }

        /* Make the ENPROM logo readable (black text) with a subtle frosted capsule */
        [data-testid="stSidebar"] [data-testid="stImage"] img{
            background: linear-gradient(135deg, rgba(255,255,255,0.82) 0%, rgba(255,255,255,0.65) 100%);
            border: 1px solid rgba(255, 255, 255, 0.32);
            border-radius: 18px;
            padding: 8px 10px;
            box-shadow:
                0 10px 26px rgba(0, 0, 0, 0.16),
                inset 0 1px 0 rgba(255, 255, 255, 0.70);
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
            background: rgba(148, 163, 184, 0.28);
            border-radius: 10px;
        }
        
        [data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
            background: rgba(148, 163, 184, 0.40);
        }
        
        /* ====================================================================
           HIDE ICONS FROM STREAMLIT MESSAGES (success, info, warning, error)
           ==================================================================== */
        
        /* Hide icons from all Streamlit message types */
        .stSuccess > div:first-child,
        .stSuccess svg,
        .stSuccess [data-testid="stIcon"],
        .stSuccess .stIcon,
        .stInfo > div:first-child,
        .stInfo svg,
        .stInfo [data-testid="stIcon"],
        .stInfo .stIcon,
        .stWarning > div:first-child,
        .stWarning svg,
        .stWarning [data-testid="stIcon"],
        .stWarning .stIcon,
        .stError > div:first-child,
        .stError svg,
        .stError [data-testid="stIcon"],
        .stError .stIcon{
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Hide icons from toast notifications */
        [data-baseweb="toast"] svg,
        [data-baseweb="toast"] [data-testid="stIcon"],
        [data-baseweb="toast"] .stIcon{
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Adjust padding since icons are removed */
        .stSuccess,
        .stInfo,
        .stWarning,
        .stError{
            padding-left: 1rem !important;
        }

        /* ====================================================================
           GLOBAL BUTTON STYLING (Main area only — excludes sidebar navigation)
           - Inspired by Analytics "Load Data" look
           - IMPORTANT: no leading dot / no ::before decoration
           ==================================================================== */

        [data-testid="stMain"]{
            --enprom-pill-radius: 999px;
            --enprom-pill-font-size: 0.86rem;
            --enprom-pill-font-weight: 800;
            --enprom-pill-pad-y: 0.56rem;
            --enprom-pill-pad-x: 1.05rem;
            --enprom-pill-min-height: 2.5rem;
        }

        /* Base pill look for all buttons in main content (including download buttons) */
        [data-testid="stMain"] .stButton > button,
        [data-testid="stMain"] .stDownloadButton > button{
            border-radius: var(--enprom-pill-radius) !important;
            font-size: var(--enprom-pill-font-size) !important;
            font-weight: var(--enprom-pill-font-weight) !important;
            letter-spacing: 0.01em !important;
            min-height: var(--enprom-pill-min-height) !important;
            padding: var(--enprom-pill-pad-y) var(--enprom-pill-pad-x) !important;
            line-height: 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.45rem !important;
            white-space: nowrap !important;
            max-width: 100% !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            backdrop-filter: blur(10px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(10px) saturate(160%) !important;
            transition: all 0.2s ease !important;
            transform: translateY(0px);
            box-sizing: border-box !important;
        }

        /* Ensure no pseudo-element decoration on buttons */
        [data-testid="stMain"] .stButton > button::before,
        [data-testid="stMain"] .stDownloadButton > button::before{
            content: none !important;
        }

        /* Primary buttons */
        [data-testid="stMain"] button[kind="primary"],
        [data-testid="stMain"] button[data-testid="baseButton-primary"]{
            background: rgba(59, 130, 246, 0.12) !important;
            color: #1d4ed8 !important;
            border: 1px solid rgba(59, 130, 246, 0.26) !important;
            box-shadow: 0 8px 22px rgba(59, 130, 246, 0.14) !important;
        }
        [data-testid="stMain"] button[kind="primary"]:hover,
        [data-testid="stMain"] button[data-testid="baseButton-primary"]:hover{
            background: rgba(59, 130, 246, 0.16) !important;
            border-color: rgba(59, 130, 246, 0.34) !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 30px rgba(59, 130, 246, 0.18) !important;
        }
        [data-testid="stMain"] button[kind="primary"]:active,
        [data-testid="stMain"] button[data-testid="baseButton-primary"]:active{
            transform: translateY(0px);
            box-shadow: 0 8px 22px rgba(59, 130, 246, 0.14) !important;
        }

        /* Secondary buttons (neutral — keep non-destructive actions non-red) */
        [data-testid="stMain"] button[kind="secondary"],
        [data-testid="stMain"] button[data-testid="baseButton-secondary"],
        [data-testid="stMain"] .stDownloadButton > button{
            background: rgba(100, 116, 139, 0.10) !important;
            color: rgba(15, 23, 42, 0.86) !important;
            border: 1px solid rgba(100, 116, 139, 0.22) !important;
            box-shadow: 0 8px 22px rgba(100, 116, 139, 0.10) !important;
        }
        [data-testid="stMain"] button[kind="secondary"]:hover,
        [data-testid="stMain"] button[data-testid="baseButton-secondary"]:hover,
        [data-testid="stMain"] .stDownloadButton > button:hover{
            background: rgba(100, 116, 139, 0.14) !important;
            border-color: rgba(100, 116, 139, 0.30) !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 30px rgba(100, 116, 139, 0.14) !important;
        }
        [data-testid="stMain"] button[kind="secondary"]:active,
        [data-testid="stMain"] button[data-testid="baseButton-secondary"]:active,
        [data-testid="stMain"] .stDownloadButton > button:active{
            transform: translateY(0px);
            box-shadow: 0 8px 22px rgba(100, 116, 139, 0.10) !important;
        }

        @media (prefers-color-scheme: dark){
            [data-testid="stMain"] button[kind="primary"],
            [data-testid="stMain"] button[data-testid="baseButton-primary"]{
                background: rgba(59, 130, 246, 0.18) !important;
                color: rgba(224, 242, 254, 0.95) !important;
                border-color: rgba(59, 130, 246, 0.32) !important;
                box-shadow: 0 10px 26px rgba(0,0,0,0.28), 0 8px 22px rgba(59, 130, 246, 0.16) !important;
            }
            [data-testid="stMain"] button[kind="primary"]:hover,
            [data-testid="stMain"] button[data-testid="baseButton-primary"]:hover{
                background: rgba(59, 130, 246, 0.22) !important;
                border-color: rgba(59, 130, 246, 0.40) !important;
            }

            [data-testid="stMain"] button[kind="secondary"],
            [data-testid="stMain"] button[data-testid="baseButton-secondary"],
            [data-testid="stMain"] .stDownloadButton > button{
                background: rgba(148, 163, 184, 0.14) !important;
                color: rgba(226, 232, 240, 0.92) !important;
                border-color: rgba(148, 163, 184, 0.22) !important;
                box-shadow: 0 10px 26px rgba(0,0,0,0.28), 0 8px 22px rgba(148, 163, 184, 0.10) !important;
            }
            [data-testid="stMain"] button[kind="secondary"]:hover,
            [data-testid="stMain"] button[data-testid="baseButton-secondary"]:hover,
            [data-testid="stMain"] .stDownloadButton > button:hover{
                background: rgba(148, 163, 184, 0.18) !important;
                border-color: rgba(148, 163, 184, 0.30) !important;
            }
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

if "correct_api_key" not in st.session_state:
    st.session_state.correct_api_key = st.secrets.get("flowwer", {}).get(
        "api_key"
    ) or os.environ.get("FLOWWER_API_KEY")

if "client" not in st.session_state:
    st.session_state.client = FlowwerAPIClient(api_key=None)

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
                max-width: 680px;
                margin: 4vh auto 2rem auto;
                text-align: center !important;
            }
            .auth-logo-section{
                margin-bottom: 1.5rem;
                margin-top: 0;
                animation: fadeInDown 0.6s ease-out;
                text-align: center !important;
            }
            .auth-logo-wrapper{
                display: inline-block;
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                padding: 3.15rem;
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
                padding: 1.95rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .auth-logo-inner img{
                height: 58px;
                max-width: 235px;
                object-fit: contain;
                display: block;
            }
            @media (max-width: 640px){
                .auth-logo-wrapper{ padding: 2.4rem; border-radius: 22px; }
                .auth-logo-inner{ padding: 1.45rem; }
                .auth-logo-inner img{ height: 52px; max-width: 220px; }
            }
            .auth-title-section{
                margin-top: 2rem;
                animation: fadeInUp 0.6s ease-out 0.2s both;
                text-align: center;
            }
            .auth-main-title{
                font-size: 2.25rem;
                font-weight: 800;
                margin: 0 0 0.5rem 0;
                letter-spacing: -0.5px;
                text-align: center;
                line-height: 1.15;
                display: inline-block;
                color: #1e293b;
            }
            /* Gradient text only when supported (prevents “rectangle” in dark mode) */
            @supports (-webkit-background-clip: text) {
                .auth-main-title{
                    background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
                    -webkit-background-clip: text;
                    background-clip: text;
                    -webkit-text-fill-color: transparent;
                    color: transparent;
                }
            }
            .auth-subtitle{
                font-size: 1rem !important;
                color: #64748b !important;
                font-weight: 500 !important;
                margin: 0 !important;
                text-align: center !important;
                padding: 0 !important;
                line-height: 1.5 !important;
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
                <h6 class="auth-subtitle">Secure authentication required</h6>
            </div>
            <div class="auth-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
            /* Modern auth screen: gradient + centered glass card */
            .stApp,
            [data-testid="stAppViewContainer"]{
                background: radial-gradient(1200px 800px at 20% 10%, rgba(99,102,241,0.22), transparent 60%),
                            radial-gradient(1000px 700px at 90% 20%, rgba(168,85,247,0.18), transparent 55%),
                            linear-gradient(135deg,
                                #f8fafc 0%,
                                #f1f5f9 30%,
                                #eef2ff 60%,
                                #faf5ff 100%) !important;
                background-attachment: fixed !important;
            }

            /* Hide Streamlit chrome on the login screen */
            header[data-testid="stHeader"], footer, #MainMenu{ visibility: hidden; }

            /* Turn the main content area into a centered card */
            .block-container{
                max-width: 680px !important;
                margin: 9vh auto 0 auto !important;
                padding: 2.5rem 2.75rem 2.25rem 2.75rem !important;
                background: rgba(255, 255, 255, 0.75) !important;
                border: 1px solid rgba(148, 163, 184, 0.35) !important;
                border-radius: 22px !important;
                box-shadow: 0 24px 70px rgba(15, 23, 42, 0.12) !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
            }

            @media (max-width: 640px){
                .block-container{
                    margin-top: 6vh !important;
                    padding: 1.5rem 1.25rem 1.25rem 1.25rem !important;
                    border-radius: 18px !important;
                }
            }

            @media (prefers-color-scheme: dark){
                .stApp,
                [data-testid="stAppViewContainer"]{
                    background: radial-gradient(1200px 800px at 20% 10%, rgba(99,102,241,0.30), transparent 60%),
                                radial-gradient(1000px 700px at 90% 20%, rgba(168,85,247,0.26), transparent 55%),
                                linear-gradient(135deg,
                                    #0b1220 0%,
                                    #0f172a 40%,
                                    #111827 100%) !important;
                }

                .block-container{
                    background: rgba(15, 23, 42, 0.72) !important;
                    border-color: rgba(51, 65, 85, 0.55) !important;
                    box-shadow: 0 24px 80px rgba(0,0,0,0.45) !important;
                }

                .auth-main-title{
                    /* Fallback: visible solid title in dark mode even if background-clip isn't supported */
                    background: none !important;
                    color: #e2e8f0 !important;
                    -webkit-text-fill-color: #e2e8f0 !important;
                }
                @supports (-webkit-background-clip: text) {
                    .auth-main-title{
                        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%) !important;
                        -webkit-background-clip: text !important;
                        background-clip: text !important;
                        -webkit-text-fill-color: transparent !important;
                        color: transparent !important;
                    }
                }

                .auth-subtitle{ color: rgba(226,232,240,0.72) !important; }
                .auth-divider{ background: linear-gradient(90deg, transparent, rgba(51,65,85,0.9), transparent) !important; }
            }
            
            /* Remove red border from input on focus */
            input[type="password"]:focus,
            input[type="text"]:focus,
            div[data-baseweb="input"] input:focus{
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 1px rgba(99,102,241,0.9) !important;
                outline: none !important;
            }
            
            /* Style input container */
            div[data-baseweb="input"]{
                border-radius: 12px !important;
                border: 1.5px solid rgba(226, 232, 240, 0.95) !important;
                transition: all 0.2s ease !important;
                background: rgba(255, 255, 255, 0.85) !important;
            }

            /* Remove password reveal icon inside the input (login screen only) */
            div[data-baseweb="input"] button{
                display: none !important;
            }
            div[data-baseweb="input"] input{
                padding-right: 0.75rem !important;
            }
            
            div[data-baseweb="input"]:focus-within{
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
            }

            @media (prefers-color-scheme: dark){
                div[data-baseweb="input"]{
                    border-color: rgba(71, 85, 105, 0.7) !important;
                    background: rgba(2, 6, 23, 0.35) !important;
                }
                div[data-baseweb="input"] input{
                    color: #e2e8f0 !important;
                }
            }
            
            /* Primary button theme to match app - pill style with consistent sizing
               (Target form submit buttons too; Streamlit DOM differs by version) */
            .block-container button[kind="primary"],
            .block-container button[data-testid="baseButton-primary"],
            .block-container div.stButton > button[kind="primary"],
            .block-container div.stButton > button[data-testid="baseButton-primary"],
            button[kind="primary"],
            button[data-testid="baseButton-primary"],
            div.stButton > button[kind="primary"],
            div.stButton > button[data-testid="baseButton-primary"],
            button[type="submit"][kind="primary"],
            button[type="submit"][data-testid="baseButton-primary"],
            div[data-testid="stForm"] button[kind="primary"],
            div[data-testid="stForm"] button[data-testid="baseButton-primary"],
            div[data-testid="stForm"] button[type="submit"]{
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
                color: #fff !important; 
                border: 0 !important;
                box-shadow: 0 8px 18px rgba(79,70,229,.25) !important;
                font-weight: 800 !important;
                font-size: 0.86rem !important;
                letter-spacing: 0.01em !important;
                border-radius: 999px !important;
                min-height: 2.5rem !important;
                padding: 0.56rem 1.05rem !important;
                transition: all 0.2s ease !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            button[kind="primary"]:hover,
            button[data-testid="baseButton-primary"]:hover,
            div.stButton > button[kind="primary"]:hover,
            div.stButton > button[data-testid="baseButton-primary"]:hover,
            button[type="submit"][kind="primary"]:hover,
            button[type="submit"][data-testid="baseButton-primary"]:hover,
            div[data-testid="stForm"] button[kind="primary"]:hover,
            div[data-testid="stForm"] button[data-testid="baseButton-primary"]:hover,
            div[data-testid="stForm"] button[type="submit"]:hover{
                transform: translateY(-1px);
                box-shadow: 0 12px 28px rgba(79,70,229,.35) !important;
            }

            /* Secondary button - pill style with consistent sizing */
            .block-container button[kind="secondary"],
            .block-container button[data-testid="baseButton-secondary"],
            .block-container div.stButton > button[kind="secondary"],
            .block-container div.stButton > button[data-testid="baseButton-secondary"],
            button[kind="secondary"],
            button[data-testid="baseButton-secondary"],
            div.stButton > button[kind="secondary"],
            div.stButton > button[data-testid="baseButton-secondary"],
            button[type="submit"][kind="secondary"],
            button[type="submit"][data-testid="baseButton-secondary"],
            div[data-testid="stForm"] button[kind="secondary"],
            div[data-testid="stForm"] button[data-testid="baseButton-secondary"],
            div[data-testid="stForm"] button[type="submit"]:not([kind="primary"]){
                border-radius: 999px !important;
                min-height: 2.5rem !important;
                padding: 0.56rem 1.05rem !important;
                font-weight: 800 !important;
                font-size: 0.86rem !important;
                letter-spacing: 0.01em !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
            }

            /* Catch-all for ALL buttons on login page - ensure pill style with maximum specificity */
            .block-container button,
            .block-container button[type="button"],
            .block-container button[type="submit"],
            .block-container .stButton,
            .block-container .stButton > button,
            .block-container div.stButton > button,
            .block-container form button,
            .block-container form button[type="submit"],
            .block-container form .stButton > button,
            form button,
            form button[type="button"],
            form button[type="submit"],
            form .stButton > button,
            form div.stButton > button,
            div[data-testid="stForm"] button,
            div[data-testid="stForm"] button[type="button"],
            div[data-testid="stForm"] button[type="submit"],
            div[data-testid="stForm"] .stButton > button,
            div[data-testid="stForm"] div.stButton > button,
            form#api_key_login_form button,
            form#api_key_login_form button[type="button"],
            form#api_key_login_form button[type="submit"],
            form#api_key_login_form .stButton > button,
            form#api_key_login_form div.stButton > button,
            div[data-testid="stForm"]:has(form#api_key_login_form) button,
            .block-container:has(form#api_key_login_form) button,
            .block-container:has(form#api_key_login_form) .stButton > button,
            .block-container:has(form#api_key_login_form) div.stButton > button{
                border-radius: 999px !important;
                min-height: 2.5rem !important;
                padding: 0.56rem 1.05rem !important;
                font-weight: 800 !important;
                font-size: 0.86rem !important;
                letter-spacing: 0.01em !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
            }

            /* Ensure primary buttons on login page have blue gradient - maximum specificity */
            .block-container button[kind="primary"],
            .block-container button[data-testid="baseButton-primary"],
            .block-container .stButton > button[kind="primary"],
            .block-container .stButton > button[data-testid="baseButton-primary"],
            .block-container form button[kind="primary"],
            .block-container form button[data-testid="baseButton-primary"],
            .block-container form .stButton > button[kind="primary"],
            form button[kind="primary"],
            form button[data-testid="baseButton-primary"],
            form .stButton > button[kind="primary"],
            form .stButton > button[data-testid="baseButton-primary"],
            div[data-testid="stForm"] button[kind="primary"],
            div[data-testid="stForm"] button[data-testid="baseButton-primary"],
            div[data-testid="stForm"] .stButton > button[kind="primary"],
            div[data-testid="stForm"] .stButton > button[data-testid="baseButton-primary"]{
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
                background-image: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
                color: #fff !important;
                border: 0 !important;
                border-width: 0 !important;
                box-shadow: 0 8px 18px rgba(79,70,229,.25) !important;
            }

            /* Neutralize global glossy button overlays on login screen */
            .block-container button::before,
            form button::before,
            div[data-testid="stForm"] button::before{
                content: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    has_saved_key = bool(st.session_state.get("correct_api_key"))

    st.caption("Enter your Flowwer API key to continue.")

    show_key = st.toggle("Show API key", value=False, help="Temporarily display the API key while typing.")

    with st.form("api_key_login_form", clear_on_submit=False):
        new_api_key = st.text_input(
            "Flowwer API Key",
            value="",
            type="default" if show_key else "password",
            placeholder="Paste your Flowwer API key",
            key="startup_api_key",
            label_visibility="visible",
        )

        btn_left, btn_right = st.columns(2)
        with btn_left:
            submit = st.form_submit_button(
                "Access",
                type="primary",
                use_container_width=True,
            )
        with btn_right:
            use_saved = st.form_submit_button(
                "Use saved key" if has_saved_key else "Use saved key",
                disabled=not has_saved_key,
                use_container_width=True,
            )

    if submit or use_saved:
        api_key_to_verify = (st.session_state.correct_api_key or "").strip() if use_saved else (new_api_key or "").strip()

        if not api_key_to_verify:
            st.warning("Please enter a valid API key.")
        else:
            # Verify the API key by making a test API call
            st.markdown(
                """
                <style>
                    .stSpinner > div {
                        border-color: #6366f1 !important;
                        border-top-color: transparent !important;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            with st.spinner("Verifying with Flowwer..."):
                time.sleep(0.2)
                is_valid, message = st.session_state.client.verify_api_key(api_key_to_verify)

            if is_valid:
                st.session_state.client.api_key = api_key_to_verify
                st.session_state.client.session.headers.update(
                    {"X-FLOWWER-ApiKey": api_key_to_verify}
                )
                st.success(message)
                time.sleep(0.6)
                st.rerun()
            else:
                st.error(message)
                st.info("Tip: confirm the key is copied without extra spaces and belongs to the correct Flowwer tenant.")

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
