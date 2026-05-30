# tests/test_database.py
import sqlite3
from database.schema import create_tables
from database.seed import seed_data


def test_create_tables():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    create_tables(conn)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    names = [r[0] for r in tables]
    assert "categories" in names
    assert "accounts" in names
    assert "transactions" in names
    assert "budgets" in names
    conn.close()


def test_seed_data():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    create_tables(conn)
    seed_data(conn)
    cats = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    assert cats == 17  # 11 expense + 6 income
    accs = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    assert accs == 4
    conn.close()
