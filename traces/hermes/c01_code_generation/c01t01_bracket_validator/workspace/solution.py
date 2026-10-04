def is_balanced(s: str) -> bool:
    """Return True if the string's brackets are balanced.

    Three bracket types are recognized: (), [], and {}. Every opening
    bracket must be closed by the matching type in LIFO (stack) order.
    Non-bracket characters are ignored, and an empty string is balanced.
    """
    stack = []
    openers = {"(", "[", "{"}
    closers = {")": "(", "]": "[", "}": "{"}

    for ch in s:
        if ch in openers:
            stack.append(ch)
        elif ch in closers:
            if not stack or stack[-1] != closers[ch]:
                return False
            stack.pop()
    return not stack
