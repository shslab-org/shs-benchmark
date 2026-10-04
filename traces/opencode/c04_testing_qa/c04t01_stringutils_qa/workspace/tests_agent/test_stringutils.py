"""Pytest suite for stringutils.py written against the SPEC.

These tests PASS against a correct implementation and FAIL against the
shipped module, which violates the spec in at least three places:

  * slugify        — does not strip leading/trailing hyphens
  * truncate       — off-by-one fit check; wrong result when width is
                     smaller than or equal to the ellipsis length
  * camel_to_snake — mishandles acronym runs (HTTPServer -> h_t_t_p_server)

count_vowels is implemented correctly in the shipped module.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stringutils import camel_to_snake, count_vowels, slugify, truncate


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_spec_example(self):
        assert slugify("  Hello, World!  ") == "hello-world"

    def test_leading_trailing_hyphens_removed(self):
        assert slugify("  Hello, World!  ") == "hello-world"

    def test_only_separators(self):
        # No alphanumeric characters remain, so the result must be empty,
        # not "-".
        assert slugify("   ") == ""
        assert slugify("!!!") == ""
        assert slugify("- - -") == ""

    def test_trailing_separators(self):
        assert slugify("trailing!!") == "trailing"

    def test_leading_separators(self):
        assert slugify("@@@start") == "start"

    def test_collapse_run_of_separators(self):
        assert slugify("a   b") == "a-b"
        assert slugify("a!!@#b") == "a-b"

    def test_already_slug(self):
        assert slugify("hello-world") == "hello-world"

    def test_digits_kept(self):
        assert slugify("a1b2") == "a1b2"
        assert slugify("42!!means") == "42-means"

    def test_mixed_case_lowercased(self):
        assert slugify("HelloWorld") == "helloworld"

    def test_single_word(self):
        assert slugify("word") == "word"

    def test_punctuation_inside(self):
        assert slugify("a-b-c") == "a-b-c"


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------

class TestTruncate:
    def test_spec_example(self):
        assert truncate("hello world", 8) == "hello..."

    def test_short_text_unchanged(self):
        assert truncate("hi", 5) == "hi"

    def test_text_exactly_width_unchanged(self):
        # len("abc") == width, so the text fits and must be returned as-is.
        assert truncate("abc", 3) == "abc"

    def test_text_just_over_width_unchanged(self):
        # len("abcd") (4) <= 5 -> unchanged.
        assert truncate("abcd", 5) == "abcd"

    def test_result_is_exactly_width_chars(self):
        # When truncation happens, the result must be EXACTLY width chars
        # including the ellipsis.
        result = truncate("hello world", 8)
        assert result == "hello..."
        assert len(result) == 8

    def test_truncation_boundary(self):
        # len("abcdef") (6) > 5 -> result is 5 chars: 2 kept + 3 ellipsis.
        assert truncate("abcdef", 5) == "ab..."

    def test_width_smaller_than_ellipsis(self):
        # width (2) < len("...") (3) -> prefix of the ellipsis, NOT a
        # crash or an empty string.
        assert truncate("abcdef", 2) == ".."

    def test_width_equal_to_ellipsis(self):
        # width (3) == len("...") (3) -> the ellipsis itself.
        assert truncate("abcdef", 3) == "..."

    def test_custom_ellipsis(self):
        assert truncate("hello world", 6, ellipsis="..") == "hell.."

    def test_custom_ellipsis_longer_than_width(self):
        # width (1) < len("ab") (2) -> prefix of the custom ellipsis.
        assert truncate("abcdef", 1, ellipsis="ab") == "a"

    def test_empty_text(self):
        assert truncate("", 5) == ""

    def test_result_never_exceeds_width(self):
        for width in range(0, 10):
            assert len(truncate("abcdef", width)) <= width


# ---------------------------------------------------------------------------
# camel_to_snake
# ---------------------------------------------------------------------------

class TestCamelToSnake:
    def test_spec_example_acronym(self):
        assert camel_to_snake("HTTPServer") == "http_server"

    def test_spec_example_plain(self):
        assert camel_to_snake("myVarName") == "my_var_name"

    def test_simple_camel(self):
        assert camel_to_snake("myVar") == "my_var"

    def test_all_caps_single_word(self):
        # An uninterrupted all-caps run is one token.
        assert camel_to_snake("HTTP") == "http"

    def test_two_acronyms_back_to_back(self):
        # No lowercase between "HTTPGET" and "Request" -> "httpget"
        # stays one token.
        assert camel_to_snake("HTTPGETRequest") == "httpget_request"

    def test_already_snake(self):
        assert camel_to_snake("already_snake") == "already_snake"

    def test_single_lowercase(self):
        assert camel_to_snake("word") == "word"

    def test_no_trailing_underscore(self):
        assert camel_to_snake("Value") == "value"


# ---------------------------------------------------------------------------
# count_vowels
# ---------------------------------------------------------------------------

class TestCountVowels:
    def test_spec_example(self):
        assert count_vowels("Banana") == 3

    def test_case_insensitive(self):
        assert count_vowels("AEIOU") == 5
        assert count_vowels("aeiou") == 5

    def test_no_vowels(self):
        assert count_vowels("rhythm") == 0

    def test_empty(self):
        assert count_vowels("") == 0

    def test_mixed(self):
        assert count_vowels("Hello World") == 3
