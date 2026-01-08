"""
Caching utilities for analytics data
Performance optimization through intelligent caching with TTL strategies
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import hashlib
import json


def get_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from prefix and parameters"""
    params_str = json.dumps(kwargs, sort_keys=True, default=str)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    return f"{prefix}_{params_hash}"


@st.cache_data(ttl=3600, show_spinner=False)
def _cache_documents_internal(documents: List[Dict], cache_key: str) -> List[Dict]:
    """Internal cached function for documents"""
    return documents


def get_cached_documents(cache_key: Optional[str] = None) -> Optional[List[Dict]]:
    """
    Get cached documents from session state with TTL

    Args:
        cache_key: Optional cache key to check specific cache

    Returns:
        Cached documents or None if not found/expired
    """
    if cache_key:
        cache_entry = st.session_state.get(f"doc_cache_{cache_key}")
        if cache_entry:
            cache_time = cache_entry.get("timestamp")
            if cache_time and (datetime.now() - cache_time) < timedelta(hours=1):
                return cache_entry.get("data")
    return st.session_state.get("documents")


def cache_documents(documents: List[Dict], cache_key: Optional[str] = None):
    """
    Cache documents in session state with timestamp

    Args:
        documents: Documents to cache
        cache_key: Optional cache key for specific cache
    """
    st.session_state.documents = documents
    if cache_key:
        st.session_state[f"doc_cache_{cache_key}"] = {
            "data": documents,
            "timestamp": datetime.now(),
        }


@st.cache_data(ttl=1800, show_spinner=False)
def _cache_cost_centers_internal(
    cost_centers: List[str], months_back: int
) -> List[str]:
    """Internal cached function for cost centers"""
    return cost_centers


def get_cached_cost_centers(months_back: int) -> Optional[List[str]]:
    """
    Get cached cost centers with 30-minute TTL

    Args:
        months_back: Number of months to look back

    Returns:
        Cached cost centers or None
    """
    cache_key = f"cc_{months_back}"
    cached = st.session_state.get(f"cost_centers_cache_{cache_key}")
    if cached:
        cache_time = cached.get("timestamp")
        if cache_time and (datetime.now() - cache_time) < timedelta(minutes=30):
            return cached.get("data")
    return None


def cache_cost_centers(cost_centers: List[str], months_back: int):
    """
    Cache cost centers with 30-minute TTL

    Args:
        cost_centers: Cost centers to cache
        months_back: Number of months for cache key
    """
    cache_key = f"cc_{months_back}"
    st.session_state[f"cost_centers_cache_{cache_key}"] = {
        "data": cost_centers,
        "timestamp": datetime.now(),
    }


def fetch_cost_centers_cached(
    api_key: str, base_url: str, months_back: int, progress_callback=None
) -> List[str]:
    """
    Fetch cost centers using the API client.
    Note: Automatic disk caching is disabled here to allow progress reporting.
    We rely on session_state caching in the calling function.
    """
    try:
        from flowwer_api_client import FlowwerAPIClient

        temp_client = FlowwerAPIClient(base_url=base_url, api_key=api_key)
        result = temp_client.get_all_cost_centers(
            months_back=months_back, progress_callback=progress_callback
        )
        return result if result is not None else []
    except Exception as e:
        print(f"Error fetching cost centers: {e}")
        return []

    st.session_state.analytics_cost_centers = cost_centers


def get_cached_receipt_data(date_key: str) -> Optional[List[Dict]]:
    """
    Get cached receipt data for a date range with validation

    Args:
        date_key: Date range key (e.g., "2024-01-01_2024-12-31")

    Returns:
        Cached receipt data or None
    """
    cached = st.session_state.get("analytics_receipt_data")
    cached_key = st.session_state.get("analytics_receipt_date_key")
    cached_time = st.session_state.get("analytics_receipt_timestamp")

    if cached and cached_key == date_key and cached_time:
        if (datetime.now() - cached_time) < timedelta(hours=1):
            return cached

    return None


def cache_receipt_data(receipt_data: List[Dict], date_key: str):
    """
    Cache receipt data with timestamp and date key

    Args:
        receipt_data: Receipt data to cache
        date_key: Date range key
    """
    st.session_state.analytics_receipt_data = receipt_data
    st.session_state.analytics_receipt_date_key = date_key
    st.session_state.analytics_receipt_timestamp = datetime.now()


@st.cache_data(ttl=600, show_spinner=False)
def cache_filtered_documents(documents: List[Dict], filter_hash: str) -> List[Dict]:
    """
    Cache filtered documents with 10-minute TTL

    Args:
        documents: Filtered documents
        filter_hash: Hash of filter parameters

    Returns:
        Cached filtered documents
    """
    return documents


def get_cached_filtered_documents(
    filter_params: Dict[str, Any],
) -> Optional[List[Dict]]:
    """
    Get cached filtered documents based on filter parameters

    Args:
        filter_params: Dictionary of filter parameters

    Returns:
        Cached filtered documents or None
    """
    filter_hash = get_cache_key("filtered", **filter_params)
    cache_entry = st.session_state.get(f"filtered_docs_{filter_hash}")

    if cache_entry:
        cache_time = cache_entry.get("timestamp")
        if cache_time and (datetime.now() - cache_time) < timedelta(minutes=10):
            return cache_entry.get("data")

    return None


def cache_filtered_documents_manual(
    filtered_docs: List[Dict], filter_params: Dict[str, Any]
):
    """
    Manually cache filtered documents

    Args:
        filtered_docs: Filtered documents to cache
        filter_params: Filter parameters for cache key
    """
    filter_hash = get_cache_key("filtered", **filter_params)
    st.session_state[f"filtered_docs_{filter_hash}"] = {
        "data": filtered_docs,
        "timestamp": datetime.now(),
    }


@st.cache_data(ttl=300, show_spinner=False)
def cache_chart_data(chart_type: str, data_hash: str, chart_data: Any) -> Any:
    """
    Cache chart data with 5-minute TTL

    Args:
        chart_type: Type of chart (e.g., "timeline", "pie")
        data_hash: Hash of data used for chart
        chart_data: Chart configuration/data

    Returns:
        Cached chart data
    """
    return chart_data


def clear_cache(cache_type: Optional[str] = None):
    """
    Clear specific or all caches

    Args:
        cache_type: Type of cache to clear ('documents', 'cost_centers', 'receipts', 'filters', None for all)
    """
    if cache_type is None or cache_type == "documents":
        keys_to_remove = [
            k for k in st.session_state.keys() if k.startswith("doc_cache_")
        ]
        for key in keys_to_remove:
            del st.session_state[key]

    if cache_type is None or cache_type == "cost_centers":
        keys_to_remove = [
            k for k in st.session_state.keys() if k.startswith("cost_centers_cache_")
        ]
        for key in keys_to_remove:
            del st.session_state[key]

    if cache_type is None or cache_type == "receipts":
        if "analytics_receipt_data" in st.session_state:
            del st.session_state.analytics_receipt_data
        if "analytics_receipt_date_key" in st.session_state:
            del st.session_state.analytics_receipt_date_key
        if "analytics_receipt_timestamp" in st.session_state:
            del st.session_state.analytics_receipt_timestamp

    if cache_type is None or cache_type == "filters":
        keys_to_remove = [
            k for k in st.session_state.keys() if k.startswith("filtered_docs_")
        ]
        for key in keys_to_remove:
            del st.session_state[key]


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about current cache usage

    Returns:
        Dictionary with cache statistics
    """
    stats = {
        "document_caches": 0,
        "cost_center_caches": 0,
        "filter_caches": 0,
        "total_cache_entries": 0,
    }

    for key in st.session_state.keys():
        if key.startswith("doc_cache_"):
            stats["document_caches"] += 1
        elif key.startswith("cost_centers_cache_"):
            stats["cost_center_caches"] += 1
        elif key.startswith("filtered_docs_"):
            stats["filter_caches"] += 1

    stats["total_cache_entries"] = (
        stats["document_caches"] + stats["cost_center_caches"] + stats["filter_caches"]
    )

    return stats
