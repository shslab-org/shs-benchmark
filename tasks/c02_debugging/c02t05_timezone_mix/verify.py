#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c02t05"
checks = []
sol = os.path.join(ws, "schedule.py")
ok = os.path.exists(sol)
checks.append({"name": "schedule.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_schedule.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    checks.append({"name": "same three public functions kept",
                   "ok": all(f"def {f}" in src for f in ("parse_stamp", "minutes_between", "add_minutes")), "points": 3})
    checks.append({"name": "no silent tzinfo stripping remains", "ok": "tzinfo=None" not in src, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
