#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c05t04"
import ast as _ast
checks = []
sol = os.path.join(ws, "taskrunner.py")
ok = os.path.exists(sol)
checks.append({"name": "taskrunner.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from taskrunner import run_tasks

class Flaky:
    def __init__(self, fail_times):
        self.calls = 0
        self.fail_times = fail_times
    def hit(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("flaky")

def test_success_after_retries():
    f = Flaky(2)
    res = run_tasks([{"id": "t1", "fn": f.hit}], retries=3, backoff_seconds=0)
    assert res == {"t1": True} and f.calls == 3

def test_fail_exhausts_retries():
    f = Flaky(99)
    res = run_tasks([{"id": "t1", "fn": f.hit}], retries=2, backoff_seconds=0)
    assert res == {"t1": False} and f.calls == 2

def test_stops_retrying_on_success():
    f = Flaky(0)
    run_tasks([{"id": "t1", "fn": f.hit}], retries=5, backoff_seconds=0)
    assert f.calls == 1
''')
    checks.append({"name": "renamed public API works (behavior preserved)", "ok": rc == 0, "points": 10,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    bad = [t for t in ["def go(", "def go (", "(l,", " l,", "=w=", "def go"] if t in src]
    checks.append({"name": "cryptic names gone", "ok": not bad, "points": 4, "detail": str(bad)})
    tree = _ast.parse(src)
    missing_doc = [n.name for n in _ast.walk(tree)
                   if isinstance(n, _ast.FunctionDef) and not _ast.get_docstring(n)]
    checks.append({"name": "docstrings on all functions", "ok": not missing_doc,
                   "points": 3, "detail": f"missing: {missing_doc}"})
    checks.append({"name": "module docstring updated (not the old placeholder)",
                   "ok": _ast.get_docstring(tree) is not None and "Refactor task" not in (_ast.get_docstring(tree) or ""), "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
