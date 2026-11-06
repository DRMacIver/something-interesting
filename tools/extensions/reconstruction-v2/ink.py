"""A small programmatic inking kit for drawing in the strip's manner.

Shapes are given as a few control points, run through Catmull-Rom splines,
and rendered supersampled before thresholding to 1-bit ink, so their edges
are as clean as the smoothed scan. Brush strokes swell and taper along their
length, and every edge gets a slight, smooth wobble so the line doesn't look
mechanical next to Watterson's.
"""
import numpy as np
from PIL import Image, ImageDraw

SUPERSAMPLE = 3


def spline(points, closed=False, samples=24):
    """Catmull-Rom curve through the points (centripetal, so no loops)."""
    p = np.asarray(points, dtype=float)
    if closed:
        p = np.vstack([p[-1], p, p[0], p[1]])
    else:
        p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        t0 = 0.0
        t1 = t0 + max(np.linalg.norm(p1 - p0), 1e-6) ** 0.5
        t2 = t1 + max(np.linalg.norm(p2 - p1), 1e-6) ** 0.5
        t3 = t2 + max(np.linalg.norm(p3 - p2), 1e-6) ** 0.5
        for t in np.linspace(t1, t2, samples, endpoint=False):
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    if not closed:
        out.append(p[-2])
    return np.array(out)


def _normals(curve, closed):
    if closed:
        tangent = np.roll(curve, -1, axis=0) - np.roll(curve, 1, axis=0)
    else:
        tangent = np.gradient(curve, axis=0)
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1, keepdims=True), 1e-9)
    return np.stack([-tangent[:, 1], tangent[:, 0]], axis=1)


def _arclength(curve):
    steps = np.linalg.norm(np.diff(curve, axis=0), axis=1)
    return np.concatenate([[0], np.cumsum(steps)])


class Wobble:
    """Smooth pseudo-random offsets along a line, a few pixels at most."""

    def __init__(self, seed, amplitude=1.6, wavelength=70):
        rng = np.random.default_rng(seed)
        self.terms = [(amplitude * rng.uniform(0.4, 1) / k, wavelength / k,
                       rng.uniform(0, 2 * np.pi)) for k in (1, 2.3, 5.1)]

    def __call__(self, s):
        return sum(a * np.sin(2 * np.pi * s / w + phase) for a, w, phase in self.terms)


class Ink:
    """A canvas to ink on, in the full-panel artwork's pixel coordinates."""

    def __init__(self, size, seed=0):
        self.size = size
        self.image = Image.new('L', tuple(v * SUPERSAMPLE for v in size), 255)
        self.pen = ImageDraw.Draw(self.image)
        self.rng = np.random.default_rng(seed)

    def _poly(self, pts, colour):
        self.pen.polygon([tuple(v * SUPERSAMPLE) for v in pts], fill=colour)

    def fill(self, points, colour=0, wobble=1.6):
        """A solid shape bounded by a smooth closed curve through the points."""
        curve = spline(points, closed=True)
        if wobble:
            s = _arclength(np.vstack([curve, curve[:1]]))[:-1]
            curve = curve + _normals(curve, True) * Wobble(self.rng.integers(1 << 30), wobble)(s)[:, None]
        self._poly(curve, colour)
        return curve

    def stroke(self, points, widths, colour=0, wobble=1.2, closed=False):
        """A brush stroke whose width follows the given profile along its length.

        `widths` is a list of widths spread evenly along the stroke; an open
        stroke's ends are rounded with half its width there.
        """
        curve = spline(points, closed=closed)
        if closed:
            curve = np.vstack([curve, curve[:1]])
        s = _arclength(curve)
        profile = np.interp(s / s[-1], np.linspace(0, 1, len(widths)), widths) / 2
        normals = _normals(curve, False)
        if closed:
            normals[-1] = normals[0]
        left_w = Wobble(self.rng.integers(1 << 30), wobble)(s)
        right_w = Wobble(self.rng.integers(1 << 30), wobble)(s)
        left = curve + normals * np.maximum(profile + left_w, 0.3)[:, None]
        right = curve - normals * np.maximum(profile + right_w, 0.3)[:, None]
        self._poly(np.vstack([left, right[::-1]]), colour)
        if not closed:
            for end, r in ((curve[0], profile[0]), (curve[-1], profile[-1])):
                if r > 0.8:
                    x, y = end * SUPERSAMPLE
                    r *= SUPERSAMPLE
                    self.pen.ellipse((x - r, y - r, x + r, y + r), fill=colour)
        return curve

    def paint(self, mask, colour):
        """Set the pixels of a boolean mask (at the canvas size) to a colour."""
        big = Image.fromarray(mask).resize(self.image.size, Image.Resampling.NEAREST)
        self.image.paste(colour, mask=big.convert('L').point(lambda v: 255 if v else 0))

    def mask(self):
        """The drawing as a boolean ink mask at the canvas size."""
        small = self.image.resize(self.size, Image.Resampling.BOX)
        return np.asarray(small) < 128


def composite(base, drawing, region):
    """Replace `base` inside the boolean `region` with the drawing's ink."""
    a = np.asarray(base).copy()
    a[region] = np.where(drawing[region], 0, 255)
    return Image.fromarray(a)
