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
import numpy as np

import stdplot

time = np.linspace(0.0, 10.0, 500)
displacement = np.exp(-0.3 * time) * np.cos(2.0 * np.pi * 0.8 * time)

with stdplot.figure("damped_oscillation") as (fig, ax):
    ax.plot(time, displacement)
    ax.set_xlabel(r"Time $t$ [s]")
    ax.set_ylabel(r"Displacement $x$ [mm]")
```
`stdplot.figure` opens a figure styled with the scienceplots `science`, `grid` and `ieee` styles and yields a
plain matplotlib `Figure` and `Axes`. When the block exits, the figure is shown: inline in a Jupyter kernel, in a
Qt window from a script, and nowhere when matplotlib's backend cannot open windows (`MPLBACKEND=Agg`). Without
LaTeX, text is rendered with matplotlib's mathtext instead, after a single warning.

Four objects cover the rest:
- `Config` says *what*: the style, the size figures are drawn at, the `targets` written when saving, the
  `output_dir`, the inline `preview`, the layout engine and the display.
- `Target` is one file: a format, an optional size (none means "the size the figure was drawn at"), a dpi and its
  margins (`Bbox.TIGHT` by default).
- `Plotter` says *how*: it binds a `Config` to whether figures are saved and shown. `stdplot.figure` and
  `stdplot.plot` are the methods of a default `Plotter`, which saves nothing.
- `AxesGrid` is what the block receives instead of an `Axes` as soon as `nrows` or `ncols` is given.

Runnable versions of the recipes below are in [`examples/`](examples).

### Figure size
```python
with stdplot.figure("training_loss", size=(6, 4)) as (fig, ax):
    ...
```
`Config(size=stdplot.Size(6, 4))` sets it for every figure. Targets without a size, such as `SCREEN`, are
written at the size the figure was drawn at.

### Saving SVG only
```python
config = stdplot.Config(targets=(stdplot.SCREEN,), output_dir="figures")

with stdplot.Plotter(config).figure("training_loss", save=True) as (fig, ax):
    ...

for path in config.paths("training_loss"):  # the files saving writes
    print(path)  # figures/training_loss.svg
```
The default targets include an IEEE PGF, which needs LaTeX; `SCREEN` alone saves everywhere.

### Notebook vs script: one switch for saving
```python
SAVE = False  # flip once to write every figure of the notebook
PLOTS = stdplot.Plotter(stdplot.Config(targets=(stdplot.SCREEN,), output_dir="figures"), save=SAVE)

with PLOTS.figure("training_loss", size=(6, 4)) as (fig, ax):
    ...

with PLOTS.figure("scratch", save=False) as (fig, ax):  # a call overrides the Plotter
    ...
```
In a notebook, figures appear below their cell. In a script, each figure opens a Qt window that blocks until it is
closed; run the script under `MPLBACKEND=Agg` (or call `matplotlib.use("Agg")` first) and it never blocks. To
never show anything, use `stdplot.Plotter(config, show=False)` or `Config(display=stdplot.Display.NONE)`.

### PGF for LaTeX
```python
paper = stdplot.Config(targets=(stdplot.IEEE_PGF, stdplot.SCREEN), output_dir="figures")
# 6.33589 in is the \textwidth of the thesis.
thesis = stdplot.Config(targets=(stdplot.pgf(6.33589),), output_dir="figures")
```
`IEEE_PGF` is one IEEE column wide, `ieee_pgf(scale=0.5)` half of one, and `pgf(width, aspect)` any width. They
keep standard margins (`Bbox.STANDARD`), so the PGF is exactly as wide as asked; include it with
`\input{figures/name.pgf}`. Saving a PGF needs the configured TeX system (`pdflatex` by default) on the PATH:
without it, `LatexNotFoundError` is raised before your drawing code runs.

### Subplot options
```python
with stdplot.figure("signals", nrows=2, ncols=2, sharex=True) as (fig, axes):
    axes[0, 1].plot(...)  # by row and column
    image = axes[3].imshow(...)  # the 4th axes, counted row by row
    for ax in axes:
        ax.set_xlabel("Time [s]")
    fig.colorbar(image, ax=axes)  # an AxesGrid goes wherever matplotlib takes several axes
```
`sharex`, `sharey`, `width_ratios`, `height_ratios`, `subplot_kw` and `gridspec_kw` are forwarded to matplotlib's
`Figure.subplots`. A 3D axes is still typed `Axes`; cast it to reach the 3D methods:
```python
import typing

from mpl_toolkits.mplot3d import Axes3D

with stdplot.figure("saddle_point", subplot_kw={"projection": "3d"}) as (fig, ax):
    typing.cast(Axes3D, ax).plot_surface(x, y, z)
```

### Two styles for the same figure
The style applies while the figure is drawn, because matplotlib reads fonts and `text.usetex` when each artist is
created. One drawn figure therefore cannot be written under two styles: draw it once per config.
```python
latex = stdplot.Config(targets=(stdplot.pgf(6.33589),), output_dir="figures")
plain = stdplot.Config(
    style=stdplot.Style().without_latex(),
    targets=(stdplot.Target(stdplot.Format.PNG, dpi=300),),
    output_dir="figures",
)

for config in (latex, plain):
    with stdplot.Plotter(config, save=True, show=False).figure("umap") as (fig, ax):
        draw_umap(ax)
```


## Disclaimer
This repository originated from a personal script I've developped on my own. Now it is rewriten heavily using `Claude` based on that previous work. It is mostly a project use by me as introduction and exploration of the capabilities of such tools in my workflow.
