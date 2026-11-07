"""Dad's hand in Watterson's brush manner.

    draw(pen, hw, gesture, wrist, knuckles, flip=False, **extra)

pen       an ink.Ink canvas (image pixel coordinates)
hw        Dad's head width in pixels (everything scales with it)
gesture   'hang'  relaxed, fingers hanging together, slightly hooked
          'rest'  resting on a knee/surface, fingers drooping and curling
          'fist'  closed fist: a compact mass with four curled finger lobes
          'grip'  holding a handle/edge: like a fist but looser, fingers
                  longer and wrapping, a little separated
          'open'  raised open hand, fingers spread a little
          'point' index finger out, the other three folded
wrist     (x, y) middle of the wrist
knuckles  (x, y) middle of the knuckle row; wrist->knuckles fixes the
          direction (towards the fingertips) and, with hw, the size
          (about 0.35 hw is the nominal distance; other distances scale
          the whole hand proportionally)
flip      mirror the hand (thumb on the other side of the axis)

Extras (all optional):
  thumb_side  +1 (default) thumb on the +90 degree side of wrist->knuckles
              (screen: rotate the direction by +90 degrees in image
              coordinates), -1 the other; multiplied by -1 when flip.
  curl        1.0 default. Scales how much fingers bend (0 = straight).
              Negative curls them the other way (towards the thumb is +).
  spread      1.0 default. Scales the fan between fingers.
  thumb       'out' (default for most), 'tuck' (folded across the front,
              fist/grip), 'up' (raised along the side), 'none'.
  scale       overall size multiplier on top of the wrist-knuckle scale.
  heavy       1.0 default. Weight of the shadow-side contour (0 = even line).
  detail      True: thin inner lines (thumb crease, knuckle marks).

The hand is built from rounded capsule fingers and a palm blob, outlined
in black from outside, then filled white (so it hides whatever is behind).
Finger separations are the gaps between the fingers' white bodies, so they
run in from the tips and stop where the palm blob begins.
"""
import math
import numpy as np
from skimage.draw import polygon as _polygon  # noqa: F401  (straight edges if needed)

OL = 0.040      # outline weight (hw)
THIN = 0.030


class _Frame:
    def __init__(self, wrist, knuckles, hw, flip, thumb_side, scale):
        w = np.asarray(wrist, float)
        k = np.asarray(knuckles, float)
        v = k - w
        d = float(np.linalg.norm(v)) or 1.0
        self.a = v / d
        self.b = np.array([-self.a[1], self.a[0]])
        self.s = (thumb_side if not flip else -thumb_side)
        self.k = k
        self.hw = hw
        # size factor: nominal wrist-knuckle distance is 0.35 hw
        self.f = max(0.5, min(2.0, d / (0.35 * hw))) * scale

    def pt(self, x, y):
        """local (x towards the thumb, y towards the fingertips) in hw -> image"""
        u = self.hw * self.f
        return self.k + self.a * (y * u) + self.b * (x * u * self.s)

    def pts(self, lst):
        return [self.pt(x, y) for x, y in lst]


def _chain(x0, y0, heading, segs, bends):
    """Polyline of joints: start, then each segment turned by the bend before it.

    heading and bends in degrees, positive towards +x (thumb side)."""
    pts = [(x0, y0)]
    h = math.radians(heading)
    x, y = x0, y0
    for i, ln in enumerate(segs):
        if i > 0:
            h += math.radians(bends[i - 1])
        x += math.sin(h) * ln
        y += math.cos(h) * ln
        pts.append((x, y))
    return pts


# finger base lateral positions (x, thumb side positive): index, middle, ring, pinky
BASE_X = [0.188, 0.063, -0.063, -0.188]

# per gesture: for each finger (index, middle, ring, pinky):
#   (heading, [segment lengths], [bends], base width)
G = {
    'hang': dict(
        fingers=[(10, [0.17, 0.12], [26], .102), (3, [0.22, 0.13], [24], .102),
                 (-5, [0.19, 0.12], [22], .098), (-13, [0.13, 0.10], [20], .088)],
        mode='merged', palm_fwd=-0.01, thumb=(55, [0.12, 0.11], [-15], .11)),
    'rest': dict(
        fingers=[(26, [0.17, 0.15, 0.10], [34, 40], .098), (12, [0.20, 0.16, 0.10], [34, 40], .098),
                 (-2, [0.18, 0.15, 0.09], [34, 40], .095), (-15, [0.13, 0.11, 0.08], [32, 36], .086)],
        mode='merged', palm_fwd=-0.03, thumb=(65, [0.12, 0.10], [-10], .11)),
    'open': dict(
        fingers=[(20, [0.18, 0.13], [8], .102), (7, [0.21, 0.14], [4], .102),
                 (-7, [0.19, 0.13], [-4], .100), (-24, [0.14, 0.11], [-8], .09)],
        mode='merged', palm_fwd=-0.01, thumb=(80, [0.13, 0.12], [-25], .115)),
    'point': dict(
        fingers=[(4, [0.20, 0.16], [4], .105), (-6, [0.10], [], .125),
                 (-12, [0.09], [], .12), (-18, [0.07], [], .105)],
        mode='stacked', palm_fwd=0.0, thumb=(70, [0.10, 0.10], [-20], .12)),
    'fist': dict(
        fingers=[(2, [0.12], [], .135), (0, [0.17], [], .14),
                 (-2, [0.15], [], .135), (-4, [0.09], [], .12)],
        mode='stacked', palm_fwd=-0.03, thumb=(40, [0.10, 0.10], [10], .125)),
    'grip': dict(
        fingers=[(8, [0.15, 0.12], [22], .135), (2, [0.18, 0.13], [22], .135),
                 (-4, [0.16, 0.12], [20], .13), (-10, [0.12, 0.09], [20], .115)],
        mode='stacked', palm_fwd=-0.02, thumb=(50, [0.10, 0.10], [5], .125)),
}


def _line(pen, pts, widths, colour=0, wobble=0.5):
    pen.stroke([tuple(p) for p in pts], widths, colour, wobble)


def draw(pen, hw, gesture, wrist, knuckles, flip=False, thumb_side=1, curl=1.0,
         spread=1.0, thumb=None, scale=1.0, heavy=1.0, detail=True, **extra):
    if gesture not in G:
        raise ValueError(gesture)
    spec = G[gesture]
    fr = _Frame(wrist, knuckles, hw, flip, thumb_side, scale)
    u = hw * fr.f
    ol = OL * hw
    wob = 0.5
    mode = spec['mode']
    cvs = curl

    # ---- geometry in local coordinates
    chains = []   # (centre points (local), widths (hw))
    for i, (head, segs, bends, w0) in enumerate(spec['fingers']):
        pts = _chain(BASE_X[i] * (1.0 if mode == 'merged' else 1.0), -0.05,
                     head * spread, [s for s in segs], [b * cvs for b in bends])
        n = len(pts)
        widths = [w0 * (1 - 0.12 * j) for j in range(n)]
        chains.append((pts, widths))
    th = spec['thumb']
    tpts = _chain(0.17, -0.14, th[0], th[1], [b * cvs for b in th[2]])
    tw = [th[3], th[3] * 0.92, th[3] * 0.85][:len(tpts)]
    thumb_mode = thumb or ('tuck' if mode == 'stacked' and gesture in ('fist', 'grip') else 'out')

    # palm blob (local coords): wrist end narrow, knuckle end wide
    pf = spec['palm_fwd']
    palm = [(-0.12, -0.33), (0.0, -0.35), (0.12, -0.32), (0.22, -0.19), (0.24, -0.04),
            (0.20, pf), (0.07, pf + 0.03), (-0.07, pf + 0.03), (-0.20, pf),
            (-0.24, -0.06), (-0.19, -0.22)]
    palm_w = fr.pts(palm)

    def pw(widths):
        return [w * u for w in widths]

    def outline_finger(pts, widths, extra_w=0.0):
        P = fr.pts(pts)
        _line(pen, P, pw([w + 2 * OL for w in widths]), 0, wob)
        return P

    def white_finger(pts, widths):
        P = fr.pts(pts)
        _line(pen, P, pw(widths), 255, wob)

    def black_palm():
        pen.fill(palm_w, 0, 0.6)
        pen.stroke(palm_w, [2 * ol], 0, wob, closed=True)

    def white_palm():
        pen.fill(palm_w, 255, 0.0)

    order = [3, 2, 1, 0]   # pinky first, index on top
    show_thumb = thumb_mode != 'none'

    if mode == 'merged':
        black_palm()
        for i in order:
            outline_finger(*chains[i])
        if show_thumb:
            outline_finger(tpts, tw)
        for i in order:
            white_finger(*chains[i])
        if show_thumb:
            white_finger(tpts, tw)
        white_palm()
    else:
        black_palm()
        white_palm()
        if show_thumb and thumb_mode not in ('tuck', 'up'):
            outline_finger(tpts, tw)
            white_finger(tpts, tw)
        for i in order:
            outline_finger(*chains[i])
            white_finger(*chains[i])
        if show_thumb and thumb_mode in ('tuck', 'up'):
            tp = _chain(0.19, 0.03, -80, [0.20], []) if thumb_mode == 'tuck' else _chain(0.2, -0.08, 8, [0.14, 0.11], [6])
            outline_finger(tp, [0.12, 0.10])
            white_finger(tp, [0.12, 0.10])
