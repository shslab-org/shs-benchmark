"""In-memory task API."""

_tasks: dict[int, dict] = {}
_next_id = 1


def create_task(title: str) -> dict:
    """Create a new task and return it.

    Example:
        >>> task = create_task("Buy milk")
        >>> {"id": task["id"], "title": "Buy milk", "done": False}
    """
    global _next_id
    task = {"id": _next_id, "title": title, "done": False}
    _tasks[_next_id] = task
    _next_id += 1
    return task


def list_tasks() -> list[dict]:
    """Return all tasks in creation order.

    Example:
        >>> [t["title"] for t in list_tasks()]
        ['Buy milk', 'Walk dog']
    """
    return [_tasks[k] for k in sorted(_tasks)]


def complete_task(task_id: int) -> dict:
    """Mark a task as done and return the updated task.

    Raises ValueError if task_id is unknown.

    Example:
        >>> complete_task(1)["done"]
        True
    """
    if task_id not in _tasks:
        raise ValueError(f"unknown task id: {task_id}")
    _tasks[task_id]["done"] = True
    return _tasks[task_id]


def delete_task(task_id: int) -> None:
    """Delete a task.

    Raises ValueError if task_id is unknown.

    Example:
        >>> delete_task(1)
    """
    if task_id not in _tasks:
        raise ValueError(f"unknown task id: {task_id}")
    del _tasks[task_id]
