"""A display that shows nothing, for scripts and headless runs."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from matplotlib.figure import Figure


class NullDisplayer:
    """Shows nothing, so a script never blocks on a window."""

    def show(self, figure: Figure, title: str) -> None:
        """Do nothing.

        Args:
            figure: Unused.
            title: Unused.
        """
