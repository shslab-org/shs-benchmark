#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c05t01"
import ast as _ast
checks = []
sol = os.path.join(ws, "pricing.py")
ok = os.path.exists(sol)
checks.append({"name": "pricing.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from pricing import retail_total, wholesale_total

def test_retail():
    assert retail_total([{"price": 10.0, "qty": 2}]) == 22.0

def test_retail_rounding():
    # 3 * 1.37 = 4.11 -> *1.10 = 4.521 -> 4.52
    assert retail_total([{"price": 1.37, "qty": 3}]) == 4.52

def test_wholesale_no_discount():
    assert wholesale_total([{"price": 10.0, "qty": 10}]) == 110.0

def test_wholesale_discount_applies():
    # 60 * 1.0 = 60 >= 50 -> *0.8=48 -> *1.1=52.8 -> 52.8
    assert wholesale_total([{"price": 1.0, "qty": 60}]) == 52.8

def test_wholesale_below_min():
    assert wholesale_total([{"price": 1.0, "qty": 49}]) == 53.9
''')
    checks.append({"name": "behavior preserved (hidden tests)", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    tree = _ast.parse(src)
    fns = [n.name for n in _ast.walk(tree) if isinstance(n, _ast.FunctionDef)]
    # duplication removed: the half-up rounding expression should appear in ONE place
    dup_count = src.count("* 100")
    checks.append({"name": "rounding logic extracted (appears once)", "ok": dup_count == 1,
                   "points": 4, "detail": f"tax+round block appears {dup_count}x"})
    checks.append({"name": "new helper function defined", "ok": len(fns) >= 3,
                   "points": 2, "detail": f"functions: {fns}"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
