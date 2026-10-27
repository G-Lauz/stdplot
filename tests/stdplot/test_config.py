from __future__ import annotations

import typing

import pytest

from stdplot.domain.config import Config, PlotRequest
from stdplot.domain.errors import MissingOutputError
from stdplot.domain.format import Format
from stdplot.domain.target import IEEE_PGF, Size, Target

if typing.TYPE_CHECKING:
    import pathlib

SVG = Target(Format.SVG, Size(4.0, 3.0))


def make_request(
    config: Config, *, nrows: int = 1, ncols: int = 1, save: bool = False
) -> PlotRequest:
    return PlotRequest(config, "figure", nrows, ncols, save=save, show=False)


def test_plot_request_save_without_output_dir_raises() -> None:
    with pytest.raises(MissingOutputError, match="output_dir"):
        make_request(Config(), save=True)


def test_plot_request_missing_output_is_value_error() -> None:
    with pytest.raises(ValueError, match="output_dir"):
        make_request(Config(), save=True)


def test_plot_request_save_without_targets_raises(tmp_path: pathlib.Path) -> None:
    with pytest.raises(MissingOutputError, match="target"):
        make_request(Config(output_dir=tmp_path, targets=()), save=True)


def test_plot_request_without_save_needs_no_output_dir() -> None:
    assert make_request(Config(), save=False).save is False


def test_plot_request_empty_name_raises() -> None:
    with pytest.raises(ValueError, match="name"):
        PlotRequest(Config(), "", 1, 1, save=False, show=False)


@pytest.mark.parametrize(("nrows", "ncols"), [(0, 1), (1, 0)])
def test_plot_request_empty_grid_raises(nrows: int, ncols: int) -> None:
    with pytest.raises(ValueError, match="1x1"):
        make_request(Config(), nrows=nrows, ncols=ncols)


def test_plot_request_output_dir_without_config_dir_raises() -> None:
    with pytest.raises(MissingOutputError, match="output_dir"):
        _ = make_request(Config()).output_dir


def test_plot_request_needs_latex_when_saving_pgf(tmp_path: pathlib.Path) -> None:
    config = Config(output_dir=tmp_path, targets=(IEEE_PGF, SVG))

    assert make_request(config, save=True).needs_latex is True


def test_plot_request_needs_no_latex_without_pgf(tmp_path: pathlib.Path) -> None:
    config = Config(output_dir=tmp_path, targets=(SVG,))

    assert make_request(config, save=True).needs_latex is False


def test_plot_request_needs_no_latex_without_save() -> None:
    assert make_request(Config(targets=(IEEE_PGF,))).needs_latex is False
