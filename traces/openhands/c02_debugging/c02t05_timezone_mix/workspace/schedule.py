"""Meeting scheduler. All datetimes are kept timezone-aware (naive means UTC)."""

from datetime import datetime, timedelta, timezone


def _ensure_utc(dt):
    """Interpret a naive datetime as UTC; leave aware datetimes untouched."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def parse_stamp(text):
    """Parse an ISO stamp. 'Z' and numeric offsets keep their tzinfo;
    naive input is interpreted as UTC (attached, not left naive)."""
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return _ensure_utc(dt)


def minutes_between(a, b):
    """Minutes from a to b (b - a). Naive inputs are interpreted as UTC."""
    return (_ensure_utc(b) - _ensure_utc(a)).total_seconds() / 60.0


def add_minutes(dt, mins):
    """Add minutes, preserving timezone awareness across day boundaries."""
    return _ensure_utc(dt) + timedelta(minutes=mins)
