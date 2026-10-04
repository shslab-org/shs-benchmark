#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t04"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 2})
cfg = os.path.join(ws, "config.py")
src = open(cfg).read() if os.path.exists(cfg) else ""
markers = ("<<<<<<<", ">>>>>>>", "=======")
checks.append({"name": "no conflict markers left", "ok": not any(m in src for m in markers), "points": 4})
rc2, out2 = vlib.run_cmd([sys.executable, "-c",
    "import sys; sys.path.insert(0,'.'); from config import greeting; print(greeting())"], ws, timeout=30)
final_ok = rc2 == 0 and "Hey there, valued user of DemoApp (v2)!" in out2
checks.append({"name": "combined greeting produced", "ok": final_ok, "points": 6,
               "detail": out2.strip()[-120:]})
rc, out = git("log", "--oneline", "--merges")
has_merge = rc == 0 and out.strip() != ""
checks.append({"name": "merge commit exists on main", "ok": has_merge, "points": 4, "detail": out.strip()[:120]})
tc = os.path.join(ws, "test_config.py")
has_test = os.path.exists(tc) and "test_greeting_combined" in open(tc).read()
checks.append({"name": "combined-greeting test added", "ok": has_test, "points": 2})
rc3, out3 = vlib.run_cmd([sys.executable, "-m", "pytest", "-q", "test_config.py", "-p", "no:cacheprovider"], ws, timeout=60)
checks.append({"name": "test suite passes on final state", "ok": rc3 == 0, "points": 2,
               "detail": out3[-200:] if rc3 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
