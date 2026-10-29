"""Decorator: turn a drawing function into a figure you can redraw with new data.

`@stdplot.plot` passes the figure and its axes ahead of the function's own
arguments. Every call draws a fresh figure and shows it, then returns what the
function returned. The figure is named after the function unless you pass a name,
and `nrows`/`ncols` give the function an `AxesGrid`, as with `stdplot.figure`.

Run: python examples/decorator.py
"""

import numpy
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from stdplot import Stdplot

# A decorator runs when its function is defined, so the session must exist before the
# decorated function below, rather than under `__main__`.
stdplot = Stdplot(save=False, show=True)


# No name given: the figure is named after the function, "damped_oscillation".
@stdplot.plot()
def damped_oscillation(
    fig: Figure, ax: Axes, time: numpy.ndarray, displacement: numpy.ndarray
) -> None:
    ax.plot(time, displacement)
    ax.set_xlabel(r"Time $t$ [s]")
    ax.set_ylabel(r"Displacement $x$ [mm]")


if __name__ == "__main__":
    time = numpy.linspace(0.0, 10.0, 500)
    displacement = numpy.exp(-0.3 * time) * numpy.cos(2.0 * numpy.pi * 0.8 * time)

    damped_oscillation(time, displacement)
