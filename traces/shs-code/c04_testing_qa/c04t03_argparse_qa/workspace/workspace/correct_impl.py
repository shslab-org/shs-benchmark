"""Correct reference implementation of argparsemini SPEC — used to verify
the test suite passes against a spec-compliant module."""


def parse(argv, spec):
    opts = {k: v.get("default") for k, v in spec.items()}
    positional = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--":
            positional.extend(argv[i + 1:])
            break
        if tok.startswith("--") and not tok[2:].startswith("-"):
            body = tok[2:]
            if "=" in body:
                name, value = body.split("=", 1)
            else:
                name, value = body, None
            if name in spec:
                if spec[name].get("type") == "value":
                    if value is None:
                        i += 1
                        value = argv[i] if i < len(argv) else None
                    opts[name] = value
                else:
                    opts[name] = True
            else:
                raise SystemExit(2)
        else:
            positional.append(tok)
        i += 1
    return opts, positional
