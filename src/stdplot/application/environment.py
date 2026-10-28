"""Detection of what the running process can do."""

from __future__ import annotations

import dataclasses
import shutil
import sys

import matplotlib
import matplotlib.backends.registry


@dataclasses.dataclass(frozen=True)
class Environment:
    """Capabilities of the running process that change how figures are drawn and shown.

    Attributes:
        latex_available: The configured TeX system is on the PATH.
        in_notebook: The process is a Jupyter kernel, so figures can be shown inline.
        headless: The selected matplotlib backend cannot open windows.
    """

    latex_available: bool
    in_notebook: bool
    headless: bool


def detect(texsystem: str) -> Environment:
    """Inspect the running process.

    Args:
        texsystem: The TeX binary PGF export runs, such as "pdflatex".

    Returns:
        The detected environment.
    """
    return Environment(
        latex_available=shutil.which(texsystem) is not None,
        in_notebook=_in_notebook(),
        headless=_headless(),
    )


def _in_notebook() -> bool:
    # A kernel imports IPython before running any user code, so an IPython that is not
    # imported yet means no kernel; importing it here would only slow the import down.
    ipython = sys.modules.get("IPython")
    if ipython is None:
        return False
    shell = ipython.get_ipython()
    # A terminal IPython also has a shell, but only a kernel renders inline images.
    return shell is not None and "IPKernelApp" in shell.config


def _headless() -> bool:
    # auto_select=False reads the backend without resolving it, so it never imports a
    # GUI toolkit; None means no backend was selected, by matplotlib.use or MPLBACKEND.
    backend = matplotlib.get_backend(auto_select=False)
    if backend is None:
        return False
    registry = matplotlib.backends.registry
    non_interactive = registry.backend_registry.list_builtin(registry.BackendFilter.NON_INTERACTIVE)
    return backend.lower() in non_interactive
