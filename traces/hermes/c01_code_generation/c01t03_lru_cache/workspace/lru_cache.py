"""LRU (Least Recently Used) cache with O(1) average get/put.

Built on collections.OrderedDict:
  - The dict gives O(1) key lookup (hash map).
  - Insertion order is preserved, so the least-recently-used entry is
    always the first key and the most-recently-used entry is the last.
  - move_to_end(key) re-marks an entry as most recently used in O(1).

Semantics:
  - ``get(key)`` returns the value and marks the key most recently used;
    returns ``-1`` for an absent key.
  - ``put(key, value)`` inserts or updates the value and marks the key
    most recently used. If the key is new and the cache is at capacity,
    the least recently used entry is evicted.
"""

from collections import OrderedDict


class LRUCache:
    """Fixed-capacity LRU cache.

    Attributes:
        capacity: Maximum number of entries (>= 1).

    Example:
        >>> cache = LRUCache(2)
        >>> cache.put("a", 1)
        >>> cache.put("b", 2)
        >>> cache.get("a")          # 'a' becomes most recently used
        1
        >>> cache.put("c", 3)       # evicts 'b' (least recently used)
        >>> cache.get("b")
        -1
        >>> cache.get("c")
        3
    """

    def __init__(self, capacity: int) -> None:
        """Create a cache that holds at most ``capacity`` entries.

        Args:
            capacity: Maximum number of entries; must be >= 1.

        Raises:
            ValueError: If ``capacity`` < 1.
        """
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._store: "OrderedDict[object, object]" = OrderedDict()

    def get(self, key):
        """Return the value for ``key`` (-1 if absent), marking it used.

        Both lookup and recency update are O(1) average time.
        """
        if key not in self._store:
            return -1
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key, value) -> None:
        """Insert or update ``key`` -> ``value``, marking it most recently used.

        Updating an existing key refreshes its recency. If the key is new
        and the cache is full, the least recently used entry is evicted.
        O(1) average time.
        """
        if key in self._store:
            self._store[key] = value
            self._store.move_to_end(key)
            return
        if len(self._store) >= self.capacity:
            self._store.popitem(last=False)  # evict least recently used
        self._store[key] = value
