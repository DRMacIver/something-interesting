# /// script
# dependencies = ["pillow", "numpy", "scipy"]
# ///
"""Cut the panels out of the original strip, erase Dad's lettering, upscale
the line art, and compute where text is allowed to flow in each panel.

Writes assets/panel{1..4}.png and assets/panels.json.
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source" / "original-strip.png"
OUT = ROOT / "assets"
SCALE = 4
DARK = 150

# All coordinates are in strip pixels. Panel boxes are the interiors, inside
# the drawn borders (panel 3 has no border in the original).
PANELS = [
    {
        "box": (5, 4, 176, 223),
        "erase": [[(62, 3), (177, 3), (177, 95), (62, 95)]],
        "mouth": (49, 45),
        "text_bottom": 140,
        "background": 255,
    },
    {
        "box": (187, 4, 353, 223),
        "erase": [[(186, 3), (354, 3), (354, 124), (300, 117), (284, 113),
                   (270, 113), (262, 96), (186, 92)]],
        # The balloon outline touches Dad's hair and shares a stretch of line
        # with Calvin's balloon, so it has to be wiped out by hand.
        "wipe": [
            [(187, 85), (220, 89), (220, 94), (213, 96), (213, 99),
             (187, 97)],
            [(250, 88), (273, 88), (273, 113), (262, 113), (262, 99),
             (250, 98)],
            [(268, 99), (276, 99), (286, 113), (283, 117), (278, 116),
             (266, 105)],
            [(328, 116), (354, 98), (354, 118), (332, 127), (332, 125),
             (328, 124)],
        ],
        "mouth": (230, 143),
        "text_bottom": 112,
        "background": 255,
    },
    {
        "box": (361, 4, 533, 223),
        "erase": [[(355, 3), (540, 3), (540, 162), (460, 162), (460, 127),
                   (355, 127)]],
        "mouth": (421, 190),
        "text_bottom": 140,
        "background": 255,
    },
    {
        "box": (541, 4, 712, 223),
        "erase": [],
        "mouth": None,
        "text_bottom": None,
        "background": 0,
    },
]


def polygon_mask(shape, polygons):
    img = Image.new("L", (shape[1], shape[0]), 0)
    draw = ImageDraw.Draw(img)
    for poly in polygons:
        draw.polygon(poly, fill=1)
    return np.asarray(img).astype(bool)


def erase_lettering(gray, polygons):
    """Whiten every dark connected component lying entirely inside the erase
    polygons, while leaving artwork that only pokes into the region
    untouched."""
    if not polygons:
        return gray
    region = polygon_mask(gray.shape, polygons)
    dark = gray < 230
    labels, count = ndimage.label(dark, structure=np.ones((3, 3)))
    out = gray.copy()
    for index, sl in enumerate(ndimage.find_objects(labels), start=1):
        component = labels[sl] == index
        if region[sl][component].all():
            out[sl][component] = 255
    return out


def wipe(gray, polygons):
    """Whiten everything inside the polygons."""
    if not polygons:
        return gray
    out = gray.copy()
    out[polygon_mask(gray.shape, polygons)] = 255
    return out


def free_rows(art, background, text_bottom):
    """For each row of the panel, the intervals where text may be placed:
    background pixels connected to the top edge of the panel."""
    if background == 0:
        return None
    blocked = ndimage.binary_dilation(art < DARK, iterations=2)
    open_ = ~blocked
    labels, _ = ndimage.label(open_)
    top_labels = set(labels[0][open_[0]].tolist()) - {0}
    free = np.isin(labels, list(top_labels))
    free[text_bottom:] = False
    rows = []
    for row in free:
        intervals = []
        x = 0
        while x < len(row):
            if row[x]:
                start = x
                while x < len(row) and row[x]:
                    x += 1
                intervals.append([start, x])
            else:
                x += 1
        rows.append(intervals)
    return rows


def crisp_upscale(art):
    """Upscale with bicubic interpolation, then push values towards pure
    black and white so the line art looks inked rather than blurry."""
    img = Image.fromarray(art).resize(
        (art.shape[1] * SCALE, art.shape[0] * SCALE), Image.BICUBIC
    )
    a = np.asarray(img).astype(float) / 255
    t = np.clip((a - 0.35) / 0.3, 0, 1)
    t = t * t * (3 - 2 * t)
    return Image.fromarray((t * 255).round().astype(np.uint8))


def main():
    strip = np.asarray(Image.open(SOURCE).convert("L")).copy()
    OUT.mkdir(exist_ok=True)
    meta = []
    for number, panel in enumerate(PANELS, start=1):
        # Crop before erasing so that the panel borders don't join lettering
        # and artwork into a single connected component.
        x0, y0, x1, y1 = panel["box"]
        def local(polygons):
            return [[(x - x0, y - y0) for x, y in poly] for poly in polygons]

        art = erase_lettering(strip[y0:y1, x0:x1], local(panel["erase"]))
        art = wipe(art, local(panel.get("wipe", [])))
        crisp_upscale(art).save(OUT / f"panel{number}.png", optimize=True)
        mouth = panel["mouth"]
        meta.append({
            "image": f"assets/panel{number}.png",
            "width": x1 - x0,
            "height": y1 - y0,
            "scale": SCALE,
            "background": "#fff" if panel["background"] else "#000",
            "mouth": None if mouth is None else [mouth[0] - x0, mouth[1] - y0],
            "free": free_rows(
                art,
                panel["background"],
                None if panel["text_bottom"] is None else panel["text_bottom"] - y0,
            ),
        })
    (OUT / "panels.json").write_text(json.dumps({"panels": meta}, separators=(",", ":")))


if __name__ == "__main__":
    main()
