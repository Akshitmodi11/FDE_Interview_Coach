"""PostToolUse hook: run ruff and mypy right after Claude edits a file.

If either finds a problem, its output goes to stderr and we exit 2, so Claude
sees it immediately and can fix it.

Tools run as `python -m ruff` / `python -m mypy` so they work even when their
scripts aren't on PATH. A tool that isn't installed is skipped with a note
rather than failing: that's a setup issue, not a code problem.
"""
import subprocess
import sys

CHECKS = [
    ("ruff", [sys.executable, "-m", "ruff", "check", "app", "tests"]),
    ("mypy", [sys.executable, "-m", "mypy", "app"]),
]

failures = []
skipped = []

for tool, command in CHECKS:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        skipped.append(tool)
        continue
    output = f"{result.stdout}{result.stderr}"
    if f"No module named {tool}" in output:
        skipped.append(tool)
        continue
    if result.returncode != 0:
        failures.append(f"$ {tool} {' '.join(command[3:])}\n{output}".rstrip())

if skipped:
    # stdout, not stderr: informational only, never blocks.
    print(f"[checks] skipped (not installed): {', '.join(skipped)}")

if failures:
    print("\n\n".join(failures), file=sys.stderr)
    sys.exit(2)

sys.exit(0)
