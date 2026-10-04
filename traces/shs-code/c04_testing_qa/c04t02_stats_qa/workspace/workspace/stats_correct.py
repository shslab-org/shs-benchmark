"""Correct reference implementation of the SPEC (test harness only)."""
import math


def mean(xs):
    if len(xs) == 0:
        raise ValueError("mean of empty list")
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("empty")
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def variance(xs):
    if len(xs) < 2:
        raise ValueError("variance needs at least 2 values")
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def percentile(xs, p):
    """numpy 'linear' interpolation; p in [0,100]."""
    s = sorted(xs)
    if len(s) == 0:
        raise ValueError("empty")
    k = (len(s) - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] + (k - f) * (s[int(c)] - s[int(f)])
