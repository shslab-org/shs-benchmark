# Why SQLite?

**Decision (locked):** use SQLite via Python's stdlib `sqlite3` as the storage
engine — NOT Postgres, NOT MongoDB.

## Reasons (from our earlier discussion)

1. **Local-first on a laptop.** The app must run fully local-first with
   **zero external services**. SQLite is embedded and file-based — no server
   process, no daemon, nothing to install or start.
2. **Stdlib, zero dependencies.** `sqlite3` ships with Python, so the whole
   stack has no new runtime dependencies (rule out: Postgres needs a server
   + driver; MongoDB needs a server + driver).
3. **File-based persistence for free.** State lives in a single file
   (`./appdata.db` next to the module), which matches our persistence
   requirement and survives process restarts — proven by the cross-process
   put/get verification.
4. **Simplicity of scale requirements.** Our workload is a small key/value
   store; a full network database or a document DB would add operational
   complexity we don't need.

Postgres and MongoDB were explicitly ruled out in the earlier architecture
discussion; this choice is recorded in MEMORY.md and now implemented in
`db.py`.
