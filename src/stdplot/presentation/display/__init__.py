from __future__ import annotations

import typing

from stdplot.application import Display

from .notebook import NotebookDisplayer
from .qt import QtDisplayer

if typing.TYPE_CHECKING:
    from stdplot.application import Displayer, Environment, Target


def select_displayer(display: Display, environment: Environment, preview: Target) -> Displayer:
    """Pick where a shown figure appears, resolving `Display.AUTO` from the environment.

    Args:
        display: The requested display.
        environment: What the running process can do.
        preview: Format and resolution an inline figure is rendered with.

    Returns:
        The notebook displayer when asked for or inside a Jupyter kernel, the Qt
        displayer otherwise.
    """
    is_auto_notebook = display is Display.AUTO and environment.in_notebook
    use_notebook = display is Display.NOTEBOOK or is_auto_notebook
    if use_notebook:
        return NotebookDisplayer(preview)
    return QtDisplayer()
