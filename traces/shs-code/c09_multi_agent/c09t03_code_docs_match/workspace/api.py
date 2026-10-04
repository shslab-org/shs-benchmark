"""In-memory task API.

Provides a small task store kept entirely in module-level memory, with
four public functions: ``create_task``, ``list_tasks``,
``complete_task`` and ``delete_task``.
"""

# Module-level storage: task id -> task dict.
_tasks: dict[int, dict] = {}
_next_id: int = 1


def create_task(title: str) -> dict:
    """Create a new task.

    Args:
        title: The title of the new task.

    Returns:
        The created task dict: ``{"id": int, "title": str, "done": False}``.
    """
    global _next_id
    task = {"id": _next_id, "title": title, "done": False}
    _tasks[_next_id] = task
    _next_id += 1
    return task


def list_tasks() -> list[dict]:
    """List all tasks currently stored.

    Returns:
        A list of all task dicts, in creation order.
    """
    return list(_tasks.values())


def complete_task(task_id: int) -> dict:
    """Mark the task with ``task_id`` as done.

    Args:
        task_id: The id of the task to complete.

    Returns:
        The updated task dict (with ``done`` set to ``True``).

    Raises:
        ValueError: If no task exists with the given ``task_id``.
    """
    if task_id not in _tasks:
        raise ValueError(f"Unknown task id: {task_id}")
    _tasks[task_id]["done"] = True
    return _tasks[task_id]


def delete_task(task_id: int) -> None:
    """Delete the task with ``task_id``.

    Args:
        task_id: The id of the task to delete.

    Returns:
        None.

    Raises:
        ValueError: If no task exists with the given ``task_id``.
    """
    if task_id not in _tasks:
        raise ValueError(f"Unknown task id: {task_id}")
    del _tasks[task_id]
