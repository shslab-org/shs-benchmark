"""Tests for http_client.py — requests-based HTTP client abstraction."""

import json
from unittest.mock import patch, MagicMock

import http_client
import config


class TestModuleLevelFunctions:
    """Tests for the free functions get/post/put/delete."""

    @patch("http_client.requests.get")
    def test_get(self, mock_get):
        resp = MagicMock(status_code=200, json=lambda: {"ok": True})
        mock_get.return_value = resp
        result = http_client.get("/health")
        assert result is resp
        args, kwargs = mock_get.call_args
        assert args[0] == "http://127.0.0.1:8734/health"
        assert kwargs["timeout"] == config.DEFAULT_TIMEOUT
        assert kwargs["headers"]["User-Agent"] == "PURPLE-TIGER/1.0"

    @patch("http_client.requests.get")
    def test_get_with_params(self, mock_get):
        resp = MagicMock(status_code=200)
        mock_get.return_value = resp
        http_client.get("/search", params={"q": "x"})
        _, kwargs = mock_get.call_args
        assert kwargs["params"] == {"q": "x"}

    @patch("http_client.requests.post")
    def test_post_json(self, mock_post):
        resp = MagicMock(status_code=200)
        mock_post.return_value = resp
        http_client.post("/items", json={"name": "widget"})
        _, kwargs = mock_post.call_args
        assert kwargs["json"] == {"name": "widget"}

    @patch("http_client.requests.post")
    def test_post_data(self, mock_post):
        resp = MagicMock(status_code=200)
        mock_post.return_value = resp
        http_client.post("/upload", data=b"\x00\x01")
        _, kwargs = mock_post.call_args
        assert kwargs["data"] == b"\x00\x01"

    @patch("http_client.requests.put")
    def test_put(self, mock_put):
        resp = MagicMock(status_code=200)
        mock_put.return_value = resp
        http_client.put("/items/1", json={"name": "x"})
        _, kwargs = mock_put.call_args
        assert kwargs["json"] == {"name": "x"}

    @patch("http_client.requests.delete")
    def test_delete(self, mock_delete):
        resp = MagicMock(status_code=204)
        mock_delete.return_value = resp
        http_client.delete("/items/1")
        mock_delete.assert_called_once()


class TestHttpClient:
    """Tests for the HttpClient class."""

    def test_init_defaults(self):
        client = http_client.HttpClient()
        assert client._base_url == config.BASE_URL
        assert client._timeout == config.DEFAULT_TIMEOUT
        assert client._headers == config.DEFAULT_HEADERS

    def test_init_custom_base_url(self):
        client = http_client.HttpClient(base_url="http://localhost:9999")
        assert client._base_url == "http://localhost:9999"

    @patch("http_client.requests.request")
    def test_get(self, mock_req):
        resp = MagicMock(status_code=200)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        result = client.get("/health")
        assert result is resp
        args, kwargs = mock_req.call_args
        assert args[0] == "GET"
        assert args[1] == "http://127.0.0.1:8734/health"
        assert kwargs["timeout"] == config.DEFAULT_TIMEOUT

    @patch("http_client.requests.request")
    def test_post_json(self, mock_req):
        resp = MagicMock(status_code=201)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        client.post("/items", json={"name": "x"})
        args, kwargs = mock_req.call_args
        assert args[0] == "POST"
        assert kwargs["json"] == {"name": "x"}

    @patch("http_client.requests.request")
    def test_post_data(self, mock_req):
        resp = MagicMock(status_code=201)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        client.post("/upload", data=b"abc")
        _, kwargs = mock_req.call_args
        assert kwargs["data"] == b"abc"

    @patch("http_client.requests.request")
    def test_put(self, mock_req):
        resp = MagicMock(status_code=200)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        client.put("/items/1", json={"name": "y"})
        args, kwargs = mock_req.call_args
        assert args[0] == "PUT"
        assert kwargs["json"] == {"name": "y"}

    @patch("http_client.requests.request")
    def test_delete(self, mock_req):
        resp = MagicMock(status_code=204)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        client.delete("/items/1")
        args, _ = mock_req.call_args
        assert args[0] == "DELETE"

    @patch("http_client.requests.request")
    def test_path_normalization_no_leading_slash(self, mock_req):
        resp = MagicMock(status_code=200)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        client.get("health")  # no leading slash
        _, url = mock_req.call_args[0]
        assert url == "http://127.0.0.1:8734/health"

    @patch("http_client.requests.request")
    def test_path_normalization_double_slash(self, mock_req):
        resp = MagicMock(status_code=200)
        mock_req.return_value = resp
        client = http_client.HttpClient()
        client.get("//health")  # double slash
        _, url = mock_req.call_args[0]
        assert url == "http://127.0.0.1:8734/health"


class TestNoUrllib:
    """Verify that no urllib usage exists in http_client."""

    def test_no_urllib_import(self):
        import inspect
        import re
        source = inspect.getsource(http_client)
        # Guard against actual urllib *import* statements only — the word
        # "urllib" may legitimately appear in docstrings/comments.
        assert not re.search(r"^\s*(import\s+urllib|from\s+urllib\b)", source, re.M)

    def test_uses_requests(self):
        import inspect
        source = inspect.getsource(http_client)
        assert "requests" in source
        assert "import requests" in source
