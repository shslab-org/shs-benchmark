"""LRU (Least Recently Used) cache with O(1) get/put.

Implements a classic LRU cache over a doubly-linked list kept in
lock-step with a hash map. The list keeps keys in recency order
(most recently used at the head), while the map goes straight to a
node for any key, giving O(1) average lookup for both operations.

Example:
    >>> cache = LRUCache(2)
    >>> cache.put(1, "a")
    >>> cache.put(2, "b")
    >>> cache.get(1)
    'a'
    >>> cache.put(3, "c")
    >>> cache.get(2)
    -1
"""

from __future__ import annotations

from typing import Any, Hashable


class _Node:
    """A node in the doubly-linked list backing the cache.

    Attributes:
        key:    The cached key.
        value:  The cached value.
        prev:   Previous node (None if first).
        next:   Next node (None if last).
    """

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: Hashable, value: Any) -> None:
        self.key: Hashable = key
        self.value: Any = value
        self.prev: "_Node | None" = None
        self.next: "_Node | None" = None


class LRUCache:
    """Least Recently Used (LRU) cache.

    Both :meth:`get` and :meth:`put` run in O(1) average time.

    Semantics:
        * ``get(key)`` returns the cached value, or ``-1`` if the key
          is absent. A successful ``get`` counts as a *use*, moving
          the key to the most-recently-used end.
        * ``put(key, value)`` inserts or updates a value. If the
          cache is at capacity and the key is new, the least
          recently used entry is evicted. Updating an existing key
          also refreshes its recency.

    Args:
        capacity: Maximum number of entries; must be >= 1.

    Raises:
        ValueError: If ``capacity`` is less than 1.
    """

    def __init__(self, capacity: int) -> None:
        """Initialize an empty LRU cache with the given capacity.

        Args:
            capacity: Maximum number of entries; must be >= 1.

        Raises:
            ValueError: If ``capacity`` is less than 1.
        """
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        self._capacity: int = capacity
        self._nodes: dict[Hashable, _Node] = {}
        # Sentinel head/tail nodes avoid boundary checks on insertion
        # and removal. The head side is the most-recently-used end.
        self._head = _Node(None, None)
        self._tail = _Node(None, None)
        self._head.next = self._tail
        self._tail.prev = self._head

    # ------------------------------------------------------------------
    # Internal list helpers
    # ------------------------------------------------------------------

    def _link_between(self, node: _Node, prev: _Node, nxt: _Node) -> None:
        """Splice ``node`` between ``prev`` and ``nxt`` in the list."""
        node.prev = prev
        node.next = nxt
        prev.next = node
        nxt.prev = node

    def _unlink(self, node: _Node) -> None:
        """Remove ``node`` from the list, linking its neighbours."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None

    def _move_to_head(self, node: _Node) -> None:
        """Move ``node`` to the most-recently-used position (head)."""
        self._unlink(node)
        self._link_between(node, self._head, self._head.next)

    def _push_head(self, node: _Node) -> None:
        """Insert ``node`` at the head (most recently used)."""
        self._link_between(node, self._head, self._head.next)

    def _pop_tail(self) -> _Node:
        """Remove and return the least-recently-used node (tail)."""
        node = self._tail.prev
        self._unlink(node)
        return node

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: Hashable) -> Any:
        """Return the value cached for ``key``, or -1 if not present.

        A hit counts as a use: the entry is moved to the head of the
        recency list.

        Args:
            key: The key to look up.

        Returns:
            The cached value, or ``-1`` when the key is absent.
        """
        node = self._nodes.get(key)
        if node is None:
            return -1
        self._move_to_head(node)
        return node.value

    def put(self, key: Hashable, value: Any) -> None:
        """Insert or update the value for ``key``.

        If ``key`` is already present its value and recency are
        updated in place. Otherwise, if the cache is full, the
        least recently used entry is evicted first.

        Args:
            key:   The key to store.
            value: The value to cache under ``key``.
        """
        node = self._nodes.get(key)
        if node is not None:
            node.value = value
            self._move_to_head(node)
            return
        if len(self._nodes) >= self._capacity:
            evicted = self._pop_tail()
            del self._nodes[evicted.key]
        new_node = _Node(key, value)
        self._nodes[key] = new_node
        self._push_head(new_node)

    def __len__(self) -> int:
        """Return the number of entries currently cached."""
        return len(self._nodes)

    def __contains__(self, key: Hashable) -> bool:
        """Return True if ``key`` is present (without affecting recency)."""
        return key in self._nodes
