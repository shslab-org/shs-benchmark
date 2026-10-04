
## Architecture Decision (recorded)
- **Storage engine: SQLite via Python stdlib `sqlite3`** — NOT Postgres, NOT MongoDB.
- **Rationale:** the app must run fully local-first on a laptop with zero external services; SQLite is embedded, file-based, and needs no server.
- This decision is locked and will be built upon in a later implementation step.
