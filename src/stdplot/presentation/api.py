"""The public drawing API: a `Plotter` session, with its `figure` and `plot` methods.

A `Plotter` binds a `Config` to the save and show defaults of every figure drawn with
it, so a notebook or a script turns saving on in one place. `stdplot.figure` and
`stdplot.plot` are the methods of a default `Plotter`: default config, not saved, shown.

Without `nrows` and `ncols`, the drawing code receives the figure's single `Axes`.
With either of them it receives an `AxesGrid`, even for a 1x1 grid, so the type of the
axes follows from the call alone. An axes of another projection, such as
`subplot_kw={"projection": "3d"}`, is still typed `Axes`: the caller casts it, as in
`typing.cast("Axes3D", ax)`, to reach the methods of that projection.
"""

from __future__ import annotations

import contextlib
import dataclasses
import functools
import typing

from stdplot.application import Config, PlotRequest, Size, detect, session

from .display import select_displayer

if typing.TYPE_CHECKING:
    import collections.abc

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from stdplot.application import AxesGrid, SubplotOptions

P = typing.ParamSpec("P")
R = typing.TypeVar("R")


@dataclasses.dataclass(frozen=True)
class Plotter:
    """A drawing session: one config, plus whether its figures are saved and shown.

    The arguments of a `figure` or `plot` call override the session's defaults for
    that call only.

    Attributes:
        config: Style, size, targets, preview and display of every figure.
        save: Write each figure to every target of the config, by default.
        show: Display each figure, by default.
    """

    config: Config = dataclasses.field(default_factory=Config)
    save: bool = False
    show: bool = True

    @typing.overload
    def figure(
        self,
        name: str,
        *,
        nrows: None = None,
        ncols: None = None,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> contextlib.AbstractContextManager[tuple[Figure, Axes]]: ...
    @typing.overload
    def figure(
        self,
        name: str,
        *,
        nrows: int,
        ncols: int | None = None,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> contextlib.AbstractContextManager[tuple[Figure, AxesGrid]]: ...
    @typing.overload
    def figure(
        self,
        name: str,
        *,
        nrows: None = None,
        ncols: int,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> contextlib.AbstractContextManager[tuple[Figure, AxesGrid]]: ...
    def figure(
        self,
        name: str,
        *,
        nrows: int | None = None,
        ncols: int | None = None,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> contextlib.AbstractContextManager[tuple[Figure, Axes | AxesGrid]]:
        """Open a styled figure, then export and show it when the block exits.

        Args:
            name: Name of the figure, used as the file stem and the window title.
            nrows: Number of rows of axes; set it or `ncols` to receive an `AxesGrid`.
            ncols: Number of columns of axes; set it or `nrows` to receive an `AxesGrid`.
            size: Size the figure is drawn at, in inches; defaults to the config's size.
            save: Write the figure to every target of the config on exit; defaults to
                the session's `save`.
            show: Display the figure on exit; defaults to the session's `show`.
            **subplots_kw: Options of the grid of axes, forwarded to
                `Figure.subplots`: `sharex`, `sharey`, `width_ratios`, `height_ratios`,
                `subplot_kw` and `gridspec_kw`.

        Returns:
            A context manager yielding the figure and its axes.

        Raises:
            ValueError: The name is empty, the grid has fewer than one row or column,
                or the size is not positive.
            MissingOutputError: Saving without an output directory or without targets.
        """
        request = self._request(
            name,
            nrows=nrows,
            ncols=ncols,
            size=size,
            save=save,
            show=show,
            subplots_kw=subplots_kw,
        )
        return _draw(request, single=nrows is None and ncols is None)

    @typing.overload
    def plot(
        self,
        name: str | None = None,
        *,
        nrows: None = None,
        ncols: None = None,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> collections.abc.Callable[
        [collections.abc.Callable[typing.Concatenate[Figure, Axes, P], R]],
        collections.abc.Callable[P, R],
    ]: ...
    @typing.overload
    def plot(
        self,
        name: str | None = None,
        *,
        nrows: int,
        ncols: int | None = None,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> collections.abc.Callable[
        [collections.abc.Callable[typing.Concatenate[Figure, AxesGrid, P], R]],
        collections.abc.Callable[P, R],
    ]: ...
    @typing.overload
    def plot(
        self,
        name: str | None = None,
        *,
        nrows: None = None,
        ncols: int,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
    ) -> collections.abc.Callable[
        [collections.abc.Callable[typing.Concatenate[Figure, AxesGrid, P], R]],
        collections.abc.Callable[P, R],
    ]: ...
    def plot(
        self,
        name: str | None = None,
        *,
        nrows: int | None = None,
        ncols: int | None = None,
        size: Size | tuple[float, float] | None = None,
        save: bool | None = None,
        show: bool | None = None,
        **subplots_kw: typing.Unpack[SubplotOptions],
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
            size: Size the figure is drawn at, in inches; defaults to the config's size.
            save: Write the figure to every target of the config after each call;
                defaults to the session's `save`.
            show: Display the figure after each call; defaults to the session's `show`.
            **subplots_kw: Options of the grid of axes, forwarded to `Figure.subplots`,
                as in `figure`.

        Returns:
            The decorator. It raises `ValueError` or `MissingOutputError` when applied, for
            the same reasons as `figure`.
        """
        single = nrows is None and ncols is None

        def decorator(
            func: collections.abc.Callable[typing.Concatenate[Figure, Axes | AxesGrid, P], R],
        ) -> collections.abc.Callable[P, R]:
            figure_name = func.__name__ if name is None else name
            request = self._request(
                figure_name,
                nrows=nrows,
                ncols=ncols,
                size=size,
                save=save,
                show=show,
                subplots_kw=subplots_kw,
            )

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with _draw(request, single=single) as (fig, axes):
                    return func(fig, axes, *args, **kwargs)

            return wrapper

        return decorator

    def _request(
        self,
        name: str,
        *,
        nrows: int | None,
        ncols: int | None,
        size: Size | tuple[float, float] | None,
        save: bool | None,
        show: bool | None,
        subplots_kw: SubplotOptions,
    ) -> PlotRequest:
        return PlotRequest(
            config=self.config,
            name=name,
            nrows=1 if nrows is None else nrows,
            ncols=1 if ncols is None else ncols,
            save=self.save if save is None else save,
            show=self.show if show is None else show,
            size=_resolve_size(size, self.config.size),
            subplots_kw=subplots_kw,
        )


def _resolve_size(size: Size | tuple[float, float] | None, default: Size) -> Size:
    if size is None:
        return default
    if isinstance(size, Size):
        return size
    return Size(*size)


@contextlib.contextmanager
def _draw(
    request: PlotRequest, *, single: bool
) -> collections.abc.Iterator[tuple[Figure, Axes | AxesGrid]]:
    environment = detect(request.config.style.latex.texsystem)
    displayer = select_displayer(request.config.display, environment, request.config.preview)
    with session(request, displayer, environment) as (fig, grid):
        yield (fig, grid.single) if single else (fig, grid)


_DEFAULT_PLOTTER = Plotter()
# Bound methods keep the overloads, so the typed signatures are written only once.
figure = _DEFAULT_PLOTTER.figure
plot = _DEFAULT_PLOTTER.plot
