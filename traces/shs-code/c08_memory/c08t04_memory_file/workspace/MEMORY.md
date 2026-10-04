# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-04 | Storage format: JSON (not CSV) | Data is nested and JSON round-trips types losslessly. |
| 2026-10-04 | Implemented storage.py per the JSON storage decision (save_notes/load_notes) | Round-trip and missing-file behavior verified. |
