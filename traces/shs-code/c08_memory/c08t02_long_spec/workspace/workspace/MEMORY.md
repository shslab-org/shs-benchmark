# Project: user management module (usermgmt.py)

## Spec (final, 10 points)
1. `create_user(username, email, password)` returns a user dict
2. email stored lowercased
3. usernames unique case-insensitively (dup in any casing -> ValueError)
4. usernames stored lowercased
5. min password length 12 (shorter -> ValueError)
6. returned dict keys: username, email, password_hash, created_at
7. password_hash = salted sha256 hexdigest; plain password never in repr
8. duplicate email -> ValueError
9. all errors are ValueError
10. single file usermgmt.py, stdlib only (hashlib, secrets, datetime)

## Status: IMPLEMENTED and verified (usermgmt.py at project root)
- 10/10 runtime checks passed (dict return, lowercased storage, exact keys,
  64-hex hash, plain password hidden in repr, ValueError on short/dup/empty)
- py_compile clean; AST import audit: imports = [hashlib, secrets, datetime], zero non-stdlib
- extra helpers: reset(), get_user(username)


## Re-verification log
- Re-verified 10/10 spec points on existing usermgmt.py (no code changes made; file was already compliant).
- Functional suite covered: dict return, exact keys, lowercase storage, salted sha256 64-hex hash,
  plain password absent from repr/str, ValueError on short password / duplicate username /
  duplicate email / empty username, case-insensitive get_user. All passed.
- No skill file created for this verification (one-off QA pass, not a reusable multi-step workflow).


## Re-verification log
- Re-verified 10/10 spec points on existing usermgmt.py (no code changes made; file was already compliant).
- Functional suite covered: dict return, exact keys, lowercase storage, salted sha256 64-hex hash,
  plain password hidden from repr, ValueError on short/dup/empty inputs.
- py_compile clean; AST import audit: imports = [hashlib, secrets, datetime], zero non-stdlib.