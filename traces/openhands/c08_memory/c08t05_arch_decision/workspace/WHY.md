# Why SQLite?

From our earlier architecture discussion:

- **Local-first requirement:** The app must run fully local on a laptop
  with zero external services. SQLite is embedded and file-based, so
  it needs no server process.
- **Stdlib available:** Python ships `sqlite3` in the standard library,
  so there are no third-party driver dependencies to install or maintain.
- **Rejected alternatives:** Postgres and MongoDB were explicitly ruled
  out because they require running external server services, which
  violates the local-first constraint.
