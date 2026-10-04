"""QA test suite for jsonutils.py (SPEC.md).

Invariants under test:
  - safe_get(obj, path, default=None): dot-path lookup, supports list indices;
    returns `default` on ANY miss (bad index, missing key, wrong type). No
    exception may ever escape.
  - deep_merge(a, b): returns a NEW dict; nested dicts merge recursively; b wins
    on conflicts; NEITHER a NOR b is mutated (not even nested). The result is
    fully independent of both inputs.
  - dumps_compact(obj): compact JSON text (no whitespace between tokens).
  - parse_lenient(text): parses JSON; single-quoted JSON is converted correctly
    WITHOUT corrupting apostrophes that appear inside string values.

The shipped jsonutils.py is defective and this suite must FAIL against it.
The module lives in the project root (parent of tests_agent/), so the parent
dir is added to sys.path to keep `import jsonutils` independent of the cwd
pytest is launched from.
"""

import copy
import os
import sys

import pytest

# Resolve the project-root jsonutils regardless of pytest's launch directory.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import jsonutils as j  # noqa: E402


def capture(fn, *args, **kwargs):
    """Call fn(*args, **kwargs) -> (result, exception_or_None).

    Lets us assert explicitly that NO exception escaped, which the spec
    requires for safe_get and parse_lenient.
    """
    try:
        return fn(*args, **kwargs), None
    except Exception as exc:  # spec: no exception may escape
        return None, exc


# --------------------------------------------------------------------------- #
# safe_get
# --------------------------------------------------------------------------- #
class TestSafeGet:
    def test_hit_dict_path(self):
        assert j.safe_get({"a": {"b": {"c": 7}}}, "a.b.c") == 7

    def test_hit_list_index(self):
        assert j.safe_get({"a": {"b": [10, 20, 30]}}, "a.b.1") == 20

    def test_hit_negative_list_index(self):
        assert j.safe_get({"a": [1, 2, 3]}, "a.-1") == 3

    def test_missing_key_returns_default(self):
        assert j.safe_get({"a": 1}, "a.b.c", "MISS") == "MISS"

    def test_out_of_range_list_returns_default(self):
        assert j.safe_get({"l": [1]}, "l.5", "MISS") == "MISS"

    def test_none_key_lookup_on_dict(self):
        # A dict key that looks numeric must be treated as a key, not an index.
        assert j.safe_get({"0": "zero"}, "0") == "zero"

    # --- seeded bug 1: bad / non-numeric list index must NOT leak --------- #
    def test_non_numeric_index_on_list_returns_default_no_throw(self):
        result, exc = capture(j.safe_get, {"a": [1, 2]}, "a.b", "MISS")
        assert exc is None, f"safe_get leaked exception {exc!r} on bad list index"
        assert result == "MISS"

    def test_garbage_index_on_list_returns_default_no_throw(self):
        result, exc = capture(j.safe_get, {"a": [1, 2]}, "a.1x", "MISS")
        assert exc is None, f"safe_get leaked exception {exc!r} on garbage index"
        assert result == "MISS"

    def test_none_path_returns_default_no_throw(self):
        # A path of the wrong type is still a miss -> default, never an exception.
        result, exc = capture(j.safe_get, {"a": 1}, None, "MISS")
        assert exc is None, f"safe_get leaked exception {exc!r} on None path"
        assert result == "MISS"

    def test_index_on_dict_returns_default_no_throw(self):
        result, exc = capture(j.safe_get, {"a": {"b": 1}}, "a.2", "MISS")
        assert exc is None, f"safe_get leaked exception {exc!r} on index-on-dict"
        assert result == "MISS"


# --------------------------------------------------------------------------- #
# deep_merge
# --------------------------------------------------------------------------- #
class TestDeepMerge:
    def test_flat_merge_b_wins(self):
        assert j.deep_merge({"a": 1, "x": 1}, {"x": 2, "b": 3}) == {
            "a": 1, "x": 2, "b": 3
        }

    def test_nested_dict_merges_recursively(self):
        assert j.deep_merge({"x": {"y": 1}}, {"x": {"w": 2}}) == {"x": {"y": 1, "w": 2}}

    def test_deep_three_level_merge(self):
        assert j.deep_merge({"a": {"b": {"c": 1}}}, {"a": {"b": {"d": 2}}}) == {
            "a": {"b": {"c": 1, "d": 2}}
        }

    def test_nested_b_wins_within_shared_key(self):
        assert j.deep_merge({"x": {"k": 1, "only_a": 5}}, {"x": {"k": 2}}) == {
            "x": {"k": 2, "only_a": 5}
        }

    def test_non_dict_b_overwrites_dict_a(self):
        assert j.deep_merge({"x": {"a": 1}}, {"x": 5}) == {"x": 5}

    def test_returns_a_new_dict(self):
        a = {"x": 1}
        b = {"y": 2}
        res = j.deep_merge(a, b)
        assert isinstance(res, dict)
        assert res is not a
        assert res is not b
        assert res == {"x": 1, "y": 2}

    def test_inputs_not_mutated_during_call(self):
        a = {"x": {"y": 1}}
        b = {"x": {"w": 2}}
        snap_a, snap_b = copy.deepcopy(a), copy.deepcopy(b)
        j.deep_merge(a, b)
        assert a == snap_a, "deep_merge mutated input 'a'"
        assert b == snap_b, "deep_merge mutated input 'b'"

    # --- seeded bug 2: result must NOT alias nested dicts of a or b ------ #
    def test_result_not_aliased_with_a_nested(self):
        a = {"x": {"y": 1}}
        res = j.deep_merge(a, {})
        res["x"]["z"] = 99  # mutate the *result*, not 'a'
        assert a == {"x": {"y": 1}}, (
            f"mutating the result changed input 'a' (a is now {a!r}); "
            "deep_merge must return a fully independent dict"
        )

    def test_result_not_aliased_with_b_nested(self):
        b = {"x": {"y": 1}}
        res = j.deep_merge({}, b)
        res["x"]["z"] = 99
        assert b == {"x": {"y": 1}}, (
            f"mutating the result changed input 'b' (b is now {b!r}); "
            "deep_merge must return a fully independent dict"
        )


# --------------------------------------------------------------------------- #
# dumps_compact
# --------------------------------------------------------------------------- #
class TestDumpsCompact:
    def test_no_spaces_top_level(self):
        assert j.dumps_compact({"a": 1, "b": [2, 3]}) == '{"a":1,"b":[2,3]}'

    def test_no_spaces_nested(self):
        assert j.dumps_compact({"x": {"y": [1, 2], "z": "s"}}) == '{"x":{"y":[1,2],"z":"s"}}'

    def test_output_has_no_whitespace(self):
        out = j.dumps_compact({"a": 1, "b": [2, 3]})
        assert " " not in out, f"dumps_compact output contains whitespace: {out!r}"

    def test_roundtrip_preserves_value(self):
        import json

        obj = {"a": 1, "b": [1, 2, {"c": None, "d": False}]}
        assert json.loads(j.dumps_compact(obj)) == obj

    def test_empty_containers(self):
        import json

        assert json.loads(j.dumps_compact({})) == {}
        assert json.loads(j.dumps_compact([])) == []


# --------------------------------------------------------------------------- #
# parse_lenient
# --------------------------------------------------------------------------- #
class TestParseLenient:
    def test_plain_json_parses(self):
        assert j.parse_lenient('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}

    # --- seeded bug 3: single-quoted JSON must convert, apostrophes intact #
    def test_single_quoted_object_parses(self):
        result, exc = capture(j.parse_lenient, "{'a': 'b', 'c': 1}")
        assert exc is None, f"parse_lenient failed on single-quoted JSON: {exc!r}"
        assert result == {"a": "b", "c": 1}

    def test_single_quoted_nested_parses(self):
        result, exc = capture(j.parse_lenient, "{'a': {'b': 'c'}, 'd': 1}")
        assert exc is None, f"parse_lenient failed on nested single-quoted JSON: {exc!r}"
        assert result == {"a": {"b": "c"}, "d": 1}

    def test_single_quoted_keys_with_scalar_literals(self):
        result, exc = capture(j.parse_lenient, "{'flag': true, 'n': 3.5, 'z': null}")
        assert exc is None, f"parse_lenient failed: {exc!r}"
        assert result == {"flag": True, "n": 3.5, "z": None}

    def test_apostrophe_inside_double_quoted_value_preserved(self):
        # Document is valid JSON; apostrophe inside a double-quoted value
        # must survive verbatim.
        result, exc = capture(j.parse_lenient, '{"key": "it\'s fine"}')
        assert exc is None, f"parse_lenient broke valid JSON: {exc!r}"
        assert result == {"key": "it's fine"}, f"apostrophe was corrupted: {result!r}"

    def test_single_quoted_key_with_apostrophe_value_preserved(self):
        # Mixed: single-quoted key + double-quoted value containing an
        # apostrophe. Must parse AND keep the apostrophe intact.
        result, exc = capture(j.parse_lenient, "{'key': \"it's fine\"}")
        assert exc is None, f"parse_lenient failed on apostrophe value: {exc!r}"
        assert result == {"key": "it's fine"}, f"apostrophe was corrupted: {result!r}"

    def test_plain_json_with_apostrophe_roundtrips(self):
        assert j.parse_lenient('{"msg": "rock \'n\' roll"}') == {"msg": "rock 'n' roll"}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
