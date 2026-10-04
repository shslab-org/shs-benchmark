"""Pytest suite for the calculator core and its plugins.

Covers:
  - Calculator.register / calculate / operations behaviour
  - Each plugin (add, subtract, multiply, divide) registers correctly
  - divide raises ZeroDivisionError on zero divisor
  - unknown operation names raise KeyError
"""

import pytest

from calculator import Calculator
from plugins import add, subtract, multiply, divide


# ── Core tests ────────────────────────────────────────────────────────────────

class TestCalculatorCore:
    """Test the Calculator core class in isolation."""

    def test_start_empty(self):
        calc = Calculator()
        assert calc.operations() == []

    def test_register_and_calculate(self):
        calc = Calculator()
        calc.register("double", lambda x: x * 2)
        assert calc.calculate("double", 21) == 42

    def test_unknown_operation_raises_keyerror(self):
        calc = Calculator()
        with pytest.raises(KeyError):
            calc.calculate("nope", 1)

    def test_operations_returns_sorted_names(self):
        calc = Calculator()
        calc.register("b", lambda x: x)
        calc.register("a", lambda x: x)
        calc.register("c", lambda x: x)
        assert calc.operations() == ["a", "b", "c"]

    def test_register_rejects_empty_name(self):
        calc = Calculator()
        with pytest.raises(ValueError):
            calc.register("", lambda: None)

    def test_register_rejects_non_callable(self):
        calc = Calculator()
        with pytest.raises(TypeError):
            calc.register("bad", 42)

    def test_multiple_args_passed_through(self):
        calc = Calculator()
        calc.register("sum3", lambda a, b, c: a + b + c)
        assert calc.calculate("sum3", 1, 2, 3) == 6


# ── Plugin tests ──────────────────────────────────────────────────────────────

@pytest.fixture
def calc() -> Calculator:
    """A fresh Calculator with all four plugins registered."""
    c = Calculator()
    for plugin in (add, subtract, multiply, divide):
        plugin.register(c)
    return c


class TestAddPlugin:
    def test_add_two_ints(self, calc):
        assert calc.calculate("add", 2, 2) == 4

    def test_add_floats(self, calc):
        assert calc.calculate("add", 1.5, 2.5) == 4.0

    def test_add_registered(self, calc):
        assert "add" in calc.operations()


class TestSubtractPlugin:
    def test_subtract(self, calc):
        assert calc.calculate("subtract", 10, 4) == 6

    def test_subtract_negative_result(self, calc):
        assert calc.calculate("subtract", 4, 10) == -6

    def test_subtract_registered(self, calc):
        assert "subtract" in calc.operations()


class TestMultiplyPlugin:
    def test_multiply(self, calc):
        assert calc.calculate("multiply", 3, 3) == 9

    def test_multiply_by_zero(self, calc):
        assert calc.calculate("multiply", 7, 0) == 0

    def test_multiply_registered(self, calc):
        assert "multiply" in calc.operations()


class TestDividePlugin:
    def test_divide(self, calc):
        assert calc.calculate("divide", 9, 2) == 4.5

    def test_divide_by_zero_raises(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.calculate("divide", 1, 0)

    def test_divide_registered(self, calc):
        assert "divide" in calc.operations()


class TestAllPluginsTogether:
    def test_operations_lists_all_four(self, calc):
        assert calc.operations() == ["add", "divide", "multiply", "subtract"]

    def test_demo_values(self, calc):
        """Mirror the four examples from main.py."""
        assert calc.calculate("add", 2, 2) == 4
        assert calc.calculate("subtract", 10, 4) == 6
        assert calc.calculate("multiply", 3, 3) == 9
        assert calc.calculate("divide", 9, 2) == 4.5
