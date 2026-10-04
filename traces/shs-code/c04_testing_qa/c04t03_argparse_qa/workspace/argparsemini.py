"""Minimal CLI parser — CONTAINS SEEDED BUGS for the QA benchmark."""


def parse(argv, spec):
    """argv: list of tokens. spec: {flag: {'type': 'flag'|'value', 'default': x}}
    Returns (options_dict, positionals_list).
    BUGS: treats unknown flags as positionals, misses '--flag=value' syntax,
    and 'flag' options overwrite instead of collecting last one only is ok —
    but attached values break."""
    opts = {k: v.get("default") for k, v in spec.items()}
    positional = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("--"):
            name = tok[2:]
            if name in spec:
                if spec[name].get("type") == "value":
                    i += 1
                    opts[name] = argv[i] if i < len(argv) else None   # BUG 1: attached '--name=val' unsupported
                else:
                    opts[name] = True
            else:
                positional.append(tok)     # BUG 2: unknown flag silently becomes positional
        else:
            positional.append(tok)
        i += 1
    return opts, positional                # BUG 3: negative numbers / '-' lost? acceptable; seeded bug is above
