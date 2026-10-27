"""Detection of what the running process can do."""

from __future__ import annotations

import dataclasses
import shutil

try:
    import IPython
except ImportError:  # stdplot[notebook] is not installed, so no kernel can be running
    IPython = None


@dataclasses.dataclass(frozen=True)
class Environment:
    """Capabilities of the running process that change how figures are drawn and shown.

    Attributes:
        latex_available: A `latex` binary is on the PATH.
        in_notebook: The process is a Jupyter kernel, so figures can be shown inline.
    """

    latex_available: bool
    in_notebook: bool


def detect() -> Environment:
    """Inspect the running process.

    Returns:
        The detected environment.
    """
    return Environment(
        latex_available=shutil.which("latex") is not None,
        in_notebook=_in_notebook(),
    )


def _in_notebook() -> bool:
    if IPython is None:
        return False
    shell = IPython.get_ipython()
    # A terminal IPython also has a shell, but only a kernel renders inline images.
    return shell is not None and "IPKernelApp" in shell.config
