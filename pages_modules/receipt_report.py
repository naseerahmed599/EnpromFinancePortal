"""
Receipt Splitting Report Page Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta
from utils.cost_center_parser import parse_cost_center, enrich_cost_center_data


def render_receipt_report_page(
    client, t, get_page_header_indigo, get_action_bar_styles, get_card_styles, to_excel
):
    """
    Render the Receipt Splitting Report page.

    Args:
        client: FlowwerAPIClient instance
        t: Translation function
        get_page_header_indigo: Function to get indigo header styles
        get_action_bar_styles: Function to get action bar styles
        get_card_styles: Function to get card styles
        to_excel: Function to convert DataFrame to Excel
    """
    st.markdown(get_page_header_indigo(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="page-header-indigo" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
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
            ">📑</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('receipt_report_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">{t('receipt_report_page.subtitle')}</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(get_card_styles(), unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {t('receipt_report_page.load_cost_centers')}")
        st.caption(t("receipt_report_page.fetch_cost_centers"))
        cc_months_back = st.selectbox(
            "Cost center lookback (months)",
            options=[3, 6, 12, 24],
            index=1,
            help="Quick filter: load cost centers from documents in the last N months.",
            key="cc_months_back",
        )
    with col2:
        if st.button(
            t("receipt_report_page.load_data"),
            use_container_width=True,
            key="btn_load_cost_centers_new",
        ):
            with st.spinner(t("receipt_report_page.loading")):
                if not client.api_key:
                    st.error("❌ API key not set! Please set your API key in Settings.")
                    st.stop()
                
                cost_centers = client.get_all_cost_centers(
                    months_back=int(cc_months_back)
                )
                if cost_centers:
                    cleaned_cc = [
                        str(cc)
                        for cc in cost_centers
                        if cc and str(cc).strip() not in ["", "None", "nan"]
                    ]
                    st.session_state.cost_centers = sorted(cleaned_cc)
                    
                    today = date.today()
                    start_date = (today - relativedelta(months=cc_months_back - 1)).replace(day=1)
                    end_date = today
                    
                    st.session_state.receipt_cc_sync_start = start_date
                    st.session_state.receipt_cc_sync_end = end_date
                    st.session_state.receipt_cc_sync_months = cc_months_back
                    
                    st.toast(
                        t("receipt_report_page.loaded_cost_centers").format(
                            count=len(st.session_state.cost_centers)
                        ),
                        icon="✅",
                    )

    st.divider()

    cost_center_list = st.session_state.get("cost_centers", [])

    st.markdown(f"### {t('receipt_report_page.report_filters')}")

    if cost_center_list:
        st.markdown(f"**{t('receipt_report_page.cost_centers_label')}**")

        col1, col2 = st.columns([2, 3])
        with col1:
            search_term = st.text_input(
                "Search",
                placeholder=t("receipt_report_page.search_placeholder"),
                help=t("receipt_report_page.search_help"),
            )
        with col2:
            if search_term:
                filtered_list = [
                    cc for cc in cost_center_list if str(cc).startswith(search_term)
                ]
                st.caption(
                    t("receipt_report_page.found_matching").format(
                        count=len(filtered_list)
                    )
                )
            else:
                filtered_list = cost_center_list
                st.caption(
                    t("receipt_report_page.available_count").format(
                        count=len(cost_center_list)
                    )
                )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        with col_btn1:
            if st.button(
                t("common.select_all"),
                key="receipt_select_all",
                use_container_width=True,
            ):
                st.session_state.receipt_cc_multiselect = (
                    filtered_list if search_term else cost_center_list
                )
                st.rerun()
        with col_btn2:
            if st.button(
                t("common.deselect_all"),
                key="receipt_deselect_all",
                use_container_width=True,
            ):
                st.session_state.receipt_cc_multiselect = []
                st.rerun()

        selected_cost_centers = st.multiselect(
            t("receipt_report_page.select_cost_centers"),
            options=filtered_list if search_term else cost_center_list,
            help=t("receipt_report_page.select_help"),
            key="receipt_cc_multiselect",
        )

        if selected_cost_centers:
            st.caption(
                t("receipt_report_page.selected_count").format(
                    count=len(selected_cost_centers)
                )
            )
    else:
        st.warning(t("receipt_report_page.load_first_warning"))
        selected_cost_centers = []

    st.markdown(f"**{t('receipt_report_page.date_range')}**")

    if (
        "receipt_cc_sync_start" in st.session_state
        and "receipt_cc_sync_end" in st.session_state
    ):
        sync_start = st.session_state.receipt_cc_sync_start
        sync_end = st.session_state.receipt_cc_sync_end
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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        from_month = st.selectbox(
            t("receipt_report_page.from_month"),
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=from_month_default,
            key="receipt_from_month",
        )
    with col2:
        from_year = st.selectbox(
            t("receipt_report_page.from_year"),
            options=list(range(2020, datetime.now().year + 1)),
            index=from_year_default,
            key="receipt_from_year",
        )
    with col3:
        to_month = st.selectbox(
            t("receipt_report_page.to_month"),
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=to_month_default,
            key="receipt_to_month",
        )
    with col4:
        to_year = st.selectbox(
            t("receipt_report_page.to_year"),
            options=list(range(2020, datetime.now().year + 1)),
            index=to_year_default,
            key="receipt_to_year",
        )

    min_date = date(from_year, from_month, 1)
    last_day = calendar.monthrange(to_year, to_month)[1]
    max_date = date(to_year, to_month, last_day)

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            t("receipt_report_page.generate_report"),
            type="primary",
            key="btn_generate_receipt_report",
            use_container_width=True,
        ):
            with st.spinner(t("receipt_report_page.fetching_data")):
                filter_params = {
                    "min_date": min_date.isoformat(),
                    "max_date": max_date.isoformat(),
                }

                report = client.get_receipt_splitting_report(**filter_params)

                if report:
                    st.session_state.full_receipt_report = report
                    total_records = len(report)

                    if selected_cost_centers and len(selected_cost_centers) > 0:
                        filtered_report = [
                            r
                            for r in report
                            if str(r.get("costCenter", "")) in selected_cost_centers
                        ]
                        st.session_state.receipt_report = filtered_report
                        st.session_state.filtered_cost_centers = selected_cost_centers
                        st.toast(
                            t("receipt_report_page.filtered_to").format(
                                filtered=len(filtered_report), total=total_records
                            ),
                            icon="✅",
                        )
                    else:
                        st.session_state.receipt_report = report
                        st.session_state.filtered_cost_centers = []
                        st.toast(
                            t("receipt_report_page.retrieved_records").format(
                                count=len(report)
                            ),
                            icon="✅",
                        )
                else:
                    st.toast(t("receipt_report_page.no_data_found"), icon="❌")

    if "receipt_report" in st.session_state and st.session_state.receipt_report:
        st.divider()
        st.markdown(f"### {t('receipt_report_page.report_results')}")

        report_data = st.session_state.receipt_report

        filtered_cc = st.session_state.get("filtered_cost_centers", [])
        if filtered_cc:
            st.info(
                t("receipt_report_page.filtered_by").replace(
                    "{count}", str(len(filtered_cc))
                )
            )
        else:
            st.info(t("receipt_report_page.showing_all"))

        df = pd.DataFrame(report_data)

        if "documentType" not in df.columns or df["documentType"].isna().any():
            doc_ids = df.get("documentId")
            if doc_ids is not None:
                unique_ids = [int(x) for x in pd.Series(doc_ids).dropna().unique()]
                type_cache = st.session_state.get("receipt_doc_type_cache", {})
                missing_ids = [i for i in unique_ids if i not in type_cache]
                if missing_ids:
                    with st.spinner("Fetching document types..."):
                        for doc_id in missing_ids:
                            try:
                                detail = client.get_document(int(doc_id))
                                dtype = ""
                                if detail:
                                    dtype = (
                                        detail.get("documentType")
                                        or detail.get("documenttype")
                                        or detail.get("documentKind")
                                        or detail.get("documentkind")
                                        or ""
                                    )
                                type_cache[doc_id] = dtype
                            except Exception:
                                type_cache[doc_id] = ""
                        st.session_state.receipt_doc_type_cache = type_cache
                df["documentType"] = df["documentId"].map(
                    st.session_state.get("receipt_doc_type_cache", {})
                )

        if "invoiceDate" in df.columns:
            df["invoiceDate"] = pd.to_datetime(
                df["invoiceDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        st.markdown(f"### {t('receipt_report_page.kpi_section_title')}")

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
            if col in df.columns:
                amount_col = col
                break

        cost_center_col = None
        for col in ["costCenter", "CostCenter", "cost_center"]:
            if col in df.columns:
                cost_center_col = col
                break

        if amount_col and cost_center_col:
            df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)
            num_cost_centers = df[cost_center_col].nunique()
            num_records = len(df)

            def classify_row(row):
                doc_type = str(
                    row.get("documentType")
                    or row.get("documenttype")
                    or row.get("documentKind")
                    or row.get("documentkind")
                    or ""
                ).lower()
                amount = row[amount_col]
                if (
                    "ausgangsrechnung" in doc_type
                    or "outgoinginvoice" in doc_type
                    or "ausgang" in doc_type
                ):
                    return "income"
                if (
                    "eingangsrechnung" in doc_type
                    or "incominginvoice" in doc_type
                    or "eingang" in doc_type
                ):
                    return "cost"
                return "income" if amount < 0 else "cost"

            df["__category"] = df.apply(classify_row, axis=1)

            income_total = df.loc[df["__category"] == "income", amount_col].abs().sum()
            cost_total = df.loc[df["__category"] == "cost", amount_col].abs().sum()

            net_total = df[amount_col].sum()
            margin = income_total - cost_total
            avg_amount = cost_total / num_cost_centers if num_cost_centers > 0 else 0

            st.markdown(
                """
                <style>
                    .kpi-cards-row {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                    }
                    .kpi-card {
                        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        padding: 1.25rem;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
                        transition: all 0.2s ease;
                    }
                    .kpi-card:hover {
                        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
                        transform: translateY(-2px);
                    }
                    @media (prefers-color-scheme: dark) {
                        .kpi-card {
                            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.6) 100%);
                            border-color: rgba(71, 85, 105, 0.5);
                        }
                    }
                    .kpi-label {
                        font-size: 0.875rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        color: #64748b;
                        margin-bottom: 0.5rem;
                    }
                    @media (prefers-color-scheme: dark) {
                        .kpi-label { color: #94a3b8; }
                    }
                    .kpi-value {
                        font-size: 2.5rem !important;
                        font-weight: 900;
                        color: #1e293b;
                        margin-bottom: 0.75rem;
                        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        white-space: nowrap;
                    }
                    @media (prefers-color-scheme: dark) {
                        .kpi-value { color: #f1f5f9; }
                    }
                    .kpi-card.primary {
                        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                        border-color: transparent;
                    }
                    .kpi-card.primary .kpi-label {
                        color: rgba(255, 255, 255, 0.85);
                    }
                    .kpi-card.primary .kpi-value {
                        color: #ffffff;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            def color_value(val):
                color = "#dc2626" if val < 0 else "#16a34a"
                return f'<span style="color:{color}">{val:,.2f} €</span>'

            kpi_html = f"""
                <div class="kpi-cards-row">
                    <div class="kpi-card primary">
                        <p class="kpi-label">Margin (Income - Cost)</p>
                        <p class="kpi-value"><strong><span style="color:#ffffff">{margin:,.2f} €</span></strong></p>
                    </div>
                    <div class="kpi-card">
                        <p class="kpi-label">Total Income (Debs)</p>
                        <p class="kpi-value">{color_value(income_total)}</p>
                    </div>
                    <div class="kpi-card">
                        <p class="kpi-label">Total Cost (Kreds)</p>
                        <p class="kpi-value">{color_value(cost_total)}</p>
                    </div>
                    <div class="kpi-card">
                        <p class="kpi-label">{t('receipt_report_page.num_cost_centers')}</p>
                        <p class="kpi-value">{num_cost_centers:,}</p>
                    </div>
                </div>
            """

            st.markdown(kpi_html, unsafe_allow_html=True)

            enriched_df = df.copy()
            enriched_df["cc_parsed"] = enriched_df[cost_center_col].apply(
                parse_cost_center
            )
            enriched_df["cc_display"] = enriched_df["cc_parsed"].apply(
                lambda x: x["display_name"]
            )
            enriched_df["cc_number"] = enriched_df[cost_center_col].astype(str)

            cc_stats = []
            for (cc_num, cc_name), sub in enriched_df.groupby(
                ["cc_number", "cc_display"]
            ):
                income_sum = (
                    sub.loc[sub["__category"] == "income", amount_col].abs().sum()
                )
                cost_sum = sub.loc[sub["__category"] == "cost", amount_col].abs().sum()
                margin_cc = income_sum - cost_sum
                cc_stats.append(
                    {
                        "cc_number": cc_num,
                        "cc_display": cc_name,
                        "income": income_sum,
                        "cost": cost_sum,
                        "margin": margin_cc,
                    }
                )
            cc_breakdown = pd.DataFrame(cc_stats)
            cc_breakdown = cc_breakdown.sort_values("margin", ascending=False)

            col_split_header1, col_split_header2 = st.columns([4, 1])
            with col_split_header1:
                st.markdown(f"**{t('receipt_report_page.cost_center_split')}:**")
            with col_split_header2:
                st.markdown(
                    f"""
                    <div style="text-align: right; padding-top: 2px;">
                        <span style="
                            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                            color: white;
                            padding: 4px 10px;
                            border-radius: 6px;
                            font-size: 0.75rem;
                            font-weight: 600;
                            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
                        " title="Total margin across selected cost centers">
                            💰 Total Margin: {margin:,.2f} €
                        </span>
                    </div>
                    """,
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
                        .cc-table-row td:last-child {
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
                        .cc-table-footer td:last-child {
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
            total_label = t("receipt_report_page.total")
            total_income_fmt = f"{income_total:,.2f} €"
            total_cost_fmt = f"{cost_total:,.2f} €"
            total_margin_fmt = f"{margin:,.2f} €"

            table_html = f"""
                <div class="cc-table-wrapper">
                  <div class="cc-table-scroll">
                    <table class="cc-table">
                      <thead class="cc-table-header">
                        <tr>
                          <th>Cost Center</th><th>Description</th><th style="text-align:right;">Income</th><th style="text-align:right;">Cost</th><th style="text-align:right;">Margin</th>
                        </tr>
                      </thead>
                      <tbody>{rows_html_str}</tbody>
                      <tfoot class="cc-table-footer">
                        <tr><td colspan="2">{total_label}</td><td style="text-align:right;">{total_income_fmt}</td><td style="text-align:right;">{total_cost_fmt}</td><td style="text-align:right;">{total_margin_fmt}</td></tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
            """

            st.markdown(table_html, unsafe_allow_html=True)
            st.divider()

        st.dataframe(df, use_container_width=True, height=500)

        st.divider()
        st.markdown(f"### {t('receipt_report_page.export_data')}")

        col1, col2 = st.columns(2)

        with col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label=t("common.download_csv"),
                data=csv_data,
                file_name=f"receipt_splitting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            excel_data = to_excel(df)
            st.download_button(
                label=t("common.download_excel"),
                data=excel_data,
                file_name=f"receipt_splitting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    else:
        st.info(t("receipt_report_page.no_report_data"))
