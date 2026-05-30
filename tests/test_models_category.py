import sqlite3
import pytest
from database.schema import create_tables
from database.seed import seed_data
from models.category import (
    get_all_categories,
    get_categories_by_type,
    get_category_by_id,
    get_category_usage_count,
    add_category,
    update_category,
    delete_category,
    reset_to_defaults,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    create_tables(c)
    seed_data(c)
    return c


def test_get_all_categories(conn):
    cats = get_all_categories(conn)
    assert len(cats) >= 17


def test_get_categories_by_type(conn):
    expenses = get_categories_by_type(conn, "expense")
    incomes = get_categories_by_type(conn, "income")
    assert len(expenses) == 11
    assert len(incomes) == 6
    for e in expenses:
        assert e["type"] == "expense"


def test_add_category(conn):
    add_category(conn, "测试", "expense", "🧪")
    cats = get_categories_by_type(conn, "expense")
    names = [c["name"] for c in cats]
    assert "测试" in names


def test_get_category_by_id(conn):
    cats = get_all_categories(conn)
    target = cats[0]
    result = get_category_by_id(conn, target["id"])
    assert result is not None
    assert result["id"] == target["id"]
    assert result["name"] == target["name"]
    assert result["type"] == target["type"]
    assert result["icon"] == target["icon"]


def test_get_category_usage_count(conn):
    cats = get_all_categories(conn)
    unused = cats[0]
    count = get_category_usage_count(conn, unused["id"])
    assert count == 0


def test_update_category(conn):
    cats = get_categories_by_type(conn, "expense")
    target = cats[0]
    update_category(conn, target["id"], "新名称", "🍜", 5)
    updated = conn.execute(
        "SELECT * FROM categories WHERE id=?", (target["id"],)
    ).fetchone()
    assert updated["name"] == "新名称"
    assert updated["icon"] == "🍜"
    assert updated["sort_order"] == 5


def test_delete_category(conn):
    before = len(get_all_categories(conn))
    cats = get_categories_by_type(conn, "expense")
    target = cats[0]
    delete_category(conn, target["id"])
    remaining = get_all_categories(conn)
    ids = [c["id"] for c in remaining]
    assert target["id"] not in ids
    assert len(remaining) == before - 1


def test_reset_to_defaults(conn):
    add_category(conn, "自定义", "expense", "🧪")
    n_before = len(get_all_categories(conn))
    reset_to_defaults(conn)
    n_after = len(get_all_categories(conn))
    assert n_after < n_before
    assert n_after == 17
    cats = get_all_categories(conn)
    assert cats[0]["name"] == "餐饮"
