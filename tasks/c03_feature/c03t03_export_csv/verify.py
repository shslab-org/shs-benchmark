#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c03t03"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys, csv, io
sys.path.insert(0, ".")
from inventory import Inventory

def test_export_header_and_rows():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 3)
    text = inv.export_csv()
    rows = list(csv.reader(io.StringIO(text)))
    assert rows[0] == ["sku", "name", "price", "qty"]
    data = rows[1:]
    assert {"A", "Apple", "0.5", "3"} in [set(r) for r in data] or ["A", "Apple", "0.5", "3"] in data
    assert ["B", "Banana", "1.0", "2"] in data or {"B", "Banana", "1.0", "2"} in [set(r) for r in data]

def test_export_roundtrip_basic():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    text = inv.export_csv()
    assert "Apple" in text and "sku" in text

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1")["qty"] == 10
''')
    checks.append({"name": "export_csv feature + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
