#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "harness"))
import vlib

ws, agent = sys.argv[1], sys.argv[2]
TID = "c07t03"
checks = []
client = None
for name in ("httpclient.py", "client.py", "retryclient.py", "fetch.py"):
    c = vlib.find_file(ws, name)
    if c:
        client = c
        break
if not client:
    for p in vlib.py_files(ws):
        if "def fetch_with_retry" in open(p).read():
            client = p
            break
checks.append({"name": "httpclient.py with fetch_with_retry exists", "ok": bool(client), "points": 5, "detail": str(client)})
if client:
    tests = [p for p in vlib.py_files(ws) if "test" in os.path.basename(p)]
    checks.append({"name": "agent-authored tests exist", "ok": bool(tests), "points": 4, "detail": str(tests)[:150]})
    base = os.path.dirname(client)
    rc, out = vlib.write_and_run_pytest(base, '''
import sys, threading, http.server, socketserver, os
sys.path.insert(0, os.path.abspath("."))
from httpclient import fetch_with_retry

class H(http.server.BaseHTTPRequestHandler):
    hits = 0
    def do_GET(self):
        H.hits += 1
        if H.hits < 3:
            self.send_response(503)
        else:
            self.send_response(200)
        self.end_headers()
        self.wfile.write(b\'{"ok": true}\')
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 0), H)
port = srv.server_address[1]
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()

def test_retries_then_succeeds():
    H.hits = 0
    data, status = fetch_with_retry("http://127.0.0.1:%d/" % port, retries=5, backoff=0.01)
    assert status == 200 and H.hits == 3

def test_respects_max_retries():
    H.hits = 0
    data, status = fetch_with_retry("http://127.0.0.1:%d/" % port, retries=1, backoff=0.01)
    assert status == 503 and H.hits == 2
''')
    checks.append({"name": "hidden behavior tests (retry-then-succeed + give-up)", "ok": rc == 0, "points": 9,
                   "detail": out[-400:] if rc != 0 else "passed"})
    if tests:
        env = dict(os.environ); env["PYTHONPATH"] = base
        rc2, out2 = vlib.run_cmd([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"] + tests, base, timeout=90, env_extra=env)
        checks.append({"name": "agent's own tests pass", "ok": rc2 == 0, "points": 2,
                       "detail": out2[-250:] if rc2 != 0 else "passed"})
res = vlib.make_result(TID, agent, checks)
print(json.dumps(res))
