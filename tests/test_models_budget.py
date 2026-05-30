import sqlite3
import pytest
from database.schema import create_tables
from database.seed import seed_data
from models.budget import (
    set_budget,
    get_budget,
    get_all_budgets_for_month,
    delete_budget,
    get_budget_status,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    c.row_factory = sqlite3.Row
    create_tables(c)
    seed_data(c)
    return c


def test_set_budget(conn):
    set_budget(conn, 1, "2026-05", 1500.0)
    budget = get_budget(conn, 1, "2026-05")
    assert budget is not None
    assert budget["amount"] == 1500.0


def test_set_budget_update_existing(conn):
    set_budget(conn, 1, "2026-05", 1500.0)
    set_budget(conn, 1, "2026-05", 2000.0)
    budget = get_budget(conn, 1, "2026-05")
    assert budget["amount"] == 2000.0


def test_get_all_budgets_for_month(conn):
    set_budget(conn, 1, "2026-05", 1500.0)
    set_budget(conn, 2, "2026-05", 500.0)
    budgets = get_all_budgets_for_month(conn, "2026-05")
    assert len(budgets) == 2


def test_delete_budget(conn):
    set_budget(conn, 1, "2026-05", 1500.0)
    delete_budget(conn, 1, "2026-05")
    budget = get_budget(conn, 1, "2026-05")
    assert budget is None


def test_get_budget_status(conn):
    set_budget(conn, 1, "2026-05", 1000.0)
    from models.transaction import add_transaction
    add_transaction(conn, "expense", 300.0, category_id=1, account_id=1, date="2026-05-01")
    add_transaction(conn, "expense", 200.0, category_id=1, account_id=1, date="2026-05-02")

    status = get_budget_status(conn, "2026-05")
    assert len(status) >= 1
    cat1 = [s for s in status if s["category_id"] == 1]
    assert len(cat1) == 1
    assert cat1[0]["spent"] == 500.0
    assert cat1[0]["remaining"] == 500.0
    assert cat1[0]["percentage"] == 50.0
