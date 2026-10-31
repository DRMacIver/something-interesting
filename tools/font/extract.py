# /// script
# dependencies = ["pymupdf", "numpy", "scipy"]
# ///
"""Extract labelled letter samples from a scanned Calvin and Hobbes book.

The scan has an OCR text layer giving each word's text and bounding box. For
each word we split the ink in its box into horizontally separate shapes; if
there is exactly one shape per character we take the OCR text as labels for
the shapes. OCR mistakes slip through this, but they are rare enough to be
filtered out later by comparing samples of the same character.

Usage: uv run tools/font/extract.py BOOK.pdf build/samples.pkl
"""

import pickle
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pymupdf
from scipy import ndimage

PAD = 0.3  # How far past the OCR box (in cap heights) a letter may reach.
WORD = re.compile(r"^[A-Z0-9.,?!'\-:;()&]+$")
# Characters whose bottom sits on the baseline, for estimating it.
ON_BASELINE = set("ABCDEFGHIKLMNOPRSTUVWXYZ0123456789")


def ink_layer(doc, page):
    """The page's 1-bit lettering layer (the soft mask of the foreground
    image in these Internet Archive scans), and the transform from page
    points to its pixels."""
    for img in page.get_images(full=True):
        xref, smask = img[0], img[1]
        if not smask:
            continue
        pix = pymupdf.Pixmap(doc, smask)
        ink = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )[..., 0] > 127
        rect = page.get_image_rects(xref)[0]
        sx = pix.width / rect.width
        sy = pix.height / rect.height
        return ink, (rect.x0, rect.y0, sx, sy)
    return None, None


def components(ink):
    """Connected components of the page as an array of rows
    (x0, x1, y0, y1, label) plus the label image."""
    labels, count = ndimage.label(ink, structure=np.ones((3, 3)))
    rows = []
    for index, sl in enumerate(ndimage.find_objects(labels), start=1):
        ys, xs = sl
        rows.append((xs.start, xs.stop, ys.start, ys.stop, index))
    return np.array(rows, dtype=np.int64).reshape(-1, 5), labels


def group(comps, labels):
    """Merge components that overlap horizontally (so the dot of a ? or !
    goes with its stroke). Returns (x0, x1, y0, y1, mask) sorted by x."""
    order = np.argsort(comps[:, 0], kind="stable")
    merged = []
    for x0, x1, y0, y1, index in comps[order].tolist():
        if merged:
            prev = merged[-1]
            overlap = min(prev[1], x1) - max(prev[0], x0)
            narrower = min(prev[1] - prev[0], x1 - x0)
            if overlap > 0.4 * narrower:
                prev[0] = min(prev[0], x0)
                prev[1] = max(prev[1], x1)
                prev[2] = min(prev[2], y0)
                prev[3] = max(prev[3], y1)
                prev[4].append(index)
                continue
        merged.append([x0, x1, y0, y1, [index]])
    out = []
    for x0, x1, y0, y1, indices in merged:
        mask = np.isin(labels[y0:y1, x0:x1], indices)
        out.append((x0, x1, y0, y1, mask))
    return out


def stroke_width(masks):
    """Typical stroke thickness: twice the median distance-to-background
    along the middle of the strokes."""
    ridges = []
    for mask in masks:
        dist = ndimage.distance_transform_edt(np.pad(mask, 1))
        ridges.append(dist[(dist >= ndimage.maximum_filter(dist, size=3)) & (dist > 0)])
    ridge = np.concatenate(ridges)
    return 2 * float(np.median(ridge)) if ridge.size else 0.0


def process_page(args):
    path, number = args
    doc = pymupdf.open(path)
    page = doc[number]
    ink, transform = ink_layer(doc, page)
    if ink is None:
        return []
    ox, oy, sx, sy = transform
    comps, labels = components(ink)
    if not len(comps):
        return []
    cx = (comps[:, 0] + comps[:, 1]) / 2
    cy = (comps[:, 2] + comps[:, 3]) / 2

    words = []
    for x0, y0, x1, y1, text, block, line, index in page.get_text("words"):
        if not WORD.match(text):
            continue
        px0, px1 = (x0 - ox) * sx, (x1 - ox) * sx
        py0, py1 = (y0 - oy) * sy, (y1 - oy) * sy
        # OCR boxes are about one line pitch tall: cap height is around
        # 0.7 of that.
        pad = PAD * 0.7 * (py1 - py0)
        chosen = (
            (cx >= px0 - pad) & (cx <= px1 + pad) & (cy >= py0) & (cy <= py1)
        )
        sizes = comps[chosen]
        if not len(sizes):
            continue
        # Balloon outlines and artwork are bigger than any letter.
        if ((sizes[:, 3] - sizes[:, 2]) > 1.5 * (py1 - py0)).any():
            continue
        groups = group(sizes, labels)
        if len(groups) != len(text):
            continue
        bottoms = [g[3] for g, c in zip(groups, text) if c in ON_BASELINE]
        tops = [g[2] for g, c in zip(groups, text) if c in ON_BASELINE]
        if len(bottoms) < 2:
            continue
        baseline = float(np.median(bottoms))
        cap = baseline - float(np.median(tops))
        if cap < 15:
            continue
        left = groups[0][0]
        letters = []
        for (gx0, gx1, gy0, gy1, mask), char in zip(groups, text):
            letters.append({
                "char": char,
                "mask": np.packbits(mask, axis=1),
                "shape": mask.shape,
                # Positions in units of cap height, relative to the word's
                # baseline and its leftmost ink.
                "x0": (gx0 - left) / cap,
                "x1": (gx1 - left) / cap,
                "top": (baseline - gy0) / cap,
                "bottom": (baseline - gy1) / cap,
            })
        words.append({
            "page": number,
            "line": (block, line),
            "text": text,
            "cap": cap,
            "stroke": stroke_width([g[4] for g in groups]) / cap,
            "left": groups[0][0],
            "right": groups[-1][1],
            "baseline": baseline,
            # Vertical position on the page, as a fraction of its height.
            "y": baseline / ink.shape[0],
            "letters": letters,
        })

    # Gaps between consecutive accepted words on the same line, in cap
    # heights, for working out the width of a space.
    by_line = defaultdict(list)
    for word in words:
        by_line[word["line"]].append(word)
    for line in by_line.values():
        line.sort(key=lambda w: w["left"])
        for a, b in zip(line, line[1:]):
            cap = (a["cap"] + b["cap"]) / 2
            if abs(a["cap"] - b["cap"]) < 0.1 * cap and abs(a["baseline"] - b["baseline"]) < 0.2 * cap:
                b["space_before"] = (b["left"] - a["right"]) / cap
    return words


def main():
    path, out = sys.argv[1], sys.argv[2]
    pages = range(pymupdf.open(path).page_count)
    if len(sys.argv) > 3:
        pages = [int(p) for p in sys.argv[3].split(",")]
    words = []
    with ProcessPoolExecutor() as pool:
        for page_words in pool.map(process_page, [(path, n) for n in pages]):
            words.extend(page_words)
    with open(out, "wb") as f:
        pickle.dump(words, f)
    letters = sum(len(w["letters"]) for w in words)
    print(f"{len(words)} words, {letters} letters")


if __name__ == "__main__":
    main()
