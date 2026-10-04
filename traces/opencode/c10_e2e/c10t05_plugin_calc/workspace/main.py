from calculator import Calculator


def main():
    calc = Calculator()

    from plugins import add, subtract, multiply, divide
    for plugin in (add, subtract, multiply, divide):
        plugin.register(calc)

    print(f"Registered operations: {calc.operations()}")
    print(f"2 + 2 = {calc.calculate('add', 2, 2)}")
    print(f"10 - 4 = {calc.calculate('subtract', 10, 4)}")
    print(f"3 * 3 = {calc.calculate('multiply', 3, 3)}")
    print(f"9 / 2 = {calc.calculate('divide', 9, 2)}")


if __name__ == "__main__":
    main()
