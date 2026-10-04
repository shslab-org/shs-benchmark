from validators import is_valid_email


def test_simple():
    assert is_valid_email("user@example.com") is True


def test_subdomains():
    assert is_valid_email("first.last@mail.example.co.uk") is True


def test_plus_and_digits():
    assert is_valid_email("user+tag123@example-site.io") is True


def test_missing_at():
    assert is_valid_email("userexample.com") is False


def test_double_at():
    assert is_valid_email("us@@er@x.com") is False


def test_no_tld():
    assert is_valid_email("user@localhost") is False


def test_leading_dot():
    assert is_valid_email(".user@example.com") is False


def test_consecutive_dots():
    assert is_valid_email("a..b@example.com") is False
