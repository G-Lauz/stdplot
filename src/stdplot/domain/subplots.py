"""Options of the grid of axes, forwarded to matplotlib's `Figure.subplots`."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import collections.abc


class SubplotOptions(typing.TypedDict, total=False):
    """Keyword arguments of `Figure.subplots` that a figure call forwards.

    Typed one by one, rather than as opaque keywords, so a type checker rejects a
    misspelled or removed argument at the call site instead of matplotlib at runtime.

    Attributes:
        sharex: Share the x axis between the axes, or within each row or column.
        sharey: Share the y axis between the axes, or within each row or column.
        width_ratios: Relative widths of the columns.
        height_ratios: Relative heights of the rows.
        subplot_kw: Keyword arguments of every axes, such as `{"projection": "3d"}`.
        gridspec_kw: Keyword arguments of the `GridSpec` laying out the axes.
    """

    sharex: bool | typing.Literal["none", "all", "row", "col"]
    sharey: bool | typing.Literal["none", "all", "row", "col"]
    width_ratios: collections.abc.Sequence[float] | None
    height_ratios: collections.abc.Sequence[float] | None
    subplot_kw: dict[str, typing.Any] | None
    gridspec_kw: dict[str, typing.Any] | None
