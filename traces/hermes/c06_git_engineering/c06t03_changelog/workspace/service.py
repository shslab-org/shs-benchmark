class PingError(Exception):
    """Raised when a ping cannot be completed."""


def ping(timeout=30):
    """Return the ping response, raising PingError on timeout."""
    if timeout <= 0:
        raise PingError("timeout must be positive")
    return "pong"
