"""Configuration of how figures are drawn, exported and shown."""

from __future__ import annotations

import dataclasses
import pathlib

from .errors import MissingOutputError
from .format import Display, Layout
from .style import Style
from .subplots import SubplotOptions
from .target import IEEE_PGF, SCREEN, Size, Target

DEFAULT_SIZE = Size(8.0, 6.0)


@dataclasses.dataclass(frozen=True)
class Config:
    """Settings shared by every figure drawn with it.

    Attributes:
        style: Style applied while the figure is drawn.
        targets: Files written when saving.
        preview: Format, dpi and optional size of the inline preview.
        output_dir: Directory the targets are written to; required when saving. A string
            is converted to a path.
        layout: Layout engine re-run before every export.
        display: Where a shown figure appears.
        size: Size the figure is drawn at; targets without a size are written at it.
    """

    style: Style = dataclasses.field(default_factory=Style)
    targets: tuple[Target, ...] = (IEEE_PGF, SCREEN)
    preview: Target = SCREEN
    output_dir: pathlib.Path | str | None = None
    layout: Layout = Layout.TIGHT
    display: Display = Display.AUTO
    size: Size = DEFAULT_SIZE

    def __post_init__(self) -> None:
        """Convert a string output directory to a path, so saving does not fail on it."""
        if isinstance(self.output_dir, str):
            # The dataclass is frozen, so its own __setattr__ refuses the assignment.
            object.__setattr__(self, "output_dir", pathlib.Path(self.output_dir))

    def paths(self, name: str) -> tuple[pathlib.Path, ...]:
        """Name the files saving a figure writes.

        Args:
            name: Name of the figure.

        Returns:
            One path in the output directory per target, in the order of the targets.

        Raises:
            MissingOutputError: The config has no output directory.
        """
        if self.output_dir is None:
            raise MissingOutputError("an output_dir")
        output_dir = pathlib.Path(self.output_dir)
        return tuple(output_dir / target.filename(name) for target in self.targets)


@dataclasses.dataclass(frozen=True)
class PlotRequest:
    """One figure to draw: its config, name, axes grid and what happens once it is drawn.

    Attributes:
        config: Settings of the figure.
        name: Name of the figure, used as the file stem and the window title.
        nrows: Number of rows of axes.
        ncols: Number of columns of axes.
        save: Write the figure to every target of the config once drawn.
        show: Display the figure once drawn.
        size: Size the figure is drawn at.
        subplots_kw: Options of the grid of axes, such as `sharex`.
    """

    config: Config
    name: str
    nrows: int
    ncols: int
    save: bool
    show: bool
    size: Size
    subplots_kw: SubplotOptions = dataclasses.field(default_factory=SubplotOptions)

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
    def needs_latex(self) -> bool:
        """Whether drawing this request needs a LaTeX installation."""
        return self.save and any(target.requires_latex for target in self.config.targets)
