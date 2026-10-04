# URL Shortener

Tiny URL shortener with in-memory storage + JSON file persistence.

```python
import shortener

code = shortener.shorten("https://example.com/a/very/long/url")
print(code)                     # e.g. 6+ char hash-based code
print(shortener.resolve(code))  # -> original url

# Custom alias
code = shortener.shorten("https://example.com/docs", alias="docs")
# Alias collision raises ValueError
shortener.shorten("https://other.com", alias="docs")
# Unknown code -> None
shortener.resolve("nope")
```

Codes survive restarts: mappings are saved to `shortener_data.json`
next to the module. Override the path with the `SHORTENER_DATA_FILE`
environment variable.

Run tests:

```bash
python -m pytest tests/ -v
```
