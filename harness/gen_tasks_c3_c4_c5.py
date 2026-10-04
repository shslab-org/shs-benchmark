#!/usr/bin/env python3
"""Generate benchmark tasks: C03 Feature, C04 Testing & QA, C05 Refactoring."""
import json, os, shutil, sys
from gen_tasks_c1_c2 import mk, V, T, CATS

# ============================ C03 FEATURE ============================

INV_MODEL = '''"""Tiny inventory package. Extend it per task instructions."""


class Inventory:
    def __init__(self):
        self._items = {}   # sku -> dict(name, price, qty)

    def add_item(self, sku, name, price, qty):
        if sku in self._items:
            self._items[sku]["qty"] += qty
        else:
            self._items[sku] = {"name": name, "price": price, "qty": qty}
        return self._items[sku]

    def get_item(self, sku):
        return self._items.get(sku)

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])
'''

INV_TEST = '''import pytest
from inventory import Inventory


def test_add_and_get():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1") == {"name": "Apple", "price": 0.5, "qty": 10}


def test_add_same_sku_increments():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.add_item("SKU1", "Apple", 0.5, 5)
    assert inv.get_item("SKU1")["qty"] == 15


def test_list_sorted_by_name():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 1)
    names = [i["name"] for i in inv.list_items()]
    assert names == ["Apple", "Banana"]


def test_get_missing_returns_none():
    assert Inventory().get_item("NOPE") is None
'''

c03t01_verify = V + r"""TID="c03t01"
checks = []
sol = os.path.join(ws, "inventory.py")
ok = os.path.exists(sol)
checks.append({"name": "inventory.py still exists (behavior preserved)", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
from inventory import Inventory

def test_search_substring_case_insensitive():
    inv = Inventory()
    inv.add_item("A", "Green Apple", 0.5, 3)
    inv.add_item("B", "Banana", 1.0, 2)
    found = inv.search("apple")
    assert [i["name"] for i in found] == ["Green Apple"]

def test_search_no_match_empty():
    assert Inventory().search("zzz") == []

def test_search_partial():
    inv = Inventory()
    inv.add_item("A", "Green Apple", 0.5, 3)
    assert len(inv.search("reen")) == 1

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1")["qty"] == 10
''')
    checks.append({"name": "search() feature + regression tests", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c03t01_prompt = BASE3 = """This directory contains a small inventory package: `inventory.py` (class
Inventory) and `test_inventory.py` (existing, passing tests).

Add a NEW feature to the Inventory class:

    def search(self, keyword: str) -> list
        # returns all items whose name contains keyword, case-insensitive,
        # in the same sorted-by-name order as list_items()

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 2 new tests for search() to test_inventory.py (append, do not
  remove anything)
- Run the full suite and make sure everything passes"""

c03t02_verify = V + r"""TID="c03t02"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
import pytest
from inventory import Inventory

def test_remove_stock_success():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 10)
    inv.remove_stock("A", 4)
    assert inv.get_item("A")["qty"] == 6

def test_remove_to_exact_zero():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    inv.remove_stock("A", 5)
    assert inv.get_item("A")["qty"] == 0

def test_remove_more_than_available_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    with pytest.raises(ValueError):
        inv.remove_stock("A", 4)

def test_remove_negative_qty_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    with pytest.raises(ValueError):
        inv.remove_stock("A", -1)

def test_remove_unknown_sku_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.remove_stock("GHOST", 1)

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1")["qty"] == 10
''')
    checks.append({"name": "remove_stock feature + validation + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c03t02_prompt = BASE3.replace("Add a NEW feature to the Inventory class:", """Add a NEW feature to the Inventory class:""").replace(
    '''    def search(self, keyword: str) -> list
        # returns all items whose name contains keyword, case-insensitive,
        # in the same sorted-by-name order as list_items()

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 2 new tests for search() to test_inventory.py (append, do not
  remove anything)
- Run the full suite and make sure everything passes''',
    '''    def remove_stock(self, sku: str, qty: int) -> None
        # decreases available qty by qty
        # raises ValueError when: sku unknown, qty <= 0, or qty > available

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 3 new tests for remove_stock to test_inventory.py (append only)
- Run the full suite and make sure everything passes''')

c03t03_verify = V + r"""TID="c03t03"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys, csv, io
sys.path.insert(0, ".")
from inventory import Inventory

def test_export_header_and_rows():
    inv = Inventory()
    inv.add_item("B", "Banana", 1.0, 2)
    inv.add_item("A", "Apple", 0.5, 3)
    text = inv.export_csv()
    rows = list(csv.reader(io.StringIO(text)))
    assert rows[0] == ["sku", "name", "price", "qty"]
    data = rows[1:]
    assert {"A", "Apple", "0.5", "3"} in [set(r) for r in data] or ["A", "Apple", "0.5", "3"] in data
    assert ["B", "Banana", "1.0", "2"] in data or {"B", "Banana", "1.0", "2"} in [set(r) for r in data]

def test_export_roundtrip_basic():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    text = inv.export_csv()
    assert "Apple" in text and "sku" in text

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    assert inv.get_item("SKU1")["qty"] == 10
''')
    checks.append({"name": "export_csv feature + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c03t03_prompt = BASE3.replace(
    '''    def search(self, keyword: str) -> list
        # returns all items whose name contains keyword, case-insensitive,
        # in the same sorted-by-name order as list_items()

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 2 new tests for search() to test_inventory.py (append, do not
  remove anything)
- Run the full suite and make sure everything passes''',
    '''    def export_csv(self) -> str
        # returns the inventory as CSV text with header
        # sku,name,price,qty  — one row per item, same order as list_items()

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 2 new tests for export_csv to test_inventory.py (append only)
- Run the full suite and make sure everything passes''')

c03t04_verify = V + r"""TID="c03t04"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
from inventory import Inventory

def test_events_recorded_on_add():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 3)
    events = inv.get_events()
    assert len(events) == 1 and "add" in str(events[0]).lower() and "A" in str(events[0])

def test_events_recorded_on_remove():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    inv.remove_stock("A", 2)
    events = inv.get_events()
    assert len(events) == 2 and "remove" in str(events[-1]).lower()

def test_events_have_timestamps():
    inv = Inventory()
    inv.add_item("A", "Apple", 0.5, 5)
    assert any(ch.isdigit() for ch in str(inv.get_events()[0])), "event must include a timestamp"

def test_original_behavior_intact():
    inv = Inventory()
    inv.add_item("SKU1", "Apple", 0.5, 10)
    inv.remove_stock("SKU1", 1)
    assert inv.get_item("SKU1")["qty"] == 9
''')
    checks.append({"name": "event log feature (add+remove, timestamps) + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c03t04_prompt = BASE3.replace(
    '''    def search(self, keyword: str) -> list
        # returns all items whose name contains keyword, case-insensitive,
        # in the same sorted-by-name order as list_items()

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 2 new tests for search() to test_inventory.py (append, do not
  remove anything)
- Run the full suite and make sure everything passes''',
    '''an append-only event log that is updated automatically:
    def get_events(self) -> list
        # chronological list of events; every add_item and every
        # remove_stock call appends one event containing at minimum:
        # an ISO-8601 timestamp, the action ("add"/"remove"), the sku

Requirements:
- Existing methods and their behavior must remain unchanged
  (implement remove_stock as well if you add event tracking that needs it:
   remove_stock(sku, qty) decreases qty, raising ValueError on unknown sku,
   qty <= 0, or qty > available)
- Existing tests must keep passing
- Add at least 3 new tests for the event log to test_inventory.py (append only)
- Run the full suite and make sure everything passes''')

c03t05_verify = V + r"""TID="c03t05"
checks = []
ok = os.path.exists(os.path.join(ws, "inventory.py"))
checks.append({"name": "inventory.py exists", "ok": ok, "points": 2})
if ok:
    rc, out = vlib.write_and_run_pytest(ws, '''
import sys
sys.path.insert(0, ".")
import pytest
from inventory import Inventory

def test_set_and_get_discount():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    inv.apply_discount("A", 25)
    assert inv.price_with_discount("A") == 1.5

def test_zero_discount():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    inv.apply_discount("A", 0)
    assert inv.price_with_discount("A") == 2.0

def test_over_100_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    with pytest.raises(ValueError):
        inv.apply_discount("A", 101)

def test_negative_raises():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    with pytest.raises(ValueError):
        inv.apply_discount("A", -5)

def test_unknown_sku_raises():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.apply_discount("GHOST", 10)

def test_no_discount_by_default():
    inv = Inventory()
    inv.add_item("A", "Apple", 2.0, 5)
    assert inv.price_with_discount("A") == 2.0
''')
    checks.append({"name": "discount feature + bounds validation + regression", "ok": rc == 0, "points": 18,
                   "detail": out[-400:] if rc != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c03t05_prompt = BASE3.replace(
    '''    def search(self, keyword: str) -> list
        # returns all items whose name contains keyword, case-insensitive,
        # in the same sorted-by-name order as list_items()

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 2 new tests for search() to test_inventory.py (append, do not
  remove anything)
- Run the full suite and make sure everything passes''',
    '''percentage discounting:
    def apply_discount(self, sku: str, pct: float) -> None
        # sets a discount percentage (0 <= pct <= 100) for that sku
        # raises ValueError for unknown sku or pct outside 0..100
    def price_with_discount(self, sku: str) -> float
        # current unit price after the sku's discount (no discount set = full price)

Requirements:
- Existing methods and their behavior must remain unchanged
- Existing tests must keep passing
- Add at least 3 new tests for discounting to test_inventory.py (append only)
- Run the full suite and make sure everything passes''')


# ============================ C04 TESTING & QA ============================

STRINGUTILS_BUGGY = '''"""String utilities — CONTAINS SEEDED BUGS for the QA benchmark."""
import re


def slugify(text):
    """Lowercase, non-alphanumerics -> single hyphen, strip ends."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())      # BUG 1: no strip of leading/trailing '-'
    return s


def truncate(text, width, ellipsis="..."):
    """Truncate with ellipsis so total length never exceeds width."""
    if len(text) <= width:                             # BUG 2: off-by-one, should be <= width - len(ellipsis) branch
        return text
    return text[: width - len(ellipsis)] + ellipsis    # BUG 2b: when width <= len(ellipsis) -> negative slice


def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return s1.lower()                                   # BUG 3: misses acronym boundary (HTTPServer -> h_t_t_p_server)


def count_vowels(text):
    return sum(1 for ch in text.lower() if ch in "aeiou")   # correct on purpose
'''

STRINGUTILS_FIXED = '''"""String utilities — reference fixed version."""
import re


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return s.strip("-")


def truncate(text, width, ellipsis="..."):
    if width <= len(ellipsis):
        return ellipsis[:width]
    if len(text) <= width:
        return text
    return text[: width - len(ellipsis)] + ellipsis


def camel_to_snake(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s1).lower()


def count_vowels(text):
    return sum(1 for ch in text.lower() if ch in "aeiou")
'''

c04_spec = """SPEC for stringutils.py (the module under test):

- slugify(text): lowercase text, replace every run of non-alphanumeric
  characters with a single hyphen, and REMOVE leading/trailing hyphens.
  slugify("  Hello, World!  ") == "hello-world"

- truncate(text, width, ellipsis="..."): if text fits within width return it
  unchanged; otherwise cut it so the result is EXACTLY width characters long
  including the ellipsis. If width is smaller than the ellipsis itself,
  return a prefix of the ellipsis cut to width.
  truncate("hello world", 8) == "hello..."
  truncate("hi", 5) == "hi"
  truncate("abcdef", 2) == ".."

- camel_to_snake(name): convert CamelCase (including acronym runs like
  "HTTPServer") to snake_case.
  camel_to_snake("HTTPServer") == "http_server"
  camel_to_snake("myVarName") == "my_var_name"

- count_vowels(text): number of vowels a,e,i,o,u (case-insensitive).
  count_vowels("Banana") == 3

YOUR JOB: write a pytest suite in tests_agent/test_stringutils.py that would
FAIL against a module violating this spec (the shipped module DOES violate it
in at least 3 places) and PASS against a correct implementation.
Do NOT modify or delete stringutils.py."""

c04t01_verify = V + r"""TID="c04t01"
import shutil, tempfile
checks = []
tdir = os.path.dirname(os.path.abspath(__file__))
test_file = os.path.join(ws, "tests_agent", "test_stringutils.py")
ok = os.path.exists(test_file)
checks.append({"name": "tests_agent/test_stringutils.py exists", "ok": ok, "points": 4})
if ok:
    code = open(test_file).read()
    checks.append({"name": "no source tampering (stringutils.py untouched)",
                   "ok": "SEEDED BUGS" in open(os.path.join(ws, "stringutils.py")).read(), "points": 3})
    buggy = tempfile.mkdtemp(); fixed = tempfile.mkdtemp()
    shutil.copy(test_file, buggy); shutil.copy(test_file, fixed)
    open(os.path.join(buggy, "stringutils.py"), "w").write(open(os.path.join(tdir, "reference_buggy.py")).read())
    open(os.path.join(fixed, "stringutils.py"), "w").write(open(os.path.join(tdir, "reference_fixed.py")).read())
    rc_b, out_b = vlib.write_and_run_pytest(buggy, code, test_name="t_buggy.py")
    rc_f, out_f = vlib.write_and_run_pytest(fixed, code, test_name="t_fixed.py")
    checks.append({"name": "tests FAIL on the buggy module (defects detected)",
                   "ok": rc_b != 0, "points": 6, "detail": out_b[-300:]})
    checks.append({"name": "tests PASS on the correct module (no false positives)",
                   "ok": rc_f == 0, "points": 6, "detail": out_f[-300:] if rc_f != 0 else "passed"})
    n_tests = code.count("def test_")
    checks.append({"name": "at least 8 test functions", "ok": n_tests >= 8, "points": 1,
                   "detail": f"found {n_tests}"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c04t02_verify = V + r"""TID="c04t02"
import shutil, tempfile
checks = []
tdir = os.path.dirname(os.path.abspath(__file__))
test_file = os.path.join(ws, "tests_agent", "test_stats.py")
ok = os.path.exists(test_file)
checks.append({"name": "tests_agent/test_stats.py exists", "ok": ok, "points": 4})
if ok:
    code = open(test_file).read()
    checks.append({"name": "no source tampering (stats.py untouched)",
                   "ok": "SEEDED BUGS" in open(os.path.join(ws, "stats.py")).read(), "points": 3})
    buggy = tempfile.mkdtemp(); fixed = tempfile.mkdtemp()
    shutil.copy(test_file, buggy); shutil.copy(test_file, fixed)
    open(os.path.join(buggy, "stats.py"), "w").write(open(os.path.join(tdir, "reference_buggy.py")).read())
    open(os.path.join(fixed, "stats.py"), "w").write(open(os.path.join(tdir, "reference_fixed.py")).read())
    rc_b, out_b = vlib.write_and_run_pytest(buggy, code, test_name="t_buggy.py")
    rc_f, out_f = vlib.write_and_run_pytest(fixed, code, test_name="t_fixed.py")
    checks.append({"name": "tests FAIL on the buggy module", "ok": rc_b != 0, "points": 6, "detail": out_b[-300:]})
    checks.append({"name": "tests PASS on the correct module", "ok": rc_f == 0, "points": 6, "detail": out_f[-300:] if rc_f != 0 else "passed"})
    n_tests = code.count("def test_")
    checks.append({"name": "at least 8 test functions", "ok": n_tests >= 8, "points": 1, "detail": f"found {n_tests}"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c04t03_verify = V + r"""TID="c04t03"
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
"""

c04t04_verify = V + r"""TID="c04t04"
import shutil, tempfile
checks = []
tdir = os.path.dirname(os.path.abspath(__file__))
test_file = os.path.join(ws, "tests_agent", "test_jsonutils.py")
ok = os.path.exists(test_file)
checks.append({"name": "tests_agent/test_jsonutils.py exists", "ok": ok, "points": 4})
if ok:
    code = open(test_file).read()
    checks.append({"name": "no source tampering (jsonutils.py untouched)",
                   "ok": "SEEDED BUGS" in open(os.path.join(ws, "jsonutils.py")).read(), "points": 3})
    buggy = tempfile.mkdtemp(); fixed = tempfile.mkdtemp()
    shutil.copy(test_file, buggy); shutil.copy(test_file, fixed)
    open(os.path.join(buggy, "jsonutils.py"), "w").write(open(os.path.join(tdir, "reference_buggy.py")).read())
    open(os.path.join(fixed, "jsonutils.py"), "w").write(open(os.path.join(tdir, "reference_fixed.py")).read())
    rc_b, out_b = vlib.write_and_run_pytest(buggy, code, test_name="t_buggy.py")
    rc_f, out_f = vlib.write_and_run_pytest(fixed, code, test_name="t_fixed.py")
    checks.append({"name": "tests FAIL on the buggy module", "ok": rc_b != 0, "points": 6, "detail": out_b[-300:]})
    checks.append({"name": "tests PASS on the correct module", "ok": rc_f == 0, "points": 6, "detail": out_f[-300:] if rc_f != 0 else "passed"})
    n_tests = code.count("def test_")
    checks.append({"name": "at least 8 test functions", "ok": n_tests >= 8, "points": 1, "detail": f"found {n_tests}"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
"""

c04t05_verify = V + r"""TID="c04t05"
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
"""

# C04 task assembly
c04t01_baseline = {
    "stringutils.py": STRINGUTILS_BUGGY,
}
c04t02_baseline = {
    "stats.py": '''"""Statistics — CONTAINS SEEDED BUGS for the QA benchmark."""
import math


def mean(xs):
    return sum(xs) / max(len(xs), 1)          # BUG 1: empty list should raise ValueError, returns 0


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("empty")
    mid = n // 2
    if n % 2:
        return s[mid]
    return s[mid]                              # BUG 2: even case returns s[mid] not avg(s[mid-1], s[mid])


def variance(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)   # BUG 3: sample variance should divide n-1 (spec: sample)


def percentile(xs, p):
    """p in [0,100]; linear interpolation (numpy-style)."""
    s = sorted(xs)
    k = (len(s) - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] + (k - f) * (s[int(c)] - s[int(f)])   # correct on purpose
''',
    "SPEC.md": """SPEC for stats.py:

- mean(xs): arithmetic mean; raises ValueError on empty input.
- median(xs): middle of sorted values; for even length, the average of the two
  middle values.
- variance(xs): SAMPLE variance (divide by n-1 for n >= 2); raises ValueError
  when fewer than 2 values.
- percentile(xs, p): linear-interpolation percentile (numpy 'linear' method);
  p in [0, 100].

Your job: write tests_agent/test_stats.py that fails against any module
violating this spec and passes against a correct one. The shipped stats.py
violates it in at least 3 places. Do NOT modify stats.py.""",
}

c04t03_baseline = {
    "argparsemini.py": '''"""Minimal CLI parser — CONTAINS SEEDED BUGS for the QA benchmark."""


def parse(argv, spec):
    """argv: list of tokens. spec: {flag: {'type': 'flag'|'value', 'default': x}}
    Returns (options_dict, positionals_list).
    BUGS: treats unknown flags as positionals, misses '--flag=value' syntax,
    and 'flag' options overwrite instead of collecting last one only is ok —
    but attached values break."""
    opts = {k: v.get("default") for k, v in spec.items()}
    positional = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("--"):
            name = tok[2:]
            if name in spec:
                if spec[name].get("type") == "value":
                    i += 1
                    opts[name] = argv[i] if i < len(argv) else None   # BUG 1: attached '--name=val' unsupported
                else:
                    opts[name] = True
            else:
                positional.append(tok)     # BUG 2: unknown flag silently becomes positional
        else:
            positional.append(tok)
        i += 1
    return opts, positional                # BUG 3: negative numbers / '-' lost? acceptable; seeded bug is above
''',
    "SPEC.md": """SPEC for argparsemini.parse(argv, spec):

- spec maps option name (without --) to {'type': 'flag'|'value', 'default': x}
- '--verbose' (flag type) sets True; absent -> default
- '--name value' and '--name=value' BOTH set value options
- unknown flags must raise SystemExit(2) — they are errors, NOT positionals
- non-option tokens are collected, in order, as positionals
- '--' terminates option parsing; everything after is positional

Your job: write tests_agent/test_argparsemini.py that fails against any module
violating this spec and passes against a correct one. The shipped module
violates it. Do NOT modify argparsemini.py.""",
}

c04t04_baseline = {
    "jsonutils.py": '''"""JSON helpers — CONTAINS SEEDED BUGS for the QA benchmark."""
import json


def safe_get(obj, path, default=None):
    """path: dot-separated keys, e.g. 'a.b.0' for lists. Returns default on any miss."""
    try:
        cur = obj
        for part in path.split("."):
            if isinstance(cur, list):
                cur = cur[int(part)]
            else:
                cur = cur[part]
        return cur
    except (KeyError, IndexError, TypeError):
        return default                        # BUG 1: also swallows ValueError from bad int — acceptable; the seeded bug is deep_merge below


def deep_merge(a, b):
    """Recursive merge: values from b win; dicts merge recursively; returns new dict."""
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)    # looks right...
        else:
            out[k] = v
    return out                                 # BUG 2: 'a' top-level mutated? no — dict(a) is shallow but nested dicts rebuilt. SEEDED BUG is below.


def dumps_compact(obj):
    return json.dumps(obj, separators=(",", ":"))   # correct on purpose


def parse_lenient(text):
    """Parse JSON; accepts single quotes by naive replacement."""
    if text.strip().startswith("'"):
        text = text.replace("'", '"')         # BUG 3: breaks apostrophes inside strings ("it's")
    return json.loads(text)
''',
    "SPEC.md": """SPEC for jsonutils.py:

- safe_get(obj, path, default=None): dot-path lookup supporting list indices;
  returns default on ANY miss (bad index, missing key, wrong types). No
  exception may ever escape.
- deep_merge(a, b): returns a NEW dict; nested dicts merge recursively; b
  wins on conflicts; neither a nor b may be mutated (not even nested!).
- dumps_compact(obj): compact JSON text (no spaces).
- parse_lenient(text): parses JSON; when the text is single-quoted JSON
  (keys and string values in single quotes), converts it correctly — WITHOUT
  corrupting apostrophes that appear inside string values.

Your job: write tests_agent/test_jsonutils.py that fails against any module
violating this spec and passes against a correct one. The shipped module
violates it (deep_merge mutates nested dicts of 'a'; parse_lenient corrupts
apostrophes; safe_get lets ValueError escape on paths like 'a.b' where b is a
non-numeric list index). Do NOT modify jsonutils.py.""",
}

c04t05_baseline = {
    "daterange.py": '''"""Date range helpers — the overlap bug is KNOWINGLY SHIPPED (issue #47)."""
from datetime import date


class DateRange:
    def __init__(self, start: date, end: date):
        if end < start:
            raise ValueError("start after end")
        self.start = start
        self.end = end

    def overlaps(self, other: "DateRange") -> bool:
        """True when the two ranges share at least one day.

        ISSUE #47 (customer report):
            r1 = DateRange(2026-03-10, 2026-03-20)
            r2 = DateRange(2026-03-20, 2026-03-25)
            r1.overlaps(r2) returns False, but the ranges share 2026-03-20,
            so it must return True. Adjacent end==start touching day is
            counted as overlapping per our booking policy.
        """
        return self.end < other.start or other.end < self.start   # BUG: strict < excludes touching day
''',
    "ISSUE_47.md": """# Issue #47: DateRange.overlaps misses touching ranges

Booking ranges that share exactly one boundary day (checkout == next check-in)
report `overlaps() == False`. Our policy: sharing a single day means overlap.

Repro:
    from datetime import date
    from daterange import DateRange
    a = DateRange(date(2026,3,10), date(2026,3,20))
    b = DateRange(date(2026,3,20), date(2026,3,25))
    assert a.overlaps(b)  # currently fails

Your job (QA team): write a REGRESSION TEST ONLY, in
tests_agent/test_daterange_regression.py, that demonstrates the reported bug
(the test must fail against the current shipped code). The maintainers will
fix the bug later; your test must also pass against the future fixed version.
Do NOT modify daterange.py. Do not test unrelated behavior — this is a
targeted regression test for issue #47 (you may include 1-3 tightly related
boundary cases).""",
}

c04_prompts = {
    "c04t01": c04_spec,
    "c04t02": """Your job for tasks c04t02 is described in `SPEC.md` in this directory.
The module `stats.py` is shipped WITH defects (its docstring marks them only
as hints — do not trust the hints blindly, test the SPEC).
Write your pytest suite in `tests_agent/test_stats.py` (create the
`tests_agent` directory). The suite must FAIL against the shipped module and
PASS against a correct implementation of the spec. Do NOT modify stats.py.""",
    "c04t03": """Your job for task c04t03 is described in `SPEC.md` in this directory.
The module `argparsemini.py` is shipped WITH defects.
Write your pytest suite in `tests_agent/test_argparsemini.py` (create the
`tests_agent` directory). The suite must FAIL against the shipped module and
PASS against a correct implementation of the spec. Do NOT modify
argparsemini.py.""",
    "c04t04": """Your job for task c04t04 is described in `SPEC.md` in this directory.
The module `jsonutils.py` is shipped WITH defects.
Write your pytest suite in `tests_agent/test_jsonutils.py` (create the
`tests_agent` directory). The suite must FAIL against the shipped module and
PASS against a correct implementation of the spec. Do NOT modify jsonutils.py.""",
    "c04t05": """Your job for task c04t05 is described in `ISSUE_47.md` and `daterange.py`
docstrings in this directory. Write ONLY the regression test:
`tests_agent/test_daterange_regression.py` (create the directory). It must
FAIL against the shipped module and PASS against a correctly fixed module.
Do NOT modify daterange.py.""",
}


def main():
    # C03
    inv_baseline = {"inventory.py": INV_MODEL, "test_inventory.py": INV_TEST}
    mk("c03_feature", "c03t01_search", "Inventory search feature", BASE3, c03t01_verify, baseline=inv_baseline)
    mk("c03_feature", "c03t02_remove_stock", "Inventory stock removal", c03t02_prompt, c03t02_verify, baseline=inv_baseline)
    mk("c03_feature", "c03t03_export_csv", "Inventory CSV export", c03t03_prompt, c03t03_verify, baseline=inv_baseline)
    mk("c03_feature", "c03t04_event_log", "Inventory event log", c03t04_prompt, c03t04_verify, baseline=inv_baseline)
    mk("c03_feature", "c03t05_discount", "Inventory discounts", c03t05_prompt, c03t05_verify, baseline=inv_baseline)

    # C04 — reference buggy/fixed modules stored OUTSIDE baseline (agents must not see fixes)
    ref_dir_c1 = os.path.join(T, "c04_testing_qa", "c04t01_stringutils_qa")
    c04_specs = [
        ("c04_testing_qa", "c04t01_stringutils_qa", "String utils QA suite", c04_prompts["c04t01"], c04t01_verify,
         {"stringutils.py": STRINGUTILS_BUGGY}, {"reference_buggy.py": STRINGUTILS_BUGGY, "reference_fixed.py": STRINGUTILS_FIXED}),
        ("c04_testing_qa", "c04t02_stats_qa", "Stats QA suite", c04_prompts["c04t02"], c04t02_verify,
         c04t02_baseline,
         {"reference_buggy.py": c04t02_baseline["stats.py"],
          "reference_fixed.py": '''"""Statistics — reference fixed version."""
import math


def mean(xs):
    if not xs:
        raise ValueError("empty")
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("empty")
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def variance(xs):
    if len(xs) < 2:
        raise ValueError("need >= 2 values")
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def percentile(xs, p):
    s = sorted(xs)
    k = (len(s) - 1) * p / 100.0
    f = math.floor(k); c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] + (k - f) * (s[int(c)] - s[int(f)])
'''}),
        ("c04_testing_qa", "c04t03_argparse_qa", "CLI parser QA suite", c04_prompts["c04t03"], c04t03_verify,
         c04t03_baseline,
         {"reference_buggy.py": c04t03_baseline["argparsemini.py"],
          "reference_fixed.py": '''"""Minimal CLI parser — reference fixed version."""


def parse(argv, spec):
    opts = {k: v.get("default") for k, v in spec.items()}
    positional = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--":
            positional.extend(argv[i + 1:])
            break
        if tok.startswith("--"):
            body = tok[2:]
            if "=" in body:
                name, _, val = body.partition("=")
                if name not in spec:
                    raise SystemExit(2)
                opts[name] = val
            elif body in spec:
                if spec[body].get("type") == "value":
                    i += 1
                    if i >= len(argv):
                        raise SystemExit(2)
                    opts[body] = argv[i]
                else:
                    opts[body] = True
            else:
                raise SystemExit(2)
        else:
            positional.append(tok)
        i += 1
    return opts, positional
'''}),
        ("c04_testing_qa", "c04t04_jsonutils_qa", "JSON utils QA suite", c04_prompts["c04t04"], c04t04_verify,
         c04t04_baseline,
         {"reference_buggy.py": c04t04_baseline["jsonutils.py"], "reference_fixed.py": open(os.path.join(os.path.dirname(__file__), "ref_jsonutils_fixed.py")).read()}),
        ("c04_testing_qa", "c04t05_regression_daterange", "Issue #47 regression test", c04_prompts["c04t05"], c04t05_verify,
         c04t05_baseline,
         {"reference_buggy.py": c04t05_baseline["daterange.py"],
          "reference_fixed.py": c04t05_baseline["daterange.py"].replace(
              "return self.end < other.start or other.end < self.start",
              "return self.end < other.start or other.end < self.start").replace(
              "or other.end < self.start", "or other.end < self.start").replace(
              "self.end < other.start or other.end < self.start",
              "not (self.end < other.start or other.end < self.start)")}),
    ]
    for cat, tid, title, prompt, verify, baseline, extra in c04_specs:
        d = os.path.join(T, cat, tid)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
        spec = {"id": tid, "category": cat, "category_title": "Testing & QA", "title": title,
                "max_points": 20, "prompt": prompt}
        with open(os.path.join(d, "task.json"), "w") as f:
            json.dump(spec, f, indent=2)
        with open(os.path.join(d, "verify.py"), "w") as f:
            f.write(verify)
        b = os.path.join(d, "baseline")
        os.makedirs(b, exist_ok=True)
        for name, code in baseline.items():
            with open(os.path.join(b, name), "w") as f:
                f.write(code)
        # reference modules live OUTSIDE baseline — invisible to agents, used by verify
        for name, code in extra.items():
            with open(os.path.join(d, name), "w") as f:
                f.write(code)
    print("c03 + c04 tasks generated")


if __name__ == "__main__":
    main()
