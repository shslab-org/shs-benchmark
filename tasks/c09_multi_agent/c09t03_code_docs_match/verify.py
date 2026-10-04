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
    # signature match: for each function, the docs must document the same
    # parameter name sequence as the code (types/defaults/markdown allowed).
    import re as _re
    plain = _re.sub(r"[`*]", "", doc)
    mismatch = []
    for n in need & set(fns):
        args = [a.arg for a in fns[n].args.args if a.arg != "self"]
        m = _re.search(rf"\b{re.escape(n) if False else n.replace('_', '_')}\s*\(([^)]*)\)", plain)
        if not m:
            mismatch.append(n + ": not documented with a signature")
            continue
        toks = [t.strip() for t in m.group(1).split(",") if t.strip() and t.strip() != "..."]
        doc_args = []
        for t in toks:
            ident = _re.match(r"([A-Za-z_][A-Za-z0-9_]*)", t)
            if ident:
                doc_args.append(ident.group(1))
        if doc_args != args:
            mismatch.append(f"{n}: docs={doc_args} code={args}")
    checks.append({"name": "documented parameter sequences match code", "ok": not mismatch,
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
