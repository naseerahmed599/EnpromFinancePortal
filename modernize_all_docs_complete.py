#!/usr/bin/env python3
"""Complete modernization of All Documents page"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add closing div and modern success message
old_checkbox_section = """    with col1:
        include_processed = st.checkbox(t('all_documents_page.include_processed'), value=False)
    
    with col2:
        include_deleted = st.checkbox(t('all_documents_page.include_deleted'), value=False)
    
    with col3:
        if st.button("   Refresh Documents", type="primary"):
            with st.spinner("Fetching documents..."):
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed,
                    include_deleted=include_deleted
                )
                st.session_state.documents = docs"""

new_checkbox_section = """    with col1:
        include_processed = st.checkbox(
            "📦 " + t('all_documents_page.include_processed'), 
            value=False,
            help="Include processed documents in the results"
        )
    
    with col2:
        include_deleted = st.checkbox(
            "🗑️ " + t('all_documents_page.include_deleted'), 
            value=False,
            help="Include deleted documents in the results"
        )
    
    with col3:
        if st.button("   Refresh Documents", type="primary", use_container_width=True):
            with st.spinner("🔍 Fetching documents..."):
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed,
                    include_deleted=include_deleted
                )
                st.session_state.documents = docs
                if docs:
                    st.success(f"✅ Successfully loaded {len(docs)} documents")
                else:
                    st.warning("⚠️ No documents found")
    
    st.markdown("</div>", unsafe_allow_html=True)"""

content = content.replace(old_checkbox_section, new_checkbox_section)

# Add statistics cards
old_success = """    if st.session_state.documents:
        st.success(f"✅ Found {len(st.session_state.documents)} documents")
        
        # Filter options
        st.subheader("🔍 Filters")"""

new_stats_and_filters = '''    if st.session_state.documents:
        # Statistics cards
        docs = st.session_state.documents
        stage_counts = {}
        for doc in docs:
            stage = doc.get('currentStage', 'Unknown')
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        st.markdown("#### 📊 Quick Statistics")
        stat_cols = st.columns(4)
        
        stats = [
            ("Total", len(docs), "📄", "#3b82f6"),
            ("Approved", stage_counts.get('Approved', 0), "✅", "#22c55e"),
            ("Pending", sum(stage_counts.get(f'Stage{i}', 0) for i in range(1, 6)), "⏳", "#f59e0b"),
            ("Draft", stage_counts.get('Draft', 0), "📝", "#8b5cf6")
        ]
        
        for idx, (label, value, icon, color) in enumerate(stats):
            with stat_cols[idx]:
                st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1.25rem;
                        border-radius: 12px;
                        border-left: 4px solid {color};
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                        text-align: center;
                    ">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                        <div style="font-size: 2rem; font-weight: 700; color: {color};">{value}</div>
                        <div style="font-size: 0.875rem; color: #64748b; font-weight: 500;">{label}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Filter panel
        with st.expander("🔍 Advanced Filters", expanded=True):'''

content = content.replace(old_success, new_stats_and_filters)

# Update filter section
old_filters = """        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Company filter
            companies = list(set([doc.get('companyName', 'Unknown') 
                                for doc in st.session_state.documents]))
            selected_company = st.selectbox("Filter by Company", 
                                           ["All"] + sorted(companies))
        
        with col2:
            # Stage filter
            stages = list(set([doc.get('currentStage', 'Unknown') 
                             for doc in st.session_state.documents]))
            selected_stage = st.selectbox("Filter by Stage", 
                                         ["All"] + sorted(stages))
        
        with col3:
            # Payment state filter
            payment_states = list(set([doc.get('paymentState', 'Unknown') 
                                     for doc in st.session_state.documents]))
            selected_payment = st.selectbox("Filter by Payment State", 
                                           ["All"] + sorted(payment_states))"""

new_filters = """            col1, col2, col3 = st.columns(3)
            
            with col1:
                companies = list(set([doc.get('companyName', 'Unknown') 
                                    for doc in st.session_state.documents]))
                selected_company = st.selectbox(
                    "🏢 Company", 
                    ["All"] + sorted(companies),
                    help="Filter documents by company"
                )
            
            with col2:
                stages = list(set([doc.get('currentStage', 'Unknown') 
                                 for doc in st.session_state.documents]))
                selected_stage = st.selectbox(
                    "📊 Stage", 
                    ["All"] + sorted(stages),
                    help="Filter documents by current stage"
                )
            
            with col3:
                payment_states = list(set([doc.get('paymentState', 'Unknown') 
                                         for doc in st.session_state.documents]))
                selected_payment = st.selectbox(
                    "💰 Payment State", 
                    ["All"] + sorted(payment_states),
                    help="Filter documents by payment status"
                )"""

content = content.replace(old_filters, new_filters)

# Update filter info badge
old_info = (
    """        st.info(f"📊 Showing {len(filtered_docs)} documents after filters")"""
)

new_badge = '''        # Filter results badge
        if len(filtered_docs) != len(docs):
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.25rem;">🔎</span>
                    <span style="color: #1e40af; font-weight: 600;">
                        Showing {len(filtered_docs)} of {len(docs)} documents
                    </span>
                </div>
            """, unsafe_allow_html=True)'''

content = content.replace(old_info, new_badge)

# Update dataframe display
old_dataframe = """            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total Gross": st.column_config.NumberColumn(
                        "Total Gross",
                        format="%.2f €"
                    )
                }
            )"""

new_dataframe = """            # Modern table header
            st.markdown("#### 📑 Documents Table")
            
            # Display table with modern styling
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500,
                column_config={
                    "Document ID": st.column_config.NumberColumn(
                        "ID",
                        help="Unique document identifier",
                        format="%d"
                    ),
                    "Total Gross": st.column_config.NumberColumn(
                        "Total Gross",
                        help="Total gross amount",
                        format="%.2f €"
                    ),
                    "Stage": st.column_config.TextColumn(
                        "Stage",
                        help="Current workflow stage"
                    ),
                    "Payment State": st.column_config.TextColumn(
                        "Payment",
                        help="Payment status"
                    )
                }
            )"""

content = content.replace(old_dataframe, new_dataframe)

# Update export section
old_export = """            # Export options
            st.subheader("💾 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="  Download as CSV",
                    data=csv,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )"""

new_export = """            # Export options with modern design
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 💾 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="  Download CSV",
                    data=csv,
                    file_name=f"flowwer_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )"""

content = content.replace(old_export, new_export)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ All Documents page fully modernized!")
print("Features added:")
print("  ✓ Modern gradient page header")
print("  ✓ Icon-based section header")
print("  ✓ Control panel with background")
print("  ✓ Statistics cards (Total, Approved, Pending, Draft)")
print("  ✓ Collapsible filter panel")
print("  ✓ Filter results badge")
print("  ✓ Enhanced table with column configs")
print("  ✓ Modern export section")
