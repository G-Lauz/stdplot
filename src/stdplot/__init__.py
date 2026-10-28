"""Publication-ready matplotlib figures, drawn once and exported to every target."""

# Importing scienceplots registers its styles, which the default Style names.
import scienceplots

from stdplot.application import (
    IEEE_PGF,
    SCREEN,
    AxesGrid,
    Bbox,
    Config,
    Display,
    Format,
    LatexNotFoundError,
    LatexSettings,
    Layout,
    MissingDependencyError,
    MissingOutputError,
    Size,
    StdplotError,
    Style,
    SubplotOptions,
    Target,
    UnknownStyleError,
    ieee_pgf,
    pgf,
)
from stdplot.presentation.api import Plotter, figure, plot

__all__ = [
    "IEEE_PGF",
    "SCREEN",
    "AxesGrid",
    "Bbox",
    "Config",
    "Display",
    "Format",
    "LatexNotFoundError",
    "LatexSettings",
    "Layout",
    "MissingDependencyError",
    "MissingOutputError",
    "Plotter",
    "Size",
    "StdplotError",
    "Style",
    "SubplotOptions",
    "Target",
    "UnknownStyleError",
    "figure",
    "ieee_pgf",
    "pgf",
    "plot",
]
