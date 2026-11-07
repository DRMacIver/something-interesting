"""One trouser leg of Dad, hip to ankle, in Watterson's brush manner.

    draw(pen, hw, hip, knee, ankle, near=True, light=False, **extra)

pen    an ink.Ink canvas (pixel coordinates of the target image)
hw     Dad's head width in pixels (all sizes scale with it)
hip, knee, ankle   (x, y) joint centres.  The leg is a thigh (hip->knee) and a
       shin (knee->ankle).  Works for a straight column (standing, walking:
       knee roughly on the hip-ankle line) and for sharply bent legs (sitting,
       crouching, kneeling).  The side the knee points to is found
       automatically: that outside of the bend gets a rounded knee bump, the
       inside gets a crisp crook.
near   True: full size.  False: far leg, 8% slimmer, fewer marks.
light  False: solid black trousers: one flat silhouette, rounded knee, a
       tapered cuff with the shin bunching slightly above it, and one to three
       short tapered white nicks (at the knee crook, shin and cuff).
       True: white trousers inside a continuous brush contour (heavier on the
       underside) with a few long straight folds that start at the contour
       and run toward the knee without crossing, a knee crescent and a hem.

Extras (defaults in brackets):
  bagginess [0.3]   0 tight .. 1 very loose: widens the leg, sags the thigh
                    underside and bunches the shin above the cuff.
  folds [None]      number of fold marks (None: 3 black / 5 light; far leg
                    uses fewer).
  cuff [True]       draw the cuff (hem line / nick) at the ankle.
  hip_cap [True]    black: round the hip end (the seat is expected to cover
                    it).  Light: the hip end is left open when True (no line
                    across the thigh top); False closes it with a contour.
  girth [1.0]       overall thickness multiplier (Watterson's seated legs run
                    1.3-1.7 times the nominal 0.6 Hw thigh).
  rim [0.0]         in Hw: thin white halo round a black near leg so it reads
                    in front of black furniture or the far leg.
  knee_bump [1.0]   scale of the rounded knee on the outside of the bend.
  outline [1.0]     scale of the outline weight (light legs).
  seed [0]          varies the brush wobble.
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SS = 4


def _unit(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def _perp(d):
    return np.array([-d[1], d[0]])


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _resample(P, step):
    P = np.asarray(P, float)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(3, int(s[-1] / step) + 1)
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)


def _geometry(hw, hip, knee, ankle, near, bag, bump, cap, cuff, girth, light):
    """Outline of the leg as two paths.  Returns dict with:
    outer  hip-outer -> knee arc -> ankle-outer   (outside of the bend)
    inner  ankle-inner -> crook -> hip-inner       (inside of the bend)
    hem    points across the ankle from outer end to inner end
    cap    points round the hip end from inner end to outer end (black only)"""
    k = (1.0 if near else 0.92) * girth
    hip, knee, ankle = (np.asarray(p, float) for p in (hip, knee, ankle))
    d1, d2 = _unit(knee - hip), _unit(ankle - knee)
    turn = _cross(d1, d2)
    dot = float(d1 @ d2)
    ang = np.arctan2(turn, dot)
    inner = 1 if turn >= 0 else -1
    n1, n2 = inner * _perp(d1), inner * _perp(d2)     # towards the inside of the bend
    L1, L2 = np.linalg.norm(knee - hip), np.linalg.norm(ankle - knee)
    g = 1 + 0.25 * bag
    wh, wk, wa = 0.30 * hw * k * g, 0.225 * hw * k * g, 0.175 * hw * k * (1 + 0.1 * bag)
    step = 0.05 * hw
    nT, nS = max(6, int(L1 / step)), max(6, int(L2 / step))
    t = np.linspace(0, 1, nT)
    sag = np.sin(np.pi * t)
    base1 = wh + (wk - wh) * t
    flare = (1 + (0.16 if not light else 0.0) * np.clip(1 - t / 0.25, 0, 1) ** 2)
    wi1 = base1 * (1 + 0.10 * bag * sag) * flare
    wo1 = base1 * (1 + 0.03 * bag * sag) * flare
    u = np.linspace(0, 1, nS)
    cf = (0.12 * hw * k / L2) if cuff else 0.0
    base2 = wk + (wa * 1.05 - wk) * u ** 0.85
    bunch = 0.05 * hw * bag * k * np.exp(-((u - (1 - cf) + 0.1) / 0.12) ** 2)
    flare2 = 1 + 0.12 * np.clip((u - (1 - cf)) / max(cf, 1e-6), 0, 1) ** 2 * (1 if cuff else 0)
    dip = 1 - 0.07 * np.exp(-((u - (1 - 2.2 * max(cf, 0.05))) / 0.07) ** 2) * (1 if not light else 0.0)
    w2 = (base2 + bunch) * flare2 * dip
    w2 = np.where(u > 1 - cf * 0.5, w2, w2)
    T = hip[None] + d1[None] * (L1 * t)[:, None]
    S = knee[None] + d2[None] * (L2 * u)[:, None]
    thigh_in = T + n1[None] * wi1[:, None]
    thigh_out = T - n1[None] * wo1[:, None]
    shin_in = S + n2[None] * w2[:, None]
    shin_out = S - n2[None] * w2[:, None]
    # knee arc on the outside
    r0, r1 = wo1[-1], w2[0]
    na = 9 + int(abs(ang) / 0.2)
    a = np.linspace(0, 1, na)
    v0 = -n1
    arc = []
    for f in a:
        th = ang * f
        c, s = np.cos(th), np.sin(th)
        v = np.array([c * v0[0] - s * v0[1], s * v0[0] + c * v0[1]])
        r = (r0 + (r1 - r0) * f) * (1 + (0.22 if not light else 0.15) * bump * np.sin(np.pi * f))
        arc.append(knee + v * r)
    arc = np.array(arc)
    outer = np.vstack([thigh_out[:-1], arc, shin_out[1:]])
    # crook on the inside
    crook = None
    ti, si = thigh_in, shin_in
    if abs(turn) > 0.06:
        A, B = thigh_in[-1], shin_in[0]
        den = _cross(d1, d2)
        uu = _cross(B - A, d2) / den       # along d1 from A (usually negative)
        vv = _cross(B - A, d1) / den       # along d2 from B (usually positive)
        if -0.95 * L1 < uu <= 0.0 and 0.0 <= vv < 0.95 * L2:
            crook = A + d1 * uu
            keep_t = (np.arange(nT) / (nT - 1) * L1 - L1) <= uu
            keep_s = (np.arange(nS) / (nS - 1) * L2) >= vv
            ti, si = thigh_in[keep_t], shin_in[keep_s]
    inn = np.vstack([si[::-1], ti[::-1]]) if crook is None else np.vstack([si[::-1], crook[None], ti[::-1]])
    # hem across the ankle (slightly convex, slanted a touch)
    ao, ai = shin_out[-1], shin_in[-1]
    mid = (ao + ai) / 2 + d2 * 0.025 * hw
    hem = np.array([ao, mid, ai])
    capp = None
    if cap and not light:
        ctr = hip
        v1 = n1
        pts = []
        for f in np.linspace(0, 1, 9):
            th = np.pi * f * inner
            c, s = np.cos(th), np.sin(th)
            v = np.array([c * v1[0] - s * v1[1], s * v1[0] + c * v1[1]])
            pts.append(ctr + v * (wh * 1.1) * (1 + 0.0))
        capp = np.array(pts)
    return dict(outer=outer, inner=inn, hem=hem, cap=capp, d1=d1, d2=d2, n1=n1, n2=n2, L1=L1, L2=L2,
                wh=wh, wk=wk, wa=wa, w2=w2, crook=crook, turn=turn, inner_sign=inner, k=k,
                hip=hip, knee=knee, ankle=ankle, ang=ang)


def _mask(size, hw, g, light, hip_cap):
    pad = int(hw)
    poly = [g['outer'], g['hem'][1:-1] if False else g['hem'], g['inner']]
    pts = np.vstack(poly)
    if g['cap'] is not None:
        pts = np.vstack([pts, g['cap']])
    W, H = size[0] + 2 * pad, size[1] + 2 * pad
    big = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(big).polygon([tuple((p + pad) * SS) for p in pts], fill=255)
    a = np.asarray(big, float) / 255
    a = ndimage.gaussian_filter(a, (0.025 if light else 0.04) * hw * SS)
    small = Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.Resampling.BOX)
    return np.asarray(small)[pad:-pad, pad:-pad] > 127


def _taper(pen, a, b, w, wob=0.6, colour=255, bulge=0.0, edge=True, n=4):
    """A mark thick at a (the contour) tapering to a point at b (edge=True), or
    swelling from a point and tapering at b (edge=False)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = _unit(b - a)
    p = _perp(d)
    pts = [a + (b - a) * f + p * bulge * np.sin(np.pi * f) for f in np.linspace(0, 1, n)]
    if edge:
        ws = list(np.linspace(w, 0.4, n))
    else:
        ws = [0.4, w, w * 0.7, 0.4][:n] if n == 4 else [0.4, w, 0.4]
    pen.stroke(pts, ws, colour=colour, wobble=wob)


def _fold(pen, a, b, w, bulge=0.0, colour=255, wob=0.4, shape='edge'):
    """Bold curved fold from a (on the contour, thick) to b (tapering to a point).
    shape 'lens': swells in the middle and tapers at both ends."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    p = _perp(_unit(b - a))
    f = np.linspace(0, 1, 7)
    pts = [a + (b - a) * x + p * bulge * np.sin(np.pi * x) for x in f]
    if shape == 'edge':
        prof = np.array([1.0, 0.95, 0.8, 0.62, 0.42, 0.24, 0.1])
    else:
        prof = np.array([0.1, 0.6, 0.95, 1.0, 0.85, 0.5, 0.1])
    pen.stroke(pts, list(np.maximum(prof * w, 0.6)), colour=colour, wobble=wob)


def draw(pen, hw, hip, knee, ankle, near=True, light=False, bagginess=0.3, folds=None,
         cuff=True, hip_cap=True, girth=1.0, rim=0.0, knee_bump=1.0, outline=1.0, seed=0, **extra):
    size = pen.size
    g = _geometry(hw, hip, knee, ankle, near, bagginess, knee_bump, hip_cap, cuff, girth, light)
    mask = _mask(size, hw, g, light, hip_cap)
    k = g['k']
    d1, d2, n1, n2 = g['d1'], g['d2'], g['n1'], g['n2']
    knee_p, hip_p = g['knee'], g['hip']
    bent = abs(g['turn']) > 0.15
    if folds is None:
        folds = (4 if light else 3) if near else (3 if light else 1)

    if not light:
        if rim and near:
            ring = ndimage.binary_dilation(mask, iterations=max(1, int(rim * hw))) & ~mask
            pen.paint(ring, 255)
        pen.paint(mask, 0)
        _black_marks(pen, g, hw, folds, cuff, bent)
    else:
        pen.paint(mask, 255)
        _light_contour(pen, g, hw, outline * (1.0 if near else 0.85), hip_cap, cuff)
        _light_folds(pen, g, hw, folds, bent, cuff, np.random.default_rng(seed + 3))


def _black_marks(pen, g, hw, folds, cuff, bent):
    k = g['k']
    d1, d2, n1, n2 = g['d1'], g['d2'], g['n1'], g['n2']
    w = 0.05 * hw * k
    if bent and folds >= 1:
        X = g['crook']
        if X is None:
            X = g['knee'] + (n1 + n2) * g['wk'] * 0.7
        dirn = -_unit(n1 + n2)
        # main crook fold: thick where it leaves the contour, curving into the knee
        _fold(pen, X + dirn * 0.01 * hw, X + dirn * 0.24 * hw * k - d1 * 0.03 * hw, w * 1.4,
              bulge=0.03 * hw, shape='edge')
        if folds >= 2:
            # shorter second fold on the thigh underside, a little way back
            idx = int(len(g['inner']) * 0.68)
            p = g['inner'][min(idx, len(g['inner']) - 1)]
            _fold(pen, p + n1 * 0.01 * hw, p - n1 * 0.12 * hw * k + d1 * 0.06 * hw, w * 1.1, bulge=0.015 * hw)
        if folds >= 3:
            idx = int(len(g['inner']) * 0.22)
            p = g['inner'][idx]
            _fold(pen, p + n2 * 0.01 * hw, p - n2 * 0.11 * hw * k - d2 * 0.05 * hw, w, bulge=-0.012 * hw)
    if cuff:
        # cuff: a short curved line across the shin just above the shoe, from the inside edge
        ai, ao = g['hem'][-1], g['hem'][0]
        a0 = ai - d2 * 0.09 * hw * k
        _fold(pen, a0 + n2 * 0.015 * hw, a0 - n2 * g['wa'] * 1.05 + d2 * 0.015 * hw, 0.05 * hw * k,
              bulge=-0.012 * hw, shape='edge')
    if folds >= 4 and not bent:
        p = g['hip'] + d1 * g['L1'] * 0.6 + n1 * g['wk'] * 0.95
        _fold(pen, p, p - n1 * 0.15 * hw, w)


def _contour_widths(P, hw, scale, base=0.04, extra=0.045):
    """Heavier on the underside (outward normal pointing down the page)."""
    tang = np.gradient(P, axis=0)
    tang /= np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-9)
    return tang


def _light_contour(pen, g, hw, scale, hip_cap, cuff):
    # one continuous path: hip outer -> knee -> ankle outer -> hem -> ankle inner -> crook -> hip inner
    P = np.vstack([g['outer'], g['hem'][1:-1], g['inner']]) if False else np.vstack([g['outer'], g['hem'], g['inner']])
    closed = not hip_cap
    P = _resample(P, 0.045 * hw)
    n = len(P)
    tang = np.gradient(P, axis=0)
    tang /= np.maximum(np.linalg.norm(tang, axis=1, keepdims=True), 1e-9)
    # polygon is wound so the leg interior is on one side: find outward normal via centre
    c = P.mean(0)
    nrm = np.stack([tang[:, 1], -tang[:, 0]], 1)
    if np.sum(((P - c) * nrm).sum(1)) < 0:
        nrm = -nrm
    down = np.clip(nrm[:, 1], 0, 1)
    W = (0.036 + 0.02 * down ** 1.5) * hw * scale * g['k'] ** 0.3
    # heavy hem
    hem_n = len(_resample(g['outer'], 0.045 * hw))
    idx = np.arange(n)
    hem_zone = (np.abs(P - g['hem'][1]).sum(1) < 0.26 * hw)
    W = np.where(hem_zone, np.maximum(W, 0.06 * hw * scale), W)
    ramp = np.ones(n)
    if not closed:
        m = max(3, int(0.12 * hw / (0.045 * hw)))
        m = 3 * m
        ramp[:m] = np.linspace(0.6, 1, m)
        ramp[-m:] = np.linspace(1, 0.6, m)
    W = W * ramp
    cuts = [0]
    keys = [g['hem'][0], g['hem'][-1]] + ([g['crook']] if g['crook'] is not None else [])
    for key in keys:
        cuts.append(int(np.argmin(np.linalg.norm(P - key, axis=1))))
    cuts = sorted(set(cuts + [n - 1]))
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a < 2:
            continue
        a2, b2 = max(0, a - 2), min(n - 1, b + 2)
        pen.stroke(P[a2:b2 + 1], list(W[a2:b2 + 1]), colour=0, wobble=0.7)


def _rot(v, a):
    c, s_ = np.cos(a), np.sin(a)
    return np.array([c * v[0] - s_ * v[1], s_ * v[0] + c * v[1]])


def _light_folds(pen, g, hw, folds, bent, cuff, rng):
    """A few bold folds, every one rooted on the contour: two from the knee
    crook (fanning toward the knee), one on the thigh underside, one on the
    shin, a crescent on the knee bump and the cuff line."""
    k = g['k']
    d1, d2, n1, n2 = g['d1'], g['d2'], g['n1'], g['n2']
    hip, knee, ankle = g['hip'], g['knee'], g['ankle']
    L1, L2, wk = g['L1'], g['L2'], g['wk']
    w = 0.05 * hw * k ** 0.4
    inner = g['inner']
    if bent:
        X = g['crook'] if g['crook'] is not None else knee + (n1 + n2) * wk * 0.8
        into = -_unit(n1 + n2)                      # from the crook toward the knee bump
        order = ['crook1', 'crescent', 'shin', 'thigh', 'crook2']
    else:
        order = ['thigh', 'shin', 'crook1']
        X = knee + n1 * wk
        into = -n1
    todo = order[:max(0, folds - (1 if cuff else 0))] if folds else []
    for name in todo:
        if name == 'crook1':
            L = (0.40 if bent else 0.3) * hw * k
            a = X + into * 0.01 * hw
            b = X + _rot(into, 0.15 * g['inner_sign']) * L
            _fold(pen, a, b, w * 1.25, bulge=0.03 * hw * g['inner_sign'], colour=0)
        elif name == 'crook2':
            L = 0.30 * hw * k
            a = X + into * 0.01 * hw
            b = X + _rot(into, -0.45 * g['inner_sign']) * L
            _fold(pen, a, b, w, bulge=-0.025 * hw * g['inner_sign'], colour=0)
        elif name == 'thigh':
            f = 0.55
            p = hip + d1 * L1 * f + n1 * g['wh'] * (0.8 - 0.3 * f) * 0.95
            e = p + (d1 * 0.95 - n1 * 0.12) * 0.42 * hw * k
            _fold(pen, p, e, w * 1.1, bulge=0.025 * hw, colour=0)
        elif name == 'shin':
            f = 0.68
            p = knee + d2 * L2 * f + n2 * g['wa'] * 1.15
            e = p + (-d2 * 0.95 - n2 * 0.12) * 0.32 * hw * k
            _fold(pen, p, e, w * 1.2, bulge=-0.025 * hw, colour=0)
        elif name == 'crescent':
            out_v = -_unit(n1 + n2)
            c = knee + out_v * wk * 0.05
            a0 = np.arctan2(out_v[1], out_v[0])
            r = wk * 0.62
            pts = [c + r * np.array([np.cos(a0 + t), np.sin(a0 + t)]) for t in np.linspace(-0.9, 0.9, 7)]
            pen.stroke(pts, [0.6, w * 0.9, w * 1.3, w * 1.45, w * 1.2, w * 0.8, 0.6], colour=0, wobble=0.4)
    if cuff:
        ao, ai = g['hem'][0], g['hem'][-1]
        up = -d2 * 0.12 * hw
        a = ao + up + (ai - ao) * 0.12
        b = ao + up + (ai - ao) * 0.88
        pen.stroke([a, (a + b) / 2 - d2 * 0.012 * hw, b], [0.6, w * 1.1, 0.6], colour=0, wobble=0.4)
