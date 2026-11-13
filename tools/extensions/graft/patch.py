"""Put one redrawn part of a grafted panel back into it.

    uv run tools/extensions/graft/patch.py PANEL.png EDIT.png OUT.png X0 Y0 X1 Y1

When one part of a grafted panel is wrong (a shoe, say), the image model is
shown the region X0..X1, Y0..Y1 of the panel and asked to redraw it with
only that part changed (`prompts/part-edit.txt`). It redraws the whole
region, a little differently everywhere, so only what it really changed is
taken: the edit is laid back over the region, the places where its ink
lies well away from the panel's (or the panel's from its) are found, and inside
those the edit replaces the panel, re-inked as `graft.py` inks a candidate.
Everything else in the panel stays as it was.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graft  # noqa: E402
from graft import build_assets  # noqa: E402


def settle(edit, panel, reach=16):
    """The edit shifted by the whole number of pixels that best lays its
    ink over the panel's (the model drifts by a few)."""
    a = ndimage.gaussian_filter(panel.astype(np.float32), 3)
    b = ndimage.gaussian_filter(edit.astype(np.float32), 3)
    best = None
    for dy in range(-reach, reach + 1, 2):
        for dx in range(-reach, reach + 1, 2):
            score = float((a * np.roll(b, (dy, dx), (0, 1))).sum())
            if best is None or score > best[0]:
                best = (score, dy, dx)
    return np.roll(edit, best[1:], (0, 1)), best[1:]


def changed(edit, panel, jitter=9, margin=30):
    """Where the edit really differs from the panel: ink in one that is more
    than `jitter` px from any ink in the other, grown by `margin`, with the
    holes filled. Only the largest such place is kept: the one part that
    was asked for."""
    far = (edit & (ndimage.distance_transform_edt(~panel) > jitter)) \
        | (panel & (ndimage.distance_transform_edt(~edit) > jitter))
    labels, count = ndimage.label(ndimage.binary_dilation(far, iterations=margin))
    if not count:
        return np.zeros(edit.shape, bool)
    sizes = ndimage.sum(far, labels, range(1, count + 1))
    return ndimage.binary_fill_holes(labels == int(np.argmax(sizes)) + 1)


def patch(panel_image, edit_image, box, protect=None):
    """(patched panel, mask of what changed). `protect` is a box of the
    panel that must not change (the scan)."""
    panel = np.asarray(panel_image.convert('L')).copy()
    x0, y0, x1, y1 = box
    region = panel[y0:y1, x0:x1]
    edit = np.asarray(edit_image.convert('L').resize((x1 - x0, y1 - y0), Image.LANCZOS))
    edit_ink, _ = settle(edit < 128, region < 128)
    mask = changed(edit_ink, region < 128)
    if protect:
        px0, py0, px1, py1 = protect
        guard = np.zeros(panel.shape, bool)
        guard[py0:py1, px0:px1] = True
        mask &= ~guard[y0:y1, x0:x1]

    # the scan's ink for the new part: its weight, its grid, its smoothing
    even = (slice(0, (y1 - y0) // 2 * 2), slice(0, (x1 - x0) // 2 * 2))
    lines = ~ndimage.binary_opening(region < 128, iterations=12) & (region < 128)
    target = graft.line_weight((lines & ~mask)[even][::2, ::2])
    # weigh only the part's lines: solid blacks caught in the mask are not lines
    solid = ndimage.binary_dilation(ndimage.binary_opening(edit_ink, iterations=12), iterations=6)
    ink = graft.reink(edit_ink[even].astype(np.float32), target, (mask & ~solid)[even][::2, ::2])
    smooth = np.asarray(build_assets.smooth(ink))
    out = region.copy()
    out[even][mask[even]] = smooth[mask[even]]
    panel[y0:y1, x0:x1] = out
    whole = np.zeros(panel.shape, bool)
    whole[y0:y1, x0:x1] = mask
    return Image.fromarray(panel), whole


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('panel')
    ap.add_argument('edit')
    ap.add_argument('out')
    ap.add_argument('box', type=int, nargs=4)
    ap.add_argument('--protect', type=int, nargs=4)
    args = ap.parse_args()
    image, mask = patch(Image.open(args.panel), Image.open(args.edit), args.box, args.protect)
    image.save(args.out)
    ys, xs = np.nonzero(mask)
    print(f'changed {int(mask.sum())} px in ({xs.min()}, {ys.min()}, {xs.max()}, {ys.max()})'
          if len(xs) else 'nothing changed')


if __name__ == '__main__':
    main()
