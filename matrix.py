def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    """Return a new matrix rotated 90 degrees clockwise.

    The input matrix is not mutated. Works for square, rectangular, and 1x1
    matrices. The result has dimensions cols x rows of the original.
    """
    rows = len(matrix)
    if rows == 0:
        return []
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows - 1, -1, -1)] for c in range(cols)]


def spiral_traverse(matrix: list[list[int]]) -> list[int]:
    """Return the elements of the matrix in clockwise spiral order.

    Traversal starts at the top-left element and proceeds right along the
    top row, down the right column, left along the bottom row, and up the
    left column, peeling off layers until all elements are visited.
    Works for square, rectangular, and 1x1 matrices.
    """
    result: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1 if matrix else -1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1
    return result
