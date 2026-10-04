#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c09t01"
checks = []
mods = {
    "textutils": vlib.find_file(ws, "textutils.py"),
    "validators": vlib.find_file(ws, "validators.py"),
    "formatters": vlib.find_file(ws, "formatters.py"),
    "main": vlib.find_file(ws, "main.py"),
}
checks.append({"name": "all 4 files exist", "ok": all(mods.values()), "points": 6, "detail": str(mods)})
if all(mods.values()):
    base = ws
    rc, out = vlib.write_and_run_pytest(base, '''
import sys, os
sys.path.insert(0, os.path.abspath("."))
from textutils import word_count
from validators import is_email
from formatters import as_table
from main import build_report

def test_units():
    assert word_count("a b c") == 3
    assert is_email("a@b.co") is True
    assert is_email("nope") is False
    assert "|" in as_table([["h1", "h2"], ["a", "b"]])

def test_integration():
    rep = build_report("Contact a@b.co or nope. Two lines here.")
    assert isinstance(rep, str) and "@" in rep
''')
    checks.append({"name": "unit + integration tests pass", "ok": rc == 0, "points": 14,
                   "detail": out[-500:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
