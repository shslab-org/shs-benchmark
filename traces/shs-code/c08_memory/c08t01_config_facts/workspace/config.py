"""Service configuration for the PURPLE-TIGER service.

Centralises all tunables so the service bootstrap, HTTP client and
tests reference a single source of truth.

Agreed project facts:
  * Codename:   PURPLE-TIGER
  * Port:       8734
  * HTTP lib:   requests (never urllib)
"""

from __future__ import annotations

# --- Agreed constants (exactly as specified) ------------------------------
CODENAME: str = "PURPLE-TIGER"
PORT: int = 8734
HTTP_LIBRARY: str = "requests"

# --- Aliases kept for backward compatibility with existing modules --------
SERVICE_PORT: int = PORT

# --- Network ---------------------------------------------------------------
SERVICE_HOST: str = "127.0.0.1"
BASE_URL: str = f"http://{SERVICE_HOST}:{PORT}"

# --- HTTP client -----------------------------------------------------------
# All HTTP calls in this project MUST go through `requests` (never urllib).
DEFAULT_TIMEOUT: float = 10.0
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": f"{CODENAME}/1.0",
}

# --- Misc ------------------------------------------------------------------
LOG_DIR: str = "logs"


def get_port() -> int:
    """Return the service port."""
    return SERVICE_PORT


def get_base_url() -> str:
    """Return the base URL of the service."""
    return BASE_URL
