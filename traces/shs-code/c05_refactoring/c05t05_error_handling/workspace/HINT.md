Refactor task: eliminate every bare `except:` in loader.py.
Required behavior after refactor:
- load(path): raise FileNotFoundError when the file is missing; raise
  json.JSONDecodeError (ValueError) when the content is not valid JSON;
  return the parsed dict otherwise.
- get(data, path): return None on missing keys / wrong types (that part is
  intentional behavior), but only catch (KeyError, TypeError) — nothing else.
- save(path, data): propagate real OSError (disk full, permission denied);
  return True on success. Keep the True/False-ish contract ONLY for OSError
  propagation being allowed: do not catch OSError — let it raise.