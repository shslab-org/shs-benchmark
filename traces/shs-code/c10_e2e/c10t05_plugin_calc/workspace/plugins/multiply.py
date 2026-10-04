"""Plugin: multiplication (``multiply``).

Registers a two-argument ``multiply`` operation on a ``Calculator``.
"""

from __future__ import annotations


def _multiply(a: float, b: float) -> float:
    """Return ``a * b``."""
    return a * b


def register(calc) -> None:
    """Register the ``multiply`` operation on ``calc``.

    Args:
        calc: A ``calculator.Calculator`` instance.
    """
    calc.register("multiply", _multiply)
