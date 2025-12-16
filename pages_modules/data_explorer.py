"""
Data Explorer Page Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render_data_explorer_page(
    client,
    t,
    get_page_header_teal,
    get_export_bar_styles,
    get_card_styles,
    get_action_bar_styles,
    to_excel,
):
    """
    Render the Data Explorer page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_teal: Function to get teal header styles
        get_export_bar_styles: Function to get export bar styles
        get_card_styles: Function to get card styles
        get_action_bar_styles: Function to get action bar styles
        to_excel: Function to convert DataFrame to Excel
    """
    st.markdown(get_page_header_teal(), unsafe_allow_html=True)
    st.markdown(get_export_bar_styles(), unsafe_allow_html=True)

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

    st.markdown(get_card_styles(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header"><span class="section-icon">1️⃣</span> Load Data</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        include_processed = st.checkbox(
            t("data_explorer_page.include_processed"),
            value=True,
            key="explorer_processed",
        )
    with col2:
        include_deleted = st.checkbox(
            t("data_explorer_page.include_deleted"), value=False, key="explorer_deleted"
        )
    with col3:
        if st.button(
            t("data_explorer_page.load_all_documents"),
            type="primary",
            use_container_width=True,
            key="btn_load_explorer_docs",
        ):
            with st.spinner(t("data_explorer_page.loading")):
                docs = client.get_all_documents(
                    include_processed=include_processed, include_deleted=include_deleted
                )

                if docs:
                    all_data = []
                    progress_bar = st.progress(0)

                    for idx, doc in enumerate(docs):
                        doc_id = doc.get("documentId")
                        if doc_id is None:
                            continue

                        splits = client.get_receipt_splits(doc_id)

                        if splits and len(splits) > 0:
                            
                            for split in splits:
                                merged_data = {
                                    "Document ID": doc_id,
                                    "Display Name": doc.get("simpleName", ""),
                                    "Booking Text": split.get("name", ""),
                                    "Cost Center": split.get("costCenter", ""),
                                    "Cost Unit (KOST2)": (
                                        split.get("costUnit")
                                        or split.get("costunit")
                                        or split.get("CostUnit")
                                        or split.get("cost_unit")
                                        or split.get("kost2")
                                        or split.get("KOST2")
                                        or split.get("Kost2")
                                        or split.get("costUnit2")
                                        or ""
                                    ),
                                    "Tax Rate %": split.get("taxPercent", ""),
                                    "Invoice Date": split.get(
                                        "invoiceDate", doc.get("invoiceDate", "")
                                    ),
                                    "Receipt Number": doc.get(
                                        "invoiceNumber", doc.get("receiptNumber", "")
                                    ),
                                    "Gross": split.get(
                                        "grossValue"
                                    ) or split.get("grossAmount") or doc.get("totalGross", ""),
                                    "Net": split.get(
                                        "netValue"
                                    ) or split.get("netAmount") or doc.get("totalNet", ""),
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
                                    "Flow": doc.get("flowName", ""),
                                    "Approval Status": split.get(
                                        "currentStage", doc.get("currentStage", "")
                                    ),
                                    "Stage Timestamp": doc.get("stageTimestamp", ""),
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
                            merged_data = {
                                "Document ID": doc_id,
                                "Display Name": doc.get("simpleName", ""),
                                "Booking Text": "",
                                "Cost Center": "",
                                "Cost Unit (KOST2)": "",
                                "Tax Rate %": "",
                                "Invoice Date": doc.get("invoiceDate", ""),
                                "Receipt Number": doc.get(
                                    "invoiceNumber", doc.get("receiptNumber", "")
                                ),
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
                                "Currency": doc.get("currencyCode", ""),
                                "Due Date": doc.get("dueDate", ""),
                                "Discount Amount": doc.get("discountAmount", ""),
                                "Discount End Period": doc.get("discountPeriodEnd", ""),
                                "Payment State": doc.get("paymentState", ""),
                                "Payment Date": doc.get("paymentDate", ""),
                                "Payment Method": doc.get("paymentMethod", ""),
                                "Dunned": doc.get("isDunning", ""),
                                "On Hold": doc.get("isOnHold", ""),
                                "Flow": doc.get("flowName", ""),
                                "Approval Status": doc.get("currentStage", ""),
                                "Stage Timestamp": doc.get("stageTimestamp", ""),
                                "Supplier Name": doc.get("supplierName", ""),
                                "Supplier VAT ID": doc.get("supplierVATId", ""),
                                "Service Date Start": doc.get("serviceStartDate", ""),
                                "Service Date End": doc.get("serviceEndDate", ""),
                                "File Name": doc.get("simpleName", ""),
                                "Creation": doc.get("creationTimestampUtc", ""),
                                "File Size": doc.get("fileSize", ""),
                            }
                            all_data.append(merged_data)

                        progress_bar.progress((idx + 1) / len(docs))

                    df_export = pd.DataFrame(all_data)

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
                            df_export[col] = pd.to_datetime(
                                df_export[col], errors="coerce"
                            ).dt.strftime("%Y-%m-%d")
                            df_export[col] = df_export[col].fillna("")

                    st.session_state.explorer_data = df_export
                    st.success(
                        f"Loaded {len(all_data)} rows from {len(docs)} documents"
                    )
                else:
                    st.error("Failed to load documents")

    if (
        "explorer_data" in st.session_state
        and st.session_state.explorer_data is not None
    ):
        df = st.session_state.explorer_data

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 2️⃣ {t('common.select_columns')}")

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

        if "selected_columns" not in st.session_state:
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

        with st.expander("📋 Column Selection (Click to expand)", expanded=False):

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(t("common.select_all"), key="btn_select_all"):
                    st.session_state.selected_columns = list(df.columns)
                    for col_name in df.columns:
                        st.session_state[f"col_{col_name}"] = True
                    st.rerun()
            with col2:
                if st.button(t("common.deselect_all"), key="btn_deselect_all"):
                    st.session_state.selected_columns = []
                    for col_name in df.columns:
                        st.session_state[f"col_{col_name}"] = False
                    st.rerun()
            with col3:
                if st.button(t("common.reset_to_default"), key="btn_reset_default"):
                    default_columns = [
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
                    st.session_state.selected_columns = default_columns
                    for col_name in df.columns:
                        st.session_state[f"col_{col_name}"] = (
                            col_name in default_columns
                        )
                    st.rerun()

            st.markdown("---")

            for category, columns in column_categories.items():
                st.markdown(f"**{category}**")

                cols = st.columns(3)
                for idx, col_name in enumerate(columns):
                    with cols[idx % 3]:
                        if col_name in df.columns:
                            is_selected = col_name in st.session_state.selected_columns

                            checkbox_key = f"col_{col_name}"
                            if checkbox_key not in st.session_state:
                                st.session_state[checkbox_key] = is_selected

                            new_value = st.checkbox(
                                col_name,
                                value=st.session_state[checkbox_key],
                                key=checkbox_key,
                            )

                            if (
                                new_value
                                and col_name not in st.session_state.selected_columns
                            ):
                                st.session_state.selected_columns.append(col_name)
                            elif (
                                not new_value
                                and col_name in st.session_state.selected_columns
                            ):
                                st.session_state.selected_columns.remove(col_name)

                st.markdown("")  

        st.info(
            f"📊 Selected {len(st.session_state.selected_columns)} of {len(df.columns)} columns"
        )

        st.markdown("---")
        st.markdown(
            f'<div class="section-header"><span class="section-icon">3️⃣</span> {t("common.view_export_data")}</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.selected_columns:
            display_df = df[st.session_state.selected_columns]

            st.write(f"**{t('common.total_rows')}:** {len(display_df)}")

            st.dataframe(display_df, use_container_width=True, height=500)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header"><span class="section-icon">📦</span> Export Options</div>',
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                csv_data = display_df.to_csv(index=False)
                st.download_button(
                    label=t("common.download_csv"),
                    data=csv_data,
                    file_name=f"flowwer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                excel_data = to_excel(display_df)
                st.download_button(
                    label=t("common.download_excel"),
                    data=excel_data,
                    file_name=f"flowwer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            with col3:
                json_data = display_df.to_json(orient="records", indent=2)
                st.download_button(
                    label=t("common.download_json"),
                    data=json_data,
                    file_name=f"flowwer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
        else:
            st.warning("⚠️ " + t("messages.please_select_column"))
    else:
        st.info(" " + t("messages.click_load_documents"))
