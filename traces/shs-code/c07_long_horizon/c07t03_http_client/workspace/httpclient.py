"""Retrying HTTP client built solely on the Python standard library.

Exposes :func:`fetch_with_retry`, which wraps :mod:`urllib.request` with
exponential-backoff retries:

* Retries on connection errors (``URLError`` / ``OSError``).
* Retries on 5xx responses.
* Does **not** retry on 4xx responses.
* Sleeps ``backoff`` seconds after the first failure, doubling after each
  subsequent failure (exponential backoff): ``backoff, 2*backoff, 4*backoff``
* Performs the initial attempt plus up to ``retries`` additional attempts
  (``retries + 1`` total in the worst case).

Only the standard library is used - no third-party dependencies.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Optional, Tuple, Union

__all__ = ["fetch_with_retry"]

# A parsed body is either decoded text, a JSON object/list, or None when
# every attempt failed at the connection level.
Body = Union[str, dict, list, None]


def _parse_body(raw: bytes, content_type: Optional[str]) -> Body:
    """Decode raw response bytes, returning parsed JSON when appropriate."""
    text = raw.decode("utf-8", errors="replace")
    if content_type and "application/json" in content_type.lower():
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            return text
    # Be forgiving of servers that omit Content-Type but serve JSON.
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            return text
    return text


def fetch_with_retry(
    url: str,
    retries: int = 3,
    backoff: float = 0.5,
    timeout: float = 5,
) -> Tuple[Body, int]:
    """Fetch ``url`` with exponential-backoff retry semantics.

    Parameters
    ----------
    url:
        Absolute ``http://`` or ``https://`` URL to fetch.
    retries:
        Maximum number of *additional* attempts after the initial request.
        Total attempts in the worst case: ``retries + 1``.
    backoff:
        Initial sleep duration (seconds) after a failure. Doubles after
        each subsequent failure.
    timeout:
        Per-request socket timeout in seconds.

    Returns
    -------
    (body, status)
        ``body`` is the response payload -- a JSON-decoded object when the
        response is JSON, otherwise the decoded response text. It is
        ``None`` when every attempt failed at the connection level.
        ``status`` is the final HTTP status code, or ``0`` when the last
        attempt failed with a connection error.

    Notes
    -----
    * 4xx responses are final -- no retry.
    * 5xx responses are retried up to ``retries`` extra attempts.
    * Connection errors are retried the same way.
    """
    if retries < 0:
        raise ValueError("retries must be >= 0")
    if backoff < 0:
        raise ValueError("backoff must be >= 0")

    total_attempts = retries + 1
    attempt = 0

    while True:
        is_last = attempt == total_attempts - 1

        try:
            resp = urllib.request.urlopen(url, timeout=timeout)
            with resp:
                raw = resp.read()
                status = resp.getcode()
                ctype = resp.headers.get("Content-Type") if resp.headers else None
                body = _parse_body(raw, ctype)
            # 2xx/3xx reached urlopen normally (redirects are followed).
            return body, status

        except urllib.error.HTTPError as exc:
            # urlopen raises HTTPError for 4xx/5xx responses.
            try:
                raw = exc.read()
            except Exception:
                raw = b""
            ctype = exc.headers.get("Content-Type") if exc.headers else None
            body = _parse_body(raw, ctype) if raw else None

            if exc.code < 500:
                # 4xx -- do not retry.
                return body, exc.code

            # 5xx -- retry with exponential backoff unless exhausted.
            if is_last:
                return body, exc.code
            time.sleep(backoff * (2 ** attempt))
            attempt += 1

        except (urllib.error.URLError, OSError):
            # Connection-level failure (DNS, refused, timeout, reset, ...).
            if is_last:
                return None, 0
            time.sleep(backoff * (2 ** attempt))
            attempt += 1

    # Unreachable, but keeps static analysers happy.
    return None, 0
