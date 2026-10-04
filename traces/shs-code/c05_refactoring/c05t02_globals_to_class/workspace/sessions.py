"""Session tracking as a `SessionStore` class (previously held in module state).

Each store instance is fully independent: its constructor starts empty.
All state lives on the instance; no module-level state or keyword is used.
"""


class SessionStore:
    """Holds session state and provides create / close / active_count ops."""

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

    def reset_all(self):
        self._sessions = {}
        self._next_id = 1
