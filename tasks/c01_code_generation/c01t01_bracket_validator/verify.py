#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c01t01"
checks = []
sol = os.path.join(ws, "solution.py")
ok = os.path.exists(sol)
checks.append({"name": "solution.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from solution import is_balanced

def test_simple_pairs():
    assert is_balanced("()") is True
    assert is_balanced("[]") is True
    assert is_balanced("{}") is True

def test_nested_mixed():
    assert is_balanced("([{}])") is True
    assert is_balanced("{[()()]}") is True

def test_unbalanced():
    assert is_balanced("(") is False
    assert is_balanced(")(") is False
    assert is_balanced("([)]") is False

def test_empty_and_nonbrackets():
    assert is_balanced("") is True
    assert is_balanced("abc") is True

def test_long():
    assert is_balanced("(" * 50 + ")" * 50) is True
    assert is_balanced("]" * 3) is False
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "all hidden tests passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
