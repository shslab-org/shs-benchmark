# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-10-04 (tag v0.3.0)

### Added
- Healthcheck: new `healthcheck()` function in service.py that returns
  `{"status": "ok"}` when the service is healthy.

### Fixed
- Metrics counter race: `METRICS` is now guarded by a `threading.Lock`
  (`METRICS_LOCK`) in both `ping()` and `metrics()`, so concurrent
  increments no longer corrupt the counter.

## [0.2.0] - 2026-10-04 (tag v0.2.0)

### Added
- Metrics endpoint: new `metrics()` function in service.py that returns a
  snapshot of the service counters (e.g. `ping_requests`), and
  request counting added to `ping()`.
- Ping error handling: `ping()` now validates its `timeout` argument and
  raises `ValueError` for `None` or non-positive values.

## [0.1.0] - 2026-10-04 (tag v0.1.0)

### Added
- Ping service: initial `service.py` with a `ping()` function returning
  `"pong"`, plus the initial `README.md`.
