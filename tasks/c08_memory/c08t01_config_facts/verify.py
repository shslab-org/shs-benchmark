#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t01"
checks = []
cfg = None
for name in ("config.py", "conf.py", "settings.py"):
    c = vlib.find_file(ws, name)
    if c:
        cfg = c
        break
checks.append({"name": "config file exists", "ok": bool(cfg), "points": 5, "detail": str(cfg)})
if cfg:
    src = open(cfg).read()
    checks.append({"name": "CODENAME == PURPLE-TIGER", "ok": "PURPLE-TIGER" in src, "points": 5})
    checks.append({"name": "PORT == 8734", "ok": "8734" in src, "points": 5})
    checks.append({"name": "HTTP library == requests", "ok": "requests" in src.lower(), "points": 5})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
