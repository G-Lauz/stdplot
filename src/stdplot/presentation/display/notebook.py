"""Inline display of figures in a Jupyter notebook."""

from __future__ import annotations

import dataclasses
import importlib
import io
import typing

from stdplot.application import Format, MissingDependencyError, write

if typing.TYPE_CHECKING:
    from matplotlib.figure import Figure

    from stdplot.application import Target


@dataclasses.dataclass(frozen=True)
class NotebookDisplayer:
    """Shows figures inline, in the output of the running cell.

    Attributes:
        target: Format, dpi, margins and optional size the figure is rendered with.
    """

    target: Target

    def show(self, figure: Figure, title: str) -> None:
        """Render the figure and display it below the cell.

        Args:
            figure: Figure to show.
            title: Unused, since an inline figure has no window to title.

        Raises:
            MissingDependencyError: IPython is not installed.
        """
        # Imported here rather than with stdplot, so a script never pays for IPython.
        try:
            display = importlib.import_module("IPython.display")
        except ImportError as error:
            raise MissingDependencyError("notebook") from error
        buffer = io.BytesIO()
        write(figure, self.target, buffer)
        data = buffer.getvalue()
        is_svg = self.target.format is Format.SVG
        image = (
            display.SVG(data=data)
            if is_svg
            else display.Image(data=data, format=self.target.format.value)
        )
        display.display(image)
