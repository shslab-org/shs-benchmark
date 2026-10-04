#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c02t04"
checks = []
sol = os.path.join(ws, "validators.py")
ok = os.path.exists(sol)
checks.append({"name": "validators.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_validators.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    checks.append({"name": "still regex-based validation (kept approach)", "ok": "re.compile" in src or "re.match" in src or "re.fullmatch" in src, "points": 2})
    # extra hidden sanity cases
    rc2, out2 = vlib.write_and_run_pytest(ws, '''
from validators import is_valid_email

def test_uppercase_local():
    assert is_valid_email("USER@x.com") is True

def test_hyphen_domain():
    assert is_valid_email("a@my-host.org") is True

def test_numeric_tld_rejected():
    assert is_valid_email("a@b.123") is False

def test_space_rejected():
    assert is_valid_email("a b@x.com") is False
''')
    checks.append({"name": "hidden edge cases", "ok": rc2 == 0, "points": 2,
                   "detail": out2[-300:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
