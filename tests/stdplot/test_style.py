from __future__ import annotations

from stdplot.domain.style import NO_LATEX_STYLE, LatexSettings, Style


def test_latex_settings_to_rc_uses_standard_bbox() -> None:
    assert LatexSettings().to_rc()["savefig.bbox"] == "standard"


def test_latex_settings_to_rc_maps_usetex() -> None:
    assert LatexSettings(usetex=False).to_rc()["text.usetex"] is False


def test_style_without_latex_appends_no_latex() -> None:
    style = Style(names=("science",))

    assert style.without_latex().names == ("science", NO_LATEX_STYLE)


def test_style_without_latex_disables_usetex() -> None:
    assert Style().without_latex().latex.usetex is False


def test_style_to_rc_list_puts_latex_overrides_last() -> None:
    style = Style(names=("science", "grid"))

    assert style.to_rc_list() == ["science", "grid", style.latex.to_rc()]
