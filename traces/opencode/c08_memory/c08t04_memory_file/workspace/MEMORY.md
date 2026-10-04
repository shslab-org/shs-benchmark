# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-10-04 | Storage format: JSON (not CSV) | Data is nested and JSON round-trips types losslessly. |
| 2026-10-04 | Implemented storage.py using JSON (save_notes/load_notes) | Per the earlier JSON decision; NOT CSV. |
