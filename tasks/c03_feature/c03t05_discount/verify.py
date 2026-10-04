#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c03t05"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
import pytest
from inventory import Inventory

def test_set_and_get_discount():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    inv.apply_discount("A", 25)
    assert inv.price_with_discount("A") == 1.5

def test_zero_discount():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    inv.apply_discount("A", 0)
    assert inv.price_with_discount("A") == 2.0

def test_over_100_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    with pytest.raises(ValueError):
        inv.apply_discount("A", 101)

def test_negative_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    with pytest.raises(ValueError):
        inv.apply_discount("A", -5)

def test_unknown_sku_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.apply_discount("GHOST", 10)

def test_no_discount_by_default():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    assert inv.price_with_discount("A") == 2.0
''')
    checks.append({"name": "discount feature + bounds validation + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
