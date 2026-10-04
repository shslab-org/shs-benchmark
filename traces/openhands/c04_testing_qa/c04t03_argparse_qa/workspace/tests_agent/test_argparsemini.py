"""QA tests for argparsemini.parse against SPEC.md.

Expected to FAIL against the shipped (buggy) module and PASS against a
correct implementation of the spec.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparsemini


SPEC = {
    "verbose": {"type": "flag", "default": False},
    "dry-run": {"type": "flag", "default": False},
    "name": {"type": "value", "default": "anon"},
    "count": {"type": "value", "default": 0},
}


def test_flag_sets_true():
    opts, pos = argparsemini.parse(["--verbose"], SPEC)
    assert opts["verbose"] is True


def test_flag_absent_uses_default():
    opts, _ = argparsemini.parse([], SPEC)
    assert opts["verbose"] is False
    assert opts["dry-run"] is False
    assert opts["name"] == "anon"
    assert opts["count"] == 0


def test_value_option_space_form():
    opts, pos = argparsemini.parse(["--name", "alice"], SPEC)
    assert opts["name"] == "alice"
    assert pos == []


def test_value_option_attached_equal_form():
    opts, pos = argparsemini.parse(["--name=alice"], SPEC)
    assert opts["name"] == "alice"
    assert pos == []


def test_attached_value_does_not_consume_next_token():
    opts, pos = argparsemini.parse(["--name=alice", "bob"], SPEC)
    assert opts["name"] == "alice"
    assert pos == ["bob"]


def test_attached_value_for_count():
    opts, pos = argparsemini.parse(["--count=5"], SPEC)
    assert opts["count"] == "5"
    assert pos == []


def test_positionals_in_order():
    opts, pos = argparsemini.parse(["a", "b", "c"], SPEC)
    assert pos == ["a", "b", "c"]


def test_mixed_positionals_and_options():
    opts, pos = argparsemini.parse(["--verbose", "in.txt", "out.txt"], SPEC)
    assert opts["verbose"] is True
    assert pos == ["in.txt", "out.txt"]


def test_unknown_flag_raises_systemexit_2():
    with pytest.raises(SystemExit) as excinfo:
        argparsemini.parse(["--bogus"], SPEC)
    assert excinfo.value.code == 2


def test_unknown_flag_with_value_raises_systemexit_2():
    with pytest.raises(SystemExit) as excinfo:
        argparsemini.parse(["--bogus=1"], SPEC)
    assert excinfo.value.code == 2


def test_unknown_flag_not_collected_as_positional():
    with pytest.raises(SystemExit):
        argparsemini.parse(["--bogus", "ok"], SPEC)


def test_double_dash_terminates_options():
    opts, pos = argparsemini.parse(["--", "x"], SPEC)
    assert opts["verbose"] is False
    assert pos == ["x"]


def test_double_dash_with_value_before_it():
    opts, pos = argparsemini.parse(["--name", "alice", "--", "file"], SPEC)
    assert opts["name"] == "alice"
    assert pos == ["file"]


def test_double_dash_treated_as_positional_before_it():
    opts, pos = argparsemini.parse(["a", "--", "b"], SPEC)
    assert pos == ["a", "b"]


def test_flag_repeated_stays_true():
    opts, _ = argparsemini.parse(["--verbose", "--verbose"], SPEC)
    assert opts["verbose"] is True
