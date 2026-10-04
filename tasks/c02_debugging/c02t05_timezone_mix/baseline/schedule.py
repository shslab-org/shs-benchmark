"""Meeting scheduler. BUG: mixes naive and timezone-aware datetimes."""

from datetime import datetime, timezone, timedelta


def parse_stamp(text):
    """Parse ISO stamp. Naive input means UTC. BUG: returns naive for 'Z'."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if text.endswith("Z"):
        dt = dt.replace(tzinfo=None)      # BUG: silently drops UTC info
    return dt


def minutes_between(a, b):
    """Minutes from a to b (b - a). BUG: crashes when mixing aware/naive."""
    return (b - a).total_seconds() / 60.0


def add_minutes(dt, mins):
    """BUG: adds minutes in local time even for aware datetimes with offset."""
    return dt + timedelta(minutes=mins)
