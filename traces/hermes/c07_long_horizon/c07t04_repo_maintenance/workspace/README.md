# Shop

A small shop demo package with three features: cart management, pricing with
bulk discounts, and JSON backup of cart contents.

## Cart (`shop/cart.py`)

`Cart` holds items keyed by SKU.

- `add(sku, qty=1)` — add to the cart; repeated adds accumulate the quantity.
- `remove(sku)` — remove a SKU from the cart (no error if it is absent).
- `items()` — return a copy of the current `{sku: quantity}` mapping.

```python
from shop.cart import Cart

cart = Cart()
cart.add("apple", 2)
cart.remove("pear")   # safe even if "pear" was never added
cart.items()          # {"apple": 2}
```

## Pricing (`shop/pricing.py`)

`final_price(qty, unit_price, bulk_threshold, bulk_discount)` returns the
total price for an order.

- Normal order: `total = qty * unit_price`.
- Bulk rule: when `qty >= bulk_threshold`, a discount is applied and
  `total = qty * unit_price * bulk_discount`.

```python
from shop.pricing import final_price

final_price(5, 2.0, bulk_threshold=10, bulk_discount=0.9)   # 10.0 (no discount)
final_price(10, 1.0, bulk_threshold=10, bulk_discount=0.9)  # 9.0 (discount applied)
```

## Backup (`shop/backup.py`)

`backup_json(cart, path)` writes the cart's current items to `path` as JSON
with `indent=2`, and returns the dict that was written. The cart itself is
not modified.

```python
from shop.cart import Cart
from shop.backup import backup_json

cart = Cart()
cart.add("apple", 2)
backup_json(cart, "cart.json")   # cart.json now contains {"apple": 2}
```

## Tests

Run the whole suite with pytest:

```
python -m pytest -q
```

Tests live in `tests/`: `test_cart.py`, `test_pricing.py`, and
`test_backup.py`.
