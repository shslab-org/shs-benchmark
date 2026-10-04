"""Least Recently Used (LRU) cache with O(1) get/put.

Implements the classic LRU eviction policy: when the cache is full and a
new key is inserted, the least recently used entry is evicted. Both reads
(`get`) and writes (`put`) count as "use" and refresh recency.
"""

from collections import OrderedDict
from typing import Any, Hashable


class LRUCache:
    """Fixed-capacity LRU cache.

    Backed by ``collections.OrderedDict`` which provides O(1) average-time
    lookup, move-to-end, and pop-first operations. The oldest key (least
    recently used) is always at the front; the most recently used key is
    at the end.

    Attributes:
        capacity: Maximum number of entries the cache may hold (>= 1).
    """

    def __init__(self, capacity: int) -> None:
        """Initialize the cache with the given capacity.

        Args:
            capacity: Maximum number of entries. Must be >= 1.

        Raises:
            ValueError: If capacity < 1.
        """
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        self.capacity: int = capacity
        self._items: "OrderedDict[Hashable, Any]" = OrderedDict()

    def get(self, key: Hashable) -> Any:
        """Return the value for *key*, or -1 if absent.

        A successful lookup marks the key as most recently used.

        Args:
            key: The key to look up.

        Returns:
            The cached value, or -1 if the key is not present.
        """
        if key not in self._items:
            return -1
        # Move to end to mark as most recently used.
        self._items.move_to_end(key)
        return self._items[key]

    def put(self, key: Hashable, value: Any) -> None:
        """Insert or update *key* to *value*, evicting LRU if at capacity.

        If *key* already exists its value is updated and recency refreshed.
        Otherwise the new entry is appended and, if the cache is full, the
        least recently used entry is evicted.

        Args:
            key: The key to insert or update.
            value: The value to associate with *key*.
        """
        if key in self._items:
            self._items[key] = value
            self._items.move_to_end(key)
        else:
            if len(self._items) >= self.capacity:
                # Evict the least recently used (front of the OrderedDict).
                self._items.popitem(last=False)
            self._items[key] = value
