"""Spec-driven pytest suite for stringutils.py.

Every expected value below is required by the written spec:

* slugify: lowercase, replace every run of non-alphanumeric characters with
  a single hyphen, and remove leading/trailing hyphens.
* truncate: return the text unchanged when it fits within ``width``;
  otherwise return exactly ``width`` characters including the ellipsis.
  If ``width`` is smaller than the ellipsis itself, return a prefix of the
  ellipsis cut to ``width``.
* camel_to_snake: convert CamelCase to snake_case, keeping acronym runs
  whole ("HTTPServer" -> "http_server").
* count_vowels: count a/e/i/o/u case-insensitively.

The shipped stringutils.py violates the spec in several places (slugify
keeps leading/trailing hyphens, truncate mishandles widths smaller than
the ellipsis, camel_to_snake breaks acronym boundaries), so this suite
fails against the shipped module and passes against a correct one.

Note: stringutils.py must NOT be modified; it is read-only here.
"""

import sys
from pathlib import Path

import pytest

# Make the module under test importable no matter where pytest runs from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import stringutils  # noqa: E402  (deliberately after the sys.path shim)


# --------------------------------------------------------------------------
# slugify
# --------------------------------------------------------------------------
class TestSlugify:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("  Hello, World!  ", "hello-world"),  # spec example
            ("hello-world 123", "hello-world-123"),  # digits kept, no leading/trailing '-'
            ("a  b", "a-b"),  # a whole run collapses to ONE hyphen
            ("a.b-c_d", "a-b-c-d"),  # every non-alnum run becomes one hyphen
            ("", ""),
            ("a", "a"),
        ],
    )
    def test_lowercase_and_collapse_runs(self, text, expected):
        assert stringutils.slugify(text) == expected

    def test_strips_leading_hyphens(self):
        assert stringutils.slugify("  Hello") == "hello"

    def test_strips_trailing_hyphens(self):
        assert stringutils.slugify("Hi There!!") == "hi-there"

    def test_strips_both_ends(self):
        assert stringutils.slugify("__a__b__") == "a-b"

    def test_all_non_alphanumeric_becomes_empty(self):
        assert stringutils.slugify("!!!") == ""


# --------------------------------------------------------------------------
# truncate
# --------------------------------------------------------------------------
class TestTruncate:
    def test_unchanged_when_text_fits(self):
        assert stringutils.truncate("hi", 5) == "hi"  # spec example
        assert stringutils.truncate("abcdef", 6) == "abcdef"  # exact fit still fits
        assert stringutils.truncate("", 3) == ""

    def test_cut_result_is_exactly_width_long(self):
        assert stringutils.truncate("hello world", 8) == "hello..."  # spec example
        assert stringutils.truncate("hello world", 5) == "he..."
        assert len(stringutils.truncate("hello world", 5)) == 5

    def test_width_equal_to_ellipsis_length(self):
        # 3 is NOT smaller than "...", so the normal cut applies:
        # prefix of length 3 - 3 == 0 plus the ellipsis.
        assert stringutils.truncate("abcdef", 3) == "..."

    @pytest.mark.parametrize(
        ("text", "width", "ellipsis", "expected"),
        [
            ("abcdef", 2, "...", ".."),  # spec example: prefix of ellipsis
            ("abcdef", 1, "...", "."),
            ("abcdef", 0, "...", ""),
            ("abcdef", 1, "abc", "a"),  # custom ellipsis, width < len(ellipsis)
            ("abcdef", 5, "--", "abc--"),  # custom ellipsis, exact width
        ],
    )
    def test_width_smaller_than_ellipsis(self, text, width, ellipsis, expected):
        assert stringutils.truncate(text, width, ellipsis) == expected


# --------------------------------------------------------------------------
# camel_to_snake
# --------------------------------------------------------------------------
class TestCamelToSnake:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("HTTPServer", "http_server"),  # spec example: acronym run + word
            ("myVarName", "my_var_name"),  # spec example
            ("myVarHTTP", "my_var_http"),  # trailing acronym run
            ("fooABC", "foo_abc"),  # acronym run after lowercase text
            ("ABC", "abc"),  # all-caps single word stays one word
            ("HTTP", "http"),
            ("simple", "simple"),
            ("AlreadyCamel", "already_camel"),
        ],
    )
    def test_camel_to_snake(self, name, expected):
        assert stringutils.camel_to_snake(name) == expected


# --------------------------------------------------------------------------
# count_vowels
# --------------------------------------------------------------------------
class TestCountVowels:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Banana", 3),  # spec example
            ("AEIOU", 5),  # case-insensitive
            ("hello", 2),
            ("Queue", 4),
            ("rhythm", 0),  # 'y' is not a vowel
            ("xyz", 0),
            ("", 0),
        ],
    )
    def test_count_vowels(self, text, expected):
        assert stringutils.count_vowels(text) == expected
