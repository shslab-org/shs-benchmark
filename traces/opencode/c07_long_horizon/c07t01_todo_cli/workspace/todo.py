import json
import os
import sys

HELP = """usage: python todo.py <command> [args]

Commands:
  add <text>     Add a new TODO item
  list           List all TODO items
  done <number>  Mark item at 1-based position <number> as done
  rm <number>    Remove item at 1-based position <number>

The TODO list persists in a JSON file. Its path comes from the TODO_FILE
environment variable (default: ./todos.json).
"""


def error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def load():
    path = os.environ.get("TODO_FILE", "./todos.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        error(f"error: cannot read {path}: {e}")
    if not isinstance(data, list):
        error(f"error: {path} is not a valid TODO list")
    return data


def save(items):
    path = os.environ.get("TODO_FILE", "./todos.json")
    with open(path, "w") as f:
        json.dump(items, f, indent=2)
        f.write("\n")


def resolve(items, num_arg, verb):
    try:
        num = int(num_arg)
    except ValueError:
        error(f"error: {verb} requires a number, got {num_arg!r}")
    if num < 1 or num > len(items):
        error(f"error: {verb} number {num} is out of range (list has {len(items)} items)")
    return num - 1


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(HELP)
        return
    cmd = args[0]
    if cmd == "add":
        if len(args) < 2:
            error("error: add requires text, e.g. 'add buy milk'")
        items = load()
        items.append({"text": " ".join(args[1:]), "done": False})
        save(items)
        print(f"added: {' '.join(args[1:])}")
    elif cmd == "list":
        items = load()
        if not items:
            print("no items")
        for i, item in enumerate(items, 1):
            box = "x" if item.get("done") else " "
            print(f"{i}. [{box}] {item['text']}")
    elif cmd == "done":
        if len(args) < 2:
            error("error: done requires a number, e.g. 'done 1'")
        items = load()
        idx = resolve(items, args[1], "done")
        items[idx]["done"] = True
        save(items)
        print(f"marked done: {items[idx]['text']}")
    elif cmd == "rm":
        if len(args) < 2:
            error("error: rm requires a number, e.g. 'rm 1'")
        items = load()
        idx = resolve(items, args[1], "rm")
        removed = items.pop(idx)
        save(items)
        print(f"removed: {removed['text']}")
    else:
        error(f"error: unknown command {cmd!r}, try --help")


if __name__ == "__main__":
    main()
