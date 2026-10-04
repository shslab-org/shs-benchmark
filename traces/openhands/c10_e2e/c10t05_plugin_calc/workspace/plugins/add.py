"""Plugin registering the "add" operation."""


def _add(a, b):
    return a + b


def register(calc):
    calc.register("add", _add)
