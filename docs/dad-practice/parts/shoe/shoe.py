"""Watterson-style shoe for Dad.

    draw(pen, hw, view, heel, toe, **extra)

pen   : ink.Ink canvas.  hw : head width in pixels (line weights scale with it).
view  : 'side' | 'three_quarter' | 'front' | 'sole'
heel, toe : (x, y) points.
    side: the two ends of the sole's ground line (toe may be left or right of
        heel; the shoe's top is on the upper side of the picture).  |toe-heel|
        is the shoe's length (~0.94 hw).
    three_quarter: the same two ends, but the shoe is seen from its laced, upper
        side: the ground contour is the heavy edge on one side of the axis, the
        top of the foot (laces, eyelets) on the other (right of heel->toe
        direction when the axis points down the picture).
    front / sole: heel = the heel end of the long axis, toe = the other end.
        front: the toe dome is at `toe`, the open ankle end at `heel`.
        sole: sole turned up to the viewer; heel end carries the heel band.
Drawn white-filled so it hides what is behind it.  Every extra below is optional.

Extras, side view:
    height=0.40    shoe height at heel/collar as a fraction of length.
    taper=0.0      0 = blunt rounded loaf toe, 1 = long tapering wedge that comes
                   to a point (shoe seen in a stride, foreshortened).
    toe_lift=0.0   raises the toe tip off the ground line (fraction of height).
    heel_scale=1.0 scales the height of the heel half (tall bunched heel > 1).
    laces=3        number of chunky lace marks (0 disables).
    toe_seam=True  rounded toe-cap seam.
    sole_band_pos=0.12 height of that line (fraction of shoe height).
    sole_band=True thin second line parallel to the sole (the sole's top edge).
    folds=0        1-3 short crease strokes across the instep (bunched shoe).
    ankle=True     white ankle oval at the heel opening (only with cuff).
    cuff=True      black trouser cuff over the heel opening; its lower edge
                   follows the ankle and the heel tucks under it.
    cuff_end=0.66  u where the cuff's top-right corner sits (a larger value slopes
                   its right edge outward; use ~1.1 when the leg fills the frame).
    cuff_rise=0.5  how far the cuff reaches up (fractions of length).
    leg_lean=0     degrees the leg leans (cuff shears with it; +leans toward toe).
    tilt=0.0       degrees; rotates the shape about the heel (toe-up positive).
    sole_weight=1  multiplier on the heavy sole line.
Three-quarter view: width=0.42 (shoe breadth / length), laces, cuff, cuff_rise,
    sole_weight.
Front view: width=0.58 (breadth / length), laces=2, cuff=False (black band at the
    open end), cuff_rise, pair=None.
Sole view: width=0.5 (breadth / length), heel_line=True, heel_pos=0.36 (fraction
    of length from the heel end), heel_tilt=0 (degrees), shade=1 (+1/-1: which
    side carries the heavy contour), pair=None.
front and sole: pair=(dx, dy) draws a second, companion shoe behind, offset from
    the first by (dx, dy) in units of this shoe's length; pair_scale=0.92,
    pair_angle=0 (degrees the companion's axis is rotated).
"""
import math
import sys

import numpy as np

sys.path.insert(0, '/Users/drmaciver/Projects/calvins-dad/tools/extensions/reconstruction-v2')
import ink  # noqa: E402
from skimage.draw import polygon as _polygon  # noqa: E402

BLACK, WHITE = 0, 255


class _Frame:
    """Local coordinates: u along heel->toe, v 'up', both in units of the length."""

    def __init__(self, heel, toe, tilt=0.0, mirror_up=True, lean=0.0):
        self.heel = np.asarray(heel, float)
        d = np.asarray(toe, float) - self.heel
        self.L = float(np.linalg.norm(d))
        self.d = d / self.L
        n = np.array([self.d[1], -self.d[0]])
        if mirror_up and n[1] > 0:
            n = -n
        self.n = n
        self.tilt = math.radians(tilt)

    def __call__(self, pts):
        p = np.asarray(pts, float).reshape(-1, 2)
        u, v = p[:, 0], p[:, 1]
        if self.tilt:
            c, s = math.cos(self.tilt), math.sin(self.tilt)
            u, v = u * c - v * s, u * s + v * c
        return self.heel + np.outer(u, self.d) * self.L + np.outer(v, self.n) * self.L


def _poly_mask(pen, pts):
    w, h = pen.size
    rr, cc = _polygon(pts[:, 1], pts[:, 0], (h, w))
    m = np.zeros((h, w), bool)
    m[rr, cc] = True
    return m


def _resample(curve, n):
    seg = np.linalg.norm(np.diff(curve, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, curve[:, 0]), np.interp(t, s, curve[:, 1])], axis=1)


def _lerp(a, b, t):
    return [tuple((1 - t) * np.array(p) + t * np.array(q)) for p, q in zip(a, b)]


def _outline(pen, F, local_pts, wfun, closed=True, n=150, fill=True, wobble=1.0):
    """Fill a smooth local-space outline and stroke it with a width profile
    wfun(u, v, k) -> width in px, where k is the fraction along the curve."""
    curve = ink.spline(local_pts, closed=closed, samples=10)
    if closed:
        curve = np.vstack([curve, curve[:1]])
    curve = _resample(curve, n)
    k = np.linspace(0, 1, n)
    widths = np.array([wfun(u, v, kk) for (u, v), kk in zip(curve, k)])
    P = F(curve)
    if fill:
        pen.fill(P[:-1] if closed else P, WHITE, wobble=0.6)
    pen.stroke(P[:-1] if closed else P, widths[:-1] if closed else widths, BLACK, wobble=wobble, closed=closed)
    return P


def _bar(pen, F, pts, w0, w1, w2, wob=0.5):
    """A tapered brush mark given in local coordinates."""
    pen.stroke(F(pts), [w0, w1, w2], BLACK, wobble=wob)


# ---------------------------------------------------------------- side
def _side(pen, hw, F, p):
    h = p['height']
    T = p['taper']
    thin, med, heavy = 0.03 * hw, 0.05 * hw, 0.075 * hw * p['sole_weight']
    hs = p['heel_scale']
    lift = p['toe_lift'] * h

    bottom = [(0.075, 0.03 * h), (0.22, -0.002), (0.5, -0.016), (0.77, -0.006), (0.92, 0.012 * h + lift * 0.4)]
    toe_round = [(0.99, 0.15 * h), (1.0, 0.36 * h), (0.97, 0.68 * h), (0.88, 0.90 * h), (0.76, 1.0 * h)]
    toe_point = [(1.0, 0.07 * h + lift), (1.005, 0.10 * h + lift), (0.92, 0.22 * h), (0.78, 0.38 * h), (0.64, 0.54 * h)]
    toe = _lerp(toe_round, toe_point, T)
    back_round = [(0.64, 1.02 * h), (0.55, 0.86 * h), (0.42, 0.76 * h), (0.29, 0.86 * h * hs),
                  (0.15, 0.98 * h * hs), (0.03, 0.80 * h * hs), (-0.012, 0.50 * h * hs), (-0.005, 0.22 * h)]
    back_point = [(0.56, 0.60 * h), (0.46, 0.55 * h), (0.34, 0.66 * h), (0.22, 0.86 * h * hs),
                  (0.12, 1.0 * h * hs), (0.03, 0.78 * h * hs), (-0.012, 0.45 * h * hs), (-0.005, 0.22 * h)]
    back = _lerp(back_round, back_point, T)
    sil = bottom + toe + back

    def wfun(u, v, k):
        sole_d = max(0.0, 1 - max(v, 0) / (0.42 * h))       # nearness to the ground
        sole = sole_d ** 1.4
        ends = min(1.0, max(0.0, (u - 0.02) / 0.10), max(0.0, (1.0 - u) / 0.06 + 0.35))
        pressure = 0.78 + 0.22 * math.sin(k * 40) * math.sin(k * 7)
        base = thin * 1.15 + (med - thin * 1.15) * (1 - sole_d)
        w = base + (heavy - base) * sole * (0.55 + 0.45 * min(1, ends)) * pressure
        if v > 0.55 * h and 0.3 < u < 0.7:
            w = thin * 0.85
        elif v > 0.6 * h:
            w = max(thin * 0.9, w * 0.75)
        return w

    _outline(pen, F, sil, wfun)

    # sole band: the sole's upper edge, a thin line parallel to the ground contour
    if p['sole_band']:
        e0, e1 = 0.12, (0.72 if p['toe_seam'] else 0.9) - 0.18 * T
        bh = p['sole_band_pos'] * h
        pts = [(e0, bh * 1.05), (0.3, bh), (0.55, bh * 0.9), (e1 - 0.1, bh * 0.85 + lift * 0.15 * 0.4), (e1, bh * 0.9 + lift * 0.3)]
        _bar(pen, F, pts, thin * 0.35, thin * 0.95, thin * 0.35, 0.5) if False else \
            pen.stroke(F(pts), [thin * 0.2, thin * 0.7, thin * 0.8, thin * 0.7, thin * 0.2], BLACK, wobble=0.6)

    # collar / opening line: from the heel, under the ankle, up into the vamp
    cx = 0.58 - 0.08 * T
    col = [(0.06, 0.52 * h * hs), (0.24, 0.49 * h), (0.42, 0.44 * h), (cx, 0.52 * h), (cx + 0.06, 0.78 * h), (cx + 0.08, 0.94 * h)]
    pen.stroke(F(col), [thin * 0.4, med * 1.0, med * 0.9, thin * 1.1, thin * 0.5, thin * 0.3], BLACK, wobble=0.8)

    # laces: chunky tapered bars crossing the tongue, perpendicular to the instep
    n = p['laces']
    for i in range(n):
        t = (i + 0.5) / max(n, 1)
        u0 = cx + 0.015 + 0.15 * t * (1 - 0.5 * T)
        vb = (0.62 + 0.20 * t * (1 - 0.35 * T)) * h
        ln = 0.13 * h / 0.36 + 0.02
        pen.stroke(F([(u0 - 0.05, vb - 0.07 * h), (u0 + 0.005, vb + 0.02 * h), (u0 + 0.045, vb + ln * 0.55 * h)]),
                   [thin * 0.5, med * 1.15, thin * 0.35], BLACK, wobble=0.5)

    # toe-cap seam
    if p['toe_seam'] and T < 0.85:
        us = 0.80 - 0.10 * T
        seam = [(us + 0.02, 0.84 * h * (1 - 0.2 * T)), (us - 0.025, 0.52 * h), (us - 0.02, 0.22 * h), (us + 0.03, 0.045 * h)]
        pen.stroke(F(seam), [thin * 0.2, thin * 0.6, thin * 0.5, thin * 0.2], BLACK, wobble=0.6)

    # folds: creases of a bunched shoe over the instep
    for i in range(p['folds']):
        u0 = 0.32 + 0.12 * i
        pen.stroke(F([(u0, 0.60 * h), (u0 + 0.07, 0.42 * h), (u0 + 0.16, 0.30 * h)]),
                   [thin * 0.3, thin * 1.1, thin * 0.3], BLACK, wobble=0.6)

    # ankle oval and cuff
    if p['ankle']:
        ov = [(0.15, 0.58 * h * hs), (0.19, 0.70 * h * hs), (0.28, 0.72 * h * hs), (0.31, 0.60 * h * hs), (0.24, 0.52 * h * hs)]
        pen.fill(F(ov), WHITE, wobble=0.4)
        pen.stroke(F(ov), [thin, med * 1.2, thin, med], BLACK, wobble=0.6, closed=True)
    if p['cuff']:
        lean = math.radians(p['leg_lean'])
        top = 1.0 * h + p['cuff_rise']

        def sh(pts):
            return [(u + math.tan(lean) * max(v - h, 0), v) for u, v in pts]

        low = [(-0.03, 0.66 * h), (0.05, 0.85 * h), (0.17, 0.78 * h), (0.30, 0.90 * h), (0.46, 0.97 * h), (0.58, 1.08 * h)]
        lowc = ink.spline(low, samples=10)
        poly = np.vstack([lowc, np.array(sh([(p['cuff_end'], top), (-0.04, top), (-0.05, 0.8 * h)]))])
        P = F(poly)
        pen.paint(_poly_mask(pen, P), BLACK)
        pen.stroke(F(lowc), [thin, heavy * 0.85, heavy * 0.7, med, thin], BLACK, wobble=0.8)


# ---------------------------------------------------------------- three quarter
def _three_quarter(pen, hw, F, p):
    W = p['width']
    thin, med, heavy = 0.03 * hw, 0.05 * hw, 0.085 * hw * p['sole_weight']
    sil = [(0.03, 0.10 * W), (0.30, -0.01 * W), (0.62, 0.0), (0.90, 0.10 * W), (1.0, 0.45 * W), (0.95, 0.85 * W),
           (0.78, 1.0 * W), (0.52, 0.96 * W), (0.30, 0.88 * W), (0.12, 0.96 * W), (0.0, 0.55 * W)]

    def wfun(u, v, k):
        g = max(0.0, 1 - v / (0.45 * W))
        base = med * (0.8 if v > 0.5 * W else 1.0)
        return base + (heavy - base) * g ** 1.2 * min(1, (u + 0.1) * 3, (1.15 - u) * 6)

    _outline(pen, F, sil, wfun)
    # laced strip: black tongue band with white bars and an eyelet
    n = p['laces']
    band = [(0.14, 0.52 * W), (0.20, 0.82 * W), (0.50, 0.84 * W), (0.66, 0.74 * W), (0.62, 0.50 * W), (0.40, 0.46 * W)]
    pen.fill(F(band), BLACK, wobble=0.5)
    pen.fill(F([(0.19, 0.64 * W), (0.215, 0.74 * W), (0.25, 0.72 * W), (0.24, 0.62 * W)]), WHITE, wobble=0.3)
    for i in range(n):
        t = (i + 0.5) / max(n, 1)
        u0 = 0.30 + 0.30 * t
        pen.stroke(F([(u0 - 0.02, 0.55 * W), (u0 + 0.02, 0.66 * W), (u0 + 0.0, 0.76 * W)]),
                   [thin * 0.8, med * 1.2, thin * 0.8], WHITE, wobble=0.3)
    # toe cap seam
    pen.stroke(F([(0.76, 0.12 * W), (0.80, 0.45 * W), (0.74, 0.78 * W)]), [thin * 0.3, thin, thin * 0.3], BLACK, wobble=0.5)
    if p['cuff']:
        poly = F([(-0.35 * p['cuff_rise'] * 2, -0.2 * W), (0.0, 0.05 * W), (0.10, 0.55 * W), (0.16, 1.1 * W), (-0.35 * p['cuff_rise'] * 2, 1.3 * W)])
        pen.paint(_poly_mask(pen, poly), BLACK)
        pen.stroke(F([(0.0, 0.1 * W), (0.10, 0.5 * W), (0.17, 1.0 * W)]), [med, heavy * 0.8, med], BLACK, wobble=0.6)


# ---------------------------------------------------------------- front
def _front(pen, hw, F, p):
    thin, med, heavy = 0.03 * hw, 0.05 * hw, 0.085 * hw * p['sole_weight']
    w = p['width'] / 2
    u0 = 0.40
    pts = []
    for u in np.linspace(0.0, 1.0, 13):
        if u <= u0:
            s = 0.93 + 0.07 * u / u0
        else:
            x = (u - u0) / (1 - u0)
            s = (1 - x ** 2.3) ** (1 / 2.3)
        pts.append((u, w * max(s, 0.0)))
    left = [(u, -v) for u, v in pts][::-1]
    right = pts
    # fill: closed shape with the ankle end closed under the cuff
    fill_pts = [(0.0, -w * 0.93)] + [(u, -v) for u, v in pts[1:-1]] + [(1.0, 0.0)] + [(u, v) for u, v in pts[-2:0:-1]] + [(0.0, w * 0.93)]
    pen.fill(F(fill_pts), WHITE, wobble=0.6)

    def wf(side):
        def f(u, v, k):
            along = 1.0 - 0.35 * min(1, abs(u - 0.5) * 2) if False else 1.0
            outer = 1.0 if side * p.get('shade', 1) > 0 else 0.0
            return (med * 0.75 + (heavy - med * 0.75) * outer) * (0.6 + 0.4 * min(1, u * 4 + 0.2)) * (0.75 + 0.25 * (1 - min(1, abs(u - 0.7) * 3)))
        return f

    for side, seq in ((-1, left), (1, right[::-1])):
        pass
    # one open stroke around the sides and the toe, from the ankle end on one side to the other
    arc = [(u, -v) for u, v in pts[1:]] [:-1] + [(1.0, 0.0)] + [(u, v) for u, v in pts[1:][::-1][1:]]
    arc = [(0.0, -w * 0.93)] + [(u, -v) for u, v in pts[1:-1]] + [(1.0, 0.0)] + [(u, v) for u, v in pts[-2:0:-1]] + [(0.0, w * 0.93)]
    curve = ink.spline(arc, samples=10)
    curve = _resample(curve, 140)
    k = np.linspace(0, 1, 140)
    widths = []
    for kk in k:
        side_heavy = 1.0 - kk if p['shade'] > 0 else kk
        top = 1 - abs(kk - 0.5) * 2
        wv = med * 0.8 + (heavy - med * 0.8) * (side_heavy ** 1.2) * (0.35 + 0.65 * (1 - top ** 3))
        widths.append(wv * (0.9 + 0.1 * math.sin(kk * 31)))
    pen.stroke(F(curve), widths, BLACK, wobble=1.0)
    # inner toe-cap line: concentric with the dome, thin
    inner = [(0.40, -w * 0.80), (0.58, -w * 0.78), (0.76, -w * 0.58), (0.86, -w * 0.30), (0.88, 0.0), (0.86, w * 0.30), (0.76, w * 0.58), (0.58, w * 0.78), (0.40, w * 0.80)]
    pen.stroke(F(inner), [thin * 0.3, thin * 0.9, thin, thin * 0.9, thin * 0.3], BLACK, wobble=0.6)
    # laces: curved bars, convex toward the toe
    for i in range(p['laces']):
        u = 0.32 - 0.12 * i + 0.1 * (1 if p['laces'] < 3 else 0)
        pen.stroke(F([(u - 0.01, -w * 0.82), (u + 0.025, -w * 0.4), (u + 0.035, 0.0), (u + 0.025, w * 0.4), (u - 0.01, w * 0.82)]),
                   [thin * 0.4, thin * 1.3, thin * 1.5, thin * 1.3, thin * 0.4], BLACK, wobble=0.5)
    if p['cuff']:
        r = p['cuff_rise']
        poly = F([(-r, -w * 1.1), (0.0, -w * 1.0), (0.08, -w * 0.8), (0.14, 0.0), (0.08, w * 0.8), (0.0, w * 1.0), (-r, w * 1.1)])
        pen.paint(_poly_mask(pen, poly), BLACK)


# ---------------------------------------------------------------- sole
def _sole(pen, hw, F, p):
    thin, med, heavy = 0.03 * hw, 0.05 * hw, 0.085 * hw * p['sole_weight']
    w = p['width'] / 2
    pw = 2.4
    pts = []
    us = np.linspace(0.0, 1.0, 29)
    for u in us:
        s = max(0.0, 1 - abs(2 * u - 1) ** pw) ** (1 / pw)
        pts.append((u, s * w * (0.88 + 0.22 * u)))
    outline = [(u, v) for u, v in pts[1:-1]] + [(1.0, 0.0)] + [(u, -v) for u, v in pts[-2:0:-1]] + [(0.0, 0.0)]
    # make it lumpy: slight asymmetry
    outline = [(u, v * (1.0 if v > 0 else 0.97) + 0.01 * math.sin(7 * u)) for u, v in outline]
    shade = p['shade']

    def wfun(u, v, k):
        side = 1.0 if v * shade < 0 else 0.0
        ends = max(0.0, 1 - min(u, 1 - u) / 0.12)
        return thin * 1.1 + (heavy - thin * 1.1) * max(side ** 1.0 * (0.5 + 0.5 * math.sin(math.pi * u)), ends * 0.7)

    _outline(pen, F, outline, wfun, n=160)
    if p['heel_line']:
        u = p['heel_pos']
        a = math.radians(p['heel_tilt'])
        half = w * max(0.0, 1 - abs(2 * u - 1) ** pw) ** (1 / pw) * (0.88 + 0.22 * u)
        for du, wt in ((0.0, 1.0), (0.065, 0.85)):
            ua = u + du
            hf = half * 0.97
            pts2 = [(ua - 0.012 + math.sin(a) * hf, -hf), (ua - 0.004, -hf * 0.4), (ua + 0.004, hf * 0.4), (ua + 0.012 - math.sin(a) * hf, hf)]
            pen.stroke(F(pts2), [thin * 0.6, med * 1.2 * wt, med * 1.2 * wt, thin * 0.6], BLACK, wobble=0.7)


def _pair(pen, hw, view, heel, toe, p, drawer):
    off = p.get('pair')
    if not off:
        return
    heel = np.asarray(heel, float)
    toe = np.asarray(toe, float)
    d = toe - heel
    L = np.linalg.norm(d)
    h2 = heel + np.array(off) * L
    sc = p.get('pair_scale', 0.92)
    a = math.radians(p.get('pair_angle', 0.0))
    c, s = math.cos(a), math.sin(a)
    d2 = np.array([d[0] * c - d[1] * s, d[0] * s + d[1] * c]) * sc
    q = dict(p, pair=None)
    q['shade'] = -p['shade']
    q['cuff'] = False
    drawer(pen, hw, view, tuple(h2), tuple(h2 + d2), q)


_DEFAULTS = dict(height=0.40, taper=0.0, toe_lift=0.0, heel_scale=1.0, laces=3, toe_seam=True, sole_band=True, sole_band_pos=0.2,
                 folds=0, ankle=True, cuff=True, cuff_rise=0.5, leg_lean=0.0, tilt=0.0, sole_weight=1.0,
                 width=None, heel_line=True, heel_pos=0.36, heel_tilt=0.0, shade=1, pair=None,
                 pair_scale=0.92, pair_angle=0.0, cuff_end=0.66)


def _draw(pen, hw, view, heel, toe, p):
    p = dict(p)
    if view == 'side':
        _side(pen, hw, _Frame(heel, toe, p['tilt']), p)
    elif view == 'three_quarter':
        p['width'] = p['width'] or 0.42
        _three_quarter(pen, hw, _Frame(heel, toe, 0, mirror_up=False), p)
    elif view == 'front':
        p['width'] = p['width'] or 0.58
        if p['pair']:
            _pair(pen, hw, view, heel, toe, p, lambda *a: _draw(*a))
        _front(pen, hw, _Frame(heel, toe, 0, mirror_up=False), p)
    elif view == 'sole':
        p['width'] = p['width'] or 0.5
        if p['pair']:
            _pair(pen, hw, view, heel, toe, p, lambda *a: _draw(*a))
        _sole(pen, hw, _Frame(heel, toe, 0, mirror_up=False), p)
    else:
        raise ValueError(view)


def draw(pen, hw, view, heel, toe, **extra):
    unknown = set(extra) - set(_DEFAULTS) - {'pair_scale', 'pair_angle'}
    if unknown:
        raise TypeError('unknown shoe extras: %s' % sorted(unknown))
    p = dict(_DEFAULTS)
    p.update(extra)
    _draw(pen, hw, view, heel, toe, p)
