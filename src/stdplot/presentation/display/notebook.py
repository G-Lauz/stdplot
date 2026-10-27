"""Inline display of figures in a Jupyter notebook."""

from __future__ import annotations

import dataclasses
import io
import typing

from stdplot.application import Format, MissingDependencyError

if typing.TYPE_CHECKING:
    from matplotlib.figure import Figure

    from stdplot.application import Target

try:
    import IPython.display
except ImportError:  # stdplot[notebook] is not installed
    IPython = None


@dataclasses.dataclass(frozen=True)
class NotebookDisplayer:
    """Shows figures inline, in the output of the running cell.

    Attributes:
        target: Format and resolution the figure is rendered with.
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
        if IPython is None:
            raise MissingDependencyError("notebook")
        buffer = io.BytesIO()
        figure.savefig(buffer, format=self.target.format.value, dpi=self.target.dpi)
        data = buffer.getvalue()
        is_svg = self.target.format is Format.SVG
        image = (
            IPython.display.SVG(data=data)
            if is_svg
            else IPython.display.Image(data=data, format=self.target.format.value)
        )
        IPython.display.display(image)
