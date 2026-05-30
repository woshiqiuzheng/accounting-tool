"""Account model — CRUD operations for accounts."""

import sqlite3
from typing import Optional
from database.seed import DEFAULT_ACCOUNTS


def get_all_accounts(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM accounts ORDER BY sort_order"
    ).fetchall()


def get_account_by_id(conn: sqlite3.Connection, account_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM accounts WHERE id=?", (account_id,)
    ).fetchone()


def add_account(conn: sqlite3.Connection, name: str, balance: float = 0.0, icon: str = "💳", sort_order: int = 0):
    conn.execute(
        "INSERT INTO accounts (name, balance, icon, sort_order) VALUES (?, ?, ?, ?)",
        (name, balance, icon, sort_order),
    )
    conn.commit()


def update_account(conn: sqlite3.Connection, account_id: int, name: str, icon: str, sort_order: int):
    conn.execute(
        "UPDATE accounts SET name=?, icon=?, sort_order=? WHERE id=?",
        (name, icon, sort_order, account_id),
    )
    conn.commit()


def update_balance(conn: sqlite3.Connection, account_id: int, new_balance: float):
    conn.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, account_id))
    conn.commit()


def delete_account(conn: sqlite3.Connection, account_id: int):
    conn.execute("DELETE FROM accounts WHERE id=?", (account_id,))
    conn.commit()


def get_account_usage_count(conn: sqlite3.Connection, account_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE account_id=? OR to_account_id=?",
        (account_id, account_id),
    ).fetchone()
    return row["cnt"] if row else 0


def reset_to_defaults(conn: sqlite3.Connection):
    conn.execute("DELETE FROM accounts")
    for name, balance, icon, sort_order in DEFAULT_ACCOUNTS:
        conn.execute(
            "INSERT INTO accounts (name, balance, icon, sort_order) VALUES (?, ?, ?, ?)",
            (name, balance, icon, sort_order),
        )
    conn.commit()
