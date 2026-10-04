# URL Shortener

A tiny URL shortener with in-memory storage plus JSON persistence, so codes
survive process restarts.

## Usage

```python
import shortener

code = shortener.shorten("https://example.com/a/very/long/url")
print(code)          # e.g. 'ab12cd34' (deterministic per URL)

shortener.shorten("https://docs.example.com/guide", alias="docs")
print(shortener.resolve("docs"))   # 'https://docs.example.com/guide'

print(shortener.resolve("nope"))   # None
```

Reusing an alias that already points at a different URL raises `ValueError`.
Codes auto-save to `data.json` next to `shortener.py`.

Run the tests: `python -m pytest tests/ -v`
