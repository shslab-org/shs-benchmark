# Retrying HTTP Client (stdlib only)

A minimal, dependency-free retrying HTTP client built on Python's
standard library (`urllib.request`). No `requests`, no `httpx`.

## Contents

| File | Purpose |
|---|---|
| `httpclient.py` | The client library (single public function). |
| `tests/test_httpclient.py` | pytest suite (real local HTTP server + mocked sleep/errors). |

## API

```python
from httpclient import fetch_with_retry

body, status = fetch_with_retry(url, retries=3, backoff=0.5, timeout=5)
```

### `fetch_with_retry(url, retries=3, backoff=0.5, timeout=5) -> (body, status)`

| Parameter | Default | Meaning |
|---|---|---|
| `url` | – | Absolute `http://` / `https://` URL. |
| `retries` | `3` | Extra attempts after the first. Worst-case total attempts = `retries + 1`. |
| `backoff` | `0.5` | Sleep after the 1st failure (seconds). Doubles each retry: `b, 2b, 4b, ...` |
| `timeout` | `5` | Per-request socket timeout (seconds). |

**Returns** `(body, status)`:

* `body` — the response payload: a JSON-decoded object when the response is
  JSON (by `Content-Type: application/json` or shape heuristics), otherwise
  the decoded text. `None` when every attempt failed at the connection level.
* `status` — final HTTP status code, or `0` when the last attempt was a
  connection-level failure.

**Retry semantics**

* **Retried:** connection errors (`URLError`/`OSError`) and **5xx** responses.
* **Not retried:** **4xx** responses — returned immediately, even with a
  high `retries` value.
* Exponential backoff: sleep `backoff * 2**attempt` after failures
  (only before the last attempt).

## Usage example

```python
from httpclient import fetch_with_retry

body, status = fetch_with_retry("https://example.com/api/data", retries=3, backoff=0.5)
if status == 200:
    print(body)          # dict/list if JSON, else str
elif status == 0:
    print("Network failure after retries")
else:
    print(f"HTTP {status}")
```

## Running the tests

```bash
python -m pytest tests/ -v
```

Tests spin up a real local `http.server` in a background thread for the
success/4xx/5xx paths, and monkeypatch `urlopen`/`sleep` for connection-error
and determinism. No external network access required.

## Design notes (why)

* **`urllib.request` only** — hard requirement; keeps the footprint to stdlib.
  `urlopen` raises `HTTPError` for 4xx/5xx, so those paths are handled by
  catching `HTTPError` and inspecting `.code`, rather than by checking a
  returned status.
* **JSON parsing is best-effort** — if a 2xx/4xx/5xx body claims
  `application/json` (or looks like a JSON container), it's decoded;
  otherwise the raw text is returned. This keeps the helper usable against
  both JSON and plain-text endpoints without the caller needing to know.
* **Backoff is exponential but applied only between attempts** — the sleep
  happens after a failure and *before* the next attempt; there is no sleep
  after the final attempt, so the function never idles unnecessarily at the
  end.
