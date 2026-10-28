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

import numpy as np

import stdplot

rng = np.random.default_rng(seed=0)
time = np.linspace(0.0, 2.0, 400)
measured = np.sin(2.0 * np.pi * 1.5 * time) + rng.normal(0.0, 0.25, time.size)
window = np.ones(25) / 25
smoothed = np.convolve(measured, window, mode="same")
residual = measured - smoothed

with stdplot.figure("measurement_analysis", nrows=2, ncols=2) as (fig, axes):
    axes[0, 0].plot(time, measured)
    axes[0, 0].set_ylabel("Raw signal [V]")

    axes[0, 1].plot(time, smoothed)
    axes[0, 1].set_ylabel("Moving average [V]")

    axes[1, 0].plot(time, residual)
    axes[1, 0].set_ylabel("Residual [V]")

    axes[1, 1].hist(residual, bins=30)
    axes[1, 1].set_xlabel("Residual [V]")
    axes[1, 1].set_ylabel("Count")

    for ax in axes.flat[:3]:
        ax.set_xlabel(r"Time $t$ [s]")
    for letter, ax in zip("abcd", axes, strict=True):
        ax.set_title(f"({letter})", loc="left")

# A single column sharing its time axis: only the bottom axes needs tick labels.
with stdplot.figure("signal_and_residual", nrows=2, sharex=True) as (fig, axes):
    axes[0].plot(time, measured, label="Raw")
    axes[0].plot(time, smoothed, label="Moving average")
    axes[0].set_ylabel("Signal [V]")
    axes[0].legend()
    axes[1].plot(time, residual)
    axes[1].set_ylabel("Residual [V]")
    axes[1].set_xlabel(r"Time $t$ [s]")

# A single row: ncols alone is enough, nrows defaults to 1.
with stdplot.figure("harmonics", ncols=3) as (fig, axes):
    print(f"The harmonics grid has shape {axes.shape} and holds {len(axes)} axes")
    for harmonic, ax in enumerate(axes, start=1):
        ax.plot(time, np.sin(2.0 * np.pi * harmonic * time))
        ax.set_title(f"Harmonic {harmonic}")
        ax.set_xlabel(r"Time $t$ [s]")
    axes[0].set_ylabel("Amplitude [V]")
