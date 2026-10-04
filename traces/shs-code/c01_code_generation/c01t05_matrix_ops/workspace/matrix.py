"""Matrix operations: rotation and spiral traversal.

Provides pure functional utilities that work on rectangular (M x N)
matrices represented as ``list[list[int]]``, including the 1x1 case.

Public API:
    - rotate_90(matrix)   -> new matrix rotated 90 degrees clockwise
    - spiral_traverse(matrix) -> elements in clockwise spiral order
"""


def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    """Return a NEW matrix rotated 90 degrees clockwise.

    The input matrix is not mutated. The original matrix dimensions
    M x N become N x M.

    For a matrix with M rows and N columns, element at (row r, col c)
    moves to (col c, row M - 1 - r).

    Args:
        matrix: A non-empty rectangular matrix (list of lists of int),
            where every inner list has the same length.

    Returns:
        A new matrix of dimensions N x M, rotated 90 degrees clockwise.

    Raises:
        ValueError: If the matrix is empty or has rows of uneven length.

    Examples:
        >>> rotate_90([[1, 2, 3],
        ...            [4, 5, 6],
        ...            [7, 8, 9]])
        [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
        >>> rotate_90([[1, 2, 3, 4],
        ...            [5, 6, 7, 8]])
        [[5, 1], [6, 2], [7, 3], [8, 4]]
        >>> rotate_90([[42]])
        [[42]]
    """
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be a non-empty 2D matrix")

    m = len(matrix)
    n = len(matrix[0])
    for row in matrix:
        if len(row) != n:
            raise ValueError("matrix rows must all have the same length")

    # New dimensions: N x M
    result = [
        [matrix[m - 1 - r][c] for r in range(m)]
        for c in range(n)
    ]
    return result


def spiral_traverse(matrix: list[list[int]]) -> list[int]:
    """Return matrix elements in clockwise spiral order, starting top-left.

    The input matrix is not mutated.

    Args:
        matrix: A non-empty rectangular matrix (list of lists of int),
            where every inner list has the same length.

    Returns:
        A flat list of all elements traversed in clockwise spiral order,
        starting from the top-left corner and moving right.

    Raises:
        ValueError: If the matrix is empty or has rows of uneven length.

    Examples:
        >>> spiral_traverse([[1, 2, 3],
        ...                  [4, 5, 6],
        ...                  [7, 8, 9]])
        [1, 2, 3, 6, 9, 8, 7, 4, 5]
        >>> spiral_traverse([[1, 2, 3, 4],
        ...                  [5, 6, 7, 8]])
        [1, 2, 3, 4, 8, 7, 6, 5]
        >>> spiral_traverse([[7]])
        [7]
    """
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be a non-empty 2D matrix")

    m = len(matrix)
    n = len(matrix[0])
    for row in matrix:
        if len(row) != n:
            raise ValueError("matrix rows must all have the same length")

    result: list[int] = []
    top, bottom = 0, m - 1
    left, right = 0, n - 1

    while top <= bottom and left <= right:
        # Traverse top row, left to right
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1

        # Traverse right column, top to bottom (if still valid)
        if left <= right:
            for r in range(top, bottom + 1):
                result.append(matrix[r][right])
            right -= 1

        # Traverse bottom row, right to left (if still valid)
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1

        # Traverse left column, bottom to top (if still valid)
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result
