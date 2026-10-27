import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.abspath(os.environ.get(
    "RXWEB_DB",
    os.path.join(os.path.dirname(__file__), "../../company.db"),
))

DEFAULT_ADMIN_EMAIL = os.environ.get("RXWEB_ADMIN_EMAIL", "").strip()
DEFAULT_ADMIN_PASS = os.environ.get("RXWEB_ADMIN_PASS", "rxweb123")
DEFAULT_USER_EMAIL = os.environ.get("RXWEB_USER_EMAIL", "").strip()
DEFAULT_USER_PASS = os.environ.get("RXWEB_USER_PASS", "user123")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema():
    """补齐后台所需表，不删除已有产品和新闻。"""
    from app.auth import hash_password

    conn = connect()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price TEXT,
            category TEXT,
            image TEXT,
            description TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY,
            title TEXT,
            date TEXT,
            source TEXT,
            summary TEXT,
            content TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            version TEXT,
            size TEXT,
            date TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            reply TEXT,
            replied_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS operation_logs (
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            username TEXT,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            detail TEXT,
            result TEXT NOT NULL DEFAULT 'success',
            ip TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            reset_token TEXT,
            reset_expires TEXT,
            created_at TEXT
        )
        """
    )
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if DEFAULT_ADMIN_EMAIL:
        c.execute(
            "UPDATE users SET email = ? WHERE lower(email) = lower(?)",
            (DEFAULT_ADMIN_EMAIL, "admin@rxweb.local"),
        )
        if not c.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (DEFAULT_ADMIN_EMAIL,)).fetchone():
            c.execute(
                "INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, 'admin', ?)",
                (DEFAULT_ADMIN_EMAIL, hash_password(DEFAULT_ADMIN_PASS), "管理员", now),
            )
    if DEFAULT_USER_EMAIL:
        c.execute(
            "UPDATE users SET email = ? WHERE lower(email) = lower(?)",
            (DEFAULT_USER_EMAIL, "user@rxweb.local"),
        )
        c.execute(
            "UPDATE messages SET email = ? WHERE lower(email) = lower(?)",
            (DEFAULT_USER_EMAIL, "user@rxweb.local"),
        )
        if not c.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (DEFAULT_USER_EMAIL,)).fetchone():
            c.execute(
                "INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, 'user', ?)",
                (DEFAULT_USER_EMAIL, hash_password(DEFAULT_USER_PASS), "演示用户", now),
            )
    conn.commit()
    conn.close()
