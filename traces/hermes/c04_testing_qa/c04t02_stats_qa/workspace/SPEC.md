SPEC for stats.py:

- mean(xs): arithmetic mean; raises ValueError on empty input.
- median(xs): middle of sorted values; for even length, the average of the two
  middle values.
- variance(xs): SAMPLE variance (divide by n-1 for n >= 2); raises ValueError
  when fewer than 2 values.
- percentile(xs, p): linear-interpolation percentile (numpy 'linear' method);
  p in [0, 100].

Your job: write tests_agent/test_stats.py that fails against any module
violating this spec and passes against a correct one. The shipped stats.py
violates it in at least 3 places. Do NOT modify stats.py.