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
