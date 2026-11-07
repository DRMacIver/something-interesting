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


def test_dad_outside_the_crops_is_the_drawing_code_s():
    import sys
    sys.path.insert(0, str(ROOT / 'tools/extensions/reconstruction-v2'))
    import dad2_refine
    import dad3
    # Redrawing over the export changes nothing: Dad outside each crop is
    # exactly what the drawing code puts there.
    for number, draw in ((2, dad2_refine.panel_two), (3, dad3.panel_three)):
        image = Image.open(OUT / f'panel{number}.png').convert('L')
        assert np.array_equal(np.asarray(draw(image)), np.asarray(image))


def test_panel2_is_not_extended_below_the_scan():
    # Panel 2's crop already reaches his knee.
    assert Image.open(OUT / 'panel2.png').height == Image.open(OUT / 'original2.png').height


def test_panel3_shows_dad_kneeling_on_the_floor():
    from scipy import ndimage
    image = np.asarray(Image.open(OUT / 'panel3.png')) < 128
    # His trousers are a solid black mass below the crop, reaching the floor
    # where Calvin and the player sit.
    trousers = ndimage.binary_erosion(image[2060:, :1600], iterations=25)
    rows = np.nonzero(trousers.any(1))[0] + 2060
    assert rows.min() < 2800 and rows.max() > 3000
    floor = np.nonzero(image[:, :1600].any(1))[0].max()
    assert 3050 < floor < 3150
    # No floor marks: nothing of him or anything else to the left of his shoe
    # on the floor line.
    assert not image[2950:, :300].any()


def test_panel3_lines_meet_the_scan_at_the_crop_s_edges():
    # Every line of the scan that runs out of the crop goes on outside it.
    image = np.asarray(Image.open(OUT / 'panel3.png')) < 128
    scan = np.asarray(Image.open(OUT / 'original3.png')) < 128

    def crossings(line):
        edges = np.flatnonzero(np.diff(np.r_[0, line.astype(int), 0]))
        return [(a + b - 1) // 2 for a, b in zip(edges[::2], edges[1::2])]

    for x in crossings(scan[-1]):
        assert image[2066:2072, 800 + x - 10:800 + x + 11].any(), x + 800
    for y in crossings(scan[:, 0]):
        assert image[y - 10:y + 11, 792:796].any(), y
