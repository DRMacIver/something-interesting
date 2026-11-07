"""The reconstructed exports must preserve their independently extracted art."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/full-panels'


def test_original_crops_are_preserved():
    for item in json.loads((OUT / 'verification.json').read_text()):
        number = item['panel']
        image = Image.open(OUT / f'panel{number}.png')
        source = np.asarray(Image.open(OUT / f'original{number}.png'))
        x, y = item['originalOffset']
        width, height = item['originalSize']
        overlap = np.asarray(image.crop((x, y, x + width, y + height)))
        assert image.size == tuple(item['size'])
        # Every panel keeps Watterson's crop exactly.
        assert np.array_equal(overlap, source)


def test_panel3_reuses_the_scanned_child_at_closeup_scale():
    image = Image.open(OUT / 'panel3.png')
    pair = Image.open(OUT / 'reused-calvin-player.png')
    scale = 1.56

    def scaled(art):
        return art.resize(tuple(round(v * scale) for v in art.size), Image.Resampling.LANCZOS)

    # Calvin's head is exactly as in panel 1, looking up towards Dad.
    def agreement(art, x, y):
        actual = image.crop((x, y, x + art.width, y + art.height))
        return np.mean((np.asarray(actual) < 128) == (np.asarray(art) < 128))

    head = scaled(pair.crop((6, 16, 452, 420)))
    assert agreement(head, 2422, 2024) > 0.98


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


def test_dad_outside_the_crops_is_the_programmatic_drawing():
    import sys
    sys.path.insert(0, str(ROOT / 'tools/extensions/reconstruction-v2'))
    import dad2_refine
    import drawn_legs
    # Redrawing over the export changes nothing: Dad outside each crop is
    # exactly what the drawing code draws.
    for number, draw in ((2, dad2_refine.panel_two), (3, drawn_legs.panel_three)):
        image = Image.open(OUT / f'panel{number}.png').convert('L')
        assert np.array_equal(np.asarray(draw(image)), np.asarray(image))


def test_close_ups_stop_above_dads_legs():
    # Panel 2's crop already reaches his knee, so it is not extended below
    # the scan; panel 3 stops just above the top of his trousers.
    assert Image.open(OUT / 'panel2.png').height == Image.open(OUT / 'original2.png').height
    image = np.asarray(Image.open(OUT / 'panel3.png')) < 128
    assert image.shape[0] > 2060
    # His trousers are a solid black mass; below the crop only brush lines
    # (at most about 50px across where strokes meet) show, and they erode away.
    from scipy import ndimage
    assert not ndimage.binary_erosion(image[2060:, :1300], iterations=25).any()

