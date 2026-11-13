"""Build the four full panels in assets/full-panels from the chosen drawings.

    uv run tools/extensions/graft/build.py

Panels 1 to 3 are the scan with a whole-scene drawing grafted round it
(`graft.py`); `PICKS` names the drawing chosen for each, kept in `picks/`.
In the two close-ups Dad's shoe is then panel 1's own (`shoe.py`), and a
few single parts are taken from redraws of them (`patch.py`). Panel 4 is the scan with its existing left extension.

Then run ../reconstruction-v2/build_review.py for panels.html.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graft  # noqa: E402
import patch  # noqa: E402
import shoe  # noqa: E402
from graft import build_assets as b  # noqa: E402
from run import FRAMES  # noqa: E402

HERE = Path(__file__).resolve().parent
LOCKED = HERE.parent / 'reconstruction-v2'
OUT = b.ROOT / 'assets/full-panels'

# For the close-ups: Dad's head width (export px), the box holding the shoe
# the model drew, where panel 1's shoe goes (its bottom-right corner), and
# the redraws of single parts to take back, in order, each with the region
# of the panel it was made from: where the shoe meets his trousers
# (prompts/join-tidy.txt) and, in panel 2, where his sleeve meets his arm at
# the crop's edge (prompts/sleeve-join.txt).
PICKS = {
    1: dict(candidate='p1-walk-1.png'),
    2: dict(candidate='p2-kneel-19.png', head=493, old_shoe=(290, 2110, 670, 2420),
            shoe_at=(800, 2410), redraws=[('p2-tidy-1.png', (0, 1560, 1680, 2680)),
                                           ('p2-sleeve-2.png', (450, 1400, 1350, 2000))]),
    3: dict(candidate='p3-kneel-3.png', head=562, old_shoe=(480, 2880, 940, 3240),
            shoe_at=(1030, 3205), redraws=[('p3-tidy-2.png', (150, 2300, 2100, 3600))]),
}


def scan_box(number):
    scan = Image.open(LOCKED / f'locked-{number}.png')
    left = FRAMES[number].left * 2
    return (left, 0, left + scan.width, scan.height)


def panel(number, panel_one=None):
    """(image, fit report) for panel 1, 2 or 3. The close-ups need the
    built panel 1, for its shoe."""
    pick = PICKS[number]
    scan = Image.open(LOCKED / f'locked-{number}.png').convert('L')
    image, report = graft.graft(scan, Image.open(HERE / 'picks' / pick['candidate']), FRAMES[number])
    if 'shoe_at' in pick:
        image = shoe.tuck(image, panel_one, pick['head'], pick['old_shoe'], pick['shoe_at'])
        for name, region in pick['redraws']:
            image, _ = patch.patch(image, Image.open(HERE / 'picks' / name), region, protect=scan_box(number))
    return image, report


def panel_four():
    scan = Image.open(LOCKED / 'locked-4.png').convert('L')
    ink = np.asarray(Image.open(LOCKED / 'original-4.png')) < 128
    extended, _ = b.extended(ink, b.PANELS[3])
    image = b.smooth(extended)
    image.paste(scan, (400, 0))
    return image


def build():
    OUT.mkdir(exist_ok=True)
    records = []
    overview = Image.new('L', (1600, 2100), 235)
    one = None
    for number in range(1, 5):
        scan = Image.open(LOCKED / f'locked-{number}.png').convert('L')
        if number == 4:
            image, report, x = panel_four(), None, 400
        else:
            image, report = panel(number, one)
            x = FRAMES[number].left * 2
            one = one or image
        scan.save(OUT / f'original{number}.png', optimize=True)
        image.save(OUT / f'panel{number}.png', optimize=True)
        preview = image.copy()
        preview.thumbnail((950, 1100))
        preview.save(OUT / f'preview{number}.png')
        source = np.asarray(scan)
        difference = np.asarray(image.crop((x, 0, x + scan.width, scan.height))) != source
        record = dict(panel=number, size=image.size, originalOffset=[x, 0], originalSize=scan.size,
                      changedOriginalPixels=int(difference.sum()),
                      originalMatchFraction=1 - float(difference.mean()),
                      changedOriginalInkPixels=int(difference[source < 255].sum()))
        if report:
            record['graft'] = dict(report.as_dict(), **PICKS[number])
        records.append(record)
        ink = ImageChops.invert(image) if number < 4 else image
        left, top, right, bottom = ink.getbbox()
        crop = image.crop((max(0, left - 30), max(0, top - 30),
                           min(image.width, right + 30), min(image.height, bottom + 30)))
        crop.thumbnail((770, 970))
        col, row = (number - 1) % 2, (number - 1) // 2
        overview.paste(crop, (col * 800 + (800 - crop.width) // 2, row * 1050 + 50))
        ImageDraw.Draw(overview).text((col * 800 + 20, row * 1050 + 20), f'Panel {number}', fill=0)
        print(f'panel {number}: {image.size}' + (f", fit {report.fit_warped:.2f}px, seam {report.seam}px" if report else ''))
    overview.save(OUT / 'overview.png')
    (OUT / 'verification.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    build()
