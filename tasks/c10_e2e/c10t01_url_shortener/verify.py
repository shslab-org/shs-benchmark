#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t01"
checks = []
mod = None
for p in vlib.py_files(ws):
    if "def shorten" in open(p).read():
        mod = p
        break
checks.append({"name": "shortener module exists", "ok": bool(mod), "points": 4, "detail": str(mod)})
if mod:
    base = os.path.dirname(mod)
    m = os.path.splitext(os.path.basename(mod))[0]
    rc, out = vlib.write_and_run_pytest(base, f'''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from {m} import shorten, resolve

def test_roundtrip():
    code = shorten("https://example.com/x")
    assert resolve(code) == "https://example.com/x"

def test_stable_short():
    a = shorten("https://example.com/x")
    b = shorten("https://example.com/x")
    assert a == b, "same url must map to same code"

def test_custom_alias():
    c = shorten("https://example.com/y", alias="mylink")
    assert c == "mylink" and resolve("mylink") == "https://example.com/y"

def test_alias_collision():
    shorten("https://a.com", alias="taken")
    try:
        shorten("https://b.com", alias="taken")
        raised = False
    except ValueError:
        raised = True
    assert raised

def test_resolve_unknown():
    assert resolve("nope123") is None
''')
    checks.append({"name": "shorten/resolve semantics (5 hidden tests)", "ok": rc == 0, "points": 16,
                   "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
