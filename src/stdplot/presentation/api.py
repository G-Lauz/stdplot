"""The public drawing API: the `figure` context manager and the `plot` decorator.

Without `nrows` and `ncols`, the drawing code receives the figure's single `Axes`.
With either of them it receives an `AxesGrid`, even for a 1x1 grid, so the type of the
axes follows from the call alone.
"""

from __future__ import annotations

import contextlib
import functools
import typing

from stdplot.application import Config, PlotRequest, detect, session

from .display import select_displayer

if typing.TYPE_CHECKING:
    import collections.abc

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from stdplot.application import AxesGrid

P = typing.ParamSpec("P")
R = typing.TypeVar("R")

DEFAULT_CONFIG = Config()


@typing.overload
def figure(
    name: str,
    *,
    nrows: None = None,
    ncols: None = None,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> contextlib.AbstractContextManager[tuple[Figure, Axes]]: ...
@typing.overload
def figure(
    name: str,
    *,
    nrows: int,
    ncols: int | None = None,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> contextlib.AbstractContextManager[tuple[Figure, AxesGrid]]: ...
@typing.overload
def figure(
    name: str,
    *,
    nrows: None = None,
    ncols: int,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> contextlib.AbstractContextManager[tuple[Figure, AxesGrid]]: ...
def figure(
    name: str,
    *,
    nrows: int | None = None,
    ncols: int | None = None,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> contextlib.AbstractContextManager[tuple[Figure, Axes | AxesGrid]]:
    """Open a styled figure, then export and show it when the block exits.

    Args:
        name: Name of the figure, used as the file stem and the window title.
        nrows: Number of rows of axes; set it or `ncols` to receive an `AxesGrid`.
        ncols: Number of columns of axes; set it or `nrows` to receive an `AxesGrid`.
        config: Style, targets, preview and display of the figure.
        save: Write the figure to every target of the config on exit.
        show: Display the figure on exit.

    Returns:
        A context manager yielding the figure and its axes.

    Raises:
        ValueError: The name is empty or the grid has fewer than one row or column.
        MissingOutputError: Saving without an output directory or without targets.
    """
    request = _request(name, nrows, ncols, config, save=save, show=show)
    return _draw(request, single=nrows is None and ncols is None)


@typing.overload
def plot(
    name: str | None = None,
    *,
    nrows: None = None,
    ncols: None = None,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> collections.abc.Callable[
    [collections.abc.Callable[typing.Concatenate[Figure, Axes, P], R]],
    collections.abc.Callable[P, R],
]: ...
@typing.overload
def plot(
    name: str | None = None,
    *,
    nrows: int,
    ncols: int | None = None,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> collections.abc.Callable[
    [collections.abc.Callable[typing.Concatenate[Figure, AxesGrid, P], R]],
    collections.abc.Callable[P, R],
]: ...
@typing.overload
def plot(
    name: str | None = None,
    *,
    nrows: None = None,
    ncols: int,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> collections.abc.Callable[
    [collections.abc.Callable[typing.Concatenate[Figure, AxesGrid, P], R]],
    collections.abc.Callable[P, R],
]: ...
def plot(
    name: str | None = None,
    *,
    nrows: int | None = None,
    ncols: int | None = None,
    config: Config = DEFAULT_CONFIG,
    save: bool = False,
    show: bool = True,
) -> collections.abc.Callable[
    [collections.abc.Callable[typing.Concatenate[Figure, Axes | AxesGrid, P], R]],
    collections.abc.Callable[P, R],
]:
    """Make a drawing function open, export and show its own figure on every call.

    The function receives the figure and its axes ahead of its own arguments. Calling
    the decorated function draws the figure and returns what the function returns.

    Args:
        name: Name of the figure; defaults to the name of the function.
        nrows: Number of rows of axes; set it or `ncols` to receive an `AxesGrid`.
        ncols: Number of columns of axes; set it or `nrows` to receive an `AxesGrid`.
        config: Style, targets, preview and display of the figure.
        save: Write the figure to every target of the config after each call.
        show: Display the figure after each call.

    Returns:
        The decorator. It raises `ValueError` or `MissingOutputError` when applied, for
        the same reasons as `figure`.
    """
    single = nrows is None and ncols is None

    def decorator(
        func: collections.abc.Callable[typing.Concatenate[Figure, Axes | AxesGrid, P], R],
    ) -> collections.abc.Callable[P, R]:
        figure_name = func.__name__ if name is None else name
        request = _request(figure_name, nrows, ncols, config, save=save, show=show)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with _draw(request, single=single) as (fig, axes):
                return func(fig, axes, *args, **kwargs)

        return wrapper

    return decorator


def _request(
    name: str,
    nrows: int | None,
    ncols: int | None,
    config: Config,
    *,
    save: bool,
    show: bool,
) -> PlotRequest:
    return PlotRequest(
        config=config,
        name=name,
        nrows=1 if nrows is None else nrows,
        ncols=1 if ncols is None else ncols,
        save=save,
        show=show,
    )


@contextlib.contextmanager
def _draw(
    request: PlotRequest, *, single: bool
) -> collections.abc.Iterator[tuple[Figure, Axes | AxesGrid]]:
    environment = detect()
    displayer = select_displayer(request.config.display, environment, request.config.preview)
    with session(request, displayer, environment) as (fig, grid):
        yield (fig, grid.single) if single else (fig, grid)
