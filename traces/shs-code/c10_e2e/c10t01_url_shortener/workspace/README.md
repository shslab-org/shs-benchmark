# URL Shortener

Shorten long URLs, resolve codes back to the original. Codes are
deterministic (hash-based, 6 chars) and persisted to JSON next to the
module, so they survive process restarts.

```python
from shortener import shorten, resolve

code = shorten("https://example.com/a/very/long/url")  # e.g. "k3j9xa"
print(resolve(code))  # -> original URL
print(resolve("nope"))  # -> None (unknown code)

# custom alias (collision raises ValueError)
code = shorten("https://example.com", alias="home")
```

Persistence: codes auto-load on import and auto-save on every
`shorten()` call.

Run tests: `pytest tests/ -v`
