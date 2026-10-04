# Why SQLite?

Decision (2026-10-04): the storage engine is SQLite, accessed through
Python's standard-library `sqlite3` module. NOT Postgres, NOT MongoDB.

## Reasons (from our earlier discussion)

1. **Local-first, zero external services.** The app must run fully on a
   laptop with zero external services. Postgres and MongoDB require a
   separate server daemon (or a container) to be running; SQLite is
   embedded in the process, so there is no server to install, start,
   configure, or keep alive.
2. **File-based.** The entire database is one plain file (`./appdata.db`)
   sitting next to the app. No sockets, no ports, no network, no
   credentials — easy to copy, back up, delete, or inspect by hand.
3. **Zero dependencies.** SQLite ships in Python's standard library as
   `sqlite3`; nothing extra to install or vendor.
4. **Right-sized for the workload.** This app's storage needs are simple
   key/value persistence on a single machine — exactly SQLite's sweet
   spot. A full RDBMS server or a document database would only add
   complexity we do not need.
