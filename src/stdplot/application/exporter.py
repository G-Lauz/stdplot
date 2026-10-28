"""Export of a figure to its targets."""

from __future__ import annotations

import typing

import matplotlib

if typing.TYPE_CHECKING:
    import pathlib

    from matplotlib.figure import Figure

    from stdplot.domain.config import Config
    from stdplot.domain.target import Target


def export(figure: Figure, config: Config, name: str) -> tuple[pathlib.Path, ...]:
    """Write the figure once per target of the config, in its output directory.

    Args:
        figure: Figure to export.
        config: Targets and output directory, created when missing.
        name: Name of the figure, used as the file stem.

    Returns:
        The written paths, in the order of the targets.

    Raises:
        MissingOutputError: The config has no output directory.
    """
    paths = config.paths(name)
    for target, path in zip(config.targets, paths, strict=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        write(figure, target, path)
    return paths


def write(figure: Figure, target: Target, destination: pathlib.Path | typing.BinaryIO) -> None:
    """Write the figure once, at the target's size, format, dpi and margins.

    The figure gets its size back afterwards, so writing does not change what is
    shown next.

    Args:
        figure: Figure to write.
        target: Format, size, dpi and margins of the output.
        destination: File path or binary stream written to.
    """
    width, height = figure.get_size_inches()
    size = target.size
    try:
        if size is not None:
            figure.set_size_inches(size.as_tuple())
        # savefig rejects bbox_inches="standard", but the rcParam takes both values.
        with matplotlib.rc_context({"savefig.bbox": target.bbox.value}):
            figure.savefig(destination, format=target.format.value, dpi=target.dpi)
    finally:
        figure.set_size_inches(width, height)
