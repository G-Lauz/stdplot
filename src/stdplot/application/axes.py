"""Typed access to the grid of axes of a figure."""

from __future__ import annotations

import dataclasses
import typing

if typing.TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


@dataclasses.dataclass(frozen=True)
class AxesGrid:
    """The axes of a figure, by row then column.

    Attributes:
        rows: One tuple per row, holding the axes of each column.
    """

    rows: tuple[tuple[Axes, ...], ...]

    @classmethod
    def from_figure(cls, figure: Figure, nrows: int, ncols: int) -> AxesGrid:
        """Add an `nrows` by `ncols` grid of axes to the figure.

        Args:
            figure: Figure the axes are added to.
            nrows: Number of rows.
            ncols: Number of columns.

        Returns:
            The grid of the added axes.
        """
        # squeeze=False keeps the array 2-D even when nrows or ncols is 1.
        array = figure.subplots(nrows, ncols, squeeze=False)
        return cls(tuple(tuple(row) for row in array))

    @property
    def shape(self) -> tuple[int, int]:
        """Number of rows and columns."""
        return (len(self.rows), len(self.rows[0]))

    @property
    def flat(self) -> tuple[Axes, ...]:
        """Every axes, row by row."""
        return tuple(axes for row in self.rows for axes in row)

    @property
    def single(self) -> Axes:
        """The only axes of a 1x1 grid.

        Raises:
            ValueError: The grid holds more than one axes.
        """
        is_single = self.shape == (1, 1)
        if not is_single:
            nrows, ncols = self.shape
            raise ValueError(f"The grid holds {nrows}x{ncols} axes, not a single one.")
        return self.rows[0][0]

    def __getitem__(self, position: tuple[int, int]) -> Axes:
        """Return the axes at `(row, column)`."""
        row, col = position
        return self.rows[row][col]
