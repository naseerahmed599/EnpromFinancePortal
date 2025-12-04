"""
Companies & Flows Page
Displays and manages companies and their approval flows.
"""

import streamlit as st
import pandas as pd


def render_companies_page(client, t, get_card_styles, get_theme_text_styles, get_section_header_styles):
    """
    Render the Companies & Flows page.
    
    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_card_styles: Function to get card styles
        get_theme_text_styles: Function to get theme text styles
        get_section_header_styles: Function to get section header styles
    """
    st.markdown(
        get_card_styles() + get_theme_text_styles() + get_section_header_styles(),
        unsafe_allow_html=True,
    )

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
            companies = client.get_companies_with_flows()
            st.session_state.companies = companies

    if "companies" in st.session_state and st.session_state.companies:
        st.success(
            t("messages.company_flow_found").replace(
                "{count}", str(len(st.session_state.companies))
            )
        )

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
