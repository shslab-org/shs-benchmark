"""Tiny inventory package. Extend it per task instructions."""

import csv
import io


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
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["sku", "name", "price", "qty"])
        for item in self.list_items():
            sku = next(k for k, v in self._items.items() if v is item)
            writer.writerow([sku, item["name"], item["price"], item["qty"]])
        return out.getvalue()
