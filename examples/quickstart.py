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

import numpy as np

import stdplot

time = np.linspace(0.0, 10.0, 500)
displacement = np.exp(-0.3 * time) * np.cos(2.0 * np.pi * 0.8 * time)

with stdplot.figure("damped_oscillation") as (fig, ax):
    ax.plot(time, displacement)
    ax.set_xlabel(r"Time $t$ [s]")
    ax.set_ylabel(r"Displacement $x$ [mm]")
