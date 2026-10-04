"""Pytest suite for argparsemini.parse() against SPEC.md.

Tests FAIL against the shipped (buggy) argparsemini.py and PASS against
a correct implementation.

Run:  cd <project_root> && python -m pytest tests_agent/test_argparsemini.py -v
"""

import sys
import os

# Make sure the project root (where argparsemini.py lives) is importable.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argparsemini


SPEC = {
    "verbose": {"type": "flag", "default": False},
    "quiet": {"type": "flag", "default": True},
    "name": {"type": "value", "default": None},
    "path": {"type": "value", "default": "/tmp"},
    "count": {"type": "value", "default": 0},
}


# ── Flag behaviour ──────────────────────────────────────────────

def test_flag_absent_uses_default():
    """Flag option not on CLI → default value."""
    opts, pos = argparsemini.parse([], SPEC)
    assert opts["verbose"] is False
    assert opts["quiet"] is True


def test_flag_present_sets_true():
    """'--verbose' on CLI → True regardless of default."""
    opts, pos = argparsemini.parse(["--verbose"], SPEC)
    assert opts["verbose"] is True


def test_flag_present_overrides_default_true():
    """'--quiet' present → True (same as default but must still be set)."""
    opts, pos = argparsemini.parse(["--quiet"], SPEC)
    assert opts["quiet"] is True


# ── Value option: space-separated form ──────────────────────────

def test_value_option_space_separated():
    """'--name Alice' → name = 'Alice'."""
    opts, pos = argparsemini.parse(["--name", "Alice"], SPEC)
    assert opts["name"] == "Alice"


def test_value_option_default_when_absent():
    """No --path → default '/tmp'."""
    opts, pos = argparsemini.parse([], SPEC)
    assert opts["path"] == "/tmp"


# ── Value option: --name=value form (BUG 1 in shipped module) ───

def test_value_option_attached_equal_sign():
    """'--name=Bob' must set name to 'Bob' (spec: both forms work)."""
    opts, pos = argparsemini.parse(["--name=Bob"], SPEC)
    assert opts["name"] == "Bob"


def test_value_option_attached_equal_sign_with_equals_in_value():
    """'--path=a=b' → value is 'a=b' (split on FIRST '=' only)."""
    opts, pos = argparsemini.parse(["--path=a=b"], SPEC)
    assert opts["path"] == "a=b"


def test_value_option_attached_empty_value():
    """'--count=' → value is empty string (not None, not error)."""
    opts, pos = argparsemini.parse(["--count="], SPEC)
    assert opts["count"] == ""


# ── Unknown flags must raise SystemExit(2) (BUG 2 in shipped) ───

def test_unknown_flag_raises_systemexit():
    """'--bogus' is not in spec → SystemExit with code 2."""
    import pytest
    with pytest.raises(SystemExit) as exc_info:
        argparsemini.parse(["--bogus"], SPEC)
    assert exc_info.value.code == 2


def test_unknown_flag_attached_equal_sign_raises_systemexit():
    """'--bogus=x' is also unknown → SystemExit(2)."""
    import pytest
    with pytest.raises(SystemExit) as exc_info:
        argparsemini.parse(["--bogus=x"], SPEC)
    assert exc_info.value.code == 2


def test_unknown_flag_mixed_with_valid():
    """Even if mixed with valid options, unknown flag must exit."""
    import pytest
    with pytest.raises(SystemExit):
        argparsemini.parse(["--verbose", "--bogus"], SPEC)


# ── Positional collection ───────────────────────────────────────

def test_positionals_collected_in_order():
    """Non-option tokens preserved in order."""
    opts, pos = argparsemini.parse(["a", "b", "c"], SPEC)
    assert pos == ["a", "b", "c"]


def test_positionals_mixed_with_options():
    """Positionals interleaved with options keep original order."""
    opts, pos = argparsemini.parse(
        ["one", "--verbose", "two", "--name", "x", "three"], SPEC
    )
    assert pos == ["one", "two", "three"]
    assert opts["verbose"] is True
    assert opts["name"] == "x"


def test_no_positionals_when_only_flags():
    """Only flag options → empty positional list."""
    opts, pos = argparsemini.parse(["--verbose", "--quiet"], SPEC)
    assert pos == []


# ── '--' terminator ────────────────────────────────────────────

def test_double_dash_terminates_option_parsing():
    """'--' makes everything after it positional, even if it looks like a flag."""
    opts, pos = argparsemini.parse(["--", "--verbose", "--name"], SPEC)
    assert pos == ["--verbose", "--name"]
    # The flags after '--' should NOT be treated as options
    assert opts["verbose"] is False  # default, not set
    assert opts["name"] is None       # default, not set


def test_double_dash_with_positionals_before():
    """'a -- b' → positionals are ['a', 'b']."""
    opts, pos = argparsemini.parse(["a", "--", "b"], SPEC)
    assert pos == ["a", "b"]


def test_double_dash_value_after_terminator_is_positional():
    """'-- --name=v' → '--name=v' is a positional, not an option."""
    opts, pos = argparsemini.parse(["--", "--name=v"], SPEC)
    assert pos == ["--name=v"]
    assert opts["name"] is None  # not set


# ── Return types and structure ──────────────────────────────────

def test_returns_tuple_of_dict_and_list():
    opts, pos = argparsemini.parse([], SPEC)
    assert isinstance(opts, dict)
    assert isinstance(pos, list)


def test_opts_contains_all_spec_keys():
    """Options dict must have every key from spec (with defaults)."""
    opts, _ = argparsemini.parse([], SPEC)
    for key in SPEC:
        assert key in opts, f"Missing key {key!r} in options dict"


def test_empty_argv_gives_defaults_only():
    """Empty argv → all defaults, no positionals."""
    opts, pos = argparsemini.parse([], SPEC)
    assert pos == []
    assert opts["verbose"] is False
    assert opts["quiet"] is True
    assert opts["name"] is None
    assert opts["path"] == "/tmp"
    assert opts["count"] == 0
