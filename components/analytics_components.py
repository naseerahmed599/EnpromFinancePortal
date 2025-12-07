"""
Reusable UI Components for Analytics Dashboard
Professional, modular components following DRY principles
"""

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar


def render_kpi_card(label, value, color="#3b82f6", trend=None, trend_value=None):
    """
    Render an enhanced KPI card with optional trend indicator

    Args:
        label: KPI label text
        value: KPI value (string or number)
        color: Accent color for the card
        trend: 'up', 'down', or None
        trend_value: Percentage or value change (e.g., "+12.5%", "-3.2%")

    Returns:
        HTML string for the KPI card
    """
    trend_html = ""
    if trend and trend_value:
        trend_class = (
            "positive"
            if trend == "up"
            else "negative" if trend == "down" else "neutral"
        )
        trend_icon = "↑" if trend == "up" else "↓" if trend == "down" else "→"
        trend_html = (
            f'<div class="kpi-trend {trend_class}">{trend_icon} {trend_value}</div>'
        )

    return f"""
        <div class="kpi-card-enhanced" style="--card-accent: {color}; --card-accent-end: {color}dd;">
            <p class="kpi-label-main">{label}</p>
            <div class="kpi-value-main" style="--value-color: {color};">{value}</div>
            {trend_html}
        </div>
    """


def render_total_badge(label, value):
    """
    Render a prominent total badge with better color scheme

    Args:
        label: Badge label
        value: Badge value

    Returns:
        HTML string for the total badge
    """
    return f"""
        <div style="text-align: right; margin-top: 0.5rem;">
            <div class="total-badge">
                <span>💰</span>
                <span>{label}: {value}</span>
            </div>
        </div>
    """


def render_tab_badge(count):
    """
    Render a badge showing count for tabs

    Args:
        count: Number to display

    Returns:
        HTML string for the tab badge
    """
    return f'<span class="tab-badge">{count}</span>'


def get_quick_date_filters():
    """
    Generate quick date filter presets

    Returns:
        Dictionary of filter name to (start_date, end_date) tuples
    """
    today = date.today()

    # This Month
    this_month_start = date(today.year, today.month, 1)
    this_month_end = date(
        today.year, today.month, calendar.monthrange(today.year, today.month)[1]
    )

    last_month_date = today - relativedelta(months=1)
    last_month_start = date(last_month_date.year, last_month_date.month, 1)
    last_month_end = date(
        last_month_date.year,
        last_month_date.month,
        calendar.monthrange(last_month_date.year, last_month_date.month)[1],
    )

    current_quarter = (today.month - 1) // 3
    quarter_start_month = current_quarter * 3 + 1
    this_quarter_start = date(today.year, quarter_start_month, 1)
    quarter_end_month = quarter_start_month + 2
    this_quarter_end = date(
        today.year,
        quarter_end_month,
        calendar.monthrange(today.year, quarter_end_month)[1],
    )

    last_quarter_start = this_quarter_start - relativedelta(months=3)
    last_quarter_end_month = last_quarter_start.month + 2
    last_quarter_end = date(
        last_quarter_start.year,
        last_quarter_end_month,
        calendar.monthrange(last_quarter_start.year, last_quarter_end_month)[1],
    )

    ytd_start = date(today.year, 1, 1)
    ytd_end = today

    last_year_start = date(today.year - 1, 1, 1)
    last_year_end = date(today.year - 1, 12, 31)

    last_30_days = today - relativedelta(days=30)

    last_90_days = today - relativedelta(days=90)

    return {
        "This Month": (this_month_start, this_month_end),
        "Last Month": (last_month_start, last_month_end),
        "This Quarter": (this_quarter_start, this_quarter_end),
        "Last Quarter": (last_quarter_start, last_quarter_end),
        "YTD": (ytd_start, ytd_end),
        "Last Year": (last_year_start, last_year_end),
        "Last 30 Days": (last_30_days, today),
        "Last 90 Days": (last_90_days, today),
    }


def calculate_kpi_trend(current_value, previous_value):
    """
    Calculate trend direction and percentage change

    Args:
        current_value: Current period value
        previous_value: Previous period value

    Returns:
        Tuple of (trend_direction, trend_percentage_string)
        trend_direction: 'up', 'down', or 'neutral'
        trend_percentage_string: e.g., "+12.5%" or "-3.2%"
    """
    if previous_value == 0:
        if current_value > 0:
            return ("up", "+100%")
        elif current_value < 0:
            return ("down", "-100%")
        else:
            return ("neutral", "0%")

    change = ((current_value - previous_value) / abs(previous_value)) * 100

    if abs(change) < 0.1:
        return ("neutral", "0%")

    trend = "up" if change > 0 else "down"
    sign = "+" if change > 0 else ""

    return (trend, f"{sign}{change:.1f}%")


def render_quick_filters_bar(t):
    """
    Render quick date filter buttons

    Args:
        t: Translation function

    Returns:
        HTML string for quick filters bar
    """
    filters = list(get_quick_date_filters().keys())

    buttons_html = ""
    for filter_name in filters:
        buttons_html += f'<button class="quick-filter-btn" data-filter="{filter_name}">{filter_name}</button>'

    return f"""
        <div style="
            display: flex;
            gap: 0.75rem;
            padding: 1rem;
            background: rgba(248, 250, 252, 0.5);
            border-radius: 12px;
            margin-bottom: 1.5rem;
            overflow-x: auto;
            flex-wrap: wrap;
        ">
            <span style="
                font-weight: 600;
                color: #64748b;
                display: flex;
                align-items: center;
                white-space: nowrap;
            ">📅 Quick Filters:</span>
            {buttons_html}
        </div>
    """


def get_filter_summary(filters_dict):
    """
    Generate a summary of active filters

    Args:
        filters_dict: Dictionary of filter names to values

    Returns:
        List of active filter descriptions
    """
    active_filters = []

    for key, value in filters_dict.items():
        if value and value != "All" and value != []:
            if isinstance(value, list):
                active_filters.append(f"{key}: {len(value)} selected")
            else:
                active_filters.append(f"{key}: {value}")

    return active_filters


def render_filter_summary_badge(active_filters):
    """
    Render a badge showing number of active filters

    Args:
        active_filters: List of active filter descriptions

    Returns:
        HTML string for filter summary badge
    """
    if not active_filters:
        return ""

    count = len(active_filters)
    filters_text = "<br>".join(active_filters)

    return f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
        " title="{filters_text}">
            <span>🔍</span>
            <span>{count} Active Filter{'s' if count != 1 else ''}</span>
        </div>
    """
