#!/usr/bin/env python3
"""Generate benchmark tasks: C01 Code Generation + C02 Debugging."""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "tasks")

CATS = {
    "c01_code_generation": "Code Generation",
    "c02_debugging": "Debugging & Bug Fixing",
    "c03_feature": "Feature Implementation",
    "c04_testing_qa": "Testing & QA",
    "c05_refactoring": "Refactoring & Code Quality",
    "c06_git_engineering": "Repository / Git / GitHub Engineering",
    "c07_long_horizon": "Long-Horizon Autonomous Task",
    "c08_memory": "Memory & Context Retention",
    "c09_multi_agent": "Multi-Agent / Parallel Engineering",
    "c10_e2e": "End-to-End Software Engineering",
}


def mk(cat, tid, title, prompt, verify, baseline=None, prompt2=None):
    d = os.path.join(T, cat, tid)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    spec = {"id": tid, "category": cat, "category_title": CATS[cat], "title": title,
            "max_points": 20, "prompt": prompt}
    if prompt2:
        spec["prompt2"] = prompt2
    with open(os.path.join(d, "task.json"), "w") as f:
        json.dump(spec, f, indent=2)
    with open(os.path.join(d, "verify.py"), "w") as f:
        f.write(verify)
    if baseline:
        b = os.path.join(d, "baseline")
        os.makedirs(b, exist_ok=True)
        for name, code in baseline.items():
            p = os.path.join(b, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(code)


V = """#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
"""

# ============================ C01 CODE GENERATION ============================

c01t01_verify = V + r"""TID="c01t01"
checks = []
sol = os.path.join(ws, "solution.py")
ok = os.path.exists(sol)
checks.append({"name": "solution.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from solution import is_balanced

def test_simple_pairs():
    assert is_balanced("()") is True
    assert is_balanced("[]") is True
    assert is_balanced("{}") is True

def test_nested_mixed():
    assert is_balanced("([{}])") is True
    assert is_balanced("{[()()]}") is True

def test_unbalanced():
    assert is_balanced("(") is False
    assert is_balanced(")(") is False
    assert is_balanced("([)]") is False

def test_empty_and_nonbrackets():
    assert is_balanced("") is True
    assert is_balanced("abc") is True

def test_long():
    assert is_balanced("(" * 50 + ")" * 50) is True
    assert is_balanced("]" * 3) is False
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "all hidden tests passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c01t01_prompt = """Implement a bracket validator in the file `solution.py` in this directory.

Required API:
    def is_balanced(s: str) -> bool

Rules:
- It must handle three bracket types: (), [], {}
- Every opening bracket must be closed by the same type in LIFO order
- Non-bracket characters must be ignored
- An empty string is balanced
Return True when balanced, False otherwise. Use an explicit stack (no recursion
on each character). Add a brief docstring. Do not create any other files."""

c01t02_verify = V + r"""TID="c01t02"
checks = []
sol = os.path.join(ws, "flatten.py")
ok = os.path.exists(sol)
checks.append({"name": "flatten.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from flatten import flatten

def test_flat_dict():
    assert flatten({"a": 1, "b": 2}) == {"a": 1, "b": 2}

def test_nested():
    assert flatten({"a": {"b": {"c": 1}}}) == {"a.b.c": 1}

def test_custom_sep():
    assert flatten({"a": {"b": 1}}, sep="/") == {"a/b": 1}

def test_lists():
    assert flatten({"a": [1, {"b": 2}]}) == {"a.0": 1, "a.1.b": 2}

def test_empty_containers():
    assert flatten({"a": {}}) == {"a": {}}
    assert flatten({"a": []}) == {"a": []}

def test_scalars():
    assert flatten({"a": None}) == {"a": None}
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "all hidden tests passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c01t02_prompt = """Implement a dictionary flattener in `flatten.py` in this directory.

Required API:
    def flatten(obj: dict, sep: str = ".") -> dict

Rules:
- Nested dicts are flattened by joining keys with `sep` (e.g. {"a": {"b": 1}} -> {"a.b": 1})
- Lists inside are indexed by position (e.g. {"a": [10]} -> {"a.0": 10})
- Empty dicts/lists are kept as leaf values under their key
- Non-dict/list scalars (str, int, float, bool, None) are leaf values
- The input object must not be mutated
Include a docstring. Do not create other files."""

c01t03_verify = V + r"""TID="c01t03"
checks = []
sol = vlib.find_file(ws, "lru_cache.py") or vlib.find_file(ws, "lru.py")
ok = bool(sol)
checks.append({"name": "lru_cache.py found", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath("lru_cache.py")))
from lru_cache import LRUCache

def test_basic_put_get():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1
    assert c.get("b") == 2

def test_eviction():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("c", 3)
    assert c.get("a") == -1
    assert c.get("b") == 2
    assert c.get("c") == 3

def test_recency_update():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    c.get("a")          # a now most recent
    c.put("c", 3)       # evicts b
    assert c.get("b") == -1
    assert c.get("a") == 1

def test_put_updates_existing():
    c = LRUCache(2)
    c.put("a", 1); c.put("a", 9); c.put("b", 2)
    assert c.get("a") == 9

def test_capacity_one():
    c = LRUCache(1)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == -1 and c.get("b") == 2
''')
    checks.append({"name": "hidden pytest suite (behavior)", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    if ok:
        tree = vlib.parse_ast_file(sol)
        src = open(sol).read()
        uses_ord = "OrderedDict" in src
        has_hash = ("__hash__" not in src) and ("dict" in src or "OrderedDict" in src)
        checks.append({"name": "O(1) structure (hash map + doubly linked list or OrderedDict)",
                       "ok": ("class" in src and ("prev" in src or "OrderedDict" in src)), "points": 4})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c01t03_prompt = """Design and implement an LRU Cache in `lru_cache.py` in this directory.

Required API:
    class LRUCache:
        def __init__(self, capacity: int)   # capacity >= 1
        def get(self, key) -> any           # returns -1 when key is absent
        def put(self, key, value) -> None

Semantics:
- Both get and put must run in O(1) average time
- get/put count as "use"; when capacity is exceeded, evict the LEAST recently used entry
- put on an existing key updates the value AND its recency

You may use collections.OrderedDict or build your own doubly linked list + hash
map. Add docstrings. Do not create other files."""

c01t04_verify = V + r"""TID="c01t04"
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
"""

c01t04_prompt = """Implement an RFC-4180-style CSV parser in `csvparse.py` in this directory —
WITHOUT importing the stdlib `csv` module (write the state machine yourself).

Required API:
    def parse_csv(text: str) -> list[list[str]]

Must support:
- comma-separated fields, one record per line
- quoted fields with double quotes: commas, newlines and escaped quotes
  (doubled quotes, i.e. "" -> ") inside quotes must be handled
- empty fields (a,,b) and a trailing newline at the end of the input

Include a docstring. Do not create other files."""

c01t05_verify = V + r"""TID="c01t05"
checks = []
sol = os.path.join(ws, "matrix.py")
ok = os.path.exists(sol)
checks.append({"name": "matrix.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
from matrix import rotate_90, spiral_traverse

def test_rotate_3x3():
    m = [[1,2,3],[4,5,6],[7,8,9]]
    assert rotate_90(m) == [[7,4,1],[8,5,2],[9,6,3]]

def test_rotate_2x2():
    assert rotate_90([[1,2],[3,4]]) == [[3,1],[4,2]]

def test_rotate_1x1_and_4x4():
    assert rotate_90([[5]]) == [[5]]
    m = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
    assert rotate_90(m) == [[13,9,5,1],[14,10,6,2],[15,11,7,3],[16,12,8,4]]

def test_input_not_mutated():
    m = [[1,2],[3,4]]
    rotate_90(m)
    assert m == [[1,2],[3,4]]

def test_spiral_3x3():
    m = [[1,2,3],[4,5,6],[7,8,9]]
    assert spiral_traverse(m) == [1,2,3,6,9,8,7,4,5]

def test_spiral_rect():
    m = [[1,2,3],[4,5,6]]
    assert spiral_traverse(m) == [1,2,3,6,5,4]

def test_spiral_single():
    assert spiral_traverse([[7]]) == [7]
''')
    checks.append({"name": "hidden pytest suite", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c01t05_prompt = """Implement matrix operations in `matrix.py` in this directory.

Required API:
    def rotate_90(matrix: list[list[int]]) -> list[list[int]]
        # returns a NEW matrix rotated 90 degrees clockwise; must NOT mutate input
    def spiral_traverse(matrix: list[list[int]]) -> list[int]
        # returns elements in clockwise spiral order, starting top-left

Both functions must handle square and rectangular matrices, plus 1x1.
Include docstrings. Do not create other files."""


# ============================ C02 DEBUGGING ============================

c02_baseline_common = {}

c02t01_baseline = {
    "search.py": '''"""Binary search module. BUG: returns wrong index / loops forever on some inputs."""


def binary_search(arr, target):
    """Return index of target in sorted arr, or -1 if absent."""
    lo, hi = 0, len(arr) - 1
    while lo < hi:            # BUG: should be lo <= hi
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1      # BUG: with lo<hi this skips the last candidate
    return -1                 # BUG: never checks arr[lo] when lo==hi
''',
    "test_search.py": '''from search import binary_search


def test_found_middle():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2


def test_found_first():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0


def test_found_last():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4


def test_absent():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1


def test_single_found():
    assert binary_search([42], 42) == 0


def test_single_absent():
    assert binary_search([42], 7) == -1


def test_two_elements():
    assert binary_search([1, 2], 2) == 1
''',
}

c02t01_verify = V + r"""TID="c02t01"
checks = []
sol = os.path.join(ws, "search.py")
ok = os.path.exists(sol)
checks.append({"name": "search.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_search.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes", "ok": rc == 0, "points": 12,
                   "detail": out[-400:] if rc != 0 else "passed"})
    rc2, out2 = vlib.write_and_run_pytest(ws, '''
from search import binary_search

def test_even_length_first():
    assert binary_search([1, 3, 5, 7], 1) == 0

def test_even_length_last():
    assert binary_search([1, 3, 5, 7], 7) == 3

def test_even_length_absent_between():
    assert binary_search([1, 3, 5, 7], 4) == -1

def test_duplicates_find_a_valid_index():
    arr = [1, 2, 2, 2, 3]
    i = binary_search(arr, 2)
    assert arr[i] == 2

def test_empty():
    assert binary_search([], 1) == -1
''')
    checks.append({"name": "extra edge cases (even length, empty, duplicates)", "ok": rc2 == 0, "points": 6,
                   "detail": out2[-400:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c02t01_prompt = """The file `search.py` in this directory contains `binary_search`, and
`test_search.py` contains its test suite. The tests are FAILING.

1. Run the tests to see the failures (python -m pytest test_search.py -q)
2. Identify the root cause of the bug(s) in binary_search
3. Fix `search.py` so that ALL tests pass
4. Re-run the tests to confirm

Rules: keep the same function signature and O(log n) complexity. Do NOT modify
test_search.py. Do not create new files."""

c02t02_baseline = {
    "cart.py": '''"""Shopping cart utilities. BUG: mutable default arguments accumulate state."""

import json


def add_item(item, cart=[]):          # BUG: shared mutable default
    cart.append(item)
    return cart


def add_tagged(item, tags=[], extra={}):   # BUG: two shared mutable defaults
    tags.append(item["sku"])
    extra["last"] = item["sku"]
    return {"sku": item["sku"], "tags": tags, "extra": extra}


def save(cart, path):
    with open(path, "w") as f:
        json.dump(cart, f)
''',
    "test_cart.py": '''from cart import add_item, add_tagged


def test_add_item_isolated():
    c1 = add_item({"sku": "A", "price": 2})
    c2 = add_item({"sku": "B", "price": 3})
    assert c1 != c2, "separate calls must not share state"
    assert c1 == [{"sku": "A", "price": 2}]


def test_add_item_explicit_list_ok():
    mine = []
    add_item({"sku": "X"}, mine)
    add_item({"sku": "Y"}, mine)
    assert len(mine) == 2


def test_add_tagged_isolated():
    r1 = add_tagged({"sku": "A"})
    r2 = add_tagged({"sku": "B"})
    assert r1["tags"] == ["A"], "tags must not leak across calls"
    assert r2["tags"] == ["B"]
    assert r1["extra"] == {"last": "A"}
''',
}

c02t02_verify = V + r"""TID="c02t02"
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
"""

c02t02_prompt = """`cart.py` has failing tests in `test_cart.py`. The root cause is the classic
Python pitfall involving default argument values that are mutable.

1. Run python -m pytest test_cart.py -q to see the failures
2. Fix the bug(s) in `cart.py` while keeping the exact same public API and
   call signatures (callers may pass an explicit list/dict, or nothing at all)
3. Make ALL tests pass. Do NOT modify test_cart.py, do not create new files."""

c02t03_baseline = {
    "money.py": '''"""Money handling. BUG: binary float arithmetic corrupts currency totals."""

CENTS_IN_DOLLAR = 100


def add_prices(a, b):
    """Add two prices given as floats of dollars. BUG: naive float add."""
    return a + b


def apply_tax(amount, rate):
    """amount: float dollars, rate: e.g. 0.0725. BUG: loses cents precision."""
    return amount * (1 + rate)


def total_price(prices):
    """Sum a list of float dollar prices. BUG: accumulates float error."""
    total = 0.0
    for p in prices:
        total += p
    return total


def format_usd(amount):
    """Format as USD string with exactly 2 decimals, half-up rounding."""
    return f"${amount:.2f}"
''',
    "test_money.py": '''from money import add_prices, apply_tax, total_price, format_usd


def test_add_cents():
    assert add_prices(0.1, 0.2) == 0.3


def test_total_accumulation():
    prices = [0.1] * 10
    assert total_price(prices) == 1.0


def test_tax_rounds_to_cents():
    # 19.99 with 7.25% tax = 21.439775 -> must round half-up to 21.44
    assert apply_tax(19.99, 0.0725) == 21.44


def test_format_two_decimals():
    assert format_usd(21.439775) == "$21.44"


def test_total_mixed_cents():
    assert total_price([1.99, 2.49, 0.02]) == 4.5
''',
}

c02t03_verify = V + r"""TID="c02t03"
checks = []
sol = os.path.join(ws, "money.py")
ok = os.path.exists(sol)
checks.append({"name": "money.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_money.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes (exact cent arithmetic)", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    checks.append({"name": "uses decimal or integer cents (no raw float math)",
                   "ok": ("Decimal" in src or "from decimal" in src or "round(" in src or "// 1" in src or "* 100" in src),
                   "points": 2})
    checks.append({"name": "format_usd still exists with same signature", "ok": "def format_usd" in src, "points": 2})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c02t03_prompt = """`money.py` handles currency amounts as floats and its tests in
`test_money.py` FAIL because binary floating point cannot represent decimal
cents exactly (0.1 + 0.2 != 0.3, etc).

Fix `money.py` so that:
- add_prices(0.1, 0.2) returns exactly 0.3
- total_price accumulates with exact cent precision (work in integer cents
  internally or use decimal.Decimal — both are acceptable)
- apply_tax rounds half-up to the cent: apply_tax(19.99, 0.0725) == 21.44
- format_usd keeps formatting with exactly two decimals

Keep every public function name/signature unchanged. Make ALL tests pass.
Do NOT modify test_money.py, do not create new files."""

c02t04_baseline = {
    "validators.py": '''"""Email validation. BUG: regex accepts invalid and rejects valid addresses."""

import re

EMAIL_RE = re.compile(r"^[a-z]+@[a-z]+\\.[a-z]{2}$")   # BUG: too strict/wrong


def is_valid_email(addr):
    """Return True when addr is a syntactically valid email address."""
    return bool(EMAIL_RE.match(addr))
''',
    "test_validators.py": '''from validators import is_valid_email


def test_simple():
    assert is_valid_email("user@example.com") is True


def test_subdomains():
    assert is_valid_email("first.last@mail.example.co.uk") is True


def test_plus_and_digits():
    assert is_valid_email("user+tag123@example-site.io") is True


def test_missing_at():
    assert is_valid_email("userexample.com") is False


def test_double_at():
    assert is_valid_email("us@@er@x.com") is False


def test_no_tld():
    assert is_valid_email("user@localhost") is False


def test_leading_dot():
    assert is_valid_email(".user@example.com") is False


def test_consecutive_dots():
    assert is_valid_email("a..b@example.com") is False
''',
}

c02t04_verify = V + r"""TID="c02t04"
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
"""

c02t04_prompt = """`validators.py` validates emails with a broken regex; `test_validators.py`
documents the expected behavior and currently FAILS.

Diagnose the regex problems (it rejects many valid addresses and accepts some
invalid ones), then fix `is_valid_email` so ALL tests pass, keeping:
- the same function name/signature
- a regex-based implementation (still use `re`)

Practical email syntax to support: local part letters/digits/._%+- (no leading
or consecutive dots), @, domain labels with hyphens, TLD of 2+ letters.
Do NOT modify test_validators.py, do not create new files."""

c02t05_baseline = {
    "schedule.py": '''"""Meeting scheduler. BUG: mixes naive and timezone-aware datetimes."""

from datetime import datetime, timezone, timedelta


def parse_stamp(text):
    """Parse ISO stamp. Naive input means UTC. BUG: returns naive for 'Z'."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if text.endswith("Z"):
        dt = dt.replace(tzinfo=None)      # BUG: silently drops UTC info
    return dt


def minutes_between(a, b):
    """Minutes from a to b (b - a). BUG: crashes when mixing aware/naive."""
    return (b - a).total_seconds() / 60.0


def add_minutes(dt, mins):
    """BUG: adds minutes in local time even for aware datetimes with offset."""
    return dt + timedelta(minutes=mins)
''',
    "test_schedule.py": '''from datetime import datetime, timezone, timedelta
from schedule import parse_stamp, minutes_between, add_minutes


def test_parse_zulu_keeps_tz():
    dt = parse_stamp("2026-01-02T03:04:05Z")
    assert dt.utcoffset() == timedelta(0), "Z stamp must stay UTC-aware"


def test_parse_offset_kept():
    dt = parse_stamp("2026-01-02T03:04:05+02:00")
    assert dt.utcoffset() == timedelta(hours=2)


def test_parse_naive_means_utc():
    dt = parse_stamp("2026-01-02T03:04:05")
    assert dt.utcoffset() == timedelta(0), "naive input must be interpreted as UTC"


def test_minutes_between_both_aware():
    a = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    b = a + timedelta(minutes=90)
    assert minutes_between(a, b) == 90.0


def test_minutes_between_mixed_offsets():
    a = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    b = datetime(2026, 1, 1, 3, 0, tzinfo=timezone(timedelta(hours=2)))
    assert minutes_between(a, b) == 60.0


def test_add_minutes_aware():
    dt = datetime(2026, 1, 1, 23, 50, tzinfo=timezone.utc)
    out = add_minutes(dt, 20)
    assert out.tzinfo is not None and out.hour == 0 and out.minute == 10
''',
}

c02t05_verify = V + r"""TID="c02t05"
checks = []
sol = os.path.join(ws, "schedule.py")
ok = os.path.exists(sol)
checks.append({"name": "schedule.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "baseline", "test_schedule.py")).read(), test_name="test_public.py")
    checks.append({"name": "public test suite passes", "ok": rc == 0, "points": 14,
                   "detail": out[-400:] if rc != 0 else "passed"})
    src = open(sol).read()
    checks.append({"name": "same three public functions kept",
                   "ok": all(f"def {f}" in src for f in ("parse_stamp", "minutes_between", "add_minutes")), "points": 3})
    checks.append({"name": "no silent tzinfo stripping remains", "ok": "tzinfo=None" not in src, "points": 1})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c02t05_prompt = """`schedule.py` mixes naive and timezone-aware datetimes and crashes or
silently drops UTC information. `test_schedule.py` defines correct behavior
and currently FAILS.

Fix `schedule.py` so that:
- a 'Z' stamp keeps its UTC awareness (no tzinfo stripping)
- a stamp with numeric offset keeps that offset
- a naive stamp is interpreted as UTC (attach UTC, do not leave it naive)
- minutes_between works for aware inputs in different offsets
- add_minutes preserves awareness across day boundaries

Keep all three function names/signatures. Make ALL tests pass. Do NOT modify
test_schedule.py, do not create new files."""


def main():
    mk("c01_code_generation", "c01t01_bracket_validator", "Bracket validator", c01t01_prompt, c01t01_verify)
    mk("c01_code_generation", "c01t02_flatten_dict", "Nested dict flattener", c01t02_prompt, c01t02_verify)
    mk("c01_code_generation", "c01t03_lru_cache", "LRU cache class", c01t03_prompt, c01t03_verify)
    mk("c01_code_generation", "c01t04_csv_parser", "CSV parser state machine", c01t04_prompt, c01t04_verify)
    mk("c01_code_generation", "c01t05_matrix_ops", "Matrix rotation + spiral", c01t05_prompt, c01t05_verify)

    mk("c02_debugging", "c02t01_binary_search", "Fix binary search", c02t01_prompt, c02t01_verify, baseline=c02t01_baseline)
    mk("c02_debugging", "c02t02_mutable_defaults", "Fix mutable default args", c02t02_prompt, c02t02_verify, baseline=c02t02_baseline)
    mk("c02_debugging", "c02t03_money_floats", "Fix float money math", c02t03_prompt, c02t03_verify, baseline=c02t03_baseline)
    mk("c02_debugging", "c02t04_email_regex", "Fix email regex", c02t04_prompt, c02t04_verify, baseline=c02t04_baseline)
    mk("c02_debugging", "c02t05_timezone_mix", "Fix naive/aware datetime mix", c02t05_prompt, c02t05_verify, baseline=c02t05_baseline)
    print("c01 + c02 tasks generated")


if __name__ == "__main__":
    main()
