import sqlite3

DB_NAME = "crash_results.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            value REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_result(user_id, value, created_at):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO results (user_id, value, created_at) VALUES (?, ?, ?)",
        (user_id, value, created_at)
    )

    conn.commit()
    conn.close()


def get_results(limit=200):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT value, created_at FROM results "
        "ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cur.fetchall()
    conn.close()
    return rows
