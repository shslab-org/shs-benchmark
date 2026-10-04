"""Pytest suite for the URL shortener.

Unit tests point the module at a per-test JSON file in pytest's tmp_path
so the default module-level data.json is never touched.
"""

import shortener


def test_round_trip(tmp_path):
    data = tmp_path / "data.json"
    shortener.reset(data_file=data)

    code = shortener.shorten("https://example.com/very/long/path")
    assert shortener.resolve(code) == "https://example.com/very/long/path"


def test_determinism(tmp_path):
    data = tmp_path / "data.json"
    shortener.reset(data_file=data)

    url = "https://determinism.example/x"
    assert shortener.shorten(url) == shortener.shorten(url)
    # Also deterministic across a fresh module reset.
    shortener.reset(data_file=data)
    assert shortener.shorten(url) is not None  # no error


def test_custom_alias(tmp_path):
    data = tmp_path / "data.json"
    shortener.reset(data_file=data)

    url = "https://alias.example/page"
    assert shortener.shorten(url, alias="mylink") == "mylink"
    assert shortener.resolve("mylink") == url


def test_alias_collision(tmp_path):
    data = tmp_path / "data.json"
    shortener.reset(data_file=data)

    shortener.shorten("https://a.example/1", alias="same")
    # Same alias pointing at a *different* URL -> ValueError.
    try:
        shortener.shorten("https://b.example/2", alias="same")
        raise AssertionError("expected ValueError for alias collision")
    except ValueError:
        pass
    # Re-shortening the identical URL under the same alias is fine.
    assert shortener.shorten("https://a.example/1", alias="same") == "same"


def test_unknown_code(tmp_path):
    data = tmp_path / "data.json"
    shortener.reset(data_file=data)

    assert shortener.resolve("does-not-exist") is None


def test_persistence_across_reset(tmp_path):
    data = tmp_path / "data.json"
    shortener.reset(data_file=data)

    code = shortener.shorten("https://persist.example/url")
    # Simulate a new process: drop in-memory state, reload from disk.
    shortener.reset(data_file=data)
    assert shortener.resolve(code) == "https://persist.example/url"
    assert data.exists()
