# JSON API Server (stdlib only)

A tiny JSON API server built on `http.server` — no external dependencies.

## Endpoints

| Method | Path            | Success          | Errors               |
|--------|-----------------|------------------|----------------------|
| GET    | `/health`       | 200 `{"status":"ok"}` |
| GET    | `/items`        | 200 `[item, ...]`    |
| POST   | `/items`        | 201 created item     | 400 (invalid JSON / missing `name`) |
| GET    | `/items/{id}`   | 200 item             | 404 (missing), 405 (non-numeric id) |
| DELETE | `/items/{id}`   | 204                | 404 (missing), 405 (wrong shape) |

## Run

```bash
python server.py --port 8000
# data persists to ./items_data.json (default)
# or specify:
python server.py --port 8000 --data /path/to/items.json
```

## Example session

```bash
# health
curl http://localhost:8000/health
# {"status": "ok"}

# create
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "widget"}'
# {"name": "widget", "id": 1}

# list
curl http://localhost:8000/items
# [{"name": "widget", "id": 1}]

# get one
curl http://localhost:8000/items/1
# {"name": "widget", "id": 1}

# delete
curl -X DELETE http://localhost:8000/items/1
# (204, empty body)

# missing
curl http://localhost:8000/items/999
# 404 {"error": "item not found"}
```

## Tests

```bash
python tests/test_server.py
# or: pytest tests/test_server.py -v
```

The integration test spawns a real server subprocess on a free port and
exercises every endpoint plus a restart-persistence check.

## Persistence

Items are stored in a JSON file. The file is written atomically
(temp-file + rename) on every mutation so a crash mid-write never
corrupts it. IDs are monotonic and survive restarts.
