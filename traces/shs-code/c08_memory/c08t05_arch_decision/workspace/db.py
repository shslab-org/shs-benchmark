"""Tiny JSON-serializing key/value store backed by SQLite (stdlib sqlite3).

The database file lives next to this module at ./appdata.db so the store
works regardless of the current working directory.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "appdata.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kv (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    return conn


def put(key: str, value) -> None:
    """Persist *key* -> *value* (value must be JSON-serializable)."""
    if not isinstance(key, str):
        raise TypeError(f"key must be str, got {type(key).__name__}")
    encoded = json.dumps(value)  # raises TypeError for non-serializable values
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO kv (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, encoded),
        )
        conn.commit()
    finally:
        conn.close()


def get(key: str, default=None):
    """Return the stored value for *key*, or *default* if missing."""
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
