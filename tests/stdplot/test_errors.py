from __future__ import annotations

import pytest

from stdplot.domain.errors import (
    LatexNotFoundError,
    MissingDependencyError,
    MissingOutputError,
    StdplotError,
    UnknownStyleError,
)


@pytest.mark.parametrize(
    "error",
    [
        LatexNotFoundError("pdflatex"),
        MissingOutputError("an output_dir"),
        MissingDependencyError("qt"),
        UnknownStyleError(("missing",)),
    ],
)
def test_error_is_stdplot_error(error: Exception) -> None:
    assert isinstance(error, StdplotError)


def test_missing_output_error_is_value_error() -> None:
    assert isinstance(MissingOutputError("an output_dir"), ValueError)


def test_missing_dependency_error_is_import_error() -> None:
    assert isinstance(MissingDependencyError("qt"), ImportError)


def test_missing_dependency_error_names_extra() -> None:
    assert 'pip install "stdplot[notebook]"' in str(MissingDependencyError("notebook"))


def test_latex_not_found_error_names_texsystem() -> None:
    assert "`xelatex` is not on the PATH" in str(LatexNotFoundError("xelatex"))


def test_latex_not_found_error_suggests_screen_target() -> None:
    assert "targets=(stdplot.SCREEN,)" in str(LatexNotFoundError("pdflatex"))


def test_unknown_style_error_lists_names() -> None:
    message = str(UnknownStyleError(("first", "second")))

    assert "first, second" in message
