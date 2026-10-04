"""QA tests for stats.py — verifies the module against SPEC.md.

Run from anywhere: this file puts the repo directory on sys.path so that
``import stats`` picks up the module under test, regardless of cwd.
"""
import math
import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import stats  # noqa: E402


def approx(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)


# ---------------------------------------------------------------- mean

def test_mean_basic():
    assert approx(stats.mean([1, 2, 3, 4]), 2.5)


def test_mean_single_value():
    assert approx(stats.mean([7]), 7.0)


def test_mean_negative_and_float():
    assert approx(stats.mean([-2.0, 2.0, 1.5]), 0.5)


def test_mean_empty_raises_value_error():
    # SPEC: mean raises ValueError on empty input.
    with pytest.raises(ValueError):
        stats.mean([])


# ---------------------------------------------------------------- median

def test_median_odd_length():
    assert approx(stats.median([3, 1, 2]), 2)


def test_median_even_length_averages_two_middles():
    # SPEC: even length -> average of the two middle values.
    assert approx(stats.median([1, 2, 3, 4]), 2.5)
    assert approx(stats.median([4, 1, 2, 3]), 2.5)


def test_median_even_length_pair():
    assert approx(stats.median([10, 20]), 15.0)


def test_median_ignores_input_order():
    assert approx(stats.median([50, 10, 30]), 30)


def test_median_empty_raises_value_error():
    with pytest.raises(ValueError):
        stats.median([])


# ---------------------------------------------------------------- variance

def test_variance_is_sample_variance():
    # SPEC: sample variance, divide by n-1.
    xs = [1, 2, 3, 4]
    # mean 2.5 -> 2.25 + 0.25 + 0.25 + 2.25 = 5.0; /3 = 5/3
    assert approx(stats.variance(xs), 5.0 / 3.0)


def test_variance_sample_not_population():
    # Values chosen so population (n) and sample (n-1) denominators
    # give clearly different results: population would be 0.5,
    # sample must be 1.0.
    xs = [0, 1, 1]
    # mean = 2/3; deviations: 4/9 + 1/9 + 1/9 = 6/9 = 2/3
    # sample: (2/3) / 2 = 1/3
    assert approx(stats.variance(xs), 1.0 / 3.0)
    with pytest.raises(AssertionError, match="population"):
        assert approx(stats.variance(xs), (2.0 / 3.0) / 3.0), \
            "variance() divides by n (population), spec requires n-1 (sample)"


def test_variance_single_value_raises():
    # SPEC: raises ValueError when fewer than 2 values.
    with pytest.raises(ValueError):
        stats.variance([42])


def test_variance_empty_raises():
    with pytest.raises(ValueError):
        stats.variance([])


def test_variance_two_values():
    # [1, 3]: mean 2, deviations 1+1 = 2, /1 = 2
    assert approx(stats.variance([1, 3]), 2.0)


# ---------------------------------------------------------------- percentile

def test_percentile_linear_interpolation():
    # numpy 'linear' method on [10, 20, 30, 40]:
    # p=50 -> k=1.5 -> 20 + 0.5*(30-20) = 25
    assert approx(stats.percentile([10, 20, 30, 40], 50), 25.0)


def test_percentile_quartiles():
    xs = [1, 2, 3, 4, 5]
    # k = 4*p/100
    assert approx(stats.percentile(xs, 0), 1.0)
    assert approx(stats.percentile(xs, 25), 2.0)
    assert approx(stats.percentile(xs, 50), 3.0)
    assert approx(stats.percentile(xs, 75), 4.0)
    assert approx(stats.percentile(xs, 100), 5.0)


def test_percentile_sub_index_interpolation():
    xs = [1, 2, 3]
    # p=50 -> k=1 -> exact middle value 2
    assert approx(stats.percentile(xs, 50), 2.0)
    # p=25 -> k=0.5 -> 1 + 0.5*(2-1) = 1.5
    assert approx(stats.percentile(xs, 25), 1.5)
    # p=75 -> k=1.5 -> 2 + 0.5*(3-2) = 2.5
    assert approx(stats.percentile(xs, 75), 2.5)


def test_percentile_single_value():
    assert approx(stats.percentile([9], 0), 9.0)
    assert approx(stats.percentile([9], 50), 9.0)
    assert approx(stats.percentile([9], 100), 9.0)


def test_percentile_even_length_matches_numpy_linear():
    # matches numpy.percentile([1,2,3,4], 25) == 1.75 and p=75 == 3.25
    assert approx(stats.percentile([1, 2, 3, 4], 25), 1.75)
    assert approx(stats.percentile([1, 2, 3, 4], 75), 3.25)


def test_percentile_order_independent():
    a = [7, 3, 9, 1, 5]
    assert approx(stats.percentile(a, 40), stats.percentile(sorted(a), 40))
