"""Cut the four panels' scans from the book, for the graft to build round.

    uv run tools/extensions/graft/scans.py [calvin-and-hobbes.pdf]

Writes `scans/locked-N.png`: each panel's art from the strip's page, with
the lettering and balloons erased, smoothed at twice the scan's resolution
as `tools/build_assets.py` smooths the editor's. These are the pixels every
full panel keeps exactly. Panel 4 also gets `scans/original-4.png`, its
1-bit ink before smoothing, which its existing left extension is joined to.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import build_assets as b  # noqa: E402

SCANS = Path(__file__).resolve().parent / 'scans'


def prepare(pdf):
    """{file name: image} for the scan of the book at `pdf`."""
    ink, background = b.layers(pdf)
    made = {}
    for number, panel in enumerate(b.PANELS, 1):
        art, _ = b.panel_art(ink, background, panel)
        if 'signature' in panel:
            # Watterson's signature is a separate asset: black over its place
            x0, y0 = panel['box'][:2]
            sx0, sy0, sx1, sy1 = panel['signature']
            art[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = True
        made[f'locked-{number}.png'] = b.smooth(art)
        if number == 4:
            made['original-4.png'] = Image.fromarray(np.where(art, 0, 255).astype('uint8'))
    return made


if __name__ == '__main__':
    SCANS.mkdir(exist_ok=True)
    for name, image in prepare(sys.argv[1] if len(sys.argv) > 1 else b.ROOT / 'calvin-and-hobbes.pdf').items():
        image.save(SCANS / name)
        print(name, image.size)
