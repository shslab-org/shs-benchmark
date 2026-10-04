"""A JSON API server built exclusively with Python standard library."""

import argparse
import json
import os
import re
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "items.json")


def load_items():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_items(items):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(items, f, indent=2)
    os.replace(tmp, DATA_FILE)


class APIState:
    """Shared in-memory state synced to the JSON file."""

    def __init__(self):
        self.items = load_items()

    def save(self):
        save_items(self.items)


STATE = APIState()


class Handler(BaseHTTPRequestHandler):
    server_version = "StdlibJSONAPI/1.0"

    # Silence default logging
    def log_message(self, fmt, *args):
        pass

    def _send(self, status, body=None, content_type="application/json"):
        self.send_response(status)
        if body is not None:
            payload = json.dumps(body).encode("utf-8")
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.end_headers()

    def _error(self, status, message):
        self._send(status, {"error": message})

    def _not_found(self):
        self._error(404, "not found")

    def _method_not_allowed(self, allowed):
        self._error(405, "method not allowed, allowed: " + ", ".join(allowed))

    def _item_by_id(self, item_id):
        return STATE.items.get(item_id)

    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        if path == "/health":
            self._send(200, {"status": "ok"})
        elif path == "/items":
            self._send(200, sorted(STATE.items.values(), key=lambda i: i.get("created_at", 0)))
        elif m := re.fullmatch(r"/items/([^/]+)", path):
            item = self._item_by_id(m.group(1))
            if item is None:
                self._not_found()
            else:
                self._send(200, item)
        else:
            self._not_found()

    def do_POST(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        if path == "/items":
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                self._error(400, "invalid Content-Length")
                return
            raw = self.rfile.read(length) if length > 0 else b""
            try:
                data = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._error(400, "invalid JSON")
                return
            if not isinstance(data, dict):
                self._error(400, "JSON body must be an object")
                return
            name = data.get("name")
            if not isinstance(name, str) or not name:
                self._error(400, "field 'name' must be a non-empty string")
                return
            item = {"id": str(uuid.uuid4()), "name": name, "created_at": time.time()}
            STATE.items[item["id"]] = item
            STATE.save()
            self._send(201, item)
        else:
            self._method_not_allowed(["GET"])

    def do_DELETE(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        if m := re.fullmatch(r"/items/([^/]+)", path):
            item_id = m.group(1)
            if item_id not in STATE.items:
                self._not_found()
            else:
                del STATE.items[item_id]
                STATE.save()
                self.send_response(204)
                self.end_headers()
        elif path in ("/items", "/health"):
            self._method_not_allowed(["GET", "POST"] if path == "/items" else ["GET"])
        else:
            self._not_found()

    def do_PUT(self):
        self._method_not_allowed(["GET", "POST", "DELETE"])

    def do_PATCH(self):
        self._method_not_allowed(["GET", "POST", "DELETE"])


def main():
    parser = argparse.ArgumentParser(description="Standard-library JSON API server")
    parser.add_argument("--port", type=int, required=True, help="TCP port to bind")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"Serving on port {args.port}, data file: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
