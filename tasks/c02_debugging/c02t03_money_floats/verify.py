#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c02t03"
checks = []
sol = os.path.join(ws, "money.py")
ok = os.path.exists(sol)
checks.append({"name": "money.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_money.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes (exact cent arithmetic)", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    checks.append({"name": "uses decimal or integer cents (no raw float math)",
                   "ok": ("Decimal" in src or "from decimal" in src or "round(" in src or "// 1" in src or "* 100" in src),
                   "points": 2})
    checks.append({"name": "format_usd still exists with same signature", "ok": "def format_usd" in src, "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
