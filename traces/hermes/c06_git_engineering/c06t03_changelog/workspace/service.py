import threading

METRICS = {}
METRICS_LOCK = threading.Lock()

def ping(timeout=5.0):
    """Return "pong"; validate timeout and raise ValueError on bad input."""
    if timeout is None:
        raise ValueError("timeout must not be None")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    with METRICS_LOCK:
        METRICS.setdefault("ping_requests", 0)
        METRICS["ping_requests"] += 1
    return "pong"

def metrics():
    """Return a snapshot of the service metrics."""
    with METRICS_LOCK:
        return dict(METRICS)

def healthcheck():
    """Return {"status": "ok"} if the service is healthy."""
    return {"status": "ok"}
