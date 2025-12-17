"""
Settings Page
Configure API settings and authentication.
"""

import streamlit as st
import time


def render_settings_page(client, t, get_page_header_slate, get_card_styles):
    """
    Render the Settings page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_slate: Function to get slate header styles
        get_card_styles: Function to get card styles
    """
    st.markdown(get_page_header_slate(), unsafe_allow_html=True)

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

    st.markdown(get_card_styles(), unsafe_allow_html=True)

    st.markdown(
        f'<div class="section-header"><span class="section-icon">🔐</span> {t("settings_page.api_config")}</div>',
        unsafe_allow_html=True,
    )

    current_key = client.api_key
    st.write("**Current API Key:**")
    if current_key:
        masked_key = f"{current_key[:8]}{'•' * 16}{current_key[-4:]}"
        st.code(masked_key, language="text")
    else:
        st.code("Not set", language="text")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header"><span class="section-icon">🔑</span> Update API Key</div>',
        unsafe_allow_html=True,
    )

    new_api_key = st.text_input(
        "Enter API Key",
        value="",
        type="password",
        placeholder="Paste your Flowwer API key",
        key="settings_api_key",
    )
    if st.button(" Save API Key", type="primary", key="btn_save_api_key"):
        if not new_api_key:
            st.warning("Please enter a valid API key.")
        else:
          
            st.markdown("""
                <style>
                    .stSpinner > div {
                        border-color: #6366f1 !important;
                        border-top-color: transparent !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            with st.spinner("🔐 Verifying your API key with Flowwer..."):
                time.sleep(0.3)  
                is_valid, message = client.verify_api_key(new_api_key.strip())
            
            if is_valid:
                st.session_state.client.api_key = new_api_key.strip()
                st.session_state.client.session.headers.update(
                    {"X-FLOWWER-ApiKey": new_api_key.strip()}
                )
                st.success(message)
                st.balloons() 
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
                st.info("💡 **Tip:** Make sure you're using the correct API key from your Flowwer account.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### API Information")
    st.write("**Base URL:**", client.base_url)
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
