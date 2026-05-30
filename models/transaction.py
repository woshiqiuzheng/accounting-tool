"""Transaction model — CRUD and query operations."""

import sqlite3
from typing import Optional


def add_transaction(
    conn: sqlite3.Connection,
    typ: str,
    amount: float,
    category_id: Optional[int] = None,
    account_id: int = 1,
    to_account_id: Optional[int] = None,
    note: str = "",
    date: Optional[str] = None,
):
    conn.execute(
        """INSERT INTO transactions (type, amount, category_id, account_id, to_account_id, note, date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (typ, amount, category_id, account_id, to_account_id, note, date),
    )
    conn.commit()


def get_transaction_by_id(conn: sqlite3.Connection, transaction_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        """SELECT t.*, c.name as category_name, c.icon as category_icon,
                  a.name as account_name, a2.name as to_account_name
           FROM transactions t
           LEFT JOIN categories c ON t.category_id = c.id
           LEFT JOIN accounts a ON t.account_id = a.id
           LEFT JOIN accounts a2 ON t.to_account_id = a2.id
           WHERE t.id=?""",
        (transaction_id,),
    ).fetchone()


def get_transactions(
    conn: sqlite3.Connection,
    typ: Optional[str] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
) -> list[sqlite3.Row]:
    query = """SELECT t.*, c.name as category_name, c.icon as category_icon,
                      a.name as account_name, a2.name as to_account_name
               FROM transactions t
               LEFT JOIN categories c ON t.category_id = c.id
               LEFT JOIN accounts a ON t.account_id = a.id
               LEFT JOIN accounts a2 ON t.to_account_id = a2.id
               WHERE 1=1"""
    params = []

    if typ and typ != "all":
        query += " AND t.type=?"
        params.append(typ)
    if category_id:
        query += " AND t.category_id=?"
        params.append(category_id)
    if account_id:
        query += " AND (t.account_id=? OR t.to_account_id=?)"
        params.extend([account_id, account_id])
    if start_date:
        query += " AND t.date>=?"
        params.append(start_date)
    if end_date:
        query += " AND t.date<=?"
        params.append(end_date)
    if search:
        query += " AND t.note LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY t.date DESC, t.id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    return conn.execute(query, params).fetchall()


def update_transaction(
    conn: sqlite3.Connection,
    transaction_id: int,
    typ: Optional[str] = None,
    amount: Optional[float] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    to_account_id: Optional[int] = None,
    note: Optional[str] = None,
    date: Optional[str] = None,
):
    fields = []
    params = []
    for field, value in [
        ("type", typ),
        ("amount", amount),
        ("category_id", category_id),
        ("account_id", account_id),
        ("to_account_id", to_account_id),
        ("note", note),
        ("date", date),
    ]:
        if value is not None:
            fields.append(f"{field}=?")
            params.append(value)
    if not fields:
        return
    fields.append("updated_at=datetime('now','localtime')")
    params.append(transaction_id)
    conn.execute(
        f"UPDATE transactions SET {', '.join(fields)} WHERE id=?",
        params,
    )
    conn.commit()


def delete_transaction(conn: sqlite3.Connection, transaction_id: int):
    conn.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()
