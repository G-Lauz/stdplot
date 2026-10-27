"""The drawing session: style a figure, hand it to the caller, then export and show it."""

from __future__ import annotations

import contextlib
import typing
import warnings

import matplotlib.style
from matplotlib.figure import Figure

from stdplot.domain.errors import LatexNotFoundError, UnknownStyleError

from .axes import AxesGrid
from .exporter import export

if typing.TYPE_CHECKING:
    import collections.abc

    from stdplot.domain.config import PlotRequest
    from stdplot.domain.style import Style

    from .environment import Environment


class Displayer(typing.Protocol):
    """Shows a finished figure to the user."""

    def show(self, figure: Figure, title: str) -> None:
        """Show the figure.

        Args:
            figure: Figure to show.
            title: Title of the figure, such as its name.
        """


def resolve_style(request: PlotRequest, environment: Environment) -> Style:
    """Pick the style to draw with, falling back to mathtext when LaTeX is missing.

    Args:
        request: The figure to draw.
        environment: What the running process can do.

    Returns:
        The configured style, or a copy without LaTeX when it is not installed.

    Raises:
        LatexNotFoundError: A target needs LaTeX and it is not installed.
    """
    style = request.config.style
    if environment.latex_available:
        return style
    if request.needs_latex:
        raise LatexNotFoundError
    if not style.latex.usetex:
        return style
    warnings.warn(
        "LaTeX is not installed; rendering text with matplotlib's mathtext instead.",
        stacklevel=2,
    )
    return style.without_latex()


def check_styles(style: Style) -> None:
    """Check that matplotlib knows every style name.

    Args:
        style: The style to check.

    Raises:
        UnknownStyleError: Some names are not registered with matplotlib.
    """
    unknown = tuple(name for name in style.names if name not in matplotlib.style.available)
    has_unknown = bool(unknown)
    if has_unknown:
        raise UnknownStyleError(unknown)


@contextlib.contextmanager
def session(
    request: PlotRequest, displayer: Displayer, environment: Environment
) -> collections.abc.Iterator[tuple[Figure, AxesGrid]]:
    """Draw one figure under the configured style, then export and show it.

    The style wraps the caller's drawing, not only the export, because matplotlib reads
    fonts and LaTeX settings when each artist is created. An error raised while drawing
    skips both the export and the display.

    Args:
        request: The figure to draw.
        displayer: Shows the figure once drawn, when the request asks for it.
        environment: What the running process can do.

    Yields:
        The figure, sized to the preview target, and its grid of axes.

    Raises:
        LatexNotFoundError: A target needs LaTeX and it is not installed.
        UnknownStyleError: Some style names are not registered with matplotlib.
    """
    style = resolve_style(request, environment)
    check_styles(style)
    config = request.config
    with matplotlib.style.context(style.to_rc_list()):
        # The ieee style raises figure.dpi to 600; the preview dpi keeps windows usable.
        figure = Figure(figsize=config.preview.size.as_tuple(), dpi=config.preview.dpi)
        figure.set_layout_engine(config.layout.value)
        grid = AxesGrid.from_figure(figure, request.nrows, request.ncols)
        yield figure, grid
        if request.save:
            export(figure, config.targets, request.output_dir, request.name)
        if request.show:
            displayer.show(figure, request.name)
