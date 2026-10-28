from __future__ import annotations

import pytest
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from stdplot.application.axes import AxesGrid


def test_axes_grid_single_when_1x1() -> None:
    figure = Figure()

    grid = AxesGrid.from_figure(figure, 1, 1)

    assert grid.single is figure.axes[0]


def test_axes_grid_single_on_2x2_raises() -> None:
    grid = AxesGrid.from_figure(Figure(), 2, 2)

    with pytest.raises(ValueError, match="2x2"):
        _ = grid.single


def test_axes_grid_shape_is_rows_then_columns() -> None:
    assert AxesGrid.from_figure(Figure(), 2, 3).shape == (2, 3)


def test_axes_grid_one_row_stays_2d() -> None:
    assert AxesGrid.from_figure(Figure(), 1, 3).shape == (1, 3)


def test_axes_grid_getitem_row_col() -> None:
    figure = Figure()

    grid = AxesGrid.from_figure(figure, 2, 3)

    assert grid[1, 2] is figure.axes[5]


@pytest.mark.parametrize(("nrows", "ncols"), [(1, 2), (2, 1)])
def test_axes_grid_getitem_int_counts_row_by_row(nrows: int, ncols: int) -> None:
    figure = Figure()

    grid = AxesGrid.from_figure(figure, nrows, ncols)

    assert grid[1] is figure.axes[1]


def test_axes_grid_flat_row_major() -> None:
    figure = Figure()

    grid = AxesGrid.from_figure(figure, 2, 2)

    assert grid.flat == tuple(figure.axes)


def test_axes_grid_iterates_row_major() -> None:
    figure = Figure()

    grid = AxesGrid.from_figure(figure, 2, 3)

    assert list(grid) == figure.axes


def test_axes_grid_len_is_rows_times_columns() -> None:
    assert len(AxesGrid.from_figure(Figure(), 2, 3)) == 6


def test_axes_grid_is_accepted_as_colorbar_axes() -> None:
    figure = Figure()
    grid = AxesGrid.from_figure(figure, 1, 2)
    image = grid[0].imshow([[0.0, 1.0], [1.0, 0.0]])

    colorbar = figure.colorbar(image, ax=grid)

    assert colorbar.ax in figure.axes


def test_axes_grid_forwards_sharex() -> None:
    grid = AxesGrid.from_figure(Figure(), 2, 1, sharex=True)

    assert grid[0].get_shared_x_axes().joined(grid[0], grid[1])


def test_axes_grid_forwards_subplot_projection() -> None:
    grid = AxesGrid.from_figure(Figure(), 1, 1, subplot_kw={"projection": "3d"})

    assert isinstance(grid.single, Axes3D)
