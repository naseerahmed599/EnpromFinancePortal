"""
Upload Document Page Module
"""

import streamlit as st
import os


def render_upload_page(client, t, get_page_header_rose, get_alert_box_styles):
    """
    Render the Upload Document page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_rose: Function to get rose header styles
        get_alert_box_styles: Function to get alert box styles
    """
    st.markdown(get_page_header_rose(), unsafe_allow_html=True)

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

    st.markdown(get_alert_box_styles(), unsafe_allow_html=True)

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
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Uploading document..."):
            result = client.upload_document(
                temp_path,
                flow_id=flow_id if flow_id > 0 else None,
                company_id=company_id if company_id > 0 else None,
                filename=custom_filename if custom_filename else None,
            )

            if result:
                st.success(t("messages.document_uploaded"))
                st.write("**Document ID:**", result.get("elementId"))
                st.write("**Name:**", result.get("name"))
            else:
                st.error("❌ " + t("upload_page.failed"))

        try:
            os.remove(temp_path)
        except:
            pass
