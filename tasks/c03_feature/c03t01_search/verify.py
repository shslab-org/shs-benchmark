#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c03t01"
checks = []
sol = os.path.join(ws, "inventory.py")
ok = os.path.exists(sol)
checks.append({"name": "inventory.py still exists (behavior preserved)", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
from inventory import Inventory

def test_search_substring_case_insensitive():
    inv = Inventory()
    inv.add_item("A", "Green Apple", 0.5, 3)
    inv.add_item("B", "Banana", 1.0, 2)
    found = inv.search("apple")
    assert [i["name"] for i in found] == ["Green Apple"]

def test_search_no_match_empty():
    assert Inventory().search("zzz") == []

def test_search_partial():
    inv = Inventory()
    inv.add_item("A", "Green Apple", 0.5, 3)
    assert len(inv.search("reen")) == 1

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1")["qty"] == 10
''')
    checks.append({"name": "search() feature + regression tests", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
