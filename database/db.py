import sqlite3
from datetime import date, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash


# Project root is the parent of the database/ directory.
DB_PATH = Path(__file__).resolve().parent.parent / "spendly.db"


# Fixed list of expense categories defined by the project spec.
CATEGORIES = (
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
)


# Sample seed data: (category, amount, description, days_ago)
# 8 expenses covering all 7 categories, with Food repeated.
SEED_EXPENSES = (
    ("Food", 85.30, "Groceries", 20),
    ("Food", 24.50, "Lunch with team", 18),
    ("Transport", 45.00, "Metro pass", 15),
    ("Bills", 59.99, "Internet", 12),
    ("Health", 18.75, "Pharmacy", 9),
    ("Entertainment", 32.00, "Movie tickets", 6),
    ("Shopping", 67.40, "New shoes", 3),
    ("Other", 12.00, "Misc", 1),
)


def get_db():
    """Open a SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't already exist. Safe to call repeatedly."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert a demo user and 8 sample expenses, but only if no users exist yet."""
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing:
            # Already seeded — don't duplicate.
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        demo_user_id = cursor.lastrowid

        today = date.today()
        for category, amount, description, days_ago in SEED_EXPENSES:
            expense_date = (today - timedelta(days=days_ago)).isoformat()
            conn.execute(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (demo_user_id, amount, category, expense_date, description),
            )

        conn.commit()
    finally:
        conn.close()
