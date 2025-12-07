"""
Theme-adaptive Glassmorphic Styles for Flowwer Streamlit App
This module contains all CSS styling for the application with automatic
light/dark mode support based on system preferences.
"""


def get_page_header_styles():
    """Returns CSS for theme-adaptive page headers"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-card {
                background: linear-gradient(135deg, 
                    rgba(59, 130, 246, 0.15) 0%, 
                    rgba(37, 99, 235, 0.1) 50%,
                    rgba(59, 130, 246, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(59, 130, 246, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(59, 130, 246, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(59, 130, 246, 0.3) !important;
            }
            .page-header-card h2 {
                color: #1e40af !important;
            }
            .page-header-card p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-card {
                background: linear-gradient(135deg, 
                    rgba(59, 130, 246, 0.25) 0%, 
                    rgba(37, 99, 235, 0.15) 50%,
                    rgba(59, 130, 246, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(59, 130, 246, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(59, 130, 246, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(59, 130, 246, 0.4) !important;
            }
            .page-header-card h2 {
                color: #93c5fd !important;
            }
            .page-header-card p {
                color: #c4b5fd !important;
            }
        }
        </style>
    """


def get_info_box_styles():
    """Returns CSS for theme-adaptive info/success/warning boxes"""
    return """
        <style>
        /* Success/Info Boxes - Theme Adaptive */
        @media (prefers-color-scheme: light) {
            .info-box-green {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.7) 50%,
                    rgba(16, 185, 129, 0.06) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(16, 185, 129, 0.3) !important;
                box-shadow: 
                    0 4px 16px rgba(16, 185, 129, 0.1),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
                border-radius: 16px !important;
                padding: 16px !important;
                margin-bottom: 20px !important;
            }
            .info-box-green span {
                color: #065f46 !important;
            }
            
            .info-box-yellow {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.7) 50%,
                    rgba(245, 158, 11, 0.06) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(245, 158, 11, 0.3) !important;
                border-left: 4px solid #f59e0b !important;
                box-shadow: 
                    0 4px 16px rgba(245, 158, 11, 0.1),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
                border-radius: 12px !important;
                padding: 16px !important;
                margin-bottom: 16px !important;
            }
            .info-box-yellow h3 {
                color: #78350f !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .info-box-green {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.7) 50%,
                    rgba(16, 185, 129, 0.15) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(16, 185, 129, 0.4) !important;
                box-shadow: 
                    0 4px 16px rgba(16, 185, 129, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
                border-radius: 16px !important;
                padding: 16px !important;
                margin-bottom: 20px !important;
            }
            .info-box-green span {
                color: #6ee7b7 !important;
            }
            
            .info-box-yellow {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.7) 50%,
                    rgba(245, 158, 11, 0.15) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(245, 158, 11, 0.4) !important;
                border-left: 4px solid #f59e0b !important;
                box-shadow: 
                    0 4px 16px rgba(245, 158, 11, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
                border-radius: 12px !important;
                padding: 16px !important;
                margin-bottom: 16px !important;
            }
            .info-box-yellow h3 {
                color: #fbbf24 !important;
            }
        }
        </style>
    """


def get_metric_styles():
    """Returns CSS for theme-adaptive Streamlit metric components"""
    return """
        <style>
        /* Streamlit Metrics - Theme Adaptive Glassmorphism */
        @media (prefers-color-scheme: light) {
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.6) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(59, 130, 246, 0.15) !important;
                border-radius: 16px !important;
                padding: 1.25rem !important;
                box-shadow: 
                    0 4px 16px rgba(59, 130, 246, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
                transition: all 0.3s ease !important;
            }
            
            [data-testid="stMetric"]:hover {
                border: 1px solid rgba(59, 130, 246, 0.3) !important;
                box-shadow: 
                    0 8px 24px rgba(59, 130, 246, 0.12),
                    0 4px 12px rgba(0, 0, 0, 0.06),
                    inset 0 1px 0 rgba(255, 255, 255, 0.95) !important;
                transform: translateY(-2px) !important;
            }
            
            [data-testid="stMetricLabel"] {
                color: #64748b !important;
                font-weight: 600 !important;
                font-size: 0.875rem !important;
            }
            
            [data-testid="stMetricValue"] {
                color: #1e293b !important;
                font-weight: 700 !important;
                font-size: 1.5rem !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.6) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(59, 130, 246, 0.2) !important;
                border-radius: 16px !important;
                padding: 1.25rem !important;
                box-shadow: 
                    0 4px 16px rgba(59, 130, 246, 0.12),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
                transition: all 0.3s ease !important;
            }
            
            [data-testid="stMetric"]:hover {
                border: 1px solid rgba(59, 130, 246, 0.4) !important;
                box-shadow: 
                    0 8px 24px rgba(59, 130, 246, 0.18),
                    0 4px 12px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
                transform: translateY(-2px) !important;
            }
            
            [data-testid="stMetricLabel"] {
                color: #94a3b8 !important;
                font-weight: 600 !important;
                font-size: 0.875rem !important;
            }
            
            [data-testid="stMetricValue"] {
                color: #f1f5f9 !important;
                font-weight: 700 !important;
                font-size: 1.5rem !important;
            }
        }
        </style>
    """


def get_action_bar_styles():
    """Returns CSS for theme-adaptive action bars (button containers)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]) {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.95) 0%, 
                    rgba(255, 255, 255, 0.85) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                padding: 1.25rem 1.5rem !important;
                border-radius: 16px !important;
                margin-bottom: 2rem !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                box-shadow: 
                    0 4px 24px rgba(0, 0, 0, 0.06),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]) {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.95) 0%, 
                    rgba(20, 20, 20, 0.85) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                padding: 1.25rem 1.5rem !important;
                border-radius: 16px !important;
                margin-bottom: 2rem !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 
                    0 4px 24px rgba(0, 0, 0, 0.3),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
        }
        </style>
    """


def get_export_bar_styles():
    """Returns CSS for theme-adaptive export button containers"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.95) 0%, 
                    rgba(255, 255, 255, 0.85) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                padding: 1.25rem 1.5rem !important;
                border-radius: 16px !important;
                margin-bottom: 2rem !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                box-shadow: 
                    0 4px 24px rgba(0, 0, 0, 0.06),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.95) 0%, 
                    rgba(20, 20, 20, 0.85) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                padding: 1.25rem 1.5rem !important;
                border-radius: 16px !important;
                margin-bottom: 2rem !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 
                    0 4px 24px rgba(0, 0, 0, 0.3),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
        }
        </style>
    """


def get_card_styles():
    """Returns CSS for theme-adaptive metric and content cards"""
    return """
        <style>
        /* Section Headers - Theme Adaptive */
        @media (prefers-color-scheme: light) {
            .section-header {
                color: #1e293b !important;
                border-bottom: 2px solid #e2e8f0 !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .section-header {
                color: #f1f5f9 !important;
                border-bottom: 2px solid #475569 !important;
            }
        }
        
        /* Metric Cards - Theme Adaptive */
        @media (prefers-color-scheme: light) {
            .metric-card-light {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.7) 50%,
                    var(--card-color, rgba(59, 130, 246, 0.04)) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            }
            .metric-card-light .metric-label {
                color: #475569 !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .metric-card-light {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.7) 50%,
                    var(--card-color-dark, rgba(59, 130, 246, 0.15)) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.4),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
            .metric-card-light .metric-label {
                color: #94a3b8 !important;
            }
        }
        
        /* Financial & Payment Cards - Theme Adaptive */
        @media (prefers-color-scheme: light) {
            .financial-card {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.7) 50%,
                    var(--card-bg, rgba(59, 130, 246, 0.04)) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            }
            .financial-card .card-label {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .financial-card {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.7) 50%,
                    var(--card-bg-dark, rgba(59, 130, 246, 0.15)) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.4),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
            .financial-card .card-label {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_alert_box_styles():
    """Returns CSS for theme-adaptive alert/notification boxes"""
    return """
        <style>
        /* Alert Boxes - Theme Adaptive */
        @media (prefers-color-scheme: light) {
            .alert-box-orange {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.7) 50%,
                    rgba(245, 158, 11, 0.06) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                border-left: 4px solid #f59e0b !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            }
            .alert-box-orange h4 { color: #92400e !important; }
            .alert-box-orange p { color: #78350f !important; }
            .alert-box-orange .subtitle { color: #92400e !important; }
            
            .alert-box-purple {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.9) 0%, 
                    rgba(255, 255, 255, 0.7) 50%,
                    rgba(139, 92, 246, 0.06) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
                border-left: 4px solid #8b5cf6 !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
            }
            .alert-box-purple h4 { color: #581c87 !important; }
            .alert-box-purple p { color: #6b21a8 !important; }
            .alert-box-purple .subtitle { color: #581c87 !important; }
        }
        
        @media (prefers-color-scheme: dark) {
            .alert-box-orange {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.7) 50%,
                    rgba(245, 158, 11, 0.15) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-left: 4px solid #f59e0b !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.4),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
            .alert-box-orange h4 { color: #fbbf24 !important; }
            .alert-box-orange p { color: #fcd34d !important; }
            .alert-box-orange .subtitle { color: #fbbf24 !important; }
            
            .alert-box-purple {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.9) 0%, 
                    rgba(20, 20, 20, 0.7) 50%,
                    rgba(139, 92, 246, 0.15) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-left: 4px solid #8b5cf6 !important;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.4),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
            .alert-box-purple h4 { color: #c4b5fd !important; }
            .alert-box-purple p { color: #ddd6fe !important; }
            .alert-box-purple .subtitle { color: #c4b5fd !important; }
        }
        </style>
    """


def get_all_document_page_styles():
    """
    Returns all combined CSS styles for the All Documents page
    This is a convenience function that combines all styles needed for that page
    """
    return (
        get_page_header_styles()
        + get_action_bar_styles()
        + get_card_styles()
        + get_alert_box_styles()
        + get_export_bar_styles()
    )


def get_page_header_purple():
    """Returns CSS for purple-themed page headers (Single Document page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-purple {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.15) 0%, 
                    rgba(124, 58, 237, 0.1) 50%,
                    rgba(139, 92, 246, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(139, 92, 246, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(139, 92, 246, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(139, 92, 246, 0.3) !important;
            }
            .page-header-purple h2 {
                color: #6d28d9 !important;
            }
            .page-header-purple p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-purple {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.25) 0%, 
                    rgba(124, 58, 237, 0.15) 50%,
                    rgba(139, 92, 246, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(139, 92, 246, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(139, 92, 246, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(139, 92, 246, 0.4) !important;
            }
            .page-header-purple h2 {
                color: #c4b5fd !important;
            }
            .page-header-purple p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_tab_styles():
    """Returns CSS for theme-adaptive Streamlit tabs with glassmorphic design"""
    return """
        <style>
        /* Streamlit Tabs - Theme Adaptive Glassmorphism */
        @media (prefers-color-scheme: light) {
            /* Tab list container */
            [data-baseweb="tab-list"] {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.85) 0%, 
                    rgba(255, 255, 255, 0.6) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(139, 92, 246, 0.15) !important;
                border-radius: 16px !important;
                padding: 8px !important;
                margin-bottom: 1.5rem !important;
                margin-top: 1.5rem !important;

                box-shadow: 
                    0 4px 16px rgba(139, 92, 246, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
                gap: 6px !important;
            }
            
            /* Individual tab buttons */
            [data-baseweb="tab"] {
                background: transparent !important;
                border: 1px solid transparent !important;
                border-radius: 12px !important;
                padding: 12px 20px !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                color: #64748b !important;
                transition: all 0.3s ease !important;
            }
            
            /* Tab hover state */
            [data-baseweb="tab"]:hover {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.1) 0%, 
                    rgba(124, 58, 237, 0.05) 100%) !important;
                border: 1px solid rgba(139, 92, 246, 0.2) !important;
                color: #6d28d9 !important;
            }
            
            /* Active/selected tab */
            [aria-selected="true"][data-baseweb="tab"] {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.15) 0%, 
                    rgba(124, 58, 237, 0.1) 100%) !important;
                border: 1px solid rgba(139, 92, 246, 0.3) !important;
                color: #6d28d9 !important;
                box-shadow: 
                    0 4px 12px rgba(139, 92, 246, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
            }
            
            /* Tab content panel */
            [data-testid="stTabContent"] {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.7) 0%, 
                    rgba(255, 255, 255, 0.5) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(139, 92, 246, 0.12) !important;
                border-radius: 16px !important;
                padding: 1.5rem !important;
                margin-top: 0 !important;
                box-shadow: 
                    0 4px 16px rgba(139, 92, 246, 0.06),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            /* Tab list container */
            [data-baseweb="tab-list"] {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.85) 0%, 
                    rgba(20, 20, 20, 0.6) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(139, 92, 246, 0.25) !important;
                border-radius: 16px !important;
                padding: 8px !important;
                margin-bottom: 1.5rem !important;
                box-shadow: 
                    0 4px 16px rgba(139, 92, 246, 0.12),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
                gap: 6px !important;
            }
            
            /* Individual tab buttons */
            [data-baseweb="tab"] {
                background: transparent !important;
                border: 1px solid transparent !important;
                border-radius: 12px !important;
                padding: 12px 20px !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                color: #94a3b8 !important;
                transition: all 0.3s ease !important;
            }
            
            /* Tab hover state */
            [data-baseweb="tab"]:hover {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.2) 0%, 
                    rgba(124, 58, 237, 0.1) 100%) !important;
                border: 1px solid rgba(139, 92, 246, 0.3) !important;
                color: #c4b5fd !important;
            }
            
            /* Active/selected tab */
            [aria-selected="true"][data-baseweb="tab"] {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.25) 0%, 
                    rgba(124, 58, 237, 0.15) 100%) !important;
                border: 1px solid rgba(139, 92, 246, 0.4) !important;
                color: #c4b5fd !important;
                box-shadow: 
                    0 4px 12px rgba(139, 92, 246, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
            }
            
            /* Tab content panel */
            [data-testid="stTabContent"] {
                background: linear-gradient(135deg, 
                    rgba(30, 30, 30, 0.7) 0%, 
                    rgba(20, 20, 20, 0.5) 100%) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(139, 92, 246, 0.2) !important;
                border-radius: 16px !important;
                padding: 1.5rem !important;
                margin-top: 0 !important;
                box-shadow: 
                    0 4px 16px rgba(139, 92, 246, 0.1),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
            }
        }
        </style>
    """


def get_page_header_cyan():
    """Returns CSS for cyan-themed page headers (Download page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-cyan {
                background: linear-gradient(135deg, 
                    rgba(14, 165, 233, 0.15) 0%, 
                    rgba(2, 132, 199, 0.1) 50%,
                    rgba(14, 165, 233, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(14, 165, 233, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(14, 165, 233, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(14, 165, 233, 0.3) !important;
            }
            .page-header-cyan h2 {
                color: #0284c7 !important;
            }
            .page-header-cyan p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-cyan {
                background: linear-gradient(135deg, 
                    rgba(14, 165, 233, 0.25) 0%, 
                    rgba(2, 132, 199, 0.15) 50%,
                    rgba(14, 165, 233, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(14, 165, 233, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(14, 165, 233, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(14, 165, 233, 0.4) !important;
            }
            .page-header-cyan h2 {
                color: #7dd3fc !important;
            }
            .page-header-cyan p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_page_header_rose():
    """Returns CSS for rose-themed page headers (Upload page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-rose {
                background: linear-gradient(135deg, 
                    rgba(244, 63, 94, 0.15) 0%, 
                    rgba(225, 29, 72, 0.1) 50%,
                    rgba(244, 63, 94, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(244, 63, 94, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(244, 63, 94, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(244, 63, 94, 0.3) !important;
            }
            .page-header-rose h2 {
                color: #e11d48 !important;
            }
            .page-header-rose p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-rose {
                background: linear-gradient(135deg, 
                    rgba(244, 63, 94, 0.25) 0%, 
                    rgba(225, 29, 72, 0.15) 50%,
                    rgba(244, 63, 94, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(244, 63, 94, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(244, 63, 94, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(244, 63, 94, 0.4) !important;
            }
            .page-header-rose h2 {
                color: #fda4af !important;
            }
            .page-header-rose p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_page_header_teal():
    """Returns CSS for teal-themed page headers (Data Explorer page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-teal {
                background: linear-gradient(135deg, 
                    rgba(20, 184, 166, 0.15) 0%, 
                    rgba(13, 148, 136, 0.1) 50%,
                    rgba(20, 184, 166, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(20, 184, 166, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(20, 184, 166, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(20, 184, 166, 0.3) !important;
            }
            .page-header-teal h2 {
                color: #0d9488 !important;
            }
            .page-header-teal p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-teal {
                background: linear-gradient(135deg, 
                    rgba(20, 184, 166, 0.25) 0%, 
                    rgba(13, 148, 136, 0.15) 50%,
                    rgba(20, 184, 166, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(20, 184, 166, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(20, 184, 166, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(20, 184, 166, 0.4) !important;
            }
            .page-header-teal h2 {
                color: #5eead4 !important;
            }
            .page-header-teal p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_page_header_indigo():
    """Returns CSS for indigo-themed page headers (Receipt Report page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-indigo {
                background: linear-gradient(135deg, 
                    rgba(99, 102, 241, 0.15) 0%, 
                    rgba(79, 70, 229, 0.1) 50%,
                    rgba(99, 102, 241, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(99, 102, 241, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(99, 102, 241, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(99, 102, 241, 0.3) !important;
            }
            .page-header-indigo h2 {
                color: #4f46e5 !important;
            }
            .page-header-indigo p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-indigo {
                background: linear-gradient(135deg, 
                    rgba(99, 102, 241, 0.25) 0%, 
                    rgba(79, 70, 229, 0.15) 50%,
                    rgba(99, 102, 241, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(99, 102, 241, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(99, 102, 241, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(99, 102, 241, 0.4) !important;
            }
            .page-header-indigo h2 {
                color: #a5b4fc !important;
            }
            .page-header-indigo p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_page_header_green():
    """Returns CSS for green-themed page headers (Approved/Signable Docs pages)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-green {
                background: linear-gradient(135deg, 
                    rgba(34, 197, 94, 0.15) 0%, 
                    rgba(22, 163, 74, 0.1) 50%,
                    rgba(34, 197, 94, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(34, 197, 94, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(34, 197, 94, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(34, 197, 94, 0.3) !important;
            }
            .page-header-green h2 {
                color: #16a34a !important;
            }
            .page-header-green p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-green {
                background: linear-gradient(135deg, 
                    rgba(34, 197, 94, 0.25) 0%, 
                    rgba(22, 163, 74, 0.15) 50%,
                    rgba(34, 197, 94, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(34, 197, 94, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(34, 197, 94, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(34, 197, 94, 0.4) !important;
            }
            .page-header-green h2 {
                color: #86efac !important;
            }
            .page-header-green p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_page_header_amber():
    """Returns CSS for amber-themed page headers (Analytics page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-amber {
                background: linear-gradient(135deg, 
                    rgba(251, 146, 60, 0.15) 0%, 
                    rgba(249, 115, 22, 0.1) 50%,
                    rgba(251, 146, 60, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(251, 146, 60, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(251, 146, 60, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(251, 146, 60, 0.3) !important;
            }
            .page-header-amber h2 {
                color: #ea580c !important;
            }
            .page-header-amber p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-amber {
                background: linear-gradient(135deg, 
                    rgba(251, 146, 60, 0.25) 0%, 
                    rgba(249, 115, 22, 0.15) 50%,
                    rgba(251, 146, 60, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(251, 146, 60, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(251, 146, 60, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(251, 146, 60, 0.4) !important;
            }
            .page-header-amber h2 {
                color: #fdba74 !important;
            }
            .page-header-amber p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_page_header_slate():
    """Returns CSS for slate-themed page headers (Settings page)"""
    return """
        <style>
        @media (prefers-color-scheme: light) {
            .page-header-slate {
                background: linear-gradient(135deg, 
                    rgba(71, 85, 105, 0.15) 0%, 
                    rgba(51, 65, 85, 0.1) 50%,
                    rgba(71, 85, 105, 0.08) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(71, 85, 105, 0.3) !important;
                box-shadow: 
                    0 8px 32px rgba(71, 85, 105, 0.15),
                    0 2px 8px rgba(0, 0, 0, 0.04),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(71, 85, 105, 0.3) !important;
            }
            .page-header-slate h2 {
                color: #334155 !important;
            }
            .page-header-slate p {
                color: #64748b !important;
            }
        }
        
        @media (prefers-color-scheme: dark) {
            .page-header-slate {
                background: linear-gradient(135deg, 
                    rgba(71, 85, 105, 0.25) 0%, 
                    rgba(51, 65, 85, 0.15) 50%,
                    rgba(71, 85, 105, 0.12) 100%) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(71, 85, 105, 0.4) !important;
                box-shadow: 
                    0 8px 32px rgba(71, 85, 105, 0.2),
                    0 2px 8px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(71, 85, 105, 0.4) !important;
            }
            .page-header-slate h2 {
                color: #cbd5e1 !important;
            }
            .page-header-slate p {
                color: #94a3b8 !important;
            }
        }
        </style>
    """


def get_theme_text_styles():
    """Returns CSS for theme-adaptive text colors used across all pages"""
    return """
        <style>
        /* Theme-adaptive text colors */
        @media (prefers-color-scheme: light) {
            .text-primary { color: #1e293b !important; }
            .text-secondary { color: #64748b !important; }
            .text-muted { color: #94a3b8 !important; }
        }
        @media (prefers-color-scheme: dark) {
            .text-primary { color: #f1f5f9 !important; }
            .text-secondary { color: #cbd5e1 !important; }
            .text-muted { color: #94a3b8 !important; }
        }
        </style>
    """


def get_section_header_styles():
    """Returns CSS for glassmorphic section headers"""
    return """
        <style>
        .section-header {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.95) 0%, 
                rgba(255, 255, 255, 0.8) 50%,
                rgba(59, 130, 246, 0.06) 100%);
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 
                0 4px 16px rgba(0, 0, 0, 0.06),
                0 2px 4px rgba(0, 0, 0, 0.04),
                inset 0 1px 0 rgba(255, 255, 255, 0.9);
        }
        
        @media (prefers-color-scheme: dark) {
            .section-header {
                background: linear-gradient(135deg, 
                    rgba(30, 41, 59, 0.95) 0%, 
                    rgba(30, 41, 59, 0.8) 50%,
                    rgba(59, 130, 246, 0.12) 100%);
                border: 1px solid rgba(100, 116, 139, 0.3);
                box-shadow: 
                    0 4px 16px rgba(0, 0, 0, 0.3),
                    0 2px 4px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }
        }
        </style>
    """


def get_kpi_card_styles():
    """Returns CSS for enhanced KPI cards with trend indicators"""
    return """
        <style>
        .kpi-card-enhanced {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .kpi-card-enhanced:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }
        
        .kpi-card-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--card-accent, #3b82f6), var(--card-accent-end, #2563eb));
        }
        
        @media (prefers-color-scheme: dark) {
            .kpi-card-enhanced {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
                border-color: rgba(71, 85, 105, 0.5);
            }
        }
        
        .kpi-value-main {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--value-color, #1e293b);
            margin: 0.5rem 0;
            line-height: 1.1;
            font-family: 'SF Mono', Monaco, monospace;
        }
        
        @media (prefers-color-scheme: dark) {
            .kpi-value-main {
                color: #f1f5f9;
            }
        }
        
        .kpi-label-main {
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin: 0;
        }
        
        @media (prefers-color-scheme: dark) {
            .kpi-label-main {
                color: #94a3b8;
            }
        }
        
        .kpi-trend {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        .kpi-trend.positive {
            background: rgba(34, 197, 94, 0.1);
            color: #16a34a;
        }
        
        .kpi-trend.negative {
            background: rgba(239, 68, 68, 0.1);
            color: #dc2626;
        }
        
        .kpi-trend.neutral {
            background: rgba(100, 116, 139, 0.1);
            color: #64748b;
        }
        
        @media (prefers-color-scheme: dark) {
            .kpi-trend.positive {
                background: rgba(34, 197, 94, 0.2);
                color: #4ade80;
            }
            
            .kpi-trend.negative {
                background: rgba(239, 68, 68, 0.2);
                color: #f87171;
            }
            
            .kpi-trend.neutral {
                background: rgba(100, 116, 139, 0.2);
                color: #94a3b8;
            }
        }
        
        .quick-filter-btn {
            background: transparent;
            border: 1.5px solid #cbd5e1;
            border-radius: 6px;
            padding: 0.4rem 0.875rem;
            font-size: 0.8rem;
            font-weight: 500;
            color: #64748b;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .quick-filter-btn:hover {
            background: rgba(59, 130, 246, 0.05);
            color: #3b82f6;
            border-color: #3b82f6;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
            transform: translateY(-1px);
        }
        
        .quick-filter-btn.active {
            background: rgba(59, 130, 246, 0.08);
            color: #3b82f6;
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
        }
        
        @media (prefers-color-scheme: dark) {
            .quick-filter-btn {
                background: transparent;
                border-color: rgba(100, 116, 139, 0.4);
                color: #94a3b8;
            }
            
            .quick-filter-btn:hover {
                background: rgba(59, 130, 246, 0.1);
                color: #60a5fa;
                border-color: #60a5fa;
            }
            
            .quick-filter-btn.active {
                background: rgba(59, 130, 246, 0.15);
                color: #60a5fa;
                border-color: #60a5fa;
            }
        }
        
        .tab-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 1.5rem;
            height: 1.5rem;
            padding: 0 0.5rem;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-left: 0.5rem;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
        }
        
        @media (prefers-color-scheme: dark) {
            .tab-badge {
                background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
            }
        }
        
        .total-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 700;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
            font-family: 'SF Mono', Monaco, monospace;
        }
        
        @media (prefers-color-scheme: dark) {
            .total-badge {
                background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
            }
        }
        </style>
    """
