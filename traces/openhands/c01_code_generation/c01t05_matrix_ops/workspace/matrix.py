"""Matrix operations: 90-degree rotation and spiral traversal."""


def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    """Return a new matrix rotated 90 degrees clockwise.

    For a matrix with R rows and C columns, the result has C rows and
    R columns. The element at position (i, j) in the result equals
    matrix[R - 1 - j][i] from the input.

    The input matrix is not mutated; a new nested list is returned.
    Works for square and rectangular matrices, as well as 1x1 matrices.

    Example:
        >>> rotate_90([[1, 2, 3], [4, 5, 6]])
        [[4, 1], [5, 2], [6, 3]]
    """
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    return [[matrix[rows - 1 - j][i] for j in range(rows)] for i in range(cols)]


def spiral_traverse(matrix: list[list[int]]) -> list[int]:
    """Return the elements of a matrix in clockwise spiral order.

    Traversal starts at the top-left corner, proceeds along the top
    edge, then the right edge, the bottom edge, and the left edge,
    peeling one layer at a time until all elements are visited.

    Works for square and rectangular matrices, as well as 1x1 matrices.

    Example:
        >>> spiral_traverse([[1, 2, 3], [4, 5, 6]])
        [1, 2, 3, 6, 5, 4]
    """
    if not matrix or not matrix[0]:
        return []

    result: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # Traverse the top edge left to right.
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1

        # Traverse the right edge top to bottom.
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1

        # Traverse the bottom edge right to left, if a row remains.
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1

        # Traverse the left edge bottom to top, if a column remains.
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1

    return result
