#!/usr/bin/env python3
"""JSON API server built exclusively on the Python standard library.

Endpoints:
    GET    /health        -> 200 {"status": "ok"}
    GET    /items         -> 200 [item, ...]
    POST   /items         -> 201 created item | 400 invalid body
    GET    /items/{id}    -> 200 item | 404 missing
    DELETE /items/{id}    -> 204 | 404 missing

Items are persisted to a JSON file so data survives restarts.
Run with:  python server.py --port N [--host H] [--data-file FILE]
"""

import argparse
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

DEFAULT_DATA_FILE = "items.json"


class ItemStore:
    """Thread-safe in-memory item store backed by a JSON file."""

    def __init__(self, path):
        self._path = path
        self._lock = threading.Lock()
        self._items = {}
        self._load()

    def _load(self):
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", {})
            if isinstance(items, dict):
                self._items = {str(k): dict(v) for k, v in items.items()}
        except (json.JSONDecodeError, OSError, TypeError, AttributeError):
            # Corrupt/unreadable data file: start fresh rather than crash.
            self._items = {}

    def _save(self):
        """Write atomically (temp file + rename) so restarts never see a torn file."""
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"items": self._items}, f, indent=2)
            f.write("\n")
        os.replace(tmp, self._path)

    def all_items(self):
        with self._lock:
            ordered = sorted(
                self._items.values(),
                key=lambda v: (v.get("created_at", ""), v.get("id", "")),
            )
            return [dict(v) for v in ordered]

    def get(self, item_id):
        with self._lock:
            item = self._items.get(str(item_id))
            return dict(item) if item else None

    def create(self, name):
        with self._lock:
            item = {
                "id": uuid.uuid4().hex,
                "name": name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            self._items[item["id"]] = item
            self._save()
            return dict(item)

    def delete(self, item_id):
        with self._lock:
            item_id = str(item_id)
            if item_id not in self._items:
                return False
            del self._items[item_id]
            self._save()
            return True


class ApiHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "StdlibJsonApi/1.0"
    store = None  # injected by main()

    # --- quiet default logging (stderr noise) -------------------------------
    def log_message(self, fmt, *args):
        pass

    # --- response helpers ----------------------------------------------------
    def _send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json_error(self, code, message, allow=None):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(code)
        if allow:
            self.send_header("Allow", allow)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_no_content(self):
        self.send_response(204)
        self.end_headers()

    def _not_found(self):
        self._send_json_error(404, "not found")

    # --- body parsing --------------------------------------------------------
    def _read_json_body(self):
        """Return (payload, error_message). payload is None when invalid."""
        raw = b""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            length = 0
        if length > 0:
            try:
                raw = self.rfile.read(length)
            except OSError:
                return None, "could not read request body"
        if not raw:
            return None, "request body must be valid JSON"
        try:
            return json.loads(raw.decode("utf-8")), None
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None, "request body must be valid JSON"

    # --- routing ---------------------------------------------------------------
    def _dispatch(self, method):
        try:
            path = urlparse(self.path).path if self.path else "/"
            segments = [s for s in path.split("/") if s]

            if segments == ["health"]:
                if method == "GET":
                    self._send_json(200, {"status": "ok"})
                else:
                    self._send_json_error(405, "method not allowed", allow="GET")
            elif segments == ["items"]:
                if method == "GET":
                    self._send_json(200, self.store.all_items())
                elif method == "POST":
                    self._create_item()
                else:
                    self._send_json_error(405, "method not allowed", allow="GET, POST")
            elif len(segments) == 2 and segments[0] == "items":
                self._dispatch_item(segments[1], method)
            else:
                self._not_found()
        except (BrokenPipeError, ConnectionResetError):
            pass  # client went away; nothing to do
        except Exception:
            # Never let a bad request crash the server: 500 instead.
            try:
                self._send_json_error(500, "internal server error")
            except OSError:
                pass

    def _dispatch_item(self, item_id, method):
        if method == "GET":
            item = self.store.get(item_id)
            if item is None:
                self._send_json_error(404, "item not found")
            else:
                self._send_json(200, item)
        elif method == "DELETE":
            if self.store.delete(item_id):
                self._send_no_content()
            else:
                self._send_json_error(404, "item not found")
        else:
            self._send_json_error(405, "method not allowed", allow="GET, DELETE")

    def _create_item(self):
        payload, error = self._read_json_body()
        if payload is None:
            self._send_json_error(400, error)
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("name"), str) or not payload["name"].strip():
            self._send_json_error(400, '"name" is required and must be a non-empty string')
            return
        item = self.store.create(payload["name"])
        self._send_json(201, item)

    # --- HTTP verbs ------------------------------------------------------------
    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_DELETE(self):
        self._dispatch("DELETE")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_PATCH(self):
        self._dispatch("PATCH")

    def do_HEAD(self):
        self._dispatch("HEAD")

    def do_OPTIONS(self):
        self._dispatch("OPTIONS")


def main():
    parser = argparse.ArgumentParser(description="std-library-only JSON API server")
    parser.add_argument("--port", type=int, default=8000, help="port to listen on (default 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default 127.0.0.1)")
    parser.add_argument("--data-file", default=DEFAULT_DATA_FILE,
                        help="JSON file used to persist items (default items.json)")
    args = parser.parse_args()

    store = ItemStore(args.data_file)
    ApiHandler.store = store

    server = ThreadingHTTPServer((args.host, args.port), ApiHandler)
    print(f"JSON API listening on http://{args.host}:{args.port} (data file: {args.data_file})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
