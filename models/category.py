"""Category model — CRUD operations for transaction categories."""

import sqlite3
from typing import Optional
from database.seed import EXPENSE_CATEGORIES, INCOME_CATEGORIES


def get_all_categories(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM categories ORDER BY type, sort_order"
    ).fetchall()


def get_categories_by_type(conn: sqlite3.Connection, typ: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM categories WHERE type=? ORDER BY sort_order", (typ,)
    ).fetchall()


def get_category_by_id(conn: sqlite3.Connection, category_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM categories WHERE id=?", (category_id,)
    ).fetchone()


def add_category(conn: sqlite3.Connection, name: str, typ: str, icon: str = "❓", sort_order: int = 0):
    conn.execute(
        "INSERT INTO categories (name, type, icon, sort_order) VALUES (?, ?, ?, ?)",
        (name, typ, icon, sort_order),
    )
    conn.commit()


def update_category(conn: sqlite3.Connection, category_id: int, name: str, icon: str, sort_order: int):
    conn.execute(
        "UPDATE categories SET name=?, icon=?, sort_order=? WHERE id=?",
        (name, icon, sort_order, category_id),
    )
    conn.commit()


def delete_category(conn: sqlite3.Connection, category_id: int):
    conn.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()


def get_category_usage_count(conn: sqlite3.Connection, category_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE category_id=?",
        (category_id,),
    ).fetchone()
    return row["cnt"] if row else 0


def reset_to_defaults(conn: sqlite3.Connection):
    conn.execute("DELETE FROM categories")
    for name, typ, icon, sort_order in EXPENSE_CATEGORIES + INCOME_CATEGORIES:
        conn.execute(
            "INSERT INTO categories (name, type, icon, sort_order) VALUES (?, ?, ?, ?)",
            (name, typ, icon, sort_order),
        )
    conn.commit()
