"""Tests for the core calculator and its plugins."""
import pytest

from calculator import Calculator
from plugins import add, subtract, multiply, divide


@pytest.fixture
def calc():
    c = Calculator()
    add.register(c)
    subtract.register(c)
    multiply.register(c)
    divide.register(c)
    return c


class TestCore:
    def test_register_and_calculate(self, calc):
        assert calc.calculate("add", 2, 2) == 4

    def test_unknown_operation_raises_keyerror(self, calc):
        with pytest.raises(KeyError):
            calc.calculate("unknown", 1, 1)

    def test_operations_lists_registered_names(self, calc):
        ops = calc.operations()
        assert "add" in ops
        assert "subtract" in ops
        assert "multiply" in ops
        assert "divide" in ops
        assert isinstance(ops, list)

    def test_register_new_operation(self):
        c = Calculator()
        c.register("square", lambda x: x * x)
        assert c.calculate("square", 5) == 25

    def test_operations_empty_by_default(self):
        assert Calculator().operations() == []


class TestAddPlugin:
    def test_basic(self, calc):
        assert calc.calculate("add", 2, 2) == 4

    def test_negative(self, calc):
        assert calc.calculate("add", -1, -1) == -2


class TestSubtractPlugin:
    def test_basic(self, calc):
        assert calc.calculate("subtract", 10, 4) == 6

    def test_negative_result(self, calc):
        assert calc.calculate("subtract", 2, 5) == -3


class TestMultiplyPlugin:
    def test_basic(self, calc):
        assert calc.calculate("multiply", 3, 3) == 9

    def test_zero(self, calc):
        assert calc.calculate("multiply", 0, 5) == 0


class TestDividePlugin:
    def test_basic(self, calc):
        assert calc.calculate("divide", 9, 2) == 4.5

    def test_zero_divisor_raises(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.calculate("divide", 1, 0)
