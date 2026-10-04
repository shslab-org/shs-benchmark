"""Tests for httpclient.fetch_with_retry.

Strategy:
* A real local ``http.server`` in a background thread serves controlled
  responses so we can exercise success, 4xx and 5xx paths end-to-end.
* ``time.sleep`` is monkeypatched to record backoff durations without
  actually sleeping, keeping tests fast and deterministic.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Tuple

import pytest

import httpclient


# ---------------------------------------------------------------------------
# Fake server
# ---------------------------------------------------------------------------

class _Scenario:
    """A sequence of (status, payload, content_type) responses served in order."""

    def __init__(self, responses: List[Tuple[int, bytes, str]]) -> None:
        self.responses = list(responses)
        self.hits = 0

    def next(self):
        if self.hits < len(self.responses):
            idx = self.hits
            self.hits += 1
            return self.responses[idx]
        # If the client retries past the scripted responses, repeat the last one.
        self.hits += 1
        return self.responses[-1]


class _Handler(BaseHTTPRequestHandler):
    scenario: _Scenario  # set per-test via factory

    def do_GET(self):  # noqa: N802 (http.server API)
        status, payload, ctype = self.scenario.next()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if status < 400:
            self.wfile.write(payload)
        else:
            # HTTPError bodies are still read by urllib client.
            self.wfile.write(payload)

    def log_message(self, *args):  # silence request logs
        pass


def make_server(responses: List[Tuple[int, bytes, str]]):
    """Start a throwaway HTTP server; return (scenario, url, stop_fn)."""
    scenario = _Scenario(responses)

    def factory():
        h = _Handler
        h.scenario = scenario

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    _Handler.scenario = scenario
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    def stop():
        server.shutdown()
        server.server_close()

    return scenario, url, stop


# ---------------------------------------------------------------------------
# sleep recording fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def recorded_sleep(monkeypatch) -> List[float]:
    sleeps: List[float] = []

    def fake_sleep(seconds: float):
        sleeps.append(seconds)

    monkeypatch.setattr(httpclient.time, "sleep", fake_sleep)
    return sleeps


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_success_first_try(recorded_sleep):
    payload = json.dumps({"ok": True}).encode()
    scenario, url, stop = make_server([(200, payload, "application/json")])
    try:
        body, status = httpclient.fetch_with_retry(url, retries=3, backoff=0.1)
    finally:
        stop()

    assert status == 200
    assert body == {"ok": True}          # JSON-parsed
    assert scenario.hits == 1
    assert recorded_sleep == []          # no failures -> no sleeps


def test_retry_then_success(recorded_sleep):
    bad = b"internal server error"
    good = json.dumps({"ok": True}).encode()
    # 500, 500, then 200
    scenario, url, stop = make_server([
        (500, bad, "text/plain"),
        (500, bad, "text/plain"),
        (200, good, "application/json"),
    ])
    try:
        body, status = httpclient.fetch_with_retry(url, retries=3, backoff=0.5)
    finally:
        stop()

    assert status == 200
    assert body == {"ok": True}
    assert scenario.hits == 3
    # Exponential: 0.5 after 1st fail, 1.0 after 2nd fail
    assert recorded_sleep == [0.5, 1.0]


def test_give_up_after_retries(recorded_sleep):
    bad = b"still broken"
    scenario, url, stop = make_server([
        (500, bad, "text/plain"),
    ])
    try:
        body, status = httpclient.fetch_with_retry(url, retries=2, backoff=0.25)
    finally:
        stop()

    # All 3 attempts (1 initial + 2 retries) return 500
    assert scenario.hits == 3
    assert status == 500
    assert body == "still broken"       # plain text stays as text
    assert recorded_sleep == [0.25, 0.5]  # exponential backoff applied


def test_4xx_no_retry(recorded_sleep):
    payload = b"not found"
    scenario, url, stop = make_server([
        (404, payload, "text/plain"),
    ])
    try:
        body, status = httpclient.fetch_with_retry(url, retries=5, backoff=0.1)
    finally:
        stop()

    # 4xx must NOT be retried, even with many retries configured.
    assert scenario.hits == 1
    assert status == 404
    assert body == "not found"
    assert recorded_sleep == []


def test_connection_error_exhausted(recorded_sleep, monkeypatch):
    """Simulate a persistent connection-level failure by making urlopen raise."""
    import urllib.error

    def fake_urlopen(url, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(httpclient.urllib.request, "urlopen", fake_urlopen)
    body, status = httpclient.fetch_with_retry(
        "http://127.0.0.1:1/unreachable", retries=2, backoff=0.1
    )
    assert body is None
    assert status == 0
    # Two sleeps: after attempt 0 and attempt 1 (attempt 2 is last -> no sleep)
    assert recorded_sleep == [0.1, 0.2]


def test_retries_zero_param():
    """retries=0 means exactly one attempt; a 5xx is returned immediately."""
    bad = b"boom"
    scenario, url, stop = make_server([(500, bad, "text/plain")])
    try:
        body, status = httpclient.fetch_with_retry(url, retries=0)
    finally:
        stop()
    assert scenario.hits == 1
    assert status == 500
    assert body == "boom"


def test_invalid_args():
    with pytest.raises(ValueError):
        httpclient.fetch_with_retry("http://x", retries=-1)
    with pytest.raises(ValueError):
        httpclient.fetch_with_retry("http://x", backoff=-1)
