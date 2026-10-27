from __future__ import annotations

import pytest
from matplotlib.figure import Figure

from stdplot.application.environment import Environment
from stdplot.domain.errors import MissingDependencyError
from stdplot.domain.format import Display
from stdplot.domain.target import SCREEN
from stdplot.presentation.display import notebook, qt, select_displayer
from stdplot.presentation.display.notebook import NotebookDisplayer
from stdplot.presentation.display.qt import QtDisplayer

IN_NOTEBOOK = Environment(latex_available=False, in_notebook=True)
OUTSIDE_NOTEBOOK = Environment(latex_available=False, in_notebook=False)


def test_select_displayer_auto_in_notebook_returns_notebook() -> None:
    displayer = select_displayer(Display.AUTO, IN_NOTEBOOK, SCREEN)

    assert displayer == NotebookDisplayer(SCREEN)


def test_select_displayer_auto_outside_notebook_returns_qt() -> None:
    assert isinstance(select_displayer(Display.AUTO, OUTSIDE_NOTEBOOK, SCREEN), QtDisplayer)


def test_select_displayer_explicit_qt_in_notebook_returns_qt() -> None:
    assert isinstance(select_displayer(Display.QT, IN_NOTEBOOK, SCREEN), QtDisplayer)


def test_select_displayer_explicit_notebook_outside_notebook_returns_notebook() -> None:
    displayer = select_displayer(Display.NOTEBOOK, OUTSIDE_NOTEBOOK, SCREEN)

    assert displayer == NotebookDisplayer(SCREEN)


@pytest.mark.skipif(qt.backend_qtagg is not None, reason="a Qt binding is installed")
def test_qt_displayer_without_binding_raises() -> None:
    with pytest.raises(MissingDependencyError, match=r"stdplot\[qt\]"):
        QtDisplayer().show(Figure(), "figure")


@pytest.mark.skipif(notebook.IPython is not None, reason="IPython is installed")
def test_notebook_displayer_without_ipython_raises() -> None:
    with pytest.raises(MissingDependencyError, match=r"stdplot\[notebook\]"):
        NotebookDisplayer(SCREEN).show(Figure(), "figure")


@pytest.mark.skipif(notebook.IPython is None, reason="IPython is not installed")
def test_notebook_displayer_displays_svg(capsys: pytest.CaptureFixture[str]) -> None:
    NotebookDisplayer(SCREEN).show(Figure(), "figure")

    # Outside a kernel, IPython's display() prints the repr of what it was given.
    assert "SVG object" in capsys.readouterr().out
