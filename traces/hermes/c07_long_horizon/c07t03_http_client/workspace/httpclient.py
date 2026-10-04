"""httpclient - a retrying HTTP GET client built on the Python standard library.

Only ``urllib.request`` / ``urllib.error`` are used; no third-party
HTTP libraries are required.

Retry policy
------------
- Network-level failures (connection refused, DNS errors, timeouts,
  connection resets) are retried.
- HTTP 5xx responses are retried.
- HTTP 4xx responses are NOT retried: they are returned to the caller
  immediately with their status code.
- Up to ``retries`` extra attempts are made (``retries + 1`` total
  requests). After each *failed* attempt the client sleeps for the
  current backoff, which doubles after every failure (exponential
  backoff: backoff, 2*backoff, 4*backoff, ...).
- If the URL still cannot be fetched after all attempts, the last
  underlying connection error is re-raised to the caller.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

__all__ = ["fetch_with_retry"]

_USER_AGENT = "stdlib-httpclient/1.0"


def fetch_with_retry(url: str, retries: int = 3, backoff: float = 0.5,
                     timeout: float = 5) -> tuple[object, int]:
    """Perform an HTTP GET on *url*, retrying on failures.

    Parameters
    ----------
    url:
        The URL to fetch.
    retries:
        Maximum number of *additional* attempts after the first one.
        ``retries=0`` means exactly one attempt. Must be >= 0.
    backoff:
        Base sleep interval in seconds after a failed attempt. The delay
        doubles after every failure (exponential backoff). Must be >= 0.
    timeout:
        Per-attempt socket timeout in seconds.

    Returns
    -------
    (body, status)
        *status* is the final HTTP status code. *body* is the response
        body decoded as JSON (if it parses as a JSON document),
        otherwise the raw body as text.

    Raises
    ------
    ValueError
        If ``retries`` or ``backoff`` is negative.
    urllib.error.URLError
        (or another socket-level OSError such as ``ConnectionError`` /
        ``TimeoutError``) if the URL still cannot be fetched after all
        ``retries + 1`` attempts.
    """
    if retries < 0:
        raise ValueError("retries must be >= 0")
    if backoff < 0:
        raise ValueError("backoff must be >= 0")

    delay = backoff
    final_status: int | None = None
    final_text: str | None = None

    for attempt in range(retries + 1):
        try:
            status, text = _request(url, timeout)
        except (urllib.error.URLError, OSError) as exc:
            # Connection-level failure (refused, DNS, timeout, reset, ...).
            if attempt == retries:
                raise  # out of retries: surface the last error
            time.sleep(delay)
            delay *= 2
            continue

        final_status, final_text = status, text

        # 5xx is retryable; 4xx (and anything else) is final.
        if 500 <= status < 600 and attempt < retries:
            time.sleep(delay)
            delay *= 2
            continue
        break

    # Control only leaves the loop via `break` above (with a value set)
    # or by `raise` inside it, so both variables are assigned here.
    assert final_status is not None and final_text is not None
    return _json_or_text(final_text), final_status


def _request(url: str, timeout: float) -> tuple[int, str]:
    """Make a single GET request.

    Returns ``(status, body_text)``. HTTP error responses (4xx/5xx) are
    reported via their status code rather than raising. Connection-level
    failures raise ``urllib.error.URLError`` (or a raw socket OSError).
    """
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read()
        except Exception:
            raw = b""
        return exc.code, raw.decode("utf-8", errors="replace")


def _json_or_text(text: str) -> object:
    """Decode *text* as JSON if possible, otherwise return it as text."""
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return text
