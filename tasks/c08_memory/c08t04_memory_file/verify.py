#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t04"
checks = []
mem = None
for name in ("MEMORY.md", "memory.md", "NOTES.md", "DECISIONS.md"):
    c = vlib.find_file(ws, name)
    if c:
        mem = c
        break
checks.append({"name": "memory/notes file exists", "ok": bool(mem), "points": 5, "detail": str(mem)})
if mem:
    txt = open(mem).read().lower()
    checks.append({"name": "memory records the JSON decision", "ok": "json" in txt and "csv" in txt,
                   "points": 4})
st = vlib.find_file(ws, "storage.py")
checks.append({"name": "storage.py exists", "ok": bool(st), "points": 4, "detail": str(st)})
if st:
    src = open(st).read()
    uses_json = "import json" in src or "json.dump" in src or "json.load" in src
    no_csv = ".csv" not in src and "csv.writer" not in src
    checks.append({"name": "implements JSON storage (per recorded decision)", "ok": uses_json, "points": 4})
    checks.append({"name": "does NOT implement CSV (decision respected)", "ok": no_csv, "points": 3})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
