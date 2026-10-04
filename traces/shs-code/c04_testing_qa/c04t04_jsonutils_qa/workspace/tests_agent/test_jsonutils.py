"""Pytest suite for jsonutils.py per SPEC.md.

Every test PASSES against a correct implementation of the spec and FAILS
against the shipped (defective) module. The shipped module is imported via
sys.path so the suite runs against the real on-disk module.

Defect classes covered (per SPEC.md):
  D1  safe_get lets an exception escape (e.g. ValueError from a bad int() on
      a non-numeric path segment) instead of returning the default.
  D2  deep_merge aliases nested dict objects with 'a' / 'b' — the result is
      not fully independent of its inputs (mutating the result mutates inputs).
  D3  parse_lenient corrupts apostrophes inside string values when converting
      single-quoted JSON (naive quote replacement).
"""
import copy
import json
import os
import sys

import pytest

# Ensure the module under test is importable from the project root.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import jsonutils  # noqa: E402  (shipped, defective module under test)


def _no_escape(fn):
    """Call fn; surface any escaped exception as a pytest failure.

    Spec: 'No exception may ever escape.' A correct implementation must never
    raise. We convert an escaped exception into a clear assertion failure so
    the result is meaningful instead of a raw error.
    """
    try:
        return fn()
    except Exception as exc:  # broad catch is intentional (spec forbids any)
        pytest.fail(f"an exception escaped from the function under test: {exc!r}")


# ---------------------------------------------------------------------------
# safe_get
# ---------------------------------------------------------------------------
def test_safe_get_nested_hit():
    obj = {"a": {"b": {"c": 42}}}
    assert jsonutils.safe_get(obj, "a.b.c") == 42


def test_safe_get_list_index_hit():
    obj = {"a": [10, 20, 30]}
    assert jsonutils.safe_get(obj, "a.1") == 20
    assert jsonutils.safe_get(obj, "a.2") == 30


def test_safe_get_deep_list_hit():
    obj = {"x": {"y": [[1, 2], [3, 4]]}}
    assert jsonutils.safe_get(obj, "x.y.1.0") == 3


def test_safe_get_negative_list_index():
    # -1 is a valid Python list index; a correct impl supports it.
    obj = {"a": [1, 2, 3]}
    assert jsonutils.safe_get(obj, "a.-1") == 3


def test_safe_get_missing_key_returns_default():
    obj = {"a": 1}
    assert jsonutils.safe_get(obj, "b", "DEFAULT") == "DEFAULT"


def test_safe_get_out_of_range_list_index_returns_default():
    obj = {"a": [1, 2, 3]}
    assert jsonutils.safe_get(obj, "a.99", "DEF") == "DEF"


def test_safe_get_default_none_when_omitted():
    obj = {}
    assert jsonutils.safe_get(obj, "x.y") is None


def test_safe_get_bad_list_index_part_returns_default_not_raises():
    # D1: segment 'b' is not a numeric index into a list. Spec: return the
    # default on ANY miss, never raise. Shipped module raises ValueError.
    obj = {"a": [1, 2, 3]}
    _no_escape(lambda: jsonutils.safe_get(obj, "a.b", "MISS"))
    assert jsonutils.safe_get(obj, "a.b", "MISS") == "MISS"


def test_safe_get_non_numeric_part_on_dict_never_raises():
    obj = {"a": {"b": 1}}
    _no_escape(lambda: jsonutils.safe_get(obj, "a.zzz", "MISS"))
    assert jsonutils.safe_get(obj, "a.zzz", "MISS") == "MISS"


def test_safe_get_traverse_non_container_never_raises():
    # Traversing through a non-container (int) must return the default.
    obj = {"a": 5}
    _no_escape(lambda: jsonutils.safe_get(obj, "a.0", "MISS"))
    assert jsonutils.safe_get(obj, "a.0", "MISS") == "MISS"


def test_safe_get_nested_lists_bad_part_never_raises():
    obj = {"a": [[1, 2], [3, 4]]}
    _no_escape(lambda: jsonutils.safe_get(obj, "a.0.9", "MISS"))
    assert jsonutils.safe_get(obj, "a.0.9", "MISS") == "MISS"


def test_safe_get_root_not_container_never_raises():
    _no_escape(lambda: jsonutils.safe_get(42, "a.b", "MISS"))
    assert jsonutils.safe_get(42, "a.b", "MISS") == "MISS"


def test_safe_get_none_input_never_raises():
    _no_escape(lambda: jsonutils.safe_get(None, "a", "MISS"))
    assert jsonutils.safe_get(None, "a", "MISS") == "MISS"


def test_safe_get_string_input_never_raises():
    _no_escape(lambda: jsonutils.safe_get("abc", "a.b", "MISS"))
    assert jsonutils.safe_get("abc", "a.b", "MISS") == "MISS"


# ---------------------------------------------------------------------------
# deep_merge
# ---------------------------------------------------------------------------
def test_deep_merge_top_level_conflict_b_wins():
    assert jsonutils.deep_merge({"k": 1}, {"k": 2}) == {"k": 2}


def test_deep_merge_returns_new_dict_not_input():
    a, b = {"x": 1}, {"y": 2}
    out = jsonutils.deep_merge(a, b)
    assert out is not a
    assert out is not b


def test_deep_merge_union_of_keys():
    assert jsonutils.deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_deep_merge_nested_recursive_merge():
    a = {"n": {"x": 1, "z": 9}, "top": "A"}
    b = {"n": {"y": 3}, "top": "B"}
    assert jsonutils.deep_merge(a, b) == {"n": {"x": 1, "z": 9, "y": 3}, "top": "B"}


def test_deep_merge_does_not_mutate_a_top_level():
    a = {"n": {"x": 1}}
    a_snap = copy.deepcopy(a)
    jsonutils.deep_merge(a, {"n": {"y": 2}})
    assert a == a_snap, "deep_merge mutated its 'a' argument"


def test_deep_merge_does_not_mutate_b_top_level():
    b = {"n": {"y": 2}}
    b_snap = copy.deepcopy(b)
    jsonutils.deep_merge({"n": {"x": 1}}, b)
    assert b == b_snap, "deep_merge mutated its 'b' argument"


def test_deep_merge_result_independent_of_a_nested():
    # D2: the returned dict must NOT share nested dict objects with 'a'.
    a = {"keep": {"inner": 1}, "conflict": {"inner": 10}}
    a_snap = copy.deepcopy(a)
    out = jsonutils.deep_merge(a, {"conflict": {"inner": 20}})
    out["keep"]["inner"] = 999
    out["conflict"]["inner"] = 999
    assert a == a_snap, "result aliases nested dicts of 'a' (mutating result mutated 'a')"


def test_deep_merge_result_independent_of_b_nested():
    # The returned dict must NOT share nested dict objects with 'b'.
    b = {"keep": {"inner": 5}}
    b_snap = copy.deepcopy(b)
    out = jsonutils.deep_merge({}, b)
    out["keep"]["inner"] = 12345
    assert b == b_snap, "result aliases nested dicts of 'b'"


def test_deep_merge_result_independent_at_depth3():
    a = {"l1": {"l2": {"l3": [1]}}}
    a_snap = copy.deepcopy(a)
    out = jsonutils.deep_merge(a, {})
    out["l1"]["l2"]["l3"].append(99)
    assert a == a_snap, "result aliases deeply nested structures of 'a'"


def test_deep_merge_nested_dict_vs_scalar_b_wins():
    assert jsonutils.deep_merge({"k": {"a": 1}}, {"k": "scalar"}) == {"k": "scalar"}


def test_deep_merge_scalar_vs_nested_dict_b_wins():
    assert jsonutils.deep_merge({"k": "scalar"}, {"k": {"a": 1}}) == {"k": {"a": 1}}


# ---------------------------------------------------------------------------
# dumps_compact
# ---------------------------------------------------------------------------
def test_dumps_compact_no_spaces():
    obj = {"a": [1, 2], "b": {"c": 3}}
    out = jsonutils.dumps_compact(obj)
    assert out == json.dumps(obj, separators=(",", ":"))
    assert " " not in out


def test_dumps_compact_round_trips():
    obj = {"x": 1, "y": [1, 2, 3]}
    assert json.loads(jsonutils.dumps_compact(obj)) == obj


def test_dumps_compact_empty_structures():
    assert jsonutils.dumps_compact({}) == "{}"
    assert jsonutils.dumps_compact([]) == "[]"


# ---------------------------------------------------------------------------
# parse_lenient
# ---------------------------------------------------------------------------
def test_parse_lenient_standard_double_quoted_json():
    # Regression: ordinary JSON must still parse.
    assert jsonutils.parse_lenient('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}


def test_parse_lenient_single_quoted_keys():
    # Lenient mode: single-quoted keys must be accepted.
    assert jsonutils.parse_lenient("{'a': 1, 'b': 2}") == {"a": 1, "b": 2}


def test_parse_lenient_single_quoted_string_values():
    assert jsonutils.parse_lenient("{'name': 'shs'}") == {"name": "shs"}


def test_parse_lenient_list_single_quoted():
    assert jsonutils.parse_lenient("['apple', 'banana', 'cherry']") == ["apple", "banana", "cherry"]


def test_parse_lenient_nested_single_quoted():
    assert jsonutils.parse_lenient("{'outer': {'inner': 'ok'}}") == {"outer": {"inner": "ok"}}


def test_parse_lenient_apostrophe_in_value_not_corrupted():
    # D3 (core): value contains an apostrophe. The correct parser must yield
    # it intact; the shipped naive replace() mangles it.
    text = "{'msg': \"don't stop\"}"
    assert jsonutils.parse_lenient(text) == {"msg": "don't stop"}


def test_parse_lenient_apostrophe_in_double_quoted_value_with_single_quoted_key():
    # Key single-quoted, value double-quoted containing an apostrophe.
    text = "{'a': \"rock 'n roll\"}"
    assert jsonutils.parse_lenient(text) == {"a": "rock 'n roll"}


def test_parse_lenient_double_quoted_apostrophes_untouched():
    # Standard JSON whose values contain apostrophes must parse untouched.
    text = '{\'a\': "rock \'n roll"}'
    assert jsonutils.parse_lenient(text) == {"a": "rock 'n roll"}


def test_parse_lenient_invalid_json_raises():
    # Genuinely broken JSON must still raise.
    with pytest.raises((json.JSONDecodeError, ValueError)):
        jsonutils.parse_lenient("{not json")


# ---------------------------------------------------------------------------
# Sanity: module exposes the four documented callables
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", [
    "safe_get", "deep_merge", "dumps_compact", "parse_lenient",
])
def test_surface_callable_present(name):
    assert callable(getattr(jsonutils, name, None)), f"{name} missing"
