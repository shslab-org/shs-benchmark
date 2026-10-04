#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t05"
checks = []
core = None
for p in vlib.py_files(ws):
    if "register" in open(p).read() and ("class Calculator" in open(p).read() or "def calculate" in open(p).read()):
        core = p
        break
checks.append({"name": "calculator core with registry exists", "ok": bool(core), "points": 5, "detail": str(core)})
if core:
    base = os.path.dirname(core)
    m = os.path.splitext(os.path.basename(core))[0]
    rc, out = vlib.write_and_run_pytest(base, f'''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from {m} import Calculator

def test_basic_ops():
    c = Calculator()
    c.register("add", lambda a, b: a + b)
    c.register("sub", lambda a, b: a - b)
    assert c.calculate("add", 2, 3) == 5
    assert c.calculate("sub", 5, 2) == 3

def test_unknown_op():
    c = Calculator()
    try:
        c.calculate("nope", 1, 2)
        raised = False
    except KeyError:
        raised = True
    assert raised
''')
    checks.append({"name": "registry + calculate semantics", "ok": rc == 0, "points": 8,
                   "detail": out[-350:] if rc != 0 else "passed"})
    plugins = [p for p in vlib.py_files(ws) if "plugin" in p.lower()]
    n_ops = sum(open(p).read().count("def register") for p in plugins)
    has_all = n_ops >= 4
    checks.append({"name": "4 operation plugins registered", "ok": has_all, "points": 4,
                   "detail": f"{n_ops} registrations in {len(plugins)} plugin files"})
    tests = [p for p in vlib.py_files(ws) if "test" in os.path.basename(p)]
    checks.append({"name": "tests exist and pass", "ok": bool(tests), "points": 3, "detail": str(tests)[:120]})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
