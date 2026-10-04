# JSON API Server (standard library only)

A minimal JSON REST API server built exclusively with the Python standard
library (`http.server`). No frameworks, no third-party dependencies.

## Features

- `GET    /health`     -> `200` `{"status": "ok"}`
- `GET    /items`      -> `200` `[item, ...]`
- `POST   /items`      -> `201` with the created item (body: `{"name": "..."}`)
- `GET    /items/{id}` -> `200` item, `404` when missing
- `DELETE /items/{id}` -> `204`, `404` when missing
- Items persist to a JSON file (default `items.json`) so data survives restarts.
- Malformed requests are answered gracefully: `400` for bad JSON / bad ids,
  `404` for unknown routes or missing items, `405` for wrong methods. The
  server never crashes on bad input.
- Corrupt or missing data files are handled gracefully: the store starts
  empty instead of raising.
- IDs are assigned from the max existing id at startup, so they never
  collide across restarts.
- Threaded (`ThreadingHTTPServer`), so concurrent requests don't block.

## Running

```bash
python server.py --port N [--host HOST] [--data FILE]
```

Examples:

```bash
python server.py --port 8000                      # data in ./items.json
python server.py --port 8000 --host 0.0.0.0       # bind all interfaces
python server.py --port 8000 --data /var/lib/app/items.json
```

Requires Python 3.10+ (uses modern type hints; works on 3.12).

## Trying it with curl

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"name":"widget"}' http://127.0.0.1:8000/items
curl -s http://127.0.0.1:8000/items
curl -s http://127.0.0.1:8000/items/1
curl -s -X DELETE http://127.0.0.1:8000/items/1
```

## Self-check

`test_server.py` starts the server on a free port, exercises every endpoint
(including error paths and restart persistence), and exits 0 on success:

```bash
python test_server.py
```

Expected output ends with:

```
28 checks, 0 failures
ALL CHECKS PASSED
```

## Error semantics

| Condition | Status |
|---|---|
| Unknown route | 404 |
| Non-integer or zero item id (GET/DELETE /items/{id}) | 400 |
| Missing item | 404 |
| Invalid JSON body / non-object body / missing empty `name` | 400 |
| Wrong method on a known resource (PUT/PATCH /items, POST /health, ...) | 405 |
| Internal failure while handling a request | 500 (never an unhandled crash) |

## Data file format

```json
{
  "1": {"id": 1, "name": "alpha"}
}
```

The file is rewritten atomically (temp file + `os.replace`) on every
mutation, so a crash mid-write cannot corrupt it.

## Layout

- `server.py`     -- the server (run this)
- `test_server.py` -- self-check script (starts the server, hits every endpoint, asserts)
