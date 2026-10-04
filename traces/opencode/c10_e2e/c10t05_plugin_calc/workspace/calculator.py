class Calculator:
    def __init__(self):
        self._ops = {}

    def register(self, name: str, fn) -> None:
        self._ops[name] = fn

    def calculate(self, name: str, *args):
        if name not in self._ops:
            raise KeyError(name)
        return self._ops[name](*args)

    def operations(self) -> list:
        return list(self._ops)
