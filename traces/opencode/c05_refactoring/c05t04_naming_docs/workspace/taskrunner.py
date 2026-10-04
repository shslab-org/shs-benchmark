"""Task runner with per-task retries and backoff."""

import time


def run_tasks(tasks, retries=3, backoff_seconds=0.5):
    """Run each task's action up to `retries` times, stopping on first failure.

    Each attempt sleeps for `backoff_seconds` before invoking the task.

    Args:
        tasks: Iterable of dicts, each with an "id" key and a "fn" callable.
        retries: Maximum number of attempts per task.
        backoff_seconds: Seconds to sleep before each attempt.

    Returns:
        dict mapping each task id to True if every attempted call succeeded,
        False if any attempt raised an exception.
    """
    results = {}
    for task in tasks:
        succeeded = False
        for _ in range(retries):
            time.sleep(backoff_seconds)
            try:
                task["fn"]()
                succeeded = True
            except Exception:
                succeeded = False
            if not succeeded:
                break
        results[task["id"]] = succeeded
    return results
