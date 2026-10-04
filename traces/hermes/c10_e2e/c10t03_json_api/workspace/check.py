#!/usr/bin/env python3
"""End-to-end self-check for server.py — standard library only.

Boots the real server in a subprocess on a free port, exercises every
endpoint (including malformed requests and restart persistence), and
asserts. Run with:  python check.py
"""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:{port}"


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(data_file, port):
    proc = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port), "--data-file", data_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    base = BASE.format(port=port)
    deadline = time.time() + 15
    while time.time() < deadline:
        if proc.poll() is not None:
            out = ""
            if proc.stdout and proc.stderr:
                out = proc.stdout.read().decode() + proc.stderr.read().decode()
            raise RuntimeError("server exited early:\n" + out)
        try:
            with urllib.request.urlopen(base + "/health", timeout=1) as r:
                if r.status == 200:
                    return proc, base
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError("server did not become ready in 15s")


def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def req(base, method, path, body=None, raw_body=None):
    """Return (status, parsed_json_or_None, headers)."""
    data = None
    if body is not None:
        data = json.dumps(body).encode()
    if raw_body is not None:
        data = raw_body if isinstance(raw_body, bytes) else raw_body.encode()
    url = base + path
    r = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            payload = resp.read()
            status = resp.status
            headers = dict(resp.headers)
    except urllib.error.HTTPError as e:
        payload = e.read()
        status = e.code
        headers = dict(e.headers)
    parsed = None
    if payload:
        try:
            parsed = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError:
            parsed = None
    return status, parsed, headers


PASS = 0
FAIL = 0
FAILURES = []


def check(label, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {label}")
    else:
        FAIL += 1
        FAILURES.append(f"{label} {detail}")
        print(f"  FAIL {label} {detail}")


def main():
    port = free_port()
    tmp = tempfile.mkdtemp(prefix="jsonapi_")
    data_file = os.path.join(tmp, "items.json")

    proc, base = start_server(data_file, port)
    try:
        print(f"-- server up at {base} (data file {data_file}) --")

        # GET /health
        s, p, _ = req(base, "GET", "/health")
        check("GET /health -> 200", s == 200, f"(got {s})")
        check("GET /health body", p == {"status": "ok"}, f"(got {p!r})")

        # POST /items (valid)
        s, p, _ = req(base, "POST", "/items", body={"name": "apple"})
        check("POST /items -> 201", s == 201, f"(got {s})")
        check("POST body has id/name/created_at",
              isinstance(p, dict) and p.get("id") and p.get("name") == "apple"
              and "created_at" in p, f"(got {p!r})")
        created = p or {}
        item_id = created.get("id", "")

        # POST second item
        s, p, _ = req(base, "POST", "/items", body={"name": "banana"})
        check("POST /items again -> 201", s == 201, f"(got {s})")
        second_id = p.get("id") if isinstance(p, dict) else None

        # GET /items
        s, p, _ = req(base, "GET", "/items")
        check("GET /items -> 200", s == 200, f"(got {s})")
        check("GET /items lists 2 items",
              isinstance(p, list) and [i.get("name") for i in p] == ["apple", "banana"],
              f"(got {p!r})")

        # POST malformed JSON -> 400
        s, p, _ = req(base, "POST", "/items", raw_body="{not json")
        check("POST /items malformed JSON -> 400", s == 400, f"(got {s})")
        check("400 has error field", isinstance(p, dict) and "error" in p, f"(got {p!r})")

        # POST empty body -> 400
        s, _, _ = req(base, "POST", "/items", raw_body="")
        check("POST /items empty body -> 400", s == 400, f"(got {s})")

        # POST missing 'name' -> 400
        s, _, _ = req(base, "POST", "/items", body={"color": "red"})
        check("POST /items missing name -> 400", s == 400, f"(got {s})")

        # POST name not a string -> 400
        s, _, _ = req(base, "POST", "/items", body={"name": 42})
        check("POST /items non-string name -> 400", s == 400, f"(got {s})")

        # GET /items/{id}
        s, p, _ = req(base, "GET", f"/items/{item_id}")
        check("GET /items/{id} -> 200", s == 200, f"(got {s})")
        check("GET /items/{id} returns the item",
              isinstance(p, dict) and p.get("name") == "apple", f"(got {p!r})")

        # GET unknown item -> 404
        s, p, _ = req(base, "GET", "/items/does-not-exist")
        check("GET /items/{unknown} -> 404", s == 404, f"(got {s})")

        # DELETE /items/{id} -> 204
        s, p, _ = req(base, "DELETE", f"/items/{second_id}")
        check("DELETE /items/{id} -> 204", s == 204, f"(got {s})")
        check("204 has empty body", p is None, f"(got {p!r})")

        # GET deleted item -> 404
        s, _, _ = req(base, "GET", f"/items/{second_id}")
        check("GET deleted item -> 404", s == 404, f"(got {s})")

        # DELETE unknown -> 404
        s, _, _ = req(base, "DELETE", "/items/nope")
        check("DELETE /items/{unknown} -> 404", s == 404, f"(got {s})")

        # Unknown path -> 404
        s, _, _ = req(base, "GET", "/nonsense")
        check("GET /nonsense -> 404", s == 404, f"(got {s})")

        # Wrong method -> 405
        s, p, _ = req(base, "POST", "/health")
        check("POST /health -> 405", s == 405, f"(got {s})")
        s, _, _ = req(base, "DELETE", "/items")
        check("DELETE /items -> 405", s == 405, f"(got {s})")

        # Unknown method (e.g. PUT) -> 405, server still alive
        s, _, _ = req(base, "PUT", "/items", body={"name": "c"})
        check("PUT /items -> 405", s == 405, f"(got {s})")

        # Server survived all malformed traffic
        s, _, _ = req(base, "GET", "/health")
        check("server alive after malformed requests", s == 200, f"(got {s})")
    finally:
        stop_server(proc)

    # --- persistence across restart ---
    print("-- restart: verifying persistence --")
    proc2, base2 = start_server(data_file, port)
    try:
        s, p, _ = req(base2, "GET", "/items")
        check("after restart GET /items -> 200", s == 200, f"(got {s})")
        check("after restart only 'apple' remains",
              isinstance(p, list) and [i.get("name") for i in p] == ["apple"],
              f"(got {p!r})")
        s, p, _ = req(base2, "GET", f"/items/{item_id}")
        check("after restart GET /items/{id} -> 200", s == 200, f"(got {s})")
        s, p, _ = req(base2, "POST", "/items", body={"name": "cherry"})
        check("after restart POST -> 201", s == 201, f"(got {s})")
        new_id = p.get("id") if isinstance(p, dict) else None

        # corrupt data file: server must not crash, starts fresh
        s2, p2, _ = req(base2, "DELETE", f"/items/{new_id}")
        check("after restart DELETE -> 204", s2 == 204, f"(got {s2})")
    finally:
        stop_server(proc2)

    print("-- corrupt data file resilience --")
    with open(data_file, "w") as f:
        f.write("{this is not valid json!!")
    proc3, base3 = start_server(data_file, port)
    try:
        s, p, _ = req(base3, "GET", "/items")
        check("corrupt data file -> server boots, empty list",
              s == 200 and p == [], f"(got {s}, {p!r})")
        s, p, _ = req(base3, "POST", "/items", body={"name": "durian"})
        check("corrupt data file -> POST still works", s == 201, f"(got {s})")
    finally:
        stop_server(proc3)

    print(f"\n{'=' * 40}\n{PASS} passed, {FAIL} failed")
    if FAILURES:
        print("Failures:")
        for f_ in FAILURES:
            print(" -", f_)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
