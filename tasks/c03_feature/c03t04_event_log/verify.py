#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c03t04"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
from inventory import Inventory

def test_events_recorded_on_add():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    events = inv.get_events()
    assert len(events) == 1 and "add" in str(events[0]).lower() and "A" in str(events[0])

def test_events_recorded_on_remove():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    inv.remove_stock("A", 2)
    events = inv.get_events()
    assert len(events) == 2 and "remove" in str(events[-1]).lower()

def test_events_have_timestamps():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    assert any(ch.isdigit() for ch in str(inv.get_events()[0])), "event must include a timestamp"

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.remove_stock("SKU1", 1)
    assert inv.get_item("SKU1")["qty"] == 9
''')
    checks.append({"name": "event log feature (add+remove, timestamps) + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
