from datetime import datetime, timezone, timedelta
from schedule import parse_stamp, minutes_between, add_minutes


def test_parse_zulu_keeps_tz():
    dt = parse_stamp("2026-01-02T03:04:05Z")
    assert dt.utcoffset() == timedelta(0), "Z stamp must stay UTC-aware"


def test_parse_offset_kept():
    dt = parse_stamp("2026-01-02T03:04:05+02:00")
    assert dt.utcoffset() == timedelta(hours=2)


def test_parse_naive_means_utc():
    dt = parse_stamp("2026-01-02T03:04:05")
    assert dt.utcoffset() == timedelta(0), "naive input must be interpreted as UTC"


def test_minutes_between_both_aware():
    a = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    b = a + timedelta(minutes=90)
    assert minutes_between(a, b) == 90.0


def test_minutes_between_mixed_offsets():
    a = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    b = datetime(2026, 1, 1, 3, 0, tzinfo=timezone(timedelta(hours=2)))
    assert minutes_between(a, b) == 60.0


def test_add_minutes_aware():
    dt = datetime(2026, 1, 1, 23, 50, tzinfo=timezone.utc)
    out = add_minutes(dt, 20)
    assert out.tzinfo is not None and out.hour == 0 and out.minute == 10
