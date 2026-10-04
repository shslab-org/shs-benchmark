"""Bracket validator.

Checks whether all brackets in a string are properly balanced.
"""


def is_balanced(s: str) -> bool:
    """Return True if all brackets in `s` are balanced, False otherwise.

    Only () [] {} are considered; other characters are ignored.
    """
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    openers = set(pairs.values())
    for ch in s:
        if ch in openers:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack
