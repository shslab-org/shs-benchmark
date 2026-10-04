"""Minimal calculator core.

The core knows nothing about specific operations: plugins register
callable operations under a name via :meth:`Calculator.register`, and
the core applies them via :meth:`Calculator.calculate`.
"""

from typing import Callable


class Calculator:
    """Holds a name -> operation registry and applies registered ops."""

    def __init__(self) -> None:
        self._ops: dict[str, Callable] = {}

    def register(self, name: str, fn) -> None:
        """Register an operation callable ``fn`` under ``name``."""
        if not callable(fn):
            raise TypeError(f"operation {name!r} must be callable")
        self._ops[name] = fn

    def calculate(self, name: str, *args):
        """Apply the registered operation ``name`` to ``*args``.

        Raises ``KeyError`` if ``name`` is not a registered operation.
        """
        if name not in self._ops:
            raise KeyError(f"unknown operation: {name!r}")
        return self._ops[name](*args)

    def operations(self) -> list:
        """Return the names of all registered operations."""
        return list(self._ops.keys())
