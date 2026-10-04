#!/usr/bin/env python3
"""A tiny JSON API server built on the Python standard library only.

Endpoints
---------
GET    /health        -> 200 {"status": "ok"}
GET    /items         -> 200 [item, ...]
POST   /items         -> 201 created item   (400 on invalid JSON / payload)
GET    /items/{id}    -> 200 item | 404 when missing
DELETE /items/{id}    -> 204  | 404 when missing

Items persist to a JSON file so a restart keeps all data.
Run:  python server.py --port 8000 [--data ./items_data.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


class ItemStore:
    """A JSON-file-backed store of items: {str_id: item_dict}."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self._next_id = 0
        self._items: dict[str, dict[str, Any]] = {}
        self._load()

    # -- persistence ---------------------------------------------------------

    def _load(self) -> None:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._items = {str(k): v for k, v in raw.items()}
                    ids = [int(k) for k in self._items if str(k).isdigit()]
                    self._next_id = (max(ids) + 1) if ids else 1
                else:
                    # Malformed shape — start fresh but keep the file.
                    self._items = {}
                    self._next_id = 1
            except (json.JSONDecodeError, OSError):
                # Corrupt file — start from an empty store.
                self._items = {}
                self._next_id = 1
        else:
            self._items = {}
            self._next_id = 1

    def _save_locked(self) -> None:
        """Atomically write the store to disk. Caller holds self._lock."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".items_", suffix=".tmp"
        )
        try:
            with open(fd, "w", encoding="utf-8") as fh:
                json.dump(self._items, fh, indent=2)
            Path(tmp_name).replace(self.path)
        except BaseException:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except OSError:
                pass
            raise

    # -- API -----------------------------------------------------------------

    def list_items(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(item, id=int(k)) for k, item in self._items.items()
                    if str(k).isdigit()] + [
                dict(item, id=k) for k, item in self._items.items()
                if not str(k).isdigit()
            ]

    def get(self, item_id: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._items.get(str(item_id))
            if item is None:
                return None
            id_value = int(item_id) if str(item_id).isdigit() else item_id
            return dict(item, id=id_value)

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            item = dict(payload)
            item["id"] = self._next_id
            self._next_id += 1
            self._items[str(item["id"])] = item
            self._save_locked()
            return item

    def delete(self, item_id: str) -> bool:
        with self._lock:
            if str(item_id) not in self._items:
                return False
            del self._items[str(item_id)]
            self._save_locked()
            return True


_ITEM_ID_RE = re.compile(r"^\d+$")


def _item_id_from_path(path: str) -> str | None:
    """Return the numeric id part of /items/{id}, or None if the path
    does not match that exact shape."""
    if not path.startswith("/items/"):
        return None
    candidate = path[len("/items/"):]
    if not candidate or "/" in candidate or not _ITEM_ID_RE.match(candidate):
        return None
    return candidate


class ApiHandler(BaseHTTPRequestHandler):
    """HTTP handler routing requests against a shared ItemStore."""

    server: "ApiServer"  # type: ignore[assignment]

    # -- helpers -------------------------------------------------------------

    def _send_json(self, status: int, body: Any) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_empty(self, status: int) -> None:
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _path(self) -> str:
        # Normalize: strip query string, collapse duplicate slashes,
        # ensure a trailing slash so "/items" and "/items/" behave the same.
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if len(path) > 1:
            path = re.sub(r"//+", "/", path)
        if not path.endswith("/") and path not in ("/", "/items", "/health"):
            pass  # trailing slash not required for our routes
        return path

    def _read_body(self) -> bytes:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length < 0:
            return b""
        return self.rfile.read(length) if length else b""

    # -- methods -------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        path = self._path()
        if path in ("/health", "/health/"):
            self._send_json(200, {"status": "ok"})
            return
        if path in ("/items", "/items/"):
            self._send_json(200, self.server.store.list_items())
            return
        if path.startswith("/items/"):
            item_id = _item_id_from_path(path)
            if item_id is not None:
                item = self.server.store.get(item_id)
                if item is None:
                    self._send_json(404, {"error": "item not found"})
                else:
                    self._send_json(200, item)
                return
            # /items/{non-numeric} — known shape, wrong method for GET
            self._send_json(405, {"error": "method not allowed"})
            return
        # Truly unknown path
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = self._path()
        if path in ("/items", "/items/"):
            raw = self._read_body()
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else None
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(400, {"error": "invalid JSON body"})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"error": "body must be a JSON object"})
                return
            if "name" not in payload:
                self._send_json(400, {"error": "'name' field is required"})
                return
            item = self.server.store.create(payload)
            self._send_json(201, item)
            return
        self._send_json(405, {"error": "method not allowed"})

    def do_DELETE(self) -> None:  # noqa: N802
        path = self._path()
        if path.startswith("/items/"):
            item_id = _item_id_from_path(path)
            if item_id is not None:
                if self.server.store.delete(item_id):
                    self._send_empty(204)
                else:
                    self._send_json(404, {"error": "item not found"})
                return
        self._send_json(405, {"error": "method not allowed"})

    # -- keep logs terse -----------------------------------------------------

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[api] " + (fmt % args) + "\n")


class ApiServer:
    """Wrapper around ThreadingHTTPServer holding the shared ItemStore."""

    def __init__(self, port: int, store: ItemStore) -> None:
        self.store = store
        self.port = port
        server = self  # the handler's self.server is the ThreadingHTTPServer

        class BoundHandler(ApiHandler):
            pass

        self.httpd = ThreadingHTTPServer(("0.0.0.0", port), BoundHandler)
        self.httpd._api_server = self
        self.httpd.store = store
        self.httpd.allow_reuse_address = True

    def serve_forever(self) -> None:
        self.httpd.serve_forever()

    def shutdown(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


def make_server(port: int, data_file: Path) -> ApiServer:
    return ApiServer(port=port, store=ItemStore(data_file))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tiny JSON API server")
    parser.add_argument("--port", type=int, default=8000,
                        help="port to listen on (default 8000)")
    parser.add_argument("--data", type=Path,
                        default=Path(__file__).resolve().parent / "items_data.json",
                        help="path to the JSON persistence file")
    args = parser.parse_args(argv)

    server = make_server(args.port, args.data)
    print(f"Serving on http://127.0.0.1:{args.port} (data: {args.data})",
          file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down", file=sys.stderr)
    finally:
        server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
