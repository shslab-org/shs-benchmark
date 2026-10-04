# Decision Log — Notes App

## 2026-10-04
- **Storage format: JSON (not CSV)** — Our data is nested and JSON round-trips types losslessly.
- **Implemented storage.py** (JSON save_notes/load_notes, load of missing file returns []) — per the 2026-10-04 JSON decision above; round-trip verified with nested + unicode data.
