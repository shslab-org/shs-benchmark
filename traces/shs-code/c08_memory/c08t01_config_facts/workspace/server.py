"""Service bootstrap for the PURPLE-TIGER service.

Starts a lightweight HTTP server on the configured port (8734) and
registers a health-check endpoint that uses the `http_client` module's
`requests`-based helpers internally to verify connectivity.
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import config
import http_client


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    """Handles requests for the PURPLE-TIGER service."""

    server_version = "PURPLE-TIGER/1.0"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") in ("/health", ""):
            self._send_json(200, {
                "service": config.CODENAME,
                "port": config.get_port(),
                "status": "ok",
                "timestamp": time.time(),
            })
        elif self.path.startswith("/echo/"):
            # Echo back the path fragment as JSON
            fragment = self.path[len("/echo/"):]
            self._send_json(200, {"echo": fragment})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return
        self._send_json(200, {"received": body})

    def log_message(self, fmt: str, *args: Any) -> None:  # silence default log
        pass


# ---------------------------------------------------------------------------
# Bootstrap helpers
# ---------------------------------------------------------------------------

def _health_check(base_url: str = config.BASE_URL) -> bool:
    """Use the requests-based http_client to verify the service is up."""
    client = http_client.HttpClient(base_url=base_url)
    try:
        resp = client.get("/health")
        return resp.status_code == 200
    except Exception:
        return False


def start_service(port: int | None = None, *, wait: float = 0.5) -> ThreadingHTTPServer:
    """Start the PURPLE-TIGER service on *port* and return the server.

    The server runs in a daemon thread so the main thread is not blocked.
    After starting, a health check is performed via `http_client`.

    Parameters
    ----------
    port:
        Port to bind. Defaults to ``config.SERVICE_PORT`` (8734).
    wait:
        Seconds to wait before the health check (default 0.5 s).

    Returns
    -------
    ThreadingHTTPServer
        The running server instance. Call ``server.shutdown()`` to stop.
    """
    port = port or config.get_port()
    server = ThreadingHTTPServer(
        (config.SERVICE_HOST, port),
        _Handler,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    # Give the server a moment to bind before health-checking
    time.sleep(wait)
    ok = _health_check()
    if not ok:
        print(f"[{config.CODENAME}] WARNING: health check failed "
              f"(service may still be binding)")
    else:
        print(f"[{config.CODENAME}] service healthy on port {port}")

    return server


def main() -> None:
    """Entry point: start the service and block."""
    server = start_service()
    try:
        threading.Event().wait()  # block forever
    except KeyboardInterrupt:
        print(f"\n[{config.CODENAME}] shutting down")
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
