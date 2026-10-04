"""Bracket validator.

Checks whether a string has balanced brackets ((), [], {}), ignoring
all non-bracket characters. Matching must follow LIFO (last-in-first-out)
order, i.e. standard nesting.
"""

from typing import Deque
from collections import deque


def is_balanced(s: str) -> bool:
    """Return True if all brackets in *s* are properly balanced, else False.

    Rules:
      - Three bracket types are recognized: () [] {}
      - Every opening bracket must be closed by the same type in LIFO order
      - Non-bracket characters are ignored
      - An empty string (or one with no brackets) is considered balanced

    Implementation uses an explicit stack (no recursion).
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    closers = set(pairs.keys())

    stack: Deque[str] = deque()  # used as a LIFO stack (append/pop on end)

    for ch in s:
        if ch in closers:
            # Closing bracket: must match the most recent unmatched opener
            if not stack or stack.pop() != pairs[ch]:
                return False
        elif ch in ("(", "[", "{"):
            stack.append(ch)
        # all other characters are ignored

    return not stack


if __name__ == "__main__":
    cases = [
        ("", True),
        ("abc", True),
        ("()", True),
        ("(())", True),
        ("()[ ]{} ", True),
        ("a(b[c{d}e]f)g", True),
        ("([{}])", True),
        ("(]", False),
        ("([)]", False),
        ("(((", False),
        (")", False),
        ("({[", False),
        ("}]", False),
        ("{[(])}", False),
        ("code{with[brackets]}", True),
        ("no brackets here at all!", True),
    ]
    for s, expected in cases:
        result = is_balanced(s)
        status = "OK" if result == expected else "FAIL"
        print(f"{status}  is_balanced({s!r}) = {result}  (expected {expected})")
        assert result == expected, f"Mismatch for {s!r}"

    print("\nAll tests passed.")
