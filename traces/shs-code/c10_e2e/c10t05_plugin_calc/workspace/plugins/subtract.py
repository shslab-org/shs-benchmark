"""Plugin: subtraction (``subtract``).

Registers a two-argument ``subtract`` operation on a ``Calculator``.
"""

from __future__ import annotations


def _subtract(a: float, b: float) -> float:
    """Return ``a - b``."""
    return a - b


def register(calc) -> None:
    """Register the ``subtract`` operation on ``calc``.

    Args:
        calc: A ``calculator.Calculator`` instance.
    """
    calc.register("subtract", _subtract)
