"""Tests: SessionStore behavior identical to old module-level ops; instances independent."""
from sessions import SessionStore


def test_constructor_starts_empty():
    s = SessionStore()
    assert s.active_count() == 0
    assert s.create("a") == 1
    assert s.active_count() == 1


def test_create_close_sequence():
    s = SessionStore()
    a, b, c = s.create("x"), s.create("y"), s.create("z")
    assert (a, b, c) == (1, 2, 3)
    assert s.active_count() == 3
    s.close(b)
    assert s.active_count() == 2
    s.close(b)          # closing again is a no-op
    s.close(999)        # unknown id is a no-op
    assert s.active_count() == 2
    s.reset_all()
    assert s.active_count() == 0
    assert s.create("w") == 1  # ids restart after reset


def test_two_instances_are_independent():
    s1, s2 = SessionStore(), SessionStore()
    assert s1.create("alice") == 1
    assert s2.create("bob") == 1          # s2 starts empty, id also 1
    assert s1.active_count() == 1
    assert s2.active_count() == 1
    s2.close(1)
    assert s2.active_count() == 0
    assert s1.active_count() == 1         # s1 unaffected by s2
