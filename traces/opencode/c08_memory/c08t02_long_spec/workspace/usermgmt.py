import hashlib
import os
import time


def create_user(username, email, password):
    if not isinstance(username, str) or not username:
        raise ValueError("username must be a non-empty string")
    if not isinstance(email, str) or not email:
        raise ValueError("email must be a non-empty string")
    if not isinstance(password, str) or len(password) < 12:
        raise ValueError("password must be at least 12 characters")

    username = username.lower()
    email = email.lower()

    if username in _USER_REGISTRY:
        raise ValueError("username already registered")
    if email in _EMAIL_REGISTRY:
        raise ValueError("email already registered")

    salt = os.urandom(16).hex()
    password_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    user = {
        "username": username,
        "email": email,
        "password_hash": f"{salt}${password_hash}",
        "created_at": time.time(),
    }

    _USER_REGISTRY[username] = user
    _EMAIL_REGISTRY[email] = user
    return user


_USER_REGISTRY = {}
_EMAIL_REGISTRY = {}
