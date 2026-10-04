#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t05"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repo exists", "ok": rc == 0, "points": 2})
rc, out = git("log", "--oneline", "--merges", "main")
merges = out.strip() if rc == 0 else "?"
checks.append({"name": "linear history (no merge commits on main)", "ok": rc == 0 and merges == "",
               "points": 5, "detail": merges[:150]})
rc, out = git("log", "--format=%s", "main")
subjects = out if rc == 0 else ""
need_sub = ["Add one", "Add two", "Add three", "Add feature", "Continue feature"]
have_all = all(s in subjects for s in need_sub)
checks.append({"name": "all 5 commits present on main after ff-merge", "ok": have_all,
               "points": 4, "detail": subjects[:200]})
mt = os.path.join(ws, "main.txt"); ft = os.path.join(ws, "feature.txt")
main_ok = os.path.exists(mt) and all(w in open(mt).read() for w in ("one", "two", "three"))
feat_ok = os.path.exists(ft) and all(w in open(ft).read() for w in ("feature work", "feature-continued"))
checks.append({"name": "main.txt contains one/two/three", "ok": main_ok, "points": 2})
checks.append({"name": "feature.txt contains feature work + continuation", "ok": feat_ok, "points": 2})
rc, out = git("log", "--format=%s", "main")
order_ok = rc == 0 and out.strip().split("\n")[-1].strip() == "Add one"
checks.append({"name": "root commit is 'Add one' (real history)", "ok": order_ok, "points": 2})
rc, out = git("status", "--porcelain")
checks.append({"name": "clean working tree", "ok": rc == 0 and out.strip() == "", "points": 3, "detail": out.strip()[:100]})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
