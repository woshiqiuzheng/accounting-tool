"""Utility helpers — date, currency formatting."""

import calendar
from datetime import datetime, date
from typing import Optional


def format_currency(amount: float) -> str:
    """Format a number as CNY currency string."""
    if amount >= 0:
        return f"¥{amount:,.2f}"
    return f"-¥{abs(amount):,.2f}"


def today_str() -> str:
    """Return today's date as YYYY-MM-DD."""
    return date.today().isoformat()


def current_month_str() -> str:
    """Return current month as YYYY-MM."""
    return date.today().strftime("%Y-%m")


def get_month_date_range(year: int, month: int) -> tuple[str, str]:
    """Return (start_date, end_date) for a given month."""
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year:04d}-{month:02d}-01"
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
    return start, end


def parse_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD string to date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def format_date_display(date_str: str) -> str:
    """Convert YYYY-MM-DD to user-friendly display format."""
    d = parse_date(date_str)
    if d:
        return d.strftime("%Y年%m月%d日")
    return date_str
