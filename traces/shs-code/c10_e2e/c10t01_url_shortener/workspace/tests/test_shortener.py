"""Pytest suite for the URL shortener.

Run:  pytest tests/test_shortener.py -v
"""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import shortener  # noqa: E402


@pytest.fixture(autouse=True)
def clean_state():
    """Each test starts with a fresh in-memory + on-disk store."""
    shortener.DATA_FILE.unlink(missing_ok=True)
    shortener._mapping = {}
    yield
    shortener.DATA_FILE.unlink(missing_ok=True)
    shortener._mapping = {}


# --- round-trip -------------------------------------------------------

def test_round_trip():
    url = "https://example.com/a-very/long?path=with&query=params"
    code = shortener.shorten(url)
    assert shortener.resolve(code) == url


def test_code_length_and_charset():
    code = shortener.shorten("https://example.com")
    assert len(code) >= 6
    assert all(c in shortener.CODE_ALPHABET for c in code)


# --- determinism -------------------------------------------------------

def test_deterministic_same_url_same_code():
    a = shortener.shorten("https://deterministic.example/x")
    b = shortener.shorten("https://deterministic.example/x")
    assert a == b


def test_different_urls_different_codes():
    a = shortener.shorten("https://one.example")
    b = shortener.shorten("https://two.example")
    assert a != b


# --- custom alias ------------------------------------------------------

def test_custom_alias_honored():
    code = shortener.shorten("https://aliased.example", alias="myalias")
    assert code == "myalias"
    assert shortener.resolve("myalias") == "https://aliased.example"


def test_alias_collision_raises_value_error():
    shortener.shorten("https://first.example", alias="taken1")
    with pytest.raises(ValueError, match="already in use"):
        shortener.shorten("https://second.example", alias="taken1")


# --- unknown code ------------------------------------------------------

def test_resolve_unknown_code_returns_none():
    assert shortener.resolve("nothere") is None


# --- persistence -------------------------------------------------------

def test_persistence_across_process_restart():
    url = "https://persist.example/abc"
    code = shortener.shorten(url)

    # Simulate a new process: wipe in-memory state, re-import the module.
    shortener._mapping = {}
    reloaded = importlib.reload(shortener)

    assert reloaded.resolve(code) == url
