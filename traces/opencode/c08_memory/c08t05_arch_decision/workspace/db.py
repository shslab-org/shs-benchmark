import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "appdata.db")


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )
    return conn


def put(key: str, value) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )


def get(key: str, default=None):
    with _conn() as conn:
        row = conn.execute(
            "SELECT value FROM kv WHERE key = ?", (key,)
        ).fetchone()
    if row is None:
        return default
    return json.loads(row[0])


if __name__ == "__main__":
    test_val = {"nested": [1, 2, 3], "x": None}
    put("demo", test_val)
    out = get("demo")
    assert out == test_val, f"round-trip failed: {out!r}"
    missing = get("nope", default="fallback")
    assert missing == "fallback", f"default failed: {missing!r}"
    put("demo", "overwritten")
    assert get("demo") == "overwritten"
    print("round-trip verified")
