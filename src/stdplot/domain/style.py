"""The visual style applied while a figure is drawn."""

from __future__ import annotations

import dataclasses

NO_LATEX_STYLE = "no-latex"


@dataclasses.dataclass(frozen=True)
class LatexSettings:
    """LaTeX rendering settings, applied on top of the named styles."""

    texsystem: str = "pdflatex"
    font_family: str = "serif"
    usetex: bool = True
    rcfonts: bool = False

    def to_rc(self) -> dict[str, object]:
        """Translate the settings to matplotlib rcParams."""
        return {
            "pgf.texsystem": self.texsystem,
            "font.family": self.font_family,
            "text.usetex": self.usetex,
            "pgf.rcfonts": self.rcfonts,
            # The science style crops exports to a tight bbox, which would make a PGF
            # narrower than the width its target was sized to fit.
            "savefig.bbox": "standard",
        }


@dataclasses.dataclass(frozen=True)
class Style:
    """Named matplotlib styles plus the LaTeX settings layered over them."""

    names: tuple[str, ...] = ("science", "grid", "ieee")
    latex: LatexSettings = LatexSettings()

    def without_latex(self) -> Style:
        """Return a copy that renders text with matplotlib's mathtext instead of LaTeX."""
        return dataclasses.replace(
            self,
            names=(*self.names, NO_LATEX_STYLE),
            latex=dataclasses.replace(self.latex, usetex=False),
        )

    def to_rc_list(self) -> list[str | dict[str, object]]:
        """Return the style in the form `matplotlib.style.context` accepts."""
        return [*self.names, self.latex.to_rc()]
