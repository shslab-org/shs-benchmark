"""Statistics — reference fixed version."""
import math


def mean(xs):
    if not xs:
        raise ValueError("empty")
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("empty")
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def variance(xs):
    if len(xs) < 2:
        raise ValueError("need >= 2 values")
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def percentile(xs, p):
    s = sorted(xs)
    k = (len(s) - 1) * p / 100.0
    f = math.floor(k); c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] + (k - f) * (s[int(c)] - s[int(f)])
