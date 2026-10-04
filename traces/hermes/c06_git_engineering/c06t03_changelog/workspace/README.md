# Service

A tiny Python ping service with a metrics endpoint, thread-safe counters, and a healthcheck.

## Endpoints

- `ping()` — returns "pong"
- `metrics()` — snapshot of counters
- `healthcheck()` — returns `{"status": "ok"}`

## Development

Tags v0.1.0, v0.2.0, v0.3.0 mark releases; see CHANGELOG.md for details.
