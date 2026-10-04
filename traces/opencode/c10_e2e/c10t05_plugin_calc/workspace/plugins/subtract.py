"""Subtraction plugin: registers the `subtract` operation."""


def subtract(a, b):
    return a - b


def register(calc):
    calc.register("subtract", subtract)
