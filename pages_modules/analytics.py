"""
Analytics Dashboard Page Module
Comprehensive analytics with KPIs, charts, and data insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
import json
from dateutil.relativedelta import relativedelta
from utils.cost_center_parser import parse_cost_center, enrich_cost_center_data
from utils.pagination import paginate_dataframe, get_page_size_selector
from components.analytics_components import (
    render_kpi_card,
    render_total_badge,
    render_tab_badge,
    get_quick_date_filters,
    calculate_kpi_trend,
)

try:
    from analytics.utils.data_processing import (
        calculate_kpis as calculate_kpis_optimized,
        filter_documents as filter_documents_optimized,
        classify_document,
    )
    from analytics.utils.caching import (
        get_cached_cost_centers,
        cache_cost_centers,
        get_cached_receipt_data,
        cache_receipt_data,
        get_cached_filtered_documents,
        cache_filtered_documents_manual,
    )
    PERFORMANCE_OPTIMIZATIONS_ENABLED = True
except ImportError:
    PERFORMANCE_OPTIMIZATIONS_ENABLED = False


def render_analytics_page(
    client,
    t,
    get_page_header_amber,
    get_action_bar_styles,
    get_card_styles,
    get_tab_styles,
    get_metric_styles,
    get_theme_text_styles,
    get_section_header_styles,
    to_excel,
    to_csv_semicolon=None,
):
    """Render the Analytics Dashboard page with comprehensive data visualization"""

    from styles.theme_styles import get_kpi_card_styles, get_glass_section_styles

    st.markdown(get_page_header_amber(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    if st.session_state.documents is not None:
        docs = st.session_state.documents
        
        st.markdown(
            f"""
            <div class="page-header-amber" style="
                padding: 2rem 2.5rem;
                border-radius: 24px;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, rgba(251, 146, 60, 0.08) 0%, rgba(249, 115, 22, 0.05) 100%);
                border: 1px solid rgba(251, 146, 60, 0.2);
                box-shadow: 0 4px 20px rgba(251, 146, 60, 0.1);
            ">
                <div style="display: flex; align-items: center; gap: 1.5rem;">
                    <div style="
                        background: linear-gradient(135deg, rgba(251, 146, 60, 0.9) 0%, rgba(249, 115, 22, 0.9) 100%);
                        width: 64px;
                        height: 64px;
                        border-radius: 16px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 32px;
                        box-shadow: 0 8px 24px rgba(251, 146, 60, 0.4),
                                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    ">📈</div>
                    <div>
                        <h2 style="
                            margin: 0;
                            font-size: 2rem;
                            font-weight: 800;
                            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                        ">{t('analytics_page.title')}</h2>
                        <p style="
                            margin: 0.5rem 0 0 0;
                            font-size: 1rem;
                            font-weight: 500;
                            color: #64748b;
                        ">{t('analytics_page.interactive_visualization')}</p>
                    </div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    else:
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
                ">📈</div>
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
                    ">{t('analytics_page.interactive_visualization')}</p>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        get_card_styles()
        + get_tab_styles()
        + get_metric_styles()
        + get_theme_text_styles()
        + get_section_header_styles()
        + get_kpi_card_styles()
        + get_glass_section_styles()
        + get_action_bar_styles(),
        unsafe_allow_html=True,
    )

    from styles.theme_styles import get_alert_box_styles

    st.markdown(get_alert_box_styles(), unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        /* Bottom-align all controls in the top row */
        div[data-testid="column"]:nth-of-type(1),
        div[data-testid="column"]:nth-of-type(2),
        div[data-testid="column"]:nth-of-type(3),
        div[data-testid="column"]:nth-of-type(4),
        div[data-testid="column"]:nth-of-type(5) {
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-end !important;
            align-items: flex-start !important;
        }
        
        /* Load Data / Clear Filters — match KPI indicator “glassy pill” style
           Streamlit cannot wrap widgets with HTML from st.markdown, so we target the actual top control row
           by selecting the horizontal block that contains BOTH a primary and secondary button. */
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) .stButton > button{
            border-radius: 999px !important;
            font-size: 0.8rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.01em !important;
            padding: 0.52rem 1.0rem 0.52rem 2.1rem !important; /* left space for dot */
            position: relative !important;
            backdrop-filter: blur(10px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(10px) saturate(160%) !important;
            transition: all 0.2s ease !important;
            transform: translateY(0px);
        }

        /* Replace global glossy overlay with a dot */
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) .stButton > button::before{
            content: "" !important;
            position: absolute !important;
            left: 0.85rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            width: 8px !important;
            height: 8px !important;
            border-radius: 999px !important;
            opacity: 1 !important;
            transition: none !important;
            background: transparent !important;
        }

        /* Load Data (primary) */
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="primary"],
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-primary"]{
            background: rgba(59, 130, 246, 0.12) !important;
            color: #1d4ed8 !important;
            border: 1px solid rgba(59, 130, 246, 0.26) !important;
            box-shadow: 0 8px 22px rgba(59, 130, 246, 0.14) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="primary"]::before,
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-primary"]::before{
            background: rgba(59, 130, 246, 0.95) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.20) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="primary"]:hover,
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-primary"]:hover{
            background: rgba(59, 130, 246, 0.16) !important;
            border-color: rgba(59, 130, 246, 0.34) !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 30px rgba(59, 130, 246, 0.18) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="primary"]:active,
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-primary"]:active{
            transform: translateY(0px);
            box-shadow: 0 8px 22px rgba(59, 130, 246, 0.14) !important;
        }

        /* Clear Filters (secondary) */
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="secondary"],
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-secondary"]{
            background: rgba(239, 68, 68, 0.10) !important;
            color: #b91c1c !important;
            border: 1px solid rgba(239, 68, 68, 0.22) !important;
            box-shadow: 0 8px 22px rgba(239, 68, 68, 0.10) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="secondary"]::before,
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-secondary"]::before{
            background: rgba(239, 68, 68, 0.92) !important;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.16) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="secondary"]:hover,
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-secondary"]:hover{
            background: rgba(239, 68, 68, 0.14) !important;
            border-color: rgba(239, 68, 68, 0.30) !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 30px rgba(239, 68, 68, 0.14) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="secondary"]:active,
        div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-secondary"]:active{
            transform: translateY(0px);
            box-shadow: 0 8px 22px rgba(239, 68, 68, 0.10) !important;
        }

        /* KPI header filter indicator (small, consistent, no "remove" UX) */
        .kpi-filter-indicator{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.34rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            border: 1px solid rgba(59, 130, 246, 0.25);
            backdrop-filter: blur(10px) saturate(160%);
            -webkit-backdrop-filter: blur(10px) saturate(160%);
            box-shadow: 0 6px 18px rgba(59, 130, 246, 0.14);
        }
        .kpi-filter-indicator .dot{
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.95);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.20);
        }
        @media (prefers-color-scheme: light){
            .kpi-filter-indicator{
                background: rgba(59, 130, 246, 0.10);
                color: #1d4ed8;
            }
        }
        @media (prefers-color-scheme: dark){
            .kpi-filter-indicator{
                background: rgba(59, 130, 246, 0.18);
                border-color: rgba(59, 130, 246, 0.32);
                color: rgba(224, 242, 254, 0.95);
                box-shadow: 0 10px 26px rgba(0, 0, 0, 0.28), 0 8px 22px rgba(59, 130, 246, 0.16);
            }
        }
        
        @media (prefers-color-scheme: dark) {
            div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="primary"],
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-primary"]{
                background: rgba(59, 130, 246, 0.18) !important;
                color: rgba(224, 242, 254, 0.95) !important;
                border-color: rgba(59, 130, 246, 0.32) !important;
                box-shadow: 0 10px 26px rgba(0,0,0,0.28), 0 8px 22px rgba(59, 130, 246, 0.16) !important;
            }
            div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="primary"]:hover,
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-primary"]:hover{
                background: rgba(59, 130, 246, 0.24) !important;
                border-color: rgba(59, 130, 246, 0.42) !important;
            }

            div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="secondary"],
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-secondary"]{
                background: rgba(239, 68, 68, 0.16) !important;
                color: rgba(254, 202, 202, 0.95) !important;
                border-color: rgba(239, 68, 68, 0.30) !important;
                box-shadow: 0 10px 26px rgba(0,0,0,0.28), 0 8px 22px rgba(239, 68, 68, 0.12) !important;
            }
            div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]):has(button[kind="secondary"]) button[kind="secondary"]:hover,
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]):has(button[data-testid="baseButton-secondary"]) button[data-testid="baseButton-secondary"]:hover{
                background: rgba(239, 68, 68, 0.22) !important;
                border-color: rgba(239, 68, 68, 0.40) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.2, 1.2, 1.2])

    with col1:
        include_processed_analytics = st.checkbox(
            t("analytics_page.include_processed"),
            value=False,
            key="analytics_processed",
        )

    with col2:
        include_deleted_analytics = st.checkbox(
            t("analytics_page.include_deleted"), value=False, key="analytics_deleted"
        )

    with col3:
        cc_months_back = st.selectbox(
            t("analytics_page.cost_center_lookback_months"),
            options=[3, 6, 12, 24],
            index=1,  
            help=t("analytics_page.cost_center_lookback_help"),
            key="analytics_cc_months_back",
        )

    with col4:
        if st.button(
            t("analytics_page.load_data"),
            type="primary",
            use_container_width=True,
            key="btn_load_analytics_docs",
        ):
            docs = None
            cost_centers = None
            
            try:
                with st.spinner(f"📄 {t('analytics_page.loading_documents')}"):
                    docs = client.get_all_documents(
                        include_processed=include_processed_analytics,
                        include_deleted=include_deleted_analytics,
                    )
                    st.session_state.documents = docs
                    st.session_state.analytics_load_time = datetime.now()
            except Exception as e:
                st.error(f"{t('analytics_page.error_loading_documents')}: {str(e)}")
                st.stop()
            
            if not client.api_key:
                st.error(f"❌ {t('analytics_page.api_key_not_set')}")
                st.stop()
            
            try:
                with st.spinner(f"🏢 {t('analytics_page.loading_cost_centers_months').format(months=cc_months_back)}"):
                    cost_centers = client.get_all_cost_centers(months_back=int(cc_months_back))
            except Exception as e:
                st.warning(f"{t('analytics_page.warning_could_not_load_cost_centers')}: {str(e)}")
                cost_centers = []
            
            if cost_centers:
                cleaned_cc = [
                    str(cc)
                    for cc in cost_centers
                    if cc and str(cc).strip() not in ["", "None", "nan"]
                ]
                st.session_state.analytics_cost_centers = sorted(cleaned_cc)
                
                today = date.today()
                start_date = (today - relativedelta(months=cc_months_back - 1)).replace(day=1)
                end_date = today
                
                st.session_state.analytics_cc_sync_start = start_date
                st.session_state.analytics_cc_sync_end = end_date
                st.session_state.analytics_cc_sync_months = cc_months_back
                
                st.toast(
                    f"✅ {t('analytics_page.loaded_documents_cost_centers').format(docs=len(docs), cc=len(cleaned_cc))}",
                    icon="✅",
                )
            else:
                st.toast(
                    f"✅ {t('analytics_page.loaded_documents_no_cost_centers').format(docs=len(docs))}",
                    icon="✅",
                )
            
            st.rerun()

    with col5:
        if st.button(
            "🗑️ Clear Filters",
            type="secondary",
            use_container_width=True,
            key="btn_clear_filters",
        ):
            keys_to_clear = [
                "analytics_company_filter",
                "analytics_stage_filter",
                "analytics_payment_filter",
                "analytics_supplier_filter",
                "analytics_currency_filter",
                "analytics_flow_filter",
                "analytics_from_month",
                "analytics_from_year",
                "analytics_to_month",
                "analytics_to_year",
                "analytics_value_threshold",
                "analytics_cc_search",
                "analytics_cc_multiselect",
                "quick_filter_selected",
                "quick_filter_start",
                "quick_filter_end",
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.divider()

    if st.session_state.documents is None:
        st.info(f"📊 {t('analytics_page.click_load_data')}")
    else:
        docs = st.session_state.documents

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

        with st.expander(t("analytics_page.advanced_filters"), expanded=False):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="font-weight: 600; color: #64748b; font-size: 0.875rem;">📅 Quick Filters:</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <style>
                /* Beautiful chip-style quick filter buttons */
                div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
                    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
                    border: 1px solid #e2e8f0 !important;
                    border-radius: 20px !important;
                    padding: 0.4rem 1rem !important;
                    font-size: 0.8rem !important;
                    font-weight: 500 !important;
                    color: #475569 !important;
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
                    letter-spacing: 0.01em !important;
                }
                
                div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
                    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
                    color: #2563eb !important;
                    border-color: #3b82f6 !important;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
                    transform: translateY(-2px);
                }
                
                div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] button[kind="secondary"]:active {
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
                    color: #1d4ed8 !important;
                    border-color: #2563eb !important;
                    transform: translateY(0px);
                    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
                }
                
                /* Polished form labels */
                div[data-testid="stExpander"] label[data-testid="stWidgetLabel"] {
                    font-size: 0.8rem !important;
                    font-weight: 600 !important;
                    color: #475569 !important;
                    margin-bottom: 0.35rem !important;
                    letter-spacing: 0.01em !important;
                }
                
                /* Modern selectbox styling */
                div[data-testid="stExpander"] div[data-baseweb="select"] > div {
                    background: #ffffff !important;
                    border: 1px solid #e2e8f0 !important;
                    border-radius: 8px !important;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
                    transition: all 0.2s ease !important;
                    font-size: 0.875rem !important;
                }
                
                div[data-testid="stExpander"] div[data-baseweb="select"] > div:hover {
                    border-color: #cbd5e1 !important;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
                }
                
                div[data-testid="stExpander"] div[data-baseweb="select"] > div:focus-within {
                    border-color: #3b82f6 !important;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
                }
                
                /* Modern text input styling */
                div[data-testid="stExpander"] input[type="text"],
                div[data-testid="stExpander"] input[type="number"] {
                    background: #ffffff !important;
                    border: 1px solid #e2e8f0 !important;
                    border-radius: 8px !important;
                    padding: 0.5rem 0.75rem !important;
                    font-size: 0.875rem !important;
                    transition: all 0.2s ease !important;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
                }
                
                div[data-testid="stExpander"] input[type="text"]:hover,
                div[data-testid="stExpander"] input[type="number"]:hover {
                    border-color: #cbd5e1 !important;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
                }
                
                div[data-testid="stExpander"] input[type="text"]:focus,
                div[data-testid="stExpander"] input[type="number"]:focus {
                    border-color: #3b82f6 !important;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
                    outline: none !important;
                }
                
                /* Modern multiselect styling */
                div[data-testid="stExpander"] div[data-baseweb="select"] input {
                    font-size: 0.875rem !important;
                }
                
                /* Help text styling */
                div[data-testid="stExpander"] .stTooltipIcon {
                    color: #94a3b8 !important;
                }
                
                /* Caption text */
                div[data-testid="stExpander"] .stCaptionContainer {
                    color: #64748b !important;
                    font-size: 0.75rem !important;
                }
                
                @media (prefers-color-scheme: dark) {
                    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
                        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%) !important;
                        border-color: rgba(71, 85, 105, 0.6) !important;
                        color: #cbd5e1 !important;
                        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
                    }
                    
                    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
                        background: linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(29, 78, 216, 0.3) 100%) !important;
                        color: #93c5fd !important;
                        border-color: #60a5fa !important;
                        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25) !important;
                    }
                    
                    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] button[kind="secondary"]:active {
                        background: linear-gradient(135deg, rgba(29, 78, 216, 0.5) 0%, rgba(37, 99, 235, 0.4) 100%) !important;
                        color: #93c5fd !important;
                    }
                    
                    div[data-testid="stExpander"] label[data-testid="stWidgetLabel"] {
                        color: #cbd5e1 !important;
                    }
                    
                    div[data-testid="stExpander"] div[data-baseweb="select"] > div {
                        background: rgba(30, 41, 59, 0.6) !important;
                        border-color: rgba(71, 85, 105, 0.6) !important;
                    }
                    
                    div[data-testid="stExpander"] div[data-baseweb="select"] > div:hover {
                        border-color: rgba(100, 116, 139, 0.8) !important;
                    }
                    
                    div[data-testid="stExpander"] input[type="text"],
                    div[data-testid="stExpander"] input[type="number"] {
                        background: rgba(30, 41, 59, 0.6) !important;
                        border-color: rgba(71, 85, 105, 0.6) !important;
                        color: #e2e8f0 !important;
                    }
                    
                    div[data-testid="stExpander"] input[type="text"]:hover,
                    div[data-testid="stExpander"] input[type="number"]:hover {
                        border-color: rgba(100, 116, 139, 0.8) !important;
                    }
                }
                </style>
            """,
                unsafe_allow_html=True,
            )

            quick_filters = get_quick_date_filters()

            qf_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
            for idx, (filter_name, (start_date, end_date)) in enumerate(
                quick_filters.items()
            ):
                with qf_cols[idx]:
                    if st.button(
                        filter_name,
                        key=f"quick_filter_{filter_name.replace(' ', '_')}",
                        use_container_width=True,
                        type="secondary",
                    ):
                        st.session_state.quick_filter_selected = filter_name
                        st.session_state.quick_filter_start = start_date
                        st.session_state.quick_filter_end = end_date
                        st.rerun()

            st.markdown(
                "<div style='margin: 1.5rem 0 1rem 0; border-top: 1px solid #e2e8f0;'></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="font-weight: 600; color: #64748b; font-size: 0.875rem;">🔍 Detailed Filters</span>
                </div>
            """,
                unsafe_allow_html=True,
            )

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
                    t("analytics_page.company"),
                    [t("analytics_page.all")] + sorted(companies),
                    help=t("analytics_page.filter_by_company_help"),
                    key="analytics_company_filter",
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
                    t("analytics_page.stage"),
                    [t("analytics_page.all")] + sorted(stages),
                    help=t("analytics_page.filter_by_stage_help"),
                    key="analytics_stage_filter",
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
                    t("analytics_page.payment_state"),
                    [t("analytics_page.all")] + sorted(payment_states),
                    help=t("analytics_page.filter_by_payment_help"),
                    key="analytics_payment_filter",
                )

            st.markdown("<br>", unsafe_allow_html=True)

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
                    t("analytics_page.supplier"),
                    [t("analytics_page.all")] + sorted(suppliers),
                    help=t("analytics_page.filter_by_supplier_help"),
                    key="analytics_supplier_filter",
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
                    t("analytics_page.currency"),
                    [t("analytics_page.all")] + sorted(currencies),
                    help=t("analytics_page.filter_by_currency_help"),
                    key="analytics_currency_filter",
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
                    t("analytics_page.flow"),
                    [t("analytics_page.all")] + sorted(flows),
                    help=t("analytics_page.filter_by_flow_help"),
                    key="analytics_flow_filter",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            col7, col8, col9, col10 = st.columns(4)

            if (
                "quick_filter_start" in st.session_state
                and "quick_filter_end" in st.session_state
            ):
                quick_start = st.session_state.quick_filter_start
                quick_end = st.session_state.quick_filter_end
                from_month_default = quick_start.month - 1
                from_year_default = list(range(2020, datetime.now().year + 1)).index(
                    quick_start.year
                )
                to_month_default = quick_end.month - 1
                to_year_default = list(range(2020, datetime.now().year + 1)).index(
                    quick_end.year
                )
            elif (
                "analytics_cc_sync_start" in st.session_state
                and "analytics_cc_sync_end" in st.session_state
            ):
                sync_start = st.session_state.analytics_cc_sync_start
                sync_end = st.session_state.analytics_cc_sync_end
                from_month_default = sync_start.month - 1
                from_year_default = list(range(2020, datetime.now().year + 1)).index(
                    sync_start.year
                )
                to_month_default = sync_end.month - 1
                to_year_default = list(range(2020, datetime.now().year + 1)).index(
                    sync_end.year
                )
            else:
                from_month_default = 0
                from_year_default = 3
                to_month_default = datetime.now().month - 1
                to_year_default = len(list(range(2020, datetime.now().year + 1))) - 1

            with col7:
                from_month = st.selectbox(
                    t("analytics_page.from_month"),
                    options=list(range(1, 13)),
                    format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                    index=from_month_default,
                    key="analytics_from_month",
                )

            with col8:
                from_year = st.selectbox(
                    t("analytics_page.from_year"),
                    options=list(range(2020, datetime.now().year + 1)),
                    index=from_year_default,
                    key="analytics_from_year",
                )

            with col9:
                to_month = st.selectbox(
                    t("analytics_page.to_month"),
                    options=list(range(1, 13)),
                    format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                    index=to_month_default,
                    key="analytics_to_month",
                )

            with col10:
                to_year = st.selectbox(
                    t("analytics_page.to_year"),
                    options=list(range(2020, datetime.now().year + 1)),
                    index=to_year_default,
                    key="analytics_to_year",
                )

            min_date = date(from_year, from_month, 1)
            last_day = calendar.monthrange(to_year, to_month)[1]
            max_date = date(to_year, to_month, last_day)
            date_from = min_date
            date_to = max_date

            if "quick_filter_selected" in st.session_state:
                st.info(
                    f"📅 Active Quick Filter: **{st.session_state.quick_filter_selected}**"
                )

            value_threshold = 0.0

           
            selected_cost_centers = []

        if PERFORMANCE_OPTIMIZATIONS_ENABLED:
         
            filter_params = {
                "company": selected_company if selected_company != t("analytics_page.all") else None,
                "stage": selected_stage if selected_stage != t("analytics_page.all") else None,
                "payment": selected_payment if selected_payment != t("analytics_page.all") else None,
                "supplier": selected_supplier if selected_supplier != t("analytics_page.all") else None,
                "currency": selected_currency if selected_currency != t("analytics_page.all") else None,
                "flow": selected_flow if selected_flow != t("analytics_page.all") else None,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "min_value": value_threshold if value_threshold > 0 else None,
            }
            
            cached_filtered = get_cached_filtered_documents(filter_params)
            if cached_filtered is not None:
                filtered_docs = cached_filtered if cached_filtered else []
            else:
                filtered_docs = filter_documents_optimized(
                    st.session_state.documents,
                    **{k: v for k, v in filter_params.items() if v is not None}
                )
                if filtered_docs is None:
                    filtered_docs = []
                cache_filtered_documents_manual(filtered_docs, filter_params)
        else:
            filtered_docs = st.session_state.documents

            if selected_company != t("analytics_page.all"):
                filtered_docs = [
                    doc
                    for doc in filtered_docs
                    if doc.get("companyName") == selected_company
                ]

            if selected_stage != t("analytics_page.all"):
                filtered_docs = [
                    doc
                    for doc in filtered_docs
                    if doc.get("currentStage") == selected_stage
                ]

            if selected_payment != t("analytics_page.all"):
                filtered_docs = [
                    doc
                    for doc in filtered_docs
                    if doc.get("paymentState") == selected_payment
                ]

            if selected_supplier != t("analytics_page.all"):
                filtered_docs = [
                    doc
                    for doc in filtered_docs
                    if doc.get("supplierName") == selected_supplier
                ]

            if selected_currency != t("analytics_page.all"):
                filtered_docs = [
                    doc
                    for doc in filtered_docs
                    if doc.get("currencyCode") == selected_currency
                ]

            if selected_flow != t("analytics_page.all"):
                filtered_docs = [
                    doc for doc in filtered_docs if doc.get("flowName") == selected_flow
                ]

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

        if value_threshold > 0:
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("totalGross", 0) >= value_threshold
            ]

        docs = filtered_docs

      
        st.markdown("<br>", unsafe_allow_html=True)

        total_docs = len(st.session_state.documents) if st.session_state.documents else len(docs)
        is_filtered = total_docs > 0 and len(docs) < total_docs
        filter_indicator_html = (
            f'<span class="kpi-filter-indicator"><span class="dot"></span>Filtered {len(docs):,}/{total_docs:,}</span>'
            if is_filtered
            else ""
        )
        
        kpi_title = t('analytics_page.key_performance_indicators')
        header_html = (
            '<div style="margin-bottom: 1.5rem;">'
            '<div class="section-header">'
            '<div style="'
            'background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);'
            'width: 48px;'
            'height: 48px;'
            'border-radius: 12px;'
            'display: flex;'
            'align-items: center;'
            'justify-content: center;'
            'font-size: 24px;'
            'box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);'
            'flex-shrink: 0;'
            '">📊</div>'
            '<div style="flex: 1;">'
            '<div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">'
            f'<h3 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{kpi_title}</h3>'
            f'{filter_indicator_html}'
            '</div>'
            f'<p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{t("analytics_page.real_time_insights_metrics")}</p>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

        if PERFORMANCE_OPTIMIZATIONS_ENABLED:
            kpi_data = calculate_kpis_optimized(docs)
            total_gross = kpi_data["total_gross"]
            total_net = kpi_data["total_net"]
            total_tax = kpi_data["total_tax"]
            avg_invoice_value = kpi_data["avg_invoice_value"]
            approved_count = kpi_data["approved_count"]
            in_workflow = kpi_data["in_workflow"]
            draft_count = kpi_data["draft_count"]
            approval_rate = kpi_data["approval_rate"]
            pending_payment_value = kpi_data["pending_payment_value"]
            stage_counts = kpi_data.get("stage_counts", {})
            payment_totals = kpi_data.get("payment_totals", {})
            
            payment_counts = {}
            for doc in docs:
                payment = doc.get("paymentState", "Unknown")
                payment_counts[payment] = payment_counts.get(payment, 0) + 1
        else:
            total_gross = sum([abs(doc.get("totalGross", 0)) for doc in docs])
            total_net = sum([abs(doc.get("totalNet", 0)) for doc in docs])
            total_tax = total_gross - total_net
            avg_invoice_value = total_gross / len(docs) if len(docs) > 0 else 0

            stage_counts = {}
            for doc in docs:
                stage = doc.get("currentStage", "Unknown")
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

            approved_count = stage_counts.get("Approved", 0)
            in_workflow = sum(stage_counts.get(f"Stage{i}", 0) for i in range(1, 6))
            draft_count = stage_counts.get("Draft", 0)
            approval_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0

            payment_counts = {}
            payment_totals = {}
            for doc in docs:
                payment = doc.get("paymentState", "Unknown")
                payment_counts[payment] = payment_counts.get(payment, 0) + 1
                payment_totals[payment] = payment_totals.get(payment, 0) + abs(doc.get(
                    "totalGross", 0
                ))

            pending_payment_value = payment_totals.get("Open", 0) + payment_totals.get(
                "Pending", 0
            )

        unique_companies = len(
            set([doc.get("companyName") for doc in docs if doc.get("companyName")])
        )
        unique_suppliers = len(
            set([doc.get("supplierName") for doc in docs if doc.get("supplierName")])
        )


        kpis = [
            (
                (
                    t("analytics_page.total_documents")
                    if hasattr(t, "__call__")
                    else "Total Documents"
                ),
                len(docs),
                "📊",
                "#3b82f6",
                "rgba(59, 130, 246, 0.04)",
            ),
            (
                (
                    t("analytics_page.total_value")
                    if hasattr(t, "__call__")
                    else "Total Value"
                ),
                f"€{total_gross:,.0f}",
                "💰",
                "#10b981",
                "rgba(16, 185, 129, 0.04)",
            ),
            (
                (
                    t("analytics_page.avg_invoice")
                    if hasattr(t, "__call__")
                    else "Avg Invoice"
                ),
                f"€{avg_invoice_value:,.0f}",
                "📈",
                "#8b5cf6",
                "rgba(139, 92, 246, 0.04)",
            ),
            (
                (
                    t("analytics_page.approval_rate")
                    if hasattr(t, "__call__")
                    else "Approval Rate"
                ),
                f"{approval_rate:.1f}%",
                "✅",
                "#22c55e",
                "rgba(34, 197, 94, 0.04)",
            ),
            (
                (
                    t("analytics_page.pending_payments")
                    if hasattr(t, "__call__")
                    else "Pending Payments"
                ),
                f"€{pending_payment_value:,.0f}",
                "⏳",
                "#f59e0b",
                "rgba(245, 158, 11, 0.04)",
            ),
            (
                (
                    t("analytics_page.total_tax")
                    if hasattr(t, "__call__")
                    else "Total Tax"
                ),
                f"€{total_tax:,.0f}",
                "💳",
                "#ef4444",
                "rgba(239, 68, 68, 0.04)",
            ),
        ]

        # KPI cards now use theme styles from get_kpi_card_styles()
        # Additional custom styling for icon wrapper
        st.markdown("""
            <style>
                /* Enhanced KPI card layout with icon - extends theme's kpi-card-enhanced */
                .kpi-card-enhanced {
                    text-align: center;
                    min-height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    position: relative;
                }
                .kpi-icon-wrapper {
                    width: 56px;
                    height: 56px;
                    border-radius: 14px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 28px;
                    margin: 0 auto 1rem;
                    background: var(--kpi-bg, rgba(59, 130, 246, 0.1));
                    box-shadow: 0 4px 12px var(--kpi-shadow, rgba(0, 0, 0, 0.1));
                }
                @media (prefers-color-scheme: dark) {
                    .kpi-icon-wrapper {
                        background: var(--kpi-bg-dark, rgba(59, 130, 246, 0.2));
                    }
                }
            </style>
        """, unsafe_allow_html=True)
        
        for row in range(0, len(kpis), 3):
            kpi_cols = st.columns(3)
            for col_idx, kpi_idx in enumerate(range(row, min(row + 3, len(kpis)))):
                label, value, icon, color, bg = kpis[kpi_idx]
                color_rgb = color.replace('#', '')
                r, g, b = int(color_rgb[0:2], 16), int(color_rgb[2:4], 16), int(color_rgb[4:6], 16)
                shadow_color = f"rgba({r}, {g}, {b}, 0.2)"
                
                with kpi_cols[col_idx]:
                    st.markdown(
                        f"""
                        <div class="kpi-card-enhanced" style="
                            --card-accent: {color};
                            --card-accent-end: {color}dd;
                            --value-color: {color};
                            --kpi-bg: {bg};
                            --kpi-shadow: {shadow_color};
                        ">
                            <div class="kpi-icon-wrapper">{icon}</div>
                            <div class="kpi-value-main" style="--value-color: {color};">{value}</div>
                            <p class="kpi-label-main">{label}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            if row + 3 < len(kpis):
                st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        insights = []
        if approval_rate < 50:
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "title": t("analytics_page.low_approval_rate"),
                "message": t("analytics_page.low_approval_rate_message").format(rate=f"{approval_rate:.1f}"),
                "color": "#f59e0b"
            })
        if pending_payment_value > total_gross * 0.3:
            insights.append({
                "type": "alert",
                "icon": "💳",
                "title": t("analytics_page.high_pending_payments"),
                "message": t("analytics_page.high_pending_payments_message").format(amount=f"{pending_payment_value:,.0f}", percent=f"{pending_payment_value/total_gross*100:.1f}"),
                "color": "#ef4444"
            })
        if in_workflow > len(docs) * 0.4:
            insights.append({
                "type": "info",
                "icon": "📋",
                "title": t("analytics_page.workflow_bottleneck"),
                "message": t("analytics_page.workflow_bottleneck_message").format(count=in_workflow, percent=f"{in_workflow/len(docs)*100:.1f}"),
                "color": "#3b82f6"
            })
        if avg_invoice_value > 10000:
            insights.append({
                "type": "success",
                "icon": "💰",
                "title": t("analytics_page.high_value_portfolio"),
                "message": t("analytics_page.high_value_portfolio_message").format(amount=f"{avg_invoice_value:,.0f}"),
                "color": "#10b981"
            })
        if draft_count > len(docs) * 0.2:
            insights.append({
                "type": "warning",
                "icon": "📝",
                "title": t("analytics_page.unprocessed_documents"),
                "message": t("analytics_page.unprocessed_documents_message").format(count=draft_count, percent=f"{draft_count/len(docs)*100:.1f}"),
                "color": "#f59e0b"
            })
        
        if insights:
            st.markdown(
                f"""
                <div style="margin: 2rem 0 1.5rem 0;">
                    <div class="section-header">
                        <div style="
                            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                            width: 48px;
                            height: 48px;
                            border-radius: 12px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 24px;
                            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
                            flex-shrink: 0;
                        ">💡</div>
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{t('analytics_page.key_insights_recommendations')}</h3>
                            <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{t('analytics_page.actionable_insights_data')}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            insight_cols = st.columns(min(len(insights), 3))
            for idx, insight in enumerate(insights[:3]):
                with insight_cols[idx]:
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, {insight['color']}15 0%, {insight['color']}08 100%);
                            border-left: 4px solid {insight['color']};
                            border-radius: 12px;
                            padding: 1.25rem;
                            margin-bottom: 1rem;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
                            transition: all 0.3s ease;
                        ">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                                <span style="font-size: 1.5rem;">{insight['icon']}</span>
                                <h4 style="
                                    margin: 0;
                                    font-size: 1rem;
                                    font-weight: 700;
                                    color: {insight['color']};
                                ">{insight['title']}</h4>
                            </div>
                            <p style="
                                margin: 0;
                                font-size: 0.875rem;
                                color: #475569;
                                line-height: 1.5;
                            ">{insight['message']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            
            if len(insights) > 3:
                with st.expander(t("analytics_page.view_more_insights").format(count=len(insights) - 3), expanded=False):
                    for insight in insights[3:]:
                        st.markdown(
                            f"""
                            <div style="
                                background: linear-gradient(135deg, {insight['color']}15 0%, {insight['color']}08 100%);
                                border-left: 4px solid {insight['color']};
                                border-radius: 12px;
                                padding: 1rem;
                                margin-bottom: 0.75rem;
                            ">
                                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                                    <span style="font-size: 1.25rem;">{insight['icon']}</span>
                                    <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: {insight['color']};">{insight['title']}</h4>
                                </div>
                                <p style="margin: 0; font-size: 0.85rem; color: #475569;">{insight['message']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        if in_workflow > 0 or draft_count > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            alert_col1, alert_col2 = st.columns(2)

            if in_workflow > 0:
                with alert_col1:
                    st.markdown(
                        f"""
                        <div class="alert-box-orange" style="
                            padding: 1.5rem;
                            border-radius: 16px;
                        ">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                                <h4 style="margin: 0; font-size: 1.25rem; font-weight: 700;">
                                    📋 {t('analytics_page.in_processing_workflow')}
                                </h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                                <strong>{in_workflow}</strong> {t('analytics_page.documents_in_approval_stages')}
                            </p>
                            <p class="subtitle" style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                {t('analytics_page.currently_moving_through')}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if draft_count > 0:
                with alert_col2:
                    st.markdown(
                        f"""
                        <div class="alert-box-purple" style="
                            padding: 1.5rem;
                            border-radius: 16px;
                        ">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                                <h4 style="margin: 0; font-size: 1.25rem; font-weight: 700;">
                                    📝 {t('analytics_page.unstarted_documents')}
                                </h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                                <strong>{draft_count}</strong> {t('analytics_page.documents_not_started')}
                            </p>
                            <p class="subtitle" style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                {t('analytics_page.require_initial_processing')}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown(
            f"""
            <div style="margin: 2.5rem 0 1.5rem 0;">
                <div class="section-header">
                    <div style="
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        width: 48px;
                        height: 48px;
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                        flex-shrink: 0;
                    ">💰</div>
                    <div style="flex: 1;">
                        <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{t('analytics_page.financial_summary')}</h3>
                        <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{t('analytics_page.comprehensive_financial_overview')}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        fin_cols = st.columns(3)

        with fin_cols[0]:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(16, 185, 129, 0.04) 100%);
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    padding: 2rem 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    min-height: 160px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(16, 185, 129, 0.2)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(16, 185, 129, 0.1)'">
                    <div style="
                        font-size: 2.5rem;
                        font-weight: 900;
                        color: #10b981;
                        margin-bottom: 0.75rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    ">€{total_net:,.0f}</div>
                    <div style="
                        font-size: 0.875rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        color: #64748b;
                        margin-bottom: 0.5rem;
                    ">{t('analytics_page.total_net_amount')}</div>
                    <div style="
                        font-size: 0.75rem;
                        color: #94a3b8;
                        font-weight: 500;
                    ">{t('analytics_page.excluding_taxes')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with fin_cols[1]:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.04) 100%);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    padding: 2rem 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    min-height: 160px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(239, 68, 68, 0.2)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(239, 68, 68, 0.1)'">
                    <div style="
                        font-size: 2.5rem;
                        font-weight: 900;
                        color: #ef4444;
                        margin-bottom: 0.75rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    ">€{total_tax:,.0f}</div>
                    <div style="
                        font-size: 0.875rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        color: #64748b;
                        margin-bottom: 0.5rem;
                    ">{t('analytics_page.total_tax_amount')}</div>
                    <div style="
                        font-size: 0.75rem;
                        color: #94a3b8;
                        font-weight: 500;
                    ">{t('analytics_page.vat_other_taxes')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with fin_cols[2]:
            paid_value = payment_totals.get("Paid", 0)
            payment_rate = (paid_value / total_gross * 100) if total_gross > 0 else 0
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.04) 100%);
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    padding: 2rem 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    min-height: 160px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(59, 130, 246, 0.2)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.1)'">
                    <div style="
                        font-size: 2.5rem;
                        font-weight: 900;
                        color: #3b82f6;
                        margin-bottom: 0.75rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    ">{payment_rate:.1f}%</div>
                    <div style="
                        font-size: 0.875rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        color: #64748b;
                        margin-bottom: 0.5rem;
                    ">{t('analytics_page.payment_rate')}</div>
                    <div style="
                        font-size: 0.75rem;
                        color: #94a3b8;
                        font-weight: 500;
                    ">€{paid_value:,.0f} {t('analytics_page.paid')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='
                border-top: 2px solid #e2e8f0;
                margin: 2rem 0 1.5rem 0;
                position: relative;
            '>
                <div style="
                    position: absolute;
                    top: -12px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: white;
                    padding: 0 1rem;
                    color: #64748b;
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{t('analytics_page.detailed_analysis')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

       
        
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                f"💰 {t('analytics_page.financial_tab')}",
                f"⚙️ {t('analytics_page.workflow_tab')}",
                f"🏪 {t('analytics_page.suppliers_tab')}",
                f"🏢 {t('analytics_page.cost_centers_tab')}",
            ]
        )

        with tab1:
            docs_with_dates = [doc for doc in docs if doc.get("invoiceDate")]
            if docs_with_dates:
                st.markdown(
                    f'<div class="section-header" style="margin-bottom: 1rem;"><div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); flex-shrink: 0; margin-right: 0.5rem;">📈</div> {t("analytics_page.monthly_spending_trend")}</div>',
                    unsafe_allow_html=True,
                )
                timeline_data = []
                for doc in docs_with_dates:
                    try:
                        timeline_data.append(
                            {
                                "Date": pd.to_datetime(doc.get("invoiceDate")),
                                "Value": doc.get("totalGross", 0),
                            }
                        )
                    except:
                        pass

                if timeline_data:
                    df_timeline = pd.DataFrame(timeline_data)
                    df_timeline["Month"] = df_timeline["Date"].dt.strftime("%Y-%m")
                    monthly_trend = (
                        df_timeline.groupby("Month").agg({"Value": "sum"}).reset_index()
                    )
                    monthly_trend.columns = ["Month", "Total Value"]

                    fig_trend = px.area(
                        monthly_trend,
                        x="Month",
                        y="Total Value",
                        labels={"Total Value": "Total Spending (€)", "Month": "Month"},
                    )
                    fig_trend.update_traces(
                        fill="tozeroy",
                        line_color="#3b82f6",
                        fillcolor="rgba(59, 130, 246, 0.25)",
                        line_width=3,
                        hovertemplate="<b>%{x}</b><br>€%{y:,.0f}<extra></extra>",
                    )
                    fig_trend.update_layout(
                        height=350,
                        showlegend=False,
                        hovermode="x unified",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif", size=12),
                        xaxis=dict(
                            gridcolor="rgba(0,0,0,0.05)",
                            showgrid=True,
                            title_font=dict(size=14, color="#64748b"),
                        ),
                        yaxis=dict(
                            gridcolor="rgba(0,0,0,0.05)",
                            showgrid=True,
                            title_font=dict(size=14, color="#64748b"),
                        ),
                        margin=dict(l=20, r=20, t=20, b=40),
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f'<div class="section-header" style="margin-bottom: 1.25rem;"><div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); flex-shrink: 0; margin-right: 0.5rem;">💳</div> {t("analytics_page.payment_status_overview")}</div>',
                    unsafe_allow_html=True,
                )
                if payment_counts:
                    paid_value = payment_totals.get("Paid", 0)
                    open_value = payment_totals.get("Open", 0) + payment_totals.get(
                        "Pending", 0
                    )
                    payment_rate = (
                        (paid_value / total_gross * 100) if total_gross > 0 else 0
                    )

                    fig_payment = px.pie(
                        values=list(payment_counts.values()),
                        names=list(payment_counts.keys()),
                        hole=0.65,
                        color_discrete_sequence=[
                            "#10b981",
                            "#f59e0b",
                            "#ef4444",
                            "#06b6d4",
                            "#8b5cf6",
                        ],
                    )
                    fig_payment.update_traces(
                        textposition="inside",
                        textinfo="percent+label",
                        textfont=dict(size=12, color="white", family="Inter, sans-serif"),
                        hovertemplate="<b>%{label}</b><br>%{value} documents<br>%{percent}<extra></extra>",
                        marker=dict(line=dict(color="#ffffff", width=2)),
                    )
                    fig_payment.update_layout(
                        height=320,
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            font=dict(size=11, color="#64748b"),
                        ),
                        margin=dict(t=20, b=20, l=20, r=120),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif"),
                    )
                    st.plotly_chart(fig_payment, use_container_width=True)

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric(
                            t("analytics_page.outstanding"), f"€{open_value:,.0f}"
                        )
                    with col_b:
                        st.metric(
                            t("analytics_page.payment_rate"), f"{payment_rate:.1f}%"
                        )

            with col2:
                st.markdown(
                    f'<div class="section-header" style="margin-bottom: 1.25rem;"><div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🎯</div> {t("analytics_page.high_value_alerts")}</div>',
                    unsafe_allow_html=True,
                )
                sorted_docs = sorted(
                    docs, key=lambda x: x.get("totalGross", 0), reverse=True
                )[:5]

                for idx, doc in enumerate(sorted_docs, 1):
                    value = doc.get("totalGross", 0)
                    supplier = doc.get("supplierName", "Unknown")[:25]
                    payment_status = doc.get("paymentState", "Unknown")

                    if payment_status == "Paid":
                        status_color = "#10b981"
                        status_bg = "rgba(16, 185, 129, 0.08)"
                    elif payment_status in ["Open", "Pending"]:
                        status_color = "#f59e0b"
                        status_bg = "rgba(245, 158, 11, 0.08)"
                    else:
                        status_color = "#6366f1"
                        status_bg = "rgba(99, 102, 241, 0.08)"

                    st.markdown(
                        f"""
                        <div style="
                            background: {status_bg};
                            padding: 0.75rem 1rem;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                            border-left: 3px solid {status_color};
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        ">
                            <div style="flex: 1;">
                                <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b; margin-bottom: 0.25rem;">#{idx}</div>
                                <div style="font-weight: 700; font-size: 0.875rem; color: #1e293b; margin-bottom: 0.25rem;">{supplier}</div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: {status_color}; text-transform: uppercase; letter-spacing: 0.5px;">● {payment_status}</div>
                            </div>
                            <div style="font-weight: 900; color: {status_color}; font-size: 1.1rem; white-space: nowrap; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);">€{value:,.0f}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        with tab2:
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown(
                    f'<div class="section-header"><div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🎯</div> {t("analytics_page.document_status_at_glance")}</div>',
                    unsafe_allow_html=True,
                )

                if stage_counts:
                    status_data = pd.DataFrame(
                        [
                            {
                                "Status": k,
                                "Count": v,
                                "Value": sum(
                                    [
                                        abs(d.get("totalGross", 0))
                                        for d in docs
                                        if d.get("currentStage") == k
                                    ]
                                ),
                            }
                            for k, v in stage_counts.items()
                        ]
                    ).sort_values("Count", ascending=True)

                    fig_status = px.bar(
                        status_data,
                        y="Status",
                        x="Count",
                        orientation="h",
                        text="Count",
                        color="Count",
                        color_continuous_scale=["#dbeafe", "#3b82f6", "#1e40af"],
                    )
                    fig_status.update_traces(textposition="outside")
                    fig_status.update_layout(
                        height=350,
                        showlegend=False,
                        xaxis_title="Number of Documents",
                        yaxis_title="",
                        margin=dict(l=20, r=20, t=20, b=20),
                    )
                    st.plotly_chart(fig_status, use_container_width=True)

            with col2:
                st.markdown(
                    f'<div class="section-header"><div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3); flex-shrink: 0; margin-right: 0.5rem;">⚠️</div> {t("analytics_page.action_required")}</div>',
                    unsafe_allow_html=True,
                )

                stages_only = {k: v for k, v in stage_counts.items() if "Stage" in k}
                if stages_only:
                    bottleneck = max(stages_only.items(), key=lambda x: x[1])
                    bottleneck_value = sum(
                        [
                            abs(d.get("totalGross", 0))
                            for d in docs
                            if d.get("currentStage") == bottleneck[0]
                        ]
                    )

                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.05));
                            padding: 1rem;
                            border-radius: 12px;
                            border-left: 4px solid #f59e0b;
                            margin-bottom: 1rem;
                        ">
                            <div style="font-size: 0.75rem; color: #92400e; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">{t('analytics_page.bottleneck_detected')}</div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: #f59e0b; margin-bottom: 0.5rem;">{bottleneck[0]}</div>
                            <div style="font-size: 0.875rem; color: #78350f;">{bottleneck[1]} {t('analytics_page.documents_stuck')}</div>
                            <div style="font-size: 0.875rem; color: #78350f; font-weight: 600;">€{bottleneck_value:,.0f} {t('analytics_page.waiting')}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                completion_rate = (
                    (approved_count / len(docs) * 100) if len(docs) > 0 else 0
                )
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
                        padding: 1rem;
                        border-radius: 12px;
                        border-left: 4px solid #10b981;
                    ">
                        <div style="font-size: 0.75rem; color: #065f46; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">{t('analytics_page.completion_rate')}</div>
                        <div style="font-size: 2rem; font-weight: 800; color: #10b981;">{completion_rate:.1f}%</div>
                        <div style="font-size: 0.875rem; color: #047857;">{approved_count} {t('analytics_page.of_approved').format(count=len(docs))}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-header"><div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🏢</div> {t("analytics_page.activity_by_company")}</div>',
                unsafe_allow_html=True,
            )

            company_data = {}
            for doc in docs:
                company = doc.get("companyName", "Unknown")
                if company not in company_data:
                    company_data[company] = {"count": 0, "value": 0, "approved": 0}
                company_data[company]["count"] += 1
                company_data[company]["value"] += abs(doc.get("totalGross", 0))
                if doc.get("currentStage") == "Approved":
                    company_data[company]["approved"] += 1

            company_df = pd.DataFrame(
                [
                    {
                        "Company": k,
                        "Documents": v["count"],
                        "Total Value": f"€{v['value']:,.0f}",
                        "Approved": (
                            f"{(v['approved']/v['count']*100):.0f}%"
                            if v["count"] > 0
                            else "0%"
                        ),
                    }
                    for k, v in sorted(
                        company_data.items(), key=lambda x: x[1]["value"], reverse=True
                    )
                ]
            )[:10]

            if len(company_df) > 10:
                page_size = get_page_size_selector(
                    current_size=10,
                    key="company_page_size",
                    options=[10, 25, 50]
                )
                
                paginated_df, _, _, _ = paginate_dataframe(
                    company_df,
                    page_size=page_size,
                    page_key="company_page",
                    show_info=True
                )
                company_df = paginated_df

            st.dataframe(
                company_df, use_container_width=True, hide_index=True, height=250
            )

        with tab3:
            supplier_values = {}
            supplier_counts = {}
            for doc in docs:
                supplier = doc.get("supplierName", "Unknown")
                value = abs(doc.get("totalGross", 0))
                supplier_values[supplier] = supplier_values.get(supplier, 0) + value
                supplier_counts[supplier] = supplier_counts.get(supplier, 0) + 1

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(
                    f'<div class="section-header"><div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🎯</div> {t("analytics_page.top_10_suppliers_spending")}</div>',
                    unsafe_allow_html=True,
                )

                top_suppliers = sorted(
                    supplier_values.items(), key=lambda x: x[1], reverse=True
                )[:10]

                if top_suppliers:
                    top_df = pd.DataFrame(top_suppliers, columns=["Supplier", "Value"])
                    top_df["Percentage"] = (top_df["Value"] / total_gross * 100).round(
                        1
                    )
                    top_df["Value_Display"] = top_df["Value"]

                    fig_suppliers = px.bar(
                        top_df,
                        y="Supplier",
                        x="Value_Display",
                        orientation="h",
                        text=top_df.apply(
                            lambda row: f"€{row['Value']:,.0f} ({row['Percentage']:.1f}%)",
                            axis=1,
                        ),
                        color="Percentage",
                        color_continuous_scale=["#dbeafe", "#3b82f6", "#1e3a8a"],
                    )
                    fig_suppliers.update_traces(textposition="outside")
                    fig_suppliers.update_layout(
                        showlegend=False,
                        height=380,
                        xaxis_title="Total Spending (€)",
                        yaxis_title="",
                        margin=dict(l=20, r=100, t=20, b=20),
                    )
                    st.plotly_chart(fig_suppliers, use_container_width=True)

            with col2:
                st.markdown(
                    f'<div class="section-header"><div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); flex-shrink: 0; margin-right: 0.5rem;">⚠️</div> {t("analytics_page.dependency_risk")}</div>',
                    unsafe_allow_html=True,
                )

                top5_value = sum([v for _, v in top_suppliers[:5]])
                top5_percentage = (
                    (top5_value / total_gross * 100) if total_gross > 0 else 0
                )

                if top5_percentage > 70:
                    risk_level = "HIGH"
                    risk_color = "#ef4444"
                    risk_bg = "rgba(239, 68, 68, 0.1)"
                    risk_message = t("analytics_page.heavy_reliance")
                elif top5_percentage > 50:
                    risk_level = "MEDIUM"
                    risk_color = "#f59e0b"
                    risk_bg = "rgba(245, 158, 11, 0.1)"
                    risk_message = t("analytics_page.moderate_concentration")
                else:
                    risk_level = "LOW"
                    risk_color = "#10b981"
                    risk_bg = "rgba(16, 185, 129, 0.1)"
                    risk_message = t("analytics_page.well_diversified")

                st.markdown(
                    f"""
                    <div style="
                        background: {risk_bg};
                        padding: 1.25rem;
                        border-radius: 12px;
                        border-left: 4px solid {risk_color};
                        margin-bottom: 1rem;
                    ">
                        <div style="font-size: 0.7rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">{t('analytics_page.concentration_risk')}</div>
                        <div style="font-size: 1.75rem; font-weight: 800; color: {risk_color}; margin-bottom: 0.5rem;">{risk_level}</div>
                        <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.75rem;">{risk_message}</div>
                        <div style="font-size: 0.75rem; color: #64748b; padding-top: 0.75rem; border-top: 1px solid rgba(0,0,0,0.1);">
                            {t('analytics_page.top_5_suppliers')}: <strong style="color: {risk_color};">{top5_percentage:.1f}%</strong> {t('analytics_page.of_total_spending')}
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div style="background: #f8fafc; padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 2rem; font-weight: 800; color: #3b82f6;">{unique_suppliers}</div>
                        <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase;">{t('analytics_page.total_suppliers')}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-header"><div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3); flex-shrink: 0; margin-right: 0.5rem;">📋</div> {t("analytics_page.supplier_performance_matrix")}</div>',
                unsafe_allow_html=True,
            )

            supplier_summary = []
            for supplier in sorted(
                supplier_values.keys(), key=lambda x: supplier_values[x], reverse=True
            )[:12]:
                value = supplier_values[supplier]
                count = supplier_counts[supplier]
                percentage = (value / total_gross * 100) if total_gross > 0 else 0
                supplier_summary.append(
                    {
                        "Supplier": supplier[:35],
                        "Total Spent": f"€{value:,.0f}",
                        "% of Total": f"{percentage:.1f}%",
                        "Invoices": count,
                        "Avg Invoice": f"€{(value / count):,.0f}",
                    }
                )

            if supplier_summary:
                df_suppliers = pd.DataFrame(supplier_summary)
                
                if len(df_suppliers) > 25:
                    page_size = get_page_size_selector(
                        current_size=25,
                        key="suppliers_page_size",
                        options=[10, 25, 50, 100]
                    )
                    
                    paginated_df, _, _, _ = paginate_dataframe(
                        df_suppliers,
                        page_size=page_size,
                        page_key="suppliers_page",
                        show_info=True
                    )
                    df_suppliers = paginated_df
                
                st.dataframe(
                    df_suppliers, use_container_width=True, hide_index=True, height=350
                )

        with tab4:
            st.markdown(
                f"""
                <div style="margin-bottom: 1.5rem;">
                    <div class="section-header">
                        <div style="
                            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                            width: 40px;
                            height: 40px;
                            border-radius: 10px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 20px;
                            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                            flex-shrink: 0;
                            margin-right: 0.5rem;
                        ">🔍</div>
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">{t('analytics_page.filter_cost_centers')}</h3>
                            <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{t('analytics_page.select_cost_centers_to_analyze')}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            cost_center_list = st.session_state.get("analytics_cost_centers", [])
            selected_cost_centers = []

            if cost_center_list:
                col_cc1, col_cc2 = st.columns([1, 2])
                with col_cc1:
                    search_term = st.text_input(
                        t("analytics_page.search"),
                        placeholder=t("analytics_page.search_placeholder"),
                        help=t("analytics_page.search_help"),
                        key="analytics_cc_search_tab4",
                    )

                if search_term:
                    filtered_cc_list = [
                        cc for cc in cost_center_list if str(cc).startswith(search_term)
                    ]
                else:
                    filtered_cc_list = cost_center_list

                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                with col_btn1:
                    if st.button(
                        t("common.select_all"),
                        key="analytics_select_all_tab4",
                        use_container_width=True,
                    ):
                        st.session_state.analytics_cc_multiselect_tab4 = filtered_cc_list
                        st.rerun()
                with col_btn2:
                    if st.button(
                        t("common.deselect_all"),
                        key="analytics_deselect_all_tab4",
                        use_container_width=True,
                    ):
                        st.session_state.analytics_cc_multiselect_tab4 = []
                        st.rerun()

                with col_cc2:
                    selected_cost_centers = st.multiselect(
                        t("analytics_page.select_cost_centers"),
                        options=filtered_cc_list,
                        help=t("analytics_page.select_help"),
                        key="analytics_cc_multiselect_tab4",
                    )

                col_info1, col_info2 = st.columns([1, 2])
                with col_info1:
                    if search_term:
                        st.caption(
                            t("analytics_page.found_matching").format(
                                count=len(filtered_cc_list)
                            )
                        )
                    else:
                        st.caption(
                            t("analytics_page.available_count").format(
                                count=len(cost_center_list)
                            )
                        )
                with col_info2:
                    if selected_cost_centers:
                        st.caption(
                            t("analytics_page.selected_count").format(
                                count=len(selected_cost_centers)
                            )
                        )
            else:
                st.info(t("analytics_page.load_cost_centers_first"))

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div style="margin-bottom: 1rem;">
                    <div class="section-header">
                        <div style="
                            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                            width: 40px;
                            height: 40px;
                            border-radius: 10px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 20px;
                            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                            flex-shrink: 0;
                            margin-right: 0.5rem;
                        ">📅</div>
                        <div style="flex: 1;">
                            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">{t('analytics_page.date_range')}</h3>
                            <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{t('analytics_page.select_date_range_for_cost_centers')}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if (
                "analytics_cc_sync_start" in st.session_state
                and "analytics_cc_sync_end" in st.session_state
            ):
                sync_start = st.session_state.analytics_cc_sync_start
                sync_end = st.session_state.analytics_cc_sync_end
                cc_from_month_default = sync_start.month - 1
                cc_from_year_default = list(range(2020, datetime.now().year + 1)).index(
                    sync_start.year
                )
                cc_to_month_default = sync_end.month - 1
                cc_to_year_default = list(range(2020, datetime.now().year + 1)).index(
                    sync_end.year
                )
            elif (
                "quick_filter_start" in st.session_state
                and "quick_filter_end" in st.session_state
            ):
                quick_start = st.session_state.quick_filter_start
                quick_end = st.session_state.quick_filter_end
                cc_from_month_default = quick_start.month - 1
                cc_from_year_default = list(range(2020, datetime.now().year + 1)).index(
                    quick_start.year
                )
                cc_to_month_default = quick_end.month - 1
                cc_to_year_default = list(range(2020, datetime.now().year + 1)).index(
                    quick_end.year
                )
            else:
                cc_from_month_default = 0
                cc_from_year_default = 3
                cc_to_month_default = datetime.now().month - 1
                cc_to_year_default = len(list(range(2020, datetime.now().year + 1))) - 1

            col_cc_date1, col_cc_date2, col_cc_date3, col_cc_date4 = st.columns(4)

            with col_cc_date1:
                cc_from_month = st.selectbox(
                    t("analytics_page.from_month"),
                    options=list(range(1, 13)),
                    format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                    index=cc_from_month_default,
                    key="analytics_cc_from_month_tab4",
                )

            with col_cc_date2:
                cc_from_year = st.selectbox(
                    t("analytics_page.from_year"),
                    options=list(range(2020, datetime.now().year + 1)),
                    index=cc_from_year_default,
                    key="analytics_cc_from_year_tab4",
                )

            with col_cc_date3:
                cc_to_month = st.selectbox(
                    t("analytics_page.to_month"),
                    options=list(range(1, 13)),
                    format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
                    index=cc_to_month_default,
                    key="analytics_cc_to_month_tab4",
                )

            with col_cc_date4:
                cc_to_year = st.selectbox(
                    t("analytics_page.to_year"),
                    options=list(range(2020, datetime.now().year + 1)),
                    index=cc_to_year_default,
                    key="analytics_cc_to_year_tab4",
                )

            cc_min_date = date(cc_from_year, cc_from_month, 1)
            cc_last_day = calendar.monthrange(cc_to_year, cc_to_month)[1]
            cc_max_date = date(cc_to_year, cc_to_month, cc_last_day)
            cc_date_from = cc_min_date
            cc_date_to = cc_max_date

            st.markdown("<br>", unsafe_allow_html=True)

            current_date_key = f"{cc_date_from.isoformat()}_{cc_date_to.isoformat()}"
            
            if PERFORMANCE_OPTIMIZATIONS_ENABLED:
                receipt_data = get_cached_receipt_data(current_date_key)
                if receipt_data is None:
                    receipt_data = []
            else:
                cached_date_key = st.session_state.get("analytics_receipt_date_key", "")
                receipt_data = st.session_state.get("analytics_receipt_data", [])
                if cached_date_key != current_date_key:
                    receipt_data = []
                if receipt_data is None:
                    receipt_data = []

            if not receipt_data or len(receipt_data) == 0:
                filter_params = {
                    "min_date": cc_date_from.isoformat(),
                    "max_date": cc_date_to.isoformat(),
                }
                with st.spinner(t("analytics_page.loading_cc_data")):
                    try:
                        receipt_report = client.get_receipt_splitting_report(
                            **filter_params
                        )
                        if receipt_report:
                            if PERFORMANCE_OPTIMIZATIONS_ENABLED:
                                cache_receipt_data(receipt_report, current_date_key)
                            else:
                                st.session_state.analytics_receipt_data = receipt_report
                                st.session_state.analytics_receipt_date_key = current_date_key
                            receipt_data = receipt_report if receipt_report else []
                        else:
                            receipt_data = []
                    except Exception as e:
                        st.error(f"Error loading receipt data: {str(e)}")
                        receipt_data = []

            if not receipt_data or len(receipt_data) == 0:
                st.warning(t("analytics_page.no_cc_data_found"))
            else:
                df_receipts = pd.DataFrame(receipt_data)

                filtered_receipts = receipt_data

                if selected_cost_centers:
                    filtered_receipts = [
                        r
                        for r in filtered_receipts
                        if str(r.get("costCenter", "")) in selected_cost_centers
                    ]

                if len(filtered_receipts) == 0:
                    st.warning(t("analytics_page.no_cc_data_after_filter"))
                else:
                    df_filtered = pd.DataFrame(filtered_receipts)

                    amount_col = None
                    for col in [
                        "grossValue",
                        "netValue",
                        "grossAmount",
                        "netAmount",
                        "amount",
                        "value",
                        "total",
                    ]:
                        if col in df_filtered.columns:
                            amount_col = col
                            break

                    cost_center_col = None
                    for col in ["costCenter", "CostCenter", "cost_center"]:
                        if col in df_filtered.columns:
                            cost_center_col = col
                            break

                    if amount_col and cost_center_col:
                        df_filtered[amount_col] = pd.to_numeric(
                            df_filtered[amount_col], errors="coerce"
                        ).fillna(0)

                        if 'analytics_doc_type_cache' not in st.session_state:
                            st.session_state.analytics_doc_type_cache = {}
                        
                        doc_type_cache = st.session_state.analytics_doc_type_cache
                        unique_doc_ids = [int(x) for x in pd.Series(df_filtered['documentId']).dropna().unique()]
                        
                        missing_ids = [doc_id for doc_id in unique_doc_ids if doc_id not in doc_type_cache]
                        
                        if missing_ids:
                            with st.spinner(t("analytics_page.enriching_documents_type").format(count=len(missing_ids))):
                                for doc_id in missing_ids:
                                    try:
                                        detail = client.get_document(int(doc_id))
                                        if detail:
                                            doc_type_cache[doc_id] = detail.get('documentType') or detail.get('documentKind') or ''
                                        else:
                                            doc_type_cache[doc_id] = ''
                                    except Exception:
                                        doc_type_cache[doc_id] = ''
                            
                            st.session_state.analytics_doc_type_cache = doc_type_cache
                        
                        df_filtered['_documentType'] = df_filtered['documentId'].map(doc_type_cache)

                        def classify_row(row):
                            doc_type = str(row.get('_documentType') or row.get('documentType') or row.get('documentKind') or '').lower()
                            amount = row[amount_col]
                            if 'ausgangsrechnung' in doc_type or 'outgoinginvoice' in doc_type or 'ausgang' in doc_type:
                                return 'income'
                            if 'eingangsrechnung' in doc_type or 'incominginvoice' in doc_type or 'eingang' in doc_type:
                                return 'cost'
                            return 'income' if amount < 0 else 'cost'
                        
                        df_filtered['__category'] = df_filtered.apply(classify_row, axis=1)
                        
                        cost_total = df_filtered.loc[df_filtered['__category'] == 'cost', amount_col].apply(abs).sum()
                        income_total = df_filtered.loc[df_filtered['__category'] == 'income', amount_col].apply(abs).sum()
                        margin = income_total - cost_total
                        net_total = df_filtered[amount_col].sum()
                        
                        num_cost_centers = df_filtered[cost_center_col].nunique()
                        num_records = len(df_filtered)

                        margin_color = "#dc2626" if margin < 0 else "#16a34a"
                        income_color = "#dc2626" if income_total < 0 else "#16a34a"
                        cost_color = "#dc2626" if cost_total < 0 else "#16a34a"
                        
                        
                        try:
                            margin_label = t('analytics_page.margin_income_cost')
                            if margin_label == 'analytics_page.margin_income_cost':
                                margin_label = 'Margin (Income - Cost)'
                        except:
                            margin_label = 'Margin (Income - Cost)'
                        
                        try:
                            income_label = t('analytics_page.total_income_debs')
                            if income_label == 'analytics_page.total_income_debs':
                                income_label = 'Total Income (Debs)'
                        except:
                            income_label = 'Total Income (Debs)'
                        
                        try:
                            cost_label = t('analytics_page.total_cost_kreds')
                            if cost_label == 'analytics_page.total_cost_kreds':
                                cost_label = 'Total Cost (Kreds)'
                        except:
                            cost_label = 'Total Cost (Kreds)'
                        
                        try:
                            cc_count_label = t('analytics_page.num_cost_centers')
                            if cc_count_label == 'analytics_page.num_cost_centers':
                                cc_count_label = 'Cost Centers'
                        except:
                            cc_count_label = 'Cost Centers'
                        
                        fin_cols_cc = st.columns(4)
                        
                        with fin_cols_cc[0]:
                            st.markdown(
                                f"""
                                <div style="
                                    background: linear-gradient(135deg, {margin_color}15 0%, {margin_color}08 100%);
                                    border: 1px solid {margin_color}40;
                                    padding: 1.5rem 1rem;
                                    border-radius: 20px;
                                    text-align: center;
                                    min-height: 140px;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: center;
                                    box-shadow: 0 4px 12px {margin_color}20;
                                    transition: all 0.3s ease;
                                    overflow: hidden;
                                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px {margin_color}30'"
                                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px {margin_color}20'">
                                    <div style="
                                        font-size: 1.8rem;
                                        font-weight: 900;
                                        color: {margin_color};
                                        margin-bottom: 0.5rem;
                                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                        font-family: 'SF Mono', Monaco, monospace;
                                        line-height: 1.2;
                                        word-break: break-word;
                                    ">{margin:,.2f} €</div>
                                    <div style="
                                        font-size: 0.75rem;
                                        font-weight: 700;
                                        text-transform: uppercase;
                                        letter-spacing: 0.5px;
                                        color: #64748b;
                                        margin-bottom: 0.5rem;
                                        line-height: 1.2;
                                    ">{margin_label}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        
                        with fin_cols_cc[1]:
                            st.markdown(
                                f"""
                                <div style="
                                    background: linear-gradient(135deg, {income_color}15 0%, {income_color}08 100%);
                                    border: 1px solid {income_color}40;
                                    padding: 1.5rem 1rem;
                                    border-radius: 20px;
                                    text-align: center;
                                    min-height: 140px;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: center;
                                    box-shadow: 0 4px 12px {income_color}20;
                                    transition: all 0.3s ease;
                                    overflow: hidden;
                                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px {income_color}30'"
                                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px {income_color}20'">
                                    <div style="
                                        font-size: 1.8rem;
                                        font-weight: 900;
                                        color: {income_color};
                                        margin-bottom: 0.5rem;
                                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                        font-family: 'SF Mono', Monaco, monospace;
                                        line-height: 1.2;
                                        word-break: break-word;
                                    ">{income_total:,.2f} €</div>
                                    <div style="
                                        font-size: 0.75rem;
                                        font-weight: 700;
                                        text-transform: uppercase;
                                        letter-spacing: 0.5px;
                                        color: #64748b;
                                        margin-bottom: 0.5rem;
                                        line-height: 1.2;
                                    ">{income_label}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        
                        with fin_cols_cc[2]:
                            st.markdown(
                                f"""
                                <div style="
                                    background: linear-gradient(135deg, {cost_color}15 0%, {cost_color}08 100%);
                                    border: 1px solid {cost_color}40;
                                    padding: 1.5rem 1rem;
                                    border-radius: 20px;
                                    text-align: center;
                                    min-height: 140px;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: center;
                                    box-shadow: 0 4px 12px {cost_color}20;
                                    transition: all 0.3s ease;
                                    overflow: hidden;
                                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px {cost_color}30'"
                                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px {cost_color}20'">
                                    <div style="
                                        font-size: 1.8rem;
                                        font-weight: 900;
                                        color: {cost_color};
                                        margin-bottom: 0.5rem;
                                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                        font-family: 'SF Mono', Monaco, monospace;
                                        line-height: 1.2;
                                        word-break: break-word;
                                    ">{cost_total:,.2f} €</div>
                                    <div style="
                                        font-size: 0.75rem;
                                        font-weight: 700;
                                        text-transform: uppercase;
                                        letter-spacing: 0.5px;
                                        color: #64748b;
                                        margin-bottom: 0.5rem;
                                        line-height: 1.2;
                                    ">{cost_label}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        
                        with fin_cols_cc[3]:
                            st.markdown(
                                f"""
                                <div style="
                                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(79, 70, 229, 0.04) 100%);
                                    border: 1px solid rgba(99, 102, 241, 0.2);
                                    padding: 1.5rem 1rem;
                                    border-radius: 20px;
                                    text-align: center;
                                    min-height: 140px;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: center;
                                    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
                                    transition: all 0.3s ease;
                                    overflow: hidden;
                                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(99, 102, 241, 0.2)'"
                                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(99, 102, 241, 0.1)'">
                                    <div style="
                                        font-size: 1.8rem;
                                        font-weight: 900;
                                        color: #6366f1;
                                        margin-bottom: 0.5rem;
                                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                        font-family: 'SF Mono', Monaco, monospace;
                                        line-height: 1.2;
                                        word-break: break-word;
                                    ">{num_cost_centers:,}</div>
                                    <div style="
                                        font-size: 0.75rem;
                                        font-weight: 700;
                                        text-transform: uppercase;
                                        letter-spacing: 0.5px;
                                        color: #64748b;
                                        margin-bottom: 0.5rem;
                                        line-height: 1.2;
                                    ">{cc_count_label}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        
                        st.markdown("<br>", unsafe_allow_html=True)

                        enriched_df = df_filtered.copy()
                        enriched_df["cc_parsed"] = enriched_df[cost_center_col].apply(
                            parse_cost_center
                        )
                        enriched_df["cc_display"] = enriched_df["cc_parsed"].apply(
                            lambda x: x["display_name"]
                        )
                        enriched_df["cc_number"] = enriched_df[cost_center_col].astype(
                            str
                        )
                        
                        def calc_cc_metrics(group):
                            income = group.loc[group['__category'] == 'income', amount_col].apply(abs).sum()
                            cost = group.loc[group['__category'] == 'cost', amount_col].apply(abs).sum()
                            margin = income - cost
                            return pd.Series({'income': income, 'cost': cost, 'margin': margin})
                        
                        cc_breakdown = enriched_df.groupby(['cc_number', 'cc_display']).apply(calc_cc_metrics).reset_index()
                        cc_breakdown = cc_breakdown.sort_values('margin', ascending=False)

                        st.markdown(
                            f'<div class="section-header" style="margin-bottom: 1.5rem;"><div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); flex-shrink: 0; margin-right: 0.5rem;">💰</div> {t("analytics_page.cost_center_split")}</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            """
                            <style>
                                .cc-table-wrapper {
                                    border: 1px solid #e2e8f0;
                                    border-radius: 10px;
                                    overflow: hidden;
                                    margin-top: 0.75rem;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-wrapper {
                                        border-color: rgba(71, 85, 105, 0.5);
                                    }
                                }
                                .cc-table-scroll {
                                    max-height: 600px;
                                    overflow-y: auto;
                                    background: #ffffff;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-scroll {
                                        background: rgba(15, 23, 42, 0.4);
                                    }
                                }
                                .cc-table {
                                    width: 100%;
                                    border-collapse: collapse;
                                }
                                .cc-table-header {
                                    background: #f8fafc;
                                    position: sticky;
                                    top: 0;
                                    z-index: 10;
                                    border-bottom: 2px solid #e2e8f0;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-header {
                                        background: rgba(30, 41, 59, 0.95);
                                        border-bottom-color: rgba(71, 85, 105, 0.5);
                                    }
                                }
                                .cc-table-header th {
                                    padding: 0.75rem 1rem;
                                    text-align: left;
                                    font-weight: 600;
                                    font-size: 0.8rem;
                                    text-transform: uppercase;
                                    letter-spacing: 0.05em;
                                    color: #64748b;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-header th {
                                        color: #94a3b8;
                                    }
                                }
                                .cc-table-header th:nth-child(3),
                                .cc-table-header th:nth-child(4),
                                .cc-table-header th:nth-child(5) {
                                    text-align: right;
                                }
                                .cc-table-row {
                                    border-bottom: 1px solid #f1f5f9;
                                    transition: background 0.15s ease;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-row {
                                        border-bottom-color: rgba(71, 85, 105, 0.2);
                                    }
                                }
                                .cc-table-row:hover {
                                    background: #f8fafc;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-row:hover {
                                        background: rgba(30, 41, 59, 0.4);
                                    }
                                }
                                .cc-table-row td {
                                    padding: 0.65rem 1rem;
                                    font-size: 0.9rem;
                                }
                                .cc-table-row td:nth-child(1) {
                                    font-weight: 600;
                                    color: #6366f1;
                                    font-family: 'SF Mono', Monaco, monospace;
                                    width: 15%;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-row td:nth-child(1) {
                                        color: #a5b4fc;
                                    }
                                }
                                .cc-table-row td:nth-child(2) {
                                    color: #1e293b;
                                    font-weight: 500;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-row td:nth-child(2) {
                                        color: #e2e8f0;
                                    }
                                }
                                .cc-table-row td:nth-child(3),
                                .cc-table-row td:nth-child(4),
                                .cc-table-row td:nth-child(5) {
                                    text-align: right;
                                    font-weight: 600;
                                    font-family: 'SF Mono', Monaco, monospace;
                                    width: 18%;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-row td:nth-child(3),
                                    .cc-table-row td:nth-child(4),
                                    .cc-table-row td:nth-child(5) {
                                        color: #a5b4fc;
                                    }
                                }
                                .cc-table-footer {
                                    background: #eef2ff;
                                    position: sticky;
                                    bottom: 0;
                                    z-index: 10;
                                    border-top: 2px solid #6366f1;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-footer {
                                        background: rgba(99, 102, 241, 0.15);
                                    }
                                }
                                .cc-table-footer td {
                                    padding: 0.85rem 1rem;
                                    font-weight: 700;
                                    font-size: 0.95rem;
                                }
                                .cc-table-footer td:nth-child(1) {
                                    color: #1e293b;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-footer td:nth-child(1) {
                                        color: #f1f5f9;
                                    }
                                }
                                .cc-table-footer td:nth-child(3),
                                .cc-table-footer td:nth-child(4),
                                .cc-table-footer td:nth-child(5) {
                                    text-align: right;
                                    font-size: 1.05rem;
                                    font-family: 'SF Mono', Monaco, monospace;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-footer td:nth-child(3),
                                    .cc-table-footer td:nth-child(4),
                                    .cc-table-footer td:nth-child(5) {
                                        color: #a5b4fc;
                                    }
                                }
                                .cc-table-scroll::-webkit-scrollbar {
                                    width: 8px;
                                }
                                .cc-table-scroll::-webkit-scrollbar-track {
                                    background: #f1f5f9;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-scroll::-webkit-scrollbar-track {
                                        background: rgba(30, 41, 59, 0.3);
                                    }
                                }
                                .cc-table-scroll::-webkit-scrollbar-thumb {
                                    background: #cbd5e1;
                                    border-radius: 4px;
                                }
                                .cc-table-scroll::-webkit-scrollbar-thumb:hover {
                                    background: #94a3b8;
                                }
                                @media (prefers-color-scheme: dark) {
                                    .cc-table-scroll::-webkit-scrollbar-thumb {
                                        background: rgba(71, 85, 105, 0.6);
                                    }
                                    .cc-table-scroll::-webkit-scrollbar-thumb:hover {
                                        background: rgba(71, 85, 105, 0.8);
                                    }
                                }
                            </style>
                            """,
                            unsafe_allow_html=True,
                        )

                        rows_html = []
                        for _, row in cc_breakdown.iterrows():
                            cc_num = row["cc_number"]
                            cc_name = row["cc_display"]
                            inc_fmt = f'<span style="color:{"#dc2626" if row["income"] < 0 else "#16a34a"}">{row["income"]:,.2f} €</span>'
                            cost_fmt = f'<span style="color:{"#dc2626" if row["cost"] < 0 else "#16a34a"}">{row["cost"]:,.2f} €</span>'
                            marg_fmt = f'<span style="color:{"#dc2626" if row["margin"] < 0 else "#16a34a"}">{row["margin"]:,.2f} €</span>'
                            rows_html.append(
                                f'<tr class="cc-table-row"><td>{cc_num}</td><td>{cc_name}</td><td style="text-align:right;">{inc_fmt}</td><td style="text-align:right;">{cost_fmt}</td><td style="text-align:right;">{marg_fmt}</td></tr>'
                            )

                        rows_html_str = "".join(rows_html)
                        total_label = t("analytics_page.total")
                        income_fmt = f'<span style="color:{"#dc2626" if income_total < 0 else "#16a34a"}">{income_total:,.2f} €</span>'
                        cost_fmt = f'<span style="color:{"#dc2626" if cost_total < 0 else "#16a34a"}">{cost_total:,.2f} €</span>'
                        margin_fmt = f'<span style="color:{"#dc2626" if margin < 0 else "#16a34a"}">{margin:,.2f} €</span>'

                        table_html = f'<div class="cc-table-wrapper"><div class="cc-table-scroll"><table class="cc-table"><thead class="cc-table-header"><tr><th>Cost Center</th><th>Description</th><th style="text-align:right;">Income</th><th style="text-align:right;">Cost</th><th style="text-align:right;">Margin</th></tr></thead><tbody>{rows_html_str}</tbody><tfoot class="cc-table-footer"><tr><td colspan="2">{total_label}</td><td style="text-align:right;">{income_fmt}</td><td style="text-align:right;">{cost_fmt}</td><td style="text-align:right;">{margin_fmt}</td></tr></tfoot></table></div></div>'

                        st.markdown(table_html, unsafe_allow_html=True)

                        st.markdown("<br><br>", unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="section-header"><div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🏢</div> {t("analytics_page.cost_centers_by_company")}</div>',
                            unsafe_allow_html=True,
                        )

                        if 'companyName' in df_filtered.columns or 'supplierName' in df_filtered.columns:
                            company_col = 'companyName' if 'companyName' in df_filtered.columns else 'supplierName'
                            
                            company_cc_data = []
                            for company in df_filtered[company_col].dropna().unique():
                                company_df = df_filtered[df_filtered[company_col] == company]
                                company_income = company_df.loc[company_df['__category'] == 'income', amount_col].apply(abs).sum()
                                company_cost = company_df.loc[company_df['__category'] == 'cost', amount_col].apply(abs).sum()
                                company_margin = company_income - company_cost
                                company_cc_count = company_df[cost_center_col].nunique()
                                
                                company_cc_data.append({
                                    'Company': company,
                                    'Cost Centers': company_cc_count,
                                    'Income': company_income,
                                    'Cost': company_cost,
                                    'Margin': company_margin,
                                    'Records': len(company_df)
                                })
                            
                            if company_cc_data:
                                company_cc_df = pd.DataFrame(company_cc_data)
                                
                                col_sort1, col_sort2 = st.columns([1, 3])
                                with col_sort1:
                                    try:
                                        company_label = t('analytics_page.companies')
                                        if company_label == 'analytics_page.companies':
                                            company_label = 'Company'
                                    except:
                                        company_label = 'Company'
                                    
                                    margin_label = t('analytics_page.margin')
                                    if margin_label == 'analytics_page.margin':
                                        margin_label = 'Margin'
                                    
                                    income_label = t('analytics_page.total_income_debs')
                                    if income_label == 'analytics_page.total_income_debs':
                                        income_label = 'Total Income (Debs)'
                                    
                                    cost_label = t('analytics_page.total_cost_kreds')
                                    if cost_label == 'analytics_page.total_cost_kreds':
                                        cost_label = 'Total Cost (Kreds)'
                                    
                                    records_label = t('analytics_page.records')
                                    if records_label == 'analytics_page.records':
                                        records_label = 'Records'
                                    
                                    cc_label = t('analytics_page.cost_centers')
                                    if cc_label == 'analytics_page.cost_centers':
                                        cc_label = 'Cost Centers'
                                    
                                    sort_options = {
                                        'Margin': margin_label,
                                        'Income': income_label,
                                        'Cost': cost_label,
                                        'Records': records_label,
                                        'Cost Centers': cc_label,
                                        'Company': company_label
                                    }
                                    sort_by_display = st.selectbox(
                                        t('analytics_page.sort_by'),
                                        options=list(sort_options.keys()),
                                        format_func=lambda x: sort_options[x],
                                        index=0,
                                        key='company_sort_by'
                                    )
                                    sort_by = sort_by_display
                                with col_sort2:
                                    sort_order = st.selectbox(
                                        t('analytics_page.sort_order'),
                                        options=[t('analytics_page.descending'), t('analytics_page.ascending')],
                                        index=0,
                                        key='company_sort_order'
                                    )
                                
                                ascending = sort_order == t('analytics_page.ascending')
                                company_cc_df = company_cc_df.sort_values(sort_by, ascending=ascending)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                
                                # Display as cards matching Financial Summary style - show top 6 companies
                                company_cols = st.columns(3)  # Always 3 columns, will wrap
                                for idx, (_, row) in enumerate(company_cc_df.head(6).iterrows()):
                                    with company_cols[idx % 3]:
                                            margin_color = "#dc2626" if row['Margin'] < 0 else "#16a34a"
                                            st.markdown(
                                                f"""
                                                <div style="
                                                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(124, 58, 237, 0.04) 100%);
                                                    border: 1px solid rgba(139, 92, 246, 0.2);
                                                    border-radius: 20px;
                                                    padding: 1.5rem;
                                                    margin-bottom: 1rem;
                                                    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
                                                    transition: all 0.3s ease;
                                                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 20px rgba(139, 92, 246, 0.2)'"
                                                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(139, 92, 246, 0.1)'">
                                                    <div style="font-weight: 700; font-size: 1rem; color: #1e293b; margin-bottom: 1rem; line-height: 1.2;">{row['Company'][:30]}</div>
                                                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem;">
                                                        <span>{t('analytics_page.cost_centers')}:</span>
                                                        <strong style="color: #6366f1;">{int(row['Cost Centers'])}</strong>
                                                    </div>
                                                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-bottom: 1rem;">
                                                        <span>{t('analytics_page.records')}:</span>
                                                        <strong style="color: #6366f1;">{int(row['Records'])}</strong>
                                                    </div>
                                                    <div style="
                                                        font-size: 2rem;
                                                        font-weight: 900;
                                                        color: {margin_color};
                                                        margin-top: 0.5rem;
                                                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                                        font-family: 'SF Mono', Monaco, monospace;
                                                        margin-bottom: 0.5rem;
                                                    ">
                                                        {row['Margin']:,.2f} €
                                                    </div>
                                                    <div style="
                                                        font-size: 0.875rem;
                                                        font-weight: 700;
                                                        text-transform: uppercase;
                                                        letter-spacing: 0.8px;
                                                        color: #64748b;
                                                    ">{t('analytics_page.margin')}</div>
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )
                        else:
                            st.info(t("analytics_page.no_company_data_available"))
                    else:
                        st.warning(t("analytics_page.no_amount_or_cc_column"))

        st.markdown("---")

        st.markdown(
            f"""
            <div style="margin: 2rem 0 1rem 0;">
                <div class="section-header">
                    <div style="
                        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                        width: 48px;
                        height: 48px;
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
                        flex-shrink: 0;
                    ">💾</div>
                    <div style="flex: 1;">
                        <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{t('analytics_page.export_analytics_data')}</h3>
                        <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{t('analytics_page.download_comprehensive_reports')}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        df_export = pd.DataFrame(
            [
                {
                    "Document ID": doc.get("documentId"),
                    "Supplier": doc.get("supplierName"),
                    "Company": doc.get("companyName"),
                    "Flow": doc.get("flowName"),
                    "Invoice Date": doc.get("invoiceDate"),
                    "Due Date": doc.get("dueDate"),
                    "Total Gross": doc.get("totalGross"),
                    "Total Net": doc.get("totalNet"),
                    "Tax Amount": doc.get("totalGross", 0) - doc.get("totalNet", 0),
                    "Currency": doc.get("currencyCode"),
                    "Stage": doc.get("currentStage"),
                    "Payment State": doc.get("paymentState"),
                    "Created Date": doc.get("createdDate"),
                }
                for doc in docs
            ]
        )

        if docs_with_dates and timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            df_timeline["Month"] = df_timeline["Date"].dt.strftime("%Y-%m")
            monthly_summary = (
                df_timeline.groupby("Month")
                .agg({"Value": ["sum", "mean", "count", "min", "max"]})
                .reset_index()
            )
            monthly_summary.columns = [
                "Month",
                "Total Value",
                "Average Value",
                "Document Count",
                "Min Value",
                "Max Value",
            ]
        else:
            monthly_summary = pd.DataFrame()

        supplier_analysis = pd.DataFrame(
            [
                {
                    "Supplier": supplier,
                    "Total Spending": value,
                    "Document Count": supplier_counts.get(supplier, 0),
                    "Average Invoice": value / supplier_counts.get(supplier, 1),
                    "% of Total": (value / total_gross * 100) if total_gross > 0 else 0,
                }
                for supplier, value in sorted(
                    supplier_values.items(), key=lambda x: x[1], reverse=True
                )
            ]
        )

        workflow_export = pd.DataFrame(
            [
                {
                    "Stage": stage,
                    "Document Count": count,
                    "Total Value": sum(
                        [
                            d.get("totalGross", 0)
                            for d in docs
                            if d.get("currentStage") == stage
                        ]
                    ),
                    "Percentage": (count / len(docs) * 100) if len(docs) > 0 else 0,
                }
                for stage, count in sorted(
                    stage_counts.items(), key=lambda x: x[1], reverse=True
                )
            ]
        )

        payment_export = pd.DataFrame(
            [
                {
                    "Payment Status": status,
                    "Document Count": count,
                    "Total Value": payment_totals.get(status, 0),
                    "Percentage": (count / len(docs) * 100) if len(docs) > 0 else 0,
                }
                for status, count in sorted(
                    payment_counts.items(), key=lambda x: x[1], reverse=True
                )
            ]
        )

        company_summary = pd.DataFrame(
            [
                {
                    "Company": company,
                    "Document Count": data["count"],
                    "Total Value": data["value"],
                    "Approved Count": data["approved"],
                    "Approval Rate": (
                        (data["approved"] / data["count"] * 100)
                        if data["count"] > 0
                        else 0
                    ),
                }
                for company, data in sorted(
                    company_data.items(), key=lambda x: x[1]["value"], reverse=True
                )
            ]
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="glass-section">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-header"><div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); flex-shrink: 0; margin-right: 0.5rem;">📊</div> {t("analytics_page.comprehensive_reports")}</div>', unsafe_allow_html=True)
        export_row1 = st.columns(2)

        with export_row1[0]:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(37, 99, 235, 0.05));
                    padding: 1rem;
                    border-radius: 12px;
                    margin-bottom: 1rem;
                    border-left: 3px solid #3b82f6;
                ">
                    <div style="font-weight: 600; font-size: 0.95rem; color: #1e293b; margin-bottom: 0.5rem;">
                        📄 Complete Document Report
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 1rem;">
                        All documents with full details, dates, amounts, and status (semicolon-delimited)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            csv_data = df_export.to_csv(
                index=False, sep=";", decimal=",", encoding="utf-8-sig"
            )
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"full_document_report_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with export_row1[1]:
            if not monthly_summary.empty:
                st.markdown(
                    """
                    <div style="
                        background: linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(14, 165, 233, 0.05));
                        padding: 1rem;
                        border-radius: 12px;
                        margin-bottom: 1rem;
                        border-left: 3px solid #06b6d4;
                    ">
                        <div style="font-weight: 600; font-size: 0.95rem; color: #1e293b; margin-bottom: 0.5rem;">
                            📈 Monthly Trend Analysis
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 1rem;">
                            Aggregated monthly statistics with totals and averages (semicolon-delimited)
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                csv_monthly = monthly_summary.to_csv(
                    index=False, sep=";", decimal=",", encoding="utf-8-sig"
                )
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_monthly,
                    file_name=f"monthly_trend_analysis_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="glass-section">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-header"><div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🔍</div> {t("analytics_page.detailed_breakdowns")}</div>', unsafe_allow_html=True)
        export_row2 = st.columns(3)

        with export_row2[0]:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(124, 58, 237, 0.05));
                    padding: 1rem;
                    border-radius: 12px;
                    margin-bottom: 1rem;
                    border-left: 3px solid #8b5cf6;
                ">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 0.3rem;">
                        🏪 Supplier Analysis
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.8rem;">
                        Spending by supplier with rankings
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            csv_supplier = supplier_analysis.to_csv(
                index=False, sep=";", decimal=",", encoding="utf-8-sig"
            )
            st.download_button(
                label="📥 Download CSV",
                data=csv_supplier,
                file_name=f"supplier_analysis_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                key="supplier_csv",
            )

        with export_row2[1]:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(5, 150, 105, 0.05));
                    padding: 1rem;
                    border-radius: 12px;
                    margin-bottom: 1rem;
                    border-left: 3px solid #10b981;
                ">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 0.3rem;">
                        ⚙️ Workflow Status
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.8rem;">
                        Documents by approval stage
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            csv_workflow = workflow_export.to_csv(
                index=False, sep=";", decimal=",", encoding="utf-8-sig"
            )
            st.download_button(
                label="📥 Download CSV",
                data=csv_workflow,
                file_name=f"workflow_status_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                key="workflow_csv",
            )

        with export_row2[2]:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(217, 119, 6, 0.05));
                    padding: 1rem;
                    border-radius: 12px;
                    margin-bottom: 1rem;
                    border-left: 3px solid #f59e0b;
                ">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 0.3rem;">
                        💳 Payment Status
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.8rem;">
                        Payment state distribution
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            csv_payment = payment_export.to_csv(
                index=False, sep=";", decimal=",", encoding="utf-8-sig"
            )
            st.download_button(
                label="📥 Download CSV",
                data=csv_payment,
                file_name=f"payment_status_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                key="payment_csv",
            )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="glass-section">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-header"><div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3); flex-shrink: 0; margin-right: 0.5rem;">🏢</div> {t("analytics_page.company_analysis")}</div>', unsafe_allow_html=True)
        export_row3 = st.columns([1, 2])

        with export_row3[0]:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(79, 70, 229, 0.05));
                    padding: 1rem;
                    border-radius: 12px;
                    margin-bottom: 1rem;
                    border-left: 3px solid #6366f1;
                ">
                    <div style="font-weight: 600; font-size: 0.9rem; color: #1e293b; margin-bottom: 0.3rem;">
                        🏢 Company Performance
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.8rem;">
                        Activity and approval rates by company
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            csv_company = company_summary.to_csv(
                index=False, sep=";", decimal=",", encoding="utf-8-sig"
            )
            st.download_button(
                label="📥 Download CSV",
                data=csv_company,
                file_name=f"company_analysis_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
                key="company_csv",
            )

        with export_row3[1]:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(148, 163, 184, 0.08), rgba(100, 116, 139, 0.05));
                    padding: 1.25rem;
                    border-radius: 12px;
                    border: 1px solid rgba(148, 163, 184, 0.2);
                ">
                    <div style="font-weight: 600; font-size: 0.85rem; color: #475569; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">
                        Export Summary
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                        <div>
                            <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 0.2rem;">Documents</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #1e293b;">{len(docs)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 0.2rem;">Date Range</div>
                            <div style="font-size: 0.8rem; font-weight: 600; color: #1e293b;">{date_from.strftime('%b %Y')} - {date_to.strftime('%b %Y')}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 0.2rem;">Total Value</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #3b82f6;">€{total_gross:,.0f}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
