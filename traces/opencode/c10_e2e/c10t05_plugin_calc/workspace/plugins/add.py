"""Addition plugin: registers the `add` operation."""


def add(a, b):
    return a + b


def register(calc):
    calc.register("add", add)
