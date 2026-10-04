"""Integration tests for the stdlib JSON API server.

Spawns `server.py` as a real subprocess on a free port and exercises every
endpoint over HTTP. Also verifies persistence across a server restart.
"""

import json
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.py"


class ServerProc:
    """Manages a server subprocess on a chosen port."""

    def __init__(self, port: int, data_file: Path):
        self.port = port
        self.data_file = data_file
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER),
             "--port", str(port), "--data", str(data_file)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 15
        while time.time() < deadline:
            if self._alive():
                return
            if self.proc.poll() is not None:
                raise RuntimeError(f"server exited early: {self.proc.returncode}")
            time.sleep(0.1)
        raise RuntimeError("server did not become ready in time")

    def _alive(self) -> bool:
        try:
            urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/health", timeout=2)
            return True
        except urllib.error.HTTPError:
            return True  # a 4xx means the server answered
        except Exception:
            return False

    def stop(self) -> None:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)

    def __enter__(self) -> "ServerProc":
        return self

    def __exit__(self, *exc) -> None:
        self.stop()


def req(method: str, url: str, body: bytes | None = None,
        headers: dict | None = None):
    h = dict(headers or {})
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=10)
        raw = resp.read()
        return resp.status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def parse(raw: bytes) -> object:
    return json.loads(raw.decode("utf-8")) if raw else None


def find_free_port() -> int:
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_all_endpoints():
    port = find_free_port()
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "items.json"
        base = f"http://127.0.0.1:{port}"
        with ServerProc(port, data) as srv:
            # GET /health
            code, raw = req("GET", base + "/health")
            assert code == 200, (code, raw)
            assert parse(raw) == {"status": "ok"}

            # GET /items (empty)
            code, raw = req("GET", base + "/items")
            assert code == 200 and parse(raw) == [], (code, raw)

            # POST /items (valid)
            body = json.dumps({"name": "first"}).encode()
            code, raw = req("POST", base + "/items", body,
                            {"Content-Type": "application/json"})
            assert code == 201, (code, raw)
            item = parse(raw)
            assert item == {"name": "first", "id": 1}, item
            item_id = item["id"]

            # POST /items (second, with extra fields)
            code, raw = req("POST", base + "/items",
                            json.dumps({"name": "second", "qty": 3}).encode(),
                            {"Content-Type": "application/json"})
            assert code == 201
            assert parse(raw) == {"name": "second", "qty": 3, "id": 2}

            # GET /items (list)
            code, raw = req("GET", base + "/items")
            assert code == 200
            items = parse(raw)
            assert [i["name"] for i in items] == ["first", "second"], items
            assert [i["id"] for i in items] == [1, 2]

            # GET /items/{id}
            code, raw = req("GET", base + f"/items/{item_id}")
            assert code == 200
            assert parse(raw) == {"name": "first", "id": 1}

            # GET /items/9999 -> 404
            code, raw = req("GET", base + "/items/9999")
            assert code == 404, (code, raw)

            # POST /items with malformed JSON -> 400
            code, raw = req("POST", base + "/items", b"not json{{",
                            {"Content-Type": "application/json"})
            assert code == 400, (code, raw)

            # POST /items with JSON array -> 400
            code, raw = req("POST", base + "/items", b"[1,2]",
                            {"Content-Type": "application/json"})
            assert code == 400

            # POST /items missing 'name' -> 400
            code, raw = req("POST", base + "/items", b"{}",
                            {"Content-Type": "application/json"})
            assert code == 400

            # POST /items with empty body -> 400
            code, raw = req("POST", base + "/items", b"",
                            {"Content-Type": "application/json"})
            assert code == 400

            # DELETE /items/{id} -> 204
            code, raw = req("DELETE", base + f"/items/{item_id}")
            assert code == 204 and raw == b"", (code, raw)

            # GET deleted item -> 404
            code, raw = req("GET", base + f"/items/{item_id}")
            assert code == 404

            # DELETE again -> 404
            code, raw = req("DELETE", base + f"/items/{item_id}")
            assert code == 404

            # Unknown path -> 404
            code, raw = req("GET", base + "/nope")
            assert code == 404

            # Method not allowed -> 405
            code, raw = req("POST", base + "/health", b"{}")
            assert code == 405, (code, raw)
            code, raw = req("DELETE", base + "/items")
            assert code == 405, (code, raw)
            code, raw = req("GET", base + "/items/abc")
            assert code == 405, (code, raw)  # non-numeric id -> 405

            # Verify persistence file written
            assert data.exists()
            stored = json.loads(data.read_text())
            assert "2" in stored

        # Persistence across a real restart: start again on same data file
        with ServerProc(port, data) as srv2:
            code, raw = req("GET", f"http://127.0.0.1:{port}/items")
            assert code == 200
            items = parse(raw)
            assert [i["id"] for i in items] == [2], items
            assert items[0]["name"] == "second"
            # New id continues from where it left off
            code, raw = req("POST",
                            f"http://127.0.0.1:{port}/items",
                            json.dumps({"name": "third"}).encode(),
                            {"Content-Type": "application/json"})
            assert code == 201
            assert parse(raw) == {"name": "third", "id": 3}


if __name__ == "__main__":
    test_all_endpoints()
    print("ALL ENDPOINT TESTS PASSED")
