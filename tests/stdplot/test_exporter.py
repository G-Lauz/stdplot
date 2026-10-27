from __future__ import annotations

import typing

import matplotlib.image
from matplotlib.figure import Figure

from stdplot.application.exporter import export
from stdplot.domain.format import Format
from stdplot.domain.target import Size, Target

if typing.TYPE_CHECKING:
    import pathlib

SIZE = Size(4.0, 3.0)
SVG = Target(Format.SVG, SIZE, dpi=72)
PNG = Target(Format.PNG, SIZE, dpi=72)


def test_export_writes_one_file_per_target(tmp_path: pathlib.Path) -> None:
    paths = export(Figure(), (SVG, PNG), tmp_path, "figure")

    assert paths == (tmp_path / "figure.svg", tmp_path / "figure.png")
    assert all(path.is_file() for path in paths)


def test_export_svg_has_target_size(tmp_path: pathlib.Path) -> None:
    (path,) = export(Figure(), (SVG,), tmp_path, "figure")

    # SVG sizes are in points: 4 x 3 in is 288 x 216 pt.
    assert 'width="288pt" height="216pt"' in path.read_text()


def test_export_png_has_target_pixels(tmp_path: pathlib.Path) -> None:
    (path,) = export(Figure(), (PNG,), tmp_path, "figure")

    assert matplotlib.image.imread(path).shape[:2] == (216, 288)


def test_export_restores_figure_size(tmp_path: pathlib.Path) -> None:
    figure = Figure(figsize=(8.0, 6.0))

    export(figure, (SVG, PNG), tmp_path, "figure")

    assert tuple(figure.get_size_inches()) == (8.0, 6.0)


def test_export_creates_output_dir(tmp_path: pathlib.Path) -> None:
    output_dir = tmp_path / "nested" / "figures"

    export(Figure(), (SVG,), output_dir, "figure")

    assert output_dir.is_dir()
