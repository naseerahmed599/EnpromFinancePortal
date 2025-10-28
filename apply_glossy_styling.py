#!/usr/bin/env python3
"""Apply glossy, premium styling to All Documents and Document Details pages"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================================
# PAGE 1: ALL DOCUMENTS - Premium Glossy Design
# ============================================================================

# Replace page title with glossy gradient banner
old_title = '''# Modern page title with gradient
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem 2rem; border-radius: 12px;
                    margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <h1 style="color: white; margin: 0; font-size: 2rem; font-weight: 700;
                       text-shadow: 0 2px 4px rgba(0,0,0,0.1);">💼 {t('app_title')}</h1>
            <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0;
                      font-size: 1rem;">{t('tagline')}</p>
        </div>
    """, unsafe_allow_html=True)'''

new_title = '''# Premium glossy page title
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4),
                        0 2px 8px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50%;
                right: -10%;
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <h1 style="
                color: white;
                margin: 0;
                font-size: 2.25rem;
                font-weight: 700;
                text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                letter-spacing: -0.5px;
            ">💼 {t('app_title')}</h1>
            <p style="
                color: rgba(255, 255, 255, 0.95);
                margin: 0.75rem 0 0 0;
                font-size: 1.1rem;
                font-weight: 400;
                text-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
            ">{t('tagline')}</p>
        </div>
    """, unsafe_allow_html=True)'''

content = content.replace(old_title, new_title)

# Replace All Documents header with glossy card
old_all_docs_header = '''    # Page header with icon
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;
                    margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        width: 48px; height: 48px; border-radius: 12px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 24px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">📋</div>
            <div>
                <h2 style="margin: 0; font-size: 1.75rem; font-weight: 700;">
                    {t('all_documents_page.title')}</h2>
                <p style="margin: 0; color: #64748b; font-size: 0.95rem;">
                    Browse and manage all documents in the system</p>
            </div>
        </div>
    """, unsafe_allow_html=True)'''

new_all_docs_header = '''    # Glossy page header card
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

# Replace control panel with glossy design
old_control_panel = '''    # Modern control panel
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;
                    margin-bottom: 1.5rem;">
    """, unsafe_allow_html=True)'''

new_control_panel = '''    # Glossy control panel
    st.markdown("""
        <div style="
            background: rgba(248, 250, 252, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
        ">
    """, unsafe_allow_html=True)'''

content = content.replace(old_control_panel, new_control_panel)

# Update statistics cards with glossy design
old_stats = '''        st.markdown("#### 📊 Quick Statistics")
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
                """, unsafe_allow_html=True)'''

new_stats = '''        st.markdown("""
            <h4 style="
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 1.25rem;
                color: #1e293b;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">📊 Quick Statistics</h4>
        """, unsafe_allow_html=True)
        stat_cols = st.columns(4)
        
        stats = [
            ("Total", len(docs), "📄", "#3b82f6", "rgba(59, 130, 246, 0.1)"),
            ("Approved", stage_counts.get('Approved', 0), "✅", "#22c55e", "rgba(34, 197, 94, 0.1)"),
            ("Pending", sum(stage_counts.get(f'Stage{i}', 0) for i in range(1, 6)), "⏳", "#f59e0b", "rgba(245, 158, 11, 0.1)"),
            ("Draft", stage_counts.get('Draft', 0), "📝", "#8b5cf6", "rgba(139, 92, 246, 0.1)")
        ]
        
        for idx, (label, value, icon, color, bg) in enumerate(stats):
            with stat_cols[idx]:
                st.markdown(f"""
                    <div style="
                        background: {bg};
                        backdrop-filter: blur(10px);
                        -webkit-backdrop-filter: blur(10px);
                        padding: 1.5rem 1.25rem;
                        border-radius: 14px;
                        border: 1px solid {color}40;
                        box-shadow: 0 4px 16px {color}20,
                                    inset 0 1px 0 rgba(255, 255, 255, 0.5);
                        text-align: center;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    ">
                        <div style="
                            font-size: 2.25rem;
                            margin-bottom: 0.75rem;
                            filter: drop-shadow(0 2px 4px {color}40);
                        ">{icon}</div>
                        <div style="
                            font-size: 2.25rem;
                            font-weight: 800;
                            color: {color};
                            text-shadow: 0 2px 8px {color}30;
                            margin-bottom: 0.5rem;
                        ">{value}</div>
                        <div style="
                            font-size: 0.875rem;
                            color: #64748b;
                            font-weight: 600;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                        ">{label}</div>
                    </div>
                """, unsafe_allow_html=True)'''

content = content.replace(old_stats, new_stats)

# ============================================================================
# PAGE 2: DOCUMENT DETAILS - Premium Glossy Design
# ============================================================================

# Replace Document Details header
old_doc_details_header = '''    # Page header with icon card
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
    """, unsafe_allow_html=True)'''

new_doc_details_header = '''    # Glossy page header card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 1.75rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid rgba(139, 92, 246, 0.2);
            box-shadow: 0 4px 24px rgba(139, 92, 246, 0.12),
                        0 2px 6px rgba(0, 0, 0, 0.04);
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
                    background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">{t('single_document_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    color: #64748b;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">View detailed information about a specific document</p>
            </div>
        </div>
    """, unsafe_allow_html=True)'''

content = content.replace(old_doc_details_header, new_doc_details_header)

# Replace search panel
old_search_panel = '''    # Modern search panel
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;
                    margin-bottom: 1.5rem;">
    """, unsafe_allow_html=True)'''

new_search_panel = '''    # Glossy search panel
    st.markdown("""
        <div style="
            background: rgba(248, 250, 252, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06),
                        inset 0 1px 0 rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
        ">
    """, unsafe_allow_html=True)'''

content = content.replace(old_search_panel, new_search_panel)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Applied premium glossy styling to pages!")
print("Features enhanced:")
print("  ✨ Glassmorphism effects (backdrop-filter blur)")
print("  ✨ Multi-layered shadows for depth")
print("  ✨ Gradient text effects")
print("  ✨ Inset highlights for 3D feel")
print("  ✨ Enhanced icon cards with double shadows")
print("  ✨ Premium stat cards with colored glows")
print("  ✨ Radial gradient overlays")
print("  ✨ Refined borders with transparency")
