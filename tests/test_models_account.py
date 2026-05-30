import sqlite3
import pytest
from database.schema import create_tables
from database.seed import seed_data
from models.account import (
    get_all_accounts,
    get_account_by_id,
    add_account,
    update_account,
    delete_account,
    update_balance,
    get_account_usage_count,
    reset_to_defaults,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    c.row_factory = sqlite3.Row
    create_tables(c)
    seed_data(c)
    return c


def test_get_all_accounts(conn):
    accounts = get_all_accounts(conn)
    assert len(accounts) == 4


def test_get_account_by_id(conn):
    accounts = get_all_accounts(conn)
    target = accounts[0]
    result = get_account_by_id(conn, target["id"])
    assert result is not None
    assert result["id"] == target["id"]


def test_add_account(conn):
    add_account(conn, "信用卡", -2000, "🏦", 5)
    accounts = get_all_accounts(conn)
    assert len(accounts) == 5
    names = [a["name"] for a in accounts]
    assert "信用卡" in names


def test_update_account(conn):
    accounts = get_all_accounts(conn)
    target = accounts[0]
    update_account(conn, target["id"], "零钱包", "👛", 0)
    updated = get_account_by_id(conn, target["id"])
    assert updated["name"] == "零钱包"
    assert updated["icon"] == "👛"


def test_update_balance(conn):
    accounts = get_all_accounts(conn)
    target = accounts[0]
    update_balance(conn, target["id"], 1000.0)
    updated = get_account_by_id(conn, target["id"])
    assert updated["balance"] == 1000.0


def test_delete_account(conn):
    before = len(get_all_accounts(conn))
    target = get_all_accounts(conn)[0]
    delete_account(conn, target["id"])
    remaining = get_all_accounts(conn)
    assert len(remaining) == before - 1
    ids = [a["id"] for a in remaining]
    assert target["id"] not in ids


def test_get_account_usage_count(conn):
    count = get_account_usage_count(conn, 1)
    assert count == 0


def test_reset_to_defaults(conn):
    add_account(conn, "自定义", 500, "🧪", 99)
    n_before = len(get_all_accounts(conn))
    reset_to_defaults(conn)
    n_after = len(get_all_accounts(conn))
    assert n_after < n_before
    assert n_after == 4
    first = get_all_accounts(conn)[0]
    assert first["name"] == "现金"
