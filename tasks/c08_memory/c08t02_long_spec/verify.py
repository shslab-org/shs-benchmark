#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t02"
checks = []
mod = None
for name in ("usermgmt.py", "users.py", "user_management.py", "accounts.py"):
    c = vlib.find_file(ws, name)
    if c:
        mod = c
        break
if not mod:
    for p in vlib.py_files(ws):
        if "def create_user" in open(p).read():
            mod = p
            break
checks.append({"name": "user management module found", "ok": bool(mod), "points": 4, "detail": str(mod)})
if mod:
    base = os.path.dirname(mod)
    rc, out = vlib.write_and_run_pytest(base, '''
import sys, os, pytest
sys.path.insert(0, os.path.abspath("."))
import usermgmt as um

def test_email_lowercased():
    u = um.create_user("Bob", "Bob@Example.COM", "abcdefghijklmnop")
    assert u["email"] == "bob@example.com"

def test_username_unique_case_insensitive():
    um.create_user("A", "a@x.com", "abcdefghijklmnop")
    with pytest.raises(ValueError):
        um.create_user("a", "other@x.com", "abcdefghijklmnop")

def test_min_password_12():
    with pytest.raises(ValueError):
        um.create_user("B", "b@x.com", "short")

def test_username_normalized_lower():
    u = um.create_user("MixedCase", "m@x.com", "abcdefghijklmnop")
    assert u["username"] == "mixedcase"

def test_no_pii_in_repr():
    u = um.create_user("C", "c@x.com", "abcdefghijklmnop")
    assert "abcdefghijklmnop" not in repr(u)
''', test_name="t_memory_spec.py", extra_files={"usermgmt.py": open(mod).read()})
    checks.append({"name": "constraints from turn-1 spec enforced (5 hidden checks)", "ok": rc == 0,
                   "points": 16, "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
