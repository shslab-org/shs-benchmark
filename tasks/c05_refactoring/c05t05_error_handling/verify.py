#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID="c05t05"
import ast as _ast
checks = []
sol = os.path.join(ws, "loader.py")
ok = os.path.exists(sol)
checks.append({"name": "loader.py exists", "ok": ok, "points": 2})
if ok:
    src = open(sol).read()
    tree = _ast.parse(src)
    checks.append({"name": "no bare except remains", "ok": not vlib.has_bare_except(tree), "points": 6})
    rc, out = vlib.write_and_run_pytest(ws, '''
import json, os, pytest
from loader import load, get, save

def test_load_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load(str(tmp_path / "nope.json"))

def test_load_bad_json_raises(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(ValueError):
        load(str(p))

def test_load_ok(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text('{"a": 1}')
    assert load(str(p)) == {"a": 1}

def test_get_missing_returns_none():
    assert get({"a": {"b": 1}}, "a.x") is None
    assert get({"a": 1}, "a.b.c") is None

def test_get_ok():
    assert get({"a": {"b": 1}}, "a.b") == 1

def test_save_ok(tmp_path):
    p = tmp_path / "out.json"
    assert save(str(p), {"x": 2}) is True
    assert json.loads(p.read_text()) == {"x": 2}
''')
    checks.append({"name": "typed exception behavior (hidden tests)", "ok": rc == 0, "points": 10,
                   "detail": out[-400:] if rc != 0 else "passed"})
    checks.append({"name": "get() catches only KeyError/TypeError",
                   "ok": "(KeyError, TypeError)" in src, "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
