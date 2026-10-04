"""Tests for config.py — PURPLE-TIGER service configuration."""

import config


class TestConstants:
    def test_codename(self):
        assert config.CODENAME == "PURPLE-TIGER"

    def test_service_port(self):
        assert config.SERVICE_PORT == 8734

    def test_service_host(self):
        assert config.SERVICE_HOST == "127.0.0.1"

    def test_base_url(self):
        assert config.BASE_URL == "http://127.0.0.1:8734"

    def test_http_library(self):
        assert config.HTTP_LIBRARY == "requests"

    def test_default_timeout(self):
        assert config.DEFAULT_TIMEOUT == 10.0

    def test_default_headers(self):
        assert config.DEFAULT_HEADERS["User-Agent"] == "PURPLE-TIGER/1.0"


class TestGetters:
    def test_get_port(self):
        assert config.get_port() == 8734

    def test_get_base_url(self):
        assert config.get_base_url() == "http://127.0.0.1:8734"
