#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c05t03"
import ast as _ast
checks = []
sol = os.path.join(ws, "report.py")
ok = os.path.exists(sol)
checks.append({"name": "report.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from report import process_orders

def test_basic():
    r = process_orders(["A,2,3.0", "B,1,5.0"])
    assert r["valid_count"] == 2 and r["invalid_count"] == 0 and r["total"] == 11.0

def test_bulk_discount():
    r = process_orders(["A,10,1.0"])
    assert r["total"] == 9.5

def test_invalid_lines():
    r = process_orders(["bad line", "A,x,1.0", "A,-1,2.0", ",2,3.0", "A,2,3.0"])
    assert r["valid_count"] == 1 and r["invalid_count"] == 4

def test_by_sku_accumulates():
    r = process_orders(["A,1,1.0", "A,1,1.0", "B,1,2.0"])
    assert r["by_sku"] == {"A": 2.0, "B": 2.0}

def test_empty():
    r = process_orders([])
    assert r == {"valid_count": 0, "invalid_count": 0, "total": 0, "by_sku": {}}
''')
    checks.append({"name": "behavior preserved (hidden tests)", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    tree = _ast.parse(src)
    fns = [n.name for n in _ast.walk(tree) if isinstance(n, _ast.FunctionDef)]
    checks.append({"name": "split into >= 4 functions total", "ok": len(fns) >= 4,
                   "points": 4, "detail": f"functions: {fns}"})
    checks.append({"name": "process_orders still public entry", "ok": "def process_orders" in src, "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
