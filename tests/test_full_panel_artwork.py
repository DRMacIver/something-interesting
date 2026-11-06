"""The reconstructed exports must preserve their independently extracted art."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/full-panels'
UNDERARM = (730, 1000, 1880, 1960)  # as in drawn_legs.UNDERARM
SEAT = (700, 1966)  # drawn_legs.panel_two redraws x < 700 below y = 1966


def test_original_overlaps_and_panel2_repair_are_preserved():
    for item in json.loads((OUT / 'verification.json').read_text()):
        number = item['panel']
        image = Image.open(OUT / f'panel{number}.png')
        source = np.asarray(Image.open(OUT / f'original{number}.png'))
        x, y = item['originalOffset']
        width, height = item['originalSize']
        overlap = np.asarray(image.crop((x, y, x + width, y + height)))
        assert image.size == tuple(item['size'])
        if number in (1, 3, 4):
            assert np.array_equal(overlap, source)
        else:
            assert np.mean(overlap == source) > 0.99
            # The prior elbow repair is retained; generation cannot redraw
            # the existing head, arms, expression or the visible record.
            # Only the line under the arm is thinned back to the scan's weight.
            approved = np.asarray(Image.open(ROOT / 'tools/extensions/reconstruction-v2/upper-2.png')).copy()
            actual = np.asarray(image.crop((400, 0, 3182, 2060))).copy()
            x0, x1, y0, y1 = UNDERARM
            for a in (approved, actual):
                a[y0:y1, x0 - 4 - 400:x1 + 4 - 400] = 0
                # Dad's seat is redrawn below his shirt's hem (SEAT in the export).
                a[SEAT[1]:, :SEAT[0] - 400] = 0
            assert np.array_equal(actual, approved)


def test_panel3_reuses_the_scanned_child_and_player_at_closeup_scale():
    image = Image.open(OUT / 'panel3.png')
    pair = Image.open(OUT / 'reused-calvin-player.png')
    # Calvin is used whole, exactly as drawn in panel 1, so his head and body
    # join as Watterson drew them. Check each insert away from the shoe-to-
    # player contact which was separated.
    for bounds, (x, y), interior in [
        ((6, 16, 452, 730), (2422, 2024), (25, 15, 600, 1080)),
        ((436, 458, 828, 696), (1782, 2714), (80, 80, 510, 340)),
    ]:
        source = pair.crop(bounds)
        scaled = source.resize(tuple(round(v * 1.56) for v in source.size), Image.Resampling.LANCZOS)
        actual = image.crop((x, y, x + scaled.width, y + scaled.height))
        assert np.array_equal(np.asarray(actual.crop(interior)), np.asarray(scaled.crop(interior)))


def test_calvin_keeps_his_scale_relative_to_dad():
    ratios = []
    # Windows enclose the widest hair/ear contours, clear of shoulders and hands.
    for number, windows in [
        (2, [(880, 790, 1550, 1110), (1880, 1320, 2600, 1750)]),
        (3, [(970, 1172, 1700, 1552), (2394, 2000, 3174, 2620)]),
    ]:
        image = Image.open(OUT / f'panel{number}.png')
        widths = []
        for window in windows:
            _, x = np.nonzero(np.asarray(image.crop(window)) < 128)
            widths.append(x.max() - x.min() + 1)
        ratios.append(widths[1] / widths[0])
    assert abs(ratios[1] / ratios[0] - 1) < 0.02


def test_dads_kneeling_legs_are_the_programmatic_drawing():
    import sys
    sys.path.insert(0, str(ROOT / 'tools/extensions/reconstruction-v2'))
    import drawn_legs
    # Redrawing over the export changes nothing: the legs and shoes below
    # each crop are exactly what drawn_legs.py draws.
    for number, draw in ((2, drawn_legs.panel_two), (3, drawn_legs.panel_three)):
        image = Image.open(OUT / f'panel{number}.png').convert('L')
        redrawn, original = np.asarray(draw(image)), np.asarray(image)
        if number == 2:
            redrawn, original = redrawn[2060:], original[2060:]
        assert np.array_equal(redrawn, original)


def test_line_under_dads_arm_in_panel2_has_the_scans_weight():
    image = np.asarray(Image.open(OUT / 'panel2.png')) < 128
    x0, x1, y0, y1 = UNDERARM
    for x in range(800, x1 - 10):
        column = image[y0:y1, x]
        top = np.argmax(column)
        assert np.argmin(column[top:]) <= 26
