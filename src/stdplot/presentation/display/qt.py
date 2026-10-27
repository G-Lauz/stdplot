"""Display of figures in a Qt window with the matplotlib toolbar."""

from __future__ import annotations

import typing

from stdplot.application import MissingDependencyError

if typing.TYPE_CHECKING:
    from matplotlib.figure import Figure

try:
    from matplotlib.backends import backend_qt, backend_qtagg
except ImportError:  # no Qt binding is installed: stdplot[qt] is missing
    backend_qt = None
    backend_qtagg = None


class QtDisplayer:
    """Shows figures in a Qt window, blocking until the window is closed."""

    def show(self, figure: Figure, title: str) -> None:
        """Open a window on the figure and run the Qt event loop until it closes.

        Args:
            figure: Figure to show.
            title: Title of the window.

        Raises:
            MissingDependencyError: No Qt binding is installed.
        """
        if backend_qt is None or backend_qtagg is None:
            raise MissingDependencyError("qt")
        previous_canvas = figure.canvas
        canvas = backend_qtagg.FigureCanvasQTAgg(figure)
        try:
            manager = backend_qt.FigureManagerQT(canvas, 1)
            manager.set_window_title(title)
            manager.show()
            backend_qt.FigureManagerQT.start_main_loop()
        finally:
            # The Qt canvas is destroyed with its window; putting the previous canvas
            # back keeps the figure drawable and savable after the window is closed.
            figure.set_canvas(previous_canvas)
