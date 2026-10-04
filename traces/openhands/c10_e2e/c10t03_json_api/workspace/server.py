#!/usr/bin/env python
"""Minimal JSON API server using only the Python standard library.

Endpoints:
    GET    /health      -> 200 {"status": "ok"}
    GET    /items       -> 200 [item, ...]
    POST   /items       -> 201 created item (accepts {"name": ...}); 400 on invalid JSON
    GET    /items/{id}  -> 200 item | 404 when missing
    DELETE /items/{id}  -> 204 | 404

Items persist to a JSON file so data survives restarts. Malformed requests
are answered with 400/404/405 -- the server never crashes on bad input.

Usage:
    python server.py --port N [--data FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

DEFAULT_DATA_FILE = "items.json"


def load_items(data_file: str) -> dict:
    """Load items from the JSON data file; return empty mapping if absent/corrupt."""
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_items(data_file: str, items: dict) -> None:
    """Atomically persist items to the JSON data file."""
    directory = os.path.dirname(os.path.abspath(data_file))
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".items-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, data_file)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


class ItemStore:
    """Thread-safe store of items persisted to a JSON file."""

    def __init__(self, data_file: str) -> None:
        self._lock = threading.Lock()
        self._data_file = data_file
        self._items: dict = load_items(data_file)
        self._next_id = max((it["id"] for it in self._items.values()
                             if isinstance(it, dict) and isinstance(it.get("id"), int)), default=0) + 1

    def list(self) -> list:
        with self._lock:

            def key(k: str) -> int:
                return int(k) if k.isdigit() else 1 << 30

            return [self._items[k] for k in sorted(self._items, key=key)]

    def get(self, item_id: int):
        with self._lock:
            return self._items.get(str(item_id))

    def create(self, name: str) -> dict:
        with self._lock:
            item = {"id": self._next_id, "name": name}
            self._items[str(self._next_id)] = item
            self._next_id += 1
            save_items(self._data_file, self._items)
            return item

    def delete(self, item_id: int) -> bool:
        with self._lock:
            if str(item_id) in self._items:
                del self._items[str(item_id)]
                save_items(self._data_file, self._items)
                return True
            return False

    def reset_for_test(self, items: list, data_file: str | None = None) -> None:
        """Test helper: replace items wholesale (optionally repointing the file)."""
        with self._lock:
            if data_file is not None:
                self._data_file = data_file
            self._items = {str(it["id"]): it for it in items}
            self._next_id = max((it["id"] for it in items), default=0) + 1
            save_items(self._data_file, self._items)


def parse_item_id(raw: str) -> int | None:
    """Return the item id if raw is a positive integer string, else None."""
    if not raw.isdigit():
        return None
    value = int(raw)
    return value if value >= 1 else None


class ApiHandler(BaseHTTPRequestHandler):
    """HTTP request handler. All error paths return JSON or 204; no crash."""

    server_version = "StdLibJsonAPI/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - keep base signature
        # Default writes to stderr on every request; keep it but prefix for greppability.
        sys.stderr.write("[server] %s - %s\n" % (self.address_string(), format % args))

    # -- helpers -----------------------------------------------------------

    @property
    def store(self) -> ItemStore:
        return self.server.store  # type: ignore[attr-defined]

    def _send_json(self, status: int, payload) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status: int, message: str) -> None:
        self._send_json(status, {"error": message})

    def _send_no_content(self) -> None:
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -- request parsing ---------------------------------------------------

    def _read_body(self) -> bytes | None:
        """Read request body; returns None when length is missing or invalid."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None
        if length < 0:
            return None
        return self.rfile.read(length) if length else b""

    def _path_parts(self) -> list[str]:
        path = self.path.split("?", 1)[0]
        return [unquote(p) for p in path.split("/") if p != ""]

    # -- method dispatch ---------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        try:
            self._handle_get()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            # Never crash on a request; report a 500 instead.
            try:
                self._send_error_json(500, "Internal server error")
            except Exception:
                pass

    def do_POST(self) -> None:  # noqa: N802
        self._safe("POST")

    def do_DELETE(self) -> None:  # noqa: N802
        self._safe("DELETE")

    def do_PUT(self) -> None:  # noqa: N802
        self._safe("PUT")

    def do_PATCH(self) -> None:  # noqa: N802
        self._safe("PATCH")

    def do_HEAD(self) -> None:  # noqa: N802
        self._safe("HEAD")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._safe("OPTIONS")

    def _safe(self, method: str) -> None:
        try:
            getattr(self, f"_handle_{method.lower()}")()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            try:
                self._send_error_json(500, "Internal server error")
            except Exception:
                pass

    # -- GET ---------------------------------------------------------------

    def _handle_get(self) -> None:
        parts = self._path_parts()
        if parts == ["health"]:
            self._send_json(200, {"status": "ok"})
        elif parts == ["items"]:
            self._send_json(200, self.store.list())
        elif len(parts) == 2 and parts[0] == "items":
            item_id = parse_item_id(parts[1])
            if item_id is None:
                self._send_error_json(400, "Item id must be a positive integer")
                return
            item = self.store.get(item_id)
            if item is None:
                self._send_error_json(404, f"Item {item_id} not found")
            else:
                self._send_json(200, item)
        else:
            self._send_error_json(404, "Not found")

    # -- POST --------------------------------------------------------------

    def _handle_post(self) -> None:
        parts = self._path_parts()
        if parts != ["items"]:
            self._send_error_json(404, "Not found")
            return

        body = self._read_body()
        if body is None:
            self._send_error_json(400, "Invalid Content-Length header")
            return

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_error_json(400, "Request body is not valid JSON")
            return

        if not isinstance(payload, dict):
            self._send_error_json(400, "Request body must be a JSON object")
            return

        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            self._send_error_json(400, "Field 'name' must be a non-empty string")
            return

        try:
            item = self.store.create(name.strip())
            self._send_json(201, item)
        except OSError:
            self._send_error_json(500, "Failed to persist item")

    # -- DELETE ------------------------------------------------------------

    def _handle_delete(self) -> None:
        parts = self._path_parts()
        if len(parts) != 2 or parts[0] != "items":
            self._send_error_json(404, "Not found")
            return
        item_id = parse_item_id(parts[1])
        if item_id is None:
            self._send_error_json(400, "Item id must be a positive integer")
            return
        if self.store.delete(item_id):
            self._send_no_content()
        else:
            self._send_error_json(404, f"Item {item_id} not found")

    # -- unsupported methods ------------------------------------------------

    def _method_not_allowed(self, allowed: list[str]) -> None:
        self.send_response(405)
        self.send_header("Allow", ", ".join(allowed))
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _handle_put(self) -> None:
        parts = self._path_parts()
        if parts == ["health"]:
            self._method_not_allowed(["GET"])
        elif parts == ["items"]:
            self._method_not_allowed(["GET", "POST"])
        elif len(parts) == 2 and parts[0] == "items":
            self._method_not_allowed(["GET", "DELETE"])
        else:
            self._send_error_json(404, "Not found")

    def _handle_patch(self) -> None:
        self._handle_put()

    def _handle_head(self) -> None:
        # HEAD mirrors GET but without a body.
        parts = self._path_parts()
        if parts == ["health"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif parts == ["items"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif len(parts) == 2 and parts[0] == "items":
            self.send_response(200 if self.store.get(parse_item_id(parts[1]) or -1) else 404)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def _handle_options(self) -> None:
        parts = self._path_parts()
        if parts == ["health"]:
            allow = ["GET", "HEAD", "OPTIONS"]
        elif parts == ["items"]:
            allow = ["GET", "POST", "HEAD", "OPTIONS"]
        elif len(parts) == 2 and parts[0] == "items":
            allow = ["GET", "DELETE", "HEAD", "OPTIONS"]
        else:
            self._send_error_json(404, "Not found")
            return
        self.send_response(200)
        self.send_header("Allow", ", ".join(allow))
        self.send_header("Content-Length", "0")
        self.end_headers()


class ApiServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, host: str, port: int, data_file: str) -> None:
        super().__init__((host, port), ApiHandler)
        self.store = ItemStore(data_file)
        self.data_file = data_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Standard-library JSON API server")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default 127.0.0.1)")
    parser.add_argument("--data", default=DEFAULT_DATA_FILE, help="Path to the JSON data file")
    args = parser.parse_args(argv)

    server = ApiServer(args.host, args.port, args.data)
    print(f"Serving on http://{args.host}:{args.port} (data file: {os.path.abspath(args.data)})", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
