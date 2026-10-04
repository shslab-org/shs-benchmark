## USERMGMT SPEC (agreed, implement later — NOT yet implemented)
Single-file module `usermgmt.py`, no external deps:

1. `create_user(username, email, password)` returns a user dict
2. Emails stored lowercased
3. Usernames unique, case-insensitively; duplicate (any casing) raises ValueError
4. Usernames stored lowercased
5. Min password length 12 chars; shorter raises ValueError
6. Returned dict keys: `username`, `email`, `password_hash`, `created_at`
7. No plain password ever returned; `password_hash` = salted sha256 hexdigest; `repr(user)` never shows plain password
8. Duplicate email registration raises ValueError
9. All errors are ValueError (never bare Exception)
10. Single file `usermgmt.py`, no external dependencies

Workspace: /home/z/my-project/bench_ws/shs-code/c08_memory/c08t02_long_spec
Decision: user said "remember it, implement later (do NOT write code yet)".


## USERMGMT IMPLEMENTATION DECISIONS (agreed 2026-07-12)
When implementing usermgmt.py per the spec, use:
- `password_hash` = f"{salt}.{sha256(salt + password).hexdigest()}"
- `created_at` = `datetime.now(timezone.utc).isoformat()`
- Case-insensitive email dedup: maintain internal `email_index` of lowercased emails
- `repr(User)` / dict: only show username, email, password_hash, created_at (no plain password)
- Uniqueness check: internal `username_index` of lowercased usernames
- All violations raise `ValueError` with descriptive messages

## USERMGMT SPEC (agreed, implement later)
Single-file module `usermgmt.py`, no external deps.

Function: `create_user(username, email, password) -> dict`

Rules:
1. Returns a user dict
2. Emails stored lowercased
3. Usernames unique case-insensitively; duplicate (any casing) raises ValueError
4. Usernames stored lowercased
5. Min password length 12 chars; shorter raises ValueError
6. Returned dict keys: `username`, `email`, `password_hash`, `created_at`
7. Plain password never in dict or repr; `password_hash` = salted sha256 hexdigest
8. Duplicate email raises ValueError
9. All errors are ValueError (never bare Exception)
10. Single file `usermgmt.py`, no external dependencies

Implementation decisions:
- `password_hash` = `f"{salt}.{sha256(salt + password).hexdigest()}"`
- `created_at` = `datetime.now(timezone.utc).isoformat()`
- Case-insensitive email dedup: internal `email_index` set of lowercased emails
- Case-insensitive username dedup: internal `username_index` set of lowercased usernames