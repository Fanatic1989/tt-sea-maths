import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "sea_app.sqlite"),
)


def init_db() -> None:
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS attempts ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "session_id TEXT, "
            "paper_id TEXT, "
            "question_id TEXT, "
            "entered_answer TEXT, "
            "is_correct INTEGER, "
            "attempt_count INTEGER, "
            "hint_level_used INTEGER, "
            "used_example INTEGER, "
            "used_tutor INTEGER, "
            "used_show_step INTEGER, "
            "used_reveal_solution INTEGER, "
            "time_spent_sec INTEGER, "
            "created_at TEXT DEFAULT (datetime('now'))"
            ");"
        )


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
