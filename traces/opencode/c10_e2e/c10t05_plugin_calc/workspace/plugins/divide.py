"""Division plugin: registers the `divide` operation.

Raises ZeroDivisionError when the divisor is zero.
"""


def divide(a, b):
    """Divide a by b.

    Raises ZeroDivisionError if b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


def register(calc):
    calc.register("divide", divide)
