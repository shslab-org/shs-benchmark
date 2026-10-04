"""Add plugin: registers an ``add`` operation."""


def add(a, b):
    """Return ``a + b``."""
    return a + b


def register(calc):
    """Register the ``add`` operation on ``calc``."""
    calc.register("add", add)
