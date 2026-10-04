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

    def export_csv(self):
        rows = []
        for sku in sorted(self._items, key=lambda s: self._items[s]["name"]):
            item = self._items[sku]
            rows.append(f"{sku},{item['name']},{item['price']},{item['qty']}")
        return "sku,name,price,qty\n" + "\n".join(rows)
