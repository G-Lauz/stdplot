from __future__ import annotations

import pytest
from matplotlib.figure import Figure

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


def test_axes_grid_flat_row_major() -> None:
    figure = Figure()

    grid = AxesGrid.from_figure(figure, 2, 2)

    assert grid.flat == tuple(figure.axes)
