"""
Pytest suite for stats.py per SPEC.md.

SPEC (authoritative):
  - mean(xs):        arithmetic mean; raises ValueError on empty input.
  - median(xs):      middle of sorted; even length -> average of two middle.
  - variance(xs):    SAMPLE variance (divide by n-1, n >= 2);
                     raises ValueError when fewer than 2 values.
  - percentile(xs, p): linear-interpolation (numpy 'linear'); p in [0, 100].

This suite MUST FAIL against the shipped (buggy) stats.py and PASS against
any correct implementation of the spec.
"""
import math
import os
import sys

import pytest

# Ensure the project root (where stats.py lives) is importable regardless of
# which directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stats  # noqa: E402


# ---------------------------------------------------------------------------
# mean(xs)
# ---------------------------------------------------------------------------

class TestMean:
    def test_empty_raises_value_error(self):
        """SPEC: mean([]) must raise ValueError. Shipped returns 0.0."""
        with pytest.raises(ValueError):
            stats.mean([])

    def test_single_value(self):
        assert stats.mean([7]) == 7.0

    def test_basic(self):
        assert stats.mean([1, 2, 3, 4]) == 2.5

    def test_negatives_and_floats(self):
        assert math.isclose(stats.mean([-1.0, 1.0, 2.5]), (2.5 / 3.0))

    def test_does_not_mutate_input(self):
        data = [1, 2, 3]
        stats.mean(data)
        assert data == [1, 2, 3]


# ---------------------------------------------------------------------------
# median(xs)
# ---------------------------------------------------------------------------

class TestMedian:
    def test_odd_length_middle(self):
        assert stats.median([3, 1, 2]) == 2

    def test_even_length_average_of_two_middles(self):
        """SPEC: even length -> average of two middle values.
        Shipped returns s[mid] (the larger of the two) instead."""
        assert stats.median([1, 2, 3, 4]) == 2.5

    def test_even_length_unsorted_input(self):
        # sorted([4, 1, 2, 3]) -> [1, 2, 3, 4]; middle two = 2, 3 -> 2.5
        assert stats.median([4, 1, 2, 3]) == 2.5

    def test_two_values(self):
        assert stats.median([10, 20]) == 15.0

    def test_single_value(self):
        assert stats.median([42]) == 42

    def test_float_median_even(self):
        assert math.isclose(stats.median([0.0, 0.1, 0.2, 100.0]), 0.15)


# ---------------------------------------------------------------------------
# variance(xs)  -- SAMPLE variance per spec
# ---------------------------------------------------------------------------

class TestVariance:
    def test_empty_raises_value_error(self):
        """SPEC: fewer than 2 values -> ValueError.
        Shipped: mean([])=0.0, then sum/len -> ZeroDivisionError (or 0.0)."""
        with pytest.raises(ValueError):
            stats.variance([])

    def test_single_value_raises_value_error(self):
        """SPEC: fewer than 2 values -> ValueError. Shipped returns 0.0."""
        with pytest.raises(ValueError):
            stats.variance([5])

    def test_sample_variance_two_values(self):
        """SAMPLE variance of [1, 2]: mean=1.5, n-1=1 ->
        ((0.5)^2 + (0.5)^2)/1 = 0.5.
        Shipped (population, /n) would give 0.25."""
        assert math.isclose(stats.variance([1, 2]), 0.5)

    def test_sample_variance_four_values(self):
        """[1,2,3,4]: mean=2.5, deviations 2.25,0.25,0.25,2.25 -> 5/3.
        Shipped (population /4) gives 1.25 instead."""
        assert math.isclose(stats.variance([1, 2, 3, 4]), 5.0 / 3.0)

    def test_sample_variance_ten(self):
        """Check a non-trivial case so population-vs-sample distinction holds.
        [0,1,2,3,4] mean=2, dev^2 sum = 4+1+0+1+4 = 10; sample = 10/4 = 2.5.
        Shipped population would be 10/5 = 2.0."""
        assert math.isclose(stats.variance([0, 1, 2, 3, 4]), 2.5)

    def test_identical_values_zero(self):
        assert stats.variance([7, 7, 7]) == 0.0

    def test_float_precision_sample_vs_population(self):
        """A value where /n and /(n-1) clearly differ.
        [2, 4, 4, 4, 5, 5, 7, 9] (classic example): mean=5,
        dev^2 sum = 9+1+1+1+0+0+4+16 = 32.
        sample = 32/7 ~ 4.571428571; population = 32/8 = 4.0."""
        v = stats.variance([2, 4, 4, 4, 5, 5, 7, 9])
        assert math.isclose(v, 32.0 / 7.0), f"expected 32/7 ≈ 4.5714, got {v}"
        assert not math.isclose(v, 4.0), "variance looks like population (/n)"


# ---------------------------------------------------------------------------
# percentile(xs, p)
# ---------------------------------------------------------------------------

class TestPercentile:
    def test_zero_returns_min(self):
        assert stats.percentile([3, 1, 2], 0) == 1

    def test_hundred_returns_max(self):
        """p=100 -> k = n-1 -> s[n-1] = max.
        Shipped computes k = (3-1)*100/100 = 2.0 -> s[2] of sorted [1,2,3]
        out-of-range path returns s[2]=3 which coincidentally is the max for
        this case; use a case where s[n] would differ. Sorted [1,2,3],
        p=100 -> k=2 -> must return s[2]=3 (max). Shipped: f=c=2 -> s[2]=3.
        Actually shipped percentile([3,1,2],100) = s[2] = 3 (max, OK); the
        real defect is p values where k lands at s[n-1] via interpolation
        vs out-of-bounds. Use a 2-element case: [5, 10], p=100 -> k = 1*1 = 1
        -> must return 10. Shipped returns s[1] = 10 (OK). Use [5,10] p=0 -> 5."""
        # For n=2, p=100: k = 1*1 = 1 -> s[1] = max = 10
        assert stats.percentile([5, 10], 100) == 10
        # For n=1, p=100: k = 0 -> s[0] = the only value
        assert stats.percentile([7], 100) == 7
        # For n=3 sorted [1,2,3], p=100: k = 2 -> s[2] = 3
        assert stats.percentile([3, 1, 2], 100) == 3

    def test_midpoint_even_linear(self):
        """numpy linear on [1,2,3,4] at p=50 ->
        k = 3*0.5 = 1.5 -> s[1] + 0.5*(s[2]-s[1]) = 2 + 0.5*1 = 2.5"""
        assert math.isclose(stats.percentile([1, 2, 3, 4], 50), 2.5)

    def test_exact_index_no_interpolation(self):
        """p where k is an integer: p=25 on [1,2,3,4] ->
        k = 3*0.25 = 0.75 -> 1 + 0.75*(2-1) = 1.75 (interpolation)."""
        assert math.isclose(stats.percentile([1, 2, 3, 4], 25), 1.75)

    def test_exact_index_integer_k(self):
        """k lands exactly on an index: p on [10,20,30,40], p=50 ->
        k = 3*0.5 = 1.5 -> 20 + 0.5*(30-20) = 25.
        p=0 -> k=0 -> 10. p=100 -> k=3 -> 40."""
        assert stats.percentile([10, 20, 30, 40], 0) == 10
        assert math.isclose(stats.percentile([10, 20, 30, 40], 50), 25)
        assert stats.percentile([10, 20, 30, 40], 100) == 40

    def test_single_element_all_p(self):
        # n=1: k=0 always -> s[0]
        assert stats.percentile([5], 0) == 5
        assert stats.percentile([5], 50) == 5
        assert stats.percentile([5], 100) == 5

    def test_linear_interpolation_match_numpy(self):
        """Cross-check against numpy's own 'linear' method if available;
        otherwise against hand-computed values."""
        xs = [15, 20, 35, 40, 50]
        try:
            import numpy as np
        except ImportError:
            np = None
        if np is not None:
            for p in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                expected = float(np.percentile(xs, p))
                got = stats.percentile(xs, p)
                assert math.isclose(got, expected, abs_tol=1e-9), (
                    f"p={p}: expected {expected}, got {got}"
                )
        else:
            # Hand-computed numpy-linear values for [15,20,35,40,50]
            expected = {
                0: 15.0,
                10: 16.5,
                20: 18.0,
                30: 21.5,
                50: 35.0,
                80: 47.0,
                100: 50.0,
            }
            for p, exp in expected.items():
                got = stats.percentile(xs, p)
                assert math.isclose(got, exp, abs_tol=1e-9), (
                    f"p={p}: expected {exp}, got {got}"
                )

    def test_unsorted_input(self):
        # result depends only on the multiset of values
        assert stats.percentile([40, 10, 30, 20], 50) == stats.percentile(
            [10, 20, 30, 40], 50
        )
