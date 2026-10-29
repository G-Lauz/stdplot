"""Configuration: one Config for a whole project, and variants derived from it.

A `Config` is an immutable dataclass, so a project defines its house style once and
derives variants with `dataclasses.replace`. It sets:

- `style`: scienceplots style names, plus the LaTeX settings applied on top of them;
- `targets`: the files written when saving;
- `size`: the size the figure is drawn at, and written at by targets without a size;
- `preview`: the format and dpi of the figure shown inline in a notebook;
- `layout`: the layout engine re-run before every export (`TIGHT`, `CONSTRAINED`, `NONE`);
- `display`: where shown figures appear (`AUTO`, `NOTEBOOK`, `QT` or `NONE`).

A `Stdplot` binds a config to the save and show defaults of its figures. This example
draws the same figure twice: for a Nature-style article, then for slides.

Run: python examples/custom_config.py
"""

import dataclasses
import pathlib

import numpy

from stdplot import Config, Format, LatexSettings, Layout, Size, Stdplot, Style, Target

OUTPUT_DIR = pathlib.Path(__file__).parent / "figures"

ARTICLE = Config(
    # The nature style uses a sans-serif font; the LaTeX settings must agree, since
    # they are applied after the named styles.
    style=Style(
        names=("science", "nature"),
        latex=LatexSettings(font_family="sans-serif"),
    ),
    targets=(
        # 89 mm is one Nature column. Unlike PGF, PDF also works without LaTeX.
        Target(Format.PDF, Size.from_width(89 / 25.4, 0.75)),
        Target(Format.PNG, Size.from_width(89 / 25.4, 0.75), dpi=600),
    ),
    size=Size(6.0, 4.5),
    preview=Target(Format.SVG, dpi=120),
    output_dir=OUTPUT_DIR / "article",
    layout=Layout.CONSTRAINED,
)

# Keeps the size, preview and layout engine; larger fonts and a 16:9 SVG for slides.
SLIDES = dataclasses.replace(
    ARTICLE,
    style=Style(names=("science", "notebook")),
    targets=(Target(Format.SVG, Size(10.0, 5.625), dpi=100),),
    output_dir=OUTPUT_DIR / "slides",
)


if __name__ == "__main__":
    time = numpy.linspace(0.0, 10.0, 500)
    displacement = numpy.exp(-0.3 * time) * numpy.cos(2.0 * numpy.pi * 0.8 * time)

    for config in (ARTICLE, SLIDES):
        stdplot = Stdplot(config, save=False, show=True)

        with stdplot.figure("damped_oscillation") as (fig, ax):
            ax.plot(time, displacement)
            ax.set_xlabel(r"Time $t$ [s]")
            ax.set_ylabel(r"Displacement $x$ [mm]")
