"""PostToolUse hook: format and lint a Python file Claude just edited.

Reads the hook event from stdin, formats the edited file with `ruff format`, applies
`ruff check --fix`, and reports anything left over. Violations that ruff cannot fix
automatically are written to stderr with exit code 2, which returns them to Claude so
the next edit corrects them rather than leaving the finding for CI.

No-ops on anything that is not a `.py` file. Ruff is run through the interpreter
executing this hook (the project venv), because the venv's `Scripts` directory is not
on PATH unless the venv is activated. A missing ruff is a non-blocking error rather
than a silent pass, so a broken setup is visible instead of looking like clean code.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_BLOCK = 2
MAX_REPORTED_LINES = 30


def edited_path(event: dict[str, object]) -> pathlib.Path | None:
    """Extract the edited file path from a PostToolUse event.

    Args:
        event: Parsed hook event payload.

    Returns:
        The path, or `None` if the event carries no file path or the file is not
        Python.
    """
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None

    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(raw, str) or not raw:
        return None

    path = pathlib.Path(raw)
    return path if path.suffix == ".py" and path.exists() else None


def run_ruff(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke ruff from the current interpreter's environment and capture its output.

    Args:
        *args: Arguments to pass.

    Returns:
        The completed process.
    """
    return subprocess.run(
        [sys.executable, "-m", "ruff", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    """Format the edited file and surface any unfixable violations.

    Returns:
        0 when the file is clean or out of scope, 1 when ruff is not installed, 2 when
        violations remain.
    """
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return EXIT_OK

    path = edited_path(event)
    if path is None:
        return EXIT_OK

    has_ruff = importlib.util.find_spec("ruff") is not None
    if not has_ruff:
        print(
            f"ruff is not installed for {sys.executable}; the edit was not formatted. "
            "Run `pip install -r requirements.txt` in the project venv.",
            file=sys.stderr,
        )
        return EXIT_ERROR

    run_ruff("format", str(path))

    # `check --fix` exits non-zero only when violations remain after fixing, so one
    # call both fixes and reports.
    remaining = run_ruff("check", "--fix", str(path))
    if remaining.returncode == 0:
        return EXIT_OK

    # stderr carries ruff's own failures, such as an invalid ruff.toml.
    output = f"{remaining.stdout}\n{remaining.stderr}"
    lines = output.strip().splitlines()[:MAX_REPORTED_LINES]
    print(
        f"ruff reports violations in {path} that it cannot fix automatically.",
        file=sys.stderr,
    )
    print("\n".join(lines), file=sys.stderr)
    return EXIT_BLOCK


if __name__ == "__main__":
    sys.exit(main())
