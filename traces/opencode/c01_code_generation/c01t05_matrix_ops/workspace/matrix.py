def rotate_90(matrix: list[list[int]]) -> list[list[int]]:
    """Return a new matrix rotated 90 degrees clockwise.

    The input matrix is not mutated. Handles square and rectangular
    matrices, including 1x1.
    """
    if not matrix or not matrix[0]:
        return []
    rows, cols = len(matrix), len(matrix[0])
    return [list(row) for row in zip(*matrix[::-1])]


def spiral_traverse(matrix: list[list[int]]) -> list[int]:
    """Return the elements of a matrix in clockwise spiral order.

    Traversal starts at the top-left corner and proceeds right, down,
    left, then up, peeling off one layer at a time. Handles square and
    rectangular matrices, including 1x1.
    """
    if not matrix or not matrix[0]:
        return []
    result: list[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    return result
