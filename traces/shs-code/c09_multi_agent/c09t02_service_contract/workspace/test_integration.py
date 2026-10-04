"""Integration tests for the service contract.

Run:  python test_integration.py
"""

import importlib
import sys
import time
import unittest

sys.path.insert(0, ".")

# Force fresh import of the services under test.
for mod in ("contract", "auth", "users"):
    sys.modules.pop(mod, None)

import contract  # noqa: E402
import auth  # noqa: E402
import users  # noqa: E402
from contract import Token, now_ts  # noqa: E402


class TestContract(unittest.TestCase):
    def test_now_ts_returns_int(self):
        ts = now_ts()
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 0)

    def test_token_roundtrip(self):
        t = Token(value="abc", user="bob", expires=12345)
        d = t.to_dict()
        t2 = Token.from_dict(d)
        self.assertEqual(t, t2)


class TestImportIsolation(unittest.TestCase):
    def test_auth_does_not_import_users(self):
        with open(auth.__file__) as f:
            auth_src = f.read()
        self.assertNotIn("import users", auth_src)
        self.assertNotIn("from users", auth_src)

    def test_users_does_not_import_auth(self):
        with open(users.__file__) as f:
            users_src = f.read()
        self.assertNotIn("import auth", users_src)
        self.assertNotIn("from auth", users_src)


class TestRegisterAuthFlow(unittest.TestCase):
    def setUp(self):
        users._reset_for_tests()
        auth._reset_for_tests()

    def test_register_and_authenticate(self):
        users.register("alice", "s3cret!")
        self.assertTrue(users.authenticate("alice", "s3cret!"))
        self.assertFalse(users.authenticate("alice", "wrong"))
        self.assertFalse(users.authenticate("bob", "s3cret!"))

    def test_duplicate_register_raises(self):
        users.register("alice", "pw1")
        with self.assertRaises(ValueError):
            users.register("alice", "pw2")

    def test_empty_username_or_password_raises(self):
        with self.assertRaises(ValueError):
            users.register("", "pw")
        with self.assertRaises(ValueError):
            users.register("u", "")

    def test_issue_token_valid(self):
        users.register("carol", "pw")
        self.assertTrue(users.authenticate("carol", "pw"))
        tok = auth.issue_token("carol")
        self.assertIsInstance(tok, Token)
        self.assertEqual(tok.user, "carol")
        self.assertEqual(tok.expires, now_ts() + auth.TOKEN_TTL_SECONDS)

    def test_verify_token_with_instance(self):
        tok = auth.issue_token("dave")
        self.assertEqual(auth.verify_token(tok), "dave")

    def test_verify_token_with_string_value(self):
        tok = auth.issue_token("erin")
        self.assertEqual(auth.verify_token(tok.value), "erin")

    def test_forged_token_rejected(self):
        # A random string that was never issued.
        self.assertIsNone(auth.verify_token("forged-value-12345"))
        # An unknown Token instance that was not issued by this service.
        fake = Token(value="another-forged-value", user="mallory",
                     expires=now_ts() + 3600)
        self.assertIsNone(auth.verify_token(fake))
        # A raw string cannot mint a user on its own.
        self.assertIsNone(auth.verify_token(""))

    def test_expired_token_rejected(self):
        tok = auth.issue_token("frank")
        # Force expiry.
        tok.expires = now_ts() - 1
        self.assertIsNone(auth.verify_token(tok))

    def test_full_flow(self):
        """register -> authenticate -> issue_token -> verify_token."""
        users._reset_for_tests()
        auth._reset_for_tests()

        users.register("gina", "hunter2")
        ok = users.authenticate("gina", "hunter2")
        self.assertTrue(ok)

        tok = auth.issue_token("gina")
        self.assertEqual(auth.verify_token(tok), "gina")
        self.assertEqual(auth.verify_token(tok.value), "gina")

    def test_token_values_are_unguessable(self):
        t1 = auth.issue_token("hank")
        t2 = auth.issue_token("hank")
        self.assertNotEqual(t1.value, t2.value)
        # 256 bits of entropy -> token_urlsafe produces ~86 base64url chars
        self.assertGreater(len(t1.value), 40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
