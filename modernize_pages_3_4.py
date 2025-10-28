#!/usr/bin/env python3
"""Modernize Approved Documents and Pending Approvals pages (Pages 3 & 4)"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================================
# PAGE 3: APPROVED DOCUMENTS
# ============================================================================

old_approved_header = """elif page == "✅ " + t('pages.approved_docs'):
    st.header("✅ " + t('approved_docs_page.title'))
    st.markdown("*" + t('approved_docs_page.subtitle') + "*")
    
    # Get companies/flows for filtering
    col1, col2 = st.columns([2, 1])"""

new_approved_header = '''elif page == "✅ " + t('pages.approved_docs'):
    # Glossy page header card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(22, 163, 74, 0.05) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 1.75rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid rgba(34, 197, 94, 0.2);
            box-shadow: 0 4px 24px rgba(34, 197, 94, 0.12),
                        0 2px 6px rgba(0, 0, 0, 0.04);
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.9) 0%, rgba(22, 163, 74, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(34, 197, 94, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">✅</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                    color: #15803d;
                ">{t('approved_docs_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    color: #64748b;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">{t('approved_docs_page.subtitle')}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Get companies/flows for filtering
    col1, col2 = st.columns([3, 1])'''

content = content.replace(old_approved_header, new_approved_header)

# Update Approved Documents button
old_approved_button = """    with col2:
        st.write("")
        st.write("")
        if st.button("   " + t('approved_docs_page.load_documents'), type="primary"):"""

new_approved_button = """    with col2:
        st.write("")
        st.write("")
        if st.button(
            "   " + t('approved_docs_page.load_documents'), 
            type="primary",
            use_container_width=True,
            key="btn_load_approved_docs"
        ):"""

content = content.replace(old_approved_button, new_approved_button)

# Update approved documents download buttons
old_approved_export = """        # Export
        st.markdown("---")
        st.subheader("  " + t('approved_docs_page.export'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="  Download as CSV",
                data=csv,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = json.dumps(docs, indent=2)
            st.download_button(
                label="  Download as JSON",
                data=json_data,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )"""

new_approved_export = """        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💾 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="  Download CSV",
                data=csv,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = json.dumps(docs, indent=2)
            st.download_button(
                label="  Download JSON",
                data=json_data,
                file_name=f"approved_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )"""

content = content.replace(old_approved_export, new_approved_export)

# ============================================================================
# PAGE 4: SIGNABLE DOCUMENTS (PENDING APPROVALS)
# ============================================================================

old_signable_header = """elif page == "⏳ " + t('pages.signable_docs'):
    st.header("⏳ " + t('signable_docs_page.title'))
    st.markdown("*" + t('signable_docs_page.subtitle') + "*")
    
    col1, col2 = st.columns([2, 1])"""

new_signable_header = '''elif page == "⏳ " + t('pages.signable_docs'):
    # Glossy page header card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 1.75rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid rgba(245, 158, 11, 0.2);
            box-shadow: 0 4px 24px rgba(245, 158, 11, 0.12),
                        0 2px 6px rgba(0, 0, 0, 0.04);
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.9) 0%, rgba(217, 119, 6, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(245, 158, 11, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">⏳</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                    color: #b45309;
                ">{t('signable_docs_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    color: #64748b;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">{t('signable_docs_page.subtitle')}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])'''

content = content.replace(old_signable_header, new_signable_header)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Modernized Approved Documents & Pending Approvals pages!")
print("Features added:")
print("  ✓ Page 3: Glossy green header with icon card")
print("  ✓ Page 3: Consistent button styling")
print("  ✓ Page 3: Modern export section")
print("  ✓ Page 4: Glossy orange/amber header with icon card")
print("  ✓ Page 4: Consistent column widths")
