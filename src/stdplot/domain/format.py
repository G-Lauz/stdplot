"""Enumerations of the export formats, layout engines and display backends."""

from __future__ import annotations

import enum


class Format(enum.Enum):
    """File format of an export; the value is both the extension and matplotlib's name."""

    PGF = "pgf"
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"


class Layout(enum.Enum):
    """Layout engine re-run before every export; the value is matplotlib's name."""

    TIGHT = "tight"
    CONSTRAINED = "constrained"
    NONE = "none"


class Display(enum.Enum):
    """Where a shown figure appears."""

    AUTO = "auto"
    NOTEBOOK = "notebook"
    QT = "qt"
