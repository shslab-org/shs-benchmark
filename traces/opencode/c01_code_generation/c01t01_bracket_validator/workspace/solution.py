def is_balanced(s: str) -> bool:
    """Check whether all bracket characters in s are balanced.

    Handles (), [], and {} in LIFO order. Non-bracket characters
    are ignored. An empty string is balanced.
    """
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in pairs.values():
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
