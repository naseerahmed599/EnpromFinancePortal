"""
Analytics Utilities
Shared utility functions with performance optimizations
"""

from .data_processing import (
    classify_document,
    calculate_kpis,
    filter_documents,
    enrich_document_types,
    get_cost_center_stats,
)
from .caching import (
    get_cached_documents,
    cache_documents,
    get_cached_cost_centers,
    cache_cost_centers,
    get_cached_receipt_data,
    cache_receipt_data,
)

__all__ = [
    'classify_document',
    'calculate_kpis',
    'filter_documents',
    'enrich_document_types',
    'get_cost_center_stats',
    'get_cached_documents',
    'cache_documents',
    'get_cached_cost_centers',
    'cache_cost_centers',
    'get_cached_receipt_data',
    'cache_receipt_data',
]

