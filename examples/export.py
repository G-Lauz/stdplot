r"""Export: draw once, write a PGF for LaTeX plus SVG and PNG copies.

With `save=True`, every target of the config is written to `output_dir` when the
block exits. A target is a format, a size in inches and a dpi: the figure is resized
for each one, so `IEEE_PGF` comes out exactly one IEEE column wide and its text
matches the paper's fonts. Include it with `\input{figures/step_response.pgf}`.

PGF needs a LaTeX installation. Without one, stdplot raises `LatexNotFoundError`
before the drawing code runs; this example then writes the other targets only.

Run: python examples/export.py
"""

import dataclasses
import pathlib

import numpy as np
from matplotlib.axes import Axes

import stdplot

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"

PAPER = stdplot.Config(
    output_dir=OUTPUT_DIR,
    targets=(
        stdplot.IEEE_PGF,  # one IEEE column, for the paper
        stdplot.SCREEN,  # 8 x 6 in SVG, for slides
        stdplot.Target(stdplot.Format.PNG, stdplot.Size(6.0, 4.0), dpi=200),
    ),
)


def draw_step_response(ax: Axes) -> None:
    time = np.linspace(0.0, 15.0, 600)
    for damping in (0.2, 0.5, 0.8):
        damped_frequency = np.sqrt(1.0 - damping**2)
        envelope = np.exp(-damping * time) / damped_frequency
        response = 1.0 - envelope * np.sin(damped_frequency * time + np.arccos(damping))
        ax.plot(time, response, label=rf"$\zeta = {damping}$")
    ax.set_xlabel(r"Time $t$ [s]")
    ax.set_ylabel(r"Output $y$")
    ax.legend(title="Damping ratio")


try:
    with stdplot.figure("step_response", config=PAPER, save=True, show=False) as (_, ax):
        draw_step_response(ax)
except stdplot.LatexNotFoundError as error:
    print(f"{error}\nWriting the targets that do not need LaTeX.")
    without_latex = tuple(target for target in PAPER.targets if not target.requires_latex)
    config = dataclasses.replace(PAPER, targets=without_latex)
    with stdplot.figure("step_response", config=config, save=True, show=False) as (_, ax):
        draw_step_response(ax)

for path in sorted(OUTPUT_DIR.glob("step_response.*")):
    print(f"Wrote {path}")
