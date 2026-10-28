from __future__ import annotations

import os
import subprocess
import sys

import pytest

from stdplot.application.environment import detect


def run_python(code: str, *, mplbackend: str | None = None) -> str:
    # A fresh interpreter: matplotlib never unsets a selected backend, and rc_context
    # does not restore it, so the backend cannot be changed back within this process.
    env = {key: value for key, value in os.environ.items() if key != "MPLBACKEND"}
    if mplbackend is not None:
        env["MPLBACKEND"] = mplbackend
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, env=env
    )
    return result.stdout.strip()


DETECT = "from stdplot.application.environment import detect; e = detect('pdflatex');"


def test_detect_outside_kernel_is_not_in_notebook() -> None:
    assert detect("pdflatex").in_notebook is False


def test_detect_missing_texsystem_has_no_latex() -> None:
    assert detect("not-a-tex-system").latex_available is False


def test_detect_without_ipython_imported_is_not_in_notebook() -> None:
    output = run_python(f"{DETECT} import sys; print('IPython' in sys.modules, e.in_notebook)")

    assert output == "False False"


@pytest.mark.parametrize("backend", ["agg", "svg"])
def test_detect_used_non_interactive_backend_is_headless(backend: str) -> None:
    output = run_python(
        f"import matplotlib; matplotlib.use({backend!r}); {DETECT} print(e.headless)"
    )

    assert output == "True"


def test_detect_mplbackend_agg_is_headless() -> None:
    assert run_python(f"{DETECT} print(e.headless)", mplbackend="Agg") == "True"


def test_detect_unselected_backend_is_not_headless() -> None:
    assert run_python(f"{DETECT} print(e.headless)") == "False"
