# /// script
# dependencies = ["numpy", "scipy", "pillow", "potracer", "fonttools", "brotli"]
# ///
"""Trace the glyph bitmaps into outlines and build a web font from them.

Spacing comes from the book too: the gaps between neighbouring letters in
the samples are fitted with a left and right side bearing per glyph, and
pairs whose gaps the side bearings don't explain become kerning pairs.

Usage: uv run tools/font/build_font.py build/glyphs.pkl assets/fonts/dad-lettering.woff2
"""

import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import potrace
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image
from scipy import ndimage

FAMILY = "Dad Lettering"
UPM = 1000
CAP_HEIGHT = 700
UPSAMPLE = 4
MIN_PAIRS = 3  # Pairs seen fewer times than this don't inform spacing.
MIN_KERN_PAIRS = 8
MIN_KERN = 15  # Smaller corrections aren't worth a kerning pair.
# Symbols the book has none of, lettered in Watterson's hand by Codex's
# image generation from the glyphs above: a sheet of 260x260 cells, five
# across, one per character in DRAWN_ORDER, on the same baseline and at the
# same cap height as the glyph bitmaps.
DRAWN = Path(__file__).parent / "drawn.png"
DRAWN_ORDER = "#$%&*+<=>@[\\]^_`{|}~"
DRAWN_CELL = 260
DRAWN_ACROSS = 5

NAMES = {
    "!": "exclam",
    "'": "quotesingle",
    "(": "parenleft",
    ")": "parenright",
    ",": "comma",
    "-": "hyphen",
    ".": "period",
    "?": "question",
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "I.pronoun": "I.pronoun",
    "/": "slash",
    "#": "numbersign",
    "$": "dollar",
    "%": "percent",
    "&": "ampersand",
    "*": "asterisk",
    "+": "plus",
    "<": "less",
    "=": "equal",
    ">": "greater",
    "@": "at",
    "[": "bracketleft",
    "\\": "backslash",
    "]": "bracketright",
    "^": "asciicircum",
    "_": "underscore",
    "`": "grave",
    "{": "braceleft",
    "|": "bar",
    "}": "braceright",
    "~": "asciitilde",
}


def glyph_name(label):
    return NAMES.get(label, label)


def trace(mean, cap, baseline):
    """Outline of a glyph bitmap as a RecordingPen in font units, with x
    measured from the left edge of the ink. Returns (pen, ink width)."""
    smooth = ndimage.gaussian_filter(mean, 0.7)
    h, w = smooth.shape
    big = Image.fromarray((np.clip(smooth, 0, 1) * 255).astype(np.uint8)).resize(
        (w * UPSAMPLE, h * UPSAMPLE), Image.BICUBIC
    )
    ink = np.asarray(big) > 127
    columns = np.flatnonzero(ink.any(axis=0))
    left = columns[0]
    scale = CAP_HEIGHT / (cap * UPSAMPLE)

    def point(p):
        return ((p.x - left) * scale, (baseline * UPSAMPLE - p.y) * scale)

    pen = RecordingPen()
    # Flipping y reverses potrace's contour directions; reversing them again
    # gives the counter-clockwise outer contours CFF expects.
    out = ReverseContourPen(pen)
    for curve in potrace.Bitmap(~ink).trace(turdsize=8, alphamax=1.0, opttolerance=0.4):
        out.moveTo(point(curve.start_point))
        for segment in curve.segments:
            if segment.is_corner:
                out.lineTo(point(segment.c))
                out.lineTo(point(segment.end_point))
            else:
                out.curveTo(point(segment.c1), point(segment.c2), point(segment.end_point))
        out.closePath()
    return pen, (columns[-1] + 1 - left) * scale


def kern_id(label):
    return glyph_name(label).replace(".", "_")


def transformed(pen, transform):
    out = RecordingPen()
    pen.replay(TransformPen(out, transform))
    return out


def combined(*pens):
    out = RecordingPen()
    for pen in pens:
        pen.replay(out)
    return out


def bounds(pen):
    xs = [x for _, args in pen.value for x, _ in args]
    ys = [y for _, args in pen.value for _, y in args]
    return min(xs), min(ys), max(xs), max(ys)


def fit_spacing(gaps, labels):
    """Left and right side bearings (in cap heights) that best explain the
    observed ink gaps between neighbouring letters: gap(a, b) = right(a) +
    left(b). Returns (left, right, residual pairs)."""
    index = {label: i for i, label in enumerate(labels)}
    n = len(labels)
    rows, targets, weights = [], [], []
    observed = {}
    for (a, b), values in gaps.items():
        if a not in index or b not in index or len(values) < MIN_PAIRS:
            continue
        median = float(np.median(values))
        observed[(a, b)] = (median, len(values))
        row = np.zeros(2 * n)
        row[n + index[a]] = 1
        row[index[b]] = 1
        rows.append(row)
        targets.append(median)
        weights.append(np.sqrt(len(values)))
    # Gently prefer letters to be spaced the same on both sides; this also
    # pins down what would otherwise be a free constant.
    typical = float(np.median(targets)) / 2
    for i in range(n):
        for side in (i, n + i):
            row = np.zeros(2 * n)
            row[side] = 1
            rows.append(row)
            targets.append(typical)
            weights.append(0.3)
    a = np.array(rows) * np.array(weights)[:, None]
    t = np.array(targets) * np.array(weights)
    solution, *_ = np.linalg.lstsq(a, t, rcond=None)
    left = dict(zip(labels, solution[:n]))
    right = dict(zip(labels, solution[n:]))
    residuals = {
        pair: (median - right[pair[0]] - left[pair[1]], count)
        for pair, (median, count) in observed.items()
    }
    return left, right, residuals


def main():
    data = pickle.load(open(sys.argv[1], "rb"))
    out_path = Path(sys.argv[2])
    cap, baseline = data["cap"], data["baseline"]
    glyphs = data["glyphs"]
    labels = sorted(glyphs)

    outlines = {}
    widths = {}
    # Alternative forms, cycled through by the calt feature so that repeated
    # letters aren't identical.
    alternates = {}
    for label in labels:
        forms = glyphs[label]["variants"] or [glyphs[label]["mean"]]
        traced = [trace(form, cap, baseline) for form in forms]
        outlines[label], widths[label] = traced[0]
        alternates[label] = [pen for pen, _ in traced[1:]]
    cycle = max(len(alts) for alts in alternates.values()) + 1

    left, right, residuals = fit_spacing(data["gaps"], labels)
    side = {
        label: (left[label] * CAP_HEIGHT, right[label] * CAP_HEIGHT)
        for label in labels
    }

    # Glyphs the book has too few examples of, made from ones it has.
    period, comma, quote = outlines["."], outlines[","], outlines["'"]
    raise_by = 0.5 * CAP_HEIGHT
    outlines[":"] = combined(period, transformed(period, (1, 0, 0, 1, 0, raise_by)))
    outlines[";"] = combined(comma, transformed(period, (1, 0, 0, 1, 0, raise_by)))
    side[":"] = side[";"] = side["."]
    quote_gap = widths["'"] + 0.1 * CAP_HEIGHT
    outlines['"'] = combined(quote, transformed(quote, (1, 0, 0, 1, quote_gap, 0)))
    side['"'] = side["'"]
    dot_gap = widths["."] + 0.12 * CAP_HEIGHT
    outlines["..."] = combined(
        period,
        transformed(period, (1, 0, 0, 1, dot_gap, 0)),
        transformed(period, (1, 0, 0, 1, 2 * dot_gap, 0)),
    )
    side["..."] = side["."]
    # The only 6 in the book is in heavy lettering; a 9 turned upside down
    # is much closer to how Watterson draws a 6.
    x0, y0, x1, y1 = bounds(outlines["9"])
    outlines["6"] = transformed(outlines["9"], (-1, 0, 0, -1, x0 + x1, y0 + y1))
    side["6"] = side["9"]
    # The book has no slashes to speak of; Watterson's would be a stroke
    # like the I's, leaning over to the right.
    outlines["/"] = transformed(outlines["I"], (1, 0, 0.45, 1, 0, 0))
    side["/"] = side["I"]
    for label, stretch in (("endash", 1.8), ("emdash", 3.2)):
        outlines[label] = transformed(outlines["-"], (stretch, 0, 0, 1, 0, 0))
        side[label] = side["-"]
    NAMES["..."] = "ellipsis"
    NAMES[":"] = "colon"
    NAMES[";"] = "semicolon"
    NAMES['"'] = "quotedbl"
    sheet = np.asarray(Image.open(DRAWN).convert("L")) < 128
    typical_side = tuple(np.median([s[k] for s in side.values()]) for k in (0, 1))
    for i, char in enumerate(DRAWN_ORDER):
        row, column = divmod(i, DRAWN_ACROSS)
        cell = sheet[
            row * DRAWN_CELL : (row + 1) * DRAWN_CELL,
            column * DRAWN_CELL : (column + 1) * DRAWN_CELL,
        ]
        outlines[char], widths[char] = trace(cell.astype(np.float32), cap, baseline)
        side[char] = typical_side

    spaces = [s for s in data["spaces"] if s < 1.5]
    typical_left = np.median([l for l, _ in side.values()])
    typical_right = np.median([r for _, r in side.values()])
    space_width = round(np.median(spaces) * CAP_HEIGHT - typical_left - typical_right)

    names = [".notdef", "space"]
    charstrings = {}
    metrics = {}

    notdef = T2CharStringPen(500, None)
    for rect in ((50, 0, 450, 700), (100, 50, 400, 650)):
        x0, y0, x1, y1 = rect
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if rect[0] == 100:
            pts.reverse()
        notdef.moveTo(pts[0])
        for p in pts[1:]:
            notdef.lineTo(p)
        notdef.closePath()
    charstrings[".notdef"] = notdef.getCharString()
    metrics[".notdef"] = (500, 50)
    # Spaces come in as many forms as letters do, all alike, so that the
    # cycle of alternates carries on from one word to the next.
    for i in range(cycle):
        name = "space" if i == 0 else f"space.alt{i}"
        charstrings[name] = T2CharStringPen(space_width, None).getCharString()
        metrics[name] = (space_width, 0)
        if i:
            names.append(name)

    def add(name, pen, lsb, rsb):
        x0, _, x1, _ = bounds(pen)
        advance = round(lsb + (x1 - x0) + rsb)
        cs = T2CharStringPen(advance, None)
        pen.replay(TransformPen(cs, (1, 0, 0, 1, lsb - x0, 0)))
        charstrings[name] = cs.getCharString()
        metrics[name] = (advance, round(lsb))
        names.append(name)

    forms = {}
    for label, pen in outlines.items():
        name = glyph_name(label)
        lsb, rsb = side[label]
        add(name, pen, lsb, rsb)
        forms[label] = [name]
        for i, alternate in enumerate(alternates.get(label, []), start=1):
            add(f"{name}.alt{i}", alternate, lsb, rsb)
            forms[label].append(f"{name}.alt{i}")

    cmap = {0x20: "space", 0xA0: "space"}
    for label in outlines:
        if len(label) == 1:
            cmap[ord(label)] = glyph_name(label)
            if label.isalpha():
                cmap[ord(label.lower())] = glyph_name(label)
    cmap.update({
        0x2018: "quotesingle",
        0x2019: "quotesingle",
        0x201C: "quotedbl",
        0x201D: "quotedbl",
        0x2026: "ellipsis",
        0x2013: "endash",
        0x2014: "emdash",
        0x2010: "hyphen",
        0x2011: "hyphen",
    })

    letters = " ".join(
        glyph_name(label) for label in outlines if len(label) == 1 and label.isalnum()
    )
    # Kerning applies to every form of a glyph.
    kern_classes = []
    kerns = []
    for (a, b), (residual, count) in sorted(residuals.items()):
        value = round(residual * CAP_HEIGHT)
        if count >= MIN_KERN_PAIRS and abs(value) >= MIN_KERN:
            kerns.append(f"  pos @k_{kern_id(a)} @k_{kern_id(b)} {value};")
    for label, names_ in forms.items():
        kern_classes.append(f"@k_{kern_id(label)} = [{' '.join(names_)}];")

    # Rotate through the alternates: a glyph following form i of anything
    # becomes form i + 1. Only characters with a full set take part.
    cycled = [label for label, f in forms.items() if len(f) == cycle]
    cycle_classes = []
    for i in range(cycle):
        members = [forms[label][i] for label in cycled]
        members.append("space" if i == 0 else f"space.alt{i}")
        cycle_classes.append(f"@cycle{i} = [{' '.join(members)}];")
    cycle_rules = [
        f"  sub @cycle{i} @cycle0' by @cycle{i + 1};" for i in range(cycle - 1)
    ]
    features = f"""
languagesystem DFLT dflt;
languagesystem latn dflt;

@letter = [{letters}];
{chr(10).join(kern_classes)}
{chr(10).join(cycle_classes)}

# Watterson letters the pronoun I with serifs and an I inside a word as a
# plain stroke.
feature calt {{
  ignore sub @letter I';
  ignore sub I' @letter;
  sub I' by I.pronoun;
}} calt;

feature calt {{
  lookup cycle {{
{chr(10).join(cycle_rules)}
  }} cycle;
}} calt;

feature kern {{
{chr(10).join(kerns)}
}} kern;
"""

    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(FAMILY.replace(" ", ""), {"FullName": FAMILY}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=900, descent=-250)
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{FAMILY} Regular",
        "fullName": FAMILY,
        "psName": FAMILY.replace(" ", "") + "-Regular",
        "version": "Version 1.0",
    })
    fb.setupOS2(
        sTypoAscender=900,
        sTypoDescender=-250,
        sTypoLineGap=0,
        usWinAscent=1000,
        usWinDescent=300,
        sCapHeight=CAP_HEIGHT,
        sxHeight=CAP_HEIGHT,
    )
    fb.setupPost()
    addOpenTypeFeaturesFromString(fb.font, features)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fb.font.flavor = "woff2"
    fb.save(out_path)
    fb.font.flavor = None
    fb.save(Path("build") / (out_path.stem + ".otf"))
    print(f"{len(names)} glyphs, {len(kerns)} kerning pairs, space {space_width}")


if __name__ == "__main__":
    main()
