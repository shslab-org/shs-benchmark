"""Spec-driven pytest suite for stringutils.

These tests are written to the SPEC, not the implementation. They must FAIL
against any module that violates the spec (including the shipped buggy one)
and PASS against a correct implementation.
"""
import os
import sys

# Make sure the project root (where stringutils.py lives) is importable
# regardless of how pytest is invoked.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import stringutils as su


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

def test_slugify_basic_spec_example():
    # The literal example from the spec.
    assert su.slugify("  Hello, World!  ") == "hello-world"


def test_slugify_strips_leading_and_trailing_hyphens():
    # Input that starts/ends with punctuation must not yield edge hyphens.
    assert su.slugify("!!!hello") == "hello"
    assert su.slugify("world!!!") == "world"
    assert su.slugify("!!!hello world!!!") == "hello-world"
    assert su.slugify("-abc-") == "abc"


def test_slugify_collapses_multiple_separators_to_one_hyphen():
    # Runs of *any* non-alphanumeric characters become a single hyphen.
    assert su.slugify("a   b") == "a-b"
    assert su.slugify("a@#$$b") == "a-b"
    assert su.slugify("a\n\nb\tc") == "a-b-c"


def test_slugify_preserves_alphanumerics_and_lowercases():
    assert su.slugify("ABC123") == "abc123"
    assert su.slugify("Hello123World") == "hello123world"


def test_slugify_all_punctuation_yields_empty_string():
    # No alphanumerics remain -> no hyphens either (nothing to join).
    assert su.slugify("!!! ???") == ""
    assert su.slugify("$$$") == ""


def test_slugify_spaces_between_words():
    assert su.slugify("one two three") == "one-two-three"


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------

def test_truncate_passthrough_when_text_fits():
    # Spec: if text fits within width, return unchanged.
    assert su.truncate("hi", 5) == "hi"
    assert su.truncate("hi", 2) == "hi"  # exact fit, no ellipsis needed
    assert su.truncate("hello", 100) == "hello"


def test_truncate_exact_width_including_ellipsis():
    # Spec example: result length must be EXACTLY width when truncated.
    result = su.truncate("hello world", 8)
    assert result == "hello..."
    assert len(result) == 8


def test_truncate_result_length_is_exactly_width():
    for text, width in [("abcdef", 5), ("longer text here", 4), ("x" * 50, 10)]:
        out = su.truncate(text, width)
        assert len(out) == width, f"width={width} produced {len(out)} chars: {out!r}"


def test_truncate_width_smaller_than_ellipsis_returns_prefix_of_ellipsis():
    # Spec: if width < len(ellipsis), return a prefix of the ellipsis cut to width.
    assert su.truncate("abcdef", 2) == ".."
    assert su.truncate("abcdef", 1) == "."
    assert su.truncate("abcdef", 0) == ""
    assert su.truncate("abcdef", 3) == "..."


def test_truncate_custom_ellipsis():
    # Text shorter than width but longer than the ellipsis is returned
    # unchanged (spec: "if text fits within width return unchanged").
    out = su.truncate("abcdef", 7, ellipsis="...")
    assert out == "abcdef"
    # When text exceeds width, result is EXACTLY width chars long and ends
    # with the full ellipsis.
    out2 = su.truncate("abcdef", 6, ellipsis="...")
    # "abcdef" fits within 6, so unchanged.
    assert out2 == "abcdef"
    out3 = su.truncate("abcdefgh", 7, ellipsis="...")
    assert out3 == "abcd..."
    assert len(out3) == 7
    # width equal to ellipsis length exactly: prefix of ellipsis (full ellipsis).
    out4 = su.truncate("abcdef", 3, ellipsis="...")
    assert out4 == "..."


def test_truncate_does_not_use_ellipsis_when_exactly_fits():
    # Exactly width long -> unchanged (no ellipsis appended).
    assert su.truncate("abc", 3) == "abc"


# ---------------------------------------------------------------------------
# camel_to_snake
# ---------------------------------------------------------------------------

def test_camel_to_snake_acronym_run():
    # Spec example: "HTTPServer" -> "http_server".
    assert su.camel_to_snake("HTTPServer") == "http_server"


def test_camel_to_snake_standard_camel_case():
    # Spec example: "myVarName" -> "my_var_name".
    assert su.camel_to_snake("myVarName") == "my_var_name"


def test_camel_to_snake_single_word():
    assert su.camel_to_snake("name") == "name"
    assert su.camel_to_snake("HTTP") == "http"


def test_camel_to_snake_mixed_boundaries():
    # A typical mixed case: lowercase start, acronym run, then normal words.
    assert su.camel_to_snake("parseHTMLData") == "parse_html_data"
    assert su.camel_to_snake("getUserIDNow") == "get_user_id_now"


def test_camel_to_snake_acronym_followed_by_word():
    assert su.camel_to_snake("URLValidator") == "url_validator"


def test_camel_to_snake_all_lowercase_unchanged():
    assert su.camel_to_snake("already_snake") == "already_snake"


# ---------------------------------------------------------------------------
# count_vowels
# ---------------------------------------------------------------------------

def test_count_vowels_spec_example():
    assert su.count_vowels("Banana") == 3


def test_count_vowels_case_insensitive():
    assert su.count_vowels("AEIOU") == 5
    assert su.count_vowels("aeiou") == 5
    assert su.count_vowels("AeIoU") == 5


def test_count_vowels_no_vowels():
    assert su.count_vowels("rhythm") == 0
    assert su.count_vowels("") == 0
    assert su.count_vowels("hll wrld") == 0


def test_count_vowels_counts_repeats():
    assert su.count_vowels("a") == 1
    assert su.count_vowels("aaaaa") == 5
    assert su.count_vowels("aeiou") == 5
