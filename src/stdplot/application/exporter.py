"""Export of a figure to its targets."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import pathlib

    from matplotlib.figure import Figure

    from stdplot.domain.target import Target


def export(
    figure: Figure, targets: tuple[Target, ...], output_dir: pathlib.Path, name: str
) -> tuple[pathlib.Path, ...]:
    """Write the figure once per target, resized to each target's size.

    The figure gets its size back afterwards, so exporting does not change what is
    shown next.

    Args:
        figure: Figure to export.
        targets: Files to write.
        output_dir: Directory the files are written to; created when missing.
        name: Name of the figure, used as the file stem.

    Returns:
        The written paths, in the order of the targets.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    width, height = figure.get_size_inches()
    try:
        return tuple(
            _write(figure, target, output_dir / target.filename(name)) for target in targets
        )
    finally:
        figure.set_size_inches(width, height)


def _write(figure: Figure, target: Target, path: pathlib.Path) -> pathlib.Path:
    figure.set_size_inches(target.size.as_tuple())
    figure.savefig(path, format=target.format.value, dpi=target.dpi)
    return path
