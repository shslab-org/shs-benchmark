"""Wire the calculator core to all plugins and demonstrate it."""

from calculator import Calculator
from plugins import add, subtract, multiply, divide


def build_calculator() -> Calculator:
    """Create a Calculator and register every bundled plugin on it."""
    calc = Calculator()
    for plugin in (add, subtract, multiply, divide):
        plugin.register(calc)
    return calc


def main() -> None:
    calc = build_calculator()
    print(f"available operations: {sorted(calc.operations())}")
    print(f"2 + 2  = {calc.calculate('add', 2, 2)}")
    print(f"10 - 4 = {calc.calculate('subtract', 10, 4)}")
    print(f"3 * 3  = {calc.calculate('multiply', 3, 3)}")
    print(f"9 / 2  = {calc.calculate('divide', 9, 2)}")


if __name__ == "__main__":
    main()
