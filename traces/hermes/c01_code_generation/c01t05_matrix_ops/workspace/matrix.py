"""Matrix operations: rotation and spiral traversal.

This module provides pure functions that work on matrices represented as
``list[list[int]]`` (a list of rows, each a list of integers). Inputs are
never mutated; all functions return new containers.
"""


def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    """Return a new matrix rotated 90 degrees clockwise.

    Works for square and rectangular matrices, including 1x1. The input is
    not modified. For an ``m`` x ``n`` input the result is an ``n`` x ``m``
    matrix in which column ``j`` of the input becomes row ``j`` of the
    output.

    Args:
        matrix: The source matrix as a list of rows.

    Returns:
        A new rotated matrix.

    Examples:
        >>> rotate_90([[1, 2, 3], [4, 5, 6]])
        [[4, 1], [5, 2], [6, 3]]
    """
    if not matrix:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[rows - 1 - i][j] for i in range(rows)] for j in range(cols)]


def spiral_traverse(matrix: list[list[int]]) -> list[int]:
    """Return the elements of a matrix in clockwise spiral order.

    Starts at the top-left corner, proceeds right along the top row, then
    down the right column, left along the bottom row, and up the left
    column, peeling off the outer layer until all elements are visited.
    Works for square and rectangular matrices, including 1x1. The input is
    not modified.

    Args:
        matrix: The source matrix as a list of rows.

    Returns:
        The spiral-ordered list of elements.

    Examples:
        >>> spiral_traverse([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        [1, 2, 3, 6, 9, 8, 7, 4, 5]
    """
    if not matrix:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    result: list[int] = []
    while top <= bottom and left <= right:
        # Top edge: left to right.
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1
        # Right edge: top to bottom.
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1
        # Bottom edge: right to left (if a bottom row still remains).
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1
        # Left edge: bottom to top (if a left column still remains).
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1
    return result
