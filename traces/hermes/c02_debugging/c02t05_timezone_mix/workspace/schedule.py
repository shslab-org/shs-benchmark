"""Meeting scheduler. Naive datetimes are treated as UTC; aware ones keep their tz."""

from datetime import datetime, timezone, timedelta


def _as_aware(dt):
    """Attach UTC to naive datetimes so aware/naive values can mix safely."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def parse_stamp(text):
    """Parse ISO stamp. 'Z' stays UTC-aware; offsets are kept; naive means UTC."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def minutes_between(a, b):
    """Minutes from a to b (b - a); naive inputs are treated as UTC."""
    return (_as_aware(b) - _as_aware(a)).total_seconds() / 60.0


def add_minutes(dt, mins):
    """Add minutes, preserving timezone awareness across day boundaries."""
    return _as_aware(dt) + timedelta(minutes=mins)
