import math

import pytest

from stats import mean, median, variance, percentile


def test_mean_basic():
    assert mean([1, 2, 3, 4]) == 2.5
    assert mean([10]) == 10


def test_mean_empty_raises():
    with pytest.raises(ValueError):
        mean([])


def test_median_odd():
    assert median([3, 1, 2]) == 2
    assert median([7]) == 7


def test_median_even_averages_middle():
    assert median([1, 2, 3, 4]) == 2.5
    assert median([1, 2, 3, 4, 5, 6]) == 3.5
    assert median([10, 0]) == 5.0


def test_median_empty_raises():
    with pytest.raises(ValueError):
        median([])


def test_variance_sample():
    # [1, 2, 3, 4, 5]: mean=3, SS=10, sample variance = 10/4 = 2.5
    assert variance([1, 2, 3, 4, 5]) == pytest.approx(2.5)
    assert variance([2, 4]) == pytest.approx(2.0)


def test_variance_two_values():
    assert variance([1, 3]) == pytest.approx(2.0)


def test_variance_fewer_than_two_raises():
    with pytest.raises(ValueError):
        variance([])
    with pytest.raises(ValueError):
        variance([1])


def test_percentile_endpoints():
    assert percentile([1, 2, 3, 4, 5], 0) == 1
    assert percentile([1, 2, 3, 4, 5], 100) == 5


def test_percentile_linear_interpolation():
    # numpy-style linear method on [1,2,3,4,5]
    assert percentile([1, 2, 3, 4, 5], 50) == pytest.approx(3)
    assert percentile([1, 2, 3, 4, 5], 25) == pytest.approx(2)
    assert percentile([1, 2, 3, 4, 5], 75) == pytest.approx(4)
    # 30th percentile: k = 4*0.30 = 1.2 -> s[1] + 0.2*(s[2]-s[1]) = 2 + 0.2 = 2.2
    assert percentile([1, 2, 3, 4, 5], 30) == pytest.approx(2.2)
    # even length
    assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)


def test_percentile_out_of_range():
    with pytest.raises(ValueError):
        percentile([1, 2, 3], -1)
    with pytest.raises(ValueError):
        percentile([1, 2, 3], 101)


# Extra spec-coverage checks (guards against subtly wrong implementations)

def test_mean_various():
    assert mean([5]) == 5
    assert mean([2, 4]) == pytest.approx(3.0)
    assert mean([1.5, 2.5]) == pytest.approx(2.0)


def test_median_not_mutating_input():
    data = [4, 1, 3, 2]
    _ = median(data)
    assert data == [4, 1, 3, 2]


def test_median_duplicates_even():
    # [1, 2, 2, 3]: middle two are 2 and 2 -> 2.0 (average required by spec)
    assert median([1, 2, 2, 3]) == pytest.approx(2.0)


def test_variance_known_values():
    # [2, 4, 4, 4, 5, 5, 7, 9]: sample variance = 32/7
    assert variance([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(32 / 7)
    # [10, 20]: sample variance = 50
    assert variance([10, 20]) == pytest.approx(50.0)


def test_percentile_matches_reference_linear_values():
    # numpy-verified linear-method values.
    # [3, 7, 1, 5, 9, 2] -> sorted [1, 2, 3, 5, 7, 9]
    # p=10 -> k=(6-1)*0.10=0.5 -> s[0]+0.5*(s[1]-s[0]) = 1+0.5 = 1.5
    assert percentile([3, 7, 1, 5, 9, 2], 10) == pytest.approx(1.5)
    # p=75 -> k=(6-1)*0.75=3.75 -> s[3]+0.75*(s[4]-s[3]) = 5+0.75*2 = 6.5
    assert percentile([3, 7, 1, 5, 9, 2], 75) == pytest.approx(6.5)
    # p=90 -> k=(6-1)*0.90=4.5 -> s[4]+0.5*(s[5]-s[4]) = 7+0.5*2 = 8.0
    assert percentile([3, 7, 1, 5, 9, 2], 90) == pytest.approx(8.0)
    # unsorted input must not matter
    assert percentile([5, 1, 3], 50) == pytest.approx(3)


def test_percentile_single_element():
    assert percentile([42], 0) == 42
    assert percentile([42], 50) == 42
    assert percentile([42], 100) == 42
