"""Meeting scheduler."""

from datetime import datetime, timezone, timedelta


def parse_stamp(text):
    """Parse ISO stamp. Naive input is interpreted as UTC."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def minutes_between(a, b):
    """Minutes from a to b (b - a), handling mixed aware/naive."""
    if a.tzinfo is None:
        a = a.replace(tzinfo=timezone.utc)
    if b.tzinfo is None:
        b = b.replace(tzinfo=timezone.utc)
    return (b - a).total_seconds() / 60.0


def add_minutes(dt, mins):
    """Add minutes, preserving tz awareness."""
    return dt + timedelta(minutes=mins)
