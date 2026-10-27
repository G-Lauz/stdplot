from __future__ import annotations

import pytest

from stdplot.domain.format import Format
from stdplot.domain.target import IEEE_COLUMN_WIDTH_IN, IEEE_PGF, Size, Target, ieee_pgf


@pytest.mark.parametrize(("width", "height"), [(0.0, 1.0), (1.0, 0.0), (-1.0, 1.0)])
def test_size_non_positive_raises(width: float, height: float) -> None:
    with pytest.raises(ValueError, match="positive"):
        Size(width, height)


def test_size_from_width_applies_aspect() -> None:
    assert Size.from_width(4.0, 0.5) == Size(4.0, 2.0)


def test_size_as_tuple_is_width_then_height() -> None:
    assert Size(4.0, 3.0).as_tuple() == (4.0, 3.0)


def test_ieee_pgf_scales_column_width() -> None:
    target = ieee_pgf(scale=0.5, aspect=1.0)

    assert target.size == Size(IEEE_COLUMN_WIDTH_IN / 2, IEEE_COLUMN_WIDTH_IN / 2)


def test_ieee_pgf_default_spans_column() -> None:
    assert IEEE_PGF.format is Format.PGF
    assert IEEE_PGF.size.width == IEEE_COLUMN_WIDTH_IN


@pytest.mark.parametrize("file_format", list(Format))
def test_target_requires_latex_only_for_pgf(file_format: Format) -> None:
    target = Target(file_format, Size(1.0, 1.0))

    assert target.requires_latex == (file_format is Format.PGF)


def test_target_filename_uses_format_extension() -> None:
    assert Target(Format.PNG, Size(1.0, 1.0)).filename("loss") == "loss.png"
