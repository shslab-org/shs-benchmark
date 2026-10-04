"""Pytest suite for the calculator core and its plugins."""

import pytest

from calculator import Calculator
from plugins import add, divide, multiply, subtract


@pytest.fixture
def calc():
    c = Calculator()
    for plugin in (add, subtract, multiply, divide):
        plugin.register(c)
    return c


class TestCore:
    def test_register_and_calculate(self):
        c = Calculator()
        c.register("double", lambda x: x * 2)
        assert c.calculate("double", 5) == 10

    def test_operations_returns_registered_names(self):
        c = Calculator()
        c.register("a", lambda x: x)
        c.register("b", lambda x: x)
        assert sorted(c.operations()) == ["a", "b"]

    def test_calculate_unknown_raises_keyerror(self):
        c = Calculator()
        with pytest.raises(KeyError):
            c.calculate("nope", 1)

    def test_register_rejects_non_callable(self):
        c = Calculator()
        with pytest.raises(TypeError):
            c.register("bad", 42)

    def test_register_overwrites_existing(self):
        c = Calculator()
        c.register("x", lambda a: a + 1)
        c.register("x", lambda a: a + 100)
        assert c.calculate("x", 1) == 101


class TestAdd:
    def test_basic(self, calc):
        assert calc.calculate("add", 2, 2) == 4

    def test_negative_numbers(self, calc):
        assert calc.calculate("add", -5, 10) == 5


class TestSubtract:
    def test_basic(self, calc):
        assert calc.calculate("subtract", 10, 4) == 6


class TestMultiply:
    def test_basic(self, calc):
        assert calc.calculate("multiply", 3, 3) == 9

    def test_by_zero(self, calc):
        assert calc.calculate("multiply", 7, 0) == 0


class TestDivide:
    def test_basic(self, calc):
        assert calc.calculate("divide", 9, 2) == 4.5

    def test_zero_divisor_raises(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.calculate("divide", 1, 0)


def test_plugins_register_all_operations(calc):
    assert sorted(calc.operations()) == ["add", "divide", "multiply", "subtract"]
