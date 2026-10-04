import pytest
from calc import add, divide


def test_add():
    assert add(2, 3) == 5


def test_divide_by_zero_should_return_none():
    assert divide(4, 0) is None


def test_divide_ok():
    assert divide(9, 3) == 3
