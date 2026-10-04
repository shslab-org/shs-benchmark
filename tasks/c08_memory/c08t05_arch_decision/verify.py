#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c08t05"
checks = []
st = None
for name in ("db.py", "store.py", "storage.py", "database.py"):
    c = vlib.find_file(ws, name)
    if c:
        st = c
        break
checks.append({"name": "storage module exists", "ok": bool(st), "points": 4, "detail": str(st)})
if st:
    src = open(st).read().lower()
    checks.append({"name": "uses sqlite (per architecture decision)", "ok": "sqlite3" in src or "sqlite" in src,
                   "points": 6})
    checks.append({"name": "no postgres dependency (decision respected)",
                   "ok": "psycopg" not in src and "postgres" not in src, "points": 4})
    base = os.path.dirname(st)
    rc, out = vlib.write_and_run_pytest(base, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
import importlib
mod = None
for m in ("db", "store", "storage", "database"):
    try:
        mod = importlib.import_module(m); break
    except Exception: pass

def test_roundtrip(tmp_path):
    p = str(tmp_path / "t.db")
    mod.put("k1", {"v": 1})
    mod.put("k2", {"v": 2})
    assert mod.get("k1") == {"v": 1}
    assert mod.get("missing") is None
''')
    checks.append({"name": "put/get works (hidden test)", "ok": rc == 0, "points": 4,
                   "detail": out[-350:] if rc != 0 else "passed"})
out_txt = ""
for f in ("agent_output.txt", "answer.md", "ANSWER.md"):
    p = os.path.join(ws, f)
    if os.path.exists(p):
        out_txt = open(p).read().lower()
        break
answer = (out_txt + " " + (open(os.path.join(ws, "WHY.md")).read().lower() if os.path.exists(os.path.join(ws, "WHY.md")) else ""))
kw = [k in answer for k in ("local", "embedded", "no server", "serverless", "zero config", "file-based", "single file", "server that", "no separate", "lightweight")]
checks.append({"name": "SQLite rationale retained in answer (local/embedded/no-server reasons)",
               "ok": any(kw), "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
