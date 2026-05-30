"""Budget model — CRUD and status queries."""

import sqlite3
import calendar
from typing import Optional


def set_budget(conn: sqlite3.Connection, category_id: int, month: str, amount: float):
    conn.execute(
        """INSERT INTO budgets (category_id, month, amount) VALUES (?, ?, ?)
           ON CONFLICT(category_id, month) DO UPDATE SET amount=excluded.amount""",
        (category_id, month, amount),
    )
    conn.commit()


def get_budget(conn: sqlite3.Connection, category_id: int, month: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM budgets WHERE category_id=? AND month=?",
        (category_id, month),
    ).fetchone()


def get_all_budgets_for_month(conn: sqlite3.Connection, month: str) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT b.*, c.name as category_name, c.icon as category_icon
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           WHERE b.month=?
           ORDER BY c.sort_order""",
        (month,),
    ).fetchall()


def delete_budget(conn: sqlite3.Connection, category_id: int, month: str):
    conn.execute(
        "DELETE FROM budgets WHERE category_id=? AND month=?",
        (category_id, month),
    )
    conn.commit()


def get_budget_status(conn: sqlite3.Connection, month: str) -> list[dict]:
    """Return budget with spent, remaining, and percentage for each budgeted category."""
    year_str, month_str = month.split("-")
    year = int(year_str)
    m = int(month_str)
    last_day = calendar.monthrange(year, m)[1]
    start_date = f"{year_str}-{m:02d}-01"
    end_date = f"{year_str}-{m:02d}-{last_day:02d}"

    rows = conn.execute(
        """SELECT b.*, c.name as category_name, c.icon as category_icon,
                  COALESCE(SUM(t.amount), 0) as spent
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           LEFT JOIN transactions t ON t.category_id = b.category_id
               AND t.date >= ? AND t.date <= ?
               AND t.type = 'expense'
           WHERE b.month=?
           GROUP BY b.id
           ORDER BY c.sort_order""",
        (start_date, end_date, month),
    ).fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["remaining"] = d["amount"] - d["spent"]
        d["percentage"] = round((d["spent"] / d["amount"]) * 100, 1) if d["amount"] > 0 else 0
        result.append(d)
    return result
