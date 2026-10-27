"""Configuration of how figures are drawn, exported and shown."""

from __future__ import annotations

import dataclasses
import typing

from .errors import MissingOutputError
from .format import Display, Layout
from .style import Style
from .target import IEEE_PGF, SCREEN, Target

if typing.TYPE_CHECKING:
    import pathlib


@dataclasses.dataclass(frozen=True)
class Config:
    """Settings shared by every figure drawn with it.

    Attributes:
        style: Style applied while the figure is drawn.
        targets: Files written when saving.
        preview: Size, resolution and format the figure is drawn and shown at.
        output_dir: Directory the targets are written to; required when saving.
        layout: Layout engine re-run before every export.
        display: Where a shown figure appears.
    """

    style: Style = dataclasses.field(default_factory=Style)
    targets: tuple[Target, ...] = (IEEE_PGF, SCREEN)
    preview: Target = SCREEN
    output_dir: pathlib.Path | None = None
    layout: Layout = Layout.TIGHT
    display: Display = Display.AUTO


@dataclasses.dataclass(frozen=True)
class PlotRequest:
    """One figure to draw: its config, name, axes grid and what happens once it is drawn."""

    config: Config
    name: str
    nrows: int
    ncols: int
    save: bool
    show: bool

    def __post_init__(self) -> None:
        """Reject requests that cannot be drawn or saved.

        Raises:
            ValueError: The name is empty or the grid has fewer than one row or column.
            MissingOutputError: Saving without an output directory or without targets.
        """
        has_name = bool(self.name)
        if not has_name:
            raise ValueError("A figure needs a non-empty name.")

        has_axes = self.nrows >= 1 and self.ncols >= 1
        if not has_axes:
            raise ValueError(f"A figure needs at least 1x1 axes, got {self.nrows}x{self.ncols}.")

        if self.save and self.config.output_dir is None:
            raise MissingOutputError("an output_dir")
        if self.save and not self.config.targets:
            raise MissingOutputError("at least one target")

    @property
    def output_dir(self) -> pathlib.Path:
        """Directory the targets are written to.

        Raises:
            MissingOutputError: The config has no output directory.
        """
        output_dir = self.config.output_dir
        if output_dir is None:
            raise MissingOutputError("an output_dir")
        return output_dir

    @property
    def needs_latex(self) -> bool:
        """Whether drawing this request needs a LaTeX installation."""
        return self.save and any(target.requires_latex for target in self.config.targets)
