# Plugin-Style Calculator

A minimal **core** (`calculator.py`) plus independent **plugins**
(`plugins/`), wired together in `main.py`.

## Layout

    calculator.py          # core: Calculator (register / calculate / operations)
    main.py                # wires core + all plugins, demonstrates 2+2, 10-4, 3*3, 9/2
    plugins/
        add.py             # registers "add"
        subtract.py        # registers "subtract"
        multiply.py        # registers "multiply"
        divide.py          # registers "divide" (raises ZeroDivisionError on /0)
    tests/test_calculator.py
    conftest.py            # puts the project root on sys.path for pytest

## How it works

- `Calculator.register(name, fn)` stores a callable under a name.
- `Calculator.calculate(name, *args)` looks the name up (unknown names
  raise `KeyError`) and applies it.
- `Calculator.operations()` lists registered names.
- Every plugin is a plain module with a single entry point,
  `register(calc)`, that calls `calc.register(...)`. Plugins depend on
  the core, never on each other.

## Run it

    python3 main.py
    python3 -m pytest tests/ -v

## How to add a new plugin (3 steps)

1. **Create a module** in `plugins/`, e.g. `power.py`, defining the
   operation and its `register` entry point:

       def power(a, b):
           """Return ``a ** b``."""
           return a ** b

       def register(calc):
           calc.register("power", power)

2. **Add tests** for it in `tests/test_calculator.py`, following the
   pattern of the existing plugin tests (registration + behaviour).

3. **Wire it in `main.py`**: import it and call its `register` on the
   calculator instance, e.g. add it to the tuple in `build_calculator()`:

       from plugins import power
       ...
       for plugin in (add, subtract, multiply, divide, power):
           plugin.register(calc)

That's it — the core needs no changes; any code holding a `Calculator`
can use the new operation immediately.
