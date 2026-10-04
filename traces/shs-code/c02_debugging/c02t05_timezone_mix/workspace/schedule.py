"""Meeting scheduler. Handles naive and timezone-aware datetimes safely."""

from datetime import datetime, timezone, timedelta


def parse_stamp(text):
    """Parse ISO stamp. Naive input means UTC; aware input keeps its offset."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)   # interpret naive stamps as UTC
    return dt


def _ensure_aware(dt):
    """Return an aware datetime; assume naive datetimes are UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def minutes_between(a, b):
    """Minutes from a to b (b - a). Naive inputs are treated as UTC."""
    a = _ensure_aware(a)
    b = _ensure_aware(b)
    return (b - a).total_seconds() / 60.0


def add_minutes(dt, mins):
    """Add minutes, preserving tz-awareness (aware datetimes stay aware)."""
    return dt + timedelta(minutes=mins)
