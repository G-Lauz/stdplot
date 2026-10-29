r"""Export: draw once, write a PGF for LaTeX plus SVG and PNG copies.

With `save=True`, every target of the config is written to `output_dir` when the
block exits, and `config.paths(name)` names the written files. A target is a format,
a size in inches, a dpi and margins: the figure is resized for each target with a
size, so `IEEE_PGF` comes out exactly one IEEE column wide and its text matches the
paper's fonts. Include it with `\input{figures/damped_oscillation.pgf}`. A target
without a size, such as `SCREEN`, is written at the size the figure was drawn at.

PGF needs a LaTeX installation. Without one, stdplot raises `LatexNotFoundError`
before the drawing code runs; this example then writes the other targets only.

Run: python examples/export.py
"""

import dataclasses
import pathlib

import numpy
from matplotlib.axes import Axes

from stdplot import IEEE_PGF, SCREEN, Config, Format, LatexNotFoundError, Size, Stdplot, Target

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"

PAPER = Config(
    output_dir=OUTPUT_DIR,
    targets=(
        IEEE_PGF,  # one IEEE column, for the paper
        SCREEN,  # SVG at the drawn size (8 x 6 in by default), for slides
        Target(Format.PNG, Size(6.0, 4.0), dpi=200),
    ),
)


def draw_damped_oscillation(ax: Axes) -> None:
    time = numpy.linspace(0.0, 10.0, 500)
    displacement = numpy.exp(-0.3 * time) * numpy.cos(2.0 * numpy.pi * 0.8 * time)

    ax.plot(time, displacement)
    ax.set_xlabel(r"Time $t$ [s]")
    ax.set_ylabel(r"Displacement $x$ [mm]")


if __name__ == "__main__":
    config = PAPER
    stdplot = Stdplot(config, save=True, show=True)
    try:
        with stdplot.figure("damped_oscillation") as (fig, ax):
            draw_damped_oscillation(ax)

    except LatexNotFoundError as error:
        print(f"{error}\nWriting the targets that do not need LaTeX.")

        without_latex = tuple(target for target in PAPER.targets if not target.requires_latex)
        config = dataclasses.replace(PAPER, targets=without_latex)

        stdplot = Stdplot(config, save=True, show=False)

        with stdplot.figure("damped_oscillation") as (fig, ax):
            draw_damped_oscillation(ax)

    for path in config.paths("damped_oscillation"):
        print(f"Wrote {path}")
