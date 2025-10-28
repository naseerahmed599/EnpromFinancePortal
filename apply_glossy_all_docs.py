#!/usr/bin/env python3
"""Apply glossy styling to All Documents page header"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace All Documents page header with glossy version
old_all_docs_header = '''if page == "📋 " + t('pages.all_documents'):
    # Page header with icon
    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        ">
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            ">📋</div>
            <div>
                <h2 style="margin: 0; font-size: 1.75rem; font-weight: 700;">{t('all_documents_page.title')}</h2>
                <p style="margin: 0; color: #64748b; font-size: 0.95rem;">Browse and manage all documents in the system</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Modern control panel
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 1.5rem;
        ">
    """, unsafe_allow_html=True)'''

new_all_docs_header = '''if page == "📋 " + t('pages.all_documents'):
    # Glossy page header card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 1.75rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid rgba(59, 130, 246, 0.2);
            box-shadow: 0 4px 24px rgba(59, 130, 246, 0.12),
                        0 2px 6px rgba(0, 0, 0, 0.04);
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
                    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">{t('all_documents_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    color: #64748b;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Browse and manage all documents in the system</p>
            </div>
        </div>
    """, unsafe_allow_html=True)'''

content = content.replace(old_all_docs_header, new_all_docs_header)

# Remove the control panel wrapper div that's still there
old_control_div_close = """                else:
                    st.warning("⚠️ No documents found")
    
    if st.session_state.documents:"""

new_control_div_close = """                else:
                    st.warning("⚠️ No documents found")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.documents:"""

content = content.replace(old_control_div_close, new_control_div_close)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Applied glossy styling to All Documents page!")
print("Changes applied:")
print("  ✓ Glossy page header with backdrop blur")
print("  ✓ Enhanced icon card with double shadows")
print("  ✓ Gradient text effect on title")
print("  ✓ Premium borders and spacing")
print("  ✓ Maintained control panel wrapper properly")
