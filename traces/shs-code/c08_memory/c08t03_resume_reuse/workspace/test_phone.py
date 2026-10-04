"""Unit tests for phone.py: normalize_phone and format_intl."""

import os
import sys
import unittest

# Make phone.py importable regardless of how the tests are launched.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phone import normalize_phone, format_intl


class TestNormalizePhone(unittest.TestCase):
    def test_spec_example_strips_symbols(self):
        self.assertEqual(normalize_phone("+1 (555) 123-4567"), "15551234567")

    def test_no_digits_returns_empty(self):
        self.assertEqual(normalize_phone("abc"), "")

    def test_mixed_text_and_digits(self):
        self.assertEqual(normalize_phone("call me at 555.1234"), "5551234")

    def test_empty_string(self):
        self.assertEqual(normalize_phone(""), "")

    def test_only_whitespace(self):
        self.assertEqual(normalize_phone("   \t  "), "")

    def test_digits_already_plain(self):
        self.assertEqual(normalize_phone("1234567890"), "1234567890")


class TestFormatIntl(unittest.TestCase):
    def test_spec_example_1(self):
        self.assertEqual(format_intl("+1 (555) 123-4567"), "+1 555 123 456 7")

    def test_spec_example_2(self):
        self.assertEqual(format_intl("44 20 7123 0000"), "+44 207 123 000 0")

    def test_no_digits_returns_empty(self):
        self.assertEqual(format_intl("abc"), "")

    def test_empty_input_returns_empty(self):
        self.assertEqual(format_intl(""), "")

    def test_cc_only_two_digit_country_code(self):
        # "44" -> CC "44", no remainder -> "+44" (no trailing space)
        self.assertEqual(format_intl("44"), "+44")

    def test_cc_only_single_digit_when_starts_with_1(self):
        # "1" -> CC "1", no remainder -> "+1"
        self.assertEqual(format_intl("1"), "+1")

    def test_starts_with_1_single_digit_cc(self):
        self.assertEqual(format_intl("123"), "+1 23")

    def test_partial_chunk_remainder(self):
        # CC "74" (starts with 7, not 1 -> 2 digits), rest "951234" -> "951 234"
        self.assertEqual(format_intl("7 495 1234"), "+74 951 234")

    def test_two_digit_cc_with_remainder(self):
        # "445" -> CC "44", rest "5" -> "+44 5"
        self.assertEqual(format_intl("445"), "+44 5")

    def test_exactly_two_digit_cc_boundary(self):
        # "12" starts with 1 -> CC "1", rest "2" -> "+1 2"
        self.assertEqual(format_intl("12"), "+1 2")

    def test_symbol_heavy_input(self):
        self.assertEqual(format_intl("(+1) 555-123-4567"), "+1 555 123 456 7")

    def test_whitespace_and_symbols_around_numbers(self):
        self.assertEqual(format_intl("  44-20-7123-0000 "), "+44 207 123 000 0")

    def test_long_number_chunking_left_to_right(self):
        # "44" + "1234567890" -> chunks "123 456 789 0"
        self.assertEqual(format_intl("44 1234567890"), "+44 123 456 789 0")


if __name__ == "__main__":
    unittest.main()
