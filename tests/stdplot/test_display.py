from __future__ import annotations

import importlib.util
import subprocess
import sys

import pytest
from matplotlib.figure import Figure

from stdplot.application.environment import Environment
from stdplot.domain.errors import MissingDependencyError
from stdplot.domain.format import Display
from stdplot.domain.target import SCREEN
from stdplot.presentation.display import select_displayer
from stdplot.presentation.display.notebook import NotebookDisplayer
from stdplot.presentation.display.null import NullDisplayer
from stdplot.presentation.display.qt import QtDisplayer

IN_NOTEBOOK = Environment(latex_available=False, in_notebook=True, headless=False)
HEADLESS_NOTEBOOK = Environment(latex_available=False, in_notebook=True, headless=True)
WITH_WINDOWS = Environment(latex_available=False, in_notebook=False, headless=False)
HEADLESS = Environment(latex_available=False, in_notebook=False, headless=True)

QT_BINDINGS = ("PySide6", "PyQt6", "PyQt5", "PySide2")
HAS_QT_BINDING = any(importlib.util.find_spec(name) is not None for name in QT_BINDINGS)
HAS_IPYTHON = importlib.util.find_spec("IPython") is not None


def test_select_displayer_auto_in_notebook_returns_notebook() -> None:
    displayer = select_displayer(Display.AUTO, IN_NOTEBOOK, SCREEN)

    assert displayer == NotebookDisplayer(SCREEN)


def test_select_displayer_auto_in_headless_notebook_returns_notebook() -> None:
    displayer = select_displayer(Display.AUTO, HEADLESS_NOTEBOOK, SCREEN)

    assert displayer == NotebookDisplayer(SCREEN)


def test_select_displayer_auto_headless_returns_null() -> None:
    assert isinstance(select_displayer(Display.AUTO, HEADLESS, SCREEN), NullDisplayer)


def test_select_displayer_auto_with_windows_returns_qt() -> None:
    assert isinstance(select_displayer(Display.AUTO, WITH_WINDOWS, SCREEN), QtDisplayer)


def test_select_displayer_none_returns_null() -> None:
    assert isinstance(select_displayer(Display.NONE, IN_NOTEBOOK, SCREEN), NullDisplayer)


def test_select_displayer_explicit_qt_in_notebook_returns_qt() -> None:
    assert isinstance(select_displayer(Display.QT, IN_NOTEBOOK, SCREEN), QtDisplayer)


def test_select_displayer_explicit_qt_headless_returns_qt() -> None:
    assert isinstance(select_displayer(Display.QT, HEADLESS, SCREEN), QtDisplayer)


def test_select_displayer_explicit_notebook_outside_notebook_returns_notebook() -> None:
    displayer = select_displayer(Display.NOTEBOOK, WITH_WINDOWS, SCREEN)

    assert displayer == NotebookDisplayer(SCREEN)


def test_import_loads_no_qt() -> None:
    # Loading a Qt binding with stdplot pins its C++ runtime on Windows, which breaks a
    # later `import jax`; a fresh interpreter shows what `import stdplot` alone loads.
    code = (
        "import sys, stdplot; "
        "print(*[name for name in sys.modules if name.startswith(('PySide', 'PyQt'))])"
    )

    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == ""


@pytest.mark.skipif(HAS_QT_BINDING, reason="a Qt binding is installed")
def test_qt_displayer_without_binding_raises() -> None:
    with pytest.raises(MissingDependencyError, match=r"stdplot\[qt\]"):
        QtDisplayer().show(Figure(), "figure")


@pytest.mark.skipif(HAS_IPYTHON, reason="IPython is installed")
def test_notebook_displayer_without_ipython_raises() -> None:
    with pytest.raises(MissingDependencyError, match=r"stdplot\[notebook\]"):
        NotebookDisplayer(SCREEN).show(Figure(), "figure")


@pytest.mark.skipif(not HAS_IPYTHON, reason="IPython is not installed")
def test_notebook_displayer_displays_svg(capsys: pytest.CaptureFixture[str]) -> None:
    NotebookDisplayer(SCREEN).show(Figure(), "figure")

    # Outside a kernel, IPython's display() prints the repr of what it was given.
    assert "SVG object" in capsys.readouterr().out
