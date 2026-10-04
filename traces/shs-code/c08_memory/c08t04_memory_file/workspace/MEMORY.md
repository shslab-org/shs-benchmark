# MEMORY.md — Decision Log

Project: tiny notes app
Convention: every decision recorded with date, decision, and one-line rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-22 | Storage format: JSON (not CSV) | Our data is nested and JSON round-trips types losslessly. |
