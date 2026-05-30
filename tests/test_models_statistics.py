import sqlite3
import pytest
from database.schema import create_tables
from database.seed import seed_data
from models.statistics import (
    get_monthly_summary,
    get_yearly_summary,
    get_category_summary,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    c.row_factory = sqlite3.Row
    create_tables(c)
    seed_data(c)
    return c


@pytest.fixture
def seed_transactions(conn):
    from models.transaction import add_transaction
    add_transaction(conn, "expense", 1000.0, category_id=1, account_id=1, date="2026-05-01")
    add_transaction(conn, "expense", 500.0, category_id=2, account_id=1, date="2026-05-05")
    add_transaction(conn, "income", 8000.0, category_id=12, account_id=2, date="2026-05-01")
    add_transaction(conn, "expense", 2000.0, category_id=1, account_id=1, date="2026-04-10")
    add_transaction(conn, "income", 8000.0, category_id=12, account_id=2, date="2026-04-01")
    add_transaction(conn, "income", 2000.0, category_id=13, account_id=2, date="2026-04-15")
    return conn


def test_get_monthly_summary(seed_transactions):
    conn = seed_transactions
    summary = get_monthly_summary(conn, "2026", "05")
    assert summary["income"] == 8000.0
    assert summary["expense"] == 1500.0
    assert summary["balance"] == 6500.0


def test_get_yearly_summary(seed_transactions):
    conn = seed_transactions
    summary = get_yearly_summary(conn, "2026")
    assert len(summary) == 2
    may = [s for s in summary if s["month"] == "05"][0]
    apr = [s for s in summary if s["month"] == "04"][0]
    assert may["income"] == 8000.0
    assert may["expense"] == 1500.0
    assert apr["income"] == 10000.0
    assert apr["expense"] == 2000.0


def test_get_category_summary(seed_transactions):
    conn = seed_transactions
    summary = get_category_summary(conn, "expense", "2026-05")
    assert len(summary) == 2
    total = sum(s["total"] for s in summary)
    assert total == 1500.0
