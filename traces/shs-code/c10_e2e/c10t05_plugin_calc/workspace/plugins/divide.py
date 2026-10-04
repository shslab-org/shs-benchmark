"""Plugin: division (``divide``).

Registers a two-argument ``divide`` operation on a ``Calculator``.

.. note::
   Raises :class:`ZeroDivisionError` when the divisor is zero.
"""

from __future__ import annotations


def _divide(a: float, b: float) -> float:
    """Return ``a / b``.

    Raises:
        ZeroDivisionError: if ``b`` is zero.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


def register(calc) -> None:
    """Register the ``divide`` operation on ``calc``.

    The registered operation raises :class:`ZeroDivisionError` when the
    second argument (divisor) is zero.

    Args:
        calc: A ``calculator.Calculator`` instance.
    """
    calc.register("divide", _divide)
