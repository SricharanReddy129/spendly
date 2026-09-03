import calendar
import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    if row["count"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]

    def day(n):
        return date(today.year, today.month, min(n, last_day)).isoformat()

    sample_expenses = [
        (user_id, 45.50, "Food", day(1), "Grocery shopping"),
        (user_id, 12.00, "Transport", day(3), "Bus fare"),
        (user_id, 89.99, "Bills", day(5), "Electricity bill"),
        (user_id, 25.00, "Health", day(8), "Pharmacy - pain relievers"),
        (user_id, 15.99, "Entertainment", day(12), "Movie ticket"),
        (user_id, 60.25, "Shopping", day(15), "New shoes"),
        (user_id, 10.00, "Other", day(20), "Miscellaneous purchase"),
        (user_id, 32.75, "Food", day(25), "Dinner with friends"),
    ]
    conn.executemany(
        """
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_expenses,
    )
    conn.commit()
    conn.close()
