"""Configuration: one Config for a whole project, and variants derived from it.

A `Config` is an immutable dataclass, so a project defines its house style once and
derives variants with `dataclasses.replace`. It sets:

- `style`: scienceplots style names, plus the LaTeX settings applied on top of them;
- `targets`: the files written when saving;
- `size`: the size the figure is drawn at, and written at by targets without a size;
- `preview`: the format and dpi of the figure shown inline in a notebook;
- `layout`: the layout engine re-run before every export (`TIGHT`, `CONSTRAINED`, `NONE`);
- `display`: where shown figures appear (`AUTO`, `NOTEBOOK`, `QT` or `NONE`).

A `Plotter` binds a config to the save and show defaults of its figures. This example
draws the same calibration plot twice: for a Nature-style article, then for slides.

Run: python examples/custom_config.py
"""

import dataclasses
import pathlib

import numpy as np
from matplotlib.axes import Axes

import stdplot

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"

ARTICLE = stdplot.Config(
    # The nature style uses a sans-serif font; the LaTeX settings must agree, since
    # they are applied after the named styles.
    style=stdplot.Style(
        names=("science", "nature"),
        latex=stdplot.LatexSettings(font_family="sans-serif"),
    ),
    targets=(
        # 89 mm is one Nature column. Unlike PGF, PDF also works without LaTeX.
        stdplot.Target(stdplot.Format.PDF, stdplot.Size.from_width(89 / 25.4, 0.75)),
        stdplot.Target(stdplot.Format.PNG, stdplot.Size.from_width(89 / 25.4, 0.75), dpi=600),
    ),
    size=stdplot.Size(6.0, 4.5),
    preview=stdplot.Target(stdplot.Format.SVG, dpi=120),
    output_dir=OUTPUT_DIR / "article",
    layout=stdplot.Layout.CONSTRAINED,
)

# Keeps the size, preview and layout engine; larger fonts and a 16:9 SVG for slides.
SLIDES = dataclasses.replace(
    ARTICLE,
    style=stdplot.Style(names=("science", "notebook")),
    targets=(stdplot.Target(stdplot.Format.SVG, stdplot.Size(10.0, 5.625), dpi=100),),
    output_dir=OUTPUT_DIR / "slides",
)


def draw_calibration(ax: Axes) -> None:
    rng = np.random.default_rng(seed=0)
    reference = np.linspace(0.0, 50.0, 12)
    measured = 1.04 * reference - 0.8 + rng.normal(0.0, 0.9, reference.size)
    slope, intercept = np.polyfit(reference, measured, deg=1)
    ax.plot(reference, measured, "o", label="Measurements")
    ax.plot(reference, slope * reference + intercept, label=f"Fit: slope {slope:.3f}")
    ax.set_xlabel("Reference temperature [K]")
    ax.set_ylabel("Sensor reading [K]")
    ax.legend()


for name, config in (("article", ARTICLE), ("slides", SLIDES)):
    with stdplot.Plotter(config, save=True).figure(f"calibration_{name}") as (_, ax):
        draw_calibration(ax)
