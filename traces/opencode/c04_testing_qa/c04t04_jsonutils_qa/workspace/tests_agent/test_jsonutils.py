import sys
from pathlib import Path

import jsonutils


# --- safe_get ---

class TestSafeGet:
    def test_basic_key(self):
        assert jsonutils.safe_get({"a": 1}, "a") == 1

    def test_nested_key(self):
        assert jsonutils.safe_get({"a": {"b": 2}}, "a.b") == 2

    def test_list_index(self):
        assert jsonutils.safe_get({"a": [10, 20]}, "a.1") == 20

    def test_missing_key_returns_default(self):
        assert jsonutils.safe_get({"a": 1}, "b", 42) == 42

    def test_missing_key_returns_none_default(self):
        assert jsonutils.safe_get({}, "x") is None

    def test_bad_index_returns_default_no_escape(self):
        # 'a.b' where b resolves into a non-numeric list index:
        # int("b") raises ValueError; the shipped code does NOT catch it.
        obj = {"a": [1, 2, 3]}
        assert jsonutils.safe_get(obj, "a.b", "DEF") == "DEF"

    def test_out_of_range_index_returns_default(self):
        obj = {"a": [1]}
        assert jsonutils.safe_get(obj, "a.5", "DEF") == "DEF"

    def test_wrong_type_lookup_returns_default(self):
        assert jsonutils.safe_get({"a": 42}, "a.b", "DEF") == "DEF"

    def test_bad_list_index_no_exception(self):
        # 'a.abc' where the list segment is not a valid int must not raise;
        # it must simply return the default. The shipped code lets
        # ValueError escape from int(part) because it is not caught.
        result = jsonutils.safe_get({"a": [1]}, "a.abc", "DEF")
        assert result == "DEF"


# --- deep_merge ---

class TestDeepMerge:
    def test_b_wins_on_conflict(self):
        assert jsonutils.deep_merge({"a": 1}, {"a": 2}) == {"a": 2}

    def test_nested_dict_merges(self):
        a = {"x": {"p": 1, "q": 2}}
        b = {"x": {"q": 3}}
        assert jsonutils.deep_merge(a, b) == {"x": {"p": 1, "q": 3}}

    def test_returns_new_dict_not_a(self):
        a = {"k": "v"}
        b = {"z": 1}
        result = jsonutils.deep_merge(a, b)
        assert result is not a
        assert result is not b

    def test_does_not_mutate_a_top_level(self):
        a = {"k": "v"}
        b = {"new": 1}
        jsonutils.deep_merge(a, b)
        assert a == {"k": "v"}

    def test_does_not_mutate_a_nested(self):
        a = {"outer": {"inner": 1}}
        b = {"outer": {"new": 2}}
        jsonutils.deep_merge(a, b)
        assert a == {"outer": {"inner": 1}}, "a was mutated: nested dict changed"

    def test_does_not_mutate_b_nested(self):
        a = {"outer": {"inner": 1}}
        b = {"outer": {"new": 2}}
        jsonutils.deep_merge(a, b)
        assert b == {"outer": {"new": 2}}, "b was mutated"

    def test_deeply_nested_no_mutation(self):
        a = {"l1": {"l2": {"l3": 1}}}
        b = {"l1": {"l2": {"new": 2}}}
        jsonutils.deep_merge(a, b)
        assert a == {"l1": {"l2": {"l3": 1}}}, "a was mutated deep"
        assert b == {"l1": {"l2": {"new": 2}}}, "b was mutated deep"


# --- dumps_compact ---

class TestDumpsCompact:
    def test_no_spaces(self):
        assert jsonutils.dumps_compact({"a": 1, "b": 2}) == '{"a":1,"b":2}'

    def test_nested(self):
        assert jsonutils.dumps_compact({"a": {"b": [1, 2]}}) == '{"a":{"b":[1,2]}}'

    def test_empty(self):
        assert jsonutils.dumps_compact({}) == "{}"

    def test_unicode_no_ascii_escape(self):
        result = jsonutils.dumps_compact({"k": "café"})
        assert "é" in result or "\\u00e9" in result


# --- parse_lenient ---

class TestParseLenient:
    def test_valid_json(self):
        assert jsonutils.parse_lenient('{"a": 1}') == {"a": 1}

    def test_single_quoted_keys(self):
        assert jsonutils.parse_lenient("{'name': 'Alice'}") == {"name": "Alice"}

    def test_single_quoted_string_value(self):
        assert jsonutils.parse_lenient("{'greeting': 'hello'}") == {"greeting": "hello"}

    def test_apostrophe_in_string_value_not_corrupted(self):
        # The shipped replace("'", '"') corrupts "it's" into "it"s".
        text = "{'msg': 'it\\'s fine'}"
        result = jsonutils.parse_lenient(text)
        assert result == {"msg": "it's fine"}, (
            f"apostrophe corrupted: got {result!r}"
        )

    def test_apostrophe_inside_double_quoted_value(self):
        # A correctly-escaped single-quote JSON should parse as-is.
        text = '{"msg": "it\'s fine"}'
        assert jsonutils.parse_lenient(text) == {"msg": "it's fine"}

    def test_nested_single_quoted(self):
        text = "{'a': {'b': 'c'}, 'd': [1, 2]}"
        assert jsonutils.parse_lenient(text) == {"a": {"b": "c"}, "d": [1, 2]}
