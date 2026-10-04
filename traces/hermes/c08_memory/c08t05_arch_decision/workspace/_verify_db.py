import db
db.put("name", "panther")
db.put("count", 42)
db.put("meta", {"a": 1, "b": [True, None]})
db.put("name", "puma")  # overwrite
assert db.get("name") == "puma", db.get("name")
assert db.get("count") == 42
assert db.get("meta") == {"a": 1, "b": [True, None]}
assert db.get("missing", "fallback") == "fallback"
assert db.get("missing") is None
print("round-trip OK:", db.get("name"), db.get("count"), db.get("meta"))
