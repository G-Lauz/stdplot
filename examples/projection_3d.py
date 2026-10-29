"""3D axes: forward `subplot_kw` to `Figure.subplots`, then cast the axes.

Keywords that `stdplot.figure` does not handle itself go to matplotlib's
`Figure.subplots`, so `subplot_kw={"projection": "3d"}` makes a 3D axes. Its static
type is still `Axes`: cast it to `Axes3D` to reach the 3D methods.

The PGF built by `stdplot.pgf` keeps standard margins, so it is exactly as wide as
asked. A 3D plot leaves wide empty margins around its box, so this PGF crops them
with a tight bbox instead, at the cost of an exact width.

PGF needs a LaTeX installation; as in `export.py`, the other targets are written
without one.

Run: python examples/projection_3d.py
"""

import pathlib
import typing

import numpy

from stdplot import SCREEN, Config, Stdplot

if typing.TYPE_CHECKING:
    from mpl_toolkits.mplot3d import Axes3D

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"

SURFACE = Config(output_dir=OUTPUT_DIR, targets=(SCREEN,))


if __name__ == "__main__":
    stdplot = Stdplot(SURFACE, save=False, show=True)

    projection_3d = {"projection": "3d"}

    with stdplot.figure("saddle_point", size=(5, 4), subplot_kw=projection_3d) as (fig, ax):
        x, y = numpy.meshgrid(numpy.linspace(-2.0, 2.0, 60), numpy.linspace(-2.0, 2.0, 60))

        ax3d = typing.cast("Axes3D", ax)

        ax3d.plot_surface(x, y, x**2 - y**2, cmap="viridis")
        ax3d.set_xlabel("$x$")
        ax3d.set_ylabel("$y$")
        ax3d.set_zlabel("$f(x, y) = x^2 - y^2$")

    for path in SURFACE.paths("saddle_point"):
        print(f"Wrote {path}")
