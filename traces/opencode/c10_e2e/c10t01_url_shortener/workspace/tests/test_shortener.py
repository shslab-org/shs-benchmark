import pytest

import shortener


@pytest.fixture(autouse=True)
def clean_state():
    shortener._reset()
    yield
    shortener._reset()


def test_round_trip():
    url = "https://example.com/very/long/path?x=1&y=2"
    code = shortener.shorten(url)
    assert shortener.resolve(code) == url


def test_determinism():
    url = "https://example.com/deterministic"
    c1 = shortener.shorten(url)
    c2 = shortener.shorten(url)
    assert c1 == c2
    assert len(c1) >= 6


def test_custom_alias():
    url = "https://example.com/foo"
    code = shortener.shorten(url, alias="myalias")
    assert code == "myalias"
    assert shortener.resolve("myalias") == url


def test_alias_collision():
    shortener.shorten("https://a.com", alias="taken")
    with pytest.raises(ValueError):
        shortener.shorten("https://b.com", alias="taken")


def test_alias_collision_with_generated_code():
    url = "https://a.com/x"
    code = shortener.shorten(url)
    with pytest.raises(ValueError):
        shortener.shorten("https://b.com/y", alias=code)


def test_unknown_code():
    assert shortener.resolve("doesnotexist") is None
