"""Statistics — CONTAINS SEEDED BUGS for the QA benchmark."""
import math


def mean(xs):
    return sum(xs) / max(len(xs), 1)          # BUG 1: empty list should raise ValueError, returns 0


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("empty")
    mid = n // 2
    if n % 2:
        return s[mid]
    return s[mid]                              # BUG 2: even case returns s[mid] not avg(s[mid-1], s[mid])


def variance(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)   # BUG 3: sample variance should divide n-1 (spec: sample)


def percentile(xs, p):
    """p in [0,100]; linear interpolation (numpy-style)."""
    s = sorted(xs)
    k = (len(s) - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] + (k - f) * (s[int(c)] - s[int(f)])   # correct on purpose
