#!/usr/bin/env python3
"""Generate benchmark tasks: C05 Refactoring, C06 Git, C07 Long-Horizon."""
import json, os, shutil, subprocess
from gen_tasks_c1_c2 import mk, V, T

# ============================ C05 REFACTORING ============================

c05t01_baseline = {
    "pricing.py": '''"""Pricing helpers — duplication to be removed (refactor task)."""


def retail_total(items):
    """items: list of dicts with 'price' and 'qty'. Adds 10% sales tax, rounds to 2 decimals."""
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    with_tax = subtotal * 1.10
    # round half-up to cents
    scaled = with_tax * 100
    rounded = (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100
    return rounded


def wholesale_total(items, min_qty=50):
    """Same math but 20% discount applied first, then 10% tax. Rounds half-up to cents."""
    subtotal = 0
    for it in items:
        subtotal += it["price"] * it["qty"]
    discounted = subtotal * 0.80 if sum(i["qty"] for i in items) >= min_qty else subtotal
    with_tax = discounted * 1.10
    scaled = with_tax * 100
    rounded = (scaled + 0.5) // 1 / 100 if scaled >= 0 else -((-scaled + 0.5) // 1) / 100
    return rounded
''',
    "HINT.md": """Refactor task: the rounding + tax block is duplicated in
retail_total and wholesale_total. Extract the shared logic into a single
helper (e.g. _round_cents(x) and/or _apply_tax(x)) and have both public
functions use it. Public API (retail_total, wholesale_total) and behavior
must remain IDENTICAL.""",
}

c05t01_verify = V + r"""TID="c05t01"
import ast as _ast
checks = []
sol = os.path.join(ws, "pricing.py")
ok = os.path.exists(sol)
checks.append({"name": "pricing.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from pricing import retail_total, wholesale_total

def test_retail():
    assert retail_total([{"price": 10.0, "qty": 2}]) == 22.0

def test_retail_rounding():
    # 3 * 1.37 = 4.11 -> *1.10 = 4.521 -> 4.52
    assert retail_total([{"price": 1.37, "qty": 3}]) == 4.52

def test_wholesale_no_discount():
    assert wholesale_total([{"price": 10.0, "qty": 10}]) == 110.0

def test_wholesale_discount_applies():
    # 60 * 1.0 = 60 >= 50 -> *0.8=48 -> *1.1=52.8 -> 52.8
    assert wholesale_total([{"price": 1.0, "qty": 60}]) == 52.8

def test_wholesale_below_min():
    assert wholesale_total([{"price": 1.0, "qty": 49}]) == 53.9
''')
    checks.append({"name": "behavior preserved (hidden tests)", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    tree = _ast.parse(src)
    fns = [n.name for n in _ast.walk(tree) if isinstance(n, _ast.FunctionDef)]
    # duplication removed: the half-up rounding expression should appear in ONE place
    dup_count = src.count("* 100")
    checks.append({"name": "rounding logic extracted (appears once)", "ok": dup_count == 1,
                   "points": 4, "detail": f"tax+round block appears {dup_count}x"})
    checks.append({"name": "new helper function defined", "ok": len(fns) >= 3,
                   "points": 2, "detail": f"functions: {fns}"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c05t02_baseline = {
    "sessions.py": '''"""Session tracking with module-level global state (refactor to a class)."""

_sessions = {}
_next_id = 1


def create(user):
    global _next_id
    sid = _next_id
    _next_id += 1
    _sessions[sid] = {"user": user, "active": True}
    return sid


def close(sid):
    if sid in _sessions:
        _sessions[sid]["active"] = False


def active_count():
    return sum(1 for s in _sessions.values() if s["active"])


def reset_all():
    global _sessions, _next_id
    _sessions = {}
    _next_id = 1
''',
    "HINT.md": """Refactor task: convert the module-level global state into a class
`SessionStore` with the same operations (create, close, active_count, plus
constructor starts empty). Keep thin module-level wrapper functions delegating
to a private store instance ONLY IF needed for backward compatibility — or
migrate fully to the class; either way the CLASS must exist and hold the
state, and module functions must not use `global` statements anymore.""",
}

c05t02_verify = V + r"""TID="c05t02"
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
"""

c05t03_baseline = {
    "report.py": '''"""God function to split (refactor task)."""


def process_orders(raw_lines):
    """Parses order lines 'sku,qty,unit_price', drops invalid lines,
    computes totals with 5% bulk discount when qty >= 10 per line,
    returns dict with keys: valid_count, invalid_count, total, by_sku."""
    valid = []
    invalid = 0
    for ln in raw_lines:
        parts = ln.strip().split(",")
        if len(parts) != 3:
            invalid += 1
            continue
        sku, qty, price = parts[0].strip(), parts[1].strip(), parts[2].strip()
        try:
            q = int(qty)
            p = float(price)
        except ValueError:
            invalid += 1
            continue
        if q <= 0 or p < 0 or not sku:
            invalid += 1
            continue
        valid.append((sku, q, p))
    total = 0.0
    by_sku = {}
    for sku, q, p in valid:
        line_total = q * p
        if q >= 10:
            line_total *= 0.95
        total += line_total
        by_sku[sku] = by_sku.get(sku, 0) + line_total
    return {"valid_count": len(valid), "invalid_count": invalid,
            "total": round(total, 2),
            "by_sku": {k: round(v, 2) for k, v in by_sku.items()}}
''',
    "HINT.md": """Refactor task: split process_orders into at least 3 focused
helper functions (e.g. parse_line / parse_all, compute_line_total, aggregate).
Public behavior must remain EXACTLY identical (same dict, same rounding).
process_orders must remain the public entry point.""",
}

c05t03_verify = V + r"""TID="c05t03"
import ast as _ast
checks = []
sol = os.path.join(ws, "report.py")
ok = os.path.exists(sol)
checks.append({"name": "report.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from report import process_orders

def test_basic():
    r = process_orders(["A,2,3.0", "B,1,5.0"])
    assert r["valid_count"] == 2 and r["invalid_count"] == 0 and r["total"] == 11.0

def test_bulk_discount():
    r = process_orders(["A,10,1.0"])
    assert r["total"] == 9.5

def test_invalid_lines():
    r = process_orders(["bad line", "A,x,1.0", "A,-1,2.0", ",2,3.0", "A,2,3.0"])
    assert r["valid_count"] == 1 and r["invalid_count"] == 4

def test_by_sku_accumulates():
    r = process_orders(["A,1,1.0", "A,1,1.0", "B,1,2.0"])
    assert r["by_sku"] == {"A": 2.0, "B": 2.0}

def test_empty():
    r = process_orders([])
    assert r == {"valid_count": 0, "invalid_count": 0, "total": 0, "by_sku": {}}
''')
    checks.append({"name": "behavior preserved (hidden tests)", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    tree = _ast.parse(src)
    fns = [n.name for n in _ast.walk(tree) if isinstance(n, _ast.FunctionDef)]
    checks.append({"name": "split into >= 4 functions total", "ok": len(fns) >= 4,
                   "points": 4, "detail": f"functions: {fns}"})
    checks.append({"name": "process_orders still public entry", "ok": "def process_orders" in src, "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c05t04_baseline = {
    "taskrunner.py": '''"""Refactor task: cryptic names, missing docstrings."""

import time


def go(l, n=3, w=0.5):
    """run l? n? w?"""
    r = {}
    for x in l:
        for _ in range(n):
            time.sleep(w)
            try:
                x["fn"]()
                ok = True
            except Exception:
                ok = False
            if not ok:
                break
        r[x["id"]] = ok
    return r
''',
    "HINT.md": """Refactor task: rename every cryptic identifier to descriptive names
(e.g. go -> run_tasks, l -> tasks, n -> retries, w -> backoff_seconds, r ->
results, x -> task, fn -> action, ok -> succeeded), and add a short docstring
to every function explaining parameters and return value. Public behavior
must remain identical: run_tasks(tasks, retries=3, backoff_seconds=0.5)
executes each task's action up to `retries` times (sleeping
backoff_seconds before each attempt), records True/False per task id, and
stops retrying a task on first success.""",
}

c05t04_verify = V + r"""TID="c05t04"
import ast as _ast
checks = []
sol = os.path.join(ws, "taskrunner.py")
ok = os.path.exists(sol)
checks.append({"name": "taskrunner.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from taskrunner import run_tasks

class Flaky:
    def __init__(self, fail_times):
        self.calls = 0
        self.fail_times = fail_times
    def hit(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("flaky")

def test_success_after_retries():
    f = Flaky(2)
    res = run_tasks([{"id": "t1", "fn": f.hit}], retries=3, backoff_seconds=0)
    assert res == {"t1": True} and f.calls == 3

def test_fail_exhausts_retries():
    f = Flaky(99)
    res = run_tasks([{"id": "t1", "fn": f.hit}], retries=2, backoff_seconds=0)
    assert res == {"t1": False} and f.calls == 2

def test_stops_retrying_on_success():
    f = Flaky(0)
    run_tasks([{"id": "t1", "fn": f.hit}], retries=5, backoff_seconds=0)
    assert f.calls == 1
''')
    checks.append({"name": "renamed public API works (behavior preserved)", "ok": rc == 0, "points": 10,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    bad = [t for t in ["def go(", "def go (", "(l,", " l,", "=w=", "def go"] if t in src]
    checks.append({"name": "cryptic names gone", "ok": not bad, "points": 4, "detail": str(bad)})
    tree = _ast.parse(src)
    missing_doc = [n.name for n in _ast.walk(tree)
                   if isinstance(n, _ast.FunctionDef) and not _ast.get_docstring(n)]
    checks.append({"name": "docstrings on all functions", "ok": not missing_doc,
                   "points": 3, "detail": f"missing: {missing_doc}"})
    checks.append({"name": "module docstring updated (not the old placeholder)",
                   "ok": _ast.get_docstring(tree) is not None and "Refactor task" not in (_ast.get_docstring(tree) or ""), "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c05t05_baseline = {
    "loader.py": '''"""Config loader with unacceptable error handling (refactor task)."""

import json


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:                                    # BUG: bare except swallows everything
        return {}


def get(data, path):
    try:
        for k in path.split("."):
            data = data[k]
        return data
    except:                                    # BUG: bare except
        return None


def save(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except:                                    # BUG: bare except hides real IO errors
        return False
    return True
''',
    "HINT.md": """Refactor task: eliminate every bare `except:` in loader.py.
Required behavior after refactor:
- load(path): raise FileNotFoundError when the file is missing; raise
  json.JSONDecodeError (ValueError) when the content is not valid JSON;
  return the parsed dict otherwise.
- get(data, path): return None on missing keys / wrong types (that part is
  intentional behavior), but only catch (KeyError, TypeError) — nothing else.
- save(path, data): propagate real OSError (disk full, permission denied);
  return True on success. Keep the True/False-ish contract ONLY for OSError
  propagation being allowed: do not catch OSError — let it raise.""",
}

c05t05_verify = V + r"""TID="c05t05"
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
"""

C05_PROMPTS = {
    "c05t01": "Refactor `pricing.py` in this directory. Read HINT.md first.\nGoal: remove the duplicated rounding/tax logic by extracting helper function(s) and reusing them from both public functions. Behavior must stay EXACTLY identical (same rounding, same results). Keep the public API unchanged. Verify with a few examples before finishing.",
    "c05t02": "Refactor `sessions.py` in this directory. Read HINT.md first. Convert the module-level global state into a `SessionStore` class with the same operations (create, close, active_count; constructor starts empty). Module functions must no longer use `global`. Behavior of the operations must remain identical. Verify with quick tests across at least two store instances before finishing.",
    "c05t03": "Refactor `report.py` in this directory. Read HINT.md first. `process_orders` is a god function: split it into at least 3 focused helper functions. Behavior must remain EXACTLY identical - hidden tests will check parsing, discounts, aggregation, rounding and the empty-input case. Keep process_orders as the public entry point.",
    "c05t04": "Refactor `taskrunner.py` in this directory. Read HINT.md first. Rename all cryptic identifiers (target public API: run_tasks(tasks, retries=3, backoff_seconds=0.5)) and add docstrings to every function. Behavior must remain identical: retries per task with backoff sleeps, stop on first success, per-task True/False result keyed by task id. Verify with quick tests before finishing.",
    "c05t05": "Refactor `loader.py` in this directory. Read HINT.md first. Replace every bare `except:` with precise typed exception handling per the required behavior. All other behavior must stay the same. Verify with quick tests before finishing.",
}


def main():
    mk("c05_refactoring", "c05t01_dedupe", "Extract duplicated pricing logic", C05_PROMPTS["c05t01"], c05t01_verify, baseline=c05t01_baseline)
    mk("c05_refactoring", "c05t02_globals_to_class", "Replace globals with a class", C05_PROMPTS["c05t02"], c05t02_verify, baseline=c05t02_baseline)
    mk("c05_refactoring", "c05t03_god_function", "Split god function", C05_PROMPTS["c05t03"], c05t03_verify, baseline=c05t03_baseline)
    mk("c05_refactoring", "c05t04_naming_docs", "Rename + document", C05_PROMPTS["c05t04"], c05t04_verify, baseline=c05t04_baseline)
    mk("c05_refactoring", "c05t05_error_handling", "Type exception handling", C05_PROMPTS["c05t05"], c05t05_verify, baseline=c05t05_baseline)
    print("c05 tasks generated")


if __name__ == "__main__":
    main()
