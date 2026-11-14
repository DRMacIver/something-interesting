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


def changed(edit, panel, jitter=9, margin=30, parts=1):
    """Where the edit really differs from the panel: ink in one that is more
    than `jitter` px from any ink in the other, grown by `margin`, with the
    holes filled. Only the `parts` largest such places are kept: the parts
    that were asked for."""
    far = (edit & (ndimage.distance_transform_edt(~panel) > jitter)) \
        | (panel & (ndimage.distance_transform_edt(~edit) > jitter))
    labels, count = ndimage.label(ndimage.binary_dilation(far, iterations=margin))
    if not count:
        return np.zeros(edit.shape, bool)
    sizes = ndimage.sum(far, labels, range(1, count + 1))
    largest = np.argsort(sizes)[::-1][:parts] + 1
    return ndimage.binary_fill_holes(np.isin(labels, largest))


def meet_scan(panel, mask, protect):
    """The panel (grey, export px) with the lines of a just-patched part
    slid to meet the scan's where they reach the crop `protect`. A redraw
    has not been through the graft's own joining, so its lines can arrive
    a little off: thinner than the scan's, or to one side."""
    x0, y0, x1, y1 = protect
    h2, w2 = panel.shape[0] // 2, panel.shape[1] // 2
    even = (slice(0, h2 * 2), slice(0, w2 * 2))
    half = lambda a: a[even].reshape(h2, 2, w2, 2).mean((1, 3))  # noqa: E731
    cover = half((panel < 128).astype(np.float32))
    near = ndimage.binary_dilation(half(mask.astype(np.float32)) > 0, iterations=25)
    left, top = x0 // 2, y0 // 2
    scan = cover[top:y1 // 2, left:x1 // 2] > 0.5
    frame = graft.Frame(left=left, right=w2 - x1 // 2, below=h2 - y1 // 2)
    crop = (slice(top, y1 // 2), slice(left, x1 // 2))
    only = {'left': near[crop][:, 0], 'right': near[crop][:, -1], 'bottom': near[crop][-1]}
    field = np.zeros((2, h2, w2), np.float32)
    for _ in range(3):
        field += graft.snap(scan, graft.warp(cover, field), frame, outside=True, only=only)[0]
    if not np.abs(field).max() > 0.25:
        return panel
    big = np.stack([np.asarray(Image.fromarray(f).resize((w2 * 2, h2 * 2), Image.BILINEAR)) * 2 for f in field])
    moved = graft.warp((panel[even] < 128).astype(np.float32), big) > 0.5
    smooth = np.asarray(build_assets.smooth(half(moved.astype(np.float32)) >= 0.5))
    change = ndimage.binary_dilation(np.abs(big).max(0) > 0.25, iterations=4)
    change[y0:y1, x0:x1] = False
    out = panel.copy()
    out[even][change] = smooth[change]
    return out


def weigh_in(panel, box, protect, strip=16):
    """The panel (grey, export px) with the drawn line in `box` as heavy,
    where it leaves the crop `protect`, as the scan's line that it carries
    on, easing back to its own weight by the far end of the box. Re-inking
    gives every drawn line the scan's typical weight, so one that continues
    a heavier stroke of the scan steps in width at the crop's edge."""
    x0, y0, x1, y1 = box
    px0, py0, px1, py1 = protect
    pad = 40
    window = (slice(max(0, y0 - pad), y1 + pad), slice(max(0, x0 - pad), x1 + pad))
    ink = panel[window] < 128
    inside = np.zeros(panel.shape, bool)
    inside[py0:py1, px0:px1] = True
    inside = inside[window]
    place = np.zeros(panel.shape, bool)
    place[y0:y1, x0:x1] = True
    place = place[window] & ~inside
    away = ndimage.distance_transform_edt(~inside)           # px outside the crop
    into = ndimage.distance_transform_edt(inside)            # px inside it
    half = ndimage.distance_transform_edt(ink)               # half a line's width, at its middle
    # the scan's line just inside the crop, beside the drawn line's first few px
    start = place & ink & (away <= strip)
    if not start.any():
        return panel
    beside = ndimage.binary_dilation(start, iterations=2 * strip) & inside & ink & (into <= strip)
    if not beside.any():
        return panel
    extra = float(half[beside].max() - half[start].max())    # px to add on each side
    if extra <= 0.5:
        return panel
    signed = ndimage.distance_transform_edt(~(ink & ~inside)) - half   # from the drawn ink alone
    ease = np.clip(1 - away / max(1.0, float(away[place].max())), 0, 1)
    heavier = (signed < extra * ease) & place
    grown = ink | heavier
    h2, w2 = grown.shape[0] // 2, grown.shape[1] // 2
    even = (slice(0, h2 * 2), slice(0, w2 * 2))
    smooth = np.asarray(build_assets.smooth(grown[even].reshape(h2, 2, w2, 2).mean((1, 3)) >= 0.5))
    change = ndimage.binary_dilation(heavier, iterations=3) & place
    out = panel.copy()
    view = out[window]
    view[even][change[even]] = smooth[change[even]]
    return out


def stubs(before, after, mask, small=1500, near=60):
    """Loose ends left beside a patched part: small pieces of ink close to
    it that were part of something larger before the patch (the end of a
    line the redraw removed, running on past the region it covered)."""
    close = ndimage.binary_dilation(mask, iterations=near) & ~mask
    labels, count = ndimage.label(after)
    sizes = ndimage.sum(after, labels, range(1, count + 1))
    was, _ = ndimage.label(before)
    was_size = np.concatenate([[0], np.bincount(was.ravel())[1:]])
    loose = np.zeros(after.shape, bool)
    for index in np.unique(labels[close & after]):
        piece = labels == index
        mostly_outside = (piece & ~mask).sum() >= 0.5 * sizes[index - 1] if index else False  # not the redraw's own
        if mostly_outside and sizes[index - 1] < small and was_size[was[piece]].max() >= 2 * sizes[index - 1]:
            loose |= piece
    return loose


def patch(panel_image, edit_image, box, protect=None, parts=1):
    """(patched panel, mask of what changed). `protect` is a box of the
    panel that must not change (the scan). `parts` is how many separate
    places the redraw was asked to change."""
    panel = np.asarray(panel_image.convert('L')).copy()
    x0, y0, x1, y1 = box
    region = panel[y0:y1, x0:x1]
    edit = np.asarray(edit_image.convert('L').resize((x1 - x0, y1 - y0), Image.LANCZOS))
    edit_ink, _ = settle(edit < 128, region < 128)
    mask = changed(edit_ink, region < 128, parts=parts)
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
    before = panel < 128
    panel[y0:y1, x0:x1] = out
    whole = np.zeros(panel.shape, bool)
    whole[y0:y1, x0:x1] = mask
    panel[stubs(before, panel < 128, whole)] = 255
    if protect:
        panel = meet_scan(panel, whole, protect)
    return Image.fromarray(panel), whole


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('panel')
    ap.add_argument('edit')
    ap.add_argument('out')
    ap.add_argument('box', type=int, nargs=4)
    ap.add_argument('--protect', type=int, nargs=4)
    ap.add_argument('--parts', type=int, default=1)
    args = ap.parse_args()
    image, mask = patch(Image.open(args.panel), Image.open(args.edit), args.box, args.protect, args.parts)
    image.save(args.out)
    ys, xs = np.nonzero(mask)
    print(f'changed {int(mask.sum())} px in ({xs.min()}, {ys.min()}, {xs.max()}, {ys.max()})'
          if len(xs) else 'nothing changed')


if __name__ == '__main__':
    main()
