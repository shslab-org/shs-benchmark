#!/usr/bin/env python3
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t02"
checks = []
cli = vlib.find_file(ws, "tasks_cli.py") or vlib.find_file(ws, "task_cli.py") or vlib.find_file(ws, "mdtask.py")
checks.append({"name": "CLI entry exists", "ok": bool(cli), "points": 4, "detail": str(cli)})
if cli:
    d = tempfile.mkdtemp()
    def run(args):
        return vlib.run_cmd([sys.executable, cli] + args, os.path.dirname(cli), timeout=60,
                            env_extra={"TASKS_DIR": d})
    rc, out = run(["add", "First task", "--priority", "high"])
    ok_add = rc == 0
    checks.append({"name": "add works (with flags)", "ok": ok_add, "points": 3, "detail": out[-150:]})
    rc, out = run(["list"])
    checks.append({"name": "list shows task + priority", "ok": rc == 0 and "First task" in out and "high" in out.lower(),
                   "points": 4, "detail": out[-200:]})
    rc, out = run(["done", "1"])
    rc, out = run(["list", "--all"])
    ok = rc == 0 and ("[x]" in out or "done" in out.lower())
    checks.append({"name": "done + list --all reflect state", "ok": ok, "points": 4, "detail": out[-200:]})
    mds = [f for f in os.listdir(d) if f.endswith(".md")]
    checks.append({"name": "markdown persistence (at least one .md in TASKS_DIR)", "ok": bool(mds),
                   "points": 4, "detail": str(mds)})
    rc, out = run(["add", "Second"])
    rc, out = run(["list"])
    checks.append({"name": "second add listed", "ok": "Second" in out, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
