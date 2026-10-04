"""Plugin registering the "multiply" operation."""


def _multiply(a, b):
    return a * b


def register(calc):
    calc.register("multiply", _multiply)
