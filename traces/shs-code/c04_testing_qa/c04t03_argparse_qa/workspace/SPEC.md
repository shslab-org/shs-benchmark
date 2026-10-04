SPEC for argparsemini.parse(argv, spec):

- spec maps option name (without --) to {'type': 'flag'|'value', 'default': x}
- '--verbose' (flag type) sets True; absent -> default
- '--name value' and '--name=value' BOTH set value options
- unknown flags must raise SystemExit(2) — they are errors, NOT positionals
- non-option tokens are collected, in order, as positionals
- '--' terminates option parsing; everything after is positional

Your job: write tests_agent/test_argparsemini.py that fails against any module
violating this spec and passes against a correct one. The shipped module
violates it. Do NOT modify argparsemini.py.