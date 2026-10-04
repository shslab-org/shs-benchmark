"""Standalone verification for refactored pricing.py."""
import sys
sys.path.insert(0, '/home/z/my-project/bench_ws/shs-code/c05_refactoring/c05t01_dedupe')
import importlib
import pricing
importlib.reload(pricing)

# 1. Helper semantics (independent hand-checks)
assert pricing._round_cents(0.005) == 0.01, pricing._round_cents(0.005)
assert pricing._round_cents(-0.005) == -0.01, pricing._round_cents(-0.005)
assert pricing._round_cents(1.234) == 1.23, pricing._round_cents(1.234)
assert pricing._round_cents(1.235) == 1.24, pricing._round_cents(1.235)
assert pricing._round_cents(0.0) == 0.0
print("[PASS] _round_cents hand-checks")

assert pricing._apply_tax(0.0) == 0.0
assert pricing._apply_tax(100.0) == 110.0
assert pricing._apply_tax(1.0) == 1.1
print("[PASS] _apply_tax hand-checks")

# 2. Public API signature check (unchanged surface)
import inspect
print("retail_total signature:    ", inspect.signature(pricing.retail_total))
print("wholesale_total signature:  ", inspect.signature(pricing.wholesale_total))
assert list(inspect.signature(pricing.retail_total).parameters) == ["items"]
assert list(inspect.signature(pricing.wholesale_total).parameters) == ["items", "min_qty"]
print("[PASS] public API signatures unchanged")

# 3. Concrete behavioral scenarios, hand-computed expected values
# (fn, items, kwargs, expected, note)
cases = [
    (pricing.retail_total, [{"price": 10.0, "qty": 3}], {}, 33.0, "basic: 30*1.10"),
    (pricing.retail_total, [{"price": 10.0, "qty": 2.5}], {}, 27.5, "fractional qty: 25*1.10"),
    (pricing.retail_total, [], {}, 0.0, "empty items -> 0"),
    (pricing.retail_total, [{"price": -10.0, "qty": 3}], {}, -33.0, "negative price: -30*1.10"),
    (pricing.retail_total, [{"price": 1.005, "qty": 1}], {}, 1.11, "float-precision: 1.005*1.10=1.1055 -> round to 1.11"),

    (pricing.wholesale_total, [{"price": 10.0, "qty": 60}], {}, 528.0, "qty 60>=50 -> discount: 600*0.8*1.1"),
    (pricing.wholesale_total, [{"price": 10.0, "qty": 49}], {}, 539.0, "qty 49<50 -> no discount: 490*1.1"),
    (pricing.wholesale_total, [{"price": 10.0, "qty": 50}], {"min_qty": 50}, 440.0, "qty==min_qty -> discount applies: 500*0.8*1.1"),
    (pricing.wholesale_total, [{"price": 10.0, "qty": 50}], {"min_qty": 60}, 550.0, "qty 50<60 -> no discount: 500*1.1"),
    (pricing.wholesale_total, [{"price": 3.333, "qty": 7}], {}, 25.66, "23.331*1.1=25.6641 -> 25.66"),
]

all_ok = True
for fn, items, kwargs, expected, note in cases:
    got = fn(items, **kwargs)
    ok = abs(got - expected) < 1e-9
    all_ok = all_ok and ok
    print(f"{'OK ' if ok else 'BAD'} {fn.__name__} {items} {kwargs} -> {got!r} (expected {expected!r})  [{note}]")

print()
print("ALL INDEPENDENT CHECKS PASS:", all_ok)
sys.exit(0 if all_ok else 1)
