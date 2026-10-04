#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c04t03"
import shutil, tempfile
checks = []
tdir = os.path.dirname(os.path.abspath(__file__))
test_file = os.path.join(ws, "tests_agent", "test_argparsemini.py")
ok = os.path.exists(test_file)
checks.append({"name": "tests_agent/test_argparsemini.py exists", "ok": ok, "points": 4})
if ok:
    code = open(test_file).read()
    checks.append({"name": "no source tampering (argparsemini.py untouched)",
                   "ok": "SEEDED BUGS" in open(os.path.join(ws, "argparsemini.py")).read(), "points": 3})
    buggy = tempfile.mkdtemp(); fixed = tempfile.mkdtemp()
    shutil.copy(test_file, buggy); shutil.copy(test_file, fixed)
    open(os.path.join(buggy, "argparsemini.py"), "w").write(open(os.path.join(tdir, "reference_buggy.py")).read())
    open(os.path.join(fixed, "argparsemini.py"), "w").write(open(os.path.join(tdir, "reference_fixed.py")).read())
    rc_b, out_b = vlib.write_and_run_pytest(buggy, code, test_name="t_buggy.py")
    rc_f, out_f = vlib.write_and_run_pytest(fixed, code, test_name="t_fixed.py")
    checks.append({"name": "tests FAIL on the buggy module", "ok": rc_b != 0, "points": 6, "detail": out_b[-300:]})
    checks.append({"name": "tests PASS on the correct module", "ok": rc_f == 0, "points": 6, "detail": out_f[-300:] if rc_f != 0 else "passed"})
    n_tests = code.count("def test_")
    checks.append({"name": "at least 8 test functions", "ok": n_tests >= 8, "points": 1, "detail": f"found {n_tests}"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
