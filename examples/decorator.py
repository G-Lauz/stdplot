"""Decorator: turn a drawing function into a figure you can redraw with new data.

`@stdplot.plot` passes the figure and its axes ahead of the function's own
arguments. Every call draws a fresh figure, saves and shows it, then returns what
the function returned. The figure is named after the function unless you pass a
name, and `nrows`/`ncols` give the function an `AxesGrid`, as with `stdplot.figure`.

Here the decorator comes from a `Plotter` that saves every figure, so the whole
script turns saving on in one place.

Run: python examples/decorator.py
"""

import pathlib

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import stdplot

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"
SCREEN_ONLY = stdplot.Config(output_dir=OUTPUT_DIR, targets=(stdplot.SCREEN,))
PLOTS = stdplot.Plotter(SCREEN_ONLY, save=True)
EPOCHS = np.arange(1, 41)


def simulate_run(learning_rate: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Return synthetic training and validation losses for one learning rate."""
    speed = learning_rate * 1000.0
    train = 0.2 + 2.0 * np.exp(-speed * EPOCHS / 8.0)
    overfitting = 0.0008 * np.maximum(EPOCHS - 25.0 / speed, 0.0) ** 2
    noise = rng.normal(0.0, 0.02, EPOCHS.size)
    return train, train + 0.1 + overfitting + noise


# Saved as figures/loss_curve.svg, after the function's name.
@PLOTS.plot()
def loss_curve(fig: Figure, ax: Axes, train: np.ndarray, validation: np.ndarray) -> int:
    """Plot one run and return the epoch with the lowest validation loss."""
    best = int(np.argmin(validation))
    ax.plot(EPOCHS, train, label="Training")
    ax.plot(EPOCHS, validation, label="Validation")
    ax.plot(EPOCHS[best], validation[best], "o", label="Lowest validation loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.legend()
    return int(EPOCHS[best])


# A custom name and a 1x2 grid: the function receives an AxesGrid.
@PLOTS.plot("learning_rate_sweep", ncols=2)
def compare_runs(
    fig: Figure, axes: stdplot.AxesGrid, runs: dict[str, tuple[np.ndarray, np.ndarray]]
) -> None:
    for label, (train, validation) in runs.items():
        axes[0, 0].plot(EPOCHS, train, label=label)
        axes[0, 1].plot(EPOCHS, validation, label=label)
    axes[0, 0].set_ylabel("Training loss")
    axes[0, 1].set_ylabel("Validation loss")
    for ax in axes.flat:
        ax.set_xlabel("Epoch")
    axes[0, 1].legend(title="Learning rate")


rng = np.random.default_rng(seed=0)
runs = {f"{rate:g}": simulate_run(rate, rng) for rate in (1e-3, 3e-3, 1e-2)}

best_epoch = loss_curve(*runs["0.003"])
print(f"Learning rate 0.003 reaches its lowest validation loss at epoch {best_epoch}")
compare_runs(runs)
