#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c02t02"
checks = []
sol = os.path.join(ws, "cart.py")
ok = os.path.exists(sol)
checks.append({"name": "cart.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_cart.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    import ast as _ast
    tree = _ast.parse(src)
    mutable_defaults = []
    for n in _ast.walk(tree):
        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            for d in n.args.defaults + [d for d in n.args.kw_defaults if d is not None]:
                if isinstance(d, (_ast.List, _ast.Dict, _ast.Set)):
                    mutable_defaults.append(n.name)
    checks.append({"name": "no mutable default arguments remain", "ok": not mutable_defaults,
                   "points": 4, "detail": f"still present in: {mutable_defaults}" if mutable_defaults else "clean"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
