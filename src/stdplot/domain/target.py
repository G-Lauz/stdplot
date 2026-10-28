"""Export targets: what format a figure is written to, at what size and with what margins."""

from __future__ import annotations

import dataclasses

from .format import Bbox, Format

IEEE_COLUMN_WIDTH_IN = 3.40067


@dataclasses.dataclass(frozen=True)
class Size:
    """Physical size of a figure, in inches."""

    width: float
    height: float

    def __post_init__(self) -> None:
        """Reject sizes matplotlib cannot draw.

        Raises:
            ValueError: The width or the height is not positive.
        """
        is_positive = self.width > 0 and self.height > 0
        if not is_positive:
            raise ValueError(f"A size must be positive, got {self.width} x {self.height} in.")

    @classmethod
    def from_width(cls, width: float, aspect: float) -> Size:
        """Build a size from its width and its height-to-width ratio.

        Args:
            width: Width, in inches.
            aspect: Height divided by width.

        Returns:
            The size.
        """
        return cls(width, width * aspect)

    def as_tuple(self) -> tuple[float, float]:
        """Return the size as the `(width, height)` pair matplotlib expects."""
        return (self.width, self.height)


@dataclasses.dataclass(frozen=True)
class Target:
    """One file a figure is exported to.

    Attributes:
        format: File format.
        size: Size the file is written at; `None` keeps the size the figure was drawn at.
        dpi: Resolution of the raster output and of the raster elements embedded in it.
        bbox: Margins of the file. A PGF sized to a column must use `Bbox.STANDARD`,
            since a tight bbox would make it narrower than the column; `pgf` and
            `ieee_pgf` do.
    """

    format: Format
    size: Size | None = None
    dpi: int = 300
    bbox: Bbox = Bbox.TIGHT

    @property
    def requires_latex(self) -> bool:
        """Whether writing this target needs a LaTeX installation."""
        return self.format is Format.PGF

    def filename(self, name: str) -> str:
        """Name the file this target writes for a figure.

        Args:
            name: Name of the figure.

        Returns:
            The file name, with the format's extension.
        """
        return f"{name}.{self.format.value}"


def pgf(width: float, aspect: float = 6 / 8, dpi: int = 300) -> Target:
    """Build a PGF target exactly `width` inches wide, such as a LaTeX text width.

    Args:
        width: Width of the PGF, in inches.
        aspect: Height divided by width.
        dpi: Resolution of the raster elements embedded in the PGF.

    Returns:
        The PGF target, with standard margins so it keeps its width.
    """
    return Target(Format.PGF, Size.from_width(width, aspect), dpi, bbox=Bbox.STANDARD)


def ieee_pgf(scale: float = 1.0, aspect: float = 6 / 8, dpi: int = 300) -> Target:
    """Build a PGF target sized to a fraction of an IEEE column.

    Args:
        scale: Fraction of the column width the figure spans.
        aspect: Height divided by width.
        dpi: Resolution of the raster elements embedded in the PGF.

    Returns:
        The PGF target.
    """
    return pgf(IEEE_COLUMN_WIDTH_IN * scale, aspect, dpi)


IEEE_PGF = ieee_pgf()
SCREEN = Target(Format.SVG, dpi=100)
