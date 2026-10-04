import json
import threading
import time
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import pytest

import httpclient


class TestWithLocalServer:
    """End-to-end tests against a real local http.server in a thread."""

    @pytest.fixture
    def server(self):
        state = {"calls": 0, "succeed_after": 0}

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                state["calls"] += 1
                if self.path == "/ok":
                    body = json.dumps({"hello": "world"}).encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/text":
                    body = b"plain text body"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/flaky":
                    # Fail with 500 until state["succeed_after"] calls have happened.
                    if state["calls"] <= state["succeed_after"]:
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(b"server error")
                    else:
                        body = b"recovered"
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(body)
                elif self.path == "/always500":
                    self.send_response(503)
                    self.end_headers()
                    self.wfile.write(b"unavailable")
                elif self.path == "/notfound":
                    body = b"nope"
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/redirect503":
                    self.send_response(503)
                    self.end_headers()
                    self.wfile.write(b"down")
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, *args):
                pass

        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        port = srv.server_address[1]
        thread = threading.Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        yield {"server": srv, "port": port, "state": state}
        srv.shutdown()
        thread.join()

    def base(self, server, path):
        return f"http://127.0.0.1:{server['port']}{path}"

    def test_success_json(self, server):
        body, status = httpclient.fetch_with_retry(self.base(server, "/ok"), retries=2, backoff=0.01)
        assert status == 200
        assert body == {"hello": "world"}
        assert server["state"]["calls"] == 1

    def test_success_text(self, server):
        body, status = httpclient.fetch_with_retry(self.base(server, "/text"), retries=2, backoff=0.01)
        assert status == 200
        assert body == "plain text body"

    def test_retry_then_success_500(self, server):
        server["state"]["succeed_after"] = 2  # two 500s, then success
        body, status = httpclient.fetch_with_retry(
            self.base(server, "/flaky"), retries=3, backoff=0.01
        )
        assert status == 200
        assert body == "recovered"
        assert server["state"]["calls"] == 3

    def test_give_up_after_retries_503(self, server):
        body, status = httpclient.fetch_with_retry(
            self.base(server, "/always500"), retries=2, backoff=0.01
        )
        # With retries exhausted, the last 5xx response should be returned
        # (we read the error body) instead of raising.
        assert status == 503
        assert body == "unavailable"
        assert server["state"]["calls"] == 3  # initial + 2 retries

    def test_404_not_retried(self, server):
        body, status = httpclient.fetch_with_retry(
            self.base(server, "/notfound"), retries=3, backoff=0.01
        )
        assert status == 404
        assert body == "nope"
        assert server["state"]["calls"] == 1  # no retries on 4xx

    def test_connection_error_gives_up(self, server):
        # A closed port guarantees URLError on every attempt.
        srv = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
        port = srv.server_address[1]
        srv.server_close()
        with pytest.raises(urllib.error.URLError):
            httpclient.fetch_with_retry(f"http://127.0.0.1:{port}/", retries=2, backoff=0.01)


class TestMocked:
    """Tests that stub the urllib layer to inspect retry/backoff behavior."""

    def test_exponential_backoff_delays(self):
        """Verify doubling backoff after each failure with 5xx responses."""
        err500 = urllib.error.HTTPError(
            "http://x/", 500, "err", {}, None
        )

        responses = [err500, err500, err500, 200]
        calls = []
        sleeps = []

        class FakeResponse:
            def __init__(self, code, body=b"ok", content_type="text/plain"):
                self.code = code
                self.body = body
                self.content_type = content_type
                self.headers = {"Content-Type": content_type}

            def read(self):
                return self.body

            def getcode(self):
                return self.code

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake_urlopen(url, timeout=None):
            calls.append((url, time.monotonic()))
            item = responses.pop(0)
            if isinstance(item, int):
                return FakeResponse(item)
            raise item

        with patch("httpclient.urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("httpclient.time.sleep", side_effect=lambda s: sleeps.append(s)):
            body, status = httpclient.fetch_with_retry("http://x/", retries=3, backoff=0.25)

        assert status == 200
        assert len(calls) == 4
        # Three 5xx failures before the final success => three sleeps, doubling.
        assert sleeps == [0.25, 0.5, 1.0]

    def test_4xx_not_retried_even_429_or_400(self):
        """4xx responses return immediately, no retry, no sleep."""
        err400 = urllib.error.HTTPError(
            "http://x/", 400, "bad", {}, None
        )
        calls = []
        sleeps = []

        with patch("httpclient.urllib.request.urlopen", side_effect=err400) as mock_open, \
             patch("httpclient.time.sleep", side_effect=lambda s: sleeps.append(s)):
            body, status = httpclient.fetch_with_retry("http://x/", retries=5, backoff=0.1)

        assert status == 400
        assert mock_open.call_count == 1
        assert sleeps == []

    def test_connection_error_retries_then_raises(self):
        """URLError every time => raises after retries+1 attempts."""
        calls = []
        sleeps = []
        conn_err = urllib.error.URLError("connection refused")

        def fake_urlopen(url, timeout=None):
            calls.append(url)
            raise conn_err

        with patch("httpclient.urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("httpclient.time.sleep", side_effect=lambda s: sleeps.append(s)):
            with pytest.raises(urllib.error.URLError):
                httpclient.fetch_with_retry("http://x/", retries=2, backoff=0.2)

        assert len(calls) == 3  # initial + 2 retries
        assert sleeps == [0.2, 0.4]  # exponential doubling

    def test_give_up_after_retries_on_persistent_5xx(self):
        """Persistent 5xx: after retries+1 attempts the final 5xx body/status is returned."""
        err500 = urllib.error.HTTPError("http://x/", 500, "err", {}, None)
        calls = []
        sleeps = []

        def fake_urlopen(url, timeout=None):
            calls.append(url)
            raise err500

        with patch("httpclient.urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("httpclient.time.sleep", side_effect=lambda s: sleeps.append(s)):
            body, status = httpclient.fetch_with_retry("http://x/", retries=2, backoff=0.1)

        # The HTTPError is created with a None body; err.read() on that
        # yields an empty body, so we assert on call count, status and
        # the exponential sleep schedule.
        assert status == 500
        assert len(calls) == 3  # initial + 2 retries
        assert sleeps == [0.1, 0.2]
