import sqlite3
from config import DATABASE_URL

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role      TEXT NOT NULL DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            status      TEXT NOT NULL DEFAULT 'pending',
            owner_id    INTEGER NOT NULL REFERENCES users(id),
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            token      TEXT UNIQUE NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            method     TEXT,
            path       TEXT,
            status     INTEGER,
            ip         TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)