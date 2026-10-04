"""Quick tests for SessionStore across multiple instances."""
from sessions import SessionStore


def test_independent_instances():
    a, b = SessionStore(), SessionStore()
    assert a.active_count() == 0 and b.active_count() == 0

    ids_a = [a.create(f"user{i}") for i in range(3)]
    assert ids_a == [1, 2, 3]
    assert a.active_count() == 3

    # Independent id sequences
    sid_b = b.create("bob")
    assert sid_b == 1
    assert b.active_count() == 1

    a.close(ids_a[1])
    assert a.active_count() == 2
    b.close(sid_b)
    assert b.active_count() == 0 and a.active_count() == 2


def test_close_unknown_id_is_noop():
    s = SessionStore()
    s.create("x")
    s.close(999)  # unknown id: no error, no change
    assert s.active_count() == 1
    s.close(1)
    s.close(1)  # double close: still no error
    assert s.active_count() == 0


def test_reset_all():
    s = SessionStore()
    for i in range(5):
        s.create(f"user{i}")
    s.reset_all()
    assert s.active_count() == 0
    assert s.create("again") == 1  # ids restart after reset


def test_no_module_level_state():
    import sessions
    for name in ("SESSIONS", "NEXT_ID", "_sessions", "_next_id"):
        assert name not in vars(sessions), f"unexpected module-level {name!r}"


if __name__ == "__main__":
    test_independent_instances()
    test_close_unknown_id_is_noop()
    test_reset_all()
    test_no_module_level_state()
    print("ALL TESTS PASSED")
