"""Divide plugin: registers a ``divide`` operation.

The registered operation raises ``ZeroDivisionError`` when the divisor
(``b``) is zero.
"""


def divide(a, b):
    """Return ``a / b``.

    Raises ``ZeroDivisionError`` if ``b`` is zero.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


def register(calc):
    """Register the ``divide`` operation on ``calc``."""
    calc.register("divide", divide)
