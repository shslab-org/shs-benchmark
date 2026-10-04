"""Tiny JSON key-value store backed by SQLite (local-first, no server).

Storage lives in ./appdata.db — a single plain file, no external
services, no server process. Standard library only.
"""

import json
import sqlite3

DB_PATH = "appdata.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS kv ("
        "  key TEXT PRIMARY KEY,"
        "  value TEXT NOT NULL"
        ")"
    )
    return conn


def put(key: str, value) -> None:
    """Store ``value`` (JSON-serializable) under ``key``."""
    if not isinstance(key, str):
        raise TypeError(f"key must be a str, got {type(key).__name__}")
    payload = json.dumps(value)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO kv (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, payload),
        )
        conn.commit()
    finally:
        conn.close()


def get(key: str, default=None):
    """Return the value stored under ``key``, or ``default`` if absent."""
    if not isinstance(key, str):
        raise TypeError(f"key must be a str, got {type(key).__name__}")
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT value FROM kv WHERE key = ?", (key,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return default
    return json.loads(row[0])
