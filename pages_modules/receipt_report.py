"""
Receipt Splitting Report Page Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
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
    with col2:
        if st.button(
            t("receipt_report_page.load_data"),
            use_container_width=True,
            key="btn_load_cost_centers_new",
        ):
            with st.spinner(t("receipt_report_page.loading")):
                cost_centers = client.get_all_cost_centers()
                if cost_centers:
                    cleaned_cc = [
                        str(cc)
                        for cc in cost_centers
                        if cc and str(cc).strip() not in ["", "None", "nan"]
                    ]
                    st.session_state.cost_centers = sorted(cleaned_cc)
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
            if st.button(t("common.select_all"), key="receipt_select_all", use_container_width=True):
                st.session_state.receipt_cc_multiselect = filtered_list if search_term else cost_center_list
                st.rerun()
        with col_btn2:
            if st.button(t("common.deselect_all"), key="receipt_deselect_all", use_container_width=True):
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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        from_month = st.selectbox(
            t("receipt_report_page.from_month"),
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=0,
        )
    with col2:
        from_year = st.selectbox(
            t("receipt_report_page.from_year"),
            options=list(range(2020, datetime.now().year + 1)),
            index=3,
        )
    with col3:
        to_month = st.selectbox(
            t("receipt_report_page.to_month"),
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=datetime.now().month - 1,
        )
    with col4:
        to_year = st.selectbox(
            t("receipt_report_page.to_year"),
            options=list(range(2020, datetime.now().year + 1)),
            index=len(list(range(2020, datetime.now().year + 1))) - 1,
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
            total_amount = df[amount_col].sum()

            num_cost_centers = df[cost_center_col].nunique()
            num_records = len(df)
            avg_amount = total_amount / num_cost_centers if num_cost_centers > 0 else 0

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
                        font-size: 0.75rem;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                        color: #64748b;
                        margin: 0 0 0.5rem 0;
                    }
                    @media (prefers-color-scheme: dark) {
                        .kpi-label { color: #94a3b8; }
                    }
                    .kpi-value {
                        font-size: 2rem !important;
                        font-weight: 700;
                        color: #1e293b;
                        margin: 0;
                        font-family: 'SF Mono', Monaco, monospace;
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

            kpi_html = f"""
                <div class="kpi-cards-row">
                    <div class="kpi-card primary">
                        <p class="kpi-label">{t('receipt_report_page.total_amount_label')}</p>
                        <p class="kpi-value">{total_amount:,.2f} €</p>
                    </div>
                    <div class="kpi-card">
                        <p class="kpi-label">{t('receipt_report_page.total_records')}</p>
                        <p class="kpi-value">{num_records:,}</p>
                    </div>
                    <div class="kpi-card">
                        <p class="kpi-label">{t('receipt_report_page.num_cost_centers')}</p>
                        <p class="kpi-value">{num_cost_centers:,}</p>
                    </div>
                    <div class="kpi-card">
                        <p class="kpi-label">{t('receipt_report_page.avg_per_cc')}</p>
                        <p class="kpi-value">{avg_amount:,.0f} €</p>
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

            cc_breakdown = (
                enriched_df.groupby(["cc_number", "cc_display"])[amount_col]
                .sum()
                .reset_index()
            )
            cc_breakdown = cc_breakdown.sort_values(amount_col, ascending=False)

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
                        " title="Total amount split across all cost centers">
                            💰 Total: {total_amount:,.2f} €
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
                    .cc-table-header th:last-child {
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
                    .cc-table-row td:last-child {
                        text-align: right;
                        font-weight: 600;
                        color: #4338ca;
                        font-family: 'SF Mono', Monaco, monospace;
                        width: 20%;
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
                    .cc-table-footer td:last-child {
                        text-align: right;
                        color: #6366f1;
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
                amt = row[amount_col]
                amt_formatted = f"{amt:,.2f} €"
                rows_html.append(
                    f'<tr class="cc-table-row"><td>{cc_num}</td><td>{cc_name}</td><td>{amt_formatted}</td></tr>'
                )

            rows_html_str = "".join(rows_html)
            total_label = t("receipt_report_page.total")
            total_formatted = f"{total_amount:,.2f} €"
            cost_center_header = t("receipt_report_page.cost_center_column")
            amount_header = t("receipt_report_page.amount_column")

            table_html = f'<div class="cc-table-wrapper"><div class="cc-table-scroll"><table class="cc-table"><thead class="cc-table-header"><tr><th>Cost Center</th><th>Description</th><th>{amount_header}</th></tr></thead><tbody>{rows_html_str}</tbody><tfoot class="cc-table-footer"><tr><td colspan="2">{total_label}</td><td>{total_formatted}</td></tr></tfoot></table></div></div>'

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
