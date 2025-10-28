#!/usr/bin/env python3
"""Modernize Document Details page (Page 2)"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace page header
old_header = """elif page == "🔎 " + t('pages.single_document'):
    st.header("🔎 " + t('single_document_page.title'))
    
    col1, col2 = st.columns([2, 1])"""

new_header = '''elif page == "🔎 " + t('pages.single_document'):
    # Page header with icon card
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;
                    margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                        width: 48px; height: 48px; border-radius: 12px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 24px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);">🔎</div>
            <div>
                <h2 style="margin: 0; font-size: 1.75rem; font-weight: 700;">
                    {t('single_document_page.title')}</h2>
                <p style="margin: 0; color: #64748b; font-size: 0.95rem;">
                    View detailed information about a specific document</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Modern search panel
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;
                    margin-bottom: 1.5rem;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])'''

content = content.replace(old_header, new_header)

# Add search panel closing and button styling
old_search = """    with col1:
        doc_id = st.number_input(t('single_document_page.enter_id'), min_value=1, step=1, value=1)
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🔍 " + t('common.get_document'), type="primary"):
            with st.spinner(t('common.loading')):
                doc = st.session_state.client.get_document(doc_id)
                st.session_state.selected_document = doc
                # Also get receipt splits (Belegaufteilung)
                if doc:
                    splits = st.session_state.client.get_receipt_splits(doc_id)
                    st.session_state.receipt_splits = splits if splits else []"""

new_search = """    with col1:
        doc_id = st.number_input(
            "🔢 " + t('single_document_page.enter_id'), 
            min_value=1, 
            step=1, 
            value=1,
            help="Enter the unique document ID to retrieve details"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🔍 " + t('common.get_document'), type="primary", use_container_width=True):
            with st.spinner("🔍 " + t('common.loading')):
                doc = st.session_state.client.get_document(doc_id)
                st.session_state.selected_document = doc
                # Also get receipt splits (Belegaufteilung)
                if doc:
                    splits = st.session_state.client.get_receipt_splits(doc_id)
                    st.session_state.receipt_splits = splits if splits else []
                    st.success(f"✅ Document #{doc_id} loaded successfully")
                else:
                    st.error(f"❌ Document #{doc_id} not found")
    
    st.markdown("</div>", unsafe_allow_html=True)"""

content = content.replace(old_search, new_search)

# Modernize receipt splits section
old_splits_header = """        # Show receipt splits if available
        if splits:
            st.success(f"✅ Found {len(splits)} receipt split(s) (Belegaufteilung) for this document")
            
            with st.expander("📊 Receipt Splits / Belegaufteilung - Click to expand", expanded=True):"""

new_splits_header = '''        # Show receipt splits if available
        if splits:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                    border: 1px solid #10b981;
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.25rem;">✅</span>
                    <span style="color: #065f46; font-weight: 600;">
                        Found {len(splits)} receipt split(s) (Belegaufteilung) for this document
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📊 Receipt Splits / Belegaufteilung - Click to expand", expanded=True):'''

content = content.replace(old_splits_header, new_splits_header)

# Modernize split cards
old_split_metrics = """                for idx, split in enumerate(splits, 1):
                    st.markdown(f"### Split #{idx}")
                    
                    col1, col2, col3, col4 = st.columns(4)"""

new_split_metrics = '''                for idx, split in enumerate(splits, 1):
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                            padding: 1rem;
                            border-radius: 10px;
                            border-left: 4px solid #f59e0b;
                            margin-bottom: 1rem;
                        ">
                            <h3 style="margin: 0; color: #78350f;">📊 Split #{idx}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)'''

content = content.replace(old_split_metrics, new_split_metrics)

# Update no splits message
old_no_splits = """        else:
            st.info(" No receipt splits (Belegaufteilung) found for this document. The document may not have been split yet.")"""

new_no_splits = '''        else:
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                ">
                    <span style="font-size: 1.25rem;"></span>
                    <span style="color: #1e40af; font-weight: 500;">
                        No receipt splits (Belegaufteilung) found for this document. 
                        The document may not have been split yet.
                    </span>
                </div>
            """, unsafe_allow_html=True)'''

content = content.replace(old_no_splits, new_no_splits)

# Modernize Document Overview section
old_overview = """        # Document Overview
        st.subheader("📋 Document Overview")
        
        col1, col2, col3, col4 = st.columns(4)"""

new_overview = '''        # Document Overview with modern header
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                            width: 36px; height: 36px; border-radius: 8px;
                            display: flex; align-items: center; justify-content: center;
                            font-size: 18px;">📋</div>
                <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700;">Document Overview</h3>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)'''

content = content.replace(old_overview, new_overview)

# Modernize Detailed Information section
old_detailed = """        # Detailed Information
        st.subheader("📄 Detailed Information")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 All Fields", "💰 Financial", "📅 Dates", "👤 Parties", "🔧 Raw JSON"])"""

new_detailed = '''        # Detailed Information with modern header
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                            width: 36px; height: 36px; border-radius: 8px;
                            display: flex; align-items: center; justify-content: center;
                            font-size: 18px;">📄</div>
                <h3 style="margin: 0; font-size: 1.5rem; font-weight: 700;">Detailed Information</h3>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 All Fields", "💰 Financial", "📅 Dates", "👤 Parties", "🔧 Raw JSON"])'''

content = content.replace(old_detailed, new_detailed)

# Update download buttons
old_download1 = """            # Export option
            csv_data = df_details.to_csv(index=False)
            st.download_button(
                label="  Download All Fields as CSV",
                data=csv_data,
                file_name=f"document_{doc_id}_all_fields.csv",
                mime="text/csv"
            )"""

new_download1 = """            # Export option
            csv_data = df_details.to_csv(index=False)
            st.download_button(
                label="  Download All Fields as CSV",
                data=csv_data,
                file_name=f"document_{doc_id}_all_fields.csv",
                mime="text/csv",
                use_container_width=True
            )"""

content = content.replace(old_download1, new_download1)

# Update split download button
old_split_download = """                # Download splits as CSV
                splits_df = pd.DataFrame(splits)
                csv_splits = splits_df.to_csv(index=False)
                st.download_button(
                    label="  Download Receipt Splits as CSV",
                    data=csv_splits,
                    file_name=f"document_{doc_id}_splits.csv",
                    mime="text/csv"
                )"""

new_split_download = """                # Download splits as CSV
                splits_df = pd.DataFrame(splits)
                csv_splits = splits_df.to_csv(index=False)
                st.download_button(
                    label="  Download Receipt Splits as CSV",
                    data=csv_splits,
                    file_name=f"document_{doc_id}_splits.csv",
                    mime="text/csv",
                    use_container_width=True
                )"""

content = content.replace(old_split_download, new_split_download)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Document Details page (Page 2) fully modernized!")
print("Features added:")
print("  ✓ Modern gradient page header with icon card")
print("  ✓ Search panel with light gradient background")
print("  ✓ Success/error messages for document loading")
print("  ✓ Modern receipt splits badge (green gradient)")
print("  ✓ Split cards with yellow gradient backgrounds")
print("  ✓ Info message styling for no splits")
print("  ✓ Section headers with icon cards (Document Overview, Detailed Info)")
print("  ✓ Enhanced download buttons (full width)")
print("  ✓ Consistent spacing and visual hierarchy")
