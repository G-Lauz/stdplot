from __future__ import annotations

from stdplot.application.environment import detect


def test_detect_outside_kernel_is_not_in_notebook() -> None:
    assert detect().in_notebook is False
