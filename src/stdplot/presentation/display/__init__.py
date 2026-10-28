from __future__ import annotations

import typing

from stdplot.application import Display

from .notebook import NotebookDisplayer
from .null import NullDisplayer
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
        The requested displayer. For `Display.AUTO`: the notebook displayer inside a
        Jupyter kernel, the null displayer when the matplotlib backend cannot open
        windows (`matplotlib.use("Agg")` or `MPLBACKEND=Agg`), the Qt displayer
        otherwise.
    """
    if display is Display.NONE:
        return NullDisplayer()
    if display is Display.NOTEBOOK:
        return NotebookDisplayer(preview)
    if display is Display.QT:
        return QtDisplayer()
    if environment.in_notebook:
        return NotebookDisplayer(preview)
    if environment.headless:
        return NullDisplayer()
    return QtDisplayer()
