"""Correct reference implementation of argparsemini per SPEC.md."""
import sys

def parse(argv, spec):
    opts = {k: v.get("default") for k, v in spec.items()}
    positional = []
    i = 0
    no_options = False
    while i < len(argv):
        tok = argv[i]
        if no_options or not tok.startswith("--") or tok == "--":
            if tok == "--":
                no_options = True
            else:
                positional.append(tok)
            i += 1
            continue
        if "=" in tok:
            name, _, val = tok.partition("=")
            name = name[2:]
            if name not in spec:
                print(f"error: unknown option {tok}", file=sys.stderr)
                sys.exit(2)
            if spec[name].get("type") != "value":
                print(f"error: option {name} does not take a value", file=sys.stderr)
                sys.exit(2)
            opts[name] = val
            i += 1
            continue
        name = tok[2:]
        if name not in spec:
            print(f"error: unknown option {tok}", file=sys.stderr)
            sys.exit(2)
        if spec[name].get("type") == "value":
            i += 1
            opts[name] = argv[i] if i < len(argv) else None
        else:
            opts[name] = True
        i += 1
    return opts, positional
