"""Session tracking using a SessionStore class (refactored from module-level globals)."""


class SessionStore:
    def __init__(self):
        self._sessions = {}
        self._next_id = 1

    def create(self, user):
        sid = self._next_id
        self._next_id += 1
        self._sessions[sid] = {"user": user, "active": True}
        return sid

    def close(self, sid):
        if sid in self._sessions:
            self._sessions[sid]["active"] = False

    def active_count(self):
        return sum(1 for s in self._sessions.values() if s["active"])
