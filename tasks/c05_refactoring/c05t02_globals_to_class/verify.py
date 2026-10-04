#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c05t02"
import ast as _ast
checks = []
sol = os.path.join(ws, "sessions.py")
ok = os.path.exists(sol)
checks.append({"name": "sessions.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from sessions import SessionStore

def test_create_and_count():
    st = SessionStore()
    st.create("alice"); st.create("bob")
    assert st.active_count() == 2

def test_close():
    st = SessionStore()
    sid = st.create("alice")
    st.close(sid)
    assert st.active_count() == 0

def test_isolated_instances():
    a, b = SessionStore(), SessionStore()
    a.create("x")
    assert a.active_count() == 1 and b.active_count() == 0

def test_ids_unique_per_store():
    st = SessionStore()
    s1 = st.create("a")
    s2 = st.create("b")
    assert s1 != s2
''')
    checks.append({"name": "SessionStore class behavior", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    tree = _ast.parse(src)
    has_global = any(isinstance(n, _ast.Global) for n in _ast.walk(tree))
    checks.append({"name": "no global statements remain", "ok": not has_global, "points": 4})
    checks.append({"name": "SessionStore class defined", "ok": "class SessionStore" in src, "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
