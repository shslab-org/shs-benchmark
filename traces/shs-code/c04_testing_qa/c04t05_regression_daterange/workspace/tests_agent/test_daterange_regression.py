"""Regression test for issue #47: DateRange.overlaps misses touching ranges.

Booking policy: two ranges that share exactly one boundary day
(checkout of the first == check-in of the second) count as overlapping.
The shipped ``overlaps`` uses a strict comparison
(``self.end < other.start or other.end < self.start``) which wrongly
returns False when a boundary day is shared.

This test must FAIL against the shipped (buggy) module and PASS against
the fixed one. Do not modify daterange.py.
"""

import sys
from datetime import date
from pathlib import Path

# Make the project root importable regardless of pytest's working directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from daterange import DateRange  # noqa: E402


def test_overlaps_touching_at_end_start_of_other():
    """r1.end == r2.start: the shared boundary day must count as overlap.

    Exact repro from issue #47.
    """
    r1 = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    r2 = DateRange(date(2026, 3, 20), date(2026, 3, 25))
    assert r1.overlaps(r2) is True
    # Symmetric direction of the call must agree as well.
    assert r2.overlaps(r1) is True


def test_overlaps_touching_single_day_range():
    """A single-day range sitting on the boundary counts as overlap."""
    booking = DateRange(date(2026, 3, 20), date(2026, 3, 20))
    adjacent = DateRange(date(2026, 3, 15), date(2026, 3, 20))
    assert booking.overlaps(adjacent) is True
    assert adjacent.overlaps(booking) is True


def test_no_overlap_when_no_shared_day():
    """Ranges with a gap between them must still report no overlap.

    end == start - 1 day means the day after one range starts is the
    first day of the next range, so no day is shared.
    """
    a = DateRange(date(2026, 3, 10), date(2026, 3, 20))
    b = DateRange(date(2026, 3, 21), date(2026, 3, 25))
    assert a.overlaps(b) is False
    assert b.overlaps(a) is False
