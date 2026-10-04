#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t02"
checks = []
contract = vlib.find_file(ws, "contract.py")
auth = vlib.find_file(ws, "auth.py") or os.path.join(ws, "auth", "__init__.py")
users = vlib.find_file(ws, "users.py") or os.path.join(ws, "users", "__init__.py")
checks.append({"name": "contract.py exists", "ok": bool(contract), "points": 3, "detail": str(contract)})
checks.append({"name": "auth + users components exist", "ok": bool(auth) and bool(users),
               "points": 3, "detail": f"auth={auth} users={users}"})
if contract and auth and users:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from contract import Token, now_ts
from auth import issue_token, verify_token
from users import register, authenticate

def test_register_and_auth():
    register("alice", "wonderland9")
    assert authenticate("alice", "wonderland9") is True
    assert authenticate("alice", "wrong") is False

def test_token_flow():
    register("bob", "builder123")
    t = issue_token("bob")
    assert verify_token(t) == "bob"

def test_forged_token_rejected():
    assert verify_token("not-a-real-token") is None
''', test_name="t_services.py")
    checks.append({"name": "cross-service integration (auth<->users via contract)", "ok": rc == 0,
                   "points": 14, "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
