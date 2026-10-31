# /// script
# dependencies = ["pillow", "numpy", "scipy", "pymupdf"]
# ///
"""Cut the panels of the 5 June 1990 strip out of the scanned book, erase
the lettering and speech balloons, smooth away the scan's pixelation, and
work out where text is allowed to flow in each panel.

Writes assets/panel{1..4}.png, assets/signature.png and assets/panels.json.

Usage: uv run tools/build_assets.py calvin-and-hobbes.pdf
"""

import json
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
PAGE = 246

# The art is smoothed and stored at this multiple of the scan's resolution.
ART_SCALE = 2
# The layout grid (free space, mouths, lettering size) is at this multiple.
GRID_SCALE = 0.5
# Every panel's art is extended by this much (in scan pixels), so that
# panels can widen to make room for long text: to the right, unless the
# panel says otherwise. Where the art runs off an edge, the extension there
# is drawn to match (see EXTENSIONS); otherwise it's background.
EXTEND = 400
EXTENSIONS = ROOT / "tools" / "extensions"

# All coordinates are scan pixels on the page. Boxes are the panel
# interiors, inside the drawn borders (panel 3 has no border, and panel 4 is
# black right to its edge).
PANELS = [
    {
        "box": (60, 1870, 879, 2906),
        # Dad's balloon and lettering. Only ink lying entirely inside these
        # regions is erased, so artwork that pokes into them survives.
        "erase": [[(320, 1870), (881, 1870), (881, 2310), (320, 2310)]],
        "speakers": {"dad": (270, 2065)},
        "text_bottom": 2520,
        # How the dialogue is lettered in the original: in a balloon, or
        # loose in the panel with just a stroke towards the speaker.
        "speech": "balloon",
    },
    {
        "box": (924, 1877, 1717, 2907),
        # Calvin runs off the right edge; the rest of him is drawn in
        # tools/extensions/panel2-right.png.
        "extensions": {"right": "panel2-right.png"},
        # Both balloons and their lettering, steering around Dad's head and
        # Calvin's hair.
        "erase": [[(924, 1877), (1720, 1877), (1720, 2545), (1612, 2545),
                   (1602, 2588), (1518, 2592), (1500, 2640), (1318, 2640),
                   (1318, 2420), (1310, 2280), (924, 2270)]],
        # Dad's balloon outline runs into his hair, which would make it part
        # of him; cut it free on either side of his head.
        "wipe": [
            [(924, 2240), (1068, 2260), (1068, 2310), (924, 2302)],
            [(1218, 2280), (1345, 2280), (1345, 2395), (1288, 2395),
             (1288, 2306), (1218, 2306)],
        ],
        # Speakers are marked just in front of their mouths. Tails find
        # their own way there round anything in the way, with a clear line
        # of sight (Calvin's comes down beside his hair, as in the
        # original, rather than onto it).
        "speakers": {"dad": (1200, 2485), "calvin": (1515, 2800)},
        "text_bottom": 2560,
        "speech": "balloon",
        # Calvin's reply is lettered in a column of this width, centred
        # where his balloon was, with its last line far enough above his
        # head to leave room for a tail; longer replies grow upwards.
        "calvin_column": (1330, 1630, 2490),
    },
    {
        "box": (1755, 1877, 2550, 2907),
        "erase": [[(1755, 1877), (2550, 1877), (2550, 2620), (2220, 2620),
                   (2220, 2460), (1755, 2460)]],
        "speakers": {"dad": (2010, 2770)},
        "text_bottom": 2600,
        "speech": "loose",
    },
    {
        # Inside the edges of the black, where it's solid.
        "box": (2588, 1890, 3372, 2911),
        "erase": [],
        # Watterson's signature, which moves to the bottom right corner
        # however wide the panel is.
        "signature": (3176, 2840, 3300, 2890),
        "speakers": {},
        "text_bottom": None,
        "dark": True,
        # Extended both ways, so that Calvin's bed stays in the middle; its
        # far end is drawn in tools/extensions/panel4-left.png.
        "extend": {"left": EXTEND // 2, "right": EXTEND // 2},
        "extensions": {"left": "panel4-left.png"},
    },
]


def layers(path):
    """The page's 1-bit ink layer, and its background layer scaled to match.
    In these scans the line art is in the ink layer, but big solid blacks
    (panel 4's night) are only in the low resolution background."""
    doc = pymupdf.open(path)
    page = doc[PAGE]
    ink = background = None
    for img in page.get_images(full=True):
        xref, smask = img[0], img[1]
        if smask:
            pix = pymupdf.Pixmap(doc, smask)
            ink = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width
            ) > 127
        else:
            pix = pymupdf.Pixmap(doc, xref)
            if pix.n > 1:
                pix = pymupdf.Pixmap(pymupdf.csGRAY, pix)
            background = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width
            )
    background = np.asarray(
        Image.fromarray(background).resize(ink.shape[::-1], Image.BICUBIC)
    )
    return ink, background


def polygon_mask(shape, polygons):
    img = Image.new("L", (shape[1], shape[0]), 0)
    draw = ImageDraw.Draw(img)
    for poly in polygons:
        draw.polygon(poly, fill=1)
    return np.asarray(img).astype(bool)


def wipe(ink, polygons):
    """Clear everything inside the polygons."""
    if not polygons:
        return ink
    return ink & ~polygon_mask(ink.shape, polygons)


def erase(ink, polygons):
    """Remove every connected piece of ink lying entirely inside the
    polygons. Returns the cleaned ink and the heights of the pieces removed."""
    if not polygons:
        return ink, []
    region = polygon_mask(ink.shape, polygons)
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    out = ink.copy()
    heights = []
    for index, sl in enumerate(ndimage.find_objects(labels), start=1):
        component = labels[sl] == index
        if region[sl][component].all():
            out[sl][component] = False
            heights.append(sl[0].stop - sl[0].start)
    return out, heights


def smooth(ink):
    """Anti-aliased, smoothed version of a 1-bit scan at ART_SCALE times the
    resolution: blur away the staircase edges, upsample, and re-threshold
    with a narrow soft edge. Lines keep their weight and shape; only the
    pixel steps go."""
    blurred = ndimage.gaussian_filter(ink.astype(np.float32), 1.1)
    h, w = blurred.shape
    big = np.asarray(
        Image.fromarray(blurred).resize((w * ART_SCALE, h * ART_SCALE), Image.BICUBIC)
    )
    t = np.clip((big - 0.38) / 0.24, 0, 1)
    coverage = t * t * (3 - 2 * t)
    return Image.fromarray((255 - coverage * 255).round().astype(np.uint8))


def free_rows(ink, text_bottom):
    """For each row of the layout grid, the intervals where text may be
    placed: background connected to the top edge of the panel."""
    blocked = ndimage.binary_dilation(ink, iterations=3)
    labels, _ = ndimage.label(~blocked)
    top = set(labels[0][labels[0] > 0].tolist())
    free = np.isin(labels, list(top))
    free[text_bottom:] = False
    return grid_rows(free)


def open_rows(ink):
    """For each row of the layout grid, the intervals clear of artwork
    anywhere in the panel; speech balloon tails can go there."""
    return grid_rows(~ndimage.binary_dilation(ink, iterations=3))


def grid_rows(free):
    step = round(1 / GRID_SCALE)
    h = free.shape[0] // step
    w = free.shape[1] // step
    # A grid cell is free only if all of it is.
    grid = free[: h * step, : w * step].reshape(h, step, w, step).all(axis=(1, 3))
    rows = []
    for row in grid:
        edges = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(np.int8), [0]])))
        rows.append(edges.reshape(-1, 2).tolist())
    return rows


def panel_art(ink, background, panel):
    """A panel's art, 1-bit at scan resolution, with the lettering and
    balloons erased; and the heights of the pieces erased."""
    x0, y0, x1, y1 = panel["box"]

    def local(points):
        return [((x - x0), (y - y0)) for x, y in points]

    # Solid blacks (Dad's trousers, the night in panel 4) are only in the
    # low resolution background layer.
    art = ink[y0:y1, x0:x1] | (background[y0:y1, x0:x1] < 110)
    art = wipe(art, [local(p) for p in panel.get("wipe", [])])
    return erase(art, [local(p) for p in panel["erase"]])


def extended(art, panel):
    """The art with its extensions on either side, and how many columns
    were added on the left."""
    widths = panel.get("extend", {"left": 0, "right": EXTEND})
    # Text layout works in the original art's coordinates.
    assert widths["left"] == 0 or panel["text_bottom"] is None

    def extension(side):
        if side in panel.get("extensions", {}):
            extra = np.asarray(Image.open(EXTENSIONS / panel["extensions"][side]).convert("L")) < 128
            assert extra.shape == (art.shape[0], widths[side]), extra.shape
            return extra
        return np.full((art.shape[0], widths[side]), bool(panel.get("dark")))

    return np.hstack([extension("left"), art, extension("right")]), widths["left"]


def cut_signature(art, panel, name):
    """Take the white signature out of the black of the panel, save it as a
    white image of its own, and return where it was relative to the bottom
    right corner (in grid pixels)."""
    x0, y0 = panel["box"][:2]
    sx0, sy0, sx1, sy1 = panel["signature"]
    region = (slice(sy0 - y0, sy1 - y0), slice(sx0 - x0, sx1 - x0))
    letters = ~art[region]
    art[region] = True
    coverage = 255 - np.asarray(smooth(letters))
    image = np.zeros(coverage.shape + (4,), dtype=np.uint8)
    image[..., :3] = 255
    image[..., 3] = coverage
    Image.fromarray(image).save(OUT / name, optimize=True)
    h, w = art.shape
    return {
        "image": f"assets/{name}",
        "width": round((sx1 - sx0) * GRID_SCALE),
        "height": round((sy1 - sy0) * GRID_SCALE),
        "right": round((w - (sx1 - x0)) * GRID_SCALE),
        "bottom": round((h - (sy1 - y0)) * GRID_SCALE),
    }


def main():
    ink, background = layers(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    meta = []
    lettering = []
    for number, panel in enumerate(PANELS, start=1):
        x0, y0, x1, y1 = panel["box"]
        art, heights = panel_art(ink, background, panel)
        lettering.extend(heights)
        signature = cut_signature(art, panel, "signature.png") if "signature" in panel else None
        art, left = extended(art, panel)
        smooth(art).save(OUT / f"panel{number}.png", optimize=True)

        def grid(point):
            x, y = point
            return [round((x - x0) * GRID_SCALE, 1), round((y - y0) * GRID_SCALE, 1)]

        entry = {
            "image": f"assets/panel{number}.png",
            # The original width; the art goes on to extendedWidth.
            "width": round((x1 - x0) * GRID_SCALE),
            "extendedWidth": round(art.shape[1] * GRID_SCALE),
            # How much of the extended art is on the left.
            "left": round(left * GRID_SCALE),
            # Whether the art ends in plain background on that side, so that
            # the panel can widen past it.
            "openLeft": bool((art[:, 0] == bool(panel.get("dark"))).all()),
            "openRight": bool((art[:, -1] == bool(panel.get("dark"))).all()),
            "height": round((y1 - y0) * GRID_SCALE),
            "background": "#000" if panel.get("dark") else "#fff",
            "speakers": {name: grid(p) for name, p in panel["speakers"].items()},
            "free": None
            if panel["text_bottom"] is None
            else free_rows(art, panel["text_bottom"] - y0),
            "open": None if panel.get("dark") else open_rows(art),
        }
        if "speech" in panel:
            entry["speech"] = panel["speech"]
        if signature:
            entry["signature"] = signature
        if "calvin_column" in panel:
            cx0, cx1, bottom = panel["calvin_column"]
            entry["calvinColumn"] = grid((cx0, bottom))[:1] + grid((cx1, bottom))
        meta.append(entry)

    # Letters are most of what was erased; their typical height is the
    # height of Watterson's capitals in this strip.
    heights = np.array(lettering)
    letters = heights[(heights > 25) & (heights < 90)]
    cap = float(np.median(letters)) * GRID_SCALE
    (OUT / "panels.json").write_text(
        json.dumps({"capHeight": round(cap, 2), "panels": meta}, separators=(",", ":"))
    )
    print(f"lettering cap height {cap:.1f} grid px from {len(letters)} letters")


if __name__ == "__main__":
    main()
