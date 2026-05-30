# 个人记账本 v1.0 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully functional personal desktop accounting tool with CustomTkinter, SQLite, and Matplotlib.

**Architecture:** Three-layer architecture (database → models → UI) with a single-window sidebar navigation. Each model has CRUD operations against SQLite. UI pages are independent modules that refresh on activation.

**Tech Stack:** Python 3.10+, CustomTkinter, SQLite3 (stdlib), Matplotlib, Pillow

---

### Task 1: Project structure and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `database/__init__.py`
- Create: `models/__init__.py`
- Create: `ui/__init__.py`
- Create: `ui/pages/__init__.py`
- Create: `ui/widgets/__init__.py`
- Create: `utils/__init__.py`
- Create: `tests/__init__.py`
- Modify: `main.py` (overwrite)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/{database,models,ui/pages,ui/widgets,utils,tests}
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
.DS_Store
.superpowers/
```

- [ ] **Step 3: Create requirements.txt**

```txt
customtkinter>=5.2.0
Pillow>=10.0.0
matplotlib>=3.7.0
pytest>=7.0.0
```

- [ ] **Step 4: Create all `__init__.py` files (empty)**

```bash
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/database/__init__.py
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/models/__init__.py
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/ui/__init__.py
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/ui/pages/__init__.py
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/ui/widgets/__init__.py
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/utils/__init__.py
touch /Users/Kioz/PyCharmProject/vibecodingstudy/first_project/tests/__init__.py
```

- [ ] **Step 5: Install dependencies**

```bash
pip install customtkinter Pillow matplotlib pytest
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: scaffold project structure and dependencies"
```

---

### Task 2: Database connection and schema

**Files:**
- Create: `database/connection.py`
- Create: `database/schema.py`

- [ ] **Step 1: Create connection.py — singleton SQLite connection manager**

```python
"""Database connection manager — single file-based SQLite connection."""

import sqlite3
import os
import shutil
from pathlib import Path

DB_DIR = Path.home() / ".personal_accounting"
DB_PATH = DB_DIR / "data.db"


def get_connection() -> sqlite3.Connection:
    """Return the singleton database connection, creating it if needed."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed data if the database is empty."""
    conn = get_connection()
    schema.create_tables(conn)
    seed.seed_data(conn)


def backup_and_rebuild():
    """Backup corrupted db and create a fresh one."""
    if DB_PATH.exists():
        backup = DB_PATH.with_suffix(".db.bak")
        shutil.copy2(DB_PATH, backup)
        DB_PATH.unlink()
    init_db()


# Late imports to avoid circular deps at module level
from database import schema, seed
```

- [ ] **Step 2: Create schema.py — DDL statements**

```python
"""Database schema — all CREATE TABLE statements."""

import sqlite3


CREATE_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'transfer')),
    amount REAL NOT NULL CHECK(amount > 0),
    category_id INTEGER,
    account_id INTEGER NOT NULL,
    to_account_id INTEGER,
    note TEXT DEFAULT '',
    date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,
    FOREIGN KEY (to_account_id) REFERENCES accounts(id) ON DELETE SET NULL
)
"""

CREATE_CATEGORIES = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    icon TEXT NOT NULL DEFAULT '❓',
    sort_order INTEGER NOT NULL DEFAULT 0
)
"""

CREATE_ACCOUNTS = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0.0,
    icon TEXT NOT NULL DEFAULT '💳',
    sort_order INTEGER NOT NULL DEFAULT 0
)
"""

CREATE_BUDGETS = """
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE(category_id, month)
)
"""


def create_tables(conn: sqlite3.Connection):
    """Execute all CREATE TABLE IF NOT EXISTS statements."""
    for ddl in [CREATE_CATEGORIES, CREATE_ACCOUNTS, CREATE_TRANSACTIONS, CREATE_BUDGETS]:
        conn.execute(ddl)
    conn.commit()
```

- [ ] **Step 3: Create seed.py — preset categories and accounts**

```python
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
```

- [ ] **Step 4: Test the database initialization**

```python
# tests/test_database.py
import os
import tempfile
import sqlite3
from pathlib import Path
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
```

Run:

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_database.py -v
```

Expected output: 2 passed

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add database layer with schema and seed data"
```

---

### Task 3: Models — Category CRUD

**Files:**
- Create: `models/category.py`
- Create: `tests/test_models_category.py`

- [ ] **Step 1: Write category model tests**

```python
# tests/test_models_category.py
import sqlite3
import pytest
from database.schema import create_tables
from database.seed import seed_data
from models.category import (
    get_all_categories,
    get_categories_by_type,
    add_category,
    update_category,
    delete_category,
    reset_to_defaults,
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
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


def test_update_category(conn):
    cats = get_categories_by_type(conn, "expense")
    target = cats[0]
    update_category(conn, target["id"], "新名称", "🍜", 5)
    updated = conn.execute(
        "SELECT * FROM categories WHERE id=?", (target["id"],)
    ).fetchone()
    assert updated["name"] == "新名称"
    assert updated["sort_order"] == 5


def test_delete_category(conn):
    cats = get_categories_by_type(conn, "expense")
    target = cats[0]
    delete_category(conn, target["id"])
    remaining = get_all_categories(conn)
    ids = [c["id"] for c in remaining]
    assert target["id"] not in ids


def test_reset_to_defaults(conn):
    add_category(conn, "自定义", "expense", "🧪")
    n_before = len(get_all_categories(conn))
    reset_to_defaults(conn)
    n_after = len(get_all_categories(conn))
    assert n_after < n_before
    assert n_after == 17
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_category.py -v
```

Expected: ImportError — no module `models.category`

- [ ] **Step 3: Write category.py**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_category.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add category model with CRUD operations"
```

---

### Task 4: Models — Account CRUD

**Files:**
- Create: `models/account.py`
- Create: `tests/test_models_account.py`

- [ ] **Step 1: Write account model tests**

```python
# tests/test_models_account.py
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
)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    create_tables(c)
    seed_data(c)
    return c


def test_get_all_accounts(conn):
    accounts = get_all_accounts(conn)
    assert len(accounts) == 4


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
    updated = conn.execute(
        "SELECT * FROM accounts WHERE id=?", (target["id"],)
    ).fetchone()
    assert updated["name"] == "零钱包"


def test_update_balance(conn):
    accounts = get_all_accounts(conn)
    target = accounts[0]
    update_balance(conn, target["id"], 1000.0)
    updated = conn.execute(
        "SELECT * FROM accounts WHERE id=?", (target["id"],)
    ).fetchone()
    assert updated["balance"] == 1000.0


def test_delete_account(conn):
    accounts = get_all_accounts(conn)
    target = accounts[0]
    delete_account(conn, target["id"])
    remaining = get_all_accounts(conn)
    ids = [a["id"] for a in remaining]
    assert target["id"] not in ids


def test_get_account_by_id(conn):
    accounts = get_all_accounts(conn)
    target = accounts[0]
    result = get_account_by_id(conn, target["id"])
    assert result is not None
    assert result["id"] == target["id"]


def test_get_account_usage_count(conn):
    from models.account import get_account_usage_count
    accounts = get_all_accounts(conn)
    count = get_account_usage_count(conn, accounts[0]["id"])
    assert count == 0
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_account.py -v
```

Expected: ImportError

- [ ] **Step 3: Write account.py**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_account.py -v
```

Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add account model with CRUD operations"
```

---

### Task 5: Models — Transaction CRUD

**Files:**
- Create: `models/transaction.py`
- Create: `tests/test_models_transaction.py`

- [ ] **Step 1: Write transaction model tests**

```python
# tests/test_models_transaction.py
import sqlite3
import pytest
from datetime import date
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
    add_transaction(conn, "income", 5000.0, category_id=12, account_id=2, date="2026-05-01")

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
    result = get_transactions(conn, search="5000")
    assert len(result) == 1


def test_pagination(conn):
    for i in range(25):
        add_transaction(conn, "expense", float(i + 1), category_id=1, account_id=1, date=f"2026-05-{(i % 30) + 1:02d}")
    page1 = get_transactions(conn, limit=20, offset=0)
    assert len(page1) == 20
    page2 = get_transactions(conn, limit=20, offset=20)
    assert len(page2) == 5
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_transaction.py -v
```

Expected: ImportError

- [ ] **Step 3: Write transaction.py**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_transaction.py -v
```

Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add transaction model with CRUD and filters"
```

---

### Task 6: Models — Budget CRUD

**Files:**
- Create: `models/budget.py`
- Create: `tests/test_models_budget.py`

- [ ] **Step 1: Write budget model tests**

```python
# tests/test_models_budget.py
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
    # Add expenses against category 1
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
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_budget.py -v
```

Expected: ImportError

- [ ] **Step 3: Write budget.py**

```python
"""Budget model — CRUD and status queries."""

import sqlite3
from typing import Optional


def set_budget(conn: sqlite3.Connection, category_id: int, month: str, amount: float):
    conn.execute(
        """INSERT INTO budgets (category_id, month, amount) VALUES (?, ?, ?)
           ON CONFLICT(category_id, month) DO UPDATE SET amount=excluded.amount""",
        (category_id, month, amount),
    )
    conn.commit()


def get_budget(conn: sqlite3.Connection, category_id: int, month: str) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM budgets WHERE category_id=? AND month=?",
        (category_id, month),
    ).fetchone()


def get_all_budgets_for_month(conn: sqlite3.Connection, month: str) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT b.*, c.name as category_name, c.icon as category_icon
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           WHERE b.month=?
           ORDER BY c.sort_order""",
        (month,),
    ).fetchall()


def delete_budget(conn: sqlite3.Connection, category_id: int, month: str):
    conn.execute(
        "DELETE FROM budgets WHERE category_id=? AND month=?",
        (category_id, month),
    )
    conn.commit()


def get_budget_status(conn: sqlite3.Connection, month: str) -> list[sqlite3.Row]:
    """Return budget with spent, remaining, and percentage for each budgeted category."""
    return conn.execute(
        """SELECT b.*, c.name as category_name, c.icon as category_icon,
                  COALESCE(SUM(CASE WHEN t.type='expense' THEN t.amount ELSE 0 END), 0) as spent
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           LEFT JOIN transactions t ON t.category_id = b.category_id
               AND t.date >= ? || '-01' AND t.date <= ? || '-31'
               AND t.type = 'expense'
           WHERE b.month=?
           GROUP BY b.id
           ORDER BY c.sort_order""",
        (month[:4], month[5:7], month),
    ).fetchall()
```

Note: The `get_budget_status` query has a kludge with date ranges. A better approach:

```python
def get_budget_status(conn: sqlite3.Connection, month: str) -> list[dict]:
    """Return budget with spent, remaining, and percentage for each budgeted category."""
    import calendar
    year_str, month_str = month.split("-")
    year = int(year_str)
    m = int(month_str)
    last_day = calendar.monthrange(year, m)[1]
    start_date = f"{year_str}-{month_str:0>2s}-01"
    end_date = f"{year_str}-{month_str:0>2s}-{last_day:02d}"

    rows = conn.execute(
        """SELECT b.*, c.name as category_name, c.icon as category_icon,
                  COALESCE(SUM(t.amount), 0) as spent
           FROM budgets b
           JOIN categories c ON b.category_id = c.id
           LEFT JOIN transactions t ON t.category_id = b.category_id
               AND t.date >= ? AND t.date <= ?
               AND t.type = 'expense'
           WHERE b.month=?
           GROUP BY b.id
           ORDER BY c.sort_order""",
        (start_date, end_date, month),
    ).fetchall()

    result = []
    for row in rows:
        d = dict(row)
        d["remaining"] = d["amount"] - d["spent"]
        d["percentage"] = round((d["spent"] / d["amount"]) * 100, 1) if d["amount"] > 0 else 0
        result.append(d)
    return result
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_budget.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add budget model with CRUD and status tracking"
```

---

### Task 7: Models — Statistics

**Files:**
- Create: `models/statistics.py`
- Create: `tests/test_models_statistics.py`

- [ ] **Step 1: Write statistics tests**

```python
# tests/test_models_statistics.py
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
    create_tables(c)
    seed_data(c)
    return c


@pytest.fixture
def seed_transactions(conn):
    from models.transaction import add_transaction
    # May 2026 data
    add_transaction(conn, "expense", 1000.0, category_id=1, account_id=1, date="2026-05-01")
    add_transaction(conn, "expense", 500.0, category_id=2, account_id=1, date="2026-05-05")
    add_transaction(conn, "income", 8000.0, category_id=12, account_id=2, date="2026-05-01")
    # April 2026 data
    add_transaction(conn, "expense", 2000.0, category_id=1, account_id=1, date="2026-04-10")
    add_transaction(conn, "income", 8000.0, category_id=12, account_id=2, date="2026-04-01")
    add_transaction(conn, "income", 2000.0, category_id=13, account_id=2, date="2026-04-15")


def test_get_monthly_summary(conn, seed_transactions):
    summary = get_monthly_summary(conn, "2026", "05")
    assert summary["income"] == 8000.0
    assert summary["expense"] == 1500.0
    assert summary["balance"] == 6500.0


def test_get_yearly_summary(conn, seed_transactions):
    summary = get_yearly_summary(conn, "2026")
    assert len(summary) == 2
    may = [s for s in summary if s["month"] == "05"][0]
    apr = [s for s in summary if s["month"] == "04"][0]
    assert may["income"] == 8000.0
    assert may["expense"] == 1500.0
    assert apr["income"] == 10000.0
    assert apr["expense"] == 2000.0


def test_get_category_summary(conn, seed_transactions):
    summary = get_category_summary(conn, "expense", "2026-05")
    assert len(summary) == 2
    total = sum(s["total"] for s in summary)
    assert total == 1500.0
```

- [ ] **Step 2: Run to confirm failure**

Expected: ImportError

- [ ] **Step 3: Write statistics.py**

```python
"""Statistics model — aggregation queries for reports."""

import sqlite3


def get_monthly_summary(conn: sqlite3.Connection, year: str, month: str) -> dict:
    """Return income, expense, balance for a single month."""
    m = int(month)
    start = f"{year}-{m:02d}-01"
    import calendar
    last_day = calendar.monthrange(int(year), m)[1]
    end = f"{year}-{m:02d}-{last_day:02d}"

    row = conn.execute(
        """SELECT
               COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
               COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions
           WHERE date >= ? AND date <= ?""",
        (start, end),
    ).fetchone()

    return {
        "income": row["income"],
        "expense": row["expense"],
        "balance": row["income"] - row["expense"],
    }


def get_yearly_summary(conn: sqlite3.Connection, year: str) -> list[dict]:
    """Return monthly income/expense/balance for each month in the year."""
    rows = conn.execute(
        """SELECT
               substr(date, 6, 2) as month,
               COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
               COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions
           WHERE date LIKE ?
           GROUP BY substr(date, 6, 2)
           ORDER BY month""",
        (f"{year}-%",),
    ).fetchall()

    return [
        {
            "month": r["month"],
            "income": r["income"],
            "expense": r["expense"],
            "balance": r["income"] - r["expense"],
        }
        for r in rows
    ]


def get_category_summary(conn: sqlite3.Connection, typ: str, month: str) -> list[dict]:
    """Return per-category totals for a given type and month."""
    year_str, month_str = month.split("-")
    import calendar
    last_day = calendar.monthrange(int(year_str), int(month_str))[1]
    start = f"{year_str}-{month_str:0>2s}-01"
    end = f"{year_str}-{month_str:0>2s}-{last_day:02d}"

    rows = conn.execute(
        """SELECT c.id, c.name, c.icon, SUM(t.amount) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.type=? AND t.date >= ? AND t.date <= ?
           GROUP BY c.id
           ORDER BY total DESC""",
        (typ, start, end),
    ).fetchall()

    return [dict(r) for r in rows]
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/test_models_statistics.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add statistics model for monthly/yearly/category aggregation"
```

---

### Task 8: Utils — helpers

**Files:**
- Create: `utils/helpers.py`

- [ ] **Step 1: Write helpers.py**

```python
"""Utility helpers — date, currency formatting."""

import calendar
from datetime import datetime, date
from typing import Optional


def format_currency(amount: float) -> str:
    """Format a number as CNY currency string."""
    if amount >= 0:
        return f"¥{amount:,.2f}"
    return f"-¥{abs(amount):,.2f}"


def today_str() -> str:
    """Return today's date as YYYY-MM-DD."""
    return date.today().isoformat()


def current_month_str() -> str:
    """Return current month as YYYY-MM."""
    return date.today().strftime("%Y-%m")


def get_month_date_range(year: int, month: int) -> tuple[str, str]:
    """Return (start_date, end_date) for a given month."""
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year:04d}-{month:02d}-01"
    end = f"{year:04d}-{month:02d}-{last_day:02d}"
    return start, end


def parse_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD string to date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def format_date_display(date_str: str) -> str:
    """Convert YYYY-MM-DD to user-friendly display format."""
    d = parse_date(date_str)
    if d:
        return d.strftime("%Y年%m月%d日")
    return date_str
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add utility helpers for formatting and dates"
```

---

### Task 9: UI Foundation — main window and sidebar navigation

**Files:**
- Create: `ui/app.py`

- [ ] **Step 1: Write app.py — main window with sidebar**

```python
"""Main application window — sidebar navigation and page container."""

import customtkinter as ctk
from typing import Optional


PAGES = [
    ("📊", "总览", 0),
    ("➕", "记账", 1),
    ("📋", "账单", 2),
    ("📈", "统计", 3),
    ("💰", "预算", 4),
    ("⚙️", "设置", 5),
]


class App(ctk.CTk):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.title("📒 个人记账本")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.resizable(True, True)

        # Initialize database
        from database.connection import init_db
        try:
            init_db()
        except Exception:
            from database.connection import backup_and_rebuild
            backup_and_rebuild()

        self._conn = None
        self._current_page_index = -1
        self._pages: list[Optional[ctk.CTkFrame]] = [None] * len(PAGES)
        self._nav_buttons: list[ctk.CTkButton] = []

        self._build_sidebar()
        self._build_main_area()

        # Show default page (overview)
        self.show_page(0)

    @property
    def conn(self):
        """Lazy database connection."""
        if self._conn is None:
            from database.connection import get_connection
            self._conn = get_connection()
        return self._conn

    def _build_sidebar(self):
        """Build the left-side icon navigation bar."""
        self.sidebar = ctk.CTkFrame(self, width=70, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        for icon, label, idx in PAGES:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}\n{label}",
                width=60,
                height=60,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray40", "gray60"),
                hover_color=("gray85", "gray25"),
                font=ctk.CTkFont(size=11),
                command=lambda i=idx: self.show_page(i),
            )
            btn.pack(pady=4, padx=5)
            self._nav_buttons.append(btn)

    def _build_main_area(self):
        """Build the main content container."""
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

    def show_page(self, index: int):
        """Switch to the page at the given index."""
        if index == self._current_page_index:
            return

        # Update nav button highlight
        for i, btn in enumerate(self._nav_buttons):
            if i == index:
                btn.configure(fg_color=("gray75", "gray30"), text_color=("black", "white"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray40", "gray60"))

        # Hide current page
        if self._current_page_index >= 0 and self._pages[self._current_page_index] is not None:
            self._pages[self._current_page_index].pack_forget()

        # Show (or lazy-load) new page
        if self._pages[index] is None:
            self._pages[index] = self._create_page(index)

        self._pages[index].pack(fill="both", expand=True)
        self._current_page_index = index

        # Refresh page data
        self._pages[index].refresh()

    def _create_page(self, index: int) -> ctk.CTkFrame:
        """Factory method — create a page by index."""
        from ui.pages.overview_page import OverviewPage
        from ui.pages.add_page import AddPage
        from ui.pages.bills_page import BillsPage
        from ui.pages.stats_page import StatsPage
        from ui.pages.budget_page import BudgetPage
        from ui.pages.settings_page import SettingsPage

        creators = [
            lambda: OverviewPage(self.main_container, self),
            lambda: AddPage(self.main_container, self),
            lambda: BillsPage(self.main_container, self),
            lambda: StatsPage(self.main_container, self),
            lambda: BudgetPage(self.main_container, self),
            lambda: SettingsPage(self.main_container, self),
        ]
        return creators[index]()
```

- [ ] **Step 2: Write the BasePage class that all pages extend**

Create `ui/base_page.py`:

```python
"""Base page class — all pages inherit from this."""

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    """Base class for all pages. Subclasses must implement refresh()."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._built = False

    def refresh(self):
        """Called when the page becomes visible. Override to reload data."""
        if not self._built:
            self.build()
            self._built = True

    def build(self):
        """Build the UI once. Called on first show."""
        raise NotImplementedError
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: add main window with sidebar navigation and base page"
```

---

### Task 10: Widget — Summary Cards

**Files:**
- Create: `ui/widgets/summary_cards.py`

- [ ] **Step 1: Write summary_cards.py**

```python
"""Summary cards widget — income, expense, balance display cards."""

import customtkinter as ctk


class SummaryCards(ctk.CTkFrame):
    """Three-column card display for income, expense, and balance."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.income_card = self._make_card(0, "💰 总收入", "¥0.00", "#1a8a3f", "#e8f5e9")
        self.expense_card = self._make_card(1, "💸 总支出", "¥0.00", "#c62828", "#fce4ec")
        self.balance_card = self._make_card(2, "📊 结余", "¥0.00", "#1565c0", "#e3f2fd")

    def _make_card(self, col, title, value, value_color, bg_color):
        card = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=12, height=100)
        card.grid(row=0, column=col, padx=6, pady=8, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13), text_color=("gray30", "gray70")).pack(pady=(14, 2))
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=value_color)
        value_label.pack()

        # Store reference for updates
        card._value_label = value_label
        return card

    def update_data(self, income: float, expense: float, balance: float):
        """Update all three cards with new values."""
        self.income_card._value_label.configure(text=f"¥{income:,.2f}")
        self.expense_card._value_label.configure(text=f"¥{expense:,.2f}")

        balance_color = "#1a8a3f" if balance >= 0 else "#c62828"
        self.balance_card._value_label.configure(text=f"¥{balance:,.2f}", text_color=balance_color)
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add summary cards widget"
```

---

### Task 11: Widget — Transaction Form

**Files:**
- Create: `ui/widgets/transaction_form.py`

- [ ] **Step 1: Write transaction_form.py**

```python
"""Transaction form widget — reusable for both add and edit modes."""

import customtkinter as ctk
from typing import Optional, Callable
from models.category import get_categories_by_type
from models.account import get_all_accounts
from utils.helpers import today_str


class TransactionForm(ctk.CTkFrame):
    """Reusable form for adding/editing transactions."""

    TRANSACTION_TYPES = [
        ("💸 支出", "expense"),
        ("💰 收入", "income"),
        ("🔄 转账", "transfer"),
    ]

    def __init__(self, parent, app, on_save: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.app = app
        self.on_save = on_save
        self._transaction_id: Optional[int] = None
        self._selected_category_id: Optional[int] = None

        self._build_type_selector()
        self._build_form_fields()
        self._build_category_grid()
        self._build_save_button()

    def _build_type_selector(self):
        ctk.CTkLabel(self, text="类型", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 4))
        self.type_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.type_frame.pack(fill="x", pady=(0, 12))

        self._type_btns = {}
        for i, (label, typ) in enumerate(self.TRANSACTION_TYPES):
            btn = ctk.CTkButton(
                self.type_frame,
                text=label,
                width=120,
                height=36,
                fg_color=("gray75", "gray30") if i == 0 else "transparent",
                text_color=("black", "white"),
                hover_color=("gray85", "gray25"),
                border_width=1,
                border_color=("gray60", "gray40"),
                command=lambda t=typ: self._select_type(t),
            )
            btn.grid(row=0, column=i, padx=4)
            self._type_btns[typ] = btn
        self._current_type = "expense"

    def _build_form_fields(self):
        # Amount
        ctk.CTkLabel(self, text="金额", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="0.00", height=36)
        self.amount_entry.pack(fill="x", pady=(2, 8))

        # Date
        ctk.CTkLabel(self, text="日期", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD", height=36)
        self.date_entry.insert(0, today_str())
        self.date_entry.pack(fill="x", pady=(2, 8))

        # Account selector
        ctk.CTkLabel(self, text="账户", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.account_var = ctk.StringVar()
        self.account_menu = ctk.CTkOptionMenu(self, variable=self.account_var, values=[], height=36)
        self.account_menu.pack(fill="x", pady=(2, 8))

        # Target account (for transfer)
        self.to_account_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.to_account_frame, text="目标账户", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.to_account_var = ctk.StringVar()
        self.to_account_menu = ctk.CTkOptionMenu(self.to_account_frame, variable=self.to_account_var, values=[], height=36)
        self.to_account_menu.pack(fill="x", pady=(2, 8))

        # Note
        ctk.CTkLabel(self, text="备注", font=ctk.CTkFont(size=13)).pack(anchor="w")
        self.note_entry = ctk.CTkEntry(self, placeholder_text="可选备注", height=36)
        self.note_entry.pack(fill="x", pady=(2, 8))

        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.error_label.pack(anchor="w", pady=(4, 0))

    def _build_category_grid(self):
        ctk.CTkLabel(self, text="分类", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(8, 4))
        self.category_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.category_frame.pack(fill="x", pady=(0, 8))
        self._category_buttons = {}
        self._populate_categories("expense")

    def _build_save_button(self):
        self.save_btn = ctk.CTkButton(
            self,
            text="💾 保存",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_save_click,
        )
        self.save_btn.pack(pady=(8, 4))

    def _select_type(self, typ: str):
        self._current_type = typ
        for t, btn in self._type_btns.items():
            btn.configure(fg_color=("gray75", "gray30") if t == typ else "transparent")

        self._populate_categories(typ if typ != "transfer" else "expense")

        # Show/hide target account for transfer
        if typ == "transfer":
            self.to_account_frame.pack(fill="x", pady=(0, 8))
        else:
            self.to_account_frame.pack_forget()
            self.error_label.configure(text="")

    def _populate_categories(self, typ: str):
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        self._category_buttons = {}
        self._selected_category_id = None

        cats = get_categories_by_type(self.app.conn, typ)
        for i, cat in enumerate(cats):
            row = i // 4
            col = i % 4
            btn = ctk.CTkButton(
                self.category_frame,
                text=f"{cat['icon']} {cat['name']}",
                width=100,
                height=50,
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                hover_color=("gray80", "gray30"),
                border_width=1,
                border_color=("gray65", "gray45"),
                command=lambda cid=cat["id"]: self._select_category(cid),
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="w")
            self._category_buttons[cat["id"]] = btn

    def _select_category(self, category_id: int):
        self._selected_category_id = category_id
        for cid, btn in self._category_buttons.items():
            btn.configure(fg_color=("gray75", "gray30") if cid == category_id else "transparent")

    def refresh_accounts(self):
        accounts = get_all_accounts(self.app.conn)
        names = [f"{a['icon']} {a['name']}" for a in accounts]
        self.account_menu.configure(values=names)
        if names:
            self.account_var.set(names[0])
        self.to_account_menu.configure(values=names)
        if len(names) > 1:
            self.to_account_var.set(names[1])
        elif names:
            self.to_account_var.set(names[0])

    def _get_account_id_from_var(self, var) -> Optional[int]:
        accounts = get_all_accounts(self.app.conn)
        for a in accounts:
            if f"{a['icon']} {a['name']}" == var.get():
                return a["id"]
        return None

    def _validate(self) -> Optional[str]:
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                return "金额必须大于 0"
        except ValueError:
            return "请输入有效金额"

        if self._current_type != "transfer" and self._selected_category_id is None:
            return "请选择分类"

        if self._get_account_id_from_var(self.account_var) is None:
            return "请选择账户"

        if self._current_type == "transfer":
            src = self._get_account_id_from_var(self.account_var)
            dst = self._get_account_id_from_var(self.to_account_var)
            if src and dst and src == dst:
                return "转账源账户和目标账户不能相同"

        return None

    def _on_save_click(self):
        error = self._validate()
        if error:
            self.error_label.configure(text=f"⚠ {error}")
            return
        self.error_label.configure(text="")

        from models.transaction import add_transaction, update_transaction

        amount = float(self.amount_entry.get())
        account_id = self._get_account_id_from_var(self.account_var)
        to_account_id = self._get_account_id_from_var(self.to_account_var) if self._current_type == "transfer" else None
        category_id = self._selected_category_id if self._current_type != "transfer" else None
        date_val = self.date_entry.get() or today_str()
        note = self.note_entry.get()

        if self._transaction_id:
            update_transaction(
                self.app.conn, self._transaction_id,
                typ=self._current_type, amount=amount,
                category_id=category_id, account_id=account_id,
                to_account_id=to_account_id, note=note, date=date_val,
            )
        else:
            add_transaction(
                self.app.conn, self._current_type, amount,
                category_id=category_id, account_id=account_id,
                to_account_id=to_account_id, note=note, date=date_val,
            )

        # Check budget alert
        if self._current_type == "expense" and category_id:
            from models.budget import get_budget_status
            status_list = get_budget_status(self.app.conn, date_val[:7])
            for s in status_list:
                if s["category_id"] == category_id and s["percentage"] > 100:
                    self._show_budget_alert(s)

        self.clear()
        if self.on_save:
            self.on_save()

    def _show_budget_alert(self, status: dict):
        import tkinter.messagebox as mb
        mb.showwarning(
            "预算超支提醒",
            f"⚠️ 本月 {status['category_icon']} {status['category_name']} "
            f"已支出 ¥{status['spent']:,.2f}\n"
            f"预算为 ¥{status['amount']:,.2f}，超支 ¥{abs(status['remaining']):,.2f}",
        )

    def load_transaction(self, transaction_id: int):
        """Load existing transaction data for editing."""
        from models.transaction import get_transaction_by_id
        t = get_transaction_by_id(self.app.conn, transaction_id)
        if not t:
            return

        self._transaction_id = transaction_id
        self._select_type(t["type"])
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(t["amount"]))
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, t["date"])
        self.note_entry.delete(0, "end")
        self.note_entry.insert(0, t["note"] or "")

        # Select account
        accounts = get_all_accounts(self.app.conn)
        for a in accounts:
            if a["id"] == t["account_id"]:
                self.account_var.set(f"{a['icon']} {a['name']}")
                break

        if t["type"] == "transfer" and t["to_account_id"]:
            for a in accounts:
                if a["id"] == t["to_account_id"]:
                    self.to_account_var.set(f"{a['icon']} {a['name']}")
                    break

        # Select category
        if t["category_id"]:
            self._select_category(t["category_id"])

        self.save_btn.configure(text="💾 更新")

    def clear(self):
        """Reset form to default state."""
        self._transaction_id = None
        self._selected_category_id = None
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, "")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, today_str())
        self.note_entry.delete(0, "end")
        self.note_entry.insert(0, "")
        self._select_type("expense")
        self._select_category(None)
        self.save_btn.configure(text="💾 保存")
        self.error_label.configure(text="")
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add reusable transaction form widget"
```

---

### Task 12: Widget — Transaction List

**Files:**
- Create: `ui/widgets/transaction_list.py`

- [ ] **Step 1: Write transaction_list.py**

```python
"""Transaction list widget — shows grouped transactions with date headers."""

import customtkinter as ctk
from typing import Optional, Callable, List
from models.transaction import get_transactions
from utils.helpers import format_currency


class TransactionList(ctk.CTkScrollableFrame):
    """Scrollable list of transactions grouped by date."""

    def __init__(self, parent, limit: int = 20, on_edit: Optional[Callable] = None, show_header: bool = True, **kwargs):
        super().__init__(parent, **kwargs)
        self.limit = limit
        self.on_edit = on_edit
        self.show_header = show_header
        self._offset = 0
        self._all_loaded = False
        self._item_frames: List[ctk.CTkFrame] = []

    def load(self, conn, typ=None, category_id=None, start_date=None, end_date=None, search=None, reset=True):
        """Query transactions and render them."""
        if reset:
            self._offset = 0
            self._all_loaded = False
            self._clear_items()

        txs = get_transactions(
            conn, typ=typ, category_id=category_id,
            start_date=start_date, end_date=end_date,
            search=search,
            limit=self.limit + 1,
            offset=self._offset,
        )

        if len(txs) <= self.limit:
            self._all_loaded = True
        else:
            txs = txs[:self.limit]

        self._render_transactions(conn, txs)
        self._offset += self.limit

    def _clear_items(self):
        for f in self._item_frames:
            f.destroy()
        self._item_frames = []

    def _render_transactions(self, conn, txs):
        if not txs:
            empty = ctk.CTkLabel(self, text="暂无账单记录", font=ctk.CTkFont(size=13), text_color="gray")
            empty.pack(pady=40)
            self._item_frames.append(empty)
            return

        current_date = None
        for t in txs:
            if t["date"] != current_date:
                current_date = t["date"]
                date_label = ctk.CTkLabel(
                    self, text=f"  {current_date}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w",
                )
                date_label.pack(fill="x", pady=(8, 2), padx=4)
                self._item_frames.append(date_label)

            item = self._render_item(t)
            item.pack(fill="x", padx=4, pady=1)
            self._item_frames.append(item)

        if not self._all_loaded:
            more_btn = ctk.CTkButton(
                self, text="加载更多...", height=32,
                fg_color="transparent", text_color=("gray30", "gray70"),
                hover_color=("gray85", "gray25"),
                command=lambda: self.load(conn, reset=False),
            )
            more_btn.pack(pady=8)
            self._item_frames.append(more_btn)

    def _render_item(self, t) -> ctk.CTkFrame:
        icon = t["category_icon"] if t["category_icon"] else "🔄"
        cat_name = t["category_name"] if t["category_name"] else "转账"
        note = t["note"] if t["note"] else ""

        if t["type"] == "income":
            amount_color = "#1a8a3f"
            sign = "+"
        elif t["type"] == "expense":
            amount_color = "#c62828"
            sign = "-"
        else:
            amount_color = "#1565c0"
            sign = "→"

        amount_text = f"{sign} ¥{t['amount']:,.2f}"
        if t["type"] == "transfer":
            account_text = f"{t['account_name']} → {t['to_account_name'] or '?'}"
        else:
            account_text = t["account_name"] or ""

        frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8, height=44)
        frame.pack_propagate(False)

        if self.on_edit:
            frame.bind("<Button-1>", lambda e, tid=t["id"]: self.on_edit(tid))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=6)

        ctk.CTkLabel(inner, text=f"{icon}  {cat_name}", font=ctk.CTkFont(size=13), width=120, anchor="w").pack(side="left")
        ctk.CTkLabel(inner, text=note, font=ctk.CTkFont(size=12), text_color="gray", width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(inner, text=account_text, font=ctk.CTkFont(size=11), text_color="gray", width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(inner, text=amount_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=amount_color).pack(side="right")

        return frame
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add reusable transaction list widget"
```

---

### Task 13: Widget — Budget Progress

**Files:**
- Create: `ui/widgets/budget_progress.py`

- [ ] **Step 1: Write budget_progress.py**

```python
"""Budget progress widget — displays budget status bars."""

import customtkinter as ctk
from typing import List, Optional
from models.budget import get_budget_status, get_all_budgets_for_month
from utils.helpers import format_currency, current_month_str


class BudgetProgress(ctk.CTkFrame):
    """Display budget progress bars for a given month."""

    def __init__(self, parent, month: Optional[str] = None, show_header: bool = True, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.month = month or current_month_str()
        self.show_header = show_header
        self._rows: List[ctk.CTkFrame] = []

    def refresh(self, conn):
        """Reload and redraw budget status from database."""
        for row in self._rows:
            row.destroy()
        self._rows = []

        if self.show_header:
            header = ctk.CTkLabel(self, text=f"💰 预算概览 ({self.month})", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
            header.pack(fill="x", pady=(0, 8))
            self._rows.append(header)

        budgets = get_all_budgets_for_month(conn, self.month)
        if not budgets:
            empty = ctk.CTkLabel(self, text="暂无预算设置", font=ctk.CTkFont(size=12), text_color="gray")
            empty.pack(pady=20)
            self._rows.append(empty)
            return

        status_list = get_budget_status(conn, self.month)

        for s in status_list:
            row = self._build_row(s)
            row.pack(fill="x", pady=4)
            self._rows.append(row)

    def _build_row(self, status: dict) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8)
        frame.pack_propagate(False)

        over_budget = status["percentage"] > 100
        bar_color = "#c62828" if over_budget else "#1a8a3f"

        # Category label
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            label_frame,
            text=f"{status['category_icon']} {status['category_name']}",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            label_frame,
            text=f"¥{status['spent']:,.0f} / ¥{status['amount']:,.0f}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="right")

        # Progress bar (custom drawn)
        progress_frame = ctk.CTkFrame(frame, height=20, fg_color=("gray85", "gray30"), corner_radius=10)
        progress_frame.pack(fill="x", padx=10, pady=(0, 8))
        progress_frame.pack_propagate(False)

        pct = min(status["percentage"], 100)
        fill_width = max(int(pct), 5)
        fill = ctk.CTkFrame(
            progress_frame,
            width=fill_width,
            height=20,
            fg_color=bar_color,
            corner_radius=10,
        )
        fill.place(x=0, y=0)
        fill.pack_propagate(False)

        pct_label = ctk.CTkLabel(
            progress_frame,
            text=f"{status['percentage']:.0f}%" if not over_budget else f"{status['percentage']:.0f}% ⚠",
            font=ctk.CTkFont(size=11),
            text_color="white",
        )
        pct_label.place(relx=0.5, rely=0.5, anchor="center")

        return frame
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add budget progress widget"
```

---

### Task 14: UI — Overview Page

**Files:**
- Create: `ui/pages/overview_page.py`

- [ ] **Step 1: Write overview_page.py**

```python
"""Overview page — monthly summary, recent transactions, budget overview."""

import customtkinter as ctk
from ui.base_page import BasePage
from ui.widgets.summary_cards import SummaryCards
from ui.widgets.transaction_list import TransactionList
from ui.widgets.budget_progress import BudgetProgress
from models.statistics import get_monthly_summary
from utils.helpers import current_month_str


class OverviewPage(BasePage):

    def build(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(header_frame, text="📊 总览", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        self.month_var = ctk.StringVar(value=current_month_str())
        self.month_menu = ctk.CTkOptionMenu(
            header_frame, variable=self.month_var, values=self._get_recent_months(),
            command=lambda _: self._refresh_data(),
            width=120,
        )
        self.month_menu.pack(side="right")

        # Summary cards
        self.summary_cards = SummaryCards(self)
        self.summary_cards.pack(fill="x", padx=20, pady=8)

        # Two-column layout
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=20, pady=8)
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)

        # Recent transactions
        recent_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        recent_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(recent_frame, text="最近账单", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 4))
        self.recent_list = TransactionList(recent_frame, limit=5, show_header=False)
        self.recent_list.pack(fill="both", expand=True)

        # Budget preview
        budget_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        budget_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.budget_preview = BudgetProgress(budget_frame, show_header=True)
        self.budget_preview.pack(fill="x")

    def _get_recent_months(self):
        import datetime
        months = []
        today = datetime.date.today()
        for i in range(12):
            m = today.month - i
            y = today.year
            while m < 1:
                m += 12
                y -= 1
            months.append(f"{y}-{m:02d}")
        return months

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_data()

    def _refresh_data(self):
        month = self.month_var.get()
        parts = month.split("-")
        if len(parts) != 2:
            return

        summary = get_monthly_summary(self.app.conn, parts[0], parts[1])
        self.summary_cards.update_data(summary["income"], summary["expense"], summary["balance"])

        start = f"{parts[0]}-{parts[1]}-01"
        import calendar
        last_day = calendar.monthrange(int(parts[0]), int(parts[1]))[1]
        end = f"{parts[0]}-{parts[1]}-{last_day:02d}"

        self.recent_list.load(self.app.conn, start_date=start, end_date=end, reset=True)
        self.budget_preview.refresh(self.app.conn)
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add overview page"
```

---

### Task 15: UI — Add Transaction Page

**Files:**
- Create: `ui/pages/add_page.py`

- [ ] **Step 1: Write add_page.py**

```python
"""Add transaction page."""

import customtkinter as ctk
from ui.base_page import BasePage
from ui.widgets.transaction_form import TransactionForm


class AddPage(BasePage):

    def build(self):
        ctk.CTkLabel(self, text="➕ 记账", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=8)

        self.form = TransactionForm(scroll, self.app, on_save=self._on_saved)
        self.form.pack(fill="x", pady=8)

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self.form.refresh_accounts()

    def _on_saved(self):
        """Called after successful save."""
        self.form.clear()
        self.form.refresh_accounts()
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add transaction form page"
```

---

### Task 16: UI — Bills Page (list, filter, edit, delete)

**Files:**
- Create: `ui/pages/bills_page.py`

- [ ] **Step 1: Write bills_page.py**

```python
"""Bills page — full transaction list with filters and edit/delete."""

import customtkinter as ctk
import tkinter.messagebox as mb
from ui.base_page import BasePage
from ui.widgets.transaction_list import TransactionList
from ui.widgets.transaction_form import TransactionForm
from models.category import get_all_categories
from models.transaction import delete_transaction


class BillsPage(BasePage):

    def build(self):
        ctk.CTkLabel(self, text="📋 账单", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))

        # Filter bar
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 8))

        # Type filter
        ctk.CTkLabel(filter_frame, text="类型:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        self.type_var = ctk.StringVar(value="全部")
        type_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self.type_var,
            values=["全部", "支出", "收入", "转账"],
            width=80, command=lambda _: self._apply_filters(),
        )
        type_menu.pack(side="left", padx=4)

        # Category filter
        ctk.CTkLabel(filter_frame, text="分类:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(8, 4))
        self.cat_var = ctk.StringVar(value="全部")
        self.cat_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self.cat_var,
            values=["全部"], width=100, command=lambda _: self._apply_filters(),
        )
        self.cat_menu.pack(side="left", padx=4)

        # Date range
        ctk.CTkLabel(filter_frame, text="从:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(8, 2))
        self.start_date_entry = ctk.CTkEntry(filter_frame, width=90, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=2)
        ctk.CTkLabel(filter_frame, text="到:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(4, 2))
        self.end_date_entry = ctk.CTkEntry(filter_frame, width=90, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=2)

        # Search
        self.search_entry = ctk.CTkEntry(filter_frame, width=120, placeholder_text="🔍 搜索备注...")
        self.search_entry.pack(side="left", padx=8)
        ctk.CTkButton(filter_frame, text="筛选", width=60, command=self._apply_filters).pack(side="left", padx=4)
        ctk.CTkButton(filter_frame, text="重置", width=60, fg_color="transparent", border_width=1,
                      command=self._reset_filters).pack(side="left", padx=4)

        # Transaction list
        self.tx_list = TransactionList(self, limit=20, on_edit=self._edit_transaction)
        self.tx_list.pack(fill="both", expand=True, padx=20, pady=8)

        # Edit dialog reference
        self._edit_dialog = None

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._populate_category_filter()
        self._apply_filters()

    def _populate_category_filter(self):
        cats = get_all_categories(self.app.conn)
        values = ["全部"] + [f"{c['icon']} {c['name']}" for c in cats]
        self.cat_menu.configure(values=values)
        self.cat_var.set("全部")

    def _get_filter_params(self):
        type_map = {"支出": "expense", "收入": "income", "转账": "transfer"}
        typ = type_map.get(self.type_var.get(), None)

        category_id = None
        if self.cat_var.get() != "全部":
            cats = get_all_categories(self.app.conn)
            for c in cats:
                if f"{c['icon']} {c['name']}" == self.cat_var.get():
                    category_id = c["id"]
                    break

        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        search = self.search_entry.get() or None

        return typ, category_id, start_date, end_date, search

    def _apply_filters(self):
        typ, category_id, start_date, end_date, search = self._get_filter_params()
        self.tx_list.load(self.app.conn, typ=typ, category_id=category_id,
                          start_date=start_date, end_date=end_date, search=search, reset=True)

    def _reset_filters(self):
        self.type_var.set("全部")
        self.cat_var.set("全部")
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        self.search_entry.delete(0, "end")
        self._apply_filters()

    def _edit_transaction(self, transaction_id: int):
        if self._edit_dialog is not None:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("编辑账单")
        dialog.geometry("500x650")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        form = TransactionForm(dialog, self.app, on_save=lambda: self._on_edit_saved(dialog))
        form.pack(fill="both", expand=True, padx=16, pady=16)
        form.refresh_accounts()
        form.load_transaction(transaction_id)

        # Delete button
        from models.transaction import get_transaction_by_id
        t = get_transaction_by_id(self.app.conn, transaction_id)
        ctk.CTkButton(
            dialog, text="🗑 删除", fg_color="#c62828", hover_color="#b71c1c",
            command=lambda: self._delete_transaction(transaction_id, dialog),
        ).pack(pady=(0, 12))

        self._edit_dialog = dialog

    def _on_edit_saved(self, dialog):
        dialog.destroy()
        self._edit_dialog = None
        self._apply_filters()

    def _delete_transaction(self, transaction_id: int, dialog):
        if not mb.askyesno("确认删除", "确定要删除这条账单记录吗？"):
            return
        delete_transaction(self.app.conn, transaction_id)
        dialog.destroy()
        self._edit_dialog = None
        self._apply_filters()
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add bills page with filters and edit dialog"
```

---

### Task 17: UI — Statistics Page

**Files:**
- Create: `ui/pages/stats_page.py`

- [ ] **Step 1: Write stats_page.py**

```python
"""Statistics page — yearly summary table and category pie charts."""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.base_page import BasePage
from models.statistics import get_yearly_summary, get_category_summary
from utils.helpers import format_currency
import datetime


class StatsPage(BasePage):

    def build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(header, text="📈 统计", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        self.year_var = ctk.StringVar(value=str(datetime.date.today().year))
        self.year_menu = ctk.CTkOptionMenu(
            header, variable=self.year_var,
            values=[str(y) for y in range(2020, datetime.date.today().year + 1)],
            command=lambda _: self._refresh_data(),
            width=80,
        )
        self.year_menu.pack(side="right")

        # Summary table
        ctk.CTkLabel(self, text="月度汇总", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(4, 4))
        self.table_frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8)
        self.table_frame.pack(fill="x", padx=20, pady=(0, 12))

        # Charts
        chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=8)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)

        # Expense chart
        expense_chart_container = ctk.CTkFrame(chart_frame, fg_color=("white", "gray20"), corner_radius=8)
        expense_chart_container.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(expense_chart_container, text="支出分类占比", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 0))
        self.expense_figure = Figure(figsize=(3, 2.5), dpi=100)
        self.expense_canvas = FigureCanvasTkAgg(self.expense_figure, expense_chart_container)
        self.expense_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Income chart
        income_chart_container = ctk.CTkFrame(chart_frame, fg_color=("white", "gray20"), corner_radius=8)
        income_chart_container.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(income_chart_container, text="收入分类占比", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(8, 0))
        self.income_figure = Figure(figsize=(3, 2.5), dpi=100)
        self.income_canvas = FigureCanvasTkAgg(self.income_figure, income_chart_container)
        self.income_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Month selector for charts
        chart_control = ctk.CTkFrame(self, fg_color="transparent")
        chart_control.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkLabel(chart_control, text="图表月份:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.chart_month_var = ctk.StringVar(value=f"{datetime.date.today().year}-{datetime.date.today().month:02d}")
        self.chart_month_menu = ctk.CTkOptionMenu(
            chart_control, variable=self.chart_month_var,
            values=[], width=80,
            command=lambda _: self._update_charts(),
        )
        self.chart_month_menu.pack(side="left", padx=4)

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_data()

    def _refresh_data(self):
        year = self.year_var.get()
        self._populate_month_menu(year)
        self._update_table(year)
        self._update_charts()

    def _populate_month_menu(self, year: str):
        months = [f"{year}-{m:02d}" for m in range(1, 13)]
        self.chart_month_menu.configure(values=months)
        current = self.chart_month_var.get()
        if current not in months:
            self.chart_month_var.set(months[0])

    def _update_table(self, year: str):
        for w in self.table_frame.winfo_children():
            w.destroy()

        data = get_yearly_summary(self.app.conn, year)
        if not data:
            ctk.CTkLabel(self.table_frame, text="该年度暂无数据", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=20)
            return

        # Header row
        hdr = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 2))
        for i, text in enumerate(["月份", "收入", "支出", "结余"]):
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(size=12, weight="bold"), width=100).grid(row=0, column=i, padx=8)

        for d in data:
            row_f = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=8, pady=1)
            balance_color = "#1a8a3f" if d["balance"] >= 0 else "#c62828"
            ctk.CTkLabel(row_f, text=f"{d['month']}月", width=100, anchor="w").grid(row=0, column=0, padx=8)
            ctk.CTkLabel(row_f, text=format_currency(d["income"]), width=100, anchor="e", text_color="#1a8a3f").grid(row=0, column=1, padx=8)
            ctk.CTkLabel(row_f, text=format_currency(d["expense"]), width=100, anchor="e", text_color="#c62828").grid(row=0, column=2, padx=8)
            ctk.CTkLabel(row_f, text=format_currency(d["balance"]), width=100, anchor="e", text_color=balance_color).grid(row=0, column=3, padx=8)

    def _update_charts(self):
        month = self.chart_month_var.get()

        self._draw_pie_chart(self.expense_figure, "expense", month, "支出分类")
        self.expense_canvas.draw()

        self._draw_pie_chart(self.income_figure, "income", month, "收入分类")
        self.income_canvas.draw()

    def _draw_pie_chart(self, figure: Figure, typ: str, month: str, title: str):
        figure.clear()
        ax = figure.add_subplot(111)

        data = get_category_summary(self.app.conn, typ, month)
        if not data:
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center", fontsize=12)
            ax.set_title(title, fontsize=10)
            return

        labels = [f"{d['icon']} {d['name']}" for d in data]
        sizes = [d["total"] for d in data]

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            startangle=90, textprops={"fontsize": 8},
        )
        ax.set_title(title, fontsize=10)
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add statistics page with table and pie charts"
```

---

### Task 18: UI — Budget Page

**Files:**
- Create: `ui/pages/budget_page.py`

- [ ] **Step 1: Write budget_page.py**

```python
"""Budget page — set and track monthly budgets."""

import customtkinter as ctk
import tkinter.simpledialog as sd
from ui.base_page import BasePage
from ui.widgets.budget_progress import BudgetProgress
from models.category import get_categories_by_type
from models.budget import set_budget, get_all_budgets_for_month
from utils.helpers import current_month_str


class BudgetPage(BasePage):

    def build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(header, text="💰 预算", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        self.month_var = ctk.StringVar(value=current_month_str())
        self.month_menu = ctk.CTkOptionMenu(
            header, variable=self.month_var,
            values=self._get_recent_months(),
            command=lambda _: self._refresh_data(),
            width=120,
        )
        self.month_menu.pack(side="right")

        ctk.CTkButton(header, text="+ 设置预算", width=100, command=self._add_budget_dialog).pack(side="right", padx=8)

        # Budget progress display
        self.budget_progress = BudgetProgress(self, show_header=False)
        self.budget_progress.pack(fill="x", padx=20, pady=8)

        # Category budget table (editable)
        ctk.CTkLabel(self, text="预算明细（点击金额可编辑）", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=20, pady=(12, 4))
        self.table_frame = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=8)
        self.table_frame.pack(fill="x", padx=20, pady=(0, 8))

    def _get_recent_months(self):
        import datetime
        months = []
        today = datetime.date.today()
        for i in range(12):
            m = today.month - i
            y = today.year
            while m < 1:
                m += 12
                y -= 1
            months.append(f"{y}-{m:02d}")
        return months

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_data()

    def _refresh_data(self):
        month = self.month_var.get()
        self.budget_progress.month = month
        self.budget_progress.refresh(self.app.conn)
        self._populate_table(month)

    def _populate_table(self, month: str):
        for w in self.table_frame.winfo_children():
            w.destroy()

        budgets = get_all_budgets_for_month(self.app.conn, month)
        if not budgets:
            ctk.CTkLabel(self.table_frame, text="暂无预算，点击右上角「设置预算」开始", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=20)
            return

        hdr = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 2))
        for i, text in enumerate(["分类", "预算金额"]):
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(size=12, weight="bold"), width=150).grid(row=0, column=i, padx=8)

        for b in budgets:
            row_f = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=8, pady=2)

            ctk.CTkLabel(row_f, text=f"{b['category_icon']} {b['category_name']}", width=150, anchor="w").grid(row=0, column=0, padx=8)

            amount_label = ctk.CTkLabel(
                row_f, text=f"¥{b['amount']:,.2f}", width=150, anchor="w",
                font=ctk.CTkFont(size=13),
                text_color=("blue", "lightblue"),
                cursor="hand2",
            )
            amount_label.grid(row=0, column=1, padx=8)

            # Click to edit
            cid = b["category_id"]
            mid = month
            amount_label.bind(
                "<Button-1>",
                lambda e, cat_id=cid, mon=mid: self._edit_budget_amount(cat_id, mon),
            )

    def _add_budget_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("设置预算")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="选择分类", font=ctk.CTkFont(size=13)).pack(pady=(12, 4))

        cats = get_categories_by_type(self.app.conn, "expense")
        cat_names = [f"{c['icon']} {c['name']}" for c in cats]
        cat_var = ctk.StringVar(value=cat_names[0] if cat_names else "")
        cat_menu = ctk.CTkOptionMenu(dialog, variable=cat_var, values=cat_names, width=200)
        cat_menu.pack(pady=4)

        ctk.CTkLabel(dialog, text="每月预算金额 (¥)", font=ctk.CTkFont(size=13)).pack(pady=(12, 4))
        amount_entry = ctk.CTkEntry(dialog, placeholder_text="0.00", width=200)
        amount_entry.pack(pady=4)

        def save():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                ctk.CTkLabel(dialog, text="请输入有效金额", text_color="red").pack()
                return

            selected_cat = cat_var.get()
            for c in cats:
                if f"{c['icon']} {c['name']}" == selected_cat:
                    set_budget(self.app.conn, c["id"], self.month_var.get(), amount)
                    dialog.destroy()
                    self._refresh_data()
                    return

        ctk.CTkButton(dialog, text="保存", command=save).pack(pady=16)

    def _edit_budget_amount(self, category_id: int, month: str):
        from models.budget import get_budget
        budget = get_budget(self.app.conn, category_id, month)
        if not budget:
            return

        from tkinter.simpledialog import askfloat
        new_amount = askfloat(
            "修改预算",
            f"输入 {budget['category_icon']}{budget['category_name']} 的新预算金额:",
            initialvalue=budget["amount"],
            minvalue=0.01,
        )
        if new_amount is not None:
            set_budget(self.app.conn, category_id, month, new_amount)
            self._refresh_data()
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add budget page with management and editing"
```

---

### Task 19: UI — Settings Page

**Files:**
- Create: `ui/pages/settings_page.py`

- [ ] **Step 1: Write settings_page.py**

```python
"""Settings page — category/account management, CSV export."""

import customtkinter as ctk
import tkinter.messagebox as mb
import csv
import os
from tkinter import filedialog
from ui.base_page import BasePage
from models.category import (
    get_categories_by_type, add_category, update_category,
    delete_category, get_category_usage_count, reset_to_defaults,
)
from models.account import (
    get_all_accounts, add_account, update_account,
    delete_account, update_balance, get_account_usage_count,
)
from models.transaction import get_transactions


class SettingsPage(BasePage):

    def build(self):
        ctk.CTkLabel(self, text="⚙️ 设置", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(16, 8))

        # Notebook-style tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=8)

        self.cat_tab = self.tab_view.add("📂 分类管理")
        self.acc_tab = self.tab_view.add("🏦 账户管理")
        self.export_tab = self.tab_view.add("📤 数据导出")

        self._build_category_tab()
        self._build_account_tab()
        self._build_export_tab()

    def refresh(self):
        if not self._built:
            self.build()
            self._built = True
        self._refresh_category_list()
        self._refresh_account_list()

    # --- Category Tab ---

    def _build_category_tab(self):
        ctk.CTkButton(self.cat_tab, text="+ 新增分类", width=100, command=self._add_category_dialog).pack(anchor="w", pady=(8, 4))
        ctk.CTkButton(self.cat_tab, text="🔄 重置为默认", width=120, fg_color="transparent", border_width=1,
                      command=self._reset_categories).pack(anchor="w", pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(self.cat_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.cat_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.cat_list_frame.pack(fill="x")

    def _refresh_category_list(self):
        for w in self.cat_list_frame.winfo_children():
            w.destroy()

        for typ, title in [("expense", "💸 支出分类"), ("income", "💰 收入分类")]:
            ctk.CTkLabel(self.cat_list_frame, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(8, 4))
            cats = get_categories_by_type(self.app.conn, typ)
            for c in cats:
                self._build_category_row(c)

    def _build_category_row(self, cat):
        row = ctk.CTkFrame(self.cat_list_frame, fg_color=("white", "gray20"), corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)

        ctk.CTkLabel(row, text=f"{cat['icon']} {cat['name']}", font=ctk.CTkFont(size=13), width=150, anchor="w").pack(side="left", padx=10, pady=6)

        def edit():
            dialog = ctk.CTkToplevel(self)
            dialog.title("编辑分类")
            dialog.geometry("300x200")
            dialog.transient(self)
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="名称:").pack(pady=(12, 2))
            name_entry = ctk.CTkEntry(dialog, width=200)
            name_entry.insert(0, cat["name"])
            name_entry.pack(pady=4)

            ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(8, 2))
            icon_entry = ctk.CTkEntry(dialog, width=200)
            icon_entry.insert(0, cat["icon"])
            icon_entry.pack(pady=4)

            def save():
                update_category(self.app.conn, cat["id"], name_entry.get(), icon_entry.get(), cat["sort_order"])
                dialog.destroy()
                self._refresh_category_list()

            ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

        ctk.CTkButton(row, text="✏️", width=30, command=edit).pack(side="right", padx=4)

        def delete():
            usage = get_category_usage_count(self.app.conn, cat["id"])
            if usage > 0:
                mb.showwarning("无法删除", f"该分类下有 {usage} 条账单记录，请先更换分类后再删除。")
                return
            if mb.askyesno("确认删除", f"确定要删除分类「{cat['name']}」吗？"):
                delete_category(self.app.conn, cat["id"])
                self._refresh_category_list()

        ctk.CTkButton(row, text="🗑", width=30, fg_color="transparent", text_color="#c62828", command=delete).pack(side="right", padx=4)

    def _add_category_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("新增分类")
        dialog.geometry("300x220")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="类型:").pack(pady=(12, 2))
        type_var = ctk.StringVar(value="expense")
        type_menu = ctk.CTkOptionMenu(dialog, variable=type_var, values=["expense", "income"], width=200)
        type_menu.pack(pady=4)

        ctk.CTkLabel(dialog, text="名称:").pack(pady=(4, 2))
        name_entry = ctk.CTkEntry(dialog, width=200)
        name_entry.pack(pady=4)

        ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(4, 2))
        icon_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="🍜")
        icon_entry.pack(pady=4)

        def save():
            if name_entry.get():
                add_category(self.app.conn, name_entry.get(), type_var.get(), icon_entry.get() or "❓")
                dialog.destroy()
                self._refresh_category_list()

        ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

    def _reset_categories(self):
        if mb.askyesno("确认重置", "将恢复所有分类为默认设置，确定吗？"):
            reset_to_defaults(self.app.conn)
            self._refresh_category_list()

    # --- Account Tab ---

    def _build_account_tab(self):
        ctk.CTkButton(self.acc_tab, text="+ 新增账户", width=100, command=self._add_account_dialog).pack(anchor="w", pady=(8, 4))

        scroll = ctk.CTkScrollableFrame(self.acc_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        self.acc_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.acc_list_frame.pack(fill="x")

    def _refresh_account_list(self):
        for w in self.acc_list_frame.winfo_children():
            w.destroy()

        accounts = get_all_accounts(self.app.conn)
        for a in accounts:
            self._build_account_row(a)

    def _build_account_row(self, account):
        row = ctk.CTkFrame(self.acc_list_frame, fg_color=("white", "gray20"), corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)

        ctk.CTkLabel(row, text=f"{account['icon']} {account['name']}", font=ctk.CTkFont(size=13), width=120, anchor="w").pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(row, text=f"余额: ¥{account['balance']:,.2f}", font=ctk.CTkFont(size=12), width=120, anchor="e").pack(side="left", padx=10)

        def edit_balance():
            from tkinter.simpledialog import askfloat
            new_bal = askfloat("修改余额", f"输入 {account['name']} 的新余额:", initialvalue=account["balance"])
            if new_bal is not None:
                update_balance(self.app.conn, account["id"], new_bal)
                self._refresh_account_list()

        ctk.CTkButton(row, text="💰调余额", width=70, command=edit_balance).pack(side="right", padx=4)

        def edit():
            dialog = ctk.CTkToplevel(self)
            dialog.title("编辑账户")
            dialog.geometry("300x200")
            dialog.transient(self)
            dialog.grab_set()

            ctk.CTkLabel(dialog, text="名称:").pack(pady=(12, 2))
            name_entry = ctk.CTkEntry(dialog, width=200)
            name_entry.insert(0, account["name"])
            name_entry.pack(pady=4)

            ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(8, 2))
            icon_entry = ctk.CTkEntry(dialog, width=200)
            icon_entry.insert(0, account["icon"])
            icon_entry.pack(pady=4)

            def save():
                update_account(self.app.conn, account["id"], name_entry.get(), icon_entry.get(), account["sort_order"])
                dialog.destroy()
                self._refresh_account_list()

            ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

        ctk.CTkButton(row, text="✏️", width=30, command=edit).pack(side="right", padx=4)

        def delete():
            usage = get_account_usage_count(self.app.conn, account["id"])
            if usage > 0:
                mb.showwarning("无法删除", f"该账户下有 {usage} 条账单记录，请先更换账户后再删除。")
                return
            if mb.askyesno("确认删除", f"确定要删除账户「{account['name']}」吗？"):
                delete_account(self.app.conn, account["id"])
                self._refresh_account_list()

        ctk.CTkButton(row, text="🗑", width=30, fg_color="transparent", text_color="#c62828", command=delete).pack(side="right", padx=4)

    def _add_account_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("新增账户")
        dialog.geometry("300x220")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="名称:").pack(pady=(12, 2))
        name_entry = ctk.CTkEntry(dialog, width=200)
        name_entry.pack(pady=4)

        ctk.CTkLabel(dialog, text="图标 (emoji):").pack(pady=(8, 2))
        icon_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="💳")
        icon_entry.pack(pady=4)

        ctk.CTkLabel(dialog, text="初始余额:").pack(pady=(8, 2))
        balance_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="0.00")
        balance_entry.pack(pady=4)

        def save():
            if name_entry.get():
                try:
                    bal = float(balance_entry.get()) if balance_entry.get() else 0.0
                except ValueError:
                    bal = 0.0
                add_account(self.app.conn, name_entry.get(), bal, icon_entry.get() or "💳")
                dialog.destroy()
                self._refresh_account_list()

        ctk.CTkButton(dialog, text="保存", command=save).pack(pady=12)

    # --- Export Tab ---

    def _build_export_tab(self):
        ctk.CTkLabel(self.export_tab, text="导出账单数据为 CSV 文件", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(12, 8))

        ctk.CTkLabel(self.export_tab, text="时间范围（可选，留空为全部）:").pack(anchor="w")
        range_frame = ctk.CTkFrame(self.export_tab, fg_color="transparent")
        range_frame.pack(anchor="w", pady=4)
        ctk.CTkLabel(range_frame, text="从:").pack(side="left")
        self.export_start = ctk.CTkEntry(range_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.export_start.pack(side="left", padx=4)
        ctk.CTkLabel(range_frame, text="到:").pack(side="left")
        self.export_end = ctk.CTkEntry(range_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.export_end.pack(side="left", padx=4)

        ctk.CTkButton(self.export_tab, text="📤 导出 CSV", command=self._export_csv).pack(pady=16)

    def _export_csv(self):
        start = self.export_start.get() or None
        end = self.export_end.get() or None

        txs = get_transactions(self.app.conn, start_date=start, end_date=end)
        if not txs:
            mb.showinfo("无数据", "所选时间范围内没有账单记录。")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            title="保存 CSV 文件",
        )
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["日期", "类型", "分类", "金额", "账户", "目标账户", "备注"])
            for t in txs:
                type_cn = {"income": "收入", "expense": "支出", "transfer": "转账"}.get(t["type"], t["type"])
                writer.writerow([
                    t["date"], type_cn,
                    f"{t['category_icon'] or ''}{t['category_name'] or '转账'}",
                    t["amount"], t["account_name"],
                    t.get("to_account_name", ""), t["note"],
                ])

        mb.showinfo("导出成功", f"已导出 {len(txs)} 条记录到:\n{file_path}")
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add settings page with category/account management and CSV export"
```

---

### Task 20: Entry point — update main.py

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Overwrite main.py**

```python
"""Personal Accounting — Entry Point.

A lightweight desktop personal accounting tool built with
CustomTkinter, SQLite, and Matplotlib.
"""

from ui.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the app to verify it starts**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python main.py
```

Expected: Application window opens with sidebar navigation and overview page. No errors in terminal.

- [ ] **Step 3: Run all tests to verify nothing is broken**

```bash
cd /Users/Kioz/PyCharmProject/vibecodingstudy/first_project
python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add application entry point"
```

---

## Spec Coverage Check

| 规范需求 | 对应任务 |
|----------|----------|
| 建表 (categories, accounts, transactions, budgets) | Task 2 |
| 预置分类/账户数据 | Task 2 |
| 分类 CRUD + 重置 | Task 3 |
| 账户 CRUD + 余额调整 | Task 4 |
| 账单 CRUD + 筛选 + 分页 | Task 5 |
| 预算 CRUD + 状态查询 | Task 6 |
| 月度/年度/分类统计 | Task 7 |
| 日期/金额格式化工具 | Task 8 |
| 主窗口 + 侧边栏导航 | Task 9 |
| BasePage 基类 | Task 9 |
| 收支摘要卡片组件 | Task 10 |
| 记账表单组件（复用） | Task 11 |
| 账单列表组件 | Task 12 |
| 预算进度组件 | Task 13 |
| 总览页 | Task 14 |
| 记账页 | Task 15 |
| 账单页 + 筛选 + 编辑弹窗 | Task 16 |
| 统计页 + 图表 | Task 17 |
| 预算页 + 超支提醒 | Task 18 |
| 设置页 (分类/账户管理) | Task 19 |
| 数据导出 CSV | Task 19 |
| 应用入口 main.py | Task 20 |
