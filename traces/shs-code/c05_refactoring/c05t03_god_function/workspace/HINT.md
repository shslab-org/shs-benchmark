Refactor task: split process_orders into at least 3 focused
helper functions (e.g. parse_line / parse_all, compute_line_total, aggregate).
Public behavior must remain EXACTLY identical (same dict, same rounding).
process_orders must remain the public entry point.