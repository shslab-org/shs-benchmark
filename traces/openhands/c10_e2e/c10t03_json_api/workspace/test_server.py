#!/usr/bin/env python
"""Self-check for server.py: starts the server on a free port and exercises
every endpoint (happy paths, error paths, persistence across restart).

Usage:
    python test_server.py

Exit code 0 = all checks passed; 1 = failure.
"""

from __future__ import annotations

import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(port: int, data_file: str) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, SERVER, "--port", str(port), "--data", data_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_up(port: int, proc: subprocess.Popen | None = None, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc is not None and proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/health")
            conn.getresponse()
            conn.close()
            return
        except (ConnectionRefusedError, OSError):
            time.sleep(0.1)
    raise RuntimeError("server did not start in time")


class Client:
    def __init__(self, port: int) -> None:
        self.port = port

    def request(self, method: str, path: str, body: str | bytes | None = None,
                headers: dict | None = None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        return resp.status, data

    def json(self, method: str, path: str, body: dict | None = None):
        raw = json.dumps(body) if body is not None else None
        status, data = self.request(method, path, raw)
        return status, json.loads(data) if data else None


CHECKS = 0
FAILED: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if ok:
        print(f"  ok  {name}")
    else:
        print(f" FAIL {name} {detail}")
        FAILED.append(name)


def run_all(port: int, data_file: str) -> None:
    c = Client(port)
    wait_up(port, None)

    # --- health ---------------------------------------------------------
    s, body = c.request("GET", "/health")
    check("GET /health -> 200", s == 200, f"status={s}")
    check("GET /health body", body == b'{"status": "ok"}', f"body={body!r}")

    # --- create ---------------------------------------------------------
    s, body = c.json("POST", "/items", {"name": "alpha"})
    check("POST /items -> 201", s == 201, f"status={s}")
    check("POST /items returns created item", isinstance(body, dict) and body.get("name") == "alpha" and body.get("id") == 1, f"body={body}")
    item1 = body

    s, body = c.json("POST", "/items", {"name": "beta"})
    check("POST /items second -> 201", s == 201 and body["id"] == 2, f"status={s} body={body}")
    item2 = body

    # --- invalid JSON / invalid body ------------------------------------
    s, body = c.request("POST", "/items", b"{not json", {"Content-Type": "application/json"})
    check("POST invalid JSON -> 400", s == 400, f"status={s} body={body}")

    s, body = c.request("POST", "/items", b'"just a string"', {"Content-Type": "application/json"})
    check("POST non-object JSON -> 400", s == 400, f"status={s}")

    s, body = c.request("POST", "/items", b"{}", {"Content-Type": "application/json"})
    check("POST missing name -> 400", s == 400, f"status={s}")

    s, body = c.request("POST", "/items", None, {"Content-Type": "application/json"})
    check("POST empty body -> 400", s == 400, f"status={s}")

    # --- list -----------------------------------------------------------
    s, body = c.json("GET", "/items")
    check("GET /items -> 200 list", s == 200, f"status={s}")
    check("GET /items contents", isinstance(body, list) and [i["name"] for i in body] == ["alpha", "beta"], f"body={body}")

    # --- get by id ------------------------------------------------------
    s, body = c.json("GET", f"/items/{item1['id']}")
    check("GET /items/1 -> 200", s == 200, f"status={s}")
    check("GET /items/1 body", body == item1, f"body={body}")

    s, body = c.json("GET", "/items/9999")
    check("GET /items/9999 -> 404", s == 404, f"status={s}")

    s, body = c.request("GET", "/items/abc")
    check("GET /items/abc -> 400 (bad id)", s == 400, f"status={s}")

    # --- delete ---------------------------------------------------------
    s, body = c.request("DELETE", f"/items/{item2['id']}")
    check("DELETE /items/2 -> 204", s == 204, f"status={s} body={body}")
    check("DELETE /items/2 no body", body == b"", f"body={body!r}")

    s, body = c.request("DELETE", "/items/9999")
    check("DELETE missing -> 404", s == 404, f"status={s}")

    s, body = c.json("GET", "/items")
    check("list after delete", isinstance(body, list) and [i["name"] for i in body] == ["alpha"], f"body={body}")

    # --- unknown routes / wrong methods ----------------------------------
    s, body = c.request("GET", "/nope")
    check("GET /nope -> 404", s == 404, f"status={s}")

    s, body = c.request("POST", "/health", b"{}")
    check("POST /health -> 404/405", s in (404, 405), f"status={s}")

    s, body = c.request("PUT", "/items", b'{"name": "x"}')
    check("PUT /items -> 405", s == 405, f"status={s}")

    s, body = c.request("PUT", f"/items/{item1['id']}", b'{"name": "x"}')
    check("PUT /items/1 -> 405", s == 405, f"status={s}")

    s, body = c.request("DELETE", "/items", b"")
    check("DELETE /items -> 404/405", s in (404, 405), f"status={s}")

    # --- persistence to disk ---------------------------------------------
    with open(data_file, "r", encoding="utf-8") as f:
        on_disk = json.load(f)
    check("data file has expected content", on_disk == {"1": {"id": 1, "name": "alpha"}}, f"disk={on_disk}")


def restart_persistence(port: int, data_file: str, proc: subprocess.Popen) -> None:
    """Stop the server, restart with the same data file, verify items persist."""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    proc2 = start_server(port, data_file)
    c = Client(port)
    try:
        wait_up(port, proc2)
        s, body = c.json("GET", "/items")
        check("GET /items after restart -> 200", s == 200, f"status={s}")
        check("items persisted across restart",
              isinstance(body, list) and [i["name"] for i in body] == ["alpha"], f"body={body}")

        # ids continue after restart (no id collision): only item id 1 remains on disk,
        # so the next created id must be 2
        s, body = c.json("POST", "/items", {"name": "gamma"})
        check("POST after restart -> 201 with new id", s == 201 and body["id"] == 2, f"status={s} body={body}")
    finally:
        proc2.terminate()
        try:
            proc2.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc2.kill()


def main() -> int:
    tmpdir = tempfile.mkdtemp(prefix="json-api-test-")
    data_file = os.path.join(tmpdir, "items.json")
    port = free_port()

    proc = start_server(port, data_file)
    try:
        run_all(port, data_file)
        restart_persistence(port, data_file, proc)
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    print(f"\n{CHECKS} checks, {len(FAILED)} failures")
    if FAILED:
        print("FAILED: " + ", ".join(FAILED))
        return 1
    print("ALL CHECKS PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
