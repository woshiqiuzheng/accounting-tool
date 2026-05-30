import sqlite3
import pytest
from database.schema import create_tables
from database.seed import seed_data
from models.transaction import (
    add_transaction,
    get_transaction_by_id,
    get_transactions,
    update_transaction,
    delete_transaction,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    c.row_factory = sqlite3.Row
    create_tables(c)
    seed_data(c)
    return c


def test_add_expense(conn):
    add_transaction(conn, "expense", 35.0, category_id=1, account_id=1, note="午餐", date="2026-05-30")
    txs = get_transactions(conn)
    assert len(txs) == 1
    assert txs[0]["amount"] == 35.0
    assert txs[0]["type"] == "expense"


def test_add_income(conn):
    add_transaction(conn, "income", 5000.0, category_id=12, account_id=2, note="工资", date="2026-05-01")
    txs = get_transactions(conn)
    assert len(txs) == 1
    assert txs[0]["type"] == "income"


def test_add_transfer(conn):
    add_transaction(conn, "transfer", 1000.0, account_id=1, to_account_id=2, note="转到银行卡", date="2026-05-15")
    txs = get_transactions(conn)
    assert len(txs) == 1
    assert txs[0]["type"] == "transfer"
    assert txs[0]["category_id"] is None


def test_get_transaction_by_id(conn):
    add_transaction(conn, "expense", 20.0, category_id=2, account_id=1, date="2026-05-30")
    txs = get_transactions(conn)
    result = get_transaction_by_id(conn, txs[0]["id"])
    assert result is not None
    assert result["amount"] == 20.0


def test_update_transaction(conn):
    add_transaction(conn, "expense", 15.0, category_id=1, account_id=1, note="早餐", date="2026-05-30")
    txs = get_transactions(conn)
    update_transaction(conn, txs[0]["id"], amount=20.0, note="早午餐")
    updated = get_transaction_by_id(conn, txs[0]["id"])
    assert updated["amount"] == 20.0
    assert updated["note"] == "早午餐"


def test_delete_transaction(conn):
    add_transaction(conn, "expense", 10.0, category_id=1, account_id=1, date="2026-05-30")
    add_transaction(conn, "expense", 20.0, category_id=1, account_id=1, date="2026-05-30")
    txs = get_transactions(conn)
    delete_transaction(conn, txs[0]["id"])
    remaining = get_transactions(conn)
    assert len(remaining) == 1


def test_get_transactions_with_filters(conn):
    add_transaction(conn, "expense", 35.0, category_id=1, account_id=1, date="2026-05-01")
    add_transaction(conn, "expense", 50.0, category_id=2, account_id=1, date="2026-05-02")
    add_transaction(conn, "income", 5000.0, category_id=12, account_id=2, note="午餐", date="2026-05-01")

    # Filter by type
    result = get_transactions(conn, typ="expense")
    assert len(result) == 2

    # Filter by category
    result = get_transactions(conn, category_id=1)
    assert len(result) == 1

    # Filter by date range
    result = get_transactions(conn, start_date="2026-05-02", end_date="2026-05-31")
    assert len(result) == 1

    # Filter by search text
    result = get_transactions(conn, search="午餐")
    assert len(result) == 1


def test_pagination(conn):
    for i in range(25):
        add_transaction(conn, "expense", float(i + 1), category_id=1, account_id=1, date=f"2026-05-{(i % 30) + 1:02d}")
    page1 = get_transactions(conn, limit=20, offset=0)
    assert len(page1) == 20
    page2 = get_transactions(conn, limit=20, offset=20)
    assert len(page2) == 5
