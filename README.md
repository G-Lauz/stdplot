# Standard Plot
A standardized wrapper around `matplotlib` targeting a variety of canvases.

## Installation
Default installation is via `pip`:
```bash
pip install stdplot
```
For notebook and GUI support, install the optional dependencies:
```bash
pip install stdplot[notebook,qt] # or [all]
```
The `qt` extra installs PySide6 for convenience only: any Qt binding matplotlib supports (PyQt6, PyQt5,
PySide2) works as well. Qt is imported only when a window opens, never by `import stdplot`.

## Usage
### Quickstart
```python
import numpy

from stdplot import Stdplot

stdplot = Stdplot()

time = numpy.linspace(0.0, 10.0, 500)
displacement = numpy.exp(-0.3 * time) * numpy.cos(2.0 * numpy.pi * 0.8 * time)

with stdplot.figure("damped_oscillation") as (fig, ax):
    ax.plot(time, displacement)
    ax.set_xlabel(r"Time $t$ [s]")
    ax.set_ylabel(r"Displacement $x$ [mm]")
```
`Stdplot()` is a drawing session with the default config. Its `figure` method opens a figure styled with the
scienceplots `science`, `grid` and `ieee` styles and yields a plain matplotlib `Figure` and `Axes`. When the block
exits, the figure is shown: inline in a Jupyter kernel, in a Qt window from a script, and nowhere when matplotlib's
backend cannot open windows (`MPLBACKEND=Agg`). Without LaTeX, text is rendered with matplotlib's mathtext
instead, after a single warning.

Four objects cover the rest:
- `Config` says *what*: the style, the size figures are drawn at, the `targets` written when saving, the
  `output_dir`, the inline `preview`, the layout engine and the display.
- `Target` is one file: a format, an optional size (none means "the size the figure was drawn at"), a dpi and its
  margins (`Bbox.TIGHT` by default).
- `Stdplot` says *how*: it binds a `Config` to whether figures are saved and shown. `Stdplot()` uses the default
  config, saves nothing and shows every figure. `import stdplot` also gives `stdplot.figure` and `stdplot.plot`,
  the methods of such a default session.
- `AxesGrid` is what the block receives instead of an `Axes` as soon as `nrows` or `ncols` is given.

Runnable versions of the recipes below are in [`examples/`](examples). The recipes reuse `time` and
`displacement` from the quickstart.

### Figure size
```python
with stdplot.figure("damped_oscillation", size=(6, 4)) as (fig, ax):
    ax.plot(time, displacement)
```
`Config(size=Size(6, 4))` sets it for every figure. Targets without a size, such as `SCREEN`, are written at the
size the figure was drawn at.

### Saving SVG only
```python
from stdplot import SCREEN, Config, Stdplot

config = Config(targets=(SCREEN,), output_dir="figures")
stdplot = Stdplot(config, save=True, show=True)

with stdplot.figure("damped_oscillation") as (fig, ax):
    ax.plot(time, displacement)
```
The default targets include an IEEE PGF, which needs LaTeX; `SCREEN` alone saves everywhere.

### Notebook vs script: one switch for saving
```python
from stdplot import SCREEN, Config, Stdplot

SAVE = False  # flip once to write every figure of the notebook

config = Config(targets=(SCREEN,), output_dir="figures")
stdplot = Stdplot(config, save=SAVE, show=True)

with stdplot.figure("damped_oscillation", size=(6, 4)) as (fig, ax):
    ax.plot(time, displacement)

with stdplot.figure("scratch", save=False) as (fig, ax):  # a call overrides the session
    ax.plot(time, displacement)
```
In a notebook, figures appear below their cell. In a script, each figure opens a Qt window that blocks until it is
closed; run the script under `MPLBACKEND=Agg` (or call `matplotlib.use("Agg")` first) and it never blocks. To
never show anything, use `Stdplot(config, show=False)` or `Config(display=Display.NONE)`.

### PGF for LaTeX
```python
from stdplot import IEEE_PGF, SCREEN, Config, pgf

paper = Config(targets=(IEEE_PGF, SCREEN), output_dir="figures")
# 6.33589 may be the \textwidth of a paper.
thesis = Config(targets=(pgf(6.33589),), output_dir="figures")
```
`IEEE_PGF` is one IEEE column wide, `ieee_pgf(scale=0.5)` half of one, and `pgf(width, aspect)` any width. They
keep standard margins (`Bbox.STANDARD`), so the PGF is exactly as wide as asked; include it with
`\input{figures/damped_oscillation.pgf}`. Saving a PGF needs the configured TeX system (`pdflatex` by default) on
the PATH: without it, `LatexNotFoundError` is raised before your drawing code runs.

### Subplot options
```python
with stdplot.figure("grid", nrows=2, ncols=2, sharex=True) as (fig, axes):
    for ax in axes:  # every axes, row by row
        ax.plot(time, displacement)
    axes[0, 0].set_title("Top left")  # by row and column
    axes[3].set_title("Bottom right")  # the 4th axes, counted row by row
```
`sharex`, `sharey`, `width_ratios`, `height_ratios`, `subplot_kw` and `gridspec_kw` are forwarded to matplotlib's
`Figure.subplots`. Being iterable, an `AxesGrid` goes wherever matplotlib takes several axes, such as
`fig.colorbar(image, ax=axes)`.

A 3D axes is still typed `Axes`; cast it to reach the 3D methods:
```python
import typing

import numpy
from mpl_toolkits.mplot3d import Axes3D

x, y = numpy.meshgrid(numpy.linspace(-2.0, 2.0, 60), numpy.linspace(-2.0, 2.0, 60))

with stdplot.figure("saddle_point", subplot_kw={"projection": "3d"}) as (fig, ax):
    ax3d = typing.cast(Axes3D, ax)
    ax3d.plot_surface(x, y, x**2 - y**2, cmap="viridis")
```

### Two styles for the same figure
The style applies while the figure is drawn, because matplotlib reads fonts and `text.usetex` when each artist is
created. One drawn figure therefore cannot be written under two styles: draw it once per config.
```python
from stdplot import Config, Format, Stdplot, Style, Target, pgf

latex = Config(targets=(pgf(6.33589),), output_dir="figures")
plain = Config(
    style=Style().without_latex(),
    targets=(Target(Format.PNG, dpi=300),),
    output_dir="figures",
)

for config in (latex, plain):
    stdplot = Stdplot(config, save=True, show=False)
    with stdplot.figure("damped_oscillation") as (fig, ax):
        ax.plot(time, displacement)
```


## Disclaimer
This repository originated from a personal script I've developped on my own. Now it is rewriten heavily using `Claude` based on that previous work. It is mostly a project use by me as introduction and exploration of the capabilities of such tools in my workflow.
