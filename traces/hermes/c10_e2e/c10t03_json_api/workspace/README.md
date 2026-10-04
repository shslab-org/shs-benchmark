# JSON API (standard library only)

A small JSON API server built **entirely on the Python standard library**
(`http.server`, `threading`, `json`, `uuid`, `argparse`, `urllib` in tests —
no frameworks, no third-party packages).

## Endpoints

| Method | Path           | Success            | Errors                     |
|--------|----------------|--------------------|----------------------------|
| GET    | `/health`      | `200` `{"status":"ok"}` | `405` other methods    |
| GET    | `/items`       | `200` `[item, ...]`     | `405` other methods    |
| POST   | `/items`       | `201` created item      | `400` invalid/missing JSON, `405` other |
| GET    | `/items/{id}`  | `200` item            | `404` not found, `405` other |
| DELETE | `/items/{id}`  | `204`               | `404` not found, `405` other |
| any    | other paths    | —                 | `404`                        |
| any    | unknown methods| —                 | `405`                        |

An item looks like:

```json
{"id": "…16 hex chars…", "name": "apple", "created_at": "2026-10-04T…Z"}
```

Malformed requests (invalid JSON bodies, empty bodies, missing/blank `name`,
wrong methods, unknown paths) are answered with structured `400/404/405` JSON
errors (`{"error": "..."}`) — the server never crashes on client input.

## Persistence

Items are stored in a JSON file (default `items.json` next to where you run
the server). Every create/delete is written atomically (temp file + rename),
so restarts keep data and a torn write can never corrupt the store. If the
data file is unreadable/corrupt, the server starts fresh with an empty store
instead of crashing.

## Run

```bash
python server.py --port 8000
# options:
#   --port N          port to listen on (default 8000)
#   --host HOST       interface to bind (default 127.0.0.1)
#   --data-file FILE  where items persist (default items.json)
```

Requires Python 3.8+ (tested on 3.13).

## Try it

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/items
curl -X POST http://127.0.0.1:8000/items -H 'Content-Type: application/json' -d '{"name": "apple"}'
curl -X DELETE http://127.0.0.1:8000/items/<id>
```

## Self-check (end-to-end)

`check.py` starts the real server as a subprocess on a free port, then
exercises every endpoint — all status codes, malformed requests, restart
persistence, and corrupt-data-file recovery — and asserts each one:

```bash
python check.py
```

Expected output ends with `ALL CHECKS PASSED` and exit code 0.
