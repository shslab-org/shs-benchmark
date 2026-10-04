"""QA tests for stats.py against SPEC.md.

Shipped stats.py has defects:
1. mean([]) should raise ValueError (returns 0.0 instead).
2. median(even-length list) should average the two middle values (returns only s[mid]).
3. variance should be SAMPLE variance (n-1 divisor) (uses n divisor instead).
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import stats


# ---------- mean ----------

def test_mean_basic():
    assert stats.mean([1, 2, 3, 4]) == 2.5


def test_mean_single_element():
    assert stats.mean([42]) == 42.0


def test_mean_floats():
    assert stats.mean([1.5, 2.5]) == 2.0


def test_mean_negative_values():
    assert stats.mean([-1, -2, -3]) == -2.0


def test_mean_empty_raises_valueerror():
    with pytest.raises(ValueError):
        stats.mean([])


# ---------- median ----------

def test_median_odd_length():
    assert stats.median([1, 2, 3, 4, 5]) == 3


def test_median_even_length_averages_middles():
    # Shipped bug: returns s[mid] instead of avg(s[mid-1], s[mid])
    assert stats.median([1, 2, 3, 4]) == 2.5


def test_median_even_length_unsorted_input():
    assert stats.median([4, 1, 2, 3]) == 2.5


def test_median_even_length_differing_middles():
    assert stats.median([1, 2, 8, 9]) == 5.0


def test_median_single_value():
    assert stats.median([7]) == 7


def test_median_negative_and_mixed():
    assert stats.median([3, 1, 2, 0, 4]) == 2


def test_median_even_duplicate_middles():
    assert stats.median([1, 2, 2, 4]) == 2.0


def test_median_empty_raises():
    with pytest.raises(ValueError):
        stats.median([])


# ---------- variance ----------

def test_variance_is_sample_variance():
    # Shipped bug: uses population divisor n instead of sample n-1.
    # Spec: sample variance, divide by n-1.
    # [2, 4, 4, 4, 5, 5, 7, 9] -> sample variance is exactly 4.571428571428571
    assert stats.variance([2, 4, 4, 4, 5, 5, 7, 9]) == 4.571428571428571


def test_variance_two_elements():
    # For [2, 8]: mean=5, deviations 3 and 3, sample variance = (9+9)/1 = 18
    assert stats.variance([2, 8]) == 18.0


def test_variance_known_small_values():
    # [1, 2, 3, 4]: mean=2.5, sum sq dev = 5, sample var = 5/3
    assert stats.variance([1, 2, 3, 4]) == pytest.approx(5.0 / 3.0)


def test_variance_fewer_than_two_raises():
    with pytest.raises(ValueError):
        stats.variance([3])
    with pytest.raises(ValueError):
        stats.variance([])


def test_variance_constant_values_zero():
    assert stats.variance([5, 5, 5]) == 0.0


def test_variance_float_values():
    # [0.0, 1.0]: sample variance = ((0-0.5)^2 + (1-0.5)^2)/1 = 0.5
    assert stats.variance([0.0, 1.0]) == 0.5


# ---------- percentile ----------

def test_percentile_ends():
    xs = [1, 2, 3, 4, 5]
    assert stats.percentile(xs, 0) == 1
    assert stats.percentile(xs, 100) == 5


def test_percentile_quartiles():
    # p=25 -> k=1.0 -> s[1] = 2 ; p=75 -> k=3.0 -> s[3] = 4
    xs = [1, 2, 3, 4, 5]
    assert stats.percentile(xs, 25) == 2
    assert stats.percentile(xs, 75) == 4


def test_percentile_median_matches_50th():
    assert stats.percentile([1, 2, 3, 4], 50) == 2.5


def test_percentile_linear_interpolation_even():
    # xs=[0, 10], p=25: k=0.25 -> 0 + 0.25*(10-0) = 2.5
    assert stats.percentile([0, 10], 25) == 2.5


def test_percentile_linear_interpolation_noninteger():
    # xs=[1,2,3,4,5,6], p=50: k=2.5 -> s[2] + 0.5*(s[3]-s[2]) = 3 + 0.5 = 3.5
    assert stats.percentile([1, 2, 3, 4, 5, 6], 50) == 3.5


def test_percentile_single_element():
    assert stats.percentile([42], 50) == 42


def test_percentile_unsorted_input():
    assert stats.percentile([9, 1, 5, 3], 0) == 1
    assert stats.percentile([9, 1, 5, 3], 100) == 9


def test_percentile_agrees_with_numpy_linear():
    # Cross-check against numpy's linear interpolation method for a few points.
    import numpy as np
    xs = [10, 20, 30, 40, 50, 60]
    for p in (0, 10, 25, 50, 60, 90, 100):
        expected = float(np.percentile(xs, p))
        assert stats.percentile(xs, p) == expected, f"p={p}"


def test_percentile_empty_raises():
    with pytest.raises((ValueError, IndexError)):
        stats.percentile([], 50)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
