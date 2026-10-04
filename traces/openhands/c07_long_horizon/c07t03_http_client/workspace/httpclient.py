"""Retrying HTTP client built only on the Python standard library.

Uses urllib.request under the hood. Retries on connection errors and
5xx responses with exponential backoff. 4xx responses are not retried.

Retry/return semantics:
- 2xx / 4xx: definitive response, returned immediately as (body, status).
- 5xx: retried up to `retries` extra times with exponential backoff.
  Once all attempts are exhausted, the last 5xx response's body and
  status code are returned as (body, status) instead of raising.
- Connection-level errors (URLError, timeout, OSError): retried up to
  `retries` extra times; if all attempts fail, the last exception is
  re-raised.
"""

import json
import time
import urllib.error
import urllib.request


def _is_server_error(status):
    return 500 <= status < 600


def _parse_body(raw, headers):
    """Return body as parsed JSON where possible, else decoded text."""
    if isinstance(raw, (bytes, bytearray)):
        text = raw.decode("utf-8", errors="replace")
    else:
        text = raw if isinstance(raw, str) else str(raw)

    content_type = ""
    if headers is not None:
        try:
            content_type = headers.get("Content-Type", "")
        except AttributeError:
            pass

    if content_type and "application/json" in content_type:
        try:
            return json.loads(text)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    stripped = text.strip()
    if stripped and stripped[0] in "{[":
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass
    return text


def fetch_with_retry(url, retries=3, backoff=0.5, timeout=5):
    """Fetch a URL, retrying transient failures.

    Args:
        url: The URL to fetch.
        retries: Number of *extra* attempts after the initial request
            (total attempts = retries + 1).
        backoff: Base delay (seconds) after the first failure; doubles
            after each subsequent failure (exponential).
        timeout: Per-request socket timeout in seconds.

    Returns:
        (body, status):
          - For 2xx/4xx: body is parsed JSON or text, status is the code.
          - For exhausted 5xx retries: body is the last error body (parsed
            JSON or text), status is the last 5xx code.

    Raises:
        urllib.error.URLError (or the underlying connection error) if all
            attempts fail with a connection-level error.
        TimeoutError if all attempts time out.
    """
    last_5xx = None
    last_conn_error = None
    current_backoff = backoff
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                raw = response.read()
                status = response.getcode()
                return _parse_body(raw, response.headers), status
        except urllib.error.HTTPError as err:
            if _is_server_error(err.code):
                last_5xx = (_parse_body(err.read(), err.headers), err.code)
                if attempt < retries:
                    time.sleep(current_backoff)
                    current_backoff *= 2
                continue
            # 4xx or other non-5xx: definitive client error, no retry.
            return _parse_body(err.read(), err.headers), err.code
        except (TimeoutError, urllib.error.URLError, OSError) as err:
            last_conn_error = err
            if attempt < retries:
                time.sleep(current_backoff)
                current_backoff *= 2
            continue

    if last_conn_error is not None:
        raise last_conn_error
    if last_5xx is not None:
        return last_5xx
    raise RuntimeError(f"All attempts failed for {url}")
