from __future__ import annotations

import dataclasses
import typing
import warnings

import matplotlib
import pytest
from matplotlib.layout_engine import TightLayoutEngine

from stdplot.application.session import _warn_latex_missing, session
from stdplot.domain.config import Config, PlotRequest
from stdplot.domain.errors import LatexNotFoundError, UnknownStyleError
from stdplot.domain.style import LatexSettings, Style
from stdplot.domain.target import IEEE_PGF, Size

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


@pytest.fixture(autouse=True)
def fresh_latex_warning() -> None:
    # The warning fires once per process; each test starts as if none had fired yet.
    _warn_latex_missing.cache_clear()


def make_request(config: Config, *, save: bool = False, show: bool = False) -> PlotRequest:
    return PlotRequest(config, "figure", 1, 1, save=save, show=show, size=config.size)


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


def test_session_without_latex_warns_once(
    recording_displayer: RecordingDisplayer, headless_environment: Environment
) -> None:
    request = make_request(Config())

    with warnings.catch_warnings(record=True) as record:
        # "always" would repeat an uncached warning at every figure.
        warnings.simplefilter("always")
        for _ in range(2):
            with session(request, recording_displayer, headless_environment):
                pass

    assert len([warning for warning in record if "mathtext" in str(warning.message)]) == 1


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
        pytest.raises(LatexNotFoundError, match="pdflatex"),
        session(request, recording_displayer, headless_environment),
    ):
        pass


def test_session_latex_error_names_configured_texsystem(
    tmp_path: pathlib.Path,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    style = Style(latex=LatexSettings(texsystem="xelatex"))
    config = Config(style=style, targets=(IEEE_PGF,), output_dir=tmp_path)

    with (
        pytest.raises(LatexNotFoundError, match="xelatex"),
        session(make_request(config, save=True), recording_displayer, headless_environment),
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


def test_session_figure_uses_request_size_and_preview_dpi(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = dataclasses.replace(make_request(svg_png_config), size=Size(5.0, 2.0))

    with session(request, recording_displayer, headless_environment) as (figure, _):
        assert tuple(figure.get_size_inches()) == (5.0, 2.0)
        assert figure.dpi == svg_png_config.preview.dpi


def test_session_forwards_subplots_kw(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    request = dataclasses.replace(
        make_request(svg_png_config), nrows=2, subplots_kw={"sharex": True}
    )

    with session(request, recording_displayer, headless_environment) as (_, grid):
        assert grid[0].get_shared_x_axes().joined(grid[0], grid[1])


def test_session_tight_layout_in_block_restores_layout_engine(
    svg_png_config: Config,
    recording_displayer: RecordingDisplayer,
    headless_environment: Environment,
) -> None:
    with session(make_request(svg_png_config), recording_displayer, headless_environment) as (
        figure,
        _,
    ):
        figure.tight_layout()

    assert isinstance(figure.get_layout_engine(), TightLayoutEngine)


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
