"""Display of figures in a Qt window with the matplotlib toolbar."""

from __future__ import annotations

import importlib
import typing

from stdplot.application import MissingDependencyError

if typing.TYPE_CHECKING:
    from matplotlib.backends.backend_qt import FigureManagerQT
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure


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
        canvas_class, manager_class = _backends()
        previous_canvas = figure.canvas
        canvas = canvas_class(figure)
        try:
            manager = manager_class(canvas, 1)
            manager.set_window_title(title)
            manager.show()
            manager_class.start_main_loop()
        finally:
            # The Qt canvas is destroyed with its window; putting the previous canvas
            # back keeps the figure drawable and savable after the window is closed.
            figure.set_canvas(previous_canvas)


def _backends() -> tuple[type[FigureCanvasQTAgg], type[FigureManagerQT]]:
    """Import the Qt backends, only once a window is about to open.

    Importing a Qt binding loads the C++ runtime it bundles, and Windows keeps the first
    runtime loaded for the whole process. Importing it with stdplot would break any
    library imported later that needs a newer runtime, such as jax.

    Raises:
        MissingDependencyError: No Qt binding is installed.
    """
    try:
        backend_qt = importlib.import_module("matplotlib.backends.backend_qt")
        backend_qtagg = importlib.import_module("matplotlib.backends.backend_qtagg")
    except ImportError as error:
        raise MissingDependencyError("qt") from error
    return backend_qtagg.FigureCanvasQTAgg, backend_qt.FigureManagerQT
