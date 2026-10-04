#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c01t04"
checks = []
sol = os.path.join(ws, "csvparse.py")
ok = os.path.exists(sol)
checks.append({"name": "csvparse.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from csvparse import parse_csv

def test_simple():
    assert parse_csv("a,b,c") == [["a", "b", "c"]]

def test_multiple_rows():
    assert parse_csv("a,b\\nc,d") == [["a","b"],["c","d"]]

def test_quoted_comma():
    assert parse_csv('"x,y",z') == [["x,y", "z"]]

def test_escaped_quotes():
    assert parse_csv('"say ""hi""' + '",2') == [['say "hi"', "2"]]

def test_newline_in_quotes():
    assert parse_csv('"line1\\nline2",b') == [["line1\\nline2", "b"]]

def test_empty_fields():
    assert parse_csv("a,,c") == [["a", "", "c"]]

def test_trailing_newline():
    assert parse_csv("a,b\\n") == [["a", "b"]]

def test_mixed():
    text = 'name,note\\n"Doe, John","He said ""ok""\\ntwice"'
    assert parse_csv(text) == [["name","note"],["Doe, John",'He said "ok"\\ntwice']]
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 16,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read() if ok else ""
    checks.append({"name": "does not just import stdlib csv", "ok": "import csv" not in src,
                   "points": 2, "detail": "task requires implementing the parser yourself"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
