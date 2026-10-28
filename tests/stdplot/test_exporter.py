from __future__ import annotations

import io
import re
import typing

import matplotlib.image
from matplotlib.figure import Figure

from stdplot.application.exporter import export, write
from stdplot.domain.config import Config
from stdplot.domain.format import Bbox, Format
from stdplot.domain.target import Size, Target

if typing.TYPE_CHECKING:
    import pathlib

SIZE = Size(4.0, 3.0)
# Standard margins keep the written size exactly the target's size.
SVG = Target(Format.SVG, SIZE, dpi=72, bbox=Bbox.STANDARD)
PNG = Target(Format.PNG, SIZE, dpi=72, bbox=Bbox.STANDARD)


def svg_width_pt(data: str) -> float:
    match = re.search(r'width="([\d.]+)pt"', data)
    assert match is not None
    return float(match.group(1))


def write_svg(figure: Figure, target: Target) -> str:
    buffer = io.BytesIO()
    write(figure, target, buffer)
    return buffer.getvalue().decode()


def test_write_to_stream_writes_target_format() -> None:
    buffer = io.BytesIO()

    write(Figure(), PNG, buffer)

    assert buffer.getvalue().startswith(b"\x89PNG")


def test_write_sizeless_target_uses_figure_size() -> None:
    figure = Figure(figsize=(5.0, 2.0))

    data = write_svg(figure, Target(Format.SVG, dpi=72, bbox=Bbox.STANDARD))

    # SVG sizes are in points: 5 x 2 in is 360 x 144 pt.
    assert 'width="360pt" height="144pt"' in data
    assert tuple(figure.get_size_inches()) == (5.0, 2.0)


def test_write_tight_bbox_crops_margins() -> None:
    figure = Figure(figsize=SIZE.as_tuple())
    figure.subplots().plot([1, 2, 3])

    data = write_svg(figure, Target(Format.SVG, SIZE, dpi=72, bbox=Bbox.TIGHT))

    assert svg_width_pt(data) < 288


def test_write_standard_bbox_keeps_target_width() -> None:
    figure = Figure(figsize=SIZE.as_tuple())
    figure.subplots().plot([1, 2, 3])

    assert svg_width_pt(write_svg(figure, SVG)) == 288


def test_export_writes_one_file_per_target(tmp_path: pathlib.Path) -> None:
    config = Config(targets=(SVG, PNG), output_dir=tmp_path)

    paths = export(Figure(), config, "figure")

    assert paths == config.paths("figure")
    assert all(path.is_file() for path in paths)


def test_export_svg_has_target_size(tmp_path: pathlib.Path) -> None:
    (path,) = export(Figure(), Config(targets=(SVG,), output_dir=tmp_path), "figure")

    # SVG sizes are in points: 4 x 3 in is 288 x 216 pt.
    assert 'width="288pt" height="216pt"' in path.read_text()


def test_export_png_has_target_pixels(tmp_path: pathlib.Path) -> None:
    (path,) = export(Figure(), Config(targets=(PNG,), output_dir=tmp_path), "figure")

    assert matplotlib.image.imread(path).shape[:2] == (216, 288)


def test_export_restores_figure_size(tmp_path: pathlib.Path) -> None:
    figure = Figure(figsize=(8.0, 6.0))

    export(figure, Config(targets=(SVG, PNG), output_dir=tmp_path), "figure")

    assert tuple(figure.get_size_inches()) == (8.0, 6.0)


def test_export_creates_output_dir(tmp_path: pathlib.Path) -> None:
    output_dir = tmp_path / "nested" / "figures"

    export(Figure(), Config(targets=(SVG,), output_dir=output_dir), "figure")

    assert output_dir.is_dir()
