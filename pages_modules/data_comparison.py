"""
Data Comparison Page Module
Cross-check data between DATEV Excel exports and Flowwer API
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os


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
                    {t('test_page.title')}
                </h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.7; font-size: 1rem;">
                    {t('test_page.subtitle')}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        """
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">DATE RANGE</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    current_year = datetime.now().year
    current_month = datetime.now().month

    with col1:
        from_month = st.selectbox(
            "From Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=0,  
            key="from_month",
        )

    with col2:
        from_year = st.selectbox(
            "From Year",
            options=list(range(2020, current_year + 1)),
            index=len(list(range(2020, current_year + 1)))
            - 2,  
            key="from_year",
        )

    with col3:
        to_month = st.selectbox(
            "To Month",
            options=list(range(1, 13)),
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            index=11,  
            key="to_month",
        )

    with col4:
        to_year = st.selectbox(
            "To Year",
            options=list(range(2020, current_year + 1)),
            index=len(list(range(2020, current_year + 1)))
            - 1,  
            key="to_year",
        )

    from_date = datetime(from_year, from_month, 1)
    if to_month == 12:
        to_date = datetime(to_year, 12, 31)
    else:
        to_date = datetime(to_year, to_month + 1, 1) - timedelta(days=1)

    st.caption(
        f"Selected: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}"
    )

    st.markdown(
        """
        <div style="
            border-left: 3px solid #6366f1;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            background: rgba(99, 102, 241, 0.03);
        ">
            <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">LOAD DATA</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

   
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_file_path = os.path.join(script_dir, "Financial_Dashboard_Latest.xlsx")

    uploaded_file = None
    if not IN_PRODUCTION:
        st.markdown("#### 📁 Data Source")
        uploaded_file = st.file_uploader(
            "Upload DATEV Excel file (or use default file if available)",
            type=["xlsx"],
            help="Upload your DATEV exported Excel file with 'Booking General' sheet",
        )

    file_to_use = None
    file_source = None

    if uploaded_file is not None:
        file_to_use = uploaded_file
        file_source = "uploaded"
        st.info(f"📤 Using uploaded file: **{uploaded_file.name}**")
    elif os.path.exists(excel_file_path):
        file_to_use = excel_file_path
        file_source = "local"
        st.info(f"📂 Using local file: **{excel_file_path}**")
    else:
        warning_msg = "⚠️ **No Data File Available**\n\n"
        if not IN_PRODUCTION:
            warning_msg += "Please upload a DATEV Excel file above, or "
        else:
            warning_msg += "Local file not found. "
        warning_msg += f"place `{excel_file_path}` in:\n`{os.getcwd()}`"
        st.warning(warning_msg)

    if st.button(
        "Load Both Datasets",
        key="btn_load_both",
        type="primary",
        use_container_width=True,
        disabled=file_to_use is None,
    ):
        if "excel_data" in st.session_state:
            del st.session_state.excel_data
        if "flowwer_data" in st.session_state:
            del st.session_state.flowwer_data
        if "comparison_results" in st.session_state:
            del st.session_state.comparison_results

        datev_success = False
        flowwer_success = False

        status_placeholder = st.empty()

        try:
            with st.spinner("Loading DATEV data..."):
                if file_source == "uploaded":
                    df_excel = pd.read_excel(
                        file_to_use,
                        sheet_name="Booking General",
                        engine="openpyxl",
                        header=1,
                    )
                else:
                    df_excel = pd.read_excel(
                        excel_file_path,
                        sheet_name="Booking General",
                        engine="openpyxl",
                        header=1,
                    )

                df_excel["Belegdatum"] = pd.to_datetime(
                    df_excel["Belegdatum"], errors="coerce"
                )
                df_excel = df_excel[
                    (df_excel["Belegdatum"] >= from_date)
                    & (df_excel["Belegdatum"] <= to_date)
                ]
                st.session_state.excel_data = df_excel
                datev_success = True
        except Exception as e:
            status_placeholder.error(f"Error loading DATEV file: {e}")
            datev_success = False

        if datev_success:
            try:
                status_placeholder.info("🔄 Loading Flowwer API data...")

                report = client.get_receipt_splitting_report(
                    min_date=from_date.isoformat(), max_date=to_date.isoformat()
                )

                if report:
                    df_flowwer = pd.DataFrame(report)

                    unique_doc_ids = df_flowwer["documentId"].unique()
                    currency_map = {}

                    with st.spinner(f"Fetching currency information..."):
                        progress_bar = st.progress(0)
                        for i, doc_id in enumerate(unique_doc_ids):
                            try:
                                doc_details = client.get_document(doc_id)
                                if doc_details and "currencyCode" in doc_details:
                                    currency_map[doc_id] = doc_details["currencyCode"]
                                else:
                                    currency_map[doc_id] = "EUR"  
                            except:
                                currency_map[doc_id] = "EUR"  

                            if i % 10 == 0:
                                progress_bar.progress((i + 1) / len(unique_doc_ids))

                        progress_bar.progress(1.0)
                        progress_bar.empty()

                    df_flowwer["currencyCode"] = df_flowwer["documentId"].map(
                        currency_map
                    )

                    st.session_state.flowwer_data = df_flowwer

                    unique_cost_centers = sorted(
                        df_flowwer["costCenter"].dropna().unique().tolist()
                    )
                    st.session_state.available_cost_centers = unique_cost_centers

                    currency_counts = df_flowwer["currencyCode"].value_counts()

                    status_placeholder.success(
                        f"✅ Data loaded: {len(df_excel):,} DATEV rows • "
                        f"{len(df_flowwer):,} Flowwer rows • "
                        f"{len(unique_cost_centers)} cost centers • "
                        f"Currencies: {', '.join([f'{curr} ({count})' for curr, count in currency_counts.items()])}"
                    )
                    flowwer_success = True
                else:
                    status_placeholder.error("Failed to load data from Flowwer API")
                    flowwer_success = False
            except Exception as e:
                status_placeholder.error(f"Error loading Flowwer data: {e}")
                flowwer_success = False
        else:
            status_placeholder.error(
                "Failed to load data. Please check your settings and try again."
            )

    if (
        "flowwer_data" in st.session_state
        and st.session_state.flowwer_data is not None
        and "available_cost_centers" in st.session_state
    ):
        st.markdown(
            """
            <div style="
                border-left: 3px solid #6366f1;
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                margin: 2rem 0 1rem 0;
                background: rgba(99, 102, 241, 0.03);
            ">
                <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">FILTER (OPTIONAL)</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            cost_center_options = ["All Cost Centers"] + st.session_state.get(
                "available_cost_centers", []
            )
            st.session_state.selected_cost_center = st.selectbox(
                "Filter by Cost Center (optional)",
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
            """
            <div style="
                border-left: 3px solid #6366f1;
                padding: 0.75rem 1.25rem;
                border-radius: 8px;
                margin: 2rem 0 1rem 0;
                background: rgba(99, 102, 241, 0.03);
            ">
                <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">COMPARISON</h3>
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
            df_flowwer = df_flowwer[
                df_flowwer["costCenter"] == st.session_state.selected_cost_center
            ].copy()

        col1, col2 = st.columns(2)
        with col1:
            st.caption("DATEV Data")
            st.metric("Rows", f"{len(df_excel):,}")

        with col2:
            st.caption("Flowwer Data")
            st.metric("Rows", f"{len(df_flowwer):,}")
            cost_center_filter = st.session_state.get(
                "selected_cost_center", "All Cost Centers"
            )
            if cost_center_filter != "All Cost Centers":
                st.metric("🏢 Filtered CC", cost_center_filter)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🔍 Cross-Check Data",
            key="btn_compare",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Cross-checking data..."):
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

                df_flowwer_clean = df_flowwer.copy()

          
                st.session_state.df_flowwer_clean_for_inspector = (
                    df_flowwer_clean.copy()
                )

                if "currentStage" in df_flowwer_clean.columns:
                    df_flowwer_clean = df_flowwer_clean[
                        df_flowwer_clean["currentStage"] == "Processed"
                    ].copy()

                df_flowwer_clean["Invoice_Number"] = (
                    df_flowwer_clean["invoiceNumber"].astype(str).str.strip()
                )
                df_flowwer_clean["Invoice_Date"] = pd.to_datetime(
                    df_flowwer_clean["invoiceDate"], errors="coerce"
                )
                df_flowwer_clean["Cost_Center"] = (
                    df_flowwer_clean["costCenter"].astype(str).str.strip()
                )
                df_flowwer_clean["Amount"] = pd.to_numeric(
                    df_flowwer_clean["grossValue"], errors="coerce"
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
                                date_str = pd.to_datetime(invoice_date).strftime("%Y-%m-%d")  # type: ignore

                            rate = get_pln_eur_rate(date_str)
                            current_amount = float(df_flowwer_clean.loc[idx, "Amount"])  # type: ignore
                            df_flowwer_clean.loc[idx, "Amount"] = current_amount / rate

                df_flowwer_clean = df_flowwer_clean[
                    (df_flowwer_clean["Invoice_Number"] != "")
                    & (df_flowwer_clean["Invoice_Number"] != "0")
                    & (df_flowwer_clean["Invoice_Number"] != "nan")
                    & (df_flowwer_clean["Invoice_Number"].notna())
                ]

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

                st.markdown("### Cross-Check Results")

                # Show filtered data counts
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.info(f"Excel: {len(df_excel_clean):,} raw records")
                with col2:
                    st.info(f"Excel: {len(df_excel_aggregated):,} unique invoices")
                with col3:
                    st.info(f"Flowwer: {len(df_flowwer_clean):,} raw records")
                with col4:
                    st.info(f"Flowwer: {len(df_flowwer_aggregated):,} unique invoices")

                st.markdown("### Cross-Checking Flowwer Records Against Excel")

                results = []
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
                                "Flowwer_Amount": flowwer_amount,
                                "DATEV_Amount": None,
                                "Amount_Match": False,
                                "Amount_Diff": None,
                            }
                        )
                    else:
                        exact_match = False
                        best_match = None

                        for _, excel_row in excel_matches.iterrows():
                            excel_date = excel_row["Invoice_Date"]
                            excel_cc = excel_row["Cost_Center"]
                            excel_amount = excel_row["Amount"]

                            excel_is_paid = (
                                abs(excel_amount) <= 0.01
                                if pd.notna(excel_amount)
                                else False
                            )

                            amount_diff = (
                                abs(abs(flowwer_amount) - abs(excel_amount))
                                if pd.notna(excel_amount)
                                else None
                            )

                            date_match = False
                            if pd.notna(flowwer_date) and pd.notna(excel_date):
                                date_match = flowwer_date.date() == excel_date.date()

                            cc_match = str(flowwer_cc) == str(excel_cc)
                            amount_match = (
                                amount_diff is not None and amount_diff <= 0.01
                            )

                            if excel_is_paid or amount_match:
                                exact_match = True
                                best_match = {
                                    "datev_date": excel_date,
                                    "datev_cc": excel_cc,
                                    "datev_amount": excel_amount,
                                    "date_match": date_match,
                                    "cc_match": cc_match,
                                    "amount_match": amount_match,
                                    "amount_diff": amount_diff,
                                }
                                break

                            if best_match is None:
                                best_match = {
                                    "datev_date": excel_date,
                                    "datev_cc": excel_cc,
                                    "datev_amount": excel_amount,
                                    "datev_is_paid": excel_is_paid,
                                    "date_match": date_match,
                                    "cc_match": cc_match,
                                    "amount_match": amount_match,
                                    "amount_diff": amount_diff,
                                }

                        if exact_match:
                            status = (
                                "Paid (DATEV)"
                                if best_match and best_match.get("datev_is_paid", False)
                                else "Match"
                            )

                            results.append(
                                {
                                    "Invoice_Number": invoice_num,
                                    "Status": status,
                                    "Flowwer_Date": flowwer_date,
                                    "DATEV_Date": excel_date if best_match else None,
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
                                        best_match["cc_match"] if best_match else False
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

        if (
            "comparison_results" in st.session_state
            and st.session_state.comparison_results is not None
        ):
            df_results = st.session_state.comparison_results

            total_checked = len(df_results)
            exact_matches = len(df_results[df_results["Status"] == "Match"])
            paid_invoices = len(df_results[df_results["Status"] == "Paid (DATEV)"])
            mismatches = len(df_results[df_results["Status"] == "Mismatch"])
            not_in_datev = len(df_results[df_results["Status"] == "Not in DATEV"])

            st.markdown(
                """
                <div style="
                    border-left: 3px solid #6366f1;
                    padding: 0.75rem 1.25rem;
                    border-radius: 8px;
                    margin: 2rem 0 1rem 0;
                    background: rgba(99, 102, 241, 0.03);
                ">
                    <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">RESULTS</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Exact Matches",
                    f"{exact_matches:,}",
                    delta=f"{(exact_matches/total_checked*100):.1f}%",
                )
            with col2:
                st.metric(
                    "Paid (DATEV)",
                    f"{paid_invoices:,}",
                    delta=f"{(paid_invoices/total_checked*100):.1f}%",
                    help="Invoices with zero balance in DATEV (payment completed)",
                )
            with col3:
                st.metric(
                    "Mismatches",
                    f"{mismatches:,}",
                    delta=f"{(mismatches/total_checked*100):.1f}%",
                    delta_color="inverse",
                )
            with col4:
                st.metric(
                    "Not in DATEV",
                    f"{not_in_datev:,}",
                    delta=f"{(not_in_datev/total_checked*100):.1f}%",
                    delta_color="inverse",
                )

            st.markdown(
                """
                <div style="
                    border-left: 3px solid #f59e0b;
                    padding: 0.75rem 1.25rem;
                    border-radius: 8px;
                    margin: 2rem 0 1rem 0;
                    background: rgba(245, 158, 11, 0.03);
                ">
                    <h3 style="margin: 0; color: #f59e0b; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">MISMATCHES</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            mismatch_df = df_results[df_results["Status"] == "Mismatch"]

            if len(mismatch_df) > 0:
                date_only_mismatch = len(
                    mismatch_df[
                        ~mismatch_df["Date_Match"]
                        & mismatch_df["CC_Match"]
                        & mismatch_df["Amount_Match"]
                    ]
                )
                cc_only_mismatch = len(
                    mismatch_df[
                        mismatch_df["Date_Match"]
                        & ~mismatch_df["CC_Match"]
                        & mismatch_df["Amount_Match"]
                    ]
                )
                amount_only_mismatch = len(
                    mismatch_df[
                        mismatch_df["Date_Match"]
                        & mismatch_df["CC_Match"]
                        & ~mismatch_df["Amount_Match"]
                    ]
                )
                multiple_mismatch = len(
                    mismatch_df[
                        ~(
                            mismatch_df["Date_Match"]
                            & mismatch_df["CC_Match"]
                            & mismatch_df["Amount_Match"]
                        )
                        & ~(
                            ~mismatch_df["Date_Match"]
                            & mismatch_df["CC_Match"]
                            & mismatch_df["Amount_Match"]
                        )
                        & ~(
                            mismatch_df["Date_Match"]
                            & ~mismatch_df["CC_Match"]
                            & mismatch_df["Amount_Match"]
                        )
                        & ~(
                            mismatch_df["Date_Match"]
                            & mismatch_df["CC_Match"]
                            & ~mismatch_df["Amount_Match"]
                        )
                    ]
                )

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Date Only", f"{date_only_mismatch:,}")
                with col2:
                    st.metric("Cost Center Only", f"{cc_only_mismatch:,}")
                with col3:
                    st.metric("Amount Only", f"{amount_only_mismatch:,}")
                with col4:
                    st.metric("Multiple Fields", f"{multiple_mismatch:,}")

                st.markdown(
                    """
                    <div style="
                        border-left: 3px solid #6366f1;
                        padding: 0.75rem 1.25rem;
                        border-radius: 8px;
                        margin: 2rem 0 1rem 0;
                        background: rgba(99, 102, 241, 0.03);
                    ">
                        <h3 style="margin: 0; color: #6366f1; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">INSPECTOR</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns([3, 1])
                with col1:
                    inspect_invoice = st.text_input(
                        "Invoice Number to Inspect",
                        placeholder="e.g., 121/2025 or 00238/25",
                        key="inspect_invoice",
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    inspect_button = st.button("🔎 Inspect", type="primary")

                if inspect_button and inspect_invoice:
                    inspect_invoice = inspect_invoice.strip()

                    if "df_excel_clean_for_inspector" in st.session_state:
                        df_excel_inspect = (
                            st.session_state.df_excel_clean_for_inspector.copy()
                        )

                        df_excel_inspect["Invoice_Number"] = (
                            df_excel_inspect["Belegfeld 1"].astype(str).str.strip()
                        )
                        df_excel_inspect["Invoice_Date"] = pd.to_datetime(
                            df_excel_inspect["Belegdatum"], errors="coerce"
                        )
                        df_excel_inspect["Cost_Center"] = (
                            pd.to_numeric(
                                df_excel_inspect["KOST1 - Kostenstelle"],
                                errors="coerce",
                            )
                            .fillna(0)
                            .astype(int)
                            .astype(str)
                            .str.replace("^0$", "", regex=True)
                        )

                        df_excel_inspect["Amount"] = df_excel_inspect["Amount"].astype(
                            str
                        )
                        df_excel_inspect["Amount"] = df_excel_inspect["Amount"].apply(
                            lambda x: (
                                -float(
                                    x.replace("(", "")
                                    .replace(")", "")
                                    .replace(",", "")
                                    .strip()
                                )
                                if "(" in str(x) and ")" in str(x)
                                else (
                                    float(str(x).replace(",", "").strip())
                                    if str(x).strip()
                                    and str(x) != "nan"
                                    and str(x) != "None"
                                    else 0
                                )
                            )
                        )

                        excel_raw_records = df_excel_inspect[
                            df_excel_inspect["Invoice_Number"] == inspect_invoice
                        ]
                    else:
                        excel_raw_records = pd.DataFrame()

                    if "df_flowwer_clean_for_inspector" in st.session_state:
                        df_flowwer_inspect = (
                            st.session_state.df_flowwer_clean_for_inspector.copy()
                        )

                        if "currentStage" in df_flowwer_inspect.columns:
                            df_flowwer_inspect = df_flowwer_inspect[
                                df_flowwer_inspect["currentStage"] == "Processed"
                            ].copy()

                        df_flowwer_inspect["Invoice_Number"] = (
                            df_flowwer_inspect["invoiceNumber"].astype(str).str.strip()
                        )
                        df_flowwer_inspect["Invoice_Date"] = pd.to_datetime(
                            df_flowwer_inspect["invoiceDate"],
                            errors="coerce",
                        )
                        df_flowwer_inspect["Cost_Center"] = (
                            df_flowwer_inspect["costCenter"].astype(str).str.strip()
                        )
                        df_flowwer_inspect["Amount"] = pd.to_numeric(
                            df_flowwer_inspect["grossValue"], errors="coerce"
                        )

                        if "currencyCode" in df_flowwer_inspect.columns:
                            pln_mask = (
                                df_flowwer_inspect["currencyCode"]
                                .str.upper()
                                .isin(["PL", "PLN"])
                            )

                            for idx in df_flowwer_inspect[pln_mask].index:
                                invoice_date = df_flowwer_inspect.loc[
                                    idx, "Invoice_Date"
                                ]
                                if pd.notna(invoice_date):
                                    if isinstance(invoice_date, pd.Timestamp):
                                        date_str = invoice_date.strftime("%Y-%m-%d")
                                    else:
                                        date_str = pd.to_datetime(invoice_date).strftime("%Y-%m-%d")  # type: ignore

                                    rate = get_pln_eur_rate(date_str)
                                    current_amount = float(df_flowwer_inspect.loc[idx, "Amount"])  # type: ignore
                                    df_flowwer_inspect.loc[idx, "Amount"] = (
                                        current_amount / rate
                                    )

                        flowwer_raw_records = df_flowwer_inspect[
                            df_flowwer_inspect["Invoice_Number"] == inspect_invoice
                        ]
                    else:
                        flowwer_raw_records = pd.DataFrame()

                    if len(excel_raw_records) > 0 or len(flowwer_raw_records) > 0:
                        st.markdown(f"### Invoice Breakdown: `{inspect_invoice}`")
                        st.caption(
                            "Comparing all transaction records from both systems"
                        )

                        if len(excel_raw_records) > 0 and len(flowwer_raw_records) > 0:
                            excel_sum = excel_raw_records["Amount"].sum()
                            flowwer_sum = flowwer_raw_records["Amount"].sum()
                            difference = abs(excel_sum - flowwer_sum)

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("DATEV Records", len(excel_raw_records))
                            with col2:
                                st.metric("DATEV Total", f"€{excel_sum:,.2f}")
                            with col3:
                                st.metric("Flowwer Records", len(flowwer_raw_records))
                            with col4:
                                st.metric("Flowwer Total", f"€{flowwer_sum:,.2f}")

                            if difference <= 0.01:
                                st.success(
                                    f"**Amounts Match** - Both systems show the same total (difference: €{difference:,.2f})"
                                )
                            elif abs(excel_sum) <= 0.01:
                                st.info(
                                    "**Invoice Paid** - DATEV shows zero balance (payment completed with offsetting entries)"
                                )
                            else:
                                st.warning(
                                    f"**Amounts Differ** - Difference of €{difference:,.2f} between systems"
                                )

                        st.markdown("---")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("DATEV Records", divider="gray")
                            if len(excel_raw_records) > 0:
                                excel_display = excel_raw_records[
                                    ["Invoice_Date", "Cost_Center", "Amount"]
                                ].copy()
                                excel_display.columns = [
                                    "Date",
                                    "Cost Center",
                                    "Amount (EUR)",
                                ]
                                excel_display["Date"] = pd.to_datetime(
                                    excel_display["Date"]
                                ).dt.strftime("%Y-%m-%d")

                                excel_display["Amount (EUR)"] = excel_display[
                                    "Amount (EUR)"
                                ].apply(
                                    lambda x: (
                                        f"€{x:,.2f}" if x >= 0 else f"-€{abs(x):,.2f}"
                                    )
                                )

                                st.dataframe(
                                    excel_display,
                                    use_container_width=True,
                                    height=300,
                                    hide_index=True,
                                )

                                total = excel_raw_records["Amount"].sum()
                                st.caption(
                                    f"**Total of {len(excel_raw_records)} records:** €{total:,.2f}"
                                )
                            else:
                                st.info("No records found in DATEV for this invoice")

                        with col2:
                            st.subheader("Flowwer Records", divider="gray")
                            if len(flowwer_raw_records) > 0:
                                flowwer_display = flowwer_raw_records[
                                    ["Invoice_Date", "Cost_Center", "Amount"]
                                ].copy()
                                flowwer_display.columns = [
                                    "Date",
                                    "Cost Center",
                                    "Amount (EUR)",
                                ]
                                flowwer_display["Date"] = pd.to_datetime(
                                    flowwer_display["Date"]
                                ).dt.strftime("%Y-%m-%d")

                                flowwer_display["Amount (EUR)"] = flowwer_display[
                                    "Amount (EUR)"
                                ].apply(
                                    lambda x: (
                                        f"€{x:,.2f}" if x >= 0 else f"-€{abs(x):,.2f}"
                                    )
                                )

                                st.dataframe(
                                    flowwer_display,
                                    use_container_width=True,
                                    height=300,
                                    hide_index=True,
                                )

                                total = flowwer_raw_records["Amount"].sum()
                                st.caption(
                                    f"**Total of {len(flowwer_raw_records)} records:** €{total:,.2f}"
                                )
                            else:
                                st.info("No records found in Flowwer for this invoice")

                        if len(excel_raw_records) > 0 and len(flowwer_raw_records) > 0:
                            excel_sum = excel_raw_records["Amount"].sum()
                            flowwer_sum = flowwer_raw_records["Amount"].sum()
                            difference = abs(excel_sum - flowwer_sum)

                            if difference > 0.01:
                                st.markdown("---")
                                st.markdown("#### Why Do the Amounts Differ?")

                                reasons = []
                                if len(excel_raw_records) != len(flowwer_raw_records):
                                    reasons.append(
                                        f"Different number of transaction records: Excel has {len(excel_raw_records)}, Flowwer has {len(flowwer_raw_records)}"
                                    )

                                if abs(excel_sum) <= 0.01:
                                    reasons.append(
                                        "Excel balance is zero - invoice has been paid with offsetting credit/debit entries"
                                    )

                                if len(excel_raw_records) > len(flowwer_raw_records):
                                    reasons.append(
                                        "DATEV contains additional correction or reversal entries that haven't been synchronized to Flowwer yet"
                                    )
                                elif len(flowwer_raw_records) > len(excel_raw_records):
                                    reasons.append(
                                        "Flowwer contains additional line items or cost center splits not yet in DATEV"
                                    )

                                excel_ccs = set(
                                    excel_raw_records["Cost_Center"].unique()
                                )
                                flowwer_ccs = set(
                                    flowwer_raw_records["Cost_Center"].unique()
                                )
                                if excel_ccs != flowwer_ccs:
                                    reasons.append(
                                        f"Different cost centers used: DATEV has {len(excel_ccs)} unique, Flowwer has {len(flowwer_ccs)} unique"
                                    )

                                for i, reason in enumerate(reasons, 1):
                                    st.write(f"{i}. {reason}")

                                if not reasons:
                                    st.write(
                                        "The records exist in both systems but the calculated totals differ. This may require manual investigation."
                                    )
                    else:
                        st.error(
                            f"Invoice number `{inspect_invoice}` was not found in either Excel or Flowwer system"
                        )

                st.markdown("---")
                st.markdown("### View Side-by-Side Comparison")

                tab1, tab2, tab3, tab4 = st.tabs(
                    [
                        "All Mismatches",
                        "Date Issues",
                        "Cost Center Issues",
                        "Amount Issues",
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
                    ).dt.strftime("%Y-%m-%d")
                    display_df["DATEV_Date"] = pd.to_datetime(
                        display_df["DATEV_Date"]
                    ).dt.strftime("%Y-%m-%d")

                    display_df["Flowwer_Amount"] = display_df["Flowwer_Amount"].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else ""
                    )
                    display_df["DATEV_Amount"] = display_df["DATEV_Amount"].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else ""
                    )
                    display_df["Amount_Diff"] = display_df["Amount_Diff"].apply(
                        lambda x: f"{x:.2f}" if pd.notna(x) else ""
                    )

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=400,
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
                        ).dt.strftime("%Y-%m-%d")
                        display_date_df["DATEV_Date"] = pd.to_datetime(
                            display_date_df["DATEV_Date"]
                        ).dt.strftime("%Y-%m-%d")

                        display_date_df["Flowwer_Amount"] = display_date_df[
                            "Flowwer_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                        st.dataframe(
                            display_date_df,
                            use_container_width=True,
                            height=400,
                        )
                    else:
                        st.success("All Invoice Dates match!")

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

                        display_cc_df["Flowwer_Amount"] = display_cc_df[
                            "Flowwer_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                        display_cc_df["DATEV_Amount"] = display_cc_df[
                            "DATEV_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                        st.dataframe(
                            display_cc_df,
                            use_container_width=True,
                            height=400,
                        )
                    else:
                        st.success("All Cost Centers match!")

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

                        display_amount_df["Flowwer_Amount"] = display_amount_df[
                            "Flowwer_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                        display_amount_df["DATEV_Amount"] = display_amount_df[
                            "DATEV_Amount"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                        display_amount_df["Amount_Diff"] = display_amount_df[
                            "Amount_Diff"
                        ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                        st.dataframe(
                            display_amount_df,
                            use_container_width=True,
                            height=400,
                        )
                    else:
                        st.success("All Amounts match!")
            else:
                st.success("Perfect! All Flowwer records match DATEV exactly!")

            not_in_datev_df = df_results[df_results["Status"] == "Not in DATEV"]
            if len(not_in_datev_df) > 0:
                st.markdown(
                    """
                    <div style="
                        border-left: 3px solid #ef4444;
                        padding: 0.75rem 1.25rem;
                        border-radius: 8px;
                        margin: 2rem 0 1rem 0;
                        background: rgba(239, 68, 68, 0.03);
                    ">
                        <h3 style="margin: 0; color: #ef4444; font-size: 1rem; font-weight: 600; letter-spacing: 0.5px;">NOT IN DATEV</h3>
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
                ).dt.strftime("%Y-%m-%d")

                display_not_found_df["Flowwer_Amount"] = display_not_found_df[
                    "Flowwer_Amount"
                ].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

                st.dataframe(
                    display_not_found_df,
                    use_container_width=True,
                    height=300,
                )

                st.markdown("### Export Complete Cross-Check Report")

                col1, col2 = st.columns(2)

                with col1:
                    csv_full = df_results.to_csv(index=False)
                    st.download_button(
                        label="CSV - Complete Report",
                        data=csv_full,
                        file_name=f"crosscheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with col2:
                    excel_full = to_excel(df_results)
                    st.download_button(
                        label="Excel - Complete Report",
                        data=excel_full,
                        file_name=f"crosscheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

    elif "excel_data" in st.session_state and st.session_state.excel_data is not None:
        st.info("Load Flowwer data to enable comparison")
    elif (
        "flowwer_data" in st.session_state and st.session_state.flowwer_data is not None
    ):
        st.info("Load Excel data to enable comparison")
    else:
        st.info("Load both Excel and Flowwer data to start comparison")
