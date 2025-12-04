"""
Analytics Dashboard Page Module
Comprehensive analytics with KPIs, charts, and data insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json


def render_analytics_page(
    client,
    t,
    get_page_header_amber,
    get_action_bar_styles,
    get_card_styles,
    get_tab_styles,
    get_metric_styles,
    get_theme_text_styles,
    get_section_header_styles,
    to_excel,
):
    """Render the Analytics Dashboard page with comprehensive data visualization"""

    st.markdown(get_page_header_amber(), unsafe_allow_html=True)
    st.markdown(get_action_bar_styles(), unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="page-header-amber" style="
            padding: 1.75rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
        ">
            <div style="
                background: linear-gradient(135deg, rgba(251, 146, 60, 0.9) 0%, rgba(249, 115, 22, 0.9) 100%);
                width: 56px;
                height: 56px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                box-shadow: 0 8px 20px rgba(251, 146, 60, 0.35),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            ">📈</div>
            <div>
                <h2 style="
                    margin: 0;
                    font-size: 1.875rem;
                    font-weight: 700;
                ">{t('analytics_page.title')}</h2>
                <p style="
                    margin: 0.5rem 0 0 0;
                    font-size: 0.95rem;
                    font-weight: 500;
                ">Interactive data visualization and insights</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        get_card_styles()
        + get_tab_styles()
        + get_metric_styles()
        + get_theme_text_styles()
        + get_section_header_styles(),
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        include_processed_analytics = st.checkbox(
            t("analytics_page.include_processed"), value=True, key="analytics_processed"
        )

    with col2:
        include_deleted_analytics = st.checkbox(
            t("analytics_page.include_deleted"), value=False, key="analytics_deleted"
        )

    with col3:
        if st.button(
            t("analytics_page.load_data"),
            type="primary",
            use_container_width=True,
            key="btn_load_analytics_docs",
        ):
            with st.spinner("Loading documents..."):
                docs = st.session_state.client.get_all_documents(
                    include_processed=include_processed_analytics,
                    include_deleted=include_deleted_analytics,
                )
                st.session_state.documents = docs
                st.session_state.analytics_load_time = datetime.now()
                st.rerun()

    if st.session_state.documents is None:
        st.info("📊 Click 'Load Data' to view analytics and insights")
    else:
        docs = st.session_state.documents

        if "analytics_load_time" in st.session_state:
            load_time = st.session_state.analytics_load_time
            time_diff = datetime.now() - load_time
            minutes_ago = int(time_diff.total_seconds() / 60)

            freshness_text = "just now" if minutes_ago < 1 else f"{minutes_ago} min ago"
            st.markdown(
                f"""
                <div class="text-secondary" style="text-align: right; font-size: 0.85rem; margin-bottom: 1rem;">
                    📡 Data loaded {freshness_text} | {len(docs)} documents
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                <span style="font-size: 2rem;">📊</span>
                Key Performance Indicators
            </h3>
        """,
            unsafe_allow_html=True,
        )

        total_gross = sum([doc.get("totalGross", 0) for doc in docs])
        total_net = sum([doc.get("totalNet", 0) for doc in docs])
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

        payment_counts = {}
        payment_totals = {}
        for doc in docs:
            payment = doc.get("paymentState", "Unknown")
            payment_counts[payment] = payment_counts.get(payment, 0) + 1
            payment_totals[payment] = payment_totals.get(payment, 0) + doc.get(
                "totalGross", 0
            )

        pending_payment_value = payment_totals.get("Open", 0) + payment_totals.get(
            "Pending", 0
        )

        unique_companies = len(
            set([doc.get("companyName") for doc in docs if doc.get("companyName")])
        )
        unique_suppliers = len(
            set([doc.get("supplierName") for doc in docs if doc.get("supplierName")])
        )

        kpi_cols = st.columns(6)

        kpis = [
            ("Total Documents", len(docs), "#3b82f6", "rgba(59, 130, 246, 0.04)"),
            (
                "Total Value",
                f"€{total_gross:,.0f}",
                "#10b981",
                "rgba(16, 185, 129, 0.04)",
            ),
            (
                "Avg Invoice",
                f"€{avg_invoice_value:,.0f}",
                "#8b5cf6",
                "rgba(139, 92, 246, 0.04)",
            ),
            (
                "Approval Rate",
                f"{approval_rate:.1f}%",
                "#22c55e",
                "rgba(34, 197, 94, 0.04)",
            ),
            (
                "Pending Payments",
                f"€{pending_payment_value:,.0f}",
                "#f59e0b",
                "rgba(245, 158, 11, 0.04)",
            ),
            ("Total Tax", f"€{total_tax:,.0f}", "#ef4444", "rgba(239, 68, 68, 0.04)"),
        ]

        for idx, (label, value, color, bg) in enumerate(kpis):
            with kpi_cols[idx]:
                st.markdown(
                    f"""
                    <div class="metric-card-light" style="
                        --card-color: {bg};
                        --card-color-dark: {color}30;
                        padding: 1.5rem 0.75rem;
                        border-radius: 20px;
                        text-align: center;
                        transition: all 0.3s ease;
                        cursor: default;
                        min-height: 180px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            font-size: 2rem;
                            font-weight: 900;
                            color: {color};
                            margin-bottom: 0.5rem;
                            line-height: 1.1;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                            white-space: nowrap;
                            overflow: visible;
                        ">{value}</div>
                        <div class="metric-label" style="
                            font-size: 0.85rem;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            line-height: 1.3;
                        ">{label}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <h3 class="section-header" style="
                font-size: 1.5rem;
                font-weight: 800;
                margin: 2rem 0 1.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding-bottom: 0.75rem;
            ">
                <span style="font-size: 2rem;">📊</span>
                Detailed Analytics
            </h3>
        """,
            unsafe_allow_html=True,
        )

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📊 Financial Analysis",
                "⚙️ Workflow Analysis",
                "🏪 Supplier Analysis",
                "📅 Timeline Analysis",
            ]
        )

        with tab1:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">💰</span>
                    Financial Breakdown
                </h3>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    '<div class="section-header"><span class="section-icon">💳</span> Payment Status</div>',
                    unsafe_allow_html=True,
                )
                if payment_counts:
                    fig_payment = px.pie(
                        values=list(payment_counts.values()),
                        names=list(payment_counts.keys()),
                        hole=0.5,
                        color_discrete_sequence=[
                            "#22c55e",
                            "#f59e0b",
                            "#ef4444",
                            "#3b82f6",
                        ],
                    )
                    fig_payment.update_traces(
                        textposition="inside", textinfo="percent+label"
                    )
                    fig_payment.update_layout(height=350, showlegend=True)
                    st.plotly_chart(fig_payment, use_container_width=True)

                st.markdown(
                    '<div class="section-header"><span class="section-icon">💱</span> Currency Distribution</div>',
                    unsafe_allow_html=True,
                )
                currency_totals = {}
                for doc in docs:
                    currency = doc.get("currencyCode", "EUR")
                    value = doc.get("totalGross", 0)
                    currency_totals[currency] = currency_totals.get(currency, 0) + value

                for currency, total in sorted(
                    currency_totals.items(), key=lambda x: x[1], reverse=True
                ):
                    percentage = (total / total_gross * 100) if total_gross > 0 else 0
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
                            padding: 0.75rem;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                            border-left: 4px solid #3b82f6;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="text-primary" style="font-weight: 600;">{currency}</span>
                                <span style="font-weight: 700; color: #3b82f6;">{total:,.2f} ({percentage:.1f}%)</span>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

            with col2:
                st.markdown(
                    '<div class="section-header"><span class="section-icon">💵</span> Payment Value by Status</div>',
                    unsafe_allow_html=True,
                )
                if payment_totals:
                    fig_payment_value = px.bar(
                        x=list(payment_totals.keys()),
                        y=list(payment_totals.values()),
                        labels={"x": "Payment State", "y": "Total Value (€)"},
                        color=list(payment_totals.values()),
                        color_continuous_scale="RdYlGn",
                    )
                    fig_payment_value.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_payment_value, use_container_width=True)

                st.markdown(
                    '<div class="section-header"><span class="section-icon">🏆</span> Top 5 Largest Invoices</div>',
                    unsafe_allow_html=True,
                )
                sorted_docs = sorted(
                    docs, key=lambda x: x.get("totalGross", 0), reverse=True
                )[:5]

                for idx, doc in enumerate(sorted_docs, 1):
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
                            padding: 0.75rem;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                            border-left: 4px solid #10b981;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span class="text-primary" style="font-weight: 600;">#{idx} {doc.get('supplierName', 'N/A')[:30]}</span>
                                    <br><span class="text-secondary" style="font-size: 0.8rem;">Doc ID: {doc.get('documentId')}</span>
                                </div>
                                <span style="font-weight: 700; color: #10b981; font-size: 1.1rem;">€{doc.get('totalGross', 0):,.2f}</span>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        with tab2:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">⚙️</span>
                    Workflow Performance
                </h3>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(
                    '<div class="section-header"><span class="section-icon">📊</span> Document Workflow Funnel</div>',
                    unsafe_allow_html=True,
                )

                funnel_data = {
                    "Stage": [
                        "Draft",
                        "Stage 1",
                        "Stage 2",
                        "Stage 3",
                        "Stage 4",
                        "Stage 5",
                        "Approved",
                    ],
                    "Count": [
                        stage_counts.get("Draft", 0),
                        stage_counts.get("Stage1", 0),
                        stage_counts.get("Stage2", 0),
                        stage_counts.get("Stage3", 0),
                        stage_counts.get("Stage4", 0),
                        stage_counts.get("Stage5", 0),
                        stage_counts.get("Approved", 0),
                    ],
                }

                fig_funnel = px.funnel(funnel_data, x="Count", y="Stage", color="Count")
                fig_funnel.update_traces(marker=dict(colorscale="Blues"))
                fig_funnel.update_layout(height=400)
                st.plotly_chart(fig_funnel, use_container_width=True)

            with col2:
                st.markdown(
                    '<div class="section-header"><span class="section-icon">🎯</span> Current Stage Distribution</div>',
                    unsafe_allow_html=True,
                )

                if stage_counts:
                    fig_stages = px.pie(
                        values=list(stage_counts.values()),
                        names=list(stage_counts.keys()),
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Rainbow,
                    )
                    fig_stages.update_traces(
                        textposition="inside", textinfo="percent+label"
                    )
                    fig_stages.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig_stages, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header"><span class="section-icon">📈</span> Workflow Efficiency Metrics</div>',
                unsafe_allow_html=True,
            )

            metric_cols = st.columns(4)

            bottleneck_stage = (
                max(stage_counts.items(), key=lambda x: x[1] if "Stage" in x[0] else 0)[
                    0
                ]
                if stage_counts
                else "N/A"
            )
            completion_rate = (approved_count / len(docs) * 100) if len(docs) > 0 else 0
            in_progress_rate = (in_workflow / len(docs) * 100) if len(docs) > 0 else 0

            workflow_metrics = [
                (
                    "Completion Rate",
                    f"{completion_rate:.1f}%",
                    "#22c55e",
                    "rgba(34, 197, 94, 0.04)",
                ),
                (
                    "In Progress",
                    f"{in_progress_rate:.1f}%",
                    "#3b82f6",
                    "rgba(59, 130, 246, 0.04)",
                ),
                ("Bottleneck", bottleneck_stage, "#f59e0b", "rgba(245, 158, 11, 0.04)"),
                (
                    "Avg Stages",
                    f"{(in_workflow / 5):.1f}",
                    "#8b5cf6",
                    "rgba(139, 92, 246, 0.04)",
                ),
            ]

            for idx, (label, value, color, bg) in enumerate(workflow_metrics):
                with metric_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="metric-card-light" style="
                            --card-color: {bg};
                            --card-color-dark: {color}30;
                            padding: 1.5rem 0.75rem;
                            border-radius: 20px;
                            text-align: center;
                            transition: all 0.3s ease;
                            cursor: default;
                            min-height: 180px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            position: relative;
                            overflow: hidden;
                        ">
                            <div style="
                                font-size: 2rem;
                                font-weight: 900;
                                color: {color};
                                margin-bottom: 0.5rem;
                                line-height: 1.1;
                                word-wrap: break-word;
                                overflow-wrap: break-word;
                                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                white-space: nowrap;
                                overflow: visible;
                            ">{value}</div>
                            <div class="metric-label" style="
                                font-size: 0.85rem;
                                font-weight: 700;
                                text-transform: uppercase;
                                letter-spacing: 0.5px;
                                line-height: 1.3;
                            ">{label}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        with tab3:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">🏪</span>
                    Supplier Intelligence
                </h3>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(
                    '<div class="section-header"><span class="section-icon">🏆</span> Top 10 Suppliers by Value</div>',
                    unsafe_allow_html=True,
                )

                supplier_values = {}
                supplier_counts = {}
                for doc in docs:
                    supplier = doc.get("supplierName", "Unknown")
                    value = doc.get("totalGross", 0)
                    supplier_values[supplier] = supplier_values.get(supplier, 0) + value
                    supplier_counts[supplier] = supplier_counts.get(supplier, 0) + 1

                top_suppliers = sorted(
                    supplier_values.items(), key=lambda x: x[1], reverse=True
                )[:10]

                if top_suppliers:
                    fig_suppliers = px.bar(
                        x=[s[1] for s in top_suppliers],
                        y=[s[0] for s in top_suppliers],
                        orientation="h",
                        labels={"x": "Total Value (€)", "y": "Supplier"},
                        color=[s[1] for s in top_suppliers],
                    )
                    fig_suppliers.update_traces(marker_color="teal")
                    fig_suppliers.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_suppliers, use_container_width=True)

            with col2:
                st.markdown(
                    '<div class="section-header"><span class="section-icon">📊</span> Top 10 Suppliers by Document Count</div>',
                    unsafe_allow_html=True,
                )

                top_suppliers_count = sorted(
                    supplier_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]

                if top_suppliers_count:
                    fig_supplier_count = px.bar(
                        x=[s[1] for s in top_suppliers_count],
                        y=[s[0] for s in top_suppliers_count],
                        orientation="h",
                        labels={"x": "Number of Documents", "y": "Supplier"},
                        color=[s[1] for s in top_suppliers_count],
                    )
                    fig_supplier_count.update_traces(marker_color="purple")
                    fig_supplier_count.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_supplier_count, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header"><span class="section-icon">📋</span> Supplier Statistics Summary</div>',
                unsafe_allow_html=True,
            )

            supplier_summary = []
            for supplier in sorted(
                supplier_values.keys(), key=lambda x: supplier_values[x], reverse=True
            )[:15]:
                supplier_summary.append(
                    {
                        "Supplier": supplier,
                        "Total Value": f"€{supplier_values[supplier]:,.2f}",
                        "Documents": supplier_counts[supplier],
                        "Avg Invoice": f"€{(supplier_values[supplier] / supplier_counts[supplier]):,.2f}",
                    }
                )

            if supplier_summary:
                df_suppliers = pd.DataFrame(supplier_summary)
                st.dataframe(
                    df_suppliers, use_container_width=True, hide_index=True, height=400
                )

        with tab4:
            st.markdown(
                """
                <h3 class="section-header" style="
                    font-size: 1.35rem;
                    font-weight: 700;
                    margin: 1rem 0 1.25rem 0;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.5rem;">📅</span>
                    Timeline & Trends
                </h3>
            """,
                unsafe_allow_html=True,
            )

            docs_with_dates = [doc for doc in docs if doc.get("invoiceDate")]

            if docs_with_dates:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(
                        '<div class="section-header"><span class="section-icon">📈</span> Invoice Value Timeline</div>',
                        unsafe_allow_html=True,
                    )

                    timeline_data = []
                    for doc in docs_with_dates:
                        try:
                            timeline_data.append(
                                {
                                    "Date": pd.to_datetime(doc.get("invoiceDate")),
                                    "Value": doc.get("totalGross", 0),
                                    "Supplier": doc.get("supplierName", "Unknown")[:30],
                                    "Status": doc.get("currentStage", "Unknown"),
                                }
                            )
                        except:
                            pass

                    if timeline_data:
                        df_timeline = pd.DataFrame(timeline_data)
                        df_timeline = df_timeline.sort_values("Date")
                        df_timeline["AbsValue"] = df_timeline["Value"].abs()

                        fig_timeline = px.scatter(
                            df_timeline,
                            x="Date",
                            y="Value",
                            size="AbsValue",
                            color="Status",
                            hover_data=["Supplier", "Value"],
                            labels={
                                "Value": "Invoice Value (€)",
                                "Date": "Invoice Date",
                            },
                        )
                        fig_timeline.update_layout(height=400)
                        st.plotly_chart(fig_timeline, use_container_width=True)

                with col2:
                    st.markdown(
                        '<div class="section-header"><span class="section-icon">📊</span> Monthly Summary</div>',
                        unsafe_allow_html=True,
                    )

                    df_timeline["Month"] = (
                        df_timeline["Date"].dt.to_period("M").astype(str) 
                    )
                    monthly_summary = (
                        df_timeline.groupby("Month")
                        .agg({"Value": ["sum", "count", "mean"]})
                        .round(2)
                    )

                    monthly_summary.columns = ["Total Value", "Count", "Avg Value"]
                    monthly_summary = monthly_summary.sort_index(ascending=False).head(
                        6
                    )

                    st.dataframe(monthly_summary, use_container_width=True, height=300)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    '<div class="section-header"><span class="section-icon">📈</span> Monthly Invoice Trends</div>',
                    unsafe_allow_html=True,
                )

                monthly_trend = (
                    df_timeline.groupby("Month").agg({"Value": "sum"}).reset_index()
                )
                monthly_trend.columns = ["Month", "Total Value"]

                fig_trend = px.line(
                    monthly_trend,
                    x="Month",
                    y="Total Value",
                    markers=True,
                    labels={"Total Value": "Total Invoice Value (€)", "Month": "Month"},
                )
                fig_trend.update_traces(line_color="#3b82f6", line_width=3)
                fig_trend.update_layout(height=300)
                st.plotly_chart(fig_trend, use_container_width=True)

            else:
                st.warning(
                    "⚠️ No documents with valid invoice dates found for timeline analysis"
                )

        st.markdown("---")
        st.markdown("### 💾 Export Analytics Data")

        export_cols = st.columns(3)

        with export_cols[0]:
            df_export = pd.DataFrame(
                [
                    {
                        "Document ID": doc.get("documentId"),
                        "Supplier": doc.get("supplierName"),
                        "Company": doc.get("companyName"),
                        "Invoice Date": doc.get("invoiceDate"),
                        "Total Gross": doc.get("totalGross"),
                        "Total Net": doc.get("totalNet"),
                        "Currency": doc.get("currencyCode"),
                        "Stage": doc.get("currentStage"),
                        "Payment State": doc.get("paymentState"),
                    }
                    for doc in docs
                ]
            )

            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📥 CSV - " + t("analytics_page.download_full_data"),
                data=csv_data,
                file_name=f"analytics_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            excel_data = to_excel(df_export)
            st.download_button(
                label="📥 Excel - " + t("analytics_page.download_full_data"),
                data=excel_data,
                file_name=f"analytics_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with export_cols[1]:
            if supplier_summary:
                df_supplier_export = pd.DataFrame(supplier_summary)
                csv_supplier = df_supplier_export.to_csv(index=False)
                st.download_button(
                    label="📥 CSV - " + t("analytics_page.download_supplier_report"),
                    data=csv_supplier,
                    file_name=f"supplier_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                excel_supplier = to_excel(df_supplier_export)
                st.download_button(
                    label="📥 Excel - " + t("analytics_page.download_supplier_report"),
                    data=excel_supplier,
                    file_name=f"supplier_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        with export_cols[2]:
            workflow_export = pd.DataFrame(
                [
                    {
                        "Stage": stage,
                        "Count": count,
                        "Percentage": f"{(count/len(docs)*100):.1f}%",
                    }
                    for stage, count in sorted(
                        stage_counts.items(), key=lambda x: x[1], reverse=True
                    )
                ]
            )
            csv_workflow = workflow_export.to_csv(index=False)
            st.download_button(
                label="📥 CSV - " + t("analytics_page.download_workflow_report"),
                data=csv_workflow,
                file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            excel_workflow = to_excel(workflow_export)
            st.download_button(
                label="📥 Excel - " + t("analytics_page.download_workflow_report"),
                data=excel_workflow,
                file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
