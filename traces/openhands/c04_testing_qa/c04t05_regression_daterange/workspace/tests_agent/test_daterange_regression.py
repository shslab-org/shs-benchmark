"""Regression tests for issue #47: DateRange.overlaps misses touching ranges.

Policy: two ranges that share exactly one boundary day (one range's end ==
the other's start) DO overlap.
"""
from datetime import date

import pytest

from daterange import DateRange


def test_touching_ranges_overlap():
    # Exact repro from issue #47: ranges share 2026-03-20.
    a = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    b = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_single_day_touch():
    # A range ending on a day where another range starts overlaps,
    # even when the first range is a single-day stay.
    a = DateRange(date(2026, 5, 1), date(2026, 5, 1))
    b = DateRange(date(2026, 5, 1), date(2026, 5, 3))
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_disjoint_ranges_do_not_overlap():
    # Genuinely separate ranges must still report no overlap.
    a = DateRange(date(2026, 3, 10), date(2026, 3, 19))
    b = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    assert not a.overlaps(b)
    assert not b.overlaps(a)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
