"""
Settings Page
Configure API settings and authentication.
"""

import streamlit as st
import time


def render_settings_page(client, t, get_page_header_slate, get_action_bar_styles, get_card_styles):
    """
    Render the Settings page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_slate: Function to get slate header styles
        get_action_bar_styles: Function to get action bar styles
        get_card_styles: Function to get card styles
    """
    st.markdown(get_page_header_slate(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

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

    st.markdown(f"### {t('settings_page.api_config')}")
    st.caption("Manage your Flowwer API key for authentication")

    current_key = client.api_key
    with st.container():
        st.markdown(
            """
            <div class="card" style="
                margin-bottom: 1.5rem;
            ">
                <div style="
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: #64748b;
                    margin-bottom: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">Current API Key</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if current_key:
            masked_key = f"{current_key[:8]}{'•' * 16}{current_key[-4:]}"
            st.markdown(
                f"""
                <div style="
                    background: rgba(15, 23, 42, 0.05);
                    border: 1px solid rgba(71, 85, 105, 0.15);
                    border-radius: 8px;
                    padding: 0.875rem 1rem;
                    font-family: 'SF Mono', Monaco, monospace;
                    font-size: 0.9rem;
                    color: #1e293b;
                    margin-top: -1.25rem;
                    margin-left: 1.5rem;
                    margin-right: 1.5rem;
                    margin-bottom: 1.5rem;
                    word-break: break-all;
                ">{masked_key}</div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="
                    background: rgba(239, 68, 68, 0.08);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 8px;
                    padding: 0.875rem 1rem;
                    font-family: 'SF Mono', Monaco, monospace;
                    font-size: 0.9rem;
                    color: #dc2626;
                    margin-top: -1.25rem;
                    margin-left: 1.5rem;
                    margin-right: 1.5rem;
                    margin-bottom: 1.5rem;
                ">Not set</div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.markdown("### Update API Key")
    st.caption("Enter a new API key to authenticate with Flowwer")

    new_api_key = st.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="Paste your Flowwer API key here",
        key="settings_api_key",
        help="Your API key will be securely stored and used for all API requests",
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("Save API Key", type="primary", key="btn_save_api_key", use_container_width=True):
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
                
                with st.spinner("Verifying your API key with Flowwer..."):
                    time.sleep(0.3)
                    is_valid, message = client.verify_api_key(new_api_key.strip())
                
                if is_valid:
                    api_key_value = new_api_key.strip()
                    st.session_state.client.api_key = api_key_value
                    st.session_state.client.session.headers.update(
                        {"X-FLOWWER-ApiKey": api_key_value}
                    )
                    st.session_state.correct_api_key = api_key_value
                    st.success(message)
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
                    st.info("💡 **Tip:** Make sure you're using the correct API key from your Flowwer account.")

    st.divider()

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown(
            """
            <div class="card" style="
                padding: 1.5rem;
                height: 100%;
            ">
                <div style="
                    font-size: 1.125rem;
                    font-weight: 700;
                    color: #1e293b;
                    margin-bottom: 1rem;
                ">API Information</div>
                <div style="margin-bottom: 0.75rem;">
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 600;
                        color: #64748b;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 0.25rem;
                    ">Base URL</div>
                    <div style="
                        font-family: 'SF Mono', Monaco, monospace;
                        font-size: 0.875rem;
                        color: #334155;
                        word-break: break-all;
                    ">{base_url}</div>
                </div>
                <div>
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 600;
                        color: #64748b;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 0.25rem;
                    ">Documentation</div>
                    <a href="https://enprom-gmbh.flowwer.de/swagger" target="_blank" style="
                        font-family: 'SF Mono', Monaco, monospace;
                        font-size: 0.875rem;
                        color: #6366f1;
                        text-decoration: none;
                    ">View API Docs →</a>
                </div>
            </div>
            """.format(base_url=client.base_url),
            unsafe_allow_html=True,
        )

    with col_info2:
        documents_count = len(st.session_state.documents) if st.session_state.documents else 0
        selected_doc_id = (
            st.session_state.selected_document.get("documentId")
            if st.session_state.selected_document
            else "None"
        )
        
        st.markdown(
            f"""
            <div class="card" style="
                padding: 1.5rem;
                height: 100%;
            ">
                <div style="
                    font-size: 1.125rem;
                    font-weight: 700;
                    color: #1e293b;
                    margin-bottom: 1rem;
                ">Session Info</div>
                <div style="margin-bottom: 0.75rem;">
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 600;
                        color: #64748b;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 0.25rem;
                    ">Documents Loaded</div>
                    <div style="
                        font-family: 'SF Mono', Monaco, monospace;
                        font-size: 1.25rem;
                        font-weight: 700;
                        color: #334155;
                    ">{documents_count:,}</div>
                </div>
                <div>
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 600;
                        color: #64748b;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        margin-bottom: 0.25rem;
                    ">Selected Document</div>
                    <div style="
                        font-family: 'SF Mono', Monaco, monospace;
                        font-size: 0.875rem;
                        color: #334155;
                    ">{selected_doc_id}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
