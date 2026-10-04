"""LRU (Least Recently Used) Cache implementation.

Provides an O(1) average-time cache that evicts the least recently used
entry when capacity is exceeded. Implemented with a doubly linked list
for ordering plus a hash map for O(1) lookup, wrapped in an explicit
sentinel-node design so both ends are handled uniformly.
"""


class _Node:
    """Node of the doubly linked list holding a key/value pair."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """Fixed-capacity LRU cache.

    Both ``get`` and ``put`` run in O(1) average time. The most recently
    used entry is kept at the tail of the internal linked list; when the
    cache exceeds its capacity, the least recently used entry (head side)
    is evicted.
    """

    def __init__(self, capacity: int):
        """Initialize the cache.

        Args:
            capacity: Maximum number of entries the cache can hold.
                Must be >= 1.

        Raises:
            ValueError: If capacity < 1.
        """
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._size = 0
        self._map = {}
        # Sentinel head/tail nodes simplify edge cases.
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    def get(self, key):
        """Return the value for ``key`` or ``-1`` if absent.

        A successful lookup counts as a use and marks the entry as most
        recently used.
        """
        node = self._map.get(key)
        if node is None:
            return -1
        self._move_to_tail(node)
        return node.value

    def put(self, key, value) -> None:
        """Insert or update ``key`` with ``value``.

        If the key already exists, its value and recency are updated.
        Otherwise the entry is added; if capacity is exceeded, the least
        recently used entry is evicted.
        """
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._move_to_tail(node)
            return
        # Evict if over capacity.
        if self._size == self.capacity:
            lru = self._head.next
            self._unlink(lru)
            del self._map[lru.key]
            self._size -= 1
        new_node = _Node(key, value)
        self._link_at_tail(new_node)
        self._map[key] = new_node
        self._size += 1

    # --- internal helpers ---------------------------------------------------

    def _unlink(self, node: _Node) -> None:
        """Remove ``node`` from the linked list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _link_at_tail(self, node: _Node) -> None:
        """Insert ``node`` right before the tail sentinel."""
        last = self._tail.prev
        last.next = node
        node.prev = last
        node.next = self._tail
        self._tail.prev = node

    def _move_to_tail(self, node: _Node) -> None:
        """Relink an existing node to the tail (most recent position)."""
        if node.next is self._tail:
            return  # already most recent
        self._unlink(node)
        self._link_at_tail(node)
