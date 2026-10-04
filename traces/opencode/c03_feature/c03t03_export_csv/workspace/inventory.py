"""Tiny inventory package. Extend it per task instructions."""


class Inventory:
    def __init__(self):
        self._items = {}   # sku -> dict(name, price, qty)

    def add_item(self, sku, name, price, qty):
        if sku in self._items:
            self._items[sku]["qty"] += qty
        else:
            self._items[sku] = {"name": name, "price": price, "qty": qty}
        return self._items[sku]

    def get_item(self, sku):
        return self._items.get(sku)

    def list_items(self):
        return sorted(self._items.values(), key=lambda i: i["name"])

    def export_csv(self) -> str:
        lines = ["sku,name,price,qty"]
        for sku, info in sorted(
            self._items.items(), key=lambda pair: pair[1]["name"]
        ):
            lines.append(f"{sku},{info['name']},{info['price']},{info['qty']}")
        return "\n".join(lines)
