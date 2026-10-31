# /// script
# dependencies = ["numpy", "scipy", "pillow", "wordfreq"]
# ///
"""Turn the extracted letter samples into one clean bitmap per character.

Every sample is scaled to a common cap height and placed on a common
baseline. For each character we find the medoid sample (the one most like
all the others), align the closest samples to it and average them.

The OCR labels are not always right (it often reads Watterson's Y as an X,
for example), so before that we drop words that aren't English and samples
that look more like a well-attested different character. Averaging many
real samples keeps Watterson's letterforms while smoothing out the scanning
noise and one-off wobbles.

Usage: uv run tools/font/glyphs.py build/samples.pkl build/glyphs.pkl
"""

import pickle
import sys
from collections import defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage
from wordfreq import zipf_frequency

CAP = 120  # Cap height, in pixels, of the normalised bitmaps.
FRAME_W = 260
FRAME_H = 260
BASELINE = 190  # Row of the baseline in the frame.
MAX_SAMPLES = 400
AVERAGE = 40  # How many of the best samples to average.

# The pronoun I is drawn with serifs; I inside words is a plain stroke.
PRONOUN_I = "I.pronoun"

# Characters that genuinely look alike, so resemblance between them is no
# sign of a misreading.
LOOKALIKES = [{"O", "0"}, {"I", "1", PRONOUN_I}, {",", "'"}]
# Words this far down the page are page numbers, not lettering.
PAGE_NUMBER_Y = 0.95


def normal_words(words):
    """Words in ordinary lettering: not the big, bold or tiny text used for
    shouting, sound effects and the like, and not typeset page numbers."""
    caps = np.array([w["cap"] for w in words])
    strokes = np.array([w["stroke"] for w in words])
    cap_lo, cap_hi = np.percentile(caps, [10, 85])
    stroke_lo, stroke_hi = np.percentile(strokes, [10, 85])
    return [
        w
        for w in words
        if cap_lo <= w["cap"] <= cap_hi and stroke_lo <= w["stroke"] <= stroke_hi
    ]


def plausible(word):
    """Whether the OCR reading of the word is believable: an English word
    (or name), or a number that isn't a page number."""
    core = word["text"].strip(".,!?:;()-'")
    if not core:
        return True
    if core.isdigit():
        return word["y"] < PAGE_NUMBER_Y
    return zipf_frequency(core.lower(), "en") >= 1.5


# Hand-lettered numbers are rare in the book and most OCR'd "digits" are
# misread letters, so the digits 2-9 come only from these instances, picked
# out by eye: (page index, OCR text of the word).
DIGIT_SOURCES = {
    "2": {(15, "20"), (18, "12"), (136, "2AM"), (145, "200-"), (210, "20")},
    "3": {(137, "-33:"), (137, "10:3)")},
    "4": {(243, "40")},
    "5": {(80, "75,"), (107, "5:30"), (203, "957")},
    "6": {(215, "6:00")},
    "7": {(14, "77"), (80, "75,"), (94, "70"), (203, "957"), (205, "70")},
    "8": {(140, "18?")},
    "9": {(203, "957")},
}


def plausible_digit(word, letter):
    """Digits are taken from lettering of any size. 2-9 must come from the
    hand-picked instances; for 0 and 1, which are common enough to filter
    automatically, this rejects shapes that can't be a single digit (usually
    several characters run together)."""
    if letter["char"] in DIGIT_SOURCES:
        return (word["page"], word["text"]) in DIGIT_SOURCES[letter["char"]]
    width = letter["x1"] - letter["x0"]
    return 0.8 <= letter["top"] <= 1.25 and abs(letter["bottom"]) <= 0.1 and width <= 0.9


def lookalike(a, b):
    return any(a in group and b in group for group in LOOKALIKES)


def drop_misreadings(descs):
    """Remove samples that sit squarely among the samples of a different,
    better attested character. `descs` maps label -> array of descriptors;
    returns label -> indices to keep."""
    centres = {}
    for label, d in descs.items():
        m = medoid(d)
        spread = np.median(np.linalg.norm(d - d[m], axis=1))
        centres[label] = (d[m], spread, len(d))
    keep = {}
    for label, d in descs.items():
        ok = np.ones(len(d), dtype=bool)
        if label in DIGIT_SOURCES:
            # Already checked by hand.
            keep[label] = np.arange(len(d))
            continue
        for other, (centre, spread, count) in centres.items():
            if other == label or count <= len(d) or lookalike(label, other):
                continue
            ok &= np.linalg.norm(d - centre, axis=1) >= spread
        keep[label] = np.flatnonzero(ok)
    return keep


def label_for(word, index):
    char = word["letters"][index]["char"]
    if char == "I" and index == 0:
        text = word["text"]
        if text == "I" or text.startswith("I'") or text[1:] in {".", ",", "!", "?"}:
            return PRONOUN_I
    return char


def normalise(letter, cap):
    """Scale a sample to the common cap height and place it in a frame with
    its baseline at BASELINE and its ink centred horizontally. Returns a float
    image in [0, 1]."""
    mask = np.unpackbits(letter["mask"], axis=1)[:, : letter["shape"][1]]
    scale = CAP / cap
    h = max(1, round(mask.shape[0] * scale))
    w = max(1, round(mask.shape[1] * scale))
    if h >= FRAME_H or w >= FRAME_W:
        return None
    img = Image.fromarray((mask * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    small = np.asarray(img).astype(np.float32) / 255
    frame = np.zeros((FRAME_H, FRAME_W), dtype=np.float32)
    top = round(BASELINE - letter["top"] * CAP)
    left = (FRAME_W - w) // 2
    if top < 0 or top + h > FRAME_H:
        return None
    frame[top : top + h, left : left + w] = small
    return frame


def medoid(descs):
    sq = (descs**2).sum(axis=1)
    dist = np.sqrt(np.maximum(sq[:, None] + sq[None, :] - 2 * descs @ descs.T, 0))
    return int(np.argmin(dist.sum(axis=1)))


def descriptor(frame):
    small = ndimage.gaussian_filter(frame, 4)[::4, ::4]
    return small.ravel()


def best_shift(reference, frame, radius=6):
    """Horizontal and vertical shift of `frame` that best overlaps
    `reference`."""
    best = (0, 0)
    best_score = -1.0
    for dy in range(-radius // 2, radius // 2 + 1):
        for dx in range(-radius, radius + 1):
            score = float((reference * np.roll(frame, (dy, dx), axis=(0, 1))).sum())
            if score > best_score:
                best_score = score
                best = (dy, dx)
    return best


def build(frames, descs):
    centre = medoid(descs)
    order = np.argsort(np.linalg.norm(descs - descs[centre], axis=1))
    chosen = order[: max(1, min(AVERAGE, len(frames) // 2))]
    reference = ndimage.gaussian_filter(frames[centre], 2)
    aligned = []
    for i in chosen:
        dy, dx = best_shift(reference, ndimage.gaussian_filter(frames[i], 2))
        aligned.append(np.roll(frames[i], (dy, dx), axis=(0, 1)))
    mean = np.mean(aligned, axis=0)
    return {
        "mean": mean,
        "medoid": frames[centre],
        "count": len(frames),
        "used": len(chosen),
    }


def spacing_data(words):
    """Observed gaps between neighbouring letters, in cap heights, keyed by
    the pair of labels."""
    gaps = defaultdict(list)
    for word in words:
        letters = word["letters"]
        for i in range(1, len(letters)):
            a = label_for(word, i - 1)
            b = label_for(word, i)
            gaps[(a, b)].append(letters[i]["x0"] - letters[i - 1]["x1"])
    return gaps


def main():
    words = pickle.load(open(sys.argv[1], "rb"))
    words = [w for w in words if plausible(w)]
    normal = {id(w) for w in normal_words(words)}
    samples = defaultdict(list)
    for word in words:
        for i, letter in enumerate(word["letters"]):
            if letter["char"].isdigit():
                if not plausible_digit(word, letter):
                    continue
            elif id(word) not in normal:
                continue
            frame = normalise(letter, word["cap"])
            if frame is not None:
                samples[label_for(word, i)].append(frame)
    rng = np.random.default_rng(0)
    for label, frames in samples.items():
        if len(frames) > MAX_SAMPLES:
            picked = rng.choice(len(frames), MAX_SAMPLES, replace=False)
            samples[label] = [frames[i] for i in picked]
    descs = {
        label: np.stack([descriptor(f) for f in frames])
        for label, frames in samples.items()
    }
    keep = drop_misreadings(descs)
    glyphs = {}
    for label, frames in sorted(samples.items()):
        kept = keep[label]
        if not len(kept) or label in ":;":
            print(label, "too few samples", len(kept))
            continue
        glyphs[label] = build([frames[i] for i in kept], descs[label][kept])
        print(label, len(frames), "->", len(kept), "averaged", glyphs[label]["used"])
    words = [w for w in words if id(w) in normal]
    spaces = [w["space_before"] for w in words if "space_before" in w]
    with open(sys.argv[2], "wb") as f:
        pickle.dump(
            {
                "cap": CAP,
                "baseline": BASELINE,
                "glyphs": glyphs,
                "gaps": dict(spacing_data(words)),
                "spaces": spaces,
            },
            f,
        )


if __name__ == "__main__":
    main()
