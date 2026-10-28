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
PLOTS = stdplot.Plotter(NO_TEX, show=False)


def test_figure_1x1_yields_axes() -> None:
    with PLOTS.figure("single") as (fig, ax):
        typing.assert_type(ax, Axes)

        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)


def test_figure_grid_yields_axes_grid() -> None:
    with PLOTS.figure("grid", nrows=2, ncols=2) as (_, axes):
        typing.assert_type(axes, stdplot.AxesGrid)

        assert axes.shape == (2, 2)


def test_figure_ncols_only_yields_one_row_grid() -> None:
    with PLOTS.figure("row", ncols=3) as (_, axes):
        typing.assert_type(axes, stdplot.AxesGrid)

        assert axes.shape == (1, 3)


def test_figure_explicit_1x1_yields_axes_grid() -> None:
    with PLOTS.figure("grid", nrows=1) as (_, axes):
        assert isinstance(axes, stdplot.AxesGrid)


def test_figure_size_tuple_sets_figure_size() -> None:
    with PLOTS.figure("sized", size=(6, 4)) as (fig, _):
        assert tuple(fig.get_size_inches()) == (6.0, 4.0)


def test_figure_without_size_uses_config_size() -> None:
    plotter = stdplot.Plotter(stdplot.Config(style=NO_TEX.style, size=stdplot.Size(5, 2)))

    with plotter.figure("sized", show=False) as (fig, _):
        assert tuple(fig.get_size_inches()) == (5.0, 2.0)


def test_figure_size_writes_sizeless_target_at_it(tmp_path: pathlib.Path) -> None:
    target = stdplot.Target(stdplot.Format.SVG, dpi=72, bbox=stdplot.Bbox.STANDARD)
    config = stdplot.Config(style=NO_TEX.style, targets=(target,), output_dir=tmp_path)

    with stdplot.Plotter(config, save=True, show=False).figure("sized", size=(6, 4)):
        pass

    # SVG sizes are in points: 6 x 4 in is 432 x 288 pt.
    assert 'width="432pt" height="288pt"' in (tmp_path / "sized.svg").read_text()


def test_figure_forwards_sharex() -> None:
    with PLOTS.figure("shared", nrows=2, sharex=True) as (_, axes):
        assert axes[0].get_shared_x_axes().joined(axes[0], axes[1])


def test_figure_default_plotter_needs_no_config() -> None:
    with stdplot.figure("default", show=False) as (fig, _):
        assert isinstance(fig, Figure)


def test_figure_save_without_output_dir_raises() -> None:
    with pytest.raises(stdplot.MissingOutputError, match="output_dir"):
        stdplot.figure("unsaved", save=True)


def test_plotter_save_writes_every_target(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    with stdplot.Plotter(svg_png_config, save=True, show=False).figure("saved") as (_, ax):
        ax.plot([1, 2, 3])

    assert sorted(path.name for path in tmp_path.iterdir()) == ["saved.png", "saved.svg"]


def test_plotter_call_save_overrides_default(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    plotter = stdplot.Plotter(svg_png_config, save=True, show=False)

    with plotter.figure("unsaved", save=False) as (_, ax):
        ax.plot([1, 2, 3])

    assert list(tmp_path.iterdir()) == []


def test_plotter_save_without_output_dir_raises() -> None:
    with pytest.raises(stdplot.MissingOutputError, match="output_dir"):
        stdplot.Plotter(save=True).figure("unsaved")


def test_plot_decorator_defaults_name_to_function_name(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    @stdplot.Plotter(svg_png_config, save=True, show=False).plot()
    def loss_curve(fig: Figure, ax: Axes) -> None:
        ax.plot([3, 2, 1])

    loss_curve()

    assert (tmp_path / "loss_curve.svg").is_file()


def test_plot_decorator_uses_given_name(
    tmp_path: pathlib.Path, svg_png_config: stdplot.Config
) -> None:
    @stdplot.Plotter(svg_png_config, show=False).plot("custom", save=True)
    def loss_curve(fig: Figure, ax: Axes) -> None:
        ax.plot([3, 2, 1])

    loss_curve()

    assert (tmp_path / "custom.svg").is_file()


def test_plot_decorator_forwards_arguments() -> None:
    @PLOTS.plot()
    def draw(fig: Figure, ax: Axes, first: int, *, second: str) -> tuple[int, str]:
        return first, second

    assert draw(1, second="two") == (1, "two")


def test_plot_decorator_passes_through_return_value() -> None:
    @PLOTS.plot()
    def draw(fig: Figure, ax: Axes) -> Axes:
        return ax

    assert isinstance(draw(), Axes)


def test_plot_decorator_grid_receives_axes_grid() -> None:
    @PLOTS.plot(nrows=2)
    def draw(fig: Figure, axes: stdplot.AxesGrid) -> tuple[int, int]:
        return axes.shape

    assert draw() == (2, 1)


def test_plot_decorator_forwards_size_and_subplots_kw() -> None:
    @PLOTS.plot(ncols=2, size=(6, 3), sharey=True)
    def draw(fig: Figure, axes: stdplot.AxesGrid) -> tuple[tuple[float, ...], bool]:
        return tuple(fig.get_size_inches()), axes[0].get_shared_y_axes().joined(*axes)

    assert draw() == ((6.0, 3.0), True)


def test_plot_decorator_keeps_function_name() -> None:
    @PLOTS.plot()
    def draw(fig: Figure, ax: Axes) -> None:
        pass

    assert draw.__name__ == "draw"


def test_plot_decorator_save_without_output_dir_raises() -> None:
    def draw(fig: Figure, ax: Axes) -> None:
        pass

    with pytest.raises(stdplot.MissingOutputError, match="output_dir"):
        stdplot.plot(save=True)(draw)
