"""Multiplication plugin: registers the `multiply` operation."""


def multiply(a, b):
    return a * b


def register(calc):
    calc.register("multiply", multiply)
