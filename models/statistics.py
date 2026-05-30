"""Statistics model — aggregation queries for reports."""

import sqlite3
import calendar


def get_monthly_summary(conn: sqlite3.Connection, year: str, month: str) -> dict:
    """Return income, expense, balance for a single month."""
    m = int(month)
    start = f"{year}-{m:02d}-01"
    last_day = calendar.monthrange(int(year), m)[1]
    end = f"{year}-{m:02d}-{last_day:02d}"

    row = conn.execute(
        """SELECT
               COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
               COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions
           WHERE date >= ? AND date <= ?""",
        (start, end),
    ).fetchone()

    return {
        "income": row["income"],
        "expense": row["expense"],
        "balance": row["income"] - row["expense"],
    }


def get_yearly_summary(conn: sqlite3.Connection, year: str) -> list[dict]:
    """Return monthly income/expense/balance for each month in the year."""
    rows = conn.execute(
        """SELECT
               substr(date, 6, 2) as month,
               COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
               COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions
           WHERE date LIKE ?
           GROUP BY substr(date, 6, 2)
           ORDER BY month""",
        (f"{year}-%",),
    ).fetchall()

    return [
        {
            "month": r["month"],
            "income": r["income"],
            "expense": r["expense"],
            "balance": r["income"] - r["expense"],
        }
        for r in rows
    ]


def get_category_summary(conn: sqlite3.Connection, typ: str, month: str) -> list[dict]:
    """Return per-category totals for a given type and month."""
    year_str, month_str = month.split("-")
    m = int(month_str)
    last_day = calendar.monthrange(int(year_str), m)[1]
    start = f"{year_str}-{m:02d}-01"
    end = f"{year_str}-{m:02d}-{last_day:02d}"

    rows = conn.execute(
        """SELECT c.id, c.name, c.icon, SUM(t.amount) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.type=? AND t.date >= ? AND t.date <= ?
           GROUP BY c.id
           ORDER BY total DESC""",
        (typ, start, end),
    ).fetchall()

    return [dict(r) for r in rows]
