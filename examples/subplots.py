"""Subplots: ask for a grid of axes and address it by row and column, or by count.

Passing `nrows` or `ncols` yields an `AxesGrid` instead of a single `Axes`, even for
a 1x1 grid, so the type of the axes always follows from the call:

- `axes[row, col]` is one `Axes`;
- `axes[i]` is the i-th axes, counted row by row, whatever the shape of the grid;
- `for ax in axes` visits every axes row by row, and `len(axes)` counts them;
- `axes.shape` is `(nrows, ncols)`.

Other keywords, such as `sharex`, `sharey`, `width_ratios` or `subplot_kw`, are
forwarded to matplotlib's `Figure.subplots`.

Each figure is shown in turn; close its window to move on to the next one. Under
`MPLBACKEND=Agg`, nothing is shown and the script runs straight through.

Run: python examples/subplots.py
"""

import numpy

from stdplot import Stdplot

if __name__ == "__main__":
    stdplot = Stdplot()

    time = numpy.linspace(0.0, 10.0, 500)
    displacement = numpy.exp(-0.3 * time) * numpy.cos(2.0 * numpy.pi * 0.8 * time)

    # A 2x2 grid: visit every axes in turn, or pick one by row and column.
    with stdplot.figure("grid", nrows=2, ncols=2) as (fig, axes):
        print(f"The grid has shape {axes.shape} and holds {len(axes)} axes")
        for ax in axes:
            ax.plot(time, displacement)
        axes[0, 0].set_title("Top left")
        axes[1, 1].set_title("Bottom right")

    # A single column sharing its time axis: only the bottom axes needs an x label.
    with stdplot.figure("column", nrows=2, sharex=True) as (fig, axes):
        axes[0].plot(time, displacement)
        axes[1].plot(time, displacement)
        axes[1].set_xlabel(r"Time $t$ [s]")
