#!/usr/bin/env python3
import json, os, sys, re, ast
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t03"
checks = []
api = vlib.find_file(ws, "api.py")
docs = vlib.find_file(ws, "DOCS.md")
checks.append({"name": "api.py exists", "ok": bool(api), "points": 3, "detail": str(api)})
checks.append({"name": "DOCS.md exists", "ok": bool(docs), "points": 3, "detail": str(docs)})
if api and docs:
    tree = ast.parse(open(api).read())
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    need = {"create_task", "list_tasks", "complete_task", "delete_task"}
    checks.append({"name": "4 required functions implemented", "ok": need.issubset(fns), "points": 5})
    doc = open(docs).read()
    names_ok = all(n in doc for n in need)
    checks.append({"name": "docs mention all 4 functions", "ok": names_ok, "points": 3})
    # signature match: docs contain def lines matching code
    mismatch = []
    for n in need & set(fns):
        args = [a.arg for a in fns[n].args.args if a.arg != "self"]
        sig = ", ".join(args)
        if sig and f"({sig})" not in doc.replace("self, ", ""):
            mismatch.append(n + "(" + sig + ")")
    checks.append({"name": "documented signatures match code", "ok": not mismatch,
                   "points": 4, "detail": "mismatched: " + str(mismatch)})
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from api import create_task, list_tasks, complete_task, delete_task

def test_lifecycle():
    t = create_task("write docs")
    tid = t["id"]
    assert any(x["id"] == tid for x in list_tasks())
    assert complete_task(tid)["done"] is True
    delete_task(tid)
    assert all(x["id"] != tid for x in list_tasks())
''')
    checks.append({"name": "task lifecycle works", "ok": rc == 0, "points": 2,
                   "detail": out[-250:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
