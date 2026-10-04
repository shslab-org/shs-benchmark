#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c01t03"
checks = []
sol = vlib.find_file(ws, "lru_cache.py") or vlib.find_file(ws, "lru.py")
ok = bool(sol)
checks.append({"name": "lru_cache.py found", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath("lru_cache.py")))
from lru_cache import LRUCache

def test_basic_put_get():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1
    assert c.get("b") == 2

def test_eviction():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("c", 3)
    assert c.get("a") == -1
    assert c.get("b") == 2
    assert c.get("c") == 3

def test_recency_update():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    c.get("a")          # a now most recent
    c.put("c", 3)       # evicts b
    assert c.get("b") == -1
    assert c.get("a") == 1

def test_put_updates_existing():
    c = LRUCache(2)
    c.put("a", 1); c.put("a", 9); c.put("b", 2)
    assert c.get("a") == 9

def test_capacity_one():
    c = LRUCache(1)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == -1 and c.get("b") == 2
''')
    checks.append({"name": "hidden pytest suite (behavior)", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    if ok:
        tree = vlib.parse_ast_file(sol)
        src = open(sol).read()
        uses_ord = "OrderedDict" in src
        has_hash = ("__hash__" not in src) and ("dict" in src or "OrderedDict" in src)
        checks.append({"name": "O(1) structure (hash map + doubly linked list or OrderedDict)",
                       "ok": ("class" in src and ("prev" in src or "OrderedDict" in src)), "points": 4})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
