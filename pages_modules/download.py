"""
Download Document Page Module
"""

import streamlit as st
import base64
import os


def render_download_page(
    client, t, get_page_header_cyan, get_action_bar_styles, get_info_box_styles
):
    """
    Render the Download Document page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_cyan: Function to get cyan header styles
        get_action_bar_styles: Function to get action bar styles
        get_info_box_styles: Function to get info box styles
    """
    st.markdown(get_page_header_cyan(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

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

    st.markdown(get_info_box_styles(), unsafe_allow_html=True)

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

    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    if "viewed_document_id" not in st.session_state:
        st.session_state.viewed_document_id = None
    if "viewed_document_path" not in st.session_state:
        st.session_state.viewed_document_path = None

    col1, col2 = st.columns(2)
    
    with col1:
        get_details_button = st.button(
            "🔍 Get Document Details (to find Unique ID)", 
            type="secondary", 
            key="btn_get_download_details",
            use_container_width=True
        )
    
    with col2:
        view_button = st.button(
            "👁️ View Document", 
            type="primary", 
            key="btn_view_pdf",
            disabled=not unique_id,
            use_container_width=True
        )

    if get_details_button:
        with st.spinner(f"Fetching document {download_doc_id}..."):
            doc = client.get_document(download_doc_id)
            if doc:
                st.success(t("messages.document_found"))
                st.write("**Unique ID:**")
                st.code(doc.get("uniqueId"), language="text")
                st.write("**Document Name:**", doc.get("simpleName"))

    if unique_id and view_button:
        output_path = f"document_{download_doc_id}.pdf"
        with st.spinner(
            f"Loading document {download_doc_id} for viewing..."
        ):
            success = client.download_document(download_doc_id, unique_id, output_path)
            if success:
                st.session_state.viewed_document_id = download_doc_id
                st.session_state.viewed_document_path = output_path
                st.success(f"✅ Document {download_doc_id} loaded successfully")
            else:
                st.error("❌ " + t("messages.download_failed"))
                st.session_state.viewed_document_id = None
                st.session_state.viewed_document_path = None

    if (st.session_state.viewed_document_path and 
        os.path.exists(st.session_state.viewed_document_path) and
        st.session_state.viewed_document_id == download_doc_id):
        st.markdown("---")
        st.markdown("### 📄 Document Preview")
        
        try:
            with open(st.session_state.viewed_document_path, "rb") as f:
                pdf_bytes = f.read()
                base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                
                pdf_display = f"""
                <iframe 
                    src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" 
                    height="800px" 
                    style="border: 1px solid #e0e0e0; border-radius: 8px;"
                    type="application/pdf">
                </iframe>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                with open(st.session_state.viewed_document_path, "rb") as f:
                    pdf_data = f.read()
                    st.download_button(
                        label="💾 Download to Computer",
                        data=pdf_data,
                        file_name=st.session_state.viewed_document_path,
                        mime="application/pdf",
                        use_container_width=True,
                    )
        except Exception as e:
            st.error(
                t("messages.error_reading_file").replace("{error}", str(e))
            )

