"""
Approved Documents Page Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json


def render_approved_docs_page(
    client, t, get_page_header_green, get_action_bar_styles, to_excel
):
    """
    Render the Approved Documents page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_green: Function to get green header styles
        get_action_bar_styles: Function to get action bar styles
        to_excel: Function to convert DataFrame to Excel
    """
    st.markdown(get_page_header_green(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

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

    col1, col2 = st.columns([3, 1])

    with col1:
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
                docs = client.get_approved_documents(flow_id=selected_flow_id)
                if docs:
                    st.session_state.approved_documents = docs
                    st.success(f"{len(docs)} " + t("approved_docs_page.found"))

    if "approved_documents" in st.session_state and st.session_state.approved_documents:
        docs = st.session_state.approved_documents

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

        if "Invoice Date" in df.columns:
            df["Invoice Date"] = pd.to_datetime(
                df["Invoice Date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            df["Invoice Date"] = df["Invoice Date"].fillna("")

        st.dataframe(df, use_container_width=True, height=500)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 💾 {t('common.export_options')}")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label=t("common.download_csv"),
                data=csv,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            excel_data = to_excel(df)
            st.download_button(
                label=t("common.download_excel"),
                data=excel_data,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with col2:
            json_data = json.dumps(docs, indent=2)
            st.download_button(
                label="  " + t("common.download_json"),
                data=json_data,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
            )
    else:
        st.info(" " + t("approved_docs_page.no_data"))
