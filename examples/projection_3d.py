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

import dataclasses
import pathlib
import typing

import numpy as np
from matplotlib.axes import Axes

import stdplot

if typing.TYPE_CHECKING:
    from mpl_toolkits.mplot3d import Axes3D

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"

SURFACE = stdplot.Config(
    output_dir=OUTPUT_DIR,
    targets=(
        dataclasses.replace(stdplot.pgf(4.0), bbox=stdplot.Bbox.TIGHT),
        stdplot.SCREEN,
    ),
)


def draw_saddle(ax: Axes) -> None:
    ax3d = typing.cast("Axes3D", ax)
    x, y = np.meshgrid(np.linspace(-2.0, 2.0, 60), np.linspace(-2.0, 2.0, 60))
    ax3d.plot_surface(x, y, x**2 - y**2, cmap="viridis")
    ax3d.set_xlabel("$x$")
    ax3d.set_ylabel("$y$")
    ax3d.set_zlabel("$f(x, y) = x^2 - y^2$")


config = SURFACE
try:
    with stdplot.Plotter(config, save=True).figure(
        "saddle_point", size=(5, 4), subplot_kw={"projection": "3d"}
    ) as (_, ax):
        draw_saddle(ax)
except stdplot.LatexNotFoundError as error:
    print(f"{error}\nWriting the targets that do not need LaTeX.")
    without_latex = tuple(target for target in SURFACE.targets if not target.requires_latex)
    config = dataclasses.replace(SURFACE, targets=without_latex)
    with stdplot.Plotter(config, save=True).figure(
        "saddle_point", size=(5, 4), subplot_kw={"projection": "3d"}
    ) as (_, ax):
        draw_saddle(ax)

for path in config.paths("saddle_point"):
    print(f"Wrote {path}")
