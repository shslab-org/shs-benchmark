"""Multiply plugin: registers a ``multiply`` operation."""


def multiply(a, b):
    """Return ``a * b``."""
    return a * b


def register(calc):
    """Register the ``multiply`` operation on ``calc``."""
    calc.register("multiply", multiply)
