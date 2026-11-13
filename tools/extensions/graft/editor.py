"""Cut the editor's panel extensions from the full-panel exports.

    uv run tools/extensions/graft/editor.py

The comic editor builds its panels in `tools/build_assets.py` from the scan
plus 1-bit extensions on the scan's grid, `tools/extensions/panelN-SIDE.png`,
of the sizes each panel's `extend` gives. This writes those files for
panels 1 to 3 from `assets/full-panels/panelN.png`, so the editor shows the
same drawings as the exports. Run `tools/build_assets.py` afterwards.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
from graft import build_assets as b  # noqa: E402


def scan_grid_ink(number):
    """The export as 1-bit ink on the scan's grid."""
    image = np.asarray(Image.open(build.OUT / f'panel{number}.png').convert('L')) < 128
    h, w = image.shape[0] // 2 * 2, image.shape[1] // 2 * 2
    return image[:h, :w].reshape(h // 2, 2, w // 2, 2).mean((1, 3)) >= 0.5


def extensions(number):
    """{side: ink} for the panel, sized as build_assets expects."""
    panel = b.PANELS[number - 1]
    widths = panel['extend']
    x0, _, x1, y1 = (v // 2 for v in build.scan_box(number))
    ink = scan_grid_ink(number)
    # room all round, in case the editor shows more than the export holds
    pad = 1000
    ink = np.pad(ink, pad)
    x0, x1, y0, y1 = x0 + pad, x1 + pad, pad, y1 + pad
    left, right, below = widths['left'], widths['right'], widths.get('below', 0)
    cut = {'left': ink[y0:y1, x0 - left:x0], 'right': ink[y0:y1, x1:x1 + right],
           'below': ink[y1:y1 + below, x0 - left:x1 + right]}
    drawn = ink.copy()
    drawn[y0:y1 + below, x0 - left:x1 + right] = False
    if drawn.any():
        raise ValueError(f'panel {number}: its extend sizes leave some of the drawing out')
    return {side: cut[side] for side in panel.get('extensions', {})}


def main():
    for number in (1, 2, 3):
        names = b.PANELS[number - 1]['extensions']
        for side, ink in extensions(number).items():
            Image.fromarray(~ink).convert('1').save(b.EXTENSIONS / names[side], optimize=True)
            print(names[side], ink.shape[::-1], 'ink' if ink.any() else 'blank')


if __name__ == '__main__':
    main()
