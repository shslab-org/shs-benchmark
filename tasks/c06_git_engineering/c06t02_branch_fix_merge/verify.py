#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t02"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 3})
rc, out = git("branch", "--list", "fix/divide-by-zero")
checks.append({"name": "branch fix/divide-by-zero exists", "ok": rc == 0 and "fix/divide-by-zero" in out,
               "points": 4, "detail": out.strip()})
rc, out = git("log", "--oneline", "main")
mainlog = [l for l in out.strip().split("\n") if l.strip()] if rc == 0 else []
checks.append({"name": "main has >= 2 commits (initial + fix via merge/ff)",
               "ok": len(mainlog) >= 2, "points": 3, "detail": str(len(mainlog))})
rc, out = git("log", "--oneline", "fix/divide-by-zero")
branchlog = [l for l in out.strip().split("\n") if l.strip()] if rc == 0 else []
checks.append({"name": "fix branch has its own commit", "ok": len(branchlog) >= 2,
               "points": 3, "detail": str(len(branchlog))})
tdir = os.path.dirname(os.path.abspath(__file__))
rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(tdir, "baseline", "test_calc.py")).read(), test_name="test_final.py")
checks.append({"name": "tests PASS on main after merge", "ok": rc == 0, "points": 6,
               "detail": out[-300:] if rc != 0 else "passed"})
rc, out = git("status", "--porcelain")
checks.append({"name": "clean working tree", "ok": rc == 0 and out.strip() == "", "points": 1, "detail": out.strip()[:100]})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
