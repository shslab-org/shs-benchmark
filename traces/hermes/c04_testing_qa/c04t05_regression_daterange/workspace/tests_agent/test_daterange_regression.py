"""Regression test for issue #47: DateRange.overlaps must count a shared
boundary day as overlap.

Fails against the shipped daterange.py (strict `<` excludes the touching day)
and passes against the fixed version.
"""
from datetime import date

import pytest

from daterange import DateRange


def test_touching_ranges_share_boundary_day_issue_47_repro():
    a = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    b = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    assert a.overlaps(b) is True


def test_touching_ranges_are_symmetric():
    a = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    b = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    assert b.overlaps(a) is True


def test_left_touching_boundary_day_counts():
    earlier = DateRange(date(2026, 3, 5), date(2026, 3, 10))
    later = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    assert later.overlaps(earlier) is True


def test_one_day_gap_is_not_overlap():
    a = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    b = DateRange(date(2026, 3, 21), date(2026, 3, 25))
    assert a.overlaps(b) is False


def test_containment_still_overlaps():
    outer = DateRange(date(2026, 3, 1), date(2026, 3, 31))
    inner = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    assert outer.overlaps(inner) is True
    assert inner.overlaps(outer) is True
