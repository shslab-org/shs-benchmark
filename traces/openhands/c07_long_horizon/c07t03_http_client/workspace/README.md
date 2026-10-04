# httpclient — retrying HTTP client (standard library only)

A tiny retrying HTTP client built exclusively on `urllib.request`
(no `requests`/`httpx`).

## API

```python
from httpclient import fetch_with_retry

data, status = fetch_with_retry(url, retries=3, backoff=0.5, timeout=5)
```

| Parameter  | Default | Meaning                                                        |
|------------|---------|----------------------------------------------------------------|
| `url`      | —       | The URL to fetch (must be a valid HTTP/HTTPS URL).            |
| `retries`  | `3`     | Number of *extra* attempts after the initial request. Total attempts = `retries + 1`. |
| `backoff`  | `0.5`   | Base delay (seconds) after the first failure. Doubles after every subsequent failure (exponential backoff: `0.5, 1.0, 2.0, ...`). |
| `timeout`  | `5`     | Per-request socket timeout in seconds.                          |

### Return value

A tuple `(data, status)`:

- `status` — the final HTTP status code (int).
- `data` — the response body:
  - parsed as a Python object if the response is JSON
    (`Content-Type: application/json`, or JSON-looking body),
  - otherwise the raw body as a `str` (decoded UTF-8).

### Retry semantics

- **Retried**: connection errors (`URLError`, timeouts, `OSError`)
  and any **5xx** HTTP response.
- **Not retried**: any **4xx** HTTP response — it is returned
  immediately, no sleep, no additional attempts.
- After `retries` extra attempts are exhausted on connection errors,
  the last exception is re-raised. For 5xx exhaustion, the final 5xx
  response body and status are returned (read from the `HTTPError`).

### Errors raised

- `urllib.error.URLError` (or the original connection error) when all
  attempts fail with a network-level error.

## Examples

```python
import httpclient

# JSON
data, status = httpclient.fetch_with_retry("https://api.example.com/items")
print(status, data)  # 200 {"items": [...]}

# plain text, 2 extra retries, start sleeping 1s
data, status = httpclient.fetch_with_retry(
    "https://example.com/plain", retries=2, backoff=1.0
)
```

## Tests

Run the pytest suite (uses a real local `http.server` thread plus
mocked/stubbed tests of the retry/backoff logic):

```bash
pytest tests/ -v
```
