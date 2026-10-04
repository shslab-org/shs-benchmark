import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def clean_store(monkeypatch, tmp_path):
    """Point the store at a fresh temp data file for each test."""
    data_file = tmp_path / "data.json"
    monkeypatch.setenv("SHORTENER_DATA_FILE", str(data_file))
    monkeypatch.delitem(sys.modules, "shortener", raising=False)
    mod = pytest.importorskip("shortener")
    yield mod
    # ensure later test isolation
    monkeypatch.delitem(sys.modules, "shortener", raising=False)


def test_round_trip(clean_store):
    url = "https://example.com/a/very/long/path?x=1&y=2"
    code = clean_store.shorten(url)
    assert len(code) >= 6
    assert clean_store.resolve(code) == url


def test_determinism(clean_store):
    url = "https://example.com/some/page"
    assert clean_store.shorten(url) == clean_store.shorten(url)
    assert clean_store.resolve(clean_store.shorten(url)) == url


def test_custom_alias(clean_store):
    url = "https://example.com/aliased"
    code = clean_store.shorten(url, alias="myalias")
    assert code == "myalias"
    assert clean_store.resolve("myalias") == url


def test_alias_collision(clean_store):
    url = "https://example.com/first"
    clean_store.shorten(url, alias="dup")
    with pytest.raises(ValueError):
        clean_store.shorten("https://example.com/second", alias="dup")
    # original mapping is intact
    assert clean_store.resolve("dup") == url


def test_unknown_code(clean_store):
    assert clean_store.resolve("doesnotexist") is None
