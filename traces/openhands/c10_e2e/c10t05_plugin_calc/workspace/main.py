"""Wire the calculator core with its plugins and demonstrate it."""

from calculator import Calculator

from plugins import add, divide, multiply, subtract

PLUGINS = [add, subtract, multiply, divide]


def build_calculator() -> Calculator:
    calc = Calculator()
    for plugin in PLUGINS:
        plugin.register(calc)
    return calc


def main() -> None:
    calc = build_calculator()
    print("Registered operations:", calc.operations())

    print("2+2 =", calc.calculate("add", 2, 2))
    print("10-4 =", calc.calculate("subtract", 10, 4))
    print("3*3 =", calc.calculate("multiply", 3, 3))
    print("9/2 =", calc.calculate("divide", 9, 2))


if __name__ == "__main__":
    main()
