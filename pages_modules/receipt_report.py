"""
Receipt Splitting Report Page Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar


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
        st.markdown("### Load Cost Centers")
        st.caption("Fetch available cost centers from the system")
    with col2:
        if st.button(
            "Load Data",
            use_container_width=True,
            key="btn_load_cost_centers_new",
        ):
            with st.spinner("Loading..."):
                cost_centers = client.get_all_cost_centers()
                if cost_centers:
                    cleaned_cc = [
                        str(cc)
                        for cc in cost_centers
                        if cc and str(cc).strip() not in ["", "None", "nan"]
                    ]
                    st.session_state.cost_centers = sorted(cleaned_cc)
                    st.toast(
                        f"Loaded {len(st.session_state.cost_centers)} cost centers",
                        icon="✅",
                    )

    st.divider()

    cost_center_list = st.session_state.get("cost_centers", [])

    st.markdown("### Report Filters")

    if cost_center_list:
        st.markdown("**Cost Centers**")

        col1, col2 = st.columns([2, 3])
        with col1:
            search_term = st.text_input(
                "Search",
                placeholder="Filter cost centers...",
                help="Search to filter the dropdown",
            )
        with col2:
            if search_term:
                filtered_list = [
                    cc for cc in cost_center_list if str(cc).startswith(search_term)
                ]
                st.caption(f"Found {len(filtered_list)} matching")
            else:
                filtered_list = cost_center_list
                st.caption(f"{len(cost_center_list)} available")

        selected_cost_centers = st.multiselect(
            "Select Cost Centers",
            options=filtered_list if search_term else cost_center_list,
            help="Leave empty to include all cost centers",
        )

        if selected_cost_centers:
            st.caption(f"Selected: {len(selected_cost_centers)} cost center(s)")
    else:
        st.warning("Load cost centers first to enable filtering")

    st.markdown("**Date Range**")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        from_month = st.selectbox(
            "From Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=0,
        )
    with col2:
        from_year = st.selectbox(
            "From Year",
            options=list(range(2020, datetime.now().year + 1)),
            index=3, 
        )
    with col3:
        to_month = st.selectbox(
            "To Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=datetime.now().month - 1,
        )
    with col4:
        to_year = st.selectbox(
            "To Year",
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
            "Generate Report",
            type="primary",
            key="btn_generate_receipt_report",
            use_container_width=True,
        ):
            with st.spinner("Fetching data from API..."):
                filter_params = {
                    "min_date": min_date.isoformat(),
                    "max_date": max_date.isoformat(),
                }

                report = client.get_receipt_splitting_report(**filter_params)

                if report:
                    total_records = len(report)

                    if selected_cost_centers:
                        report = [
                            r
                            for r in report
                            if str(r.get("costCenter", "")) in selected_cost_centers
                        ]
                        st.session_state.receipt_report = report
                        st.session_state.filtered_cost_centers = selected_cost_centers
                        st.toast(
                            f"Filtered to {len(report):,} of {total_records:,} records",
                            icon="✅",
                        )
                    else:
                        st.session_state.receipt_report = report
                        st.session_state.filtered_cost_centers = []
                        st.toast(f"Retrieved {len(report):,} records", icon="✅")
                else:
                    st.toast("No data found", icon="❌")

    if "receipt_report" in st.session_state and st.session_state.receipt_report:
        st.divider()
        st.markdown("### Report Results")

        report_data = st.session_state.receipt_report

        filtered_cc = st.session_state.get("filtered_cost_centers", [])
        if filtered_cc:
            st.info(f"Filtered by {len(filtered_cc)} cost center(s)")
        else:
            st.info("Showing all cost centers")

        df = pd.DataFrame(report_data)

        if "invoiceDate" in df.columns:
            df["invoiceDate"] = pd.to_datetime(
                df["invoiceDate"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        st.metric("Total Records", f"{len(df):,}")

        st.dataframe(df, use_container_width=True, height=500)

        st.divider()
        st.markdown("### Export Data")

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
        st.info("No data to display. Generate a report first.")
