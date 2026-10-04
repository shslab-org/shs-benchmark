#!/usr/bin/env python3
import json, os, sys, time, urllib.request, socket, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c10t03"
checks = []
srv = vlib.find_file(ws, "server.py") or vlib.find_file(ws, "app.py")
checks.append({"name": "server module exists", "ok": bool(srv), "points": 4, "detail": str(srv)})
if srv:
    port = 18973
    proc = subprocess.Popen([sys.executable, srv, "--port", str(port)], cwd=os.path.dirname(srv),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = False
    try:
        time.sleep(2.0)
        def req(method, path, body=None):
            r = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                       data=json.dumps(body).encode() if body else None,
                                       headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(r, timeout=5) as resp:
                    return resp.status, resp.read()
            except urllib.error.HTTPError as e:
                return e.code, e.read()
        s, b = req("GET", "/health")
        health_ok = s == 200
        s1, b1 = req("GET", "/items")
        s2, b2 = req("POST", "/items", {"name": "alpha"})
        created = json.loads(b2) if s2 in (200, 201) else {}
        iid = created.get("id")
        s3, b3 = req("GET", f"/items/{iid}") if iid else (0, b"")
        s4, b4 = req("GET", "/items/99999")
        checks.append({"name": "GET /health -> 200", "ok": health_ok, "points": 3})
        checks.append({"name": "GET /items -> 200 JSON list", "ok": s1 == 200 and isinstance(json.loads(b1), list),
                       "points": 3})
        checks.append({"name": "POST /items creates + returns id", "ok": s2 in (200, 201) and iid is not None,
                       "points": 4})
        checks.append({"name": "GET /items/{id} returns created item", "ok": s3 == 200 and iid is not None,
                       "points": 3})
        checks.append({"name": "unknown id -> 404", "ok": s4 == 404, "points": 3})
    except Exception as e:
        checks.append({"name": "server reachable", "ok": False, "points": 16, "detail": str(e)[:200]})
    finally:
        proc.terminate()
        proc.wait(timeout=10)
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
