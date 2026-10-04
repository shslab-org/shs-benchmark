import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparsemini
import pytest


def test_flag_present():
    spec = {"verbose": {"type": "flag", "default": False}}
    opts, pos = argparsemini.parse(["--verbose"], spec)
    assert opts["verbose"] is True
    assert pos == []


def test_flag_absent_uses_default():
    spec = {"verbose": {"type": "flag", "default": False}}
    opts, pos = argparsemini.parse([], spec)
    assert opts["verbose"] is False
    assert pos == []


def test_value_flag_separated():
    spec = {"name": {"type": "value", "default": None}}
    opts, pos = argparsemini.parse(["--name", "Alice"], spec)
    assert opts["name"] == "Alice"
    assert pos == []


def test_value_flag_attached():
    spec = {"name": {"type": "value", "default": None}}
    opts, pos = argparsemini.parse(["--name=Alice"], spec)
    assert opts["name"] == "Alice"
    assert pos == []


def test_value_flag_attached_empty():
    spec = {"name": {"type": "value", "default": None}}
    opts, pos = argparsemini.parse(["--name="], spec)
    assert opts["name"] == ""
    assert pos == []


def test_unknown_flag_raises_systemexit():
    spec = {"verbose": {"type": "flag", "default": False}}
    with pytest.raises(SystemExit) as exc_info:
        argparsemini.parse(["--verbose", "--unknown"], spec)
    assert exc_info.value.code == 2


def test_unknown_flag_alone_raises_systemexit():
    spec = {"verbose": {"type": "flag", "default": False}}
    with pytest.raises(SystemExit) as exc_info:
        argparsemini.parse(["--bogus"], spec)
    assert exc_info.value.code == 2


def test_positional_tokens_collected_in_order():
    spec = {"verbose": {"type": "flag", "default": False}}
    opts, pos = argparsemini.parse(["file1.txt", "--verbose", "file2.txt"], spec)
    assert pos == ["file1.txt", "file2.txt"]
    assert opts["verbose"] is True


def test_double_dash_terminates_option_parsing():
    spec = {
        "verbose": {"type": "flag", "default": False},
        "name": {"type": "value", "default": None},
    }
    opts, pos = argparsemini.parse(
        ["--name", "Alice", "--", "--verbose", "x", "--name=Bob"],
        spec,
    )
    assert pos == ["--verbose", "x", "--name=Bob"]
    assert opts["name"] == "Alice"
    assert opts["verbose"] is False


def test_value_flag_mixed_syntax():
    spec = {"name": {"type": "value", "default": "d"}}
    opts, pos = argparsemini.parse(["--name=A", "b", "--name=C"], spec)
    assert opts["name"] == "C"
    assert pos == ["b"]


def test_multiple_positionals():
    spec = {"v": {"type": "flag", "default": False}}
    opts, pos = argparsemini.parse(["a", "b", "c"], spec)
    assert pos == ["a", "b", "c"]
