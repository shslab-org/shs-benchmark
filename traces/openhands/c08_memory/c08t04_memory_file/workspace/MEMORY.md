# Memory / Decision Log

## 2026-10-04
- **Storage format: JSON (not CSV)** — our data is nested and JSON round-trips types losslessly.
- **Implemented storage.py per the JSON decision** — `save_notes`/`load_notes` use json; missing files load as `[]`, verified by round-trip test.

## 2026-01-14
- **Storage format: JSON (not CSV)** — our data is nested and JSON round-trips types losslessly.
- **Implemented storage.py per the JSON decision** — `save_notes`/`load_notes` use the json module; missing files load as `[]`, verified by round-trip test.
