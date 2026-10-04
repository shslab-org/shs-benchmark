"""A small map-reduce style transformation pipeline."""


class Transform:
    def __init__(self, name: str, fn, enabled: bool = True):
        self.name = name
        self.fn = fn
        self.enabled = enabled

    def apply(self, value):
        if not self.enabled:
            return value
        return self.fn(value)


def run_pipeline(value, transforms, collect_errors: bool = False):
    errors = []
    for t in transforms:
        try:
            value = t.apply(value)
        except Exception:
            if not t.enabled:
                continue
            if collect_errors:
                errors.append(t.name)
            continue
    if collect_errors:
        return value, errors
    return value


# ---- independent example transforms ----

def _upper(s: str) -> str:
    return s.upper()


def _strip(s: str) -> str:
    return s.strip()


def _reverse(s: str) -> str:
    return s[::-1]


def _word_count_wrap(s: str) -> str:
    return str(len(s.split()))


UPPER = Transform("upper", _upper)
STRIP = Transform("strip", _strip)
REVERSE = Transform("reverse", _reverse)
WORD_COUNT_WRAP = Transform("word_count_wrap", _word_count_wrap)


if __name__ == "__main__":
    text = "  hello benchmark  "
    print(f"initial: {text!r}")
    step1 = UPPER.apply(text)
    print(f"after upper: {step1!r}")
    step2 = STRIP.apply(step1)
    print(f"after strip: {step2!r}")
    step3 = REVERSE.apply(step2)
    print(f"after reverse: {step3!r}")
    step4 = WORD_COUNT_WRAP.apply(step3)
    print(f"after word_count_wrap: {step4!r}")

    transforms = [UPPER, STRIP, REVERSE, WORD_COUNT_WRAP]
    result, errs = run_pipeline(text, transforms, collect_errors=True)
    print(f"pipeline result: {result!r}, errors: {errs}")

    failing = Transform("failing", lambda v: 1 / 0)
    mixed = [UPPER, failing, STRIP]
    result, errs = run_pipeline(text, mixed, collect_errors=True)
    print(f"skipped failing: result={result!r}, errors={errs}")
    plain = run_pipeline(text, mixed)
    print(f"skipped failing (no collect): {plain!r}")
