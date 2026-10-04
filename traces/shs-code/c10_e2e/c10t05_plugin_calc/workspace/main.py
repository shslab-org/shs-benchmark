"""Demonstration entry-point.

Wires the Calculator core with all four plugins and prints
four example calculations: 2+2, 10-4, 3*3, 9/2.

Run:  python main.py
"""

from __future__ import annotations

from calculator import Calculator
from plugins import add, subtract, multiply, divide


def main() -> None:
    calc = Calculator()

    # Register every plugin
    for plugin in (add, subtract, multiply, divide):
        plugin.register(calc)

    print("Registered operations:", calc.operations())
    print()

    # Demonstrate each operation
    print("2 + 2 =", calc.calculate("add", 2, 2))
    print("10 - 4 =", calc.calculate("subtract", 10, 4))
    print("3 * 3 =", calc.calculate("multiply", 3, 3))
    print("9 / 2 =", calc.calculate("divide", 9, 2))


if __name__ == "__main__":
    main()
