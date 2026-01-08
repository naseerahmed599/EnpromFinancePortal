"""
Signable Documents (Pending Approvals) Page Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json


def normalize_dict(obj):
    """
    Normalize an object to ensure it's a dictionary.
    Handles cases where the API returns JSON strings instead of parsed objects.
    """
    if isinstance(obj, dict):
        return obj
    elif isinstance(obj, str):
        try:
            return json.loads(obj)
        except (json.JSONDecodeError, ValueError):
            return {"raw": obj}
    else:
        return {"raw": str(obj)}


def render_signable_docs_page(
    client, t, get_page_header_amber, get_action_bar_styles, to_excel
):
    """
    Render the Signable Documents page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_amber: Function to get amber header styles
        get_action_bar_styles: Function to get action bar styles
        to_excel: Function to convert DataFrame to Excel
    """
    st.markdown(get_page_header_amber(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

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
                all_docs_cache = st.session_state.get("documents")
                docs = None

                if all_docs_cache and not backup_list:

                    signable_stages = [f"Stage{i}" for i in range(1, 6)]
                    docs = [
                        d
                        for d in all_docs_cache
                        if d.get("currentStage") in signable_stages
                    ]
                else:

                    try:
                        docs = client.get_signable_documents(
                            backup_list=backup_list, use_filter_method=False
                        )
                    except:
                        docs = client.get_signable_documents(
                            backup_list=backup_list, use_filter_method=True
                        )

                if docs is not None:
                    normalized_docs = []
                    for doc in docs:
                        normalized_doc = normalize_dict(doc)
                        if normalized_doc and isinstance(normalized_doc, dict):
                            normalized_docs.append(normalized_doc)
                    st.session_state.signable_documents = normalized_docs
                    if normalized_docs:
                        st.success(
                            f"{len(normalized_docs)} " + t("signable_docs_page.found")
                        )
                    else:
                        st.info(
                            "ℹ️ No signable documents found. The API returned an empty list."
                        )
                else:
                    st.error(
                        "Failed to retrieve signable documents. Please check the API connection."
                    )

    if "signable_documents" in st.session_state and st.session_state.signable_documents:
        docs = st.session_state.signable_documents

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

        date_columns = ["Invoice Date", "Upload Time"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime(
                    "%Y-%m-%d"
                )
                df[col] = df[col].fillna("")

        st.dataframe(df, use_container_width=True, height=500)

        st.markdown("---")
        st.subheader("  " + t("signable_docs_page.export"))

        col1, col2, col3 = st.columns(3)

        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label=t("common.download_csv"),
                data=csv,
                file_name=f"signable_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            excel_data = to_excel(df)
            st.download_button(
                label=t("common.download_excel"),
                data=excel_data,
                file_name=f"signable_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with col3:
            json_data = json.dumps(docs, indent=2)
            st.download_button(
                label=t("common.download_json"),
                data=json_data,
                file_name=f"signable_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
    else:
        st.info(" " + t("signable_docs_page.no_data"))
