"""Tests for the calculator core and its plugins."""

import pytest

from calculator import Calculator
from plugins import add, subtract, multiply, divide


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

class TestCalculatorCore:
    def test_new_calculator_has_no_operations(self):
        assert Calculator().operations() == []

    def test_register_then_operations(self):
        calc = Calculator()
        calc.register("add", lambda a, b: a + b)
        assert calc.operations() == ["add"]

    def test_register_multiple_operations(self):
        calc = Calculator()
        calc.register("add", lambda a, b: a + b)
        calc.register("sub", lambda a, b: a - b)
        assert sorted(calc.operations()) == ["add", "sub"]

    def test_calculate_applies_operation(self):
        calc = Calculator()
        calc.register("add", lambda a, b: a + b)
        assert calc.calculate("add", 2, 3) == 5

    def test_calculate_forwards_multiple_args(self):
        calc = Calculator()
        calc.register("sum_all", lambda *xs: sum(xs))
        assert calc.calculate("sum_all", 1, 2, 3, 4) == 10

    def test_calculate_no_args(self):
        calc = Calculator()
        calc.register("answer", lambda: 42)
        assert calc.calculate("answer") == 42

    def test_calculate_unknown_name_raises_keyerror(self):
        calc = Calculator()
        with pytest.raises(KeyError):
            calc.calculate("nope", 1, 2)

    def test_unknown_name_keyerror_message(self):
        calc = Calculator()
        with pytest.raises(KeyError, match="nope"):
            calc.calculate("nope", 1, 2)

    def test_register_requires_callable(self):
        calc = Calculator()
        with pytest.raises(TypeError):
            calc.register("bad", 42)

    def test_re_register_replaces_operation(self):
        calc = Calculator()
        calc.register("add", lambda a, b: a + b)
        calc.register("add", lambda a, b: a * b)
        assert calc.calculate("add", 2, 3) == 6


# ---------------------------------------------------------------------------
# Plugins
# ---------------------------------------------------------------------------

class TestAddPlugin:
    def test_operation_registered(self):
        calc = Calculator()
        add.register(calc)
        assert "add" in calc.operations()

    def test_add(self):
        calc = Calculator()
        add.register(calc)
        assert calc.calculate("add", 2, 3) == 5
        assert calc.calculate("add", -1, 1) == 0
        assert calc.calculate("add", 0.5, 0.25) == 0.75


class TestSubtractPlugin:
    def test_operation_registered(self):
        calc = Calculator()
        subtract.register(calc)
        assert "subtract" in calc.operations()

    def test_subtract(self):
        calc = Calculator()
        subtract.register(calc)
        assert calc.calculate("subtract", 10, 4) == 6
        assert calc.calculate("subtract", 0, 5) == -5


class TestMultiplyPlugin:
    def test_operation_registered(self):
        calc = Calculator()
        multiply.register(calc)
        assert "multiply" in calc.operations()

    def test_multiply(self):
        calc = Calculator()
        multiply.register(calc)
        assert calc.calculate("multiply", 3, 3) == 9
        assert calc.calculate("multiply", 0, 100) == 0


class TestDividePlugin:
    def test_operation_registered(self):
        calc = Calculator()
        divide.register(calc)
        assert "divide" in calc.operations()

    def test_divide(self):
        calc = Calculator()
        divide.register(calc)
        assert calc.calculate("divide", 9, 2) == 4.5

    def test_divide_by_zero_raises(self):
        calc = Calculator()
        divide.register(calc)
        with pytest.raises(ZeroDivisionError):
            calc.calculate("divide", 1, 0)

    def test_divide_documented(self):
        assert divide.divide.__doc__ is not None
        assert "ZeroDivisionError" in divide.divide.__doc__


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------

class TestWiring:
    def test_all_plugins_on_one_calculator(self):
        calc = Calculator()
        for plugin in (add, subtract, multiply, divide):
            plugin.register(calc)
        assert sorted(calc.operations()) == ["add", "divide", "multiply", "subtract"]

    def test_demonstrated_values(self):
        calc = Calculator()
        for plugin in (add, subtract, multiply, divide):
            plugin.register(calc)
        assert calc.calculate("add", 2, 2) == 4
        assert calc.calculate("subtract", 10, 4) == 6
        assert calc.calculate("multiply", 3, 3) == 9
        assert calc.calculate("divide", 9, 2) == 4.5

    def test_main_builds_calculator(self):
        from main import build_calculator
        calc = build_calculator()
        assert sorted(calc.operations()) == ["add", "divide", "multiply", "subtract"]
