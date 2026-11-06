"""The reconstructed exports must preserve their independently extracted art."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/full-panels'


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
            approved = Image.open(ROOT / 'tools/extensions/reconstruction-v2/upper-2.png')
            assert np.array_equal(np.asarray(image.crop((400, 0, 3182, 2060))), np.asarray(approved))


def test_panel3_reuses_the_scanned_child_and_player_at_closeup_scale():
    image = Image.open(OUT / 'panel3.png')
    pair = Image.open(OUT / 'reused-calvin-player.png')
    # Check each insert away from the shoe-to-player contact which was separated.
    for bounds, (x, y), interior, mirrored in [
        ((6, 16, 452, 730), (2422, 2024), (25, 15, 655, 580), False),
        ((-10, 16, 436, 730), (2422, 2024), (32, 701, 630, 1050), True),
        ((436, 458, 828, 696), (1782, 2714), (80, 80, 510, 340), False),
    ]:
        source = pair.crop(bounds)
        if mirrored:
            source = ImageOps.mirror(source)
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
        assert np.array_equal(np.asarray(draw(image)), np.asarray(image))
