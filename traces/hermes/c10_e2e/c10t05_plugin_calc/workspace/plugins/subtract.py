"""Subtract plugin: registers a ``subtract`` operation."""


def subtract(a, b):
    """Return ``a - b``."""
    return a - b


def register(calc):
    """Register the ``subtract`` operation on ``calc``."""
    calc.register("subtract", subtract)
