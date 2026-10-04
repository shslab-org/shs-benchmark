"""Minimal calculator core: an extensible registry of named operations."""


class Calculator:
    def __init__(self) -> None:
        self._operations = {}

    def register(self, name: str, fn) -> None:
        """Register an operation callable under a name."""
        if not callable(fn):
            raise TypeError("fn must be callable")
        self._operations[name] = fn

    def calculate(self, name: str, *args):
        """Apply the registered operation named ``name`` to ``args``.

        Raises KeyError if the operation has not been registered.
        """
        return self._operations[name](*args)

    def operations(self) -> list:
        """Return the names of all registered operations."""
        return list(self._operations)
