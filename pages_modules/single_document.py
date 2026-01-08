"""
Single Document Page Module
View detailed information about a specific document with receipt splits
"""

import streamlit as st
import pandas as pd
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


def normalize_split(split):
    """
    Normalize a receipt split to ensure it's a dictionary.
    Handles cases where the API returns JSON strings instead of parsed objects.
    """
    return normalize_dict(split)


def normalize_splits(splits):
    """
    Normalize a list of receipt splits to ensure all items are dictionaries.
    Handles various API response formats.
    """
    if not splits:
        return []

    if isinstance(splits, dict):
        if "documentReceiptSplits" in splits:
            splits = splits["documentReceiptSplits"]
        elif "splits" in splits:
            splits = splits["splits"]
        elif "receiptSplits" in splits:
            splits = splits["receiptSplits"]
        elif "data" in splits:
            splits = splits["data"]
        else:
            return [splits]

    if isinstance(splits, str):
        try:
            parsed = json.loads(splits)
            return normalize_splits(parsed)
        except (json.JSONDecodeError, ValueError):
            return []

    if not isinstance(splits, list):
        return []

    normalized = []
    for split in splits:
        normalized_split = normalize_split(split)

        if normalized_split and isinstance(normalized_split, dict):
            if "raw" in normalized_split and len(normalized_split) == 1:
                raw_value = normalized_split["raw"]
                if isinstance(raw_value, str) and raw_value != "documentReceiptSplits":
                    try:
                        parsed = json.loads(raw_value)
                        if isinstance(parsed, list):
                            return normalize_splits(parsed)
                        elif isinstance(parsed, dict):
                            normalized.append(parsed)
                    except (json.JSONDecodeError, ValueError):
                        pass
            elif "raw" not in normalized_split or len(normalized_split) > 1:
                normalized.append(normalized_split)

    return normalized


def render_single_document_page(
    client,
    t,
    get_page_header_purple,
    get_action_bar_styles,
    get_info_box_styles,
    get_card_styles,
    get_metric_styles,
    get_tab_styles,
    get_theme_text_styles,
    get_section_header_styles,
    to_excel,
):
    """Render the Single Document page with detailed document information and receipt splits"""

    st.markdown(
        get_page_header_purple()
        + get_action_bar_styles()
        + get_info_box_styles()
        + get_card_styles()
        + get_metric_styles()
        + get_tab_styles()
        + get_theme_text_styles()
        + get_section_header_styles(),
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="page-header-purple" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(139, 92, 246, 0.9) 0%, rgba(124, 58, 237, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(139, 92, 246, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">🔎</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('single_document_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">View detailed information about a specific document</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Search by Document ID or Invoice Number")

    col1, col2 = st.columns(2)

    with col1:
        search_type = st.radio(
            "Search by:",
            options=["Document ID", "Invoice Number"],
            horizontal=True,
            help="Choose whether to search by Document ID or Invoice Number",
            key="single_doc_search_type",
        )

    with col2:
        pass

    col1, col2 = st.columns([4, 1])

    with col1:
        if search_type == "Document ID":
            search_value = st.number_input(
                "Document ID",
                min_value=1,
                step=1,
                value=1,
                help="Enter the unique document ID to retrieve details",
            )
        else:
            search_value = st.text_input(
                "Invoice Number",
                placeholder="Enter invoice number...",
                help="Enter the invoice number to search for the document",
            )

    with col2:
        st.markdown('<div style="margin-top: 1.85rem;"></div>', unsafe_allow_html=True)
        if st.button(
            "Search",
            type="primary",
            use_container_width=True,
            key="btn_get_document_details",
        ):
            with st.spinner("🔍 Searching..."):
                doc = None

                if search_type == "Document ID":
                    doc = st.session_state.client.get_document(int(search_value))
                    if doc:
                        doc = normalize_dict(doc)
                    doc_id = int(search_value)
                else:
                    if search_value:
                        all_docs = st.session_state.get("documents")

                        if not all_docs:
                            with st.spinner("Downloading document list..."):
                                all_docs = st.session_state.client.get_all_documents(
                                    include_processed=True
                                )
                                if all_docs:
                                    st.session_state.documents = all_docs

                        if all_docs:
                            matching_docs = []
                            search_val_lower = str(search_value).lower().strip()

                            for d in all_docs:
                                normalized_d = normalize_dict(d)
                                inv_num = (
                                    str(normalized_d.get("invoiceNumber", ""))
                                    .lower()
                                    .strip()
                                )

                                if inv_num == search_val_lower:
                                    matching_docs.append(normalized_d)

                            if matching_docs:
                                doc = matching_docs[0]
                                doc_id = doc.get("documentId")
                            else:
                                st.error(
                                    f"❌ No document found with invoice number: {search_value}"
                                )
                        else:
                            st.error("Failed to retrieve documents")
                    else:
                        st.warning("Please enter an invoice number")

                if doc:
                    doc = normalize_dict(doc)
                    st.session_state.selected_document = doc
                    if "doc_id" in locals() and doc_id:
                        normalized_splits = []
                        if isinstance(doc, dict):
                            embedded_splits = doc.get("receiptSplits") or doc.get(
                                "documentReceiptSplits"
                            )
                            if embedded_splits:
                                normalized_splits = normalize_splits(embedded_splits)

                        if not normalized_splits:
                            splits = st.session_state.client.get_receipt_splits(
                                int(doc_id)
                            )
                            if splits:
                                normalized_splits = normalize_splits(splits)
                                if not normalized_splits or all(
                                    isinstance(s, dict) and "raw" in s and len(s) == 1
                                    for s in normalized_splits
                                ):
                                    full_doc = st.session_state.client.get_document(
                                        int(doc_id)
                                    )
                                    if full_doc and isinstance(full_doc, dict):
                                        full_doc = normalize_dict(full_doc)
                                        embedded_splits = full_doc.get(
                                            "receiptSplits"
                                        ) or full_doc.get("documentReceiptSplits")
                                        if embedded_splits:
                                            normalized_splits = normalize_splits(
                                                embedded_splits
                                            )
                                            st.session_state.selected_document = (
                                                full_doc
                                            )

                        st.session_state.receipt_splits = normalized_splits
                    else:
                        st.session_state.receipt_splits = []

                    if search_type == "Document ID":
                        st.success(f"Document #{doc_id} loaded successfully")
                    else:
                        st.success(
                            f"Document found! (ID: {doc_id}, Invoice: {search_value})"
                        )
                elif search_type == "Document ID":
                    st.error(f"Document #{search_value} not found")

    if st.session_state.selected_document:
        doc = st.session_state.selected_document
        doc = normalize_dict(doc)
        splits = st.session_state.get("receipt_splits", [])
        splits = normalize_splits(splits)

        if splits:
            st.markdown(
                f"""
                <div class="info-box-green">
                    <span style="font-weight: 600;">
                        Found {len(splits)} receipt split(s) (Belegaufteilung) for this document
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander(
                "Receipt Splits / Belegaufteilung - Click to expand", expanded=True
            ):
                for idx, split in enumerate(splits, 1):
                    st.markdown(
                        f"""
                        <div class="info-box-yellow">
                            <h3 style="margin: 0;"> Split #{idx}</h3>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        cost_center = (
                            split.get("costCenter")
                            or split.get("costcenter")
                            or split.get("CostCenter")
                            or split.get("cost_center")
                            or "N/A"
                        )
                        st.metric("Cost Center", cost_center)
                        net_value = (
                            split.get("netValue")
                            or split.get("netAmount")
                            or split.get("net_value")
                            or split.get("net_amount")
                            or 0
                        )
                        st.metric("Net Value", f"€{float(net_value):,.2f}")

                    with col2:
                        cost_unit = (
                            split.get("costUnit")
                            or split.get("costunit")
                            or split.get("CostUnit")
                            or split.get("cost_unit")
                            or split.get("kost2")
                            or split.get("KOST2")
                            or split.get("Kost2")
                            or split.get("costUnit2")
                            or split.get("cost_unit2")
                            or split.get("account")
                        )

                        if not cost_unit or cost_unit == "N/A":
                            if isinstance(doc, dict):
                                cost_unit = (
                                    doc.get("costUnit")
                                    or doc.get("costunit")
                                    or doc.get("CostUnit")
                                    or doc.get("cost_unit")
                                    or doc.get("kost2")
                                    or doc.get("KOST2")
                                    or doc.get("Kost2")
                                )

                        if not cost_unit:
                            cost_unit = "Not set"

                        st.metric("Cost Unit", cost_unit)
                        gross_value = (
                            split.get("grossValue")
                            or split.get("grossAmount")
                            or split.get("gross_value")
                            or split.get("gross_amount")
                            or 0
                        )
                        st.metric("Gross Value", f"€{float(gross_value):,.2f}")

                    with col3:
                        st.metric("Tax %", f"{split.get('taxPercent', 0):.1f}%")
                        st.write("**Booking Text:**")
                        booking_text = (
                            split.get("bookingText")
                            or split.get("name")
                            or split.get("booking_text")
                            or split.get("BookingText")
                            or "N/A"
                        )
                        st.info(booking_text)

                    with col4:
                        invoice_number = (
                            split.get("invoiceNumber")
                            or split.get("invoice_number")
                            or (
                                doc.get("invoiceNumber")
                                if isinstance(doc, dict)
                                else None
                            )
                            or "N/A"
                        )
                        st.write("**Invoice Number:**", invoice_number)

                        invoice_date = (
                            split.get("invoiceDate")
                            or split.get("invoice_date")
                            or (
                                doc.get("invoiceDate")
                                if isinstance(doc, dict)
                                else None
                            )
                            or "N/A"
                        )
                        st.write("**Invoice Date:**", invoice_date)

                        payment_state = (
                            split.get("paymentState")
                            or split.get("payment_state")
                            or (
                                doc.get("paymentState")
                                if isinstance(doc, dict)
                                else None
                            )
                            or "N/A"
                        )
                        st.write("**Payment State:**", payment_state)

                    with st.expander(f"🔍 All fields for split #{idx}"):
                        split_items = split.items()
                        if "raw" in split and len(split) == 1:
                            st.warning(
                                f"Split #{idx} appears to be invalid. Raw value: {split.get('raw')}"
                            )
                            st.info(
                                "💡 Tip: The receipt splits might be embedded in the document object. Check the 'Raw JSON' tab."
                            )
                        else:
                            split_df = pd.DataFrame(
                                [
                                    {"Field": key, "Value": value}
                                    for key, value in split_items
                                ]
                            )
                            st.dataframe(
                                split_df, use_container_width=True, hide_index=True
                            )

                    if idx < len(splits):
                        st.markdown("---")

                splits_df = pd.DataFrame(splits)

                col1, col2 = st.columns(2)

                with col1:
                    csv_splits = splits_df.to_csv(index=False)
                    st.download_button(
                        label=t("common.download_csv"),
                        data=csv_splits,
                        file_name=f"document_{doc.get('documentId', 'unknown')}_splits.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                with col2:
                    excel_splits = to_excel(splits_df)
                    st.download_button(
                        label=t("common.download_excel"),
                        data=excel_splits,
                        file_name=f"document_{doc.get('documentId', 'unknown')}_splits.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
        else:
            st.markdown(
                f"""
                <div class="info-box-blue" style="
                    background: linear-gradient(135deg, 
                        rgba(255, 255, 255, 0.9) 0%, 
                        rgba(255, 255, 255, 0.7) 50%,
                        rgba(59, 130, 246, 0.06) 100%) !important;
                    backdrop-filter: blur(16px) saturate(180%) !important;
                    -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                    border: 1px solid rgba(59, 130, 246, 0.3) !important;
                    border-radius: 16px !important;
                    padding: 1rem !important;
                    margin-bottom: 1rem !important;
                    box-shadow: 
                        0 4px 16px rgba(59, 130, 246, 0.1),
                        0 2px 8px rgba(0, 0, 0, 0.04),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
                ">
                    <span style="font-size: 1.25rem;">ℹ️</span>
                    <span style="color: #1e40af; font-weight: 500;">
                        {t('single_document_page.no_receipt_splits')}
                    </span>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="section-header">
                <div class="section-icon">📋</div>
                <h3>{t('single_document_page.overview')}</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Document ID", doc.get("documentId"))
            st.metric("Stage", doc.get("currentStage", "N/A"))

        with col2:
            st.metric(
                "Total Gross",
                f"{doc.get('totalGross', 0):.2f} {doc.get('currencyCode', 'EUR')}",
            )
            st.metric(
                "Total Net",
                f"{doc.get('totalNet', 0):.2f} {doc.get('currencyCode', 'EUR')}",
            )

        with col3:
            st.metric("Company", doc.get("companyName", "N/A"))
            st.metric("Flow", doc.get("flowName", "N/A"))

        with col4:
            st.metric("Payment State", doc.get("paymentState", "N/A"))
            st.metric("Supplier", doc.get("supplierName", "N/A"))

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="section-header">
                <h3>Detailed Information</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📋 All Fields", "💰 Financial", "📅 Dates", "👤 Parties", "🔧 Raw JSON"]
        )

        with tab1:
            st.markdown("**Complete Document Details**")

            def flatten_value(value, indent=0):
                """Flatten nested dictionaries and lists into readable text"""
                if value is None:
                    return "N/A"
                elif isinstance(value, bool):
                    return "✅ Yes" if value else "❌ No"
                elif isinstance(value, dict):
                    # Format dictionary as bullet points
                    items = []
                    for k, v in value.items():
                        if isinstance(v, (dict, list)):
                            items.append(f"  • {k}: {flatten_value(v, indent+1)}")
                        else:
                            items.append(f"  • {k}: {v}")
                    return "\n" + "\n".join(items)
                elif isinstance(value, list):
                    if not value:
                        return "[]"
                    items = []
                    for i, item in enumerate(value, 1):
                        if isinstance(item, (dict, list)):
                            items.append(f"  [{i}] {flatten_value(item, indent+1)}")
                        else:
                            items.append(f"  • {item}")
                    return "\n" + "\n".join(items)
                elif isinstance(value, (int, float)):
                    return f"{value:,}" if isinstance(value, int) else f"{value:.2f}"
                else:
                    return str(value)

            all_fields = {}
            nested_fields = {}

            for key, value in doc.items():
                readable_key = key.replace("_", " ").replace("  ", " ").title()

                if isinstance(value, (dict, list)) and value:
                    nested_fields[readable_key] = value
                    all_fields[readable_key] = flatten_value(value)
                else:
                    all_fields[readable_key] = flatten_value(value)

            df_details = pd.DataFrame(
                [
                    {"Field": key, "Value": value}
                    for key, value in sorted(all_fields.items())
                ]
            )

            st.dataframe(
                df_details, use_container_width=True, hide_index=True, height=600
            )

            st.info(
                f" Showing {len(all_fields)} fields returned by the API ({len(nested_fields)} complex/nested fields)"
            )

            if nested_fields:
                with st.expander(
                    f"🔍 Expand Complex Fields ({len(nested_fields)} fields with nested data)"
                ):
                    for field_name, field_value in sorted(nested_fields.items()):
                        st.markdown(f"**{field_name}:**")
                        if isinstance(field_value, dict):
                            nested_df = pd.DataFrame(
                                [
                                    {"Property": k, "Value": v}
                                    for k, v in field_value.items()
                                ]
                            )
                            st.dataframe(
                                nested_df, use_container_width=True, hide_index=True
                            )
                        elif isinstance(field_value, list):
                            if field_value and isinstance(field_value[0], dict):
                                # List of dictionaries - show as table
                                st.dataframe(
                                    pd.DataFrame(field_value),
                                    use_container_width=True,
                                    hide_index=True,
                                )
                            else:
                                for item in field_value:
                                    st.write(f"  • {item}")
                        st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                csv_data = df_details.to_csv(index=False)
                st.download_button(
                    label=t("common.download_csv"),
                    data=csv_data,
                    file_name=f"document_{doc.get('documentId', 'unknown')}_all_fields.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                excel_data = to_excel(df_details)
                st.download_button(
                    label=t("common.download_excel"),
                    data=excel_data,
                    file_name=f"document_{doc.get('documentId', 'unknown')}_all_fields.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            with st.expander("🔍 View Raw Field Names (for debugging)"):
                st.code(", ".join(sorted(doc.keys())), language="text")

        with tab2:
            st.markdown("**💰 Financial Information**")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Gross", f"€{doc.get('totalGross', 0):,.2f}")
                st.metric("Total Net", f"€{doc.get('totalNet', 0):,.2f}")
                st.metric("Tax Amount", f"€{doc.get('taxAmount', 0):,.2f}")
                st.write("**Currency:**", doc.get("currencyCode", "EUR"))

            with col2:
                st.metric("Discount Amount", f"€{doc.get('discountAmount', 0):,.2f}")
                st.metric("Discount Rate", f"{doc.get('discountRate', 0):.2f}%")
                st.write("**Payment State:**", doc.get("paymentState", "N/A"))
                st.write("**Payment Method:**", doc.get("paymentMethod", "N/A"))

            st.markdown("---")
            st.write("**Accounting Details:**")

            cost_center = (
                doc.get("costCenter")
                or doc.get("costcenter")
                or doc.get("CostCenter")
                or doc.get("cost_center")
                or doc.get("kost1")
                or doc.get("KOST1")
            )

            cost_unit = (
                doc.get("costUnit")
                or doc.get("costunit")
                or doc.get("CostUnit")
                or doc.get("cost_unit")
                or doc.get("kost2")
                or doc.get("KOST2")
            )

            booking_text = (
                doc.get("bookingText")
                or doc.get("bookingtext")
                or doc.get("BookingText")
                or doc.get("booking_text")
                or doc.get("name")
            )

            if not cost_center and splits:
                first_split = normalize_split(splits[0]) if splits else {}
                cost_center = (
                    first_split.get("costCenter")
                    or first_split.get("costcenter")
                    or first_split.get("CostCenter")
                    or first_split.get("cost_center")
                )

            if not cost_unit and splits:
                first_split = normalize_split(splits[0]) if splits else {}
                cost_unit = (
                    first_split.get("costUnit")
                    or first_split.get("costunit")
                    or first_split.get("CostUnit")
                    or first_split.get("cost_unit")
                    or first_split.get("kost2")
                    or first_split.get("KOST2")
                    or first_split.get("Kost2")
                    or first_split.get("costUnit2")
                    or first_split.get("cost_unit2")
                )

            if not booking_text and splits:
                first_split = normalize_split(splits[0]) if splits else {}
                booking_text = (
                    first_split.get("bookingText")
                    or first_split.get("name")
                    or first_split.get("BookingText")
                    or first_split.get("booking_text")
                )

            if splits and (cost_center or cost_unit or booking_text):
                st.info(" Accounting details from Receipt Splits (Belegaufteilung)")

            st.write("- **Cost Center:**", cost_center or "N/A")
            st.write("- **Cost Unit (KOST2):**", cost_unit or "N/A")
            st.write("- **Booking Text:**", booking_text or "N/A")

            if splits and len(splits) > 1:
                st.warning(
                    f"⚠️ This document has {len(splits)} receipt splits. Values shown are from the first split. Check the Receipt Splits section for all values."
                )

        with tab3:
            st.markdown("**📅 Date Information**")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Invoice Date:**", doc.get("invoiceDate", "N/A"))
                st.write(
                    "**Receipt Date:**",
                    doc.get("receiptDate", doc.get("uploadTime", "N/A")),
                )
                st.write("**Upload Time:**", doc.get("uploadTime", "N/A"))
                st.write("**Due Date:**", doc.get("dueDate", "N/A"))

            with col2:
                st.write("**Payment Date:**", doc.get("paymentDate", "N/A"))
                st.write("**Service Start:**", doc.get("serviceStartDate", "N/A"))
                st.write("**Service End:**", doc.get("serviceEndDate", "N/A"))
                st.write(
                    "**Discount Period End:**", doc.get("discountPeriodEnd", "N/A")
                )

        with tab4:
            st.markdown("**👤 Parties Information**")

            st.write("### Supplier Details")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Name:**", doc.get("supplierName", "N/A"))
                st.write("**VAT ID:**", doc.get("supplierVATId", "N/A"))
                st.write("**Street:**", doc.get("supplierStreet", "N/A"))
                st.write("**City:**", doc.get("supplierCity", "N/A"))

            with col2:
                st.write("**Postal Code:**", doc.get("supplierPostalCode", "N/A"))
                st.write("**Country:**", doc.get("supplierCountry", "N/A"))
                st.write("**IBAN:**", doc.get("iban", "N/A"))
                st.write("**BIC:**", doc.get("bic", "N/A"))

            st.markdown("---")
            st.write("### Company Details")
            st.write("**Company:**", doc.get("companyName", "N/A"))
            st.write("**Flow:**", doc.get("flowName", "N/A"))

        with tab5:
            st.markdown("**🔧 Complete Raw JSON Data**")

            st.info(f"Total fields in API response: {len(doc)}")

            search_term = st.text_input(
                "🔍 Search in JSON data:", placeholder="e.g., booking, cost, date"
            )

            if search_term:
                filtered_doc = {
                    k: v
                    for k, v in doc.items()
                    if search_term.lower() in k.lower()
                    or (isinstance(v, str) and search_term.lower() in v.lower())
                }
                st.write(f"Found {len(filtered_doc)} matching fields:")
                st.json(filtered_doc)
            else:
                st.json(doc)
