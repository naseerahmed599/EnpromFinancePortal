#!/usr/bin/env python3
"""Fix empty bar issue and enhance button styles"""

with open("streamlit_flowwer_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================================
# FIX: Remove empty bars and enhance button styles
# ============================================================================

# Fix Page 1: All Documents - Remove the old control panel wrapper and add modern button styles
old_control_panel_start = '''    # Glossy control panel
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
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])'''

new_control_panel_start = """    # Control panel with modern styling
    col1, col2, col3 = st.columns([1, 1, 2])"""

content = content.replace(old_control_panel_start, new_control_panel_start)

# Remove closing div for control panel
old_control_close = """                else:
                    st.warning("⚠️ No documents found")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.documents:"""

new_control_close = """                else:
                    st.warning("⚠️ No documents found")
    
    if st.session_state.documents:"""

content = content.replace(old_control_close, new_control_close)

# Fix Page 2: Document Details - Remove search panel wrapper
old_search_panel_start = '''    # Glossy search panel
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
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])'''

new_search_panel_start = """    # Search panel
    col1, col2 = st.columns([2, 1])"""

content = content.replace(old_search_panel_start, new_search_panel_start)

# Remove closing div for search panel
old_search_close = """                else:
                    st.error(f"❌ Document #{doc_id} not found")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.selected_document:"""

new_search_close = """                else:
                    st.error(f"❌ Document #{doc_id} not found")
    
    if st.session_state.selected_document:"""

content = content.replace(old_search_close, new_search_close)

# Now add modern button styling to the CSS
old_css_end = '''        /* Custom scrollbar */
        [data-testid="stSidebar"]::-webkit-scrollbar {
            width: 6px;
        }
        
        [data-testid="stSidebar"]::-webkit-scrollbar-track {
            background: transparent;
        }
        
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }
        
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)'''

new_css_end = '''        /* Custom scrollbar */
        [data-testid="stSidebar"]::-webkit-scrollbar {
            width: 6px;
        }
        
        [data-testid="stSidebar"]::-webkit-scrollbar-track {
            background: transparent;
        }
        
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }
        
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Modern button styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            transform: translateY(-2px) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0px) !important;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
        }
        
        /* Download button styling */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            transform: translateY(-2px) !important;
        }
        
        .stDownloadButton > button:active {
            transform: translateY(0px) !important;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3) !important;
        }
        
        /* Checkbox styling */
        .stCheckbox {
            padding: 0.5rem 0 !important;
        }
        
        /* Number input styling */
        .stNumberInput > div > div > input {
            border-radius: 10px !important;
            border: 2px solid #e2e8f0 !important;
            padding: 0.75rem !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stNumberInput > div > div > input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)'''

content = content.replace(old_css_end, new_css_end)

with open("streamlit_flowwer_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Fixed empty bars and enhanced button styles!")
print("Changes applied:")
print("  ✓ Removed empty wrapper divs causing bars")
print("  ✓ Enhanced button styling (blue gradient with glow)")
print("  ✓ Improved download button styling (green gradient)")
print("  ✓ Added hover effects (lift + enhanced shadow)")
print("  ✓ Added active/press effects")
print("  ✓ Styled number inputs with focus effects")
print("  ✓ Refined checkbox spacing")
