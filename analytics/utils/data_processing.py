"""
Data processing utilities for analytics
Optimized functions for document classification and calculations
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache


def classify_document(doc: Dict[str, Any]) -> str:
    """
    Classify a document as 'income' or 'cost'
    
    Args:
        doc: Document dictionary
        
    Returns:
        'income' or 'cost'
    """
    doc_type = str(
        doc.get("documentType")
        or doc.get("documenttype")
        or doc.get("documentKind")
        or doc.get("documentkind")
        or ""
    ).lower()
    
    amount = doc.get("totalGross", 0) or doc.get("totalNet", 0) or 0
    
    if any(keyword in doc_type for keyword in [
        "ausgangsrechnung", "outgoinginvoice", "ausgang",
        "invoice", "rechnung", "sales", "revenue"
    ]):
        return "income"
    
    if any(keyword in doc_type for keyword in [
        "eingangsrechnung", "incominginvoice", "eingang",
        "expense", "cost", "purchase"
    ]):
        return "cost"
    
    return "income" if amount < 0 else "cost"


@lru_cache(maxsize=128)
def _calculate_totals_cached(doc_ids_tuple: Tuple[int, ...], amounts_tuple: Tuple[float, ...]) -> Dict[str, float]:
    """Cached calculation of totals"""
    return {
        "total_gross": sum(abs(a) for a in amounts_tuple),
        "total_net": sum(abs(a * 0.8) for a in amounts_tuple),  
    }


def calculate_kpis(docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate KPIs from documents
    
    Args:
        docs: List of document dictionaries
        
    Returns:
        Dictionary with KPI values
    """
    if not docs:
        return {
            "total_gross": 0,
            "total_net": 0,
            "total_tax": 0,
            "avg_invoice_value": 0,
            "approved_count": 0,
            "in_workflow": 0,
            "draft_count": 0,
            "approval_rate": 0,
            "pending_payment_value": 0,
        }
    
    total_gross = sum(abs(doc.get("totalGross", 0)) for doc in docs)
    total_net = sum(abs(doc.get("totalNet", 0)) for doc in docs)
    total_tax = total_gross - total_net
    avg_invoice_value = total_gross / len(docs) if len(docs) > 0 else 0
    
    stage_counts = {}
    for doc in docs:
        stage = doc.get("currentStage", "Unknown")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    approved_count = stage_counts.get("Approved", 0)
    in_workflow = sum(stage_counts.get(f"Stage{i}", 0) for i in range(1, 6))
    draft_count = stage_counts.get("Draft", 0)
    approval_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0
    
    payment_totals = {}
    for doc in docs:
        payment = doc.get("paymentState", "Unknown")
        amount = abs(doc.get("totalGross", 0))
        payment_totals[payment] = payment_totals.get(payment, 0) + amount
    
    pending_payment_value = payment_totals.get("Open", 0) + payment_totals.get("Pending", 0)
    
    return {
        "total_gross": total_gross,
        "total_net": total_net,
        "total_tax": total_tax,
        "avg_invoice_value": avg_invoice_value,
        "approved_count": approved_count,
        "in_workflow": in_workflow,
        "draft_count": draft_count,
        "approval_rate": approval_rate,
        "pending_payment_value": pending_payment_value,
        "stage_counts": stage_counts,
        "payment_totals": payment_totals,
    }


def filter_documents(
    docs: List[Dict[str, Any]],
    company: Optional[str] = None,
    stage: Optional[str] = None,
    payment: Optional[str] = None,
    supplier: Optional[str] = None,
    currency: Optional[str] = None,
    flow: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_value: Optional[float] = None,
    cost_centers: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Filter documents based on various criteria
    
    Args:
        docs: List of documents to filter
        company: Company name filter
        stage: Stage filter
        payment: Payment state filter
        supplier: Supplier name filter
        currency: Currency filter
        flow: Flow filter
        date_from: Start date (ISO format)
        date_to: End date (ISO format)
        min_value: Minimum value filter
        cost_centers: List of cost centers to filter
        
    Returns:
        Filtered list of documents
    """
    filtered = docs
    
    if company and company != "All":
        filtered = [d for d in filtered if d.get("companyName") == company]
    
    if stage and stage != "All":
        filtered = [d for d in filtered if d.get("currentStage") == stage]
    
    if payment and payment != "All":
        filtered = [d for d in filtered if d.get("paymentState") == payment]
    
    if supplier and supplier != "All":
        filtered = [d for d in filtered if d.get("supplierName") == supplier]
    
    if currency and currency != "All":
        filtered = [d for d in filtered if d.get("currency") == currency]
    
    if flow and flow != "All":
        filtered = [d for d in filtered if d.get("flowName") == flow]
    
    if date_from:
        filtered = [d for d in filtered if d.get("invoiceDate", "") >= date_from]
    
    if date_to:
        filtered = [d for d in filtered if d.get("invoiceDate", "") <= date_to]
    
    if min_value is not None and min_value > 0:
        filtered = [d for d in filtered if abs(d.get("totalGross", 0)) >= min_value]
    
    if cost_centers and len(cost_centers) > 0:
        filtered = [d for d in filtered if _has_matching_cost_center(d, cost_centers)]
    
    return filtered


def _has_matching_cost_center(doc: Dict[str, Any], cost_centers: List[str]) -> bool:
    """Check if document has matching cost center"""
    splits = doc.get("receiptSplits") or doc.get("documentReceiptSplits") or []
    for split in splits:
        cc = str(split.get("costCenter", "")).strip()
        if cc in cost_centers:
            return True
    return False


def enrich_document_types(
    docs: List[Dict[str, Any]],
    client,
    cache_key: str = "analytics_doc_type_cache"
) -> List[Dict[str, Any]]:
    """
    Enrich documents with document type information
    
    Args:
        docs: List of documents
        client: API client instance
        cache_key: Session state key for type cache
        
    Returns:
        Documents with enriched type information
    """
    import streamlit as st
    
    if cache_key not in st.session_state:
        st.session_state[cache_key] = {}
    
    type_cache = st.session_state[cache_key]
    
    doc_ids = [int(d.get("documentId", 0)) for d in docs if d.get("documentId")]
    unique_ids = list(set(doc_ids))
    
    missing_ids = [doc_id for doc_id in unique_ids if doc_id not in type_cache]
    
    if missing_ids:
        for doc_id in missing_ids:
            try:
                detail = client.get_document(int(doc_id))
                if detail:
                    doc_type = (
                        detail.get("documentType")
                        or detail.get("documentKind")
                        or ""
                    )
                    type_cache[doc_id] = doc_type
                else:
                    type_cache[doc_id] = ""
            except Exception:
                type_cache[doc_id] = ""
    
    enriched = []
    for doc in docs:
        doc_id = doc.get("documentId")
        if doc_id and int(doc_id) in type_cache:
            doc = doc.copy()
            doc["documentType"] = type_cache[int(doc_id)]
        enriched.append(doc)
    
    return enriched


def get_cost_center_stats(
    docs: List[Dict[str, Any]],
    amount_col: str = "totalGross"
) -> Dict[str, Dict[str, float]]:
    """
    Calculate statistics by cost center
    
    Args:
        docs: List of documents with receipt splits
        amount_col: Column name for amount
        
    Returns:
        Dictionary mapping cost center to stats (income, cost, margin)
    """
    cc_stats = {}
    
    for doc in docs:
        category = classify_document(doc)
        amount = abs(doc.get(amount_col, 0))
        
        splits = doc.get("receiptSplits") or doc.get("documentReceiptSplits") or []
        
        if not splits:
            cc = "UNASSIGNED"
            if cc not in cc_stats:
                cc_stats[cc] = {"income": 0, "cost": 0, "margin": 0}
            
            if category == "income":
                cc_stats[cc]["income"] += amount
            else:
                cc_stats[cc]["cost"] += amount
        else:
            for split in splits:
                cc = str(split.get("costCenter", "UNASSIGNED")).strip()
                if not cc or cc == "None":
                    cc = "UNASSIGNED"
                
                if cc not in cc_stats:
                    cc_stats[cc] = {"income": 0, "cost": 0, "margin": 0}
                
                split_amount = abs(split.get("netAmount", 0) or split.get("grossAmount", 0) or 0)
                
                if category == "income":
                    cc_stats[cc]["income"] += split_amount
                else:
                    cc_stats[cc]["cost"] += split_amount
    
    for cc in cc_stats:
        cc_stats[cc]["margin"] = cc_stats[cc]["income"] - cc_stats[cc]["cost"]
    
    return cc_stats

