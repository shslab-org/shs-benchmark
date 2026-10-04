"""Minimal CLI parser — reference fixed version."""


def parse(argv, spec):
    opts = {k: v.get("default") for k, v in spec.items()}
    positional = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--":
            positional.extend(argv[i + 1:])
            break
        if tok.startswith("--"):
            body = tok[2:]
            if "=" in body:
                name, _, val = body.partition("=")
                if name not in spec:
                    raise SystemExit(2)
                opts[name] = val
            elif body in spec:
                if spec[body].get("type") == "value":
                    i += 1
                    if i >= len(argv):
                        raise SystemExit(2)
                    opts[body] = argv[i]
                else:
                    opts[body] = True
            else:
                raise SystemExit(2)
        else:
            positional.append(tok)
        i += 1
    return opts, positional
