"""Pytest suite for stringutils — spec-based black-box tests.

Fails against the shipped (buggy) module; passes against any
implementation that meets the spec.
"""
import pytest

import stringutils as su


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------
class TestSlugify:
    def test_spec_example(self):
        assert su.slugify("  Hello, World!  ") == "hello-world"

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("-abc", "abc"),                # leading hyphen removed
            ("abc-", "abc"),                # trailing hyphen removed
            (" -abc- ", "abc"),             # both ends removed
            ("!!!", ""),                   # nothing left after stripping
            ("a!@#b  c", "a-b-c"),          # runs collapse to one hyphen
            ("abc", "abc"),
            ("hello-world", "hello-world"),
            ("MiXeD", "mixed"),
            ("a1_b2", "a1-b2"),
        ],
    )
    def test_cases(self, text, expected):
        assert su.slugify(text) == expected


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------
class TestTruncate:
    def test_spec_example(self):
        assert su.truncate("hello world", 8) == "hello..."

    def test_shorter_than_width_unchanged(self):
        assert su.truncate("hi", 5) == "hi"

    def test_exactly_width_unchanged(self):
        # len(text) == width -> fits -> unchanged
        assert su.truncate("hello", 5) == "hello"

    def test_width_smaller_than_ellipsis(self):
        # width 2 < len("...") 3 -> ellipsis prefix of length 2
        assert su.truncate("abcdef", 2) == ".."
        assert len(su.truncate("abcdef", 2)) == 2

    def test_width_equal_to_ellipsis(self):
        assert su.truncate("abcdef", 3) == "..."
        assert len(su.truncate("abcdef", 3)) == 3

    def test_result_exactly_width(self):
        for width in range(4, 11):
            assert len(su.truncate("abcdef", width)) == width

    def test_text_longer_by_one(self):
        assert su.truncate("abcdef", 4) == "a..."

    def test_empty_text(self):
        assert su.truncate("", 5) == ""

    def test_custom_ellipsis(self):
        out = su.truncate("hello world", 7, ellipsis="--")
        assert out == "hello--"
        assert len(out) == 7

    def test_width_smaller_than_custom_ellipsis(self):
        # ellipsis "..." width 1 -> prefix "..."[:1] = "."
        assert su.truncate("abcdef", 1) == "."
        assert su.truncate("abcdef", 0) == ""


# ---------------------------------------------------------------------------
# camel_to_snake
# ---------------------------------------------------------------------------
class TestCamelToSnake:
    def test_spec_examples(self):
        assert su.camel_to_snake("HTTPServer") == "http_server"
        assert su.camel_to_snake("myVarName") == "my_var_name"

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("hello", "hello"),
            ("camelCase", "camel_case"),
            ("alreadySnake", "already_snake"),
            ("", ""),
            ("HTMLView2", "html_view2"),
            ("ABCDef", "abc_def"),
            ("A", "a"),
            ("Ab", "ab"),
            ("aB", "a_b"),
            ("A1B", "a1_b"),
        ],
    )
    def test_cases(self, name, expected):
        assert su.camel_to_snake(name) == expected


# ---------------------------------------------------------------------------
# count_vowels
# ---------------------------------------------------------------------------
class TestCountVowels:
    def test_spec_example(self):
        assert su.count_vowels("Banana") == 3

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("aeiou", 5),
            ("AEIOU", 5),
            ("Rhythm", 0),
            ("", 0),
            ("AEIOUaeiou", 10),
        ],
    )
    def test_cases(self, text, expected):
        assert su.count_vowels(text) == expected
