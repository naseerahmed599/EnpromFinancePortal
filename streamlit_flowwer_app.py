"""
ENPROM Finance Portal - Professional Document Management System
Interactive portal for financial document workflows and approvals
With multilingual support (English/German) and professional styling
"""

import streamlit as st
import pandas as pd
from flowwer_api_client import FlowwerAPIClient, DocumentHelper
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
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

# Page config
st.set_page_config(
    page_title="ENPROM Finance Portal",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load language file
@st.cache_data
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


# Custom CSS for modern professional styling
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


# Load languages - cache it with file hash to auto-reload on changes
@st.cache_data
def get_languages(version=2):  # Increment version to force reload
    return load_languages()


# Clear cache and reload if needed
languages = get_languages()

# Initialize session state
if "client" not in st.session_state:
    # Initialize with API key directly (like Postman)
    st.session_state.client = FlowwerAPIClient(
        api_key="MXrKdv77r3lTlPzdc9U9mjdT5YzA87iL"
    )

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
    lang_options = {"en": "🇬🇧 English", "de": "🇩🇪 Deutsch"}

    selected_lang = st.selectbox(
        "Language / Sprache",
        options=["en", "de"],
        format_func=lambda x: lang_options[x],
        index=0 if current_lang == "en" else 1,
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
        st.success("🔐 Connected")
    else:
        st.error("🔐 Not Connected")

# Get the current page
page = st.session_state.current_page

# ============================================================================
# PAGE: ALL DOCUMENTS
# ============================================================================
if page == "📋 " + t("pages.all_documents"):
    # Apply all theme-adaptive glassmorphic styles for this page
    st.markdown(get_all_document_page_styles(), unsafe_allow_html=True)
    
    # Glossy page header card - Theme Adaptive
    st.markdown(
        f"""
        <div class="page-header-card" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.9) 0%, rgba(37, 99, 235, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">📋</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('all_documents_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Browse and manage all documents in the system</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1.5, 1.5, 2])

    with col1:
        include_processed = st.checkbox(
            t("all_documents_page.include_processed"),
            value=False,
            help="Include processed documents in the results",
        )

    with col2:
        include_deleted = st.checkbox(
            t("all_documents_page.include_deleted"),
            value=False,
            help="Include deleted documents in the results",
        )

    with col3:
        if st.button(
            "Refresh Documents",
            type="primary",
            use_container_width=True,
            key="btn_refresh_all_docs",
        ):
            with st.spinner("Fetching documents..."):
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed, include_deleted=include_deleted
                )
                st.session_state.documents = docs
                if docs:
                    st.success(f"Successfully loaded {len(docs)} documents")
                else:
                    st.warning("No documents found")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.documents:
        # Statistics cards
        docs = st.session_state.documents
        stage_counts = {}
        payment_counts = {}
        company_counts = {}
        total_gross = 0
        total_net = 0

        for doc in docs:
            stage = doc.get("currentStage", "Unknown")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

            payment = doc.get("paymentState", "Unknown")
            payment_counts[payment] = payment_counts.get(payment, 0) + 1

            company = doc.get("companyName", "Unknown")
            company_counts[company] = company_counts.get(company, 0) + 1

            total_gross += doc.get("totalGross", 0)
            total_net += doc.get("totalNet", 0)

        # Key Metrics Row - Most Important Information
        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                Key Performance Metrics
            </h3>
        """,
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(5)

        # Calculate important metrics
        approved_count = stage_counts.get("Approved", 0)
        pending_count = sum(stage_counts.get(f"Stage{i}", 0) for i in range(1, 6))
        unstarted_count = stage_counts.get("Draft", 0)
        approval_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0

        key_metrics = [
            ("Total Documents", len(docs), "📊", "#3b82f6", "rgba(59, 130, 246, 0.04)"),
            (
                "Total Value",
                f"€{total_gross:,.0f}",
                "💰",
                "#10b981",
                "rgba(16, 185, 129, 0.04)",
            ),
            ("Approved", approved_count, "✅", "#22c55e", "rgba(34, 197, 94, 0.04)"),
            ("In Workflow", pending_count, "⏳", "#f59e0b", "rgba(245, 158, 11, 0.04)"),
            ("Unstarted", unstarted_count, "📝", "#8b5cf6", "rgba(139, 92, 246, 0.04)"),
        ]

        for idx, (label, value, icon, color, bg) in enumerate(key_metrics):
            with metric_cols[idx]:
                st.markdown(
                    f"""
                    <div class="metric-card-light" style="
                        --card-color: {bg};
                        --card-color-dark: {color}30;
                        padding: 1.5rem 1rem;
                        border-radius: 20px;
                        text-align: center;
                        transition: all 0.3s ease;
                        cursor: default;
                        min-height: 180px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            font-size: 2.5rem;
                            font-weight: 900;
                            color: {color};
                            margin-bottom: 0.5rem;
                            line-height: 1.2;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        ">{value}</div>
                        <div class="metric-label" style="
                            font-size: 0.85rem;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            line-height: 1.3;
                        ">{label}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        # Action Required Alert
        if pending_count > 0 or unstarted_count > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            action_col1, action_col2 = st.columns(2)

            if pending_count > 0:
                with action_col1:
                    st.markdown(
                        f"""
                        <div class="alert-box-orange" style="
                            padding: 1.5rem;
                            border-radius: 16px;
                        ">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                                <h4 style="margin: 0; font-size: 1.25rem; font-weight: 700;">
                                    In Processing Workflow
                                </h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                                <strong>{pending_count}</strong> document(s) in approval stages
                            </p>
                            <p class="subtitle" style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                These documents are currently in workflow stages 1-5
                            </p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

            if unstarted_count > 0:
                with action_col2:
                    st.markdown(
                        f"""
                        <div class="alert-box-purple" style="
                            padding: 1.5rem;
                            border-radius: 16px;
                        ">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                                <h4 style="margin: 0; font-size: 1.25rem; font-weight: 700;">
                                    Unstarted Documents
                                </h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                                <strong>{unstarted_count}</strong> document(s) not yet started
                            </p>
                            <p class="subtitle" style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                These documents require initial processing
                            </p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # Financial Overview
        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2.5rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                Financial Summary
            </h3>
        """,
            unsafe_allow_html=True,
        )

        fin_cols = st.columns(3)

        with fin_cols[0]:
            st.markdown(
                f"""
                <div class="financial-card" style="
                    --card-bg: rgba(16, 185, 129, 0.04);
                    --card-bg-dark: rgba(16, 185, 129, 0.15);
                    padding: 1.5rem 1rem;
                    border-radius: 20px;
                    text-align: center;
                    min-height: 140px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <div class="card-label" style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem;">
                        TOTAL GROSS
                    </div>
                    <div style="font-size: 2.25rem; font-weight: 900; color: #10b981; word-wrap: break-word; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        €{total_gross:,.2f}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with fin_cols[1]:
            st.markdown(
                f"""
                <div class="financial-card" style="
                    --card-bg: rgba(59, 130, 246, 0.04);
                    --card-bg-dark: rgba(59, 130, 246, 0.15);
                    padding: 1.5rem 1rem;
                    border-radius: 20px;
                    text-align: center;
                    min-height: 140px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <div class="card-label" style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem;">
                        TOTAL NET
                    </div>
                    <div style="font-size: 2.25rem; font-weight: 900; color: #3b82f6; word-wrap: break-word; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        €{total_net:,.2f}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with fin_cols[2]:
            tax_amount = total_gross - total_net
            st.markdown(
                f"""
                <div class="financial-card" style="
                    --card-bg: rgba(239, 68, 68, 0.04);
                    --card-bg-dark: rgba(239, 68, 68, 0.15);
                    padding: 1.5rem 1rem;
                    border-radius: 20px;
                    text-align: center;
                    min-height: 140px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <div class="card-label" style="font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem;">
                        TOTAL TAX
                    </div>
                    <div style="font-size: 2.25rem; font-weight: 900; color: #ef4444; word-wrap: break-word; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        €{tax_amount:,.2f}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Payment Status Overview
        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2.5rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                Payment Status Breakdown
            </h3>
        """,
            unsafe_allow_html=True,
        )

        pay_cols = st.columns(min(len(payment_counts), 4))
        payment_colors = {
            "Open": ("#f59e0b", "rgba(245, 158, 11, 0.04)"),
            "Paid": ("#22c55e", "rgba(34, 197, 94, 0.04)"),
            "Pending": ("#3b82f6", "rgba(59, 130, 246, 0.04)"),
            "Overdue": ("#ef4444", "rgba(239, 68, 68, 0.04)"),
        }

        for idx, (payment_state, count) in enumerate(
            sorted(payment_counts.items())[:4]
        ):
            color, bg = payment_colors.get(
                payment_state, ("#64748b", "rgba(100, 116, 139, 0.04)")
            )
            bg_dark = bg.replace("0.04", "0.15")  # Create dark mode variant
            with pay_cols[idx]:
                st.markdown(
                    f"""
                    <div class="financial-card" style="
                        --card-bg: {bg};
                        --card-bg-dark: {bg_dark};
                        padding: 1.25rem 1rem;
                        border-radius: 20px;
                        text-align: center;
                        min-height: 120px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    ">
                        <div style="font-size: 1.75rem; font-weight: 900; color: {color}; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                            {count}
                        </div>
                        <div class="card-label" style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                            {payment_state}
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Filter panel
        with st.expander("Advanced Filters", expanded=True):

            # Row 1: Company, Stage, Payment State
            col1, col2, col3 = st.columns(3)

            with col1:
                companies = list(
                    set(
                        [
                            doc.get("companyName", "Unknown")
                            for doc in st.session_state.documents
                        ]
                    )
                )
                selected_company = st.selectbox(
                    "Company",
                    ["All"] + sorted(companies),
                    help="Filter documents by company",
                )

            with col2:
                stages = list(
                    set(
                        [
                            doc.get("currentStage", "Unknown")
                            for doc in st.session_state.documents
                        ]
                    )
                )
                selected_stage = st.selectbox(
                    "Stage",
                    ["All"] + sorted(stages),
                    help="Filter documents by current stage",
                )

            with col3:
                payment_states = list(
                    set(
                        [
                            doc.get("paymentState", "Unknown")
                            for doc in st.session_state.documents
                        ]
                    )
                )
                selected_payment = st.selectbox(
                    "Payment State",
                    ["All"] + sorted(payment_states),
                    help="Filter documents by payment status",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Row 2: Supplier, Currency, Flow
            col4, col5, col6 = st.columns(3)

            with col4:
                suppliers = list(
                    set(
                        [
                            doc.get("supplierName", "Unknown")
                            for doc in st.session_state.documents
                            if doc.get("supplierName")
                        ]
                    )
                )
                selected_supplier = st.selectbox(
                    "Supplier",
                    ["All"] + sorted(suppliers),
                    help="Filter documents by supplier",
                )

            with col5:
                currencies = list(
                    set(
                        [
                            doc.get("currencyCode", "EUR")
                            for doc in st.session_state.documents
                            if doc.get("currencyCode")
                        ]
                    )
                )
                selected_currency = st.selectbox(
                    "Currency",
                    ["All"] + sorted(currencies),
                    help="Filter documents by currency",
                )

            with col6:
                flows = list(
                    set(
                        [
                            doc.get("flowName", "Unknown")
                            for doc in st.session_state.documents
                            if doc.get("flowName")
                        ]
                    )
                )
                selected_flow = st.selectbox(
                    "Flow",
                    ["All"] + sorted(flows),
                    help="Filter documents by approval flow",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Row 3: Date Range and Value Range
            col7, col8, col9 = st.columns(3)

            with col7:
                # Get date range from documents
                invoice_dates = [
                    doc.get("invoiceDate")
                    for doc in st.session_state.documents
                    if doc.get("invoiceDate")
                ]
                if invoice_dates:
                    try:
                        valid_dates = [pd.to_datetime(d) for d in invoice_dates if d]
                        if valid_dates:
                            min_doc_date = min(valid_dates).date()
                            max_doc_date = max(valid_dates).date()

                            date_from = st.date_input(
                                "Invoice Date From",
                                value=None,
                                min_value=min_doc_date,
                                max_value=max_doc_date,
                                help="Filter by invoice date (from)",
                            )
                        else:
                            date_from = None
                    except:
                        date_from = None
                else:
                    date_from = None

            with col8:
                if invoice_dates:
                    try:
                        if valid_dates:
                            date_to = st.date_input(
                                "Invoice Date To",
                                value=None,
                                min_value=min_doc_date,
                                max_value=max_doc_date,
                                help="Filter by invoice date (to)",
                            )
                        else:
                            date_to = None
                    except:
                        date_to = None
                else:
                    date_to = None

            with col9:
                # Value range filter
                gross_values = [
                    doc.get("totalGross", 0) for doc in st.session_state.documents
                ]
                if gross_values:
                    max_value = max(gross_values)
                    value_threshold = st.number_input(
                        "Min Value (€)",
                        min_value=0.0,
                        max_value=float(max_value),
                        value=0.0,
                        step=100.0,
                        help="Show only documents with value above this threshold",
                    )
                else:
                    value_threshold = 0.0

        # Apply filters
        filtered_docs = st.session_state.documents

        if selected_company != "All":
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("companyName") == selected_company
            ]

        if selected_stage != "All":
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("currentStage") == selected_stage
            ]

        if selected_payment != "All":
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("paymentState") == selected_payment
            ]

        if selected_supplier != "All":
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("supplierName") == selected_supplier
            ]

        if selected_currency != "All":
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("currencyCode") == selected_currency
            ]

        if selected_flow != "All":
            filtered_docs = [
                doc for doc in filtered_docs if doc.get("flowName") == selected_flow
            ]

        # Date range filter
        if date_from:

            def is_date_after_or_equal(doc, target_date):
                date_str = doc.get("invoiceDate")
                if not date_str:
                    return False
                try:
                    doc_date = pd.to_datetime(date_str, errors="coerce")
                    if pd.isna(doc_date):
                        return False
                    return doc_date.date() >= target_date
                except:
                    return False

            filtered_docs = [
                doc for doc in filtered_docs if is_date_after_or_equal(doc, date_from)
            ]

        if date_to:

            def is_date_before_or_equal(doc, target_date):
                date_str = doc.get("invoiceDate")
                if not date_str:
                    return False
                try:
                    doc_date = pd.to_datetime(date_str, errors="coerce")
                    if pd.isna(doc_date):
                        return False
                    return doc_date.date() <= target_date
                except:
                    return False

            filtered_docs = [
                doc for doc in filtered_docs if is_date_before_or_equal(doc, date_to)
            ]

        # Value threshold filter
        if value_threshold > 0:
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("totalGross", 0) >= value_threshold
            ]

        # Filter results badge
        if len(filtered_docs) != len(docs):
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, 
                        rgba(255, 255, 255, 0.95) 0%, 
                        rgba(255, 255, 255, 0.8) 50%,
                        rgba(59, 130, 246, 0.06) 100%);
                    backdrop-filter: blur(16px) saturate(180%);
                    -webkit-backdrop-filter: blur(16px) saturate(180%);
                    border: 1px solid rgba(255, 255, 255, 0.8);
                    border-radius: 12px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    box-shadow: 
                        0 4px 16px rgba(0, 0, 0, 0.06),
                        0 2px 4px rgba(0, 0, 0, 0.04),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9);
                ">
                    <span style="font-size: 1.25rem;">🔎</span>
                    <span style="color: #1e40af; font-weight: 600;">
                        Showing {len(filtered_docs)} of {len(docs)} documents
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Convert to DataFrame for display
        if filtered_docs:
            df_data = []
            for doc in filtered_docs:
                df_data.append(
                    {
                        "Document ID": doc.get("documentId"),
                        "Name": doc.get("simpleName", "N/A"),
                        "Company": doc.get("companyName", "N/A"),
                        "Flow": doc.get("flowName", "N/A"),
                        "Stage": doc.get("currentStage", "N/A"),
                        "Invoice #": doc.get("invoiceNumber", "N/A"),
                        "Invoice Date": doc.get("invoiceDate", "N/A"),
                        "Total Gross": doc.get("totalGross", 0),
                        "Currency": doc.get("currencyCode", "EUR"),
                        "Supplier": doc.get("supplierName", "N/A"),
                        "Payment State": doc.get("paymentState", "N/A"),
                    }
                )

            df = pd.DataFrame(df_data)

            # Modern table header
            st.markdown("#### Documents Table")

            # Display table with modern styling
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500,
                column_config={
                    "Document ID": st.column_config.NumberColumn(
                        "ID", help="Unique document identifier", format="%d"
                    ),
                    "Total Gross": st.column_config.NumberColumn(
                        "Total Gross", help="Total gross amount", format="%.2f €"
                    ),
                    "Stage": st.column_config.TextColumn(
                        "Stage", help="Current workflow stage"
                    ),
                    "Payment State": st.column_config.TextColumn(
                        "Payment", help="Payment status"
                    ),
                },
            )

            # Export options with glassmorphic action bar
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"#### {t('common.export_options')}")

            col1, col2 = st.columns(2)

            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                json_data = json.dumps(filtered_docs, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

# ============================================================================
# PAGE: SINGLE DOCUMENT
# ============================================================================
elif page == "🔎 " + t("pages.single_document"):
    # Apply all styles at once to minimize spacing
    st.markdown(
        get_page_header_purple() + 
        get_action_bar_styles() + 
        get_info_box_styles() + 
        get_card_styles() + 
        get_metric_styles() + 
        get_tab_styles() +
        get_theme_text_styles(),
        unsafe_allow_html=True,
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
    col1, col2 = st.columns([4, 1])

    with col1:
        doc_id = st.number_input(
            "🔢 " + t("single_document_page.enter_id"),
            min_value=1,
            step=1,
            value=1,
            help="Enter the unique document ID to retrieve details",
            label_visibility="visible",
        )

    with col2:
        # Align button with input field
        st.markdown('<div style="margin-top: 1.85rem;"></div>', unsafe_allow_html=True)
        if st.button(
            t("common.get_document"),
            type="primary",
            use_container_width=True,
            key="btn_get_document_details",
        ):
            with st.spinner("🔍 " + t("common.loading")):
                doc = st.session_state.client.get_document(doc_id)
                st.session_state.selected_document = doc
                # Also get receipt splits (Belegaufteilung)
                if doc:
                    splits = st.session_state.client.get_receipt_splits(doc_id)
                    st.session_state.receipt_splits = splits if splits else []
                    st.success(f"Document #{doc_id} loaded successfully")
                else:
                    st.error(f"❌ Document #{doc_id} not found")

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

                # Download splits as CSV
                splits_df = pd.DataFrame(splits)
                csv_splits = splits_df.to_csv(index=False)
                st.download_button(
                    label="  Download Receipt Splits CSV",
                    data=csv_splits,
                    file_name=f"document_{doc_id}_splits.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        else:
            st.markdown(
                """
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
                        No receipt splits (Belegaufteilung) found for this document. 
                        The document may not have been split yet.
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Document Overview with modern header
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="section-header">
                <div class="section-icon">📋</div>
                <h3>Document Overview</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

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
            csv_data = df_details.to_csv(index=False)
            st.download_button(
                label="  Download All Fields CSV",
                data=csv_data,
                file_name=f"document_{doc_id}_all_fields.csv",
                mime="text/csv",
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
    # Add theme-adaptive styles
    st.markdown(
        get_card_styles() + get_theme_text_styles() + get_section_header_styles(),
        unsafe_allow_html=True,
    )
    
    # Glossy page header card
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(79, 70, 229, 0.05) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
            box-shadow: 0 4px 24px rgba(99, 102, 241, 0.12),
                        0 2px 6px rgba(0, 0, 0, 0.04);
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
                box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">🏢</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('companies_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Manage companies and approval flows</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button(
        t("companies_page.refresh"), type="primary", key="btn_refresh_companies"
    ):
        with st.spinner(t("common.loading")):
            companies = st.session_state.client.get_companies_with_flows()
            st.session_state.companies = companies

    if "companies" in st.session_state and st.session_state.companies:
        st.success(f"Found {len(st.session_state.companies)} company/flow combinations")

        # Convert to DataFrame
        df_data = []
        for comp in st.session_state.companies:
            df_data.append(
                {
                    "Company ID": comp.get("companyId"),
                    "Company Name": comp.get("companyName"),
                    "Flow ID": comp.get("flowId"),
                    "Flow Name": comp.get("flowName"),
                }
            )

        df = pd.DataFrame(df_data)

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Summary statistics
        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                📊 Summary Statistics
            </h3>
        """,
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns(2)

        unique_companies = df["Company Name"].nunique()
        total_flows = len(df)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card-light" style="
                    --card-color: rgba(99, 102, 241, 0.04);
                    --card-color-dark: #6366f130;
                    padding: 1.5rem 1rem;
                    border-radius: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                    cursor: default;
                    min-height: 180px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        font-size: 2.5rem;
                        font-weight: 900;
                        color: #6366f1;
                        margin-bottom: 0.5rem;
                        line-height: 1.2;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    ">{unique_companies}</div>
                    <div class="metric-label" style="
                        font-size: 0.85rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        line-height: 1.3;
                    ">Unique Companies</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card-light" style="
                    --card-color: rgba(139, 92, 246, 0.04);
                    --card-color-dark: #8b5cf630;
                    padding: 1.5rem 1rem;
                    border-radius: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                    cursor: default;
                    min-height: 180px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        font-size: 2.5rem;
                        font-weight: 900;
                        color: #8b5cf6;
                        margin-bottom: 0.5rem;
                        line-height: 1.2;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    ">{total_flows}</div>
                    <div class="metric-label" style="
                        font-size: 0.85rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        line-height: 1.3;
                    ">Total Flows</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        st.info("🏢 Click 'Refresh Companies' to load the list of companies and flows")

# ============================================================================
# PAGE: DOWNLOAD DOCUMENT
# ============================================================================
elif page == "  " + t("pages.download"):
    # Apply cyan header styles
    st.markdown(get_page_header_cyan(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-cyan" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(14, 165, 233, 0.9) 0%, rgba(2, 132, 199, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(14, 165, 233, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">📥</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('download_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Download document PDFs using ID and unique identifier</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Apply info box styles
    st.markdown(get_info_box_styles(), unsafe_allow_html=True)
    
    # Info box with glassmorphic styling
    st.markdown(
        f"""
        <div class="info-box">
            <div class="info-box-icon">💡</div>
            <div class="info-box-text">{t("download_page.info")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        download_doc_id = st.number_input(
            "Document ID", min_value=1, step=1, value=1, key="download_id"
        )

    with col2:
        unique_id = st.text_input(
            "Unique ID (UUID)", placeholder="e.g., a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        )

    st.write(
        "**Tip:** Get the Unique ID by first viewing the document details in the 'Single Document' page"
    )
    
    # Apply action bar styles
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    if st.button(
        "Get Document Details (to find Unique ID)", key="btn_get_download_details"
    ):
        with st.spinner(f"Fetching document {download_doc_id}..."):
            doc = st.session_state.client.get_document(download_doc_id)
            if doc:
                st.success("Document found!")
                st.write("**Unique ID:**")
                st.code(doc.get("uniqueId"), language="text")
                st.write("**Document Name:**", doc.get("simpleName"))

    if unique_id and st.button("Download PDF", type="primary", key="btn_download_pdf"):
        output_path = f"document_{download_doc_id}.pdf"
        with st.spinner(f"Downloading document {download_doc_id}..."):
            success = st.session_state.client.download_document(
                download_doc_id, unique_id, output_path
            )
            if success:
                st.success(f"Document downloaded to: {output_path}")

                # Provide download button
                try:
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="💾 Save to your computer",
                            data=f,
                            file_name=output_path,
                            mime="application/pdf",
                        )
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            else:
                st.error("❌ Download failed. Check the Document ID and Unique ID.")

# ============================================================================
# PAGE: UPLOAD DOCUMENT
# ============================================================================
elif page == "📤 " + t("pages.upload"):
    # Apply rose header styles
    st.markdown(get_page_header_rose(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-rose" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(244, 63, 94, 0.9) 0%, rgba(225, 29, 72, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(244, 63, 94, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">📤</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('upload_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Upload PDF documents to Flowwer</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Apply alert box styles
    st.markdown(get_alert_box_styles(), unsafe_allow_html=True)
    
    # Feature disabled notice with glassmorphic styling
    st.markdown(
        """
        <div class="warning-box">
            <div class="warning-box-icon">⚠️</div>
            <div class="warning-box-text">Document upload is currently disabled. This feature will be available soon.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        t("upload_page.choose_file"), type=["pdf"], disabled=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        flow_id = st.number_input(
            "Flow ID (optional)", min_value=0, step=1, value=0, disabled=True
        )

    with col2:
        company_id = st.number_input(
            "Company ID (optional)", min_value=0, step=1, value=0, disabled=True
        )

    with col3:
        custom_filename = st.text_input(
            "Custom filename (optional)", placeholder="invoice.pdf", disabled=True
        )

    if uploaded_file and st.button(
        "Upload to Flowwer", type="primary", key="btn_upload_document", disabled=True
    ):
        # Save uploaded file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Uploading document..."):
            result = st.session_state.client.upload_document(
                temp_path,
                flow_id=flow_id if flow_id > 0 else None,
                company_id=company_id if company_id > 0 else None,
                filename=custom_filename if custom_filename else None,
            )

            if result:
                st.success("Document uploaded successfully!")
                st.write("**Document ID:**", result.get("elementId"))
                st.write("**Name:**", result.get("name"))
            else:
                st.error("❌ Upload failed. Check the logs for details.")

        # Clean up temp file
        import os

        try:
            os.remove(temp_path)
        except:
            pass

# ============================================================================
# PAGE: DATA EXPLORER
# ============================================================================
elif page == "📊 " + t("pages.data_explorer"):
    # Apply teal header styles
    st.markdown(get_page_header_teal(), unsafe_allow_html=True)
    st.markdown(get_export_bar_styles(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-teal" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(20, 184, 166, 0.9) 0%, rgba(13, 148, 136, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(20, 184, 166, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">📊</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">Data Explorer - Flexible Document Export</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">View and export all documents with receipt splits and customizable columns</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Apply card styles (includes section headers) and action bar styles
    st.markdown(get_card_styles(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    # Load Data Section
    st.markdown('<div class="section-header"><span class="section-icon">1️⃣</span> Load Data</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        include_processed = st.checkbox(
            "Include Processed Documents", value=True, key="explorer_processed"
        )
    with col2:
        include_deleted = st.checkbox(
            "Include Deleted Documents", value=False, key="explorer_deleted"
        )
    with col3:
        if st.button(
            "Load All Documents",
            type="primary",
            use_container_width=True,
            key="btn_load_explorer_docs",
        ):
            with st.spinner("Loading documents and receipt splits..."):
                # Fetch all documents
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed, include_deleted=include_deleted
                )

                if docs:
                    # For each document, try to get receipt splits
                    all_data = []
                    progress_bar = st.progress(0)

                    for idx, doc in enumerate(docs):
                        doc_id = doc.get("documentId")
                        if doc_id is None:
                            continue

                        splits = st.session_state.client.get_receipt_splits(doc_id)

                        if splits and len(splits) > 0:
                            # Document has splits - create one row per split
                            for split in splits:
                                merged_data = {
                                    # ID & Display
                                    "Document ID": doc_id,
                                    "Display Name": doc.get("simpleName", ""),
                                    # Belegaufteilung (Document Splitting)
                                    "Booking Text": split.get("name", ""),
                                    "Cost Center": split.get("costCenter", ""),
                                    "Cost Unit (KOST2)": split.get("costUnit", ""),
                                    "Tax Rate %": split.get("taxPercent", ""),
                                    # Invoice-related (Rechnungsbezogen)
                                    "Invoice Date": split.get(
                                        "invoiceDate", doc.get("invoiceDate", "")
                                    ),
                                    "Receipt Number": doc.get("receiptNumber", ""),
                                    "Gross": split.get(
                                        "grossValue", doc.get("totalGross", "")
                                    ),
                                    "Net": split.get(
                                        "netValue", doc.get("totalNet", "")
                                    ),
                                    "Company": doc.get("companyName", ""),
                                    "Date of Receipt": doc.get(
                                        "dateOfReceipt", doc.get("uploadTime", "")
                                    ),
                                    "Document Type": doc.get("documentType", ""),
                                    "Document Status": doc.get("currentStage", ""),
                                    "Purchase Order Number": doc.get(
                                        "purchaseOrderNumber", ""
                                    ),
                                    "Own Reference": doc.get("ownReference", ""),
                                    "Foreign Reference": doc.get(
                                        "foreignReference", ""
                                    ),
                                    # Payment (Bezahlung)
                                    "Currency": doc.get("currencyCode", ""),
                                    "Due Date": doc.get("dueDate", ""),
                                    "Discount Amount": doc.get("discountAmount", ""),
                                    "Discount End Period": doc.get(
                                        "discountPeriodEnd", ""
                                    ),
                                    "Payment State": split.get(
                                        "paymentState", doc.get("paymentState", "")
                                    ),
                                    "Payment Date": doc.get("paymentDate", ""),
                                    "Payment Method": doc.get("paymentMethod", ""),
                                    "Dunned": doc.get("isDunning", ""),
                                    "On Hold": doc.get("isOnHold", ""),
                                    # Approval (Freigabe)
                                    "Flow": doc.get("flowName", ""),
                                    "Approval Status": split.get(
                                        "currentStage", doc.get("currentStage", "")
                                    ),
                                    "Stage Timestamp": doc.get("stageTimestamp", ""),
                                    # Others (Weiteres)
                                    "Supplier Name": split.get(
                                        "supplierName", doc.get("supplierName", "")
                                    ),
                                    "Supplier VAT ID": doc.get("supplierVATId", ""),
                                    "Service Date Start": doc.get(
                                        "serviceStartDate", ""
                                    ),
                                    "Service Date End": doc.get("serviceEndDate", ""),
                                    "File Name": split.get(
                                        "documentName", doc.get("simpleName", "")
                                    ),
                                    "Creation": doc.get("creationTimestampUtc", ""),
                                    "File Size": doc.get("fileSize", ""),
                                }
                                all_data.append(merged_data)
                        else:
                            # No splits - create single row with document data
                            merged_data = {
                                # ID & Display
                                "Document ID": doc_id,
                                "Display Name": doc.get("simpleName", ""),
                                # Belegaufteilung (Document Splitting)
                                "Booking Text": "",
                                "Cost Center": "",
                                "Cost Unit (KOST2)": "",
                                "Tax Rate %": "",
                                # Invoice-related
                                "Invoice Date": doc.get("invoiceDate", ""),
                                "Receipt Number": doc.get("receiptNumber", ""),
                                "Gross": doc.get("totalGross", ""),
                                "Net": doc.get("totalNet", ""),
                                "Company": doc.get("companyName", ""),
                                "Date of Receipt": doc.get(
                                    "dateOfReceipt", doc.get("uploadTime", "")
                                ),
                                "Document Type": doc.get("documentType", ""),
                                "Document Status": doc.get("currentStage", ""),
                                "Purchase Order Number": doc.get(
                                    "purchaseOrderNumber", ""
                                ),
                                "Own Reference": doc.get("ownReference", ""),
                                "Foreign Reference": doc.get("foreignReference", ""),
                                # Payment
                                "Currency": doc.get("currencyCode", ""),
                                "Due Date": doc.get("dueDate", ""),
                                "Discount Amount": doc.get("discountAmount", ""),
                                "Discount End Period": doc.get("discountPeriodEnd", ""),
                                "Payment State": doc.get("paymentState", ""),
                                "Payment Date": doc.get("paymentDate", ""),
                                "Payment Method": doc.get("paymentMethod", ""),
                                "Dunned": doc.get("isDunning", ""),
                                "On Hold": doc.get("isOnHold", ""),
                                # Approval
                                "Flow": doc.get("flowName", ""),
                                "Approval Status": doc.get("currentStage", ""),
                                "Stage Timestamp": doc.get("stageTimestamp", ""),
                                # Others
                                "Supplier Name": doc.get("supplierName", ""),
                                "Supplier VAT ID": doc.get("supplierVATId", ""),
                                "Service Date Start": doc.get("serviceStartDate", ""),
                                "Service Date End": doc.get("serviceEndDate", ""),
                                "File Name": doc.get("simpleName", ""),
                                "Creation": doc.get("creationTimestampUtc", ""),
                                "File Size": doc.get("fileSize", ""),
                            }
                            all_data.append(merged_data)

                        # Update progress
                        progress_bar.progress((idx + 1) / len(docs))

                    # Create DataFrame
                    df_export = pd.DataFrame(all_data)

                    # Format dates for better readability
                    date_columns = [
                        "Invoice Date",
                        "Date of Receipt",
                        "Due Date",
                        "Payment Date",
                        "Service Date Start",
                        "Service Date End",
                        "Discount End Period",
                        "Stage Timestamp",
                        "Creation",
                    ]

                    for col in date_columns:
                        if col in df_export.columns:
                            # Convert to datetime and format as YYYY-MM-DD (or empty string if invalid)
                            df_export[col] = pd.to_datetime(
                                df_export[col], errors="coerce"
                            ).dt.strftime("%Y-%m-%d")
                            df_export[col] = df_export[col].fillna(
                                ""
                            )  # Replace NaT with empty string

                    st.session_state.explorer_data = df_export
                    st.success(
                        f"Loaded {len(all_data)} rows from {len(docs)} documents"
                    )
                else:
                    st.error("Failed to load documents")

    # Column Selection Section
    if (
        "explorer_data" in st.session_state
        and st.session_state.explorer_data is not None
    ):
        df = st.session_state.explorer_data

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 2️⃣ {t('common.select_columns')}")

        # Define column categories
        column_categories = {
            "ID & Display": ["Document ID", "Display Name"],
            "Belegaufteilung (Document Splitting)": [
                "Booking Text",
                "Cost Center",
                "Cost Unit (KOST2)",
                "Tax Rate %",
            ],
            "Rechnungsbezogen (Invoice-related)": [
                "Invoice Date",
                "Receipt Number",
                "Gross",
                "Net",
                "Company",
                "Date of Receipt",
                "Document Type",
                "Document Status",
                "Purchase Order Number",
                "Own Reference",
                "Foreign Reference",
            ],
            "Bezahlung (Payment)": [
                "Currency",
                "Due Date",
                "Discount Amount",
                "Discount End Period",
                "Payment State",
                "Payment Date",
                "Payment Method",
                "Dunned",
                "On Hold",
            ],
            "Freigabe (Approval)": ["Flow", "Approval Status", "Stage Timestamp"],
            "Weiteres (Others)": [
                "Supplier Name",
                "Supplier VAT ID",
                "Service Date Start",
                "Service Date End",
                "File Name",
                "Creation",
                "File Size",
            ],
        }

        # Initialize selected columns in session state
        if "selected_columns" not in st.session_state:
            # Default: select commonly used columns
            st.session_state.selected_columns = [
                "Document ID",
                "Display Name",
                "Booking Text",
                "Cost Center",
                "Invoice Date",
                "Gross",
                "Net",
                "Company",
                "Supplier Name",
                "Payment State",
            ]

        # Column selector with categories
        with st.expander("📋 Column Selection (Click to expand)", expanded=False):

            # Quick select buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Select All"):
                    st.session_state.selected_columns = list(df.columns)
                    st.rerun()
            with col2:
                if st.button("Deselect All"):
                    st.session_state.selected_columns = []
                    st.rerun()
            with col3:
                if st.button("Reset to Default"):
                    st.session_state.selected_columns = [
                        "Document ID",
                        "Display Name",
                        "Booking Text",
                        "Cost Center",
                        "Invoice Date",
                        "Gross",
                        "Net",
                        "Company",
                        "Supplier Name",
                        "Payment State",
                    ]
                    st.rerun()

            st.markdown("---")

            # Category-based column selection
            for category, columns in column_categories.items():
                st.markdown(f"**{category}**")

                # Create columns for checkboxes (3 per row)
                cols = st.columns(3)
                for idx, col_name in enumerate(columns):
                    with cols[idx % 3]:
                        if col_name in df.columns:
                            checked = col_name in st.session_state.selected_columns
                            if st.checkbox(
                                col_name, value=checked, key=f"col_{col_name}"
                            ):
                                if col_name not in st.session_state.selected_columns:
                                    st.session_state.selected_columns.append(col_name)
                            else:
                                if col_name in st.session_state.selected_columns:
                                    st.session_state.selected_columns.remove(col_name)

                st.markdown("")  # Spacing

        st.info(
            f"📊 Selected {len(st.session_state.selected_columns)} of {len(df.columns)} columns"
        )

        # Display Data Section
        st.markdown("---")
        st.markdown(f'<div class="section-header"><span class="section-icon">3️⃣</span> {t("common.view_export_data")}</div>', unsafe_allow_html=True)

        # Filter data by selected columns
        if st.session_state.selected_columns:
            display_df = df[st.session_state.selected_columns]

            # Show row count and data
            st.write(f"**{t('common.total_rows')}:** {len(display_df)}")

            # Display dataframe
            st.dataframe(display_df, use_container_width=True, height=500)

            # Export options
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header"><span class="section-icon">📦</span> Export Options</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                csv_data = display_df.to_csv(index=False)
                st.download_button(
                    label="  Download CSV",
                    data=csv_data,
                    file_name=f"flowwer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                json_data = display_df.to_json(orient="records", indent=2)
                st.download_button(
                    label="  Download JSON",
                    data=json_data,
                    file_name=f"flowwer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
        else:
            st.warning("⚠️ Please select at least one column to display")
    else:
        st.info(" Click 'Load All Documents' above to start exploring data")

# ============================================================================
# PAGE: RECEIPT SPLITTING REPORT
# ============================================================================
elif page == "📑 " + t("pages.receipt_report"):
    # Apply indigo header styles
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
                box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">📑</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('receipt_report_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">{t('receipt_report_page.subtitle')}</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Apply card styles (includes section headers)
    st.markdown(get_card_styles(), unsafe_allow_html=True)

    # Load filter options first
    st.markdown(f'<div class="section-header"><span class="section-icon">1️⃣</span> {t("receipt_report_page.load_options")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Load Cost Centers", use_container_width=True, key="btn_load_cost_centers"
        ):
            with st.spinner("Loading cost centers..."):
                cost_centers = st.session_state.client.get_all_cost_centers()
                if cost_centers:
                    st.session_state.cost_centers = cost_centers
                    st.success(f"Loaded {len(cost_centers)} cost centers")

    with col2:
        if st.button(
            "Load Accounts", use_container_width=True, key="btn_load_accounts"
        ):
            with st.spinner("Loading accounts..."):
                accounts = st.session_state.client.get_all_accounts()
                if accounts:
                    st.session_state.accounts = accounts
                    st.success(f"Loaded {len(accounts)} accounts")

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter Section
    st.markdown(f'<div class="section-header"><span class="section-icon">2️⃣</span> {t("receipt_report_page.filters")}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        # Cost Center filter
        cost_center_list = st.session_state.get("cost_centers", [])
        # Ensure all items are strings
        cost_center_options = ["All Cost Centers"] + [
            str(cc) for cc in cost_center_list if cc
        ]
        selected_cost_center = st.selectbox(
            t("receipt_report_page.cost_center"), cost_center_options
        )
        # Convert back to empty string for API if "All" selected
        if selected_cost_center == "All Cost Centers":
            selected_cost_center = ""

    with col2:
        # Account filter
        account_list = st.session_state.get("accounts", [])
        # Ensure all items are strings
        account_options = ["All Accounts"] + [str(acc) for acc in account_list if acc]
        selected_account = st.selectbox(
            t("receipt_report_page.account"), account_options
        )
        # Convert back to empty string for API if "All" selected
        if selected_account == "All Accounts":
            selected_account = ""

    with col3:
        # Company filter
        selected_company = st.text_input(
            t("receipt_report_page.company"), placeholder="e.g., Enprom GmbH"
        )

    # Date range filter
    st.markdown("**" + t("receipt_report_page.date_range") + "**")
    col1, col2 = st.columns(2)
    with col1:
        min_date = st.date_input(
            "📅 " + t("receipt_report_page.from_date"),
            value=datetime.now() - timedelta(days=30),
        )
    with col2:
        max_date = st.date_input(
            "📅 " + t("receipt_report_page.to_date"), value=datetime.now()
        )

    # Generate Report Button
    if st.button(
        t("receipt_report_page.generate"),
        type="primary",
        key="btn_generate_receipt_report",
    ):
        with st.spinner(t("receipt_report_page.loading")):
            # Prepare filter parameters
            filter_params = {}
            if selected_cost_center:
                filter_params["cost_center"] = selected_cost_center
            if selected_account:
                filter_params["account"] = selected_account
            if selected_company:
                filter_params["company"] = selected_company
            if min_date:
                filter_params["min_date"] = min_date.isoformat()
            if max_date:
                filter_params["max_date"] = max_date.isoformat()

            # Get report
            report = st.session_state.client.get_receipt_splitting_report(
                **filter_params
            )

            if report:
                st.session_state.receipt_report = report
                st.success(f"{len(report)} " + t("receipt_report_page.found"))

    # Display Report
    if "receipt_report" in st.session_state and st.session_state.receipt_report:
        st.markdown("---")
        st.subheader("3️⃣ Report Results")

        report_data = st.session_state.receipt_report

        # Convert to DataFrame
        df = pd.DataFrame(report_data)

        # Format dates
        if "invoiceDate" in df.columns:
            df["invoiceDate"] = pd.to_datetime(
                df["invoiceDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        # Display
        st.dataframe(df, use_container_width=True, height=500)

        # Export
        st.markdown("---")
        st.subheader("  " + t("receipt_report_page.export"))

        csv_data = df.to_csv(index=False)
        st.download_button(
            label=t("receipt_report_page.download_csv"),
            data=csv_data,
            file_name=f"receipt_splitting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info(" " + t("receipt_report_page.no_data"))

# ============================================================================
# PAGE: APPROVED DOCUMENTS
# ============================================================================
elif page == "✅ " + t("pages.approved_docs"):
    # Apply green header styles
    st.markdown(get_page_header_green(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-green" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.9) 0%, rgba(22, 163, 74, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(34, 197, 94, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">✅</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('approved_docs_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">{t('approved_docs_page.subtitle')}</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Get companies/flows for filtering
    col1, col2 = st.columns([3, 1])

    with col1:
        # Flow filter
        if "companies" in st.session_state and st.session_state.companies:
            flow_options = [{"id": None, "name": t("approved_docs_page.all_flows")}]
            flow_options.extend(
                [
                    {
                        "id": comp.get("flowId"),
                        "name": f"{comp.get('flowName')} ({comp.get('companyName')})",
                    }
                    for comp in st.session_state.companies
                ]
            )

            selected_flow_idx = st.selectbox(
                t("approved_docs_page.filter_by_flow"),
                range(len(flow_options)),
                format_func=lambda i: flow_options[i]["name"],
            )
            selected_flow_id = flow_options[selected_flow_idx]["id"]
        else:
            selected_flow_id = None
            st.info(
                "💡 Load companies first (in Companies page) to enable flow filtering"
            )

    with col2:
        st.write("")
        st.write("")
        if st.button(
            t("approved_docs_page.load_documents"),
            type="primary",
            use_container_width=True,
            key="btn_load_approved_docs",
        ):
            with st.spinner(t("approved_docs_page.loading")):
                docs = st.session_state.client.get_approved_documents(
                    flow_id=selected_flow_id
                )
                if docs:
                    st.session_state.approved_documents = docs
                    st.success(f"{len(docs)} " + t("approved_docs_page.found"))

    # Display approved documents
    if "approved_documents" in st.session_state and st.session_state.approved_documents:
        docs = st.session_state.approved_documents

        # Convert to DataFrame
        df_data = []
        for doc in docs:
            df_data.append(
                {
                    "Document ID": doc.get("documentId"),
                    "Name": doc.get("simpleName", "N/A"),
                    "Company": doc.get("companyName", "N/A"),
                    "Flow": doc.get("flowName", "N/A"),
                    "Invoice #": doc.get("invoiceNumber", "N/A"),
                    "Invoice Date": doc.get("invoiceDate", "N/A"),
                    "Total Gross": doc.get("totalGross", 0),
                    "Currency": doc.get("currencyCode", "EUR"),
                    "Supplier": doc.get("supplierName", "N/A"),
                    "Payment State": doc.get("paymentState", "N/A"),
                }
            )

        df = pd.DataFrame(df_data)

        # Format dates
        if "Invoice Date" in df.columns:
            df["Invoice Date"] = pd.to_datetime(
                df["Invoice Date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            df["Invoice Date"] = df["Invoice Date"].fillna("")

        st.dataframe(df, use_container_width=True, height=500)

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 💾 {t('common.export_options')}")

        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="  Download CSV",
                data=csv,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            json_data = json.dumps(docs, indent=2)
            st.download_button(
                label="  Download JSON",
                data=json_data,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
    else:
        st.info(" " + t("approved_docs_page.no_data"))

# ============================================================================
# PAGE: SIGNABLE DOCUMENTS (PENDING APPROVALS)
# ============================================================================
elif page == "⏳ " + t("pages.signable_docs"):
    # Apply amber header styles
    st.markdown(get_page_header_amber(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-amber" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.9) 0%, rgba(217, 119, 6, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(245, 158, 11, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">⏳</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('signable_docs_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">{t('signable_docs_page.subtitle')}</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        backup_list = st.checkbox(t("signable_docs_page.backup_list"), value=False)

    with col2:
        st.write("")
        st.write("")
        if st.button(" " + t("signable_docs_page.load_documents"), type="primary"):
            with st.spinner(t("signable_docs_page.loading")):
                docs = st.session_state.client.get_signable_documents(
                    backup_list=backup_list
                )
                if docs:
                    st.session_state.signable_documents = docs
                    st.success(f"{len(docs)} " + t("signable_docs_page.found"))

    # Display signable documents
    if "signable_documents" in st.session_state and st.session_state.signable_documents:
        docs = st.session_state.signable_documents

        # Convert to DataFrame
        df_data = []
        for doc in docs:
            df_data.append(
                {
                    "Document ID": doc.get("documentId"),
                    "Name": doc.get("simpleName", "N/A"),
                    "Company": doc.get("companyName", "N/A"),
                    "Flow": doc.get("flowName", "N/A"),
                    "Current Stage": doc.get("currentStage", "N/A"),
                    "Invoice #": doc.get("invoiceNumber", "N/A"),
                    "Invoice Date": doc.get("invoiceDate", "N/A"),
                    "Total Gross": doc.get("totalGross", 0),
                    "Currency": doc.get("currencyCode", "EUR"),
                    "Supplier": doc.get("supplierName", "N/A"),
                    "Upload Time": doc.get("uploadTime", "N/A"),
                }
            )

        df = pd.DataFrame(df_data)

        # Format dates
        date_columns = ["Invoice Date", "Upload Time"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime(
                    "%Y-%m-%d"
                )
                df[col] = df[col].fillna("")

        st.dataframe(df, use_container_width=True, height=500)

        # Export
        st.markdown("---")
        st.subheader("  " + t("signable_docs_page.export"))

        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="  Download as CSV",
                data=csv,
                file_name=f"signable_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            json_data = json.dumps(docs, indent=2)
            st.download_button(
                label="  Download as JSON",
                data=json_data,
                file_name=f"signable_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
    else:
        st.info(" " + t("signable_docs_page.no_data"))

# ============================================================================
# PAGE: ANALYTICS DASHBOARD
# ============================================================================
elif page == "📈 " + t("pages.analytics"):
    # Apply amber header styles
    st.markdown(get_page_header_amber(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-amber" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(251, 146, 60, 0.9) 0%, rgba(249, 115, 22, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(251, 146, 60, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">�</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('analytics_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Interactive data visualization and insights</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Apply card styles (for section headers) and tab styles
    st.markdown(
        get_card_styles() + 
        get_tab_styles() + 
        get_metric_styles() + 
        get_theme_text_styles() + 
        get_section_header_styles(), 
        unsafe_allow_html=True
    )

    # Load controls
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        include_processed_analytics = st.checkbox(
            "Include Processed", value=True, key="analytics_processed"
        )

    with col2:
        include_deleted_analytics = st.checkbox(
            "Include Deleted", value=False, key="analytics_deleted"
        )

    with col3:
        if st.button(
            "Load Data",
            type="primary",
            use_container_width=True,
            key="btn_load_analytics_docs",
        ):
            with st.spinner("Loading documents..."):
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed_analytics,
                    include_deleted=include_deleted_analytics,
                )
                st.session_state.documents = docs
                st.session_state.analytics_load_time = datetime.now()
                st.rerun()

    if st.session_state.documents is None:
        st.info("📊 Click 'Load Data' to view analytics and insights")
    else:
        docs = st.session_state.documents

        # Data freshness indicator
        if "analytics_load_time" in st.session_state:
            load_time = st.session_state.analytics_load_time
            time_diff = datetime.now() - load_time
            minutes_ago = int(time_diff.total_seconds() / 60)

            freshness_text = "just now" if minutes_ago < 1 else f"{minutes_ago} min ago"
            st.markdown(
                f"""
                <div class="text-secondary" style="text-align: right; font-size: 0.85rem; margin-bottom: 1rem;">
                    📡 Data loaded {freshness_text} | {len(docs)} documents
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Enhanced KPI Section
        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                <span style="font-size: 2rem;">📊</span>
                Key Performance Indicators
            </h3>
        """,
            unsafe_allow_html=True,
        )

        # Calculate comprehensive metrics
        total_gross = sum([doc.get("totalGross", 0) for doc in docs])
        total_net = sum([doc.get("totalNet", 0) for doc in docs])
        total_tax = total_gross - total_net
        avg_invoice_value = total_gross / len(docs) if len(docs) > 0 else 0

        # Stage analysis
        stage_counts = {}
        for doc in docs:
            stage = doc.get("currentStage", "Unknown")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

        approved_count = stage_counts.get("Approved", 0)
        in_workflow = sum(stage_counts.get(f"Stage{i}", 0) for i in range(1, 6))
        draft_count = stage_counts.get("Draft", 0)
        approval_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0

        # Payment analysis
        payment_counts = {}
        payment_totals = {}
        for doc in docs:
            payment = doc.get("paymentState", "Unknown")
            payment_counts[payment] = payment_counts.get(payment, 0) + 1
            payment_totals[payment] = payment_totals.get(payment, 0) + doc.get(
                "totalGross", 0
            )

        pending_payment_value = payment_totals.get("Open", 0) + payment_totals.get(
            "Pending", 0
        )

        # Supplier & Company counts
        unique_companies = len(
            set([doc.get("companyName") for doc in docs if doc.get("companyName")])
        )
        unique_suppliers = len(
            set([doc.get("supplierName") for doc in docs if doc.get("supplierName")])
        )

        # Display enhanced KPIs with glassmorphic metric cards matching All Documents page
        kpi_cols = st.columns(6)

        kpis = [
            ("Total Documents", len(docs), "#3b82f6", "rgba(59, 130, 246, 0.04)"),
            ("Total Value", f"€{total_gross:,.0f}", "#10b981", "rgba(16, 185, 129, 0.04)"),
            ("Avg Invoice", f"€{avg_invoice_value:,.0f}", "#8b5cf6", "rgba(139, 92, 246, 0.04)"),
            ("Approval Rate", f"{approval_rate:.1f}%", "#22c55e", "rgba(34, 197, 94, 0.04)"),
            ("Pending Payments", f"€{pending_payment_value:,.0f}", "#f59e0b", "rgba(245, 158, 11, 0.04)"),
            ("Total Tax", f"€{total_tax:,.0f}", "#ef4444", "rgba(239, 68, 68, 0.04)"),
        ]

        for idx, (label, value, color, bg) in enumerate(kpis):
            with kpi_cols[idx]:
                st.markdown(
                    f"""
                    <div class="metric-card-light" style="
                        --card-color: {bg};
                        --card-color-dark: {color}30;
                        padding: 1.5rem 0.75rem;
                        border-radius: 20px;
                        text-align: center;
                        transition: all 0.3s ease;
                        cursor: default;
                        min-height: 180px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            font-size: 2rem;
                            font-weight: 900;
                            color: {color};
                            margin-bottom: 0.5rem;
                            line-height: 1.1;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                            white-space: nowrap;
                            overflow: visible;
                        ">{value}</div>
                        <div class="metric-label" style="
                            font-size: 0.85rem;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            line-height: 1.3;
                        ">{label}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Detailed Analysis Section Header
        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                <span style="font-size: 2rem;">📊</span>
                Detailed Analytics
            </h3>
        """,
            unsafe_allow_html=True,
        )

        # Tabbed Analysis Sections
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Financial Analysis",
                "⚙️ Workflow Analysis",
                "🏪 Supplier Analysis",
                "📅 Timeline Analysis",
            ]
        )

        # TAB 1: Financial Analysis
        with tab1:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">💰</span>
                    Financial Breakdown
                </h3>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                # Payment Status Distribution (Donut Chart)
                st.markdown('<div class="section-header"><span class="section-icon">💳</span> Payment Status</div>', unsafe_allow_html=True)
                if payment_counts:
                    fig_payment = px.pie(
                        values=list(payment_counts.values()),
                        names=list(payment_counts.keys()),
                        hole=0.5,
                        color_discrete_sequence=[
                            "#22c55e",
                            "#f59e0b",
                            "#ef4444",
                            "#3b82f6",
                        ],
                    )
                    fig_payment.update_traces(
                        textposition="inside", textinfo="percent+label"
                    )
                    fig_payment.update_layout(height=350, showlegend=True)
                    st.plotly_chart(fig_payment, use_container_width=True)

                # Currency Breakdown
                st.markdown('<div class="section-header"><span class="section-icon">💱</span> Currency Distribution</div>', unsafe_allow_html=True)
                currency_totals = {}
                for doc in docs:
                    currency = doc.get("currencyCode", "EUR")
                    value = doc.get("totalGross", 0)
                    currency_totals[currency] = currency_totals.get(currency, 0) + value

                for currency, total in sorted(
                    currency_totals.items(), key=lambda x: x[1], reverse=True
                ):
                    percentage = (total / total_gross * 100) if total_gross > 0 else 0
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
                            padding: 0.75rem;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                            border-left: 4px solid #3b82f6;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="text-primary" style="font-weight: 600;">{currency}</span>
                                <span style="font-weight: 700; color: #3b82f6;">{total:,.2f} ({percentage:.1f}%)</span>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

            with col2:
                # Payment State by Value (Bar Chart)
                st.markdown('<div class="section-header"><span class="section-icon">💵</span> Payment Value by Status</div>', unsafe_allow_html=True)
                if payment_totals:
                    fig_payment_value = px.bar(
                        x=list(payment_totals.keys()),
                        y=list(payment_totals.values()),
                        labels={"x": "Payment State", "y": "Total Value (€)"},
                        color=list(payment_totals.values()),
                        color_continuous_scale="RdYlGn",
                    )
                    fig_payment_value.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_payment_value, use_container_width=True)

                # Top 5 Invoices
                st.markdown('<div class="section-header"><span class="section-icon">🏆</span> Top 5 Largest Invoices</div>', unsafe_allow_html=True)
                sorted_docs = sorted(
                    docs, key=lambda x: x.get("totalGross", 0), reverse=True
                )[:5]

                for idx, doc in enumerate(sorted_docs, 1):
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
                            padding: 0.75rem;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                            border-left: 4px solid #10b981;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span class="text-primary" style="font-weight: 600;">#{idx} {doc.get('supplierName', 'N/A')[:30]}</span>
                                    <br><span class="text-secondary" style="font-size: 0.8rem;">Doc ID: {doc.get('documentId')}</span>
                                </div>
                                <span style="font-weight: 700; color: #10b981; font-size: 1.1rem;">€{doc.get('totalGross', 0):,.2f}</span>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # TAB 2: Workflow Analysis
        with tab2:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">⚙️</span>
                    Workflow Performance
                </h3>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                # Workflow Funnel
                st.markdown('<div class="section-header"><span class="section-icon">📊</span> Document Workflow Funnel</div>', unsafe_allow_html=True)

                funnel_data = {
                    "Stage": [
                        "Draft",
                        "Stage 1",
                        "Stage 2",
                        "Stage 3",
                        "Stage 4",
                        "Stage 5",
                        "Approved",
                    ],
                    "Count": [
                        stage_counts.get("Draft", 0),
                        stage_counts.get("Stage1", 0),
                        stage_counts.get("Stage2", 0),
                        stage_counts.get("Stage3", 0),
                        stage_counts.get("Stage4", 0),
                        stage_counts.get("Stage5", 0),
                        stage_counts.get("Approved", 0),
                    ],
                }

                fig_funnel = px.funnel(funnel_data, x="Count", y="Stage", color="Count")
                fig_funnel.update_traces(marker=dict(colorscale="Blues"))
                fig_funnel.update_layout(height=400)
                st.plotly_chart(fig_funnel, use_container_width=True)

            with col2:
                # Stage Distribution (Pie)
                st.markdown('<div class="section-header"><span class="section-icon">🎯</span> Current Stage Distribution</div>', unsafe_allow_html=True)

                if stage_counts:
                    fig_stages = px.pie(
                        values=list(stage_counts.values()),
                        names=list(stage_counts.keys()),
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Rainbow,
                    )
                    fig_stages.update_traces(
                        textposition="inside", textinfo="percent+label"
                    )
                    fig_stages.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig_stages, use_container_width=True)

            # Workflow Metrics
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header"><span class="section-icon">📈</span> Workflow Efficiency Metrics</div>', unsafe_allow_html=True)

            metric_cols = st.columns(4)

            bottleneck_stage = (
                max(stage_counts.items(), key=lambda x: x[1] if "Stage" in x[0] else 0)[
                    0
                ]
                if stage_counts
                else "N/A"
            )
            completion_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0
            in_progress_rate = (in_workflow / len(docs) * 100) if len(docs) > 0 else 0

            workflow_metrics = [
                ("Completion Rate", f"{completion_rate:.1f}%", "#22c55e", "rgba(34, 197, 94, 0.04)"),
                ("In Progress", f"{in_progress_rate:.1f}%", "#3b82f6", "rgba(59, 130, 246, 0.04)"),
                ("Bottleneck", bottleneck_stage, "#f59e0b", "rgba(245, 158, 11, 0.04)"),
                ("Avg Stages", f"{(in_workflow / 5):.1f}", "#8b5cf6", "rgba(139, 92, 246, 0.04)"),
            ]

            for idx, (label, value, color, bg) in enumerate(workflow_metrics):
                with metric_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="metric-card-light" style="
                            --card-color: {bg};
                            --card-color-dark: {color}30;
                            padding: 1.5rem 0.75rem;
                            border-radius: 20px;
                            text-align: center;
                            transition: all 0.3s ease;
                            cursor: default;
                            min-height: 180px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            position: relative;
                            overflow: hidden;
                        ">
                            <div style="
                                font-size: 2rem;
                                font-weight: 900;
                                color: {color};
                                margin-bottom: 0.5rem;
                                line-height: 1.1;
                                word-wrap: break-word;
                                overflow-wrap: break-word;
                                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                white-space: nowrap;
                                overflow: visible;
                            ">{value}</div>
                            <div class="metric-label" style="
                                font-size: 0.85rem;
                                font-weight: 700;
                                text-transform: uppercase;
                                letter-spacing: 0.5px;
                                line-height: 1.3;
                            ">{label}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # TAB 3: Supplier Analysis
        with tab3:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">🏪</span>
                    Supplier Intelligence
                </h3>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                # Top 10 Suppliers by Value
                st.markdown('<div class="section-header"><span class="section-icon">🏆</span> Top 10 Suppliers by Value</div>', unsafe_allow_html=True)

                supplier_values = {}
                supplier_counts = {}
                for doc in docs:
                    supplier = doc.get("supplierName", "Unknown")
                    value = doc.get("totalGross", 0)
                    supplier_values[supplier] = supplier_values.get(supplier, 0) + value
                    supplier_counts[supplier] = supplier_counts.get(supplier, 0) + 1

                top_suppliers = sorted(
                    supplier_values.items(), key=lambda x: x[1], reverse=True
                )[:10]

                if top_suppliers:
                    fig_suppliers = px.bar(
                        x=[s[1] for s in top_suppliers],
                        y=[s[0] for s in top_suppliers],
                        orientation="h",
                        labels={"x": "Total Value (€)", "y": "Supplier"},
                        color=[s[1] for s in top_suppliers],
                    )
                    fig_suppliers.update_traces(marker_color="teal")
                    fig_suppliers.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_suppliers, use_container_width=True)

            with col2:
                # Top 10 Suppliers by Document Count
                st.markdown('<div class="section-header"><span class="section-icon">📊</span> Top 10 Suppliers by Document Count</div>', unsafe_allow_html=True)

                top_suppliers_count = sorted(
                    supplier_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]

                if top_suppliers_count:
                    fig_supplier_count = px.bar(
                        x=[s[1] for s in top_suppliers_count],
                        y=[s[0] for s in top_suppliers_count],
                        orientation="h",
                        labels={"x": "Number of Documents", "y": "Supplier"},
                        color=[s[1] for s in top_suppliers_count],
                    )
                    fig_supplier_count.update_traces(marker_color="purple")
                    fig_supplier_count.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_supplier_count, use_container_width=True)

            # Supplier Statistics Table
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header"><span class="section-icon">📋</span> Supplier Statistics Summary</div>', unsafe_allow_html=True)

            supplier_summary = []
            for supplier in sorted(
                supplier_values.keys(), key=lambda x: supplier_values[x], reverse=True
            )[:15]:
                supplier_summary.append(
                    {
                        "Supplier": supplier,
                        "Total Value": f"€{supplier_values[supplier]:,.2f}",
                        "Documents": supplier_counts[supplier],
                        "Avg Invoice": f"€{(supplier_values[supplier] / supplier_counts[supplier]):,.2f}",
                    }
                )

            if supplier_summary:
                df_suppliers = pd.DataFrame(supplier_summary)
                st.dataframe(
                    df_suppliers, use_container_width=True, hide_index=True, height=400
                )

        # TAB 4: Timeline Analysis
        with tab4:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">📅</span>
                    Timeline & Trends
                </h3>
            """,
                unsafe_allow_html=True,
            )

            # Filter documents with valid dates
            docs_with_dates = [doc for doc in docs if doc.get("invoiceDate")]

            if docs_with_dates:
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Invoice Timeline Scatter
                    st.markdown('<div class="section-header"><span class="section-icon">📈</span> Invoice Value Timeline</div>', unsafe_allow_html=True)

                    timeline_data = []
                    for doc in docs_with_dates:
                        try:
                            timeline_data.append(
                                {
                                    "Date": pd.to_datetime(doc.get("invoiceDate")),
                                    "Value": doc.get("totalGross", 0),
                                    "Supplier": doc.get("supplierName", "Unknown")[:30],
                                    "Status": doc.get("currentStage", "Unknown"),
                                }
                            )
                        except:
                            pass

                    if timeline_data:
                        df_timeline = pd.DataFrame(timeline_data)
                        df_timeline = df_timeline.sort_values("Date")
                        df_timeline["AbsValue"] = df_timeline["Value"].abs()

                        fig_timeline = px.scatter(
                            df_timeline,
                            x="Date",
                            y="Value",
                            size="AbsValue",
                            color="Status",
                            hover_data=["Supplier", "Value"],
                            labels={
                                "Value": "Invoice Value (€)",
                                "Date": "Invoice Date",
                            },
                        )
                        fig_timeline.update_layout(height=400)
                        st.plotly_chart(fig_timeline, use_container_width=True)

                with col2:
                    # Monthly Summary
                    st.markdown('<div class="section-header"><span class="section-icon">📊</span> Monthly Summary</div>', unsafe_allow_html=True)

                    df_timeline["Month"] = (
                        df_timeline["Date"].dt.to_period("M").astype(str)
                    )
                    monthly_summary = (
                        df_timeline.groupby("Month")
                        .agg({"Value": ["sum", "count", "mean"]})
                        .round(2)
                    )

                    monthly_summary.columns = ["Total Value", "Count", "Avg Value"]
                    monthly_summary = monthly_summary.sort_index(ascending=False).head(
                        6
                    )

                    st.dataframe(monthly_summary, use_container_width=True, height=300)

                # Monthly Trend Line Chart
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header"><span class="section-icon">📈</span> Monthly Invoice Trends</div>', unsafe_allow_html=True)

                monthly_trend = (
                    df_timeline.groupby("Month").agg({"Value": "sum"}).reset_index()
                )
                monthly_trend.columns = ["Month", "Total Value"]

                fig_trend = px.line(
                    monthly_trend,
                    x="Month",
                    y="Total Value",
                    markers=True,
                    labels={"Total Value": "Total Invoice Value (€)", "Month": "Month"},
                )
                fig_trend.update_traces(line_color="#3b82f6", line_width=3)
                fig_trend.update_layout(height=300)
                st.plotly_chart(fig_trend, use_container_width=True)

            else:
                st.warning(
                    "⚠️ No documents with valid invoice dates found for timeline analysis"
                )

        # Export Section
        st.markdown("---")
        st.markdown("### 💾 Export Analytics Data")

        export_cols = st.columns(3)

        with export_cols[0]:
            # Export full dataset
            df_export = pd.DataFrame(
                [
                    {
                        "Document ID": doc.get("documentId"),
                        "Supplier": doc.get("supplierName"),
                        "Company": doc.get("companyName"),
                        "Invoice Date": doc.get("invoiceDate"),
                        "Total Gross": doc.get("totalGross"),
                        "Total Net": doc.get("totalNet"),
                        "Currency": doc.get("currencyCode"),
                        "Stage": doc.get("currentStage"),
                        "Payment State": doc.get("paymentState"),
                    }
                    for doc in docs
                ]
            )

            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Data (CSV)",
                data=csv_data,
                file_name=f"analytics_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with export_cols[1]:
            # Export supplier summary
            if supplier_summary:
                df_supplier_export = pd.DataFrame(supplier_summary)
                csv_supplier = df_supplier_export.to_csv(index=False)
                st.download_button(
                    label="📥 Download Supplier Report (CSV)",
                    data=csv_supplier,
                    file_name=f"supplier_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with export_cols[2]:
            # Export workflow summary
            workflow_export = pd.DataFrame(
                [
                    {
                        "Stage": stage,
                        "Count": count,
                        "Percentage": f"{(count/len(docs)*100):.1f}%",
                    }
                    for stage, count in sorted(
                        stage_counts.items(), key=lambda x: x[1], reverse=True
                    )
                ]
            )
            csv_workflow = workflow_export.to_csv(index=False)
            st.download_button(
                label="📥 Download Workflow Report (CSV)",
                data=csv_workflow,
                file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

# ============================================================================
# PAGE: SETTINGS
# ============================================================================
elif page == "⚙️ " + t("pages.settings"):
    # Apply slate header styles
    st.markdown(get_page_header_slate(), unsafe_allow_html=True)
    
    # Glossy page header card
    st.markdown(
        f"""
        <div class="page-header-slate" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(100, 116, 139, 0.9) 0%, rgba(71, 85, 105, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(100, 116, 139, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">⚙️</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('settings_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Configure API settings and authentication</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Apply card styles (for section headers), tab styles, and alert box styles
    st.markdown(get_card_styles(), unsafe_allow_html=True)
    st.markdown(get_tab_styles(), unsafe_allow_html=True)
    st.markdown(get_alert_box_styles(), unsafe_allow_html=True)

    # Feature disabled notice with glassmorphic styling
    st.markdown(
        """
        <div class="warning-box">
            <div class="warning-box-icon">⚠️</div>
            <div class="warning-box-text">Settings are currently disabled. API configuration is managed by administrators.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="section-header"><span class="section-icon">🔐</span> {t("settings_page.api_config")}</div>', unsafe_allow_html=True)

    current_key = st.session_state.client.api_key
    st.write("**Current API Key:**")
    # Mask the API key - show only first 8 and last 4 characters
    if current_key:
        masked_key = f"{current_key[:8]}{'•' * 16}{current_key[-4:]}"
        st.code(masked_key, language="text")
    else:
        st.code("Not set", language="text")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-icon">🔑</span> Change API Key</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Use Existing Key", "Generate New Key"])

    with tab1:
        new_api_key = st.text_input(
            "Enter API Key",
            value="",
            type="password",
            disabled=True,
            placeholder="API Key management is disabled",
        )
        if st.button(
            " Save API Key", type="primary", key="btn_save_api_key", disabled=True
        ):
            st.session_state.client.api_key = new_api_key
            st.session_state.client.session.headers.update(
                {"X-FLOWWER-ApiKey": new_api_key}
            )
            st.success("API Key updated!")
            st.rerun()

    with tab2:
        st.write("Generate a new API key using your credentials")
        username = st.text_input(
            "Username",
            value="",
            disabled=True,
            placeholder="Authentication is disabled",
        )
        password = st.text_input(
            "Password",
            type="password",
            value="",
            disabled=True,
            placeholder="Authentication is disabled",
        )

        if st.button(
            "🔐 Authenticate & Get New Key",
            type="primary",
            key="btn_authenticate",
            disabled=True,
        ):
            with st.spinner("Authenticating..."):
                if st.session_state.client.authenticate(username, password):
                    st.success("Authentication successful!")
                    st.write("**New API Key:**")
                    st.code(st.session_state.client.api_key, language="text")
                else:
                    st.error("Authentication failed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### API Information")
    st.write("**Base URL:**", st.session_state.client.base_url)
    st.write("**API Documentation:**", "https://enprom-gmbh.flowwer.de/swagger")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Session Info")
    st.write(
        "**Documents Loaded:**",
        len(st.session_state.documents) if st.session_state.documents else 0,
    )
    st.write(
        "**Selected Document:**",
        (
            st.session_state.selected_document.get("documentId")
            if st.session_state.selected_document
            else "None"
        ),
    )

# Professional footer
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
