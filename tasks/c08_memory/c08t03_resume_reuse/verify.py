#!/usr/bin/env python3
import json, os, sys, ast
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t03"
checks = []
ph = vlib.find_file(ws, "phone.py")
checks.append({"name": "phone.py exists", "ok": bool(ph), "points": 3, "detail": str(ph)})
if ph:
    base = os.path.dirname(ph)
    rc, out = vlib.write_and_run_pytest(base, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from phone import normalize_phone, format_intl

def test_normalize_digits():
    assert normalize_phone("+1 (555) 123-4567") == "15551234567"

def test_normalize_na():
    assert normalize_phone("abc") == ""

def test_format_intl_us():
    assert format_intl("+1 (555) 123-4567") == "+1 555 123 456 7"

def test_format_intl_other():
    assert format_intl("44 20 7123 0000") == "+44 207 123 000 0"
''')
    checks.append({"name": "both functions behave per spec", "ok": rc == 0, "points": 13,
                   "detail": out[-450:] if rc != 0 else "passed"})
    src = open(ph).read()
    tree = ast.parse(src)
    calls = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            calls.add(n.func.id)
    reuse = "format_intl" in calls and "normalize_phone" in calls
    checks.append({"name": "format_intl REUSES normalize_phone (turn-1 function, not reimplemented)",
                   "ok": reuse, "points": 4})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
