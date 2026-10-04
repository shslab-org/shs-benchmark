"""HTTP client abstraction using `requests` for the PURPLE-TIGER service.

All outbound HTTP calls in this project MUST use this module (never
urllib). It wraps `requests` with the default timeout, headers and
base URL from `config`.
"""

from __future__ import annotations

import requests
import config


def get(path: str, *, params: dict | None = None) -> requests.Response:
    """Perform a GET request against the service base URL."""
    url = f"{config.BASE_URL}/{path.lstrip('/')}"
    return requests.get(
        url,
        params=params,
        timeout=config.DEFAULT_TIMEOUT,
        headers=config.DEFAULT_HEADERS,
    )


def post(path: str, *, json: dict | None = None, data: bytes | None = None) -> requests.Response:
    """Perform a POST request against the service base URL."""
    url = f"{config.BASE_URL}/{path.lstrip('/')}"
    return requests.post(
        url,
        json=json,
        data=data,
        timeout=config.DEFAULT_TIMEOUT,
        headers=config.DEFAULT_HEADERS,
    )


def put(path: str, *, json: dict | None = None) -> requests.Response:
    """Perform a PUT request against the service base URL."""
    url = f"{config.BASE_URL}/{path.lstrip('/')}"
    return requests.put(
        url,
        json=json,
        timeout=config.DEFAULT_TIMEOUT,
        headers=config.DEFAULT_HEADERS,
    )


def delete(path: str) -> requests.Response:
    """Perform a DELETE request against the service base URL."""
    url = f"{config.BASE_URL}/{path.lstrip('/')}"
    return requests.delete(
        url,
        timeout=config.DEFAULT_TIMEOUT,
        headers=config.DEFAULT_HEADERS,
    )


class HttpClient:
    """High-level client bundling GET/POST/PUT/DELETE helpers.

    Usage::

        client = HttpClient()
        resp = client.get("/health")
        resp = client.post("/items", json={"name": "x"})
    """

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or config.BASE_URL
        self._timeout = config.DEFAULT_TIMEOUT
        self._headers = dict(config.DEFAULT_HEADERS)

    # -- low-level helpers ---------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        return requests.request(
            method,
            self._url(path),
            timeout=self._timeout,
            headers=self._headers,
            **kwargs,
        )

    # -- verb helpers --------------------------------------------------------

    def get(self, path: str, *, params: dict | None = None) -> requests.Response:
        return self._request("GET", path, params=params)

    def post(self, path: str, *, json: dict | None = None, data: bytes | None = None) -> requests.Response:
        return self._request("POST", path, json=json, data=data)

    def put(self, path: str, *, json: dict | None = None) -> requests.Response:
        return self._request("PUT", path, json=json)

    def delete(self, path: str) -> requests.Response:
        return self._request("DELETE", path)
