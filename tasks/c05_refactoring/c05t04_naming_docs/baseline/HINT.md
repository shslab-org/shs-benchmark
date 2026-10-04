Refactor task: rename every cryptic identifier to descriptive names
(e.g. go -> run_tasks, l -> tasks, n -> retries, w -> backoff_seconds, r ->
results, x -> task, fn -> action, ok -> succeeded), and add a short docstring
to every function explaining parameters and return value. Public behavior
must remain identical: run_tasks(tasks, retries=3, backoff_seconds=0.5)
executes each task's action up to `retries` times (sleeping
backoff_seconds before each attempt), records True/False per task id, and
stops retrying a task on first success.