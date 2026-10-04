"""Plugin-style calculator core.

The :class:`Calculator` is intentionally minimal: it only knows how to
store named operations and invoke them. All concrete math operations
(plus, minus, times, ...) live in *plugins* that register themselves
on a ``Calculator`` instance via ``register``.
"""

from __future__ import annotations

from typing import Any, Callable


class Calculator:
    """A tiny plugin-style calculator core.

    Operations are registered under a string name by plugin modules
    (see ``plugins/``) and applied by name via :meth:`calculate`.
    """

    def __init__(self) -> None:
        self._ops: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        """Register an operation ``fn`` under ``name``.

        Args:
            name: Operation name (e.g. ``"add"``).
            fn:   Callable that implements the operation.

        Raises:
            TypeError: if ``fn`` is not callable.
            ValueError: if ``name`` is empty.
        """
        if not name:
            raise ValueError("operation name must not be empty")
        if not callable(fn):
            raise TypeError("operation must be callable")
        self._ops[name] = fn

    def calculate(self, name: str, *args: Any) -> Any:
        """Apply the operation registered under ``name`` to ``*args``.

        Raises:
            KeyError: if no operation is registered under ``name``.
        """
        if name not in self._ops:
            raise KeyError(f"no operation registered under {name!r}")
        return self._ops[name](*args)

    def operations(self) -> list[str]:
        """Return the names of all registered operations (sorted)."""
        return sorted(self._ops)
