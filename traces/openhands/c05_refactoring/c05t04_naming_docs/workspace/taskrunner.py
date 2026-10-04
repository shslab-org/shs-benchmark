"""Task runner: execute each task's action with retries and backoff."""

import time


def run_tasks(tasks, retries=3, backoff_seconds=0.5):
    """Run each task's action, retrying on failure.

    Parameters:
        tasks: iterable of dicts, each with an "id" key and a callable
            under "fn".
        retries: maximum number of attempts per task (default 3).
        backoff_seconds: sleep duration before each attempt.

    Returns:
        dict mapping each task id to True if its action succeeded
        (attempts stop on first success) or False after exhausting
        retries.
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
            if succeeded:
                break
        results[task["id"]] = succeeded
    return results
