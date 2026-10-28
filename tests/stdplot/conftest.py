from __future__ import annotations

import typing

import pytest

from stdplot.application.environment import Environment
from stdplot.domain.config import Config
from stdplot.domain.format import Format
from stdplot.domain.style import LatexSettings, Style
from stdplot.domain.target import Size, Target

if typing.TYPE_CHECKING:
    import pathlib


@pytest.fixture
def headless_environment() -> Environment:
    return Environment(latex_available=False, in_notebook=False, headless=True)


@pytest.fixture
def latex_environment() -> Environment:
    return Environment(latex_available=True, in_notebook=False, headless=True)


@pytest.fixture
def svg_png_config(tmp_path: pathlib.Path) -> Config:
    size = Size(4.0, 3.0)
    return Config(
        # Without usetex, drawing never calls a TeX binary, whatever the machine has.
        style=Style(latex=LatexSettings(usetex=False)),
        targets=(Target(Format.SVG, size, dpi=72), Target(Format.PNG, size, dpi=72)),
        output_dir=tmp_path,
    )
