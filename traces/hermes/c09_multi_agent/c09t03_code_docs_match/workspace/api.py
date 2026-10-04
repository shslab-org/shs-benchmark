"""In-memory task API.

A small module-level task store using standard library only.
"""

# Module-level storage: task id -> task dict
_tasks: dict = {}
_next_id: int = 1


def create_task(title: str) -> dict:
    """Create a new task and store it in _tasks.

    Returns a new dict {"id": int, "title": title, "done": False}
    with the next sequential integer id.
    """
    global _next_id
    task = {"id": _next_id, "title": title, "done": False}
    _tasks[_next_id] = task
    _next_id += 1
    return task


def list_tasks() -> list[dict]:
    """Return a list of all stored task dicts, in id order."""
    return [_tasks[tid] for tid in sorted(_tasks)]


def complete_task(task_id: int) -> dict:
    """Mark the task with the given id as done and return it.

    Raises ValueError if the task does not exist.
    """
    if task_id not in _tasks:
        raise ValueError(f"Task {task_id} not found")
    task = _tasks[task_id]
    task["done"] = True
    return task


def delete_task(task_id: int) -> None:
    """Remove the task with the given id from _tasks.

    Raises ValueError if the task does not exist.
    """
    if task_id not in _tasks:
        raise ValueError(f"Task {task_id} not found")
    del _tasks[task_id]
