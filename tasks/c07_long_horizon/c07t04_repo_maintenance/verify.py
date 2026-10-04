#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t04"
checks = []
rc, out = vlib.write_and_run_pytest(ws, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from shop.cart import Cart
from shop.pricing import final_price

def test_cart_add_remove():
    c = Cart()
    c.add("apple", 2)
    c.add("pear", 1)
    c.remove("apple")
    assert c.items() == {"pear": 1}

def test_cart_quantity_update():
    c = Cart()
    c.add("apple", 2)
    c.add("apple", 3)
    assert c.items() == {"apple": 5}

def test_pricing_bulk():
    assert final_price(10, 1.0, bulk_threshold=10, bulk_discount=0.9) == 9.0

def test_pricing_normal():
    assert final_price(5, 2.0, bulk_threshold=10, bulk_discount=0.9) == 10.0
''', test_name="t_final.py")
checks.append({"name": "all 4 hidden tests pass (2 bug fixes)", "ok": rc == 0, "points": 8,
               "detail": out[-500:] if rc != 0 else "passed"})
bk = vlib.find_file(ws, "backup.py")
ok_bk = bool(bk) and "def backup_json" in open(bk).read()
checks.append({"name": "backup feature exists (shop/backup.py with backup_json)", "ok": ok_bk, "points": 4})
bt = os.path.join(ws, "tests", "test_backup.py")
checks.append({"name": "tests for backup added", "ok": os.path.exists(bt) and "def test" in open(bt).read(), "points": 2})
rdme = open(os.path.join(ws, "README.md")).read().lower() if os.path.exists(os.path.join(ws, "README.md")) else ""
checks.append({"name": "README updated (cart + pricing/backup mentioned)",
               "ok": "cart" in rdme and ("pricing" in rdme or "backup" in rdme), "points": 2})
rc, out = vlib.run_cmd(["git", "-C", ws, "log", "--oneline"], ws, timeout=20)
n_commits = len([l for l in out.strip().split("\n") if l.strip()]) if rc == 0 and out.strip() else 0
checks.append({"name": "work committed with git (>= 2 commits)", "ok": n_commits >= 2,
               "points": 4, "detail": str(n_commits) + " commits"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
