"""Task runner: execute a collection of tasks with retries and backoff."""

import time


def run_tasks(tasks, retries=3, backoff_seconds=0.5):
    """Run a list of tasks, retrying each up to ``retries`` times.

    Each task is a dict with:
      - ``"id"``: a unique task identifier used as the result key.
      - ``"fn"``: a callable with no arguments to execute.

    Before every attempt the runner sleeps for ``backoff_seconds``.
    A task stops being retried as soon as an attempt raises an exception
    (loop breaks on failure); the outcome recorded for the task is whether
    the last executed attempt succeeded.

    Parameters:
        tasks (list[dict]): Task dicts as described above.
        retries (int): Maximum number of attempts per task (default 3).
        backoff_seconds (float): Seconds to sleep before each attempt
            (default 0.5).

    Returns:
        dict: Mapping of task id -> bool (True if the task's final attempt
        succeeded, False otherwise).
    """
    results = {}
    for task in tasks:
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
