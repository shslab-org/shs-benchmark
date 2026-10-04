from typing import Any

_tasks: list[dict[str, Any]] = []
_next_id: int = 1


def create_task(title: str) -> dict:
    global _next_id
    task = {"id": _next_id, "title": title, "done": False}
    _next_id += 1
    _tasks.append(task)
    return task


def list_tasks() -> list[dict]:
    return list(_tasks)


def complete_task(task_id: int) -> dict:
    for task in _tasks:
        if task["id"] == task_id:
            task["done"] = True
            return task
    raise ValueError(f"No task with id {task_id}")


def delete_task(task_id: int) -> None:
    for i, task in enumerate(_tasks):
        if task["id"] == task_id:
            del _tasks[i]
            return
    raise ValueError(f"No task with id {task_id}")
