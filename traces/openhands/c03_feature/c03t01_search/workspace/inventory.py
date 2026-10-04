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

    def search(self, keyword: str) -> list:
        kw = keyword.lower()
        matches = [i for i in self._items.values() if kw in i["name"].lower()]
        return sorted(matches, key=lambda i: i["name"])
