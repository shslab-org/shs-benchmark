#!/usr/bin/env python3
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t01"
checks = []
cli = vlib.find_file(ws, "todo.py")
checks.append({"name": "todo.py exists", "ok": bool(cli), "points": 4, "detail": str(cli)})
if cli:
    d = tempfile.mkdtemp()
    datafile = os.path.join(d, "todos.json")
    def run(args):
        return vlib.run_cmd([sys.executable, cli] + args, os.path.dirname(cli), timeout=60,
                            env_extra={"TODO_FILE": datafile})
    rc, out = run(["add", "Write benchmark report"])
    checks.append({"name": "add command works", "ok": rc == 0, "points": 3, "detail": out[-150:]})
    rc, out = run(["add", "Ship it"])
    rc, out = run(["list"])
    ok = rc == 0 and "Write benchmark report" in out and "Ship it" in out
    checks.append({"name": "list shows added items", "ok": ok, "points": 4, "detail": out[-200:]})
    rc, out = run(["done", "1"])
    rc, out = run(["list"])
    ok = rc == 0 and ("[x]" in out or "done" in out.lower())
    checks.append({"name": "done marks item (visible in list)", "ok": ok, "points": 4, "detail": out[-200:]})
    ok = os.path.exists(datafile)
    if ok:
        try:
            data = json.load(open(datafile))
            ok = isinstance(data, (list, dict)) and len(data) >= 2
        except Exception:
            ok = False
    checks.append({"name": "state persisted to JSON between runs", "ok": ok, "points": 5})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
