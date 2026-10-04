"""Shared verification helpers for shs-benchmark verify scripts."""
import ast, json, os, shutil, subprocess, sys, tempfile, textwrap

PASS = "pass"
FAIL = "fail"


def make_result(task, agent, checks):
    total = sum(c.get("points", 0) for c in checks if c["ok"])
    max_total = sum(c.get("points", 0) for c in checks)
    passed = total == max_total and max_total > 0
    return {
        "task": task,
        "agent": agent,
        "points": total,
        "max_points": max_total,
        "passed": passed,
        "checks": checks,
    }


def write_and_run_pytest(workspace, test_code, test_name="test_hidden.py", extra_files=None, cwd=None):
    """Materialize hidden test code and run pytest against workspace.

    Returns (returncode, stdout_tail).
    """
    tmp = tempfile.mkdtemp(prefix="benchverify_")
    try:
        test_path = os.path.join(tmp, test_name)
        with open(test_path, "w") as f:
            f.write(textwrap.dedent(test_code))
        for name, code in (extra_files or {}).items():
            p = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(textwrap.dedent(code))
        env = dict(os.environ)
        env["PYTHONPATH"] = workspace + os.pathsep + tmp + os.pathsep + env.get("PYTHONPATH", "")
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-x", "-q", test_path, "--tb=short", "-p", "no:cacheprovider"],
            cwd=cwd or workspace, capture_output=True, text=True, timeout=120, env=env,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out[-2000:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_cmd(cmd, cwd, timeout=60, env_extra=None):
    """Run a command, return (rc, combined_output_tail)."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, ((r.stdout or "") + (r.stderr or ""))[-2500:]
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except Exception as e:
        return 1, f"LAUNCH_ERROR: {e}"


def find_file(workspace, name, skip_dirs=(".git", "node_modules", "__pycache__", ".venv")):
    for dirpath, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        if name in filenames:
            return os.path.join(dirpath, name)
    return None


def parse_ast_file(path):
    with open(path) as f:
        return ast.parse(f.read())


def module_functions(tree):
    return {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def module_classes(tree):
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


def has_bare_except(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.ExceptHandler) and n.type is None:
            return True
    return False


def py_files(workspace, skip_dirs=(".git", "node_modules", "__pycache__", ".venv", "tests_agent")):
    out = []
    for dirpath, dirnames, filenames in os.walk(workspace):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            if fn.endswith(".py"):
                out.append(os.path.join(dirpath, fn))
    return out
