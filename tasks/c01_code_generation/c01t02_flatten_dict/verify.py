#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c01t02"
checks = []
sol = os.path.join(ws, "flatten.py")
ok = os.path.exists(sol)
checks.append({"name": "flatten.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from flatten import flatten

def test_flat_dict():
    assert flatten({"a": 1, "b": 2}) == {"a": 1, "b": 2}

def test_nested():
    assert flatten({"a": {"b": {"c": 1}}}) == {"a.b.c": 1}

def test_custom_sep():
    assert flatten({"a": {"b": 1}}, sep="/") == {"a/b": 1}

def test_lists():
    assert flatten({"a": [1, {"b": 2}]}) == {"a.0": 1, "a.1.b": 2}

def test_empty_containers():
    assert flatten({"a": {}}) == {"a": {}}
    assert flatten({"a": []}) == {"a": []}

def test_scalars():
    assert flatten({"a": None}) == {"a": None}
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "all hidden tests passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
