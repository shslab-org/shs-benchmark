#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c03t02"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
import pytest
from inventory import Inventory

def test_remove_stock_success():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 10)
    inv.remove_stock("A", 4)
    assert inv.get_item("A")["qty"] == 6

def test_remove_to_exact_zero():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    inv.remove_stock("A", 5)
    assert inv.get_item("A")["qty"] == 0

def test_remove_more_than_available_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    with pytest.raises(ValueError):
        inv.remove_stock("A", 4)

def test_remove_negative_qty_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    with pytest.raises(ValueError):
        inv.remove_stock("A", -1)

def test_remove_unknown_sku_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.remove_stock("GHOST", 1)

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1")["qty"] == 10
''')
    checks.append({"name": "remove_stock feature + validation + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
