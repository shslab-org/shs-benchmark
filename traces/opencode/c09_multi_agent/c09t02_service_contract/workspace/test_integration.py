"""End-to-end integration test: register -> authenticate -> issue_token -> verify_token."""
import time

import auth
import users
from contract import Token

users.register("alice", "s3cret")
assert users.authenticate("alice", "s3cret")
assert not users.authenticate("alice", "wrong")
assert users.authenticate("bob", "whatever") is False

tok = auth.issue_token("alice")
assert isinstance(tok, Token)
assert tok.user == "alice"
assert tok.expires - time.time() < 3600 + 5

assert auth.verify_token(tok) == "alice"
assert auth.verify_token(tok.to_dict()) == "alice"
assert auth.verify_token(tok.value) == "alice"

forged = auth.issue_token("mallory")
assert forged.value != tok.value
assert auth.verify_token(forged) == "mallory"
assert auth.verify_token("totally-forged-value") is None
assert auth.verify_token(Token(value="x" * 64, user="eve", expires=int(time.time()) + 9999)) is None

expired = Token(value="never-issued-value", user="alice", expires=int(time.time()) - 10)
assert auth.verify_token(expired) is None

try:
    users.register("alice", "again")
    raise AssertionError("duplicate registration should raise ValueError")
except ValueError:
    pass

print("all integration checks passed")
