"""Binary search module. BUG: returns wrong index / loops forever on some inputs."""


def binary_search(arr, target):
    """Return index of target in sorted arr, or -1 if absent."""
    lo, hi = 0, len(arr) - 1
    while lo < hi:            # BUG: should be lo <= hi
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1      # BUG: with lo<hi this skips the last candidate
    return -1                 # BUG: never checks arr[lo] when lo==hi
