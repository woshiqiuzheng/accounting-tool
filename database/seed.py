"""Seed data — presets for categories and accounts."""

import sqlite3


EXPENSE_CATEGORIES = [
    ("餐饮", "expense", "🍜", 1),
    ("交通", "expense", "🚗", 2),
    ("购物", "expense", "🛒", 3),
    ("居住", "expense", "🏠", 4),
    ("通讯", "expense", "📱", 5),
    ("娱乐", "expense", "🎮", 6),
    ("医疗", "expense", "🏥", 7),
    ("教育", "expense", "📚", 8),
    ("人情", "expense", "🎁", 9),
    ("旅行", "expense", "✈️", 10),
    ("其他", "expense", "❓", 99),
]

INCOME_CATEGORIES = [
    ("工资", "income", "💼", 1),
    ("兼职", "income", "🏪", 2),
    ("奖金", "income", "🎯", 3),
    ("理财", "income", "📈", 4),
    ("红包", "income", "🧧", 5),
    ("其他", "income", "❓", 99),
]

DEFAULT_ACCOUNTS = [
    ("现金", 0.0, "💳", 1),
    ("银行卡", 0.0, "🏦", 2),
    ("支付宝", 0.0, "📱", 3),
    ("微信支付", 0.0, "💚", 4),
]


def seed_data(conn: sqlite3.Connection):
    """Insert preset data if tables are empty."""
    cur = conn.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] > 0:
        return  # already seeded

    for name, typ, icon, sort_order in EXPENSE_CATEGORIES + INCOME_CATEGORIES:
        conn.execute(
            "INSERT INTO categories (name, type, icon, sort_order) VALUES (?, ?, ?, ?)",
            (name, typ, icon, sort_order),
        )

    for name, balance, icon, sort_order in DEFAULT_ACCOUNTS:
        conn.execute(
            "INSERT INTO accounts (name, balance, icon, sort_order) VALUES (?, ?, ?, ?)",
            (name, balance, icon, sort_order),
        )
    conn.commit()
