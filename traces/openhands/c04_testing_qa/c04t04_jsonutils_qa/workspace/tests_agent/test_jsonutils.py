"""QA tests for jsonutils.py against SPEC.md.

Run from the directory containing jsonutils.py:
    python -m pytest tests_agent/test_jsonutils.py
"""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jsonutils


# ---------------------------------------------------------------------------
# safe_get
# ---------------------------------------------------------------------------

def test_safe_get_basic_dict_path():
    assert jsonutils.safe_get({"a": {"b": 1}}, "a.b") == 1


def test_safe_get_list_index():
    assert jsonutils.safe_get({"a": [10, 20]}, "a.1") == 20


def test_safe_get_missing_key_returns_default():
    assert jsonutils.safe_get({"a": 1}, "b", "dflt") == "dflt"


def test_safe_get_out_of_range_index_returns_default():
    assert jsonutils.safe_get({"a": [1, 2]}, "a.99", -1) == -1


def test_safe_get_non_numeric_index_on_list_returns_default_not_raise():
    # SPEC: "returns default on ANY miss (bad index, missing key, wrong
    # types). No exception may ever escape."
    # The shipped module lets ValueError escape from int("b").
    assert jsonutils.safe_get({"a": [1, 2]}, "a.b", "MISS") == "MISS"


def test_safe_get_indexing_a_string_returns_default_not_raise():
    # Wrong type: path tries to index a non-list, non-dict value.
    assert jsonutils.safe_get({"a": "str"}, "a.0", "MISS") == "MISS"


def test_safe_get_deep_miss_returns_default_not_raise():
    assert jsonutils.safe_get({"a": {"b": 1}}, "a.b.c", "MISS") == "MISS"


def test_safe_get_no_default_is_none():
    assert jsonutils.safe_get({"a": 1}, "nope") is None


# ---------------------------------------------------------------------------
# deep_merge
# ---------------------------------------------------------------------------

def test_deep_merge_returns_new_dict():
    a = {"x": 1}
    b = {"y": 2}
    result = jsonutils.deep_merge(a, b)
    assert result is not a
    assert result is not b
    assert result == {"x": 1, "y": 2}


def test_deep_merge_b_wins_on_conflict():
    a = {"k": 1, "nested": {"n": 1}}
    b = {"k": 2, "nested": {"n": 3, "m": 5}}
    result = jsonutils.deep_merge(a, b)
    assert result == {"k": 2, "nested": {"n": 3, "m": 5}}


def test_deep_merge_does_not_mutate_a_nested():
    # SPEC: "neither a nor b may be mutated (not even nested!)."
    a = {"x": {"y": 1}}
    a_snapshot = copy.deepcopy(a)
    result = jsonutils.deep_merge(a, {"z": 2})
    assert a == a_snapshot, "deep_merge mutated 'a' or shares its nested dict"
    # Mutating the result must not affect 'a' (i.e. nested must be copied).
    result["x"]["y"] = 999
    assert a == a_snapshot, "result shares 'a's nested dict; mutating result mutated a"


def test_deep_merge_does_not_mutate_b_nested():
    b = {"x": {"y": 1}}
    b_snapshot = copy.deepcopy(b)
    jsonutils.deep_merge({"x": {"z": 0}}, b)
    assert b == b_snapshot, "deep_merge mutated 'b' or shares its nested dict"


def test_deep_merge_multiple_nested_levels():
    a = {"l1": {"l2": {"v": 1}, "keep": 7}}
    b = {"l1": {"l2": {"v": 2, "w": 3}}}
    a_snapshot = copy.deepcopy(a)
    b_snapshot = copy.deepcopy(b)
    result = jsonutils.deep_merge(a, b)
    assert result == {"l1": {"l2": {"v": 2, "w": 3}, "keep": 7}}
    assert a == a_snapshot and b == b_snapshot


def test_deep_merge_non_dict_replacement():
    a = {"k": {"n": 1}}
    b = {"k": "scalar"}
    assert jsonutils.deep_merge(a, b) == {"k": "scalar"}


# ---------------------------------------------------------------------------
# dumps_compact
# ---------------------------------------------------------------------------

def test_dumps_compact_no_spaces():
    obj = {"a": [1, 2], "b": {"c": 3}}
    out = jsonutils.dumps_compact(obj)
    assert out == json.dumps(obj, separators=(",", ":"))
    assert " " not in out


def test_dumps_compact_round_trip():
    obj = {"x": 1, "y": [True, None, "s"]}
    assert json.loads(jsonutils.dumps_compact(obj)) == obj


# ---------------------------------------------------------------------------
# parse_lenient
# ---------------------------------------------------------------------------

def test_parse_lenient_plain_double_quoted_json():
    assert jsonutils.parse_lenient('{"a": 1}') == {"a": 1}


def test_parse_lenient_single_quoted_object():
    # SPEC: "when the text is single-quoted JSON (keys and string values in
    # single quotes), converts it correctly".
    assert jsonutils.parse_lenient("{'a': 'b'}") == {"a": "b"}


def test_parse_lenient_single_quoted_nested():
    text = "{'a': {'b': 'c', 'n': 1}}"
    assert jsonutils.parse_lenient(text) == {"a": {"b": "c", "n": 1}}


def test_parse_lenient_does_not_corrupt_apostrophes_in_values():
    # A double-quoted string value containing an apostrophe must survive
    # intact. A naive global ' -> " replacement mangles these.
    text = "{'msg': 'don\"' + chr(39) + 't panic'}"
    result = jsonutils.parse_lenient(text)
    assert result == {"msg": "don" + chr(39) + "t panic"}


def test_parse_lenient_apostrophe_in_double_quoted_value_not_duplicated():
    # Apostrophes inside single-quoted string values must be preserved,
    # not duplicated or corrupted by the quote conversion.
    text = "{'tag': 'a', 'msg': 'x" + chr(39) + "y'}"
    result = jsonutils.parse_lenient(text)
    assert result == {"tag": "a", "msg": "x" + chr(39) + "y"}


if __name__ == "__main__":
    sys.exit(pytest.main([os.path.abspath(__file__), "-v"]))
