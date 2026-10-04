#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c06t01"
def git(*a):
    return vlib.run_cmd(["git"] + list(a), ws, timeout=30)
checks = []
rc, out = git("rev-parse", "--is-inside-work-tree")
checks.append({"name": "git repository initialized", "ok": rc == 0 and out.strip() == "true", "points": 4})
rc, out = git("log", "--oneline")
commits = [l for l in out.strip().split("\n") if l.strip()] if rc == 0 else []
checks.append({"name": "at least 3 commits", "ok": len(commits) >= 3, "points": 5, "detail": str(len(commits)) + " commits"})
rc, out = git("ls-files")
tracked = out.strip().split("\n") if rc == 0 else []
checks.append({"name": "app code tracked", "ok": "app.py" in tracked and "utils.py" in tracked,
               "points": 3, "detail": str(tracked[:6])})
checks.append({"name": "scratch notes NOT tracked", "ok": "notes.txt" not in tracked, "points": 3})
gi = os.path.join(ws, ".gitignore")
checks.append({"name": ".gitignore exists and covers notes", "ok": os.path.exists(gi) and "notes" in open(gi).read(),
               "points": 3})
rc, out = git("log", "--format=%s")
subjects = out.strip().split("\n") if rc == 0 else []
descriptive = sum(1 for s in subjects if len(s.strip()) > 8)
checks.append({"name": "commit messages are descriptive", "ok": rc == 0 and descriptive >= 3,
               "points": 2, "detail": str(subjects[:5])})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
