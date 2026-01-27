"""
Data Comparison Page Module
Cross-check data between DATEV Excel exports and Flowwer API
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px
import plotly.graph_objects as go


def render_data_comparison_page(
    client,
    t,
    get_page_header_indigo,
    get_action_bar_styles,
    to_excel,
    get_pln_eur_rate,
    IN_PRODUCTION,
):
    """Render the Data Comparison page for cross-checking DATEV and Flowwer data"""

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
                box-shadow: 0 8px 16px rgba(79, 70, 229, 0.25);
            ">
                📊
            </div>
            <div style="flex: 1;">
                <h1 style="margin: 0; font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    {t('data_comparison_page.title')}
                </h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.7; font-size: 1rem;">
                    {t('data_comparison_page.subtitle')}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.date_range')}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    current_year = datetime.now().year
    current_month = datetime.now().month

    with col1:
        from_month = st.selectbox(
            t("data_comparison_page.from_month"),
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=0,
            key="from_month",
        )

    with col2:
        from_year = st.selectbox(
            t("data_comparison_page.from_year"),
            options=list(range(2020, current_year + 1)),
            index=len(list(range(2020, current_year + 1))) - 2,
            key="from_year",
        )

    with col3:
        to_month = st.selectbox(
            t("data_comparison_page.to_month"),
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=11,
            key="to_month",
        )

    with col4:
        to_year = st.selectbox(
            t("data_comparison_page.to_year"),
            options=list(range(2020, current_year + 1)),
            index=len(list(range(2020, current_year + 1))) - 1,
            key="to_year",
        )

    from_date = datetime(from_year, from_month, 1)
    if to_month == 12:
        to_date = datetime(to_year, 12, 31)
    else:
        to_date = datetime(to_year, to_month + 1, 1) - timedelta(days=1)

    if from_date > to_date:
        st.error(t("data_comparison_page.invalid_date_range"))
        st.info(t("data_comparison_page.date_range_hint"))
        return
    
    date_range_days = (to_date - from_date).days + 1
    st.info(f"📅 Selected range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')} ({date_range_days} days)")

    with st.expander(t("data_comparison_page.advanced_settings"), expanded=False):
        search_lookahead_months = st.slider(
            t("data_comparison_page.search_lookahead"),
            min_value=0,
            max_value=12,
            value=4,
            help="Extends the API search range by X months.",
        )

    st.markdown(
        f"""
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.cc_filter_title')}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cost_center_list = st.session_state.get("comparison_cost_centers", [])

    if not cost_center_list:
        st.info(t("data_comparison_page.cc_filter_hint_text"))
        if st.button(
            t("data_comparison_page.load_cc_options_btn"),
            key="btn_load_cc_options",
            type="secondary",
        ):
            with st.spinner(t("data_comparison_page.loading_cc_spinner")):
                try:

                    cc_fetch_start = from_date
                    cc_fetch_end = to_date

                    cost_centers = client.get_cost_centers_for_range(
                        min_date=cc_fetch_start.isoformat(),
                        max_date=cc_fetch_end.isoformat(),
                    )

                    if cost_centers:
                        cleaned_cc = [
                            str(cc)
                            for cc in cost_centers
                            if cc and str(cc).strip() not in ["", "None", "nan"]
                        ]
                        st.session_state.comparison_cost_centers = sorted(cleaned_cc)
                        st.rerun()
                    else:
                        st.warning(t("data_comparison_page.no_cc_found"))
                except Exception as e:
                    st.error(f"Error loading cost centers: {e}")

    if cost_center_list:
        col1, col2 = st.columns([2, 3])
        with col1:
            search_term = st.text_input(
                t("data_comparison_page.search_cc"),
                placeholder=t("data_comparison_page.cc_placeholder"),
                key="cc_search_comparison",
            )
        with col2:
            if search_term:
                filtered_list = [
                    cc for cc in cost_center_list if str(cc).startswith(search_term)
                ]
            else:
                filtered_list = cost_center_list

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        with col_btn1:
            if st.button(
                t("data_comparison_page.select_all"),
                key="comparison_select_all",
                use_container_width=True,
            ):
                st.session_state.comparison_cc_multiselect = filtered_list
                st.rerun()
        with col_btn2:
            if st.button(
                t("data_comparison_page.deselect_all"),
                key="comparison_deselect_all",
                use_container_width=True,
            ):
                st.session_state.comparison_cc_multiselect = []
                st.rerun()

        selected_cost_centers = st.multiselect(
            t("data_comparison_page.select_cc_label"),
            options=filtered_list if search_term else cost_center_list,
            key="comparison_cc_multiselect",
        )

    st.markdown(
        f"""
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.load_data_title')}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        sync_button = st.button(
            t("data_comparison_page.sync_button"),
            key="btn_load_both",
            type="primary",
            use_container_width=True,
        )
    with col_btn2:
        if st.button(
            t("data_comparison_page.clear_all_button"),
            key="btn_clear_all",
            type="secondary",
            use_container_width=True,
        ):
            keys_to_clear = [
                "excel_data", "flowwer_data", "comparison_results",
                "df_excel_aggregated", "df_flowwer_aggregated",
                "df_excel_clean_for_inspector", "df_flowwer_clean_for_inspector",
                "currency_cache", "invoice_number_cache",
                "comparison_cc_multiselect", "selected_cost_center"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success(t("data_comparison_page.data_cleared"))
            st.rerun()
    
    if sync_button:
        if "excel_data" in st.session_state:
            del st.session_state.excel_data
        if "flowwer_data" in st.session_state:
            del st.session_state.flowwer_data
        if "comparison_results" in st.session_state:
            del st.session_state.comparison_results

        datev_success = False
        flowwer_success = False
        
        selected_cost_centers = st.session_state.get("comparison_cc_multiselect", [])

        status_container = st.empty()
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        datev_success = False
        flowwer_success = False
        
        try:
            progress_text.text("Connecting to PowerApps Dataverse...")
            progress_bar.progress(0.05)
            
            dv_client = st.session_state.get("dv_client")
            if dv_client:
                date_filter = f"cr597_belegdatum ge {from_date.strftime('%Y-%m-%d')} and cr597_belegdatum le {to_date.strftime('%Y-%m-%d')}"
                progress_bar.progress(0.10)
                
                df_pa = dv_client.get_table_data("cr597_fin_kontobuchungens", filter_query=date_filter)
                progress_bar.progress(0.25)
                
                if not df_pa.empty:
                    progress_text.text(f"Mapping {len(df_pa)} records from PowerApps...")
                    mapping = {
                        "cr597_belegdatum": "Belegdatum", "cr597_belegfeld1": "Belegfeld 1",
                        "cr597_kost1kostenstelle": "KOST1 - Kostenstelle", "cr597_amount": "Amount",
                        "cr597_buchungstext": "Buchungstext"
                    }
                    df_mapped = df_pa.rename(columns={k: v for k, v in mapping.items() if k in df_pa.columns})
                    if "Belegdatum" in df_mapped.columns:
                        df_mapped["Belegdatum"] = pd.to_datetime(df_mapped["Belegdatum"], errors='coerce').dt.tz_localize(None)
                    
                    if selected_cost_centers:
                        df_mapped["KOST_STR"] = df_mapped["KOST1 - Kostenstelle"].astype(str)
                        df_mapped = df_mapped[df_mapped["KOST_STR"].isin([str(cc) for cc in selected_cost_centers])]
                        df_mapped.drop(columns=["KOST_STR"], inplace=True)

                    st.session_state.excel_data = df_mapped
                    progress_text.text("PowerApps synchronization complete.")
                    progress_bar.progress(0.40)
                    datev_success = True
                else:
                    progress_text.text("No records found in PowerApps.")
                    st.session_state.excel_data = pd.DataFrame()
                    progress_bar.progress(0.40)
                    datev_success = True
            else:
                progress_bar.empty()
                progress_text.empty()
                st.error("Dataverse Client not found.")
        except Exception as e:
            progress_bar.empty()
            progress_text.empty()
            st.error(f"PowerApps Sync Error: {e}")
            datev_success = False

        if datev_success:
            try:
                progress_text.text("Connecting to Flowwer API...")
                progress_bar.progress(0.45)
                
                lookahead_days = search_lookahead_months * 30
                search_max_date = to_date + timedelta(days=lookahead_days)
                current_time = datetime.now()
                if search_max_date > current_time: search_max_date = current_time
                if to_date > search_max_date: search_max_date = to_date

                progress_text.text(f"Searching documents up to {search_max_date.date()}...")
                progress_bar.progress(0.50)
                
                filter_params = {"min_date": from_date.isoformat(), "max_date": search_max_date.isoformat()}
                report = client.get_receipt_splitting_report(**filter_params)
                progress_bar.progress(0.65)

                if selected_cost_centers and len(selected_cost_centers) > 0 and report:
                    cost_center_field = next((f for f in ["costCenter", "CostCenter", "cost_center"] if report and len(report) > 0 and f in report[0]), None)
                    if cost_center_field:
                        report = [r for r in report if str(r.get(cost_center_field, "")) in selected_cost_centers]

                if report:
                    df_flowwer = pd.DataFrame(report)
                    progress_text.text(f"Downloaded {len(df_flowwer)} Flowwer records.")
                    progress_bar.progress(0.70)
                    
                    doc_id_col = next((c for c in ["documentId", "document_id", "id", "Id"] if c in df_flowwer.columns), None)
                    st.session_state.flowwer_doc_id_col = doc_id_col
                    
                    currency_cache = st.session_state.get("currency_cache", {})
                    if doc_id_col:
                        progress_text.text("Verifying currency codes...")
                        progress_bar.progress(0.75)
                        
                        unique_ids = df_flowwer[doc_id_col].unique()
                        missing = [did for did in unique_ids if did not in currency_cache]
                        if missing:
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                                f_to_id = {executor.submit(client.get_document, did): did for did in missing}
                                completed = 0
                                total = len(f_to_id)
                                for f in concurrent.futures.as_completed(f_to_id):
                                    did = f_to_id[f]
                                    try:
                                        res = f.result()
                                        currency_cache[did] = res.get("currencyCode", "EUR") if res else "EUR"
                                    except: 
                                        currency_cache[did] = "EUR"
                                    completed += 1
                                    progress_bar.progress(0.75 + (completed / total) * 0.15)
                            st.session_state.currency_cache = currency_cache
                    
                    df_flowwer["currencyCode"] = df_flowwer[doc_id_col].map(currency_cache).fillna("EUR") if doc_id_col else "EUR"
                    st.session_state.flowwer_data = df_flowwer

                    cost_center_col = None
                    for col in ["costCenter", "CostCenter", "cost_center"]:
                        if col in df_flowwer.columns:
                            cost_center_col = col
                            break
                    if cost_center_col:
                        unique_cost_centers = sorted(
                            df_flowwer[cost_center_col].dropna().unique().tolist()
                        )
                    else:
                        unique_cost_centers = []
                    st.session_state.available_cost_centers = unique_cost_centers

                    progress_text.text(
                        t("data_comparison_page.data_loaded_summary").format(
                            datev_count=f"{len(st.session_state.excel_data):,}",
                            flowwer_count=f"{len(df_flowwer):,}",
                        )
                    )
                    progress_bar.progress(1.0)
                    flowwer_success = True
                else:
                    progress_text.text("Flowwer Sync: No data found.")
                    st.session_state.flowwer_data = pd.DataFrame()
                    progress_bar.progress(1.0)
                    flowwer_success = True
            except Exception as e:
                progress_bar.empty()
                progress_text.empty()
                st.error(f"Flowwer Sync Error: {e}")
                flowwer_success = False
        
        progress_bar.empty()
        progress_text.empty()
        
        if datev_success and flowwer_success:
            st.success("All systems synchronized successfully!")
        elif not datev_success or not flowwer_success:
            st.warning("One or more datasets failed to sync. Results may be incomplete.")

    if "flowwer_data" in st.session_state and st.session_state.flowwer_data is not None:
        df_flowwer_display = st.session_state.flowwer_data
        cost_center_col = None
        for col in ["costCenter", "CostCenter", "cost_center"]:
            if col in df_flowwer_display.columns:
                cost_center_col = col
                break

        if cost_center_col:
            available_cost_centers = sorted(
                df_flowwer_display[cost_center_col].dropna().unique().tolist()
            )
            st.session_state.available_cost_centers = available_cost_centers

            st.markdown(
                f"""
                <div style="
                    border-left: 3px solid #6366f1;
                    padding: 0.75rem 1.25rem;
                    border-radius: 8px;
                    margin: 2rem 0 1rem 0;
                    background: rgba(99, 102, 241, 0.03);
                ">
                    <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.additional_filter_title')}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                cost_center_options = ["All Cost Centers"] + available_cost_centers
                st.session_state.selected_cost_center = st.selectbox(
                    t("data_comparison_page.filter_by_cc_label"),
                    options=cost_center_options,
                    key="cost_center_selector",
                )
            with col2:
                pass

    if (
        "excel_data" in st.session_state
        and st.session_state.excel_data is not None
        and "flowwer_data" in st.session_state
        and st.session_state.flowwer_data is not None
    ):

        st.markdown(
            f"""
            <div style="
                border-left: 3px solid #6366f1;
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                margin: 2rem 0 1rem 0;
                background: rgba(99, 102, 241, 0.03);
            ">
                <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.comparison_title')}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        df_excel = st.session_state.excel_data
        df_flowwer = st.session_state.flowwer_data

        if (
            "selected_cost_center" in st.session_state
            and st.session_state.selected_cost_center != "All Cost Centers"
        ):
            cost_center_col = None
            for col in ["costCenter", "CostCenter", "cost_center"]:
                if col in df_flowwer.columns:
                    cost_center_col = col
                    break
            if cost_center_col:
                df_flowwer = df_flowwer[
                    df_flowwer[cost_center_col] == st.session_state.selected_cost_center
                ].copy()

        col1, col2 = st.columns(2)
        with col1:
            st.caption(t("data_comparison_page.datev_data_caption"))
            st.metric(t("data_comparison_page.rows_metric"), f"{len(df_excel):,}")

        with col2:
            st.caption(t("data_comparison_page.flowwer_data_caption"))
            st.metric(t("data_comparison_page.rows_metric"), f"{len(df_flowwer):,}")
            cost_center_filter = st.session_state.get(
                "selected_cost_center", "All Cost Centers"
            )
            if cost_center_filter != "All Cost Centers":
                st.metric(
                    t("data_comparison_page.filtered_cc_metric"), cost_center_filter
                )

        st.markdown("<br>", unsafe_allow_html=True)
        col_compare1, col_compare2 = st.columns([3, 1])
        with col_compare1:
            compare_button = st.button(
                t("data_comparison_page.cross_check_btn"),
                key="btn_compare",
                type="primary",
                use_container_width=True,
            )
        with col_compare2:
            tolerance = st.number_input(
                t("data_comparison_page.tolerance_label"),
                min_value=0.0,
                max_value=10.0,
                value=0.01,
                step=0.01,
                format="%.2f",
                help=t("data_comparison_page.tolerance_help"),
                key="amount_tolerance"
            )
        
        if compare_button:
            with st.spinner(t("data_comparison_page.checking_spinner")):
                df_excel_clean = df_excel.copy()

                st.session_state.df_excel_clean_for_inspector = df_excel_clean.copy()
                df_excel_clean["Invoice_Number"] = (
                    df_excel_clean["Belegfeld 1"].astype(str).str.strip()
                )
                df_excel_clean["Invoice_Date"] = pd.to_datetime(
                    df_excel_clean["Belegdatum"], errors="coerce"
                )
                df_excel_clean["Cost_Center"] = (
                    pd.to_numeric(
                        df_excel_clean["KOST1 - Kostenstelle"], errors="coerce"
                    )
                    .fillna(0)
                    .astype(int)
                    .astype(str)
                    .str.replace("^0$", "", regex=True)
                )

                if "Buchungstext" in df_excel_clean.columns:
                    df_excel_clean["Buchungstext"] = (
                        df_excel_clean["Buchungstext"].astype(str).str.strip()
                    )
                else:
                    df_excel_clean["Buchungstext"] = ""

                df_excel_clean["Amount"] = df_excel_clean["Amount"].astype(str)
                df_excel_clean["Amount"] = df_excel_clean["Amount"].apply(
                    lambda x: (
                        -float(
                            x.replace("(", "").replace(")", "").replace(",", "").strip()
                        )
                        if "(" in str(x) and ")" in str(x)
                        else (
                            float(str(x).replace(",", "").strip())
                            if str(x).strip() and str(x) != "nan" and str(x) != "None"
                            else 0
                        )
                    )
                )

                df_excel_clean = df_excel_clean[
                    (df_excel_clean["Invoice_Number"] != "")
                    & (df_excel_clean["Invoice_Number"] != "0")
                    & (df_excel_clean["Invoice_Number"] != "nan")
                    & (df_excel_clean["Invoice_Number"] != "None")
                    & (df_excel_clean["Invoice_Number"].notna())
                ]

                if (
                    "selected_cost_center" in st.session_state
                    and st.session_state.selected_cost_center != "All Cost Centers"
                ):
                    df_excel_clean = df_excel_clean[
                        df_excel_clean["Cost_Center"]
                        == st.session_state.selected_cost_center
                    ].copy()

                df_excel_aggregated = (
                    df_excel_clean.groupby(
                        ["Invoice_Number", "Buchungstext"],
                        as_index=False,
                        dropna=False,
                    )
                    .agg(
                        {
                            "Invoice_Date": "first",
                            "Cost_Center": "first",
                            "Amount": "sum",
                        }
                    )
                    .copy()
                )

                df_flowwer_clean = df_flowwer.copy()

                st.session_state.df_flowwer_clean_for_inspector = (
                    df_flowwer_clean.copy()
                )

                initial_count = len(df_flowwer_clean)

                if "currentStage" in df_flowwer_clean.columns:
                    before_stage_filter = len(df_flowwer_clean)
                    valid_stages = ["Processed", "Draft", "Approved"]
                    df_flowwer_clean = df_flowwer_clean[
                        df_flowwer_clean["currentStage"].isin(valid_stages)
                    ].copy()
                    after_stage_filter = len(df_flowwer_clean)

                    if before_stage_filter > 0 and after_stage_filter == 0:
                        unique_stages = (
                            df_flowwer["currentStage"].unique()
                            if "currentStage" in df_flowwer.columns
                            else []
                        )
                        st.warning(
                            t("data_comparison_page.all_filtered_warning").format(
                                count=before_stage_filter
                            )
                        )
                    elif before_stage_filter > after_stage_filter:
                        pass

                invoice_number_col = None
                for col in [
                    "invoiceNumber",
                    "invoice_number",
                    "InvoiceNumber",
                    "receiptNumber",
                    "receipt_number",
                ]:
                    if col in df_flowwer_clean.columns:
                        invoice_number_col = col
                        break

                if invoice_number_col:
                    df_flowwer_clean["Invoice_Number"] = (
                        df_flowwer_clean[invoice_number_col].astype(str).str.strip()
                    )
                else:

                    doc_id_col = st.session_state.get("flowwer_doc_id_col")
                    if doc_id_col is None:
                        for col in [
                            "documentId",
                            "document_id",
                            "DocumentId",
                            "id",
                            "Id",
                        ]:
                            if col in df_flowwer_clean.columns:
                                doc_id_col = col
                                break

                    if doc_id_col and len(df_flowwer_clean) > 0:
                        unique_doc_ids = df_flowwer[doc_id_col].dropna().unique()

                        invoice_cache = st.session_state.get("invoice_number_cache", {})
                        missing_ids = [
                            doc_id
                            for doc_id in unique_doc_ids
                            if doc_id not in invoice_cache
                        ]

                        if missing_ids:
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            total_missing = len(missing_ids)
                            status_text.text(f"Fetching invoice numbers: 0/{total_missing}")
                            
                            for i, doc_id in enumerate(missing_ids):
                                try:
                                    doc_details = client.get_document(doc_id)
                                    if doc_details:
                                        inv_num = (
                                            doc_details.get("invoiceNumber")
                                            or doc_details.get("invoice_number")
                                            or doc_details.get("InvoiceNumber")
                                            or doc_details.get("receiptNumber")
                                            or doc_details.get("receipt_number")
                                            or ""
                                        )
                                        invoice_cache[doc_id] = (
                                            str(inv_num).strip() if inv_num else ""
                                        )
                                    else:
                                        invoice_cache[doc_id] = ""
                                except Exception:
                                    invoice_cache[doc_id] = ""

                                progress = (i + 1) / total_missing
                                progress_bar.progress(progress)
                                status_text.text(f"Fetching invoice numbers: {i + 1}/{total_missing}")
                            
                            progress_bar.empty()
                            status_text.empty()

                            st.session_state.invoice_number_cache = invoice_cache

                        df_flowwer_clean["Invoice_Number"] = (
                            df_flowwer_clean[doc_id_col].map(invoice_cache).fillna("")
                        )

                        non_empty_invoices = (
                            df_flowwer_clean["Invoice_Number"] != ""
                        ).sum()
                        if non_empty_invoices < len(df_flowwer_clean):
                            missing_count = len(df_flowwer_clean) - non_empty_invoices
                    else:
                        df_flowwer_clean["Invoice_Number"] = ""

                invoice_date_col = None
                for col in [
                    "invoiceDate",
                    "invoice_date",
                    "InvoiceDate",
                    "date",
                    "Date",
                ]:
                    if col in df_flowwer_clean.columns:
                        invoice_date_col = col
                        break
                if invoice_date_col:
                    df_flowwer_clean["Invoice_Date"] = pd.to_datetime(
                        df_flowwer_clean[invoice_date_col], errors="coerce"
                    ).dt.tz_localize(None)
                    missing_dates = df_flowwer_clean["Invoice_Date"].isna().sum()
                    if missing_dates > 0:
                        st.warning(
                            t("data_comparison_page.missing_dates_warning").format(
                                count=f"{missing_dates:,}"
                            )
                        )
                else:
                    df_flowwer_clean["Invoice_Date"] = pd.NaT

                cost_center_col = None
                for col in ["costCenter", "CostCenter", "cost_center"]:
                    if col in df_flowwer_clean.columns:
                        cost_center_col = col
                        break
                if cost_center_col:
                    df_flowwer_clean["Cost_Center"] = (
                        df_flowwer_clean[cost_center_col].astype(str).str.strip()
                    )
                else:
                    df_flowwer_clean["Cost_Center"] = ""

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
                    if col in df_flowwer_clean.columns:
                        amount_col = col
                        break
                if amount_col:
                    df_flowwer_clean["Amount"] = pd.to_numeric(
                        df_flowwer_clean[amount_col], errors="coerce"
                    )
                else:
                    df_flowwer_clean["Amount"] = 0

                before_invoice_filter = len(df_flowwer_clean)
                df_flowwer_clean = df_flowwer_clean[
                    (df_flowwer_clean["Invoice_Number"] != "")
                    & (df_flowwer_clean["Invoice_Number"] != "0")
                    & (df_flowwer_clean["Invoice_Number"] != "nan")
                    & (df_flowwer_clean["Invoice_Number"] != "None")
                    & (df_flowwer_clean["Invoice_Number"].notna())
                ]
                after_invoice_filter = len(df_flowwer_clean)

                before_date_filter = len(df_flowwer_clean)
                df_flowwer_clean = df_flowwer_clean[
                    df_flowwer_clean["Invoice_Date"].notna()
                    & (df_flowwer_clean["Invoice_Date"] >= from_date)
                    & (df_flowwer_clean["Invoice_Date"] <= to_date)
                ]
                after_date_filter = len(df_flowwer_clean)

                if before_date_filter > after_date_filter:
                    filtered_out_dates = before_date_filter - after_date_filter
                    st.info(
                        t("data_comparison_page.filtered_out_info").format(
                            count=f"{filtered_out_dates:,}",
                            start=from_date.strftime("%Y-%m-%d"),
                            end=to_date.strftime("%Y-%m-%d"),
                        )
                    )

                if after_date_filter == 0 and before_date_filter > 0:
                    st.warning(
                        t("data_comparison_page.all_filtered_date_warning").format(
                            count=f"{before_date_filter:,}"
                        )
                    )

                if "currencyCode" in df_flowwer_clean.columns:
                    pln_mask = (
                        df_flowwer_clean["currencyCode"].str.upper().isin(["PL", "PLN"])
                    )

                    for idx in df_flowwer_clean[pln_mask].index:
                        invoice_date = df_flowwer_clean.loc[idx, "Invoice_Date"]
                        if pd.notna(invoice_date):
                            if isinstance(invoice_date, pd.Timestamp):
                                date_str = invoice_date.strftime("%Y-%m-%d")
                            else:
                                date_str = pd.to_datetime(invoice_date).strftime(  # type: ignore
                                    "%Y-%m-%d"
                                )

                            rate = get_pln_eur_rate(date_str)
                            current_amount = float(df_flowwer_clean.loc[idx, "Amount"]) # type: ignore
                            df_flowwer_clean.loc[idx, "Amount"] = current_amount / rate

                if before_invoice_filter > 0 and after_invoice_filter == 0:
                    st.warning(
                        t("data_comparison_page.all_filtered_inv_warning").format(
                            count=before_invoice_filter
                        )
                    )

                df_flowwer_aggregated = (
                    df_flowwer_clean.groupby(
                        ["Invoice_Number"],
                        as_index=False,
                        dropna=False,
                    )
                    .agg(
                        {
                            "Invoice_Date": "first",
                            "Cost_Center": "first",
                            "Amount": "sum",
                        }
                    )
                    .copy()
                )

                excel_unique_invoices = df_excel_clean["Invoice_Number"].nunique()
                flowwer_unique_invoices = df_flowwer_clean["Invoice_Number"].nunique()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        t("data_comparison_page.excel_records_metric"),
                        f"{len(df_excel_clean):,}",
                    )
                with col2:
                    st.metric(
                        t("data_comparison_page.excel_inv_unique_metric"),
                        f"{excel_unique_invoices:,}",
                    )
                with col3:
                    st.metric(
                        t("data_comparison_page.flowwer_records_metric"),
                        f"{len(df_flowwer_clean):,}",
                    )
                with col4:
                    st.metric(
                        t("data_comparison_page.flowwer_inv_unique_metric"),
                        f"{flowwer_unique_invoices:,}",
                    )

                st.markdown(f"### {t('data_comparison_page.results_title')}")

                results = []

                if len(df_flowwer_aggregated) == 0:
                    st.warning(
                        t("data_comparison_page.no_records_warning")
                        + "\n"
                        + "This could mean:\n"
                        "- No data matches the selected date range\n"
                        "- Cost center filter removed all records\n"
                        "- Data loading failed\n\n"
                        "Please check your filters and try again."
                    )
                    df_results = pd.DataFrame(
                        columns=[
                            "Invoice_Number",
                            "Status",
                            "Flowwer_Date",
                            "DATEV_Date",
                            "Date_Match",
                            "Flowwer_CC",
                            "DATEV_CC",
                            "CC_Match",
                            "Buchungstext_Match",
                            "Flowwer_Amount",
                            "DATEV_Amount",
                            "Amount_Match",
                            "Amount_Diff",
                        ]
                    )
                    st.session_state.comparison_results = df_results
                    st.session_state.df_excel_aggregated = df_excel_aggregated
                    st.session_state.df_flowwer_aggregated = df_flowwer_aggregated
                else:
                    for idx, flowwer_row in df_flowwer_aggregated.iterrows():
                        invoice_num = flowwer_row["Invoice_Number"]
                        flowwer_date = flowwer_row["Invoice_Date"]
                        flowwer_cc = flowwer_row["Cost_Center"]
                        flowwer_amount = flowwer_row["Amount"]

                        excel_matches = df_excel_aggregated[
                            df_excel_aggregated["Invoice_Number"] == invoice_num
                        ]

                        if len(excel_matches) == 0:
                            results.append(
                                {
                                    "Invoice_Number": invoice_num,
                                    "Status": "Not in DATEV",
                                    "Flowwer_Date": flowwer_date,
                                    "DATEV_Date": None,
                                    "Date_Match": False,
                                    "Flowwer_CC": flowwer_cc,
                                    "DATEV_CC": "",
                                    "CC_Match": False,
                                    "Buchungstext_Match": False,
                                    "Flowwer_Amount": flowwer_amount,
                                    "DATEV_Amount": None,
                                    "Amount_Match": False,
                                    "Amount_Diff": None,
                                }
                            )
                        else:
                            exact_match = False
                            best_match = None

                            total_excel_amount = excel_matches["Amount"].sum()
                            excel_is_paid = abs(total_excel_amount) <= 0.01

                            for _, excel_row in excel_matches.iterrows():
                                excel_date = excel_row["Invoice_Date"]
                                excel_cc = excel_row["Cost_Center"]
                                excel_amount = excel_row["Amount"]
                                excel_text = excel_row.get("Buchungstext", "")

                                amount_diff = (
                                    abs(abs(flowwer_amount) - abs(excel_amount))
                                    if pd.notna(excel_amount)
                                    else None
                                )

                                total_amount_diff = abs(
                                    abs(flowwer_amount) - abs(total_excel_amount)
                                )

                                date_match = False
                                if pd.notna(flowwer_date) and pd.notna(excel_date):
                                    date_match = (
                                        flowwer_date.date() == excel_date.date()
                                    )

                                cc_match = str(flowwer_cc) == str(excel_cc)

                                tolerance = st.session_state.get("amount_tolerance", 0.01)
                                amount_match = (
                                    amount_diff is not None and amount_diff <= tolerance
                                )
                                total_amount_match = total_amount_diff <= tolerance

                                if excel_is_paid:
                                    exact_match = True
                                else:
                                
                                    if date_match and cc_match and (amount_match or total_amount_match):
                                        exact_match = True

                                current_score = 0
                                if amount_match: current_score += 4
                                elif total_amount_match: current_score += 3
                                if date_match: current_score += 2
                                if cc_match: current_score += 1

                                update_best = False
                                if best_match is None:
                                    update_best = True
                                else:
                                    old_score = 0
                                    if best_match.get("amount_match"): old_score += 4
                                    elif best_match.get("is_total_match"): old_score += 3
                                    if best_match.get("date_match"): old_score += 2
                                    if best_match.get("cc_match"): old_score += 1
                                    
                                    if current_score > old_score:
                                        update_best = True

                                if update_best or exact_match:
                                    use_total = (total_amount_match and not amount_match)
                                    final_amount = total_excel_amount if use_total else excel_amount
                                    final_diff = total_amount_diff if use_total else amount_diff
                                    final_amount_match = amount_match or total_amount_match

                                    best_match = {
                                        "datev_date": excel_date,
                                        "datev_cc": excel_cc,
                                        "datev_text": excel_text,
                                        "datev_amount": final_amount,
                                        "date_match": date_match,
                                        "cc_match": cc_match,
                                        "text_match": True,
                                        "amount_match": final_amount_match,
                                        "amount_diff": final_diff,
                                        "datev_is_paid": excel_is_paid,
                                        "is_total_match": use_total
                                    }
                                
                                if exact_match:
                                    break

                            if exact_match:
                                status = "Paid (DATEV)" if excel_is_paid else "Match"

                                results.append(
                                    {
                                        "Invoice_Number": invoice_num,
                                        "Status": status,
                                        "Flowwer_Date": flowwer_date,
                                        "DATEV_Date": (
                                            best_match["datev_date"]
                                            if best_match
                                            else None
                                        ),
                                        "Date_Match": (
                                            best_match["date_match"]
                                            if best_match
                                            else False
                                        ),
                                        "Flowwer_CC": flowwer_cc,
                                        "DATEV_CC": (
                                            best_match["datev_cc"] if best_match else ""
                                        ),
                                        "CC_Match": (
                                            best_match["cc_match"]
                                            if best_match
                                            else False
                                        ),
                                        "Buchungstext": (
                                            best_match["datev_text"]
                                            if best_match
                                            else ""
                                        ),
                                        "Flowwer_Amount": flowwer_amount,
                                        "DATEV_Amount": (
                                            best_match["datev_amount"]
                                            if best_match
                                            else None
                                        ),
                                        "Amount_Match": (
                                            best_match["amount_match"]
                                            if best_match
                                            else False
                                        ),
                                        "Amount_Diff": (
                                            best_match["amount_diff"]
                                            if best_match
                                            else None
                                        ),
                                    }
                                )
                            elif best_match is not None:
                                results.append(
                                    {
                                        "Invoice_Number": invoice_num,
                                        "Status": "Mismatch",
                                        "Flowwer_Date": flowwer_date,
                                        "DATEV_Date": best_match["datev_date"],
                                        "Date_Match": best_match["date_match"],
                                        "Flowwer_CC": flowwer_cc,
                                        "DATEV_CC": best_match["datev_cc"],
                                        "CC_Match": best_match["cc_match"],
                                        "Buchungstext": best_match["datev_text"],
                                        "Flowwer_Amount": flowwer_amount,
                                        "DATEV_Amount": best_match["datev_amount"],
                                        "Amount_Match": best_match["amount_match"],
                                        "Amount_Diff": best_match["amount_diff"],
                                    }
                                )
                            else:
                                results.append(
                                    {
                                        "Invoice_Number": invoice_num,
                                        "Status": "Mismatch",
                                        "Flowwer_Date": flowwer_date,
                                        "DATEV_Date": None,
                                        "Date_Match": False,
                                        "Flowwer_CC": flowwer_cc,
                                        "DATEV_CC": "",
                                        "CC_Match": False,
                                        "Buchungstext": "",
                                        "Flowwer_Amount": flowwer_amount,
                                        "DATEV_Amount": None,
                                        "Amount_Match": False,
                                        "Amount_Diff": None,
                                    }
                                )

                    df_results = pd.DataFrame(results)

                    st.session_state.comparison_results = df_results
                    st.session_state.df_excel_aggregated = df_excel_aggregated
                    st.session_state.df_flowwer_aggregated = df_flowwer_aggregated
                    
                    st.session_state.inspector_excel_ready = df_excel_clean.copy()
                    st.session_state.inspector_flowwer_ready = df_flowwer_clean.copy()
                    st.session_state.invoice_list_for_autocomplete = sorted(df_results["Invoice_Number"].unique().tolist())

        if (
            "comparison_results" in st.session_state
            and st.session_state.comparison_results is not None
        ):
            df_results = st.session_state.comparison_results

            if df_results.empty or "Status" not in df_results.columns:
                st.error(t("data_comparison_page.incomplete_results"))
                st.info(
                    "The comparison may have encountered an error. Check the data loading and try again."
                )
                total_checked = 0
                exact_matches = 0
                paid_invoices = 0
                mismatches = 0
                not_in_datev = 0
            else:
                total_checked = len(df_results)
                exact_matches = len(df_results[df_results["Status"] == "Match"])
                paid_invoices = len(df_results[df_results["Status"] == "Paid (DATEV)"])
                mismatches = len(df_results[df_results["Status"] == "Mismatch"])
                not_in_datev = len(df_results[df_results["Status"] == "Not in DATEV"])

            if (
                "df_excel_aggregated" in st.session_state
                and "df_flowwer_aggregated" in st.session_state
            ):
                excel_invs = set(
                    st.session_state.df_excel_aggregated["Invoice_Number"].unique()
                )
                flowwer_invs = set(
                    st.session_state.df_flowwer_aggregated["Invoice_Number"].unique()
                )
                excel_only_invs = excel_invs - flowwer_invs
                excel_only_count = len(excel_only_invs)
            else:
                excel_only_count = 0
                excel_only_invs = set()

            if total_checked > 0:
                st.markdown(
                    f"""
                <div style="
                    border-left: 3px solid #6366f1;
                    padding: 0.75rem 1.25rem;
                    border-radius: 8px;
                    margin: 2rem 0 1rem 0;
                    background: rgba(99, 102, 241, 0.03);
                ">
                    <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.results_section_title')}</h3>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("""
                    <style>
                    .metric-card {
                        background: rgba(128, 128, 128, 0.05);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(128, 128, 128, 0.2);
                        border-radius: 16px;
                        padding: 1.25rem;
                        display: flex;
                        flex-direction: column;
                        gap: 0.5rem;
                        transition: all 0.3s ease;
                        height: 100%;
                    }
                    .metric-card:hover {
                        transform: translateY(-4px);
                        background: rgba(128, 128, 128, 0.1);
                        border-color: rgba(99, 102, 241, 0.5);
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
                    }
                    .metric-label {
                        font-size: 0.8rem;
                        font-weight: 500;
                        opacity: 0.8;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                    .metric-value {
                        font-size: 1.75rem;
                        font-weight: 700;
                    }
                    .metric-delta {
                        font-size: 0.8rem;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 0.25rem;
                        opacity: 0.9;
                    }
                    .delta-up { color: #10b981 !important; }
                    .delta-down { color: #ef4444 !important; }
                    </style>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    delta_text = f"{(exact_matches/total_checked*100):.1f}%" if total_checked > 0 else "0%"
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">✅ {t('data_comparison_page.exact_matches_metric')}</div>
                            <div class="metric-value">{exact_matches:,}</div>
                            <div class="metric-delta delta-up">↑ {delta_text} coverage</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    delta_text = f"{(paid_invoices/total_checked*100):.1f}%" if total_checked > 0 else "0%"
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">💰 {t('data_comparison_page.paid_datev_metric')}</div>
                            <div class="metric-value">{paid_invoices:,}</div>
                            <div class="metric-delta delta-neutral">ℹ️ {delta_text} of total</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col3:
                    delta_text = f"{(mismatches/total_checked*100):.1f}%" if total_checked > 0 else "0%"
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">⚠️ {t('data_comparison_page.mismatches_metric')}</div>
                            <div class="metric-value">{mismatches:,}</div>
                            <div class="metric-delta delta-down">↓ {delta_text} mismatch</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col4:
                    delta_text = f"{(not_in_datev/total_checked*100):.1f}%" if total_checked > 0 else "0%"
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">❌ {t('data_comparison_page.not_in_datev_metric')}</div>
                            <div class="metric-value">{not_in_datev:,}</div>
                            <div class="metric-delta delta-down">! {delta_text} missing</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col5:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">🔍 {t('data_comparison_page.not_in_flowwer_metric')}</div>
                            <div class="metric-value">{excel_only_count:,}</div>
                            <div class="metric-delta">Unmapped in API</div>
                        </div>
                    """, unsafe_allow_html=True)

                mismatch_df = df_results[df_results["Status"] == "Mismatch"]
                date_only_mismatch = len(mismatch_df[~mismatch_df["Date_Match"] & mismatch_df["CC_Match"] & mismatch_df["Amount_Match"]]) if not mismatch_df.empty else 0
                cc_only_mismatch = len(mismatch_df[mismatch_df["Date_Match"] & ~mismatch_df["CC_Match"] & mismatch_df["Amount_Match"]]) if not mismatch_df.empty else 0
                amount_only_mismatch = len(mismatch_df[mismatch_df["Date_Match"] & mismatch_df["CC_Match"] & ~mismatch_df["Amount_Match"]]) if not mismatch_df.empty else 0
                multiple_mismatch = len(mismatch_df[~(mismatch_df["Date_Match"] & mismatch_df["CC_Match"] & mismatch_df["Amount_Match"]) & ~(~mismatch_df["Date_Match"] & mismatch_df["CC_Match"] & mismatch_df["Amount_Match"]) & ~(mismatch_df["Date_Match"] & ~mismatch_df["CC_Match"] & mismatch_df["Amount_Match"]) & ~(mismatch_df["Date_Match"] & mismatch_df["CC_Match"] & ~mismatch_df["Amount_Match"])]) if not mismatch_df.empty else 0

                st.markdown("<br>", unsafe_allow_html=True)
                chart_col1, chart_col2 = st.columns([1, 1])

                with chart_col1:
                    status_counts = df_results["Status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]
                    
                    fig_pie = px.pie(
                        status_counts, values='Count', names='Status', hole=0.6,
                        color='Status', color_discrete_map={"Match": "#10b981", "Mismatch": "#f59e0b", "Not in DATEV": "#ef4444", "Paid (DATEV)": "#3b82f6"},
                        title="📊 Reconciliation Overview"
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)

                with chart_col2:
                    mismatch_data = {"Category": ["Date", "Cost Center", "Amount", "Multiple"], "Count": [date_only_mismatch, cc_only_mismatch, amount_only_mismatch, multiple_mismatch]}
                    df_mismatch_viz = pd.DataFrame(mismatch_data)
                    
                    fig_bar = px.bar(df_mismatch_viz, x='Category', y='Count', color='Category', color_discrete_sequence=["#f59e0b", "#6366f1", "#10b981", "#ef4444"], title="🔍 Mismatch Breakdown")
                    fig_bar.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="Invoices")
                    st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown(f"""
                    <div style="border-left: 3px solid #f59e0b; padding: 0.75rem 1.25rem; border-radius: 8px; margin: 2rem 0 1rem 0; background: rgba(245, 158, 11, 0.03);">
                        <h3 style="margin: 0; color: #f59e0b; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.mismatches_section_title')}</h3>
                    </div>
                """, unsafe_allow_html=True)

                if len(mismatch_df) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #f59e0b;"><div class="metric-label">{t('data_comparison_page.date_only_metric')}</div><div class="metric-value">{date_only_mismatch:,}</div><div class="metric-delta delta-neutral">📅 Timing diff</div></div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #6366f1;"><div class="metric-label">{t('data_comparison_page.cc_only_metric')}</div><div class="metric-value">{cc_only_mismatch:,}</div><div class="metric-delta delta-neutral">🏢 CC mismatch</div></div>""", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #10b981;"><div class="metric-label">{t('data_comparison_page.amount_only_metric')}</div><div class="metric-value">{amount_only_mismatch:,}</div><div class="metric-delta delta-neutral">💶 Value diff</div></div>""", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"""<div class="metric-card" style="border-left: 4px solid #ef4444;"><div class="metric-label">{t('data_comparison_page.multiple_metric')}</div><div class="metric-value">{multiple_mismatch:,}</div><div class="metric-delta delta-down">❗ Complex issue</div></div>""", unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="
                        border-left: 3px solid #6366f1;
                        padding: 0.75rem 1.25rem;
                        border-radius: 8px;
                        margin: 2rem 0 1rem 0;
                        background: rgba(99, 102, 241, 0.03);
                    ">
                        <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.inspector_title')}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                invoice_options = st.session_state.get("invoice_list_for_autocomplete", [])
                if not invoice_options:
                    invoice_options = sorted(df_results["Invoice_Number"].unique().tolist())
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    inspect_invoice = st.selectbox(
                        t("data_comparison_page.inspect_input_label"),
                        options=["---"] + invoice_options,
                        key="inspect_invoice_selector",
                        help="Select an invoice number to see detailed comparison"
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔄 Refresh", help="Reload invoice list", use_container_width=True):
                        if "invoice_list_for_autocomplete" in st.session_state:
                            del st.session_state["invoice_list_for_autocomplete"]
                        st.rerun()

                if inspect_invoice and inspect_invoice != "---":
                    inspect_invoice = inspect_invoice.strip()
                    
                    with st.spinner("Loading invoice details..."):
                        if "inspector_excel_ready" in st.session_state:
                            df_excel_inspect = st.session_state.inspector_excel_ready
                            excel_raw_records = df_excel_inspect[
                                df_excel_inspect["Invoice_Number"] == inspect_invoice
                            ]
                        else:
                            excel_raw_records = pd.DataFrame()

                        if "inspector_flowwer_ready" in st.session_state:
                            df_flowwer_inspect = st.session_state.inspector_flowwer_ready
                            flowwer_raw_records = df_flowwer_inspect[
                                df_flowwer_inspect["Invoice_Number"] == inspect_invoice
                            ]
                        else:
                            flowwer_raw_records = pd.DataFrame()

                    if len(excel_raw_records) > 0 or len(flowwer_raw_records) > 0:
                        st.markdown(
                            t("data_comparison_page.invoice_breakdown_title").format(
                                invoice=inspect_invoice
                            )
                        )

                        if len(excel_raw_records) > 0 and len(flowwer_raw_records) > 0:
                            excel_sum = excel_raw_records["Amount"].sum()
                            flowwer_sum = flowwer_raw_records["Amount"].sum()
                            difference = abs(excel_sum - flowwer_sum)

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric(
                                    t("data_comparison_page.excel_records_metric")
                                    .replace("Entries", "")
                                    .strip(),
                                    len(excel_raw_records),
                                )
                            with col2:
                                st.metric(
                                    t("data_comparison_page.datev_total_metric"),
                                    f"€{excel_sum:,.2f}",
                                )
                            with col3:
                                st.metric(
                                    t("data_comparison_page.flowwer_records_metric")
                                    .replace("Entries", "")
                                    .strip(),
                                    len(flowwer_raw_records),
                                )
                            with col4:
                                st.metric(
                                    t("data_comparison_page.flowwer_total_metric"),
                                    f"€{flowwer_sum:,.2f}",
                                )

                            if difference <= 0.01:
                                st.success(
                                    t("data_comparison_page.amounts_match_msg").format(
                                        diff=f"{difference:,.2f}"
                                    )
                                )
                            elif abs(excel_sum) <= 0.01:
                                st.info(t("data_comparison_page.invoice_paid_msg"))
                            else:
                                st.warning(
                                    t("data_comparison_page.amounts_differ_msg").format(
                                        diff=f"{difference:,.2f}"
                                    )
                                )

                        st.markdown("---")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader(
                                t("data_comparison_page.datev_records_subheader"),
                                divider="gray",
                            )
                            if len(excel_raw_records) > 0:
                                cols_to_show = ["Invoice_Date", "Cost_Center", "Amount"]
                                if "Buchungstext" in excel_raw_records.columns:
                                    cols_to_show.insert(2, "Buchungstext")

                                excel_display = excel_raw_records[cols_to_show].copy()

                                rename_map = {
                                    "Invoice_Date": t(
                                        "data_comparison_page.date_only_metric"
                                    )
                                    .replace("Only", "")
                                    .strip(),  # "Date",
                                    "Cost_Center": t(
                                        "data_comparison_page.cc_only_metric"
                                    )
                                    .replace("Only", "")
                                    .strip(),  # "Cost Center",
                                    "Buchungstext": "Description",
                                    "Amount": t(
                                        "data_comparison_page.amount_only_metric"
                                    )
                                    .replace("Only", "")
                                    .strip()
                                    + " (EUR)",  # "Amount (EUR)",
                                }
                                excel_display.rename(columns=rename_map, inplace=True)

                                excel_display[rename_map["Invoice_Date"]] = (
                                    pd.to_datetime(
                                        excel_display[rename_map["Invoice_Date"]]
                                    )
                                )

                                st.dataframe(
                                    excel_display,
                                    use_container_width=True,
                                    height=300,
                                    hide_index=True,
                                    column_config={
                                        rename_map[
                                            "Invoice_Date"
                                        ]: st.column_config.DateColumn(
                                            format="YYYY-MM-DD"
                                        ),
                                        rename_map[
                                            "Amount"
                                        ]: st.column_config.NumberColumn(
                                            format="€%.2f"
                                        ),
                                    },
                                )

                                total = excel_raw_records["Amount"].sum()
                                st.caption(
                                    f"**Total of {len(excel_raw_records)} records:** €{total:,.2f}"
                                )

                                if "Buchungstext" in excel_raw_records.columns:
                                    st.markdown("##### Subtotals by Description")
                                    subtotals = excel_raw_records.groupby(
                                        "Buchungstext"
                                    )["Amount"].sum()
                                    for desc, amount in subtotals.items():
                                        amount_str = (
                                            f"€{amount:,.2f}"
                                            if amount >= 0
                                            else f"-€{abs(amount):,.2f}"
                                        )
                                        desc_label = desc if desc else "(Empty)"
                                        st.write(f"- **{desc_label}:** {amount_str}")
                            else:
                                st.info(t("data_comparison_page.no_records_datev"))

                        with col2:
                            st.subheader(
                                t("data_comparison_page.flowwer_records_subheader"),
                                divider="gray",
                            )
                            if len(flowwer_raw_records) > 0:
                                flowwer_display = flowwer_raw_records[
                                    ["Invoice_Date", "Cost_Center", "Amount"]
                                ].copy()
                                flowwer_display.columns = [
                                    t("data_comparison_page.date_only_metric")
                                    .replace("Only", "")
                                    .strip(),  # "Date",
                                    t("data_comparison_page.cc_only_metric")
                                    .replace("Only", "")
                                    .strip(),  # "Cost Center",
                                    t("data_comparison_page.amount_only_metric")
                                    .replace("Only", "")
                                    .strip()
                                    + " (EUR)",  # "Amount (EUR)",
                                ]
                                flowwer_display[flowwer_display.columns[0]] = (
                                    pd.to_datetime(
                                        flowwer_display[flowwer_display.columns[0]]
                                    )
                                )

                                st.dataframe(
                                    flowwer_display,
                                    use_container_width=True,
                                    height=300,
                                    hide_index=True,
                                    column_config={
                                        flowwer_display.columns[
                                            0
                                        ]: st.column_config.DateColumn(
                                            format="YYYY-MM-DD"
                                        ),
                                        flowwer_display.columns[
                                            2
                                        ]: st.column_config.NumberColumn(
                                            format="€%.2f"
                                        ),
                                    },
                                )

                                total = flowwer_raw_records["Amount"].sum()
                                st.caption(
                                    f"**Total of {len(flowwer_raw_records)} records:** €{total:,.2f}"
                                )
                            else:
                                st.info(t("data_comparison_page.no_records_flowwer"))

                        if len(excel_raw_records) > 0 and len(flowwer_raw_records) > 0:
                            excel_sum = excel_raw_records["Amount"].sum()
                            flowwer_sum = flowwer_raw_records["Amount"].sum()
                            difference = abs(excel_sum - flowwer_sum)

                            if difference > 0.01:
                                st.markdown("---")
                                st.markdown(t("data_comparison_page.why_differ_title"))

                                reasons = []
                                if len(excel_raw_records) != len(flowwer_raw_records):
                                    reasons.append(
                                        t(
                                            "data_comparison_page.diff_reason_count"
                                        ).format(
                                            excel=len(excel_raw_records),
                                            flowwer=len(flowwer_raw_records),
                                        )
                                    )

                                if abs(excel_sum) <= 0.01:
                                    reasons.append(
                                        t("data_comparison_page.diff_reason_zero")
                                    )

                                if len(excel_raw_records) > len(flowwer_raw_records):
                                    reasons.append(
                                        t(
                                            "data_comparison_page.diff_reason_extra_datev"
                                        )
                                    )
                                elif len(flowwer_raw_records) > len(excel_raw_records):
                                    reasons.append(
                                        t(
                                            "data_comparison_page.diff_reason_extra_flowwer"
                                        )
                                    )

                                excel_ccs = set(
                                    excel_raw_records["Cost_Center"].unique()
                                )
                                flowwer_ccs = set(
                                    flowwer_raw_records["Cost_Center"].unique()
                                )
                                if excel_ccs != flowwer_ccs:
                                    reasons.append(
                                        t("data_comparison_page.diff_reason_cc").format(
                                            excel=len(excel_ccs),
                                            flowwer=len(flowwer_ccs),
                                        )
                                    )

                                for i, reason in enumerate(reasons, 1):
                                    st.write(f"{i}. {reason}")

                                if not reasons:
                                    st.write(
                                        t("data_comparison_page.diff_reason_unknown")
                                    )
                    else:
                        st.error(
                            t("data_comparison_page.invoice_not_found").format(
                                invoice=inspect_invoice
                            )
                        )

                st.markdown("---")
                st.markdown(t("data_comparison_page.side_by_side_title"))

                tab1, tab2, tab3, tab4 = st.tabs(
                    [
                        t("data_comparison_page.tab_all_mismatches"),
                        t("data_comparison_page.tab_date_issues"),
                        t("data_comparison_page.tab_cc_issues"),
                        t("data_comparison_page.tab_amount_issues"),
                    ]
                )

                with tab1:
                    display_df = (
                        mismatch_df[
                            [
                                "Invoice_Number",
                                "Flowwer_Date",
                                "DATEV_Date",
                                "Date_Match",
                                "Flowwer_CC",
                                "DATEV_CC",
                                "CC_Match",
                                "Flowwer_Amount",
                                "DATEV_Amount",
                                "Amount_Diff",
                                "Amount_Match",
                            ]
                        ]
                        .head(100)
                        .copy()
                    )

                    display_df["Flowwer_Date"] = pd.to_datetime(
                        display_df["Flowwer_Date"]
                    )
                    display_df["DATEV_Date"] = pd.to_datetime(display_df["DATEV_Date"])

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=400,
                        column_config={
                            "Invoice_Number": st.column_config.TextColumn("Invoice"),
                            "Flowwer_Date": st.column_config.DateColumn(
                                "Flowwer Date", format="YYYY-MM-DD"
                            ),
                            "DATEV_Date": st.column_config.DateColumn(
                                "DATEV Date", format="YYYY-MM-DD"
                            ),
                            "Date_Match": st.column_config.CheckboxColumn("Date OK"),
                            "Flowwer_CC": st.column_config.TextColumn(
                                "Flowwer Cost Center"
                            ),
                            "DATEV_CC": st.column_config.TextColumn(
                                "DATEV Cost Center"
                            ),
                            "CC_Match": st.column_config.CheckboxColumn("CC OK"),
                            "Flowwer_Amount": st.column_config.NumberColumn(
                                "Flowwer Amount", format="€%.2f"
                            ),
                            "DATEV_Amount": st.column_config.NumberColumn(
                                "DATEV Amount", format="€%.2f"
                            ),
                            "Amount_Diff": st.column_config.NumberColumn(
                                "Difference", format="€%.2f"
                            ),
                            "Amount_Match": st.column_config.CheckboxColumn(
                                "Amount OK"
                            ),
                        },
                    )

                with tab2:
                    date_issues = mismatch_df[~mismatch_df["Date_Match"]]
                    if len(date_issues) > 0:
                        display_date_df = (
                            date_issues[
                                [
                                    "Invoice_Number",
                                    "Flowwer_Date",
                                    "DATEV_Date",
                                    "Flowwer_CC",
                                    "Flowwer_Amount",
                                ]
                            ]
                            .head(100)
                            .copy()
                        )
                        display_date_df["Flowwer_Date"] = pd.to_datetime(
                            display_date_df["Flowwer_Date"]
                        )
                        display_date_df["DATEV_Date"] = pd.to_datetime(
                            display_date_df["DATEV_Date"]
                        )

                        st.dataframe(
                            display_date_df,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "Invoice_Number": st.column_config.TextColumn(
                                    "Invoice"
                                ),
                                "Flowwer_Date": st.column_config.DateColumn(
                                    "Flowwer Date", format="YYYY-MM-DD"
                                ),
                                "DATEV_Date": st.column_config.DateColumn(
                                    "DATEV Date", format="YYYY-MM-DD"
                                ),
                                "Flowwer_CC": st.column_config.TextColumn(
                                    "Cost Center"
                                ),
                                "Flowwer_Amount": st.column_config.NumberColumn(
                                    "Amount", format="€%.2f"
                                ),
                            },
                        )
                    else:
                        st.success(t("data_comparison_page.all_dates_match"))

                with tab3:
                    cc_issues = mismatch_df[~mismatch_df["CC_Match"]]
                    if len(cc_issues) > 0:
                        display_cc_df = (
                            cc_issues[
                                [
                                    "Invoice_Number",
                                    "Flowwer_CC",
                                    "DATEV_CC",
                                    "Flowwer_Amount",
                                    "DATEV_Amount",
                                ]
                            ]
                            .head(100)
                            .copy()
                        )

                        st.dataframe(
                            display_cc_df,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "Invoice_Number": st.column_config.TextColumn(
                                    "Invoice"
                                ),
                                "Flowwer_CC": st.column_config.TextColumn(
                                    "Flowwer Cost Center"
                                ),
                                "DATEV_CC": st.column_config.TextColumn(
                                    "DATEV Cost Center"
                                ),
                                "Flowwer_Amount": st.column_config.NumberColumn(
                                    "Flowwer Amount", format="€%.2f"
                                ),
                                "DATEV_Amount": st.column_config.NumberColumn(
                                    "DATEV Amount", format="€%.2f"
                                ),
                            },
                        )
                    else:
                        st.success(t("data_comparison_page.all_cc_match"))

                with tab4:
                    amount_issues = mismatch_df[~mismatch_df["Amount_Match"]]
                    if len(amount_issues) > 0:
                        display_amount_df = (
                            amount_issues[
                                [
                                    "Invoice_Number",
                                    "Flowwer_Amount",
                                    "DATEV_Amount",
                                    "Amount_Diff",
                                    "Flowwer_CC",
                                ]
                            ]
                            .head(100)
                            .copy()
                        )

                        st.dataframe(
                            display_amount_df,
                            use_container_width=True,
                            height=400,
                            column_config={
                                "Invoice_Number": st.column_config.TextColumn(
                                    "Invoice"
                                ),
                                "Flowwer_Amount": st.column_config.NumberColumn(
                                    "Flowwer Amount", format="€%.2f"
                                ),
                                "DATEV_Amount": st.column_config.NumberColumn(
                                    "DATEV Amount", format="€%.2f"
                                ),
                                "Amount_Diff": st.column_config.NumberColumn(
                                    "Difference", format="€%.2f"
                                ),
                                "Flowwer_CC": st.column_config.TextColumn(
                                    "Cost Center"
                                ),
                            },
                        )
                    else:
                        st.success(t("data_comparison_page.all_amounts_match"))
            else:
                not_in_datev_df = df_results[df_results["Status"] == "Not in DATEV"]
                if len(not_in_datev_df) == 0:
                    st.success(t("data_comparison_page.perfect_match_msg"))
                else:
                    st.info(
                        t("data_comparison_page.no_mismatches_but_missing").format(
                            count=len(not_in_datev_df)
                        )
                    )

            not_in_datev_df = df_results[df_results["Status"] == "Not in DATEV"]
            if len(not_in_datev_df) > 0:
                st.markdown(
                    f"""
                        <div style="
                            border-left: 3px solid #ef4444;
                            padding: 0.75rem 1.25rem;
                            border-radius: 8px;
                            margin: 2rem 0 1rem 0;
                            background: rgba(239, 68, 68, 0.03);
                        ">
                            <h3 style="margin: 0; color: #ef4444; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.not_in_datev_title')}</h3>
                        </div>
                        """,
                    unsafe_allow_html=True,
                )
                display_not_found_df = (
                    not_in_datev_df[
                        [
                            "Invoice_Number",
                            "Flowwer_Date",
                            "Flowwer_CC",
                            "Flowwer_Amount",
                        ]
                    ]
                    .head(50)
                    .copy()
                )
                display_not_found_df["Flowwer_Date"] = pd.to_datetime(
                    display_not_found_df["Flowwer_Date"]
                )

                st.dataframe(
                    display_not_found_df,
                    use_container_width=True,
                    height=300,
                    column_config={
                        "Invoice_Number": st.column_config.TextColumn("Invoice"),
                        "Flowwer_Date": st.column_config.DateColumn(
                            "Flowwer Date", format="YYYY-MM-DD"
                        ),
                        "Flowwer_CC": st.column_config.TextColumn(
                            "Flowwer Cost Center"
                        ),
                        "Flowwer_Amount": st.column_config.NumberColumn(
                            "Flowwer Amount", format="€%.2f"
                        ),
                    },
                )

            if excel_only_count > 0:
                st.markdown(
                    f"""
                        <div style="
                            border-left: 3px solid #8b5cf6;
                            padding: 0.75rem 1.25rem;
                            border-radius: 8px;
                            margin: 2rem 0 1rem 0;
                            background: rgba(139, 92, 246, 0.03);
                        ">
                            <h3 style="margin: 0; color: #8b5cf6; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">{t('data_comparison_page.not_in_flowwer_title')}</h3>
                        </div>
                        """,
                    unsafe_allow_html=True,
                )
                st.caption(
                    t("data_comparison_page.showing_missing_flowwer").format(
                        count=excel_only_count
                    )
                )

                # Fetch details for display
                df_excel_agg = st.session_state.df_excel_aggregated
                excel_only_df = (
                    df_excel_agg[df_excel_agg["Invoice_Number"].isin(excel_only_invs)]
                    .head(50)
                    .copy()
                )

                display_excel_only = excel_only_df[
                    [
                        "Invoice_Number",
                        "Invoice_Date",
                        "Cost_Center",
                        "Amount",
                        "Buchungstext",
                    ]
                ].copy()
                display_excel_only.columns = [
                    "Invoice",
                    "Date",
                    "Cost Center",
                    "Amount",
                    "Description",
                ]

                display_excel_only["Date"] = pd.to_datetime(display_excel_only["Date"])

                st.dataframe(
                    display_excel_only,
                    use_container_width=True,
                    height=300,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
                        "Amount": st.column_config.NumberColumn(format="€%.2f"),
                    },
                )

            st.markdown(t("data_comparison_page.export_title"))

            col1, col2 = st.columns(2)

            with col1:
                csv_full = df_results.to_csv(index=False)
                st.download_button(
                    label=t("data_comparison_page.csv_btn"),
                    data=csv_full,
                    file_name=f"crosscheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                excel_full = to_excel(df_results)
                st.download_button(
                    label=t("data_comparison_page.excel_btn"),
                    data=excel_full,
                    file_name=f"crosscheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    elif "excel_data" in st.session_state and st.session_state.excel_data is not None:
        st.info(t("data_comparison_page.load_flowwer_hint"))
    elif (
        "flowwer_data" in st.session_state and st.session_state.flowwer_data is not None
    ):
        st.info(t("data_comparison_page.load_excel_hint"))
    else:
        st.info(t("data_comparison_page.load_both_hint"))
