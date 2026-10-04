"""Self-check: starts server.py on a free port, exercises every endpoint,
asserts behavior, and verifies persistence across a restart. Run:

    python self_check.py
"""

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")
DATA = os.path.join(HERE, "items.json")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(port):
    proc = subprocess.Popen(
        [sys.executable, SERVER, "--port", str(port)],
        cwd=HERE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1):
                return proc
        except (urllib.error.URLError, ConnectionError, OSError):
            if proc.poll() is not None:
                raise RuntimeError("server exited early: " + proc.stderr.read().decode())
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError("server did not come up in time")


def stop_server(proc):
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def request(port, method, path, body=None, raw_body=None):
    url = f"http://127.0.0.1:{port}{path}"
    data = None
    headers = {}
    if raw_body is not None:
        data = raw_body
        headers["Content-Type"] = "application/json"
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return e.code, raw.decode("utf-8", "replace")


CHECKS = []


def check(name, fn):
    fn()
    CHECKS.append(name)
    print(f"  ok: {name}")


def main():
    if os.path.exists(DATA):
        os.remove(DATA)

    port = free_port()
    proc = start_server(port)
    base = lambda path: f"/{path.lstrip('/')}"
    print(f"Server up on port {port}")

    def c_health():
        status, body = request(port, "GET", "/health")
        assert status == 200, f"expected 200 got {status}"
        assert body == {"status": "ok"}, f"unexpected body: {body}"

    def c_get_items_empty():
        status, body = request(port, "GET", "/items")
        assert status == 200, f"expected 200 got {status}"
        assert body == [], f"expected empty list got {body}"

    created = {}

    def c_post_item():
        status, body = request(port, "POST", "/items", body={"name": "apple"})
        assert status == 201, f"expected 201 got {status}"
        assert body["name"] == "apple"
        assert "id" in body
        created["apple"] = body["id"]

    def c_post_second():
        status, body = request(port, "POST", "/items", body={"name": "banana"})
        assert status == 201, f"expected 201 got {status}"
        created["banana"] = body["id"]

    def c_get_items_two():
        status, body = request(port, "GET", "/items")
        assert status == 200
        names = sorted(i["name"] for i in body)
        assert names == ["apple", "banana"], f"unexpected items: {names}"

    def c_get_item():
        status, body = request(port, "GET", f"/items/{created['apple']}")
        assert status == 200, f"expected 200 got {status}"
        assert body["name"] == "apple"
        assert body["id"] == created["apple"]

    def c_get_missing_item():
        status, _ = request(port, "GET", "/items/does-not-exist")
        assert status == 404, f"expected 404 got {status}"

    def c_post_invalid_json():
        status, body = request(port, "POST", "/items", raw_body=b"{not valid json")
        assert status == 400, f"expected 400 got {status}"
        assert "error" in body

    def c_post_missing_name():
        status, _ = request(port, "POST", "/items", body={"foo": "bar"})
        assert status == 400, f"expected 400 got {status}"

    def c_post_empty_name():
        status, _ = request(port, "POST", "/items", body={"name": ""})
        assert status == 400, f"expected 400 got {status}"

    def c_post_non_object():
        status, _ = request(port, "POST", "/items", raw_body=b'"just a string"')
        assert status == 400, f"expected 400 got {status}"

    def c_unknown_route():
        status, _ = request(port, "GET", "/nope")
        assert status == 404, f"expected 404 got {status}"

    def c_wrong_method():
        status, _ = request(port, "PUT", "/items")
        assert status == 405, f"expected 405 got {status}"
        status, _ = request(port, "DELETE", "/health")
        assert status == 405, f"expected 405 got {status}"

    def c_delete_item():
        status, _ = request(port, "DELETE", f"/items/{created['banana']}")
        assert status == 204, f"expected 204 got {status}"

    def c_delete_missing():
        status, _ = request(port, "DELETE", "/items/never-created")
        assert status == 404, f"expected 404 got {status}"

    def c_items_after_delete():
        status, body = request(port, "GET", "/items")
        assert status == 200
        names = [i["name"] for i in body]
        assert names == ["apple"], f"expected ['apple'] got {names}"

    for name, fn in [
        ("GET /health -> 200 ok", c_health),
        ("GET /items (empty) -> 200 []", c_get_items_empty),
        ("POST /items valid -> 201", c_post_item),
        ("POST /items second -> 201", c_post_second),
        ("GET /items lists created", c_get_items_two),
        ("GET /items/{id} -> 200", c_get_item),
        ("GET /items/{unknown} -> 404", c_get_missing_item),
        ("POST /items bad JSON -> 400", c_post_invalid_json),
        ("POST /items missing name -> 400", c_post_missing_name),
        ("POST /items empty name -> 400", c_post_empty_name),
        ("POST /items non-object body -> 400", c_post_non_object),
        ("GET /unknown -> 404", c_unknown_route),
        ("PUT /items -> 405, DELETE /health -> 405", c_wrong_method),
        ("DELETE /items/{id} -> 204", c_delete_item),
        ("DELETE /items/{unknown} -> 404", c_delete_missing),
        ("GET /items reflects delete", c_items_after_delete),
    ]:
        check(name, fn)

    # --- restart persistence ---
    stop_server(proc)
    print("Server stopped; restarting to verify persistence")
    proc = start_server(port)
    try:
        def c_persisted():
            status, body = request(port, "GET", "/items")
            assert status == 200
            ids = [i["id"] for i in body]
            assert created["apple"] in ids, "apple survived restart"
            assert created["banana"] not in ids, "banana was deleted and stayed gone"

        def c_persisted_file():
            with open(DATA) as f:
                data = json.load(f)
            assert created["apple"] in data
            assert created["banana"] not in data

        check("data persists across restart (API)", c_persisted)
        check("data persists across restart (items.json)", c_persisted_file)
    finally:
        stop_server(proc)

    print(f"\nAll {len(CHECKS)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
