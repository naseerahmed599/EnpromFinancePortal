#!/usr/bin/env python3
"""Script to modernize the All Documents page"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the old title section
old_title = """# Title and header
st.title("💼 " + t('app_title'))
st.markdown("---")"""

new_title = '''# Modern page title with gradient
st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">💼 {t('app_title')}</h1>
        <p style="
            color: rgba(255, 255, 255, 0.9);
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
        ">{t('tagline')}</p>
    </div>
""", unsafe_allow_html=True)'''

content = content.replace(old_title, new_title)

# Now modernize the All Documents page
old_all_docs_start = """if page == "📋 " + t('pages.all_documents'):
    st.header("📋 " + t('all_documents_page.title'))
    
    col1, col2, col3 = st.columns([1, 1, 2])"""

new_all_docs_start = '''if page == "📋 " + t('pages.all_documents'):
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
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])'''

content = content.replace(old_all_docs_start, new_all_docs_start)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ All Documents page modernization complete!")
