"""Task runner: executes task actions with retries and a fixed backoff.

A task is a dict with an "id" key and an "action" key holding a
zero-argument callable. run_tasks() gives each task up to `retries`
attempts, sleeping `backoff_seconds` before every attempt, and stops
retrying a task as soon as its action succeeds.
"""

import time


def run_tasks(tasks, retries=3, backoff_seconds=0.5):
    """Run each task's action, retrying with backoff until it succeeds.

    Args:
        tasks: Iterable of task dicts. Each task needs an "id" (used as the
            key in the result) and an "action" (a zero-argument callable).
        retries: Maximum number of attempts per task (default: 3).
        backoff_seconds: Seconds to sleep before every attempt, including
            the first (default: 0.5).

    Returns:
        Dict mapping each task id to True if the action succeeded on any
        attempt, False if all attempts raised an exception.
    """
    results = {}
    for task in tasks:
        succeeded = False
        for _ in range(retries):
            time.sleep(backoff_seconds)
            try:
                task["action"]()
                succeeded = True
                break
            except Exception:
                succeeded = False
        results[task["id"]] = succeeded
    return results
