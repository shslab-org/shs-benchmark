"""Session tracking with module-level global state (refactor to a class)."""

_sessions = {}
_next_id = 1


def create(user):
    global _next_id
    sid = _next_id
    _next_id += 1
    _sessions[sid] = {"user": user, "active": True}
    return sid


def close(sid):
    if sid in _sessions:
        _sessions[sid]["active"] = False


def active_count():
    return sum(1 for s in _sessions.values() if s["active"])


def reset_all():
    global _sessions, _next_id
    _sessions = {}
    _next_id = 1
