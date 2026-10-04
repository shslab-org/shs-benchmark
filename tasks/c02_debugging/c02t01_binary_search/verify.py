#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c02t01"
checks = []
sol = os.path.join(ws, "search.py")
ok = os.path.exists(sol)
checks.append({"name": "search.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_search.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    rc2, out2 = vlib.write_and_run_pytest(ws, '''
from search import binary_search

def test_even_length_first():
    assert binary_search([1, 3, 5, 7], 1) == 0

def test_even_length_last():
    assert binary_search([1, 3, 5, 7], 7) == 3

def test_even_length_absent_between():
    assert binary_search([1, 3, 5, 7], 4) == -1

def test_duplicates_find_a_valid_index():
    arr = [1, 2, 2, 2, 3]
    i = binary_search(arr, 2)
    assert arr[i] == 2

def test_empty():
    assert binary_search([], 1) == -1
''')
    checks.append({"name": "extra edge cases (even length, empty, duplicates)", "ok": rc2 == 0, "points": 6,
                   "detail": out2[-400:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
