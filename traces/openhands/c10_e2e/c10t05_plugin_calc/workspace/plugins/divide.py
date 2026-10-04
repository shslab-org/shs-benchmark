"""Plugin registering the "divide" operation.

Raise ZeroDivisionError when the divisor is zero.
"""


def _divide(a, b):
    """Divide ``a`` by ``b``.

    Raises:
        ZeroDivisionError: if ``b`` is zero.
    """
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a / b


def register(calc):
    calc.register("divide", _divide)
