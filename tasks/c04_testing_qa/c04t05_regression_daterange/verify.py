#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c04t05"
import shutil, tempfile
checks = []
tdir = os.path.dirname(os.path.abspath(__file__))
test_file = os.path.join(ws, "tests_agent", "test_daterange_regression.py")
ok = os.path.exists(test_file)
checks.append({"name": "tests_agent/test_daterange_regression.py exists", "ok": ok, "points": 3})
if ok:
    code = open(test_file).read()
    checks.append({"name": "no source tampering (daterange.py untouched)",
                   "ok": "KNOWINGLY SHIPPED" in open(os.path.join(ws, "daterange.py")).read(), "points": 2})
    buggy = tempfile.mkdtemp(); fixed = tempfile.mkdtemp()
    shutil.copy(test_file, buggy); shutil.copy(test_file, fixed)
    open(os.path.join(buggy, "daterange.py"), "w").write(open(os.path.join(tdir, "reference_buggy.py")).read())
    open(os.path.join(fixed, "daterange.py"), "w").write(open(os.path.join(tdir, "reference_fixed.py")).read())
    rc_b, out_b = vlib.write_and_run_pytest(buggy, code, test_name="t_buggy.py")
    rc_f, out_f = vlib.write_and_run_pytest(fixed, code, test_name="t_fixed.py")
    checks.append({"name": "regression test FAILS on shipped buggy code (reproduces issue)",
                   "ok": rc_b != 0, "points": 8, "detail": out_b[-300:]})
    checks.append({"name": "regression test PASSES after correct fix (targeted, not over-broad)",
                   "ok": rc_f == 0, "points": 7, "detail": out_f[-300:] if rc_f != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
