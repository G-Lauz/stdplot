"""Quickstart: draw one figure and look at it.

`stdplot.figure` opens a figure styled with the scienceplots `science`, `grid` and
`ieee` styles, and yields its `Figure` and `Axes`. The whole matplotlib API is
available on both. When the block exits, the figure is shown:

- from a script, in a Qt window with the matplotlib toolbar (`stdplot[qt]` extra);
- in a Jupyter kernel, inline below the cell (`stdplot[notebook]` extra).

Without a LaTeX installation, stdplot warns once and renders text with matplotlib's
mathtext instead, so the same code runs everywhere.

Run: python examples/quickstart.py
"""

import numpy

from stdplot import Stdplot

if __name__ == "__main__":
    stdplot = Stdplot()

    time = numpy.linspace(0.0, 10.0, 500)
    displacement = numpy.exp(-0.3 * time) * numpy.cos(2.0 * numpy.pi * 0.8 * time)

    with stdplot.figure("damped_oscillation") as (fig, ax):
        ax.plot(time, displacement)
        ax.set_xlabel(r"Time $t$ [s]")
        ax.set_ylabel(r"Displacement $x$ [mm]")
