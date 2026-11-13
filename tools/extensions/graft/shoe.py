"""Dad's shoe behind his knee, in Watterson's own ink.

    uv run tools/extensions/graft/shoe.py PANEL PANEL1 OUT HEAD_PX  X0 Y0 X1 Y1  AX AY

The image model's shoes come out small and soft. `tuck` replaces the shoe a
grafted panel has in the box X0..Y1 with the planted shoe from the grafted
panel 1 (PANEL1), mirrored so its toe points back, enlarged by the ratio of
Dad's head sizes (HEAD_PX against panel 1's) and thinned to this drawing's
line. It is not turned over: upside down it stops reading as a shoe. Its
bottom-right corner goes to (AX, AY), behind the black trousers, so only
the toe and instep show, as they do under his trouser hem in panel 1.

Where the shoe meets the trousers is then tidied by the image model
(`prompts/join-tidy.txt`) and taken back with `patch.py`.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graft  # noqa: E402
from graft import build_assets  # noqa: E402

PANEL1_HEAD = 290                    # Dad's head width in panel 1, export px
PANEL1_SHOE = (380, 1760, 760, 2020)  # his planted shoe in the grafted panel 1
HEAVY = 1.35                         # he draws shoes with his heaviest line


def solid_of(ink, radius=16):
    """The solid blacks of a drawing: what survives losing `radius` px all round."""
    return ndimage.binary_dilation(ndimage.binary_erosion(ink, iterations=radius), iterations=radius) & ink


def part_in(ink, box):
    """(part, solid): everything outlined in the box that is not solid
    black, with the paper it encloses; and the drawing's solid blacks."""
    x0, y0, x1, y1 = box
    solid = solid_of(ink)
    inside = np.zeros(ink.shape, bool)
    inside[y0:y1, x0:x1] = True
    lines = ink & inside & ~solid
    closed = ndimage.binary_fill_holes(lines | (solid & inside))
    return (closed & ~solid) | lines, solid


def panel_one_shoe(source, scale):
    """(alpha, ink) of panel 1's planted shoe with the edge of the trouser
    hem that lies over it, mirrored and enlarged."""
    ink = np.asarray(source.convert('L')) < 128
    shoe, solid = part_in(ink, PANEL1_SHOE)
    hem = solid & ndimage.binary_dilation(shoe, iterations=11)
    piece = shoe | hem
    ys, xs = np.nonzero(piece)
    box = (xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5)

    def turned(mask):
        image = Image.fromarray((mask[box[1]:box[3], box[0]:box[2]] * 255).astype(np.uint8))
        image = ImageOps.mirror(image)
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
        return np.asarray(image) > 127

    return turned(piece), turned(ink & piece), turned(hem)


def tuck(panel_image, source, head, old_box, anchor):
    """The panel with the shoe in `old_box` replaced by panel 1's, its
    bottom-right corner at `anchor`, behind the trousers."""
    alpha, inked, hem = panel_one_shoe(source, head / PANEL1_HEAD)
    panel = np.asarray(panel_image.convert('L')).copy()
    ink = panel < 128
    old, solid = part_in(ink, old_box)

    # the weight of the lines it joins, not of panel 1's enlarged
    around = np.zeros(ink.shape, bool)
    around[max(old_box[1] - 600, 0):old_box[3], old_box[0]:old_box[2] + 700] = True
    want = HEAVY * graft.line_weight((ink & around & ~ndimage.binary_dilation(solid, iterations=4))[::2, ::2])
    have = graft.line_weight((inked & ~ndimage.binary_dilation(hem, iterations=4))[::2, ::2])
    thin = max(0.0, have - want)  # per side, export px
    inked = (ndimage.distance_transform_edt(inked & ~hem) > thin) | hem

    h, w = alpha.shape
    x0, y0 = anchor[0] - w, anchor[1] - h
    layer = np.zeros(ink.shape, bool)
    layer_ink = np.zeros(ink.shape, bool)
    layer[y0:y0 + h, x0:x0 + w] = alpha
    layer_ink[y0:y0 + h, x0:x0 + w] = inked

    new = ink & ~(old & ~solid)
    show = layer & ~ndimage.binary_fill_holes(solid)  # behind the trousers, white fold marks and all
    new[show] = layer_ink[show]
    # crumbs: loose bits of ink that came with the piece
    labels, count = ndimage.label(new)
    sizes = ndimage.sum(new, labels, range(1, count + 1))
    small = np.isin(labels, [i + 1 for i, size in enumerate(sizes) if size < 2500])
    new &= ~(small & ndimage.binary_dilation(layer, iterations=6))

    even = (slice(0, new.shape[0] // 2 * 2), slice(0, new.shape[1] // 2 * 2))
    half = new[even].reshape(new.shape[0] // 2, 2, new.shape[1] // 2, 2).mean((1, 3)) >= 0.5
    smooth = np.asarray(build_assets.smooth(half))
    changed = ndimage.binary_dilation((old & ~solid) | show, iterations=12)
    panel[even][changed[even]] = smooth[changed[even]]
    return Image.fromarray(panel)


if __name__ == '__main__':
    panel, source, out = sys.argv[1:4]
    head, x0, y0, x1, y1, ax, ay = map(int, sys.argv[4:11])
    tuck(Image.open(panel), Image.open(source), head, (x0, y0, x1, y1), (ax, ay)).save(out)
