"""End-to-end check of the decomposed services:
register -> authenticate -> issue_token -> verify_token + forged-token rejection.
Run: python flow_check.py  (exits non-zero on failure)
"""
import json
import time

import auth
import users
from contract import Token, now_ts

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        FAILURES.append(name)


# --- users: register + duplicate ---
users.register("ada", "s3cret")
try:
    users.register("ada", "other")
    check("duplicate username raises ValueError", False)
except ValueError as e:
    check("duplicate username raises ValueError", True, f"({e})")

# --- authenticate ---
check("authenticate correct password", users.authenticate("ada", "s3cret") is True)
check("authenticate wrong password", users.authenticate("ada", "nope") is False)
check("authenticate unknown user", users.authenticate("ghost", "x") is False)

# --- issue_token ---
tok = auth.issue_token("ada")
check("token is Token", isinstance(tok, Token))
check("token user field", tok.user == "ada")
check("token expires ~3600s out", 3590 <= tok.expires - now_ts() <= 3600,
      f"(ttl={tok.expires - now_ts()})")
check("token value unguessable (long hex)", len(tok.value) >= 64)

# --- verify_token: all three accepted forms ---
check("verify via Token object", auth.verify_token(tok) == "ada")
check("verify via dict", auth.verify_token(tok.to_dict()) == "ada")
check("verify via JSON str", auth.verify_token(json.dumps(tok.to_dict())) == "ada")

# round-trip through Token.from_dict
tok2 = Token.from_dict(tok.to_dict())
check("Token.from_dict round-trip", tok2 == tok)

# --- forged-token rejection ---
# 1) tamper signature
d = tok.to_dict()
bad_sig = dict(d, value=d["value"].rstrip() + "f" if not d["value"].endswith("f") else d["value"].rstrip() + "e")
check("forged: tampered signature", auth.verify_token(bad_sig) is None)

# 2) valid signature for a different user (reused token signed for "ada")
d2 = tok.to_dict()
d2["user"] = "eve"
check("forged: stolen token claiming other user", auth.verify_token(d2) is None)

# 3) expired token (signed with the same key, expiry in the past)
forged_expired = auth.issue_token("ada")
rand_part = forged_expired.value.split(".")[0]
expired_payload = {
    "value": f"{rand_part}.{auth._sign('ada', now_ts() - 5, rand_part)}",
    "user": "ada",
    "expires": now_ts() - 5,
}
check("expired token rejected", auth.verify_token(expired_payload) is None)

# 4) arbitrary garbage strings / malformed input
for junk in ["garbage", "ada.deadbeef", "", json.dumps({"user": "ada"}), json.dumps({"value": "x", "user": "ada", "expires": 1})]:
    check(f"malformed input rejected: {junk!r:.40}", auth.verify_token(junk) is None)

# 5) fully fabricated token (random material, no valid signature)
fake = Token(value="f00f." + "0" * 64, user="ada", expires=now_ts() + 3600)
check("forged: fabricated token (no valid sig)", auth.verify_token(fake) is None)
check("forged: fabricated token as JSON", auth.verify_token(json.dumps(fake.to_dict())) is None)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    raise SystemExit(1)
print("ALL CHECKS PASSED")
