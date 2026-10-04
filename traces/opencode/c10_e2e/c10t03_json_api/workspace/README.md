# Stdlib JSON API Server

A JSON API server built with **only the Python standard library**
(`http.server`), no frameworks, no dependencies.

## Run

```bash
python server.py --port 8080
```

Items persist to `items.json` next to `server.py`, so data survives restarts.

## Endpoints

| Method | Path         | Success        | Errors            |
| ------ | ------------ | -------------- | ----------------- |
| GET    | `/health`    | 200 `{"status": "ok"}` | -             |
| GET    | `/items`     | 200 `[item, ...]` | -               |
| POST   | `/items`     | 201 created item (body must be `{"name": "..."}`) | 400 invalid JSON / bad body |
| GET    | `/items/{id}`| 200 item       | 404 missing       |
| DELETE | `/items/{id}`| 204            | 404 missing       |

All other routes return 404; unsupported methods on known routes return 405.
Malformed requests never crash the server.

## Item shape

```json
{"id": "uuid4-string", "name": "apple", "created_at": 1759000000.0}
```

## Verify

```bash
python self_check.py
```

The self-check starts the server on a free port, exercises every endpoint
(including 400/404/405 paths), stops it, restarts it, and asserts data
persistence — 18 checks.
