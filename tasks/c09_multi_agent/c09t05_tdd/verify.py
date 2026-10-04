#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t05"
checks = []
impl = None
for name in ("cart.py", "cart/cart.py"):
    p = os.path.join(ws, name)
    if os.path.exists(p):
        impl = p
        break
if not impl:
    for p in vlib.py_files(ws):
        if "class Cart" in open(p).read():
            impl = p
            break
checks.append({"name": "Cart implementation exists", "ok": bool(impl), "points": 5, "detail": str(impl)})
tests = [p for p in vlib.py_files(ws) if "test" in os.path.basename(p)]
checks.append({"name": "test suite exists (written FIRST per TDD)", "ok": bool(tests), "points": 5, "detail": str(tests)[:120]})
if impl and tests:
    n_tests = sum(open(p).read().count("def test_") for p in tests)
    checks.append({"name": ">= 6 test functions", "ok": n_tests >= 6, "points": 2, "detail": str(n_tests)})
    base = ws
    rc, out = vlib.write_and_run_pytest(base, open(tests[0]).read(), test_name="t_agent.py")
    checks.append({"name": "agent's own suite passes against own implementation", "ok": rc == 0,
                   "points": 3, "detail": out[-300:] if rc != 0 else "passed"})
    rc2, out2 = vlib.write_and_run_pytest(base, '''
import sys, os, pytest
sys.path.insert(0, os.path.abspath("."))
from cart import Cart

def test_add_increments():
    c = Cart(); c.add("a"); c.add("a")
    assert c.items() == {"a": 2}

def test_remove_removes_line():
    c = Cart(); c.add("a", 2); c.remove("a")
    assert c.items() == {}

def test_remove_missing_raises():
    c = Cart()
    with pytest.raises(ValueError):
        c.remove("ghost")

def test_total():
    c = Cart(); c.add("a", 2); c.add("b", 1)
    assert c.total({"a": 1.5, "b": 2.0}) == 5.0
''', test_name="t_ref.py")
    checks.append({"name": "implementation satisfies reference tests", "ok": rc2 == 0,
                   "points": 5, "detail": out2[-300:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
