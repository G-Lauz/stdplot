from __future__ import annotations

import typing

import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import stdplot

if typing.TYPE_CHECKING:
    import pathlib

# Without usetex, drawing never calls a TeX binary, whatever the machine has.
NO_TEX = stdplot.Config(style=stdplot.Style(latex=stdplot.LatexSettings(usetex=False)))


def test_figure_1x1_yields_axes() -> None:
    with stdplot.figure("single", config=NO_TEX, show=False) as (fig, ax):
        typing.assert_type(ax, Axes)

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)


def test_figure_grid_yields_axes_grid() -> None:
    with stdplot.figure("grid", nrows=2, ncols=2, config=NO_TEX, show=False) as (_, axes):
        typing.assert_type(axes, stdplot.AxesGrid)

        assert axes.shape == (2, 2)


def test_figure_ncols_only_yields_one_row_grid() -> None:
    with stdplot.figure("row", ncols=3, config=NO_TEX, show=False) as (_, axes):
        typing.assert_type(axes, stdplot.AxesGrid)

        assert axes.shape == (1, 3)


def test_figure_explicit_1x1_yields_axes_grid() -> None:
    with stdplot.figure("grid", nrows=1, config=NO_TEX, show=False) as (_, axes):
        assert isinstance(axes, stdplot.AxesGrid)


def test_figure_save_without_output_dir_raises() -> None:
    with pytest.raises(stdplot.MissingOutputError, match="output_dir"):
        stdplot.figure("unsaved", save=True)


def test_figure_save_writes_every_target(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    with stdplot.figure("saved", config=svg_png_config, save=True, show=False) as (_, ax):
        ax.plot([1, 2, 3])

    assert sorted(path.name for path in tmp_path.iterdir()) == ["saved.png", "saved.svg"]


def test_plot_decorator_defaults_name_to_function_name(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    @stdplot.plot(config=svg_png_config, save=True, show=False)
    def loss_curve(fig: Figure, ax: Axes) -> None:
        ax.plot([3, 2, 1])

    loss_curve()

    assert (tmp_path / "loss_curve.svg").is_file()


def test_plot_decorator_uses_given_name(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    @stdplot.plot("custom", config=svg_png_config, save=True, show=False)
    def loss_curve(fig: Figure, ax: Axes) -> None:
        ax.plot([3, 2, 1])

    loss_curve()

    assert (tmp_path / "custom.svg").is_file()


def test_plot_decorator_forwards_arguments() -> None:
    @stdplot.plot(config=NO_TEX, show=False)
    def draw(fig: Figure, ax: Axes, first: int, *, second: str) -> tuple[int, str]:
        return first, second

    assert draw(1, second="two") == (1, "two")


def test_plot_decorator_passes_through_return_value() -> None:
    @stdplot.plot(config=NO_TEX, show=False)
    def draw(fig: Figure, ax: Axes) -> Axes:
        return ax

    assert isinstance(draw(), Axes)


def test_plot_decorator_grid_receives_axes_grid() -> None:
    @stdplot.plot(nrows=2, config=NO_TEX, show=False)
    def draw(fig: Figure, axes: stdplot.AxesGrid) -> tuple[int, int]:
        return axes.shape

    assert draw() == (2, 1)


def test_plot_decorator_keeps_function_name() -> None:
    @stdplot.plot(config=NO_TEX, show=False)
    def draw(fig: Figure, ax: Axes) -> None:
        pass

    assert draw.__name__ == "draw"


def test_plot_decorator_save_without_output_dir_raises() -> None:
    def draw(fig: Figure, ax: Axes) -> None:
        pass

    with pytest.raises(stdplot.MissingOutputError, match="output_dir"):
        stdplot.plot(save=True)(draw)
