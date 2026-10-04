#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t04"
checks = []
runner = vlib.find_file(ws, "pipeline.py") or vlib.find_file(ws, "runner.py")
checks.append({"name": "runner exists (pipeline.py)", "ok": bool(runner), "points": 3, "detail": str(runner)})
if runner:
    base = os.path.dirname(runner)
    rc, out = vlib.write_and_run_pytest(base, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from pipeline import Transform, run_pipeline

def test_upper():
    assert Transform("upper", lambda s: s.upper()).apply("abc") == "ABC"

def test_pipeline_order():
    t1 = Transform("strip", lambda s: s.strip())
    t2 = Transform("upper", lambda s: s.upper())
    out = run_pipeline("  hi  ", [t1, t2])
    assert out == "HI"

def test_skip_disabled():
    t = Transform("no", lambda s: s + "X", enabled=False)
    assert run_pipeline("a", [t]) == "a"

def test_error_isolation():
    def boom(s): raise RuntimeError("x")
    t_bad = Transform("bad", boom)
    t_ok = Transform("ok", lambda s: s + "!")
    out, errs = run_pipeline("a", [t_bad, t_ok], collect_errors=True)
    assert out == "a!" and len(errs) == 1
''')
    checks.append({"name": "transform + pipeline semantics (hidden tests)", "ok": rc == 0,
                   "points": 17, "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
