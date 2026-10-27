"""Exceptions raised by stdplot."""

from __future__ import annotations


class StdplotError(Exception):
    """Base class of every error raised by stdplot."""


class LatexNotFoundError(StdplotError):
    """A target needs LaTeX, but no LaTeX installation is on the PATH."""

    def __init__(self) -> None:
        """Build the message explaining why LaTeX is needed."""
        super().__init__(
            "A PGF target needs a LaTeX installation, but `latex` is not on the PATH. "
            "Install a TeX distribution or remove the PGF targets from the config."
        )


class MissingOutputError(StdplotError, ValueError):
    """Saving was requested, but the config does not say where or as what."""

    def __init__(self, missing: str) -> None:
        """Build the message naming the missing setting.

        Args:
            missing: What the config lacks, such as "an output_dir".
        """
        super().__init__(f"Saving a figure needs {missing} in the config.")


class MissingDependencyError(StdplotError, ImportError):
    """A feature needs an optional dependency that is not installed."""

    def __init__(self, extra: str) -> None:
        """Build the message naming the extra to install.

        Args:
            extra: Name of the stdplot extra providing the dependency, such as "qt".
        """
        super().__init__(
            f'This feature needs an optional dependency: pip install "stdplot[{extra}]"'
        )
        self.extra = extra


class UnknownStyleError(StdplotError):
    """A style name is not registered with matplotlib."""

    def __init__(self, names: tuple[str, ...]) -> None:
        """Build the message listing the unknown styles.

        Args:
            names: The style names matplotlib does not know.
        """
        super().__init__(
            f"Unknown matplotlib style(s): {', '.join(names)}. "
            "See matplotlib.style.available for the registered names."
        )
        self.names = names
