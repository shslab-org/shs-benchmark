import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# --- In-process round-trip ---
import db

TEST_VALUES = [
    ("str", "hello"),
    ("int", 42),
    ("float", 3.14),
    ("bool_true", True),
    ("bool_false", False),
    ("none", None),
    ("list", [1, 2, "three", {"nested": "yes"}]),
    ("dict", {"a": 1, "b": [2, 3]}),
]

for key, value in TEST_VALUES:
    db.put(key, value)
    got = db.get(key)
    assert got == value, f"round-trip mismatch for {key!r}: {got!r} != {value!r}"
    print(f"  ok: put/get({key!r}) -> {got!r}")

# Missing key returns default
assert db.get("missing-key") is None
assert db.get("missing-key", "fallback") == "fallback"
print("  ok: missing key -> default works")

# Overwrite semantics
db.put("str", "world")
assert db.get("str") == "world"
db.put("str", "hello")  # restore
assert db.get("str") == "hello"
print("  ok: overwrite (upsert) works")

# Non-serializable value raises
try:
    db.put("bad", object())
    raise AssertionError("expected TypeError for non-serializable value")
except TypeError:
    print("  ok: non-serializable value -> TypeError")

# Non-str key raises
try:
    db.put(123, "x")
    raise AssertionError("expected TypeError for non-str key")
except TypeError:
    print("  ok: non-str key -> TypeError")

# --- Cross-process round-trip (real restart persistence) ---
KP = "xproc-key"
KV = {"payload": "across", "n": 7}
db.put(KP, KV)

proc_a_snippet = f"""
import sys
sys.path.insert(0, {str(ROOT)!r})
import db
db.put({KP!r}, {KV!r})
print("A stored", {KP!r})
"""
proc_b_snippet = f"""
import sys
sys.path.insert(0, {str(ROOT)!r})
import db
got = db.get({KP!r})
assert got == {KV!r}, f"cross-process mismatch: {{got!r}}"
print("B resolved", {KP!r}, "->", got)
"""

ra = subprocess.run([sys.executable, "-c", proc_a_snippet], capture_output=True, text=True)
assert ra.returncode == 0, f"proc A failed:\n{ra.stderr}"
rb = subprocess.run([sys.executable, "-c", proc_b_snippet], capture_output=True, text=True)
assert rb.returncode == 0, f"proc B failed:\n{rb.stderr}"
print(ra.stdout.strip())
print(rb.stdout.strip())
print("  ok: cross-process persistence verified")

# Confirm the file is a real SQLite DB
import sqlite3
conn = sqlite3.connect(db.DB_PATH)
schema = conn.execute("SELECT sql FROM sqlite_master WHERE name='kv'").fetchone()
conn.close()
assert schema is not None
print(f"  ok: {db.DB_PATH.name} is a SQLite file with kv table")

print("ALL ROUND-TRIP CHECKS PASSED")
