"""Plugin registering the "subtract" operation."""


def _subtract(a, b):
    return a - b


def register(calc):
    calc.register("subtract", _subtract)
