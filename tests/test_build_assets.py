"""Checks on how the asset build works out where things may go in a panel."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

import build_assets  # noqa: E402


def open_at(rows, x, y):
    """Whether art pixel (x, y) is open, from grid rows."""
    gx, gy = x * build_assets.GRID_SCALE, y * build_assets.GRID_SCALE
    return any(a <= gx < b for a, b in rows[int(gy)])


def test_space_enclosed_by_the_art_is_not_open():
    # A ring of ink (a face, say) in a blank panel.
    ink = np.zeros((100, 100), dtype=bool)
    yy, xx = np.mgrid[:100, :100]
    r = np.hypot(xx - 50, yy - 40)
    ink[(r > 20) & (r < 24)] = True
    rows = build_assets.open_rows(ink)
    assert open_at(rows, 10, 10), "outside the ring"
    assert not open_at(rows, 50, 40), "inside the ring"


def test_space_reaching_only_the_bottom_edge_is_not_open():
    # A figure cut off by the bottom of the panel: its inside (a shirt and
    # face) reaches the bottom edge but nothing else.
    ink = np.zeros((100, 100), dtype=bool)
    ink[30:, 30:33] = True
    ink[30:, 67:70] = True
    ink[30:33, 30:70] = True
    rows = build_assets.open_rows(ink)
    assert open_at(rows, 10, 50), "beside the figure"
    assert not open_at(rows, 50, 60), "inside the figure"


def test_space_behind_a_small_gap_in_the_art_is_not_open():
    # A ring with a small gap in it, as hand-inked outlines often have.
    ink = np.zeros((100, 100), dtype=bool)
    yy, xx = np.mgrid[:100, :100]
    r = np.hypot(xx - 50, yy - 40)
    ink[(r > 20) & (r < 24)] = True
    ink[34:46, 66:80] = False
    rows = build_assets.open_rows(ink)
    assert open_at(rows, 10, 10), "outside the ring"
    assert not open_at(rows, 50, 40), "inside the ring"
