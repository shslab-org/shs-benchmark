"""Plugin: addition (``add``).

Registers a two-argument ``add`` operation on a ``Calculator``.
"""

from __future__ import annotations


def _add(a: float, b: float) -> float:
    """Return ``a + b``."""
    return a + b


def register(calc) -> None:
    """Register the ``add`` operation on ``calc``.

    Args:
        calc: A ``calculator.Calculator`` instance.
    """
    calc.register("add", _add)
