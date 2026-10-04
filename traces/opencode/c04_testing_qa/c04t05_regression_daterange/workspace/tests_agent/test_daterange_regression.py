"""Regression test for issue #47: DateRange.overlaps misses touching ranges.

Currently daterange.overlaps uses strict `<`, so two ranges that share
exactly one boundary day (a.end == b.start) incorrectly report no overlap.
Per the booking policy, sharing a single day means overlap.
"""
from datetime import date

from daterange import DateRange


def test_overlaps_touching_at_end_of_first():
    """First range's last day == second range's first day -> overlap."""
    a = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    b = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_overlaps_touching_at_end_of_second():
    """Second range's last day == first range's first day -> overlap."""
    a = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    b = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_no_overlap_when_separated_by_one_day():
    """Ranges with one full day between them must not overlap."""
    a = DateRange(date(2026, 3, 10), date(2026, 3, 15))
    b = DateRange(date(2026, 3, 17), date(2026, 3, 20))
    assert not a.overlaps(b)
    assert not b.overlaps(a)
