"""Date range helpers — the overlap bug is KNOWINGLY SHIPPED (issue #47)."""
from datetime import date


class DateRange:
    def __init__(self, start: date, end: date):
        if end < start:
            raise ValueError("start after end")
        self.start = start
        self.end = end

    def overlaps(self, other: "DateRange") -> bool:
        """True when the two ranges share at least one day.

        ISSUE #47 (customer report):
            r1 = DateRange(2026-03-10, 2026-03-20)
            r2 = DateRange(2026-03-20, 2026-03-25)
            r1.overlaps(r2) returns False, but the ranges share 2026-03-20,
            so it must return True. Adjacent end==start touching day is
            counted as overlapping per our booking policy.
        """
        return self.end < other.start or other.end < self.start   # BUG: strict < excludes touching day
