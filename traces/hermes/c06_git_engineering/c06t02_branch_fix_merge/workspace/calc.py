"""Calculator with a bug in divide()."""


def add(a, b):
    return a + b


def divide(a, b):
    return a / b        # BUG: ZeroDivisionError instead of None
