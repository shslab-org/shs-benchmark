import json
import sqlite3

DB_PATH = "appdata.db"


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
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )


def get(key: str, default=None):
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM kv WHERE key = ?", (key,)
        ).fetchone()
    if row is None:
        return default
    return json.loads(row[0])


if __name__ == "__main__":
    put("greeting", {"hello": "world", "n": 42, "items": [1, 2, 3]})
    assert get("greeting") == {"hello": "world", "n": 42, "items": [1, 2, 3]}
    put("missing_check", "x")
    assert get("missing_check") == "x"
    assert get("no_such_key", "fallback") == "fallback"
    print("round-trip OK:", get("greeting"))
