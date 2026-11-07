"""Short shirt sleeve plus bare upper arm and forearm, Watterson-style.

draw(pen, hw, shoulder, elbow, wrist=None, near=True, stripes=False, **extra)

pen       ink.Ink canvas.   hw  head width in pixels (all sizes scale with it).
shoulder, elbow, wrist  (x, y) points; wrist optional (no forearm if None).
          The sleeve hangs from the shoulder to a plain hem 0.8 of the way to
          the elbow (a straight cut across, drawn with a slight sag); the bare
          arm (0.3 hw) emerges from the front part of the hem and runs on to
          the elbow (open end if no wrist) and the wrist (open end, no hand).
          Everything is white-filled so it covers what is behind it.
near      True: full-weight outline. False: lighter, fewer creases.
stripes   dark bands running down the sleeve (striped shirt); they follow the
          cloth: they interpolate between the bulging back and front contours,
          crowd towards the back (foreshortening) and stop at the hem.
extras:
  flare=1.0        hem width multiplier (1.0 -> 0.8 hw wide hem).
  crumple=3        number of fold creases (0 for none). They radiate from the
                   armpit / shoulder and, if a wrist is given, lean into the bend.
  front=None       +1/-1: which perpendicular side (normal = (-uy, ux)) the arm
                   comes out on. Default: the side facing +x (right).
  hem=0.8          fraction of shoulder->elbow where the hem sits.
  arm=0.3          arm width in hw (forearm tapers to 0.82 of it at the wrist).
  shoulder_w=0.75  sleeve width at the shoulder in hw.
  stripe_gap=0.2   target spacing of stripes in hw (at the front; closer at back).
  hem_tilt=0.1     hem slant (fraction of hem width; front end lower).
  hem_wave=1.0     amount of ripple in the hem line (0 = smooth).
  hem_sag=0.05     how far (hw) the middle of the hem sags below the corners.
  bulge=0.0        extra outward belly of the sleeve (hw) for bulky sleeves.
  line=0.04        outline weight in hw.
  seed=None        seed for the little irregularities (default from geometry).
  stripe_dir       ignored (kept for compatibility); stripes always run down.
"""
import numpy as np
from skimage.draw import polygon as _poly
import sys
sys.path.insert(0, '/Users/drmaciver/Projects/calvins-dad/tools/extensions/reconstruction-v2')
import ink as _ink


def _mask(pen, pts):
    m = np.zeros((pen.size[1], pen.size[0]), bool)
    p = np.asarray(pts, float)
    rr, cc = _poly(p[:, 1], p[:, 0], m.shape)
    m[rr, cc] = True
    return m


def _unit(v):
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-9)


def _smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def _centre(points, samples=16):
    return _ink.spline(points, samples=samples)


def _rounded(points, r):
    """Polyline with its corners cut into smooth arcs of about radius r."""
    pts = [np.asarray(p, float) for p in points]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        ra = min(r, np.linalg.norm(b - a) * 0.45)
        rc = min(r, np.linalg.norm(c - b) * 0.45)
        p0 = b + _unit(a - b) * ra
        p2 = b + _unit(c - b) * rc
        for t in np.linspace(0, 1, 9):
            out.append((1 - t) ** 2 * p0 + 2 * t * (1 - t) * b + t * t * p2)
    out.append(pts[-1])
    return np.array(out)


def _resample(curve, step):
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))])
    k = max(int(s[-1] / step), 2)
    q = np.linspace(0, s[-1], k)
    return np.stack([np.interp(q, s, curve[:, 0]), np.interp(q, s, curve[:, 1])], 1)


def _limb(pen, pts, w0, w1, lw, heavy_side, elbow_i=None, wob=0.7, bulge_at=None):
    """A bare limb: white tube with a tapering outline, open at both ends."""
    c = _resample(np.asarray(pts, float), max(lw, 3))
    n_ = len(c)
    t = np.linspace(0, 1, n_)
    half = (w0 + (w1 - w0) * t) / 2
    if bulge_at is not None:
        half = half * (1 + 0.07 * np.exp(-((t - bulge_at) / 0.12) ** 2))
    tan = np.gradient(c, axis=0)
    tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-9)
    nor = np.stack([-tan[:, 1], tan[:, 0]], 1)
    left = c + nor * half[:, None]
    right = c - nor * half[:, None]
    for i in range(n_ - 1):
        pen.paint(_mask(pen, [left[i], left[i + 1], right[i + 1], right[i]]), 255)
    # distance of every outline point to the centreline: inside a tight bend the inner
    # offset curve folds back on itself; those points are not drawn
    from scipy.spatial import cKDTree
    tree = cKDTree(c)
    for side, curve in ((1, left), (-1, right)):
        heavy = side == heavy_side
        base = lw * (2.3 if heavy else 1.5)
        prof = base * (0.75 + 0.45 * np.sin(np.pi * np.clip(t * 0.9 + 0.05, 0, 1)))
        dist, _ = tree.query(curve)
        ok = dist > half * 0.93
        i = 0
        while i < n_:
            if not ok[i]:
                i += 1
                continue
            j = i
            while j < n_ and ok[j]:
                j += 1
            if j - i >= 2:
                seg = curve[i:j]
                k = max(len(seg) // 8, 2)
                pw = prof[i:j]
                pen.stroke(seg, list(pw[::k]) + [pw[-1]], 0, wob)
            i = j
    return c, half, nor


def draw(pen, hw, shoulder, elbow, wrist=None, near=True, stripes=False,
         flare=1.0, crumple=3, front=None, hem=0.8, arm=0.3, shoulder_w=0.75,
         stripe_gap=0.2, line=0.04, bulge=0.0, hem_tilt=0.1, hem_sag=0.05, hem_wave=1.0,
         seed=None, stripe_dir=None, **extra):
    S = np.array(shoulder, float)
    E = np.array(elbow, float)
    L = np.linalg.norm(E - S)
    u = (E - S) / L
    n = np.array([-u[1], u[0]])
    if front is None:
        front = 1 if n[0] >= 0 else -1
    n = n * front          # n points to the front side
    lw = line * hw * (1.0 if near else 0.75)
    rng = np.random.default_rng(seed if seed is not None else int(abs(S[0]) * 7 + abs(S[1])) % 10007)
    hwid = 0.8 * hw * flare
    Lh = L * hem
    H = S + u * Lh
    aw = arm * hw

    # ------------------------------------------------------------- bare arm
    side_a = H + n * (hwid / 2 - aw / 2 - 0.07 * hw)        # arm axis at the hem
    a0 = side_a - u * 0.3 * hw                               # starts hidden in sleeve
    if wrist is None:
        axis = [a0, side_a, E]
        c, half, nor = _limb(pen, axis, aw, aw * 0.97, lw, -1, wob=0.6)
    else:
        W = np.array(wrist, float)
        # the bend sits just below the hem, on the arm's own axis (no hook back to the nominal elbow)
        E = side_a + u * max(L - Lh, 0.6 * hw)
        a0 = side_a - u * 0.9 * hw
        d_in = _unit(E - a0)
        v = _unit(W - E)
        cen = _rounded([a0, E, W], 0.6 * hw)
        # outer side of the elbow (the side the bend points to) gets the weight
        turn = d_in[0] * v[1] - d_in[1] * v[0]
        # left normal of travel is (-ty, tx); outer side of the bend is opposite the turn
        heavy = -1 if turn > 0 else 1
        # forearm: a touch wider near the elbow, tapering to the wrist
        c, half, nor = _limb(pen, cen, aw * 1.25, aw * 0.85, lw, heavy, bulge_at=0.3, wob=0.6)

    # --------------------------------------------------------------- sleeve
    sh = shoulder_w * hw / 2
    tt = np.array([0.0, 0.18, 0.4, 0.62, 0.82, 1.0])

    def half_w(t, side):
        flare_t = 1 - (1 - t) ** 2.2
        w = sh + (hwid / 2 - sh) * flare_t
        belly = bulge * hw * np.sin(np.pi * min(t * 1.1, 1)) ** 0.8
        if side < 0:     # back (away from the arm): rounder, bulging at the deltoid
            w = w * (1 + 0.24 * np.sin(np.pi * min(t * 1.1, 1))) + belly + 0.06 * hw * np.sin(np.pi * t)
        else:
            w = w * (1 + 0.06 * np.sin(np.pi * t)) + belly * 0.6
        return w

    def side_pts(side):
        return [S + u * (Lh * t + 0.02 * hw) + n * side * half_w(t, side) for t in tt]

    tilt = hwid * hem_tilt
    back = side_pts(-1)
    frnt = side_pts(+1)
    # the hem corners (front end a little lower), slight flare-out at the corners
    Hb = back[-1] - u * tilt / 2 + u * 0.0
    Hf = frnt[-1] + u * tilt / 2
    back[-1] = Hb
    frnt[-1] = Hf
    top = S - u * 0.14 * hw
    cap = [top - n * sh * 0.8 + u * 0.1 * hw, top - u * 0.03 * hw, top + n * sh * 0.75 + u * 0.06 * hw]
    back_c = _ink.spline(back[::-1] + cap[:1], samples=12)         # hem -> shoulder (back)
    front_c = _ink.spline(cap[2:] + frnt, samples=12)               # shoulder -> hem (front)
    cap_c = _ink.spline(cap, samples=10)
    mid = (Hb + Hf) / 2 + u * hem_sag * hw
    hem_c = _ink.spline([Hb, Hb + (mid - Hb) * 0.35 + u * hem_sag * hw * 0.3 - u * 0.03 * hw * hem_wave, mid,
                         Hf + (mid - Hf) * 0.4 + u * hem_sag * hw * 0.2 + u * 0.03 * hw * hem_wave, Hf], samples=10)
    outline = np.vstack([back_c, cap_c, front_c, hem_c[::-1][1:]])
    m = _mask(pen, outline)
    pen.paint(m, 255)

    def prof(k, vals):
        return list(np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(vals)), vals) * lw)

    # back contour: heavy shadow side, thinning to the hem and over the shoulder
    pen.stroke(np.vstack([back_c, cap_c[:len(cap_c) // 2]]),
               prof(10, [0.9, 1.8, 2.4, 2.3, 1.9, 1.4, 1.2]), 0, 1.0)
    pen.stroke(np.vstack([cap_c[len(cap_c) // 2:], front_c]),
               prof(10, [1.6, 1.7, 1.4, 1.2, 1.2, 1.3, 1.4]), 0, 0.9)
    # hem: plain cut, a little heavier at the back end, tapering at the front
    hd = _unit(Hb - Hf)
    hem_c = np.vstack([[Hb + hd * lw * 0.9], hem_c])
    pen.stroke(hem_c, prof(8, [1.6, 2.2, 1.9, 1.6, 1.2, 1.0]), 0, 0.5)

    if stripes:
        # stripes follow the cloth: interpolate between the two side contours
        bs = _ink.spline(back[::-1], samples=10)[::-1]   # shoulder -> hem on the back
        fs = _ink.spline(frnt, samples=10)
        k = min(len(bs), len(fs))
        bs = bs[np.linspace(0, len(bs) - 1, k).astype(int)]
        fs = fs[np.linspace(0, len(fs) - 1, k).astype(int)]
        wid = np.linalg.norm(Hf - Hb)
        count = max(int(round(wid / (stripe_gap * hw))) - 1, 2)
        fr = (np.arange(count) + 1) / (count + 1)
        fr = fr ** 0.8            # foreshortening: crowded toward the back
        n_s = 1.0
        for j, f in enumerate(fr):
            pts = bs * (1 - f) + fs * f
            pts = pts[1:-1][:-1]
            k_ = len(pts)
            tt_ = np.linspace(0, 1, k_)
            # bow with the cloth: bulge sideways, more at the back, and ripple a little
            bow = (0.05 * hw * np.sin(np.pi * tt_) * (1 - 1.4 * f) + 0.012 * hw * np.sin(5 * tt_ + 3 * j)) * n_s
            pts = pts + n[None, :] * bow[:, None]
            wv = lw * (0.6 + 0.4 * (1 - f) + 0.2 * rng.random())
            widths = [wv * 0.25, wv, wv * 1.15, wv * 1.0, wv * 0.6, wv * 0.2]
            tmp = _ink.Ink(pen.size, seed=int(rng.integers(1 << 20)))
            tmp.stroke(pts, widths, 0, 0.6)
            pen.paint(tmp.mask() & m, 0)

    if near and crumple:
        _creases(pen, S, u, n, L, Lh, hw, sh, hwid, lw, crumple, rng, back, frnt, wrist, E)


def _creases(pen, S, u, n, L, Lh, hw, sh, hwid, lw, crumple, rng, back, frnt, wrist, E):
    """Bold bent fold strokes: pulls from the armpit (back contour), a shoulder fold, an elbow crease."""
    lean = 0.0
    if wrist is not None:
        lean = float(np.clip(np.dot(_unit(np.asarray(wrist, float) - E), n) * 0.8, -1, 1))
    # (contour point, side, length hw, lean inward, bend direction)
    anchors = [
        (back[2], -1, 0.34, 0.5, 1),
        (back[3], -1, 0.28, 0.6, -1),
        (back[1], -1, 0.24, 0.7, 1),
        (frnt[4], +1, 0.22, 0.5, -1),
        (back[4], -1, 0.2, 0.6, 1),
    ]
    for i in range(int(crumple)):
        p0, side, ln, ang, bend = anchors[i % len(anchors)]
        ln *= hw * (0.9 + 0.2 * rng.random())
        inward = -side * n
        d = _unit(u * (1.0 - 0.6 * ang) + inward * ang + n * lean * 0.2)
        p0 = np.asarray(p0, float) + inward * lw * 1.2
        perp = np.array([-d[1], d[0]]) * bend
        p1 = p0 + d * ln * 0.55 + perp * ln * 0.06
        d2 = _unit(d + perp * 0.9)          # the fold kinks part-way along
        p2 = p1 + d2 * ln * 0.45
        pen.stroke([p0, p1, p2], [lw * 1.9, lw * 1.5, lw * 0.15], 0, 0.3)
    if crumple >= 2:
        # shoulder seam: arc under the deltoid on the front
        s0 = S + u * 0.1 * hw + n * sh * 0.8
        s1 = S + u * 0.25 * hw + n * sh * 0.5
        s2 = S + u * 0.4 * hw + n * sh * 0.3
        pen.stroke([s0, s1, s2], [lw * 0.8, lw * 1.2, lw * 0.2], 0, 0.25)
