#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t03"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 2})
rc, out = git("tag")
tags = set(out.strip().split("\n")) if rc == 0 and out.strip() else set()
need = {"v0.1.0", "v0.2.0", "v0.3.0"}
checks.append({"name": "3 version tags exist", "ok": need.issubset(tags), "points": 4, "detail": str(sorted(tags))})
rc, out = git("log", "--oneline")
n = len([l for l in out.strip().split("\n") if l.strip()]) if rc == 0 else 0
checks.append({"name": "6 history commits recreated (extra commits allowed)", "ok": n >= 6, "points": 4, "detail": str(n) + " commits"})
cl = os.path.join(ws, "CHANGELOG.md")
ok_cl = os.path.exists(cl)
checks.append({"name": "CHANGELOG.md exists", "ok": ok_cl, "points": 3})
if ok_cl:
    txt = open(cl).read()
    checks.append({"name": "sections for all three versions", "ok": all(v in txt for v in ("0.1.0", "0.2.0", "0.3.0")), "points": 3})
    low = txt.lower()
    checks.append({"name": "content derived from history (mentions ping/metrics/healthcheck)",
                   "ok": ("ping" in low and "metrics" in low and ("health" in low or "readme" in low)),
                   "points": 4})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
