"""
Pagination utilities for large datasets
Provides efficient pagination for DataFrames and lists
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional


def paginate_dataframe(
    df: pd.DataFrame,
    page_size: int = 50,
    page_key: str = "page",
    show_info: bool = True
) -> Tuple[pd.DataFrame, int, int, int]:
    """
    Paginate a DataFrame with navigation controls
    
    Args:
        df: DataFrame to paginate
        page_size: Number of rows per page
        page_key: Unique key for page state
        show_info: Show pagination info
        
    Returns:
        Tuple of (paginated_df, current_page, total_pages, total_rows)
    """
    if df is None or len(df) == 0:
        return pd.DataFrame(), 0, 0, 0
    
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size  
    
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    current_page = st.session_state[page_key]
    
    if current_page < 1:
        current_page = 1
    elif current_page > total_pages:
        current_page = total_pages
    
    st.session_state[page_key] = current_page
    
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_df = df.iloc[start_idx:end_idx].copy()
    
    if total_pages > 1:
        _render_pagination_controls(
            current_page, total_pages, page_key, show_info, total_rows, page_size
        )
    
    return paginated_df, current_page, total_pages, total_rows


def _render_pagination_controls(
    current_page: int,
    total_pages: int,
    page_key: str,
    show_info: bool,
    total_rows: int,
    page_size: int
):
    """Render pagination navigation controls"""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", key=f"{page_key}_first", disabled=current_page == 1):
            st.session_state[page_key] = 1
            st.rerun()
    
    with col2:
        if st.button("◀️ Prev", key=f"{page_key}_prev", disabled=current_page == 1):
            st.session_state[page_key] = current_page - 1
            st.rerun()
    
    with col3:
        if show_info:
            start_row = (current_page - 1) * page_size + 1
            end_row = min(current_page * page_size, total_rows)
            st.markdown(
                f"<div style='text-align: center; padding: 0.5rem;'>"
                f"<strong>Page {current_page} of {total_pages}</strong><br>"
                f"<small>Showing {start_row:,} - {end_row:,} of {total_rows:,} rows</small>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            page_num = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=current_page,
                key=f"{page_key}_input",
                label_visibility="collapsed"
            )
            if page_num != current_page:
                st.session_state[page_key] = page_num
                st.rerun()
    
    with col4:
        if st.button("Next ▶️", key=f"{page_key}_next", disabled=current_page == total_pages):
            st.session_state[page_key] = current_page + 1
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", key=f"{page_key}_last", disabled=current_page == total_pages):
            st.session_state[page_key] = total_pages
            st.rerun()


def paginate_list(
    items: List[Any],
    page_size: int = 50,
    page_key: str = "page"
) -> Tuple[List[Any], int, int, int]:
    """
    Paginate a list with navigation controls
    
    Args:
        items: List to paginate
        page_size: Number of items per page
        page_key: Unique key for page state
        
    Returns:
        Tuple of (paginated_items, current_page, total_pages, total_items)
    """
    if not items:
        return [], 0, 0, 0
    
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    
    current_page = st.session_state[page_key]
    
    if current_page < 1:
        current_page = 1
    elif current_page > total_pages:
        current_page = total_pages
    
    st.session_state[page_key] = current_page
    
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_items = items[start_idx:end_idx]
    
    if total_pages > 1:
        _render_pagination_controls(
            current_page, total_pages, page_key, True, total_items, page_size
        )
    
    return paginated_items, current_page, total_pages, total_items


def get_page_size_selector(
    current_size: int = 50,
    key: str = "page_size",
    options: List[int] = [25, 50, 100, 200, 500]
) -> int:
    """
    Get page size selector widget
    
    Args:
        current_size: Current page size
        key: Unique key for widget
        options: Available page size options
        
    Returns:
        Selected page size
    """
    return st.selectbox(
        "Rows per page",
        options=options,
        index=options.index(current_size) if current_size in options else 1,
        key=key
    )

