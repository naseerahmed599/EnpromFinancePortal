"""
All Documents Page Module
Browse and manage all documents with comprehensive filtering and statistics
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json


def render_all_documents_page(client, t, get_all_document_page_styles, to_excel):
    """Render the All Documents page with filtering and statistics"""

    st.markdown(get_all_document_page_styles(), unsafe_allow_html=True)

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
            t("all_documents_page.refresh"),
            type="primary",
            use_container_width=True,
            key="btn_refresh_all_docs",
        ):
            with st.spinner(t("all_documents_page.loading")):
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed, include_deleted=include_deleted
                )
                st.session_state.documents = docs
                if docs:
                    st.success(
                        t("messages.successfully_loaded_docs").replace(
                            "{count}", str(len(docs))
                        )
                    )
                else:
                    st.warning("No documents found")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.documents:
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

        st.markdown(
            f"""
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                {t('all_docs_metrics.key_performance_metrics')}
            </h3>
        """,
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(5)

        approved_count = stage_counts.get("Approved", 0)
        pending_count = sum(stage_counts.get(f"Stage{i}", 0) for i in range(1, 6))
        unstarted_count = stage_counts.get("Draft", 0)
        approval_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0

        key_metrics = [
            (
                t("all_docs_metrics.total_documents"),
                len(docs),
                "📊",
                "#3b82f6",
                "rgba(59, 130, 246, 0.04)",
            ),
            (
                t("all_docs_metrics.total_value"),
                f"€{total_gross:,.0f}",
                "💰",
                "#10b981",
                "rgba(16, 185, 129, 0.04)",
            ),
            (
                t("all_docs_metrics.approved"),
                approved_count,
                "✅",
                "#22c55e",
                "rgba(34, 197, 94, 0.04)",
            ),
            (
                t("all_docs_metrics.in_workflow"),
                pending_count,
                "⏳",
                "#f59e0b",
                "rgba(245, 158, 11, 0.04)",
            ),
            (
                t("all_docs_metrics.unstarted"),
                unstarted_count,
                "📝",
                "#8b5cf6",
                "rgba(139, 92, 246, 0.04)",
            ),
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
                                    {t('all_docs_metrics.in_processing_workflow')}
                                </h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                                {t('all_docs_metrics.documents_in_approval').replace('{count}', f'<strong>{pending_count}</strong>')}
                            </p>
                            <p class="subtitle" style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                {t('all_docs_metrics.in_workflow_stages')}
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
                                    {t('all_docs_metrics.unstarted_documents')}
                                </h4>
                            </div>
                            <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                                {t('all_docs_metrics.documents_not_started').replace('{count}', f'<strong>{unstarted_count}</strong>')}
                            </p>
                            <p class="subtitle" style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                {t('all_docs_metrics.require_initial_processing')}
                            </p>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        st.markdown(
            f"""
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2.5rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                {t('all_docs_metrics.financial_summary')}
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
                        {t('all_docs_metrics.total_gross')}
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
                        {t('all_docs_metrics.total_net')}
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
                        {t('all_docs_metrics.total_tax')}
                    </div>
                    <div style="font-size: 2.25rem; font-weight: 900; color: #ef4444; word-wrap: break-word; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        €{tax_amount:,.2f}
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2.5rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                {t('all_docs_metrics.payment_status_overview')}
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
            bg_dark = bg.replace("0.04", "0.15") 
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

        with st.expander(t("all_docs_metrics.advanced_filters"), expanded=True):

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
                    t("all_docs_metrics.company"),
                    [t("all_docs_metrics.all")] + sorted(companies),
                    help=t("all_docs_metrics.filter_by_company_help"),
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
                    t("all_docs_metrics.stage"),
                    [t("all_docs_metrics.all")] + sorted(stages),
                    help=t("all_docs_metrics.filter_by_stage_help"),
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
                    t("all_docs_metrics.payment_state"),
                    [t("all_docs_metrics.all")] + sorted(payment_states),
                    help=t("all_docs_metrics.filter_by_payment_help"),
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
                    t("all_docs_metrics.supplier"),
                    [t("all_docs_metrics.all")] + sorted(suppliers),
                    help=t("all_docs_metrics.filter_by_supplier_help"),
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
                    t("all_docs_metrics.currency"),
                    [t("all_docs_metrics.all")] + sorted(currencies),
                    help=t("all_docs_metrics.filter_by_currency_help"),
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
                    t("all_docs_metrics.flow"),
                    [t("all_docs_metrics.all")] + sorted(flows),
                    help=t("all_docs_metrics.filter_by_flow_help"),
                )

            st.markdown("<br>", unsafe_allow_html=True)

            col7, col8, col9 = st.columns(3)

            with col7:
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
                                t("all_docs_metrics.invoice_date_from"),
                                value=None,
                                min_value=min_doc_date,
                                max_value=max_doc_date,
                                help=t("all_docs_metrics.filter_by_date_from_help"),
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
                                t("all_docs_metrics.invoice_date_to"),
                                value=None,
                                min_value=min_doc_date,
                                max_value=max_doc_date,
                                help=t("all_docs_metrics.filter_by_date_to_help"),
                            )
                        else:
                            date_to = None
                    except:
                        date_to = None
                else:
                    date_to = None

            with col9:
                gross_values = [
                    doc.get("totalGross", 0) for doc in st.session_state.documents
                ]
                if gross_values:
                    max_value = max(gross_values)
                    value_threshold = st.number_input(
                        t("all_docs_metrics.min_value"),
                        min_value=0.0,
                        max_value=float(max_value),
                        value=0.0,
                        step=100.0,
                        help=t("all_docs_metrics.filter_by_value_help"),
                    )
                else:
                    value_threshold = 0.0

        filtered_docs = st.session_state.documents

        if selected_company != t("all_docs_metrics.all"):
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("companyName") == selected_company
            ]

        if selected_stage != t("all_docs_metrics.all"):
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("currentStage") == selected_stage
            ]

        if selected_payment != t("all_docs_metrics.all"):
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("paymentState") == selected_payment
            ]

        if selected_supplier != t("all_docs_metrics.all"):
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("supplierName") == selected_supplier
            ]

        if selected_currency != t("all_docs_metrics.all"):
            filtered_docs = [
                doc
                for doc in filtered_docs
                if doc.get("currencyCode") == selected_currency
            ]

        if selected_flow != t("all_docs_metrics.all"):
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

        if len(filtered_docs) != len(docs):
            showing_text = (
                t("all_docs_metrics.showing_of")
                .replace("{filtered}", str(len(filtered_docs)))
                .replace("{total}", str(len(docs)))
            )
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
                        {showing_text}
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

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

            st.markdown(f"#### {t('common.documents_table')}")

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

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"#### {t('common.export_options')}")

            col1, col2, col3 = st.columns(3)

            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label=t("common.download_csv"),
                    data=csv,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                excel_data = to_excel(df)
                st.download_button(
                    label=t("common.download_excel"),
                    data=excel_data,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            with col3:
                json_data = json.dumps(filtered_docs, indent=2)
                st.download_button(
                    label=t("common.download_json"),
                    data=json_data,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
