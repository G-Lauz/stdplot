from __future__ import annotations

import dataclasses
import typing

import matplotlib
import pytest

from stdplot.application.session import session
from stdplot.domain.config import Config, PlotRequest
from stdplot.domain.errors import LatexNotFoundError, UnknownStyleError
from stdplot.domain.style import Style
from stdplot.domain.target import IEEE_PGF

if typing.TYPE_CHECKING:
    import pathlib

    from matplotlib.figure import Figure

    from stdplot.application.environment import Environment


class RecordingDisplayer:
    def __init__(self) -> None:
        self.shown: list[tuple[Figure, str]] = []

    def show(self, figure: Figure, title: str) -> None:
        self.shown.append((figure, title))


@pytest.fixture
def recording_displayer() -> RecordingDisplayer:
    return RecordingDisplayer()


def make_request(config: Config, *, save: bool = False, show: bool = False) -> PlotRequest:
    return PlotRequest(config, "figure", 1, 1, save=save, show=show)


def test_session_without_latex_uses_no_latex_style(
    recording_displayer: RecordingDisplayer, headless_environment: Environment
) -> None:
    request = make_request(Config())

    with (
        pytest.warns(UserWarning, match="LaTeX is not installed"),
        session(request, recording_displayer, headless_environment),
    ):
        usetex = matplotlib.rcParams["text.usetex"]

    assert usetex is False


def test_session_without_latex_warns(
    recording_displayer: RecordingDisplayer, headless_environment: Environment
) -> None:
    request = make_request(Config())

    with (
        pytest.warns(UserWarning, match="mathtext"),
        session(request, recording_displayer, headless_environment),
    ):
        pass


def test_session_with_latex_keeps_usetex(
    recording_displayer: RecordingDisplayer, latex_environment: Environment
) -> None:
    with session(make_request(Config()), recording_displayer, latex_environment):
        usetex = matplotlib.rcParams["text.usetex"]

    assert usetex is True


def test_session_pgf_target_without_latex_raises(
    tmp_path: pathlib.Path,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = make_request(Config(targets=(IEEE_PGF,), output_dir=tmp_path), save=True)

    with (
        pytest.raises(LatexNotFoundError),
        session(request, recording_displayer, headless_environment),
    ):
        pass


def test_session_unknown_style_raises(
    recording_displayer: RecordingDisplayer, latex_environment: Environment
) -> None:
    request = make_request(Config(style=Style(names=("not-a-style",))))

    with (
        pytest.raises(UnknownStyleError, match="not-a-style"),
        session(request, recording_displayer, latex_environment),
    ):
        pass


def test_session_restores_rcparams_after_exit(
    recording_displayer: RecordingDisplayer, latex_environment: Environment
) -> None:
    before = (matplotlib.rcParams["text.usetex"], matplotlib.rcParams["figure.dpi"])

    with session(make_request(Config()), recording_displayer, latex_environment):
        pass

    assert (matplotlib.rcParams["text.usetex"], matplotlib.rcParams["figure.dpi"]) == before


def test_session_figure_uses_preview_size_and_dpi(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    preview = svg_png_config.preview

    with session(make_request(svg_png_config), recording_displayer, headless_environment) as (
        figure,
        _,
    ):
        assert tuple(figure.get_size_inches()) == preview.size.as_tuple()
        assert figure.dpi == preview.dpi


def test_session_grid_has_requested_shape(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = dataclasses.replace(make_request(svg_png_config), nrows=2, ncols=3)

    with session(request, recording_displayer, headless_environment) as (_, grid):
        assert grid.shape == (2, 3)


def test_session_save_writes_every_target(
    tmp_path: pathlib.Path,
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = make_request(svg_png_config, save=True)

    with session(request, recording_displayer, headless_environment) as (_, grid):
        grid.single.plot([1, 2, 3])

    assert sorted(path.name for path in tmp_path.iterdir()) == ["figure.png", "figure.svg"]


def test_session_show_calls_displayer(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = make_request(svg_png_config, show=True)

    with session(request, recording_displayer, headless_environment) as (figure, _):
        pass

    assert recording_displayer.shown == [(figure, "figure")]


def test_session_without_show_skips_displayer(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    with session(make_request(svg_png_config), recording_displayer, headless_environment):
        pass

    assert recording_displayer.shown == []


def test_session_body_error_skips_export(
    tmp_path: pathlib.Path,
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = make_request(svg_png_config, save=True)

    with (
        pytest.raises(RuntimeError, match="drawing failed"),
        session(request, recording_displayer, headless_environment),
    ):
        raise RuntimeError("drawing failed")

    assert list(tmp_path.iterdir()) == []


def test_session_body_error_skips_show(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = make_request(svg_png_config, show=True)

    with (
        pytest.raises(RuntimeError, match="drawing failed"),
        session(request, recording_displayer, headless_environment),
    ):
        raise RuntimeError("drawing failed")

    assert recording_displayer.shown == []
