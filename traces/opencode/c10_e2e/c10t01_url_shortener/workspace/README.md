# URL Shortener

Deterministic URL shortener with JSON persistence.

```python
from shortener import shorten, resolve

code = shorten("https://example.com/very/long/url?x=1")
print(code)            # e.g. "K7mQ2bXz"

print(resolve(code))   # https://example.com/very/long/url?x=1

# Custom alias
code = shorten("https://docs.python.org", alias="pydocs")
print(resolve("pydocs"))

# Unknown code returns None
print(resolve("nope"))  # None
```

Codes are hash-based and deterministic (same URL → same code, 8 chars).
A data file `shortener_data.json` sits next to `shortener.py` and is
auto-loaded/saved, so codes survive process restarts.

Run tests: `python -m pytest tests/ -v`
