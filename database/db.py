import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "budget_data.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            prompt TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monthly_budget REAL NOT NULL DEFAULT 0,
            alert_threshold REAL NOT NULL DEFAULT 0.8,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            tokens_used INTEGER NOT NULL DEFAULT 0,
            tokens_saved INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM budget")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
            INSERT INTO budget (monthly_budget, alert_threshold, updated_at)
            VALUES (?, ?, ?)
        """, (0.0, 0.8, datetime.now().isoformat()))

    conn.commit()
    conn.close()

def log_usage(model, input_tokens, output_tokens, prompt=""):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().isoformat()
    total = input_tokens + output_tokens

    cursor.execute("""
        INSERT INTO usage_log 
        (date, model, input_tokens, output_tokens, total_tokens, prompt, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (today, model, input_tokens, output_tokens, total, prompt[:100], now))

    conn.commit()
    conn.close()

def get_today_usage():
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT 
            COALESCE(SUM(input_tokens), 0) as total_input,
            COALESCE(SUM(output_tokens), 0) as total_output,
            COALESCE(SUM(total_tokens), 0) as total_tokens,
            COUNT(*) as request_count
        FROM usage_log WHERE date = ?
    """, (today,))

    row = cursor.fetchone()
    conn.close()
    return dict(row)

def get_monthly_usage():
    conn = get_connection()
    cursor = conn.cursor()
    month = datetime.now().strftime("%Y-%m")

    cursor.execute("""
        SELECT 
            COALESCE(SUM(input_tokens), 0) as total_input,
            COALESCE(SUM(output_tokens), 0) as total_output,
            COALESCE(SUM(total_tokens), 0) as total_tokens,
            COUNT(*) as request_count
        FROM usage_log WHERE date LIKE ?
    """, (f"{month}%",))

    row = cursor.fetchone()
    conn.close()
    return dict(row)

def get_budget():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budget ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"monthly_budget": 0.0, "alert_threshold": 0.8}

def update_budget(monthly_budget, alert_threshold=0.8):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE budget SET monthly_budget=?, alert_threshold=?, updated_at=?
    """, (monthly_budget, alert_threshold, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_usage_history(days=7):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date,
               SUM(total_tokens) as total_tokens,
               COUNT(*) as requests
        FROM usage_log
        GROUP BY date
        ORDER BY date DESC
        LIMIT ?
    """, (days,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]