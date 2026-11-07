"""Dad in panel 2, outside Watterson's scan, drawn to docs/dad-drawing-spec.md.

He sits back on his heels, leaning far forward to the record player (the
skeleton is POSES[2] in pose.py). Everything of him left of the scan (x <
800) and below it is drawn here: his back and shirt, the near sleeve (panel
1's own sleeve, turned to his arm), the upper arm and elbow, his trousers
and the near shoe. This is the basis for iteration ("draft A"); it is not
yet accepted.

Fixed by the scan:
- his collar's left point at about (815, 1185), where his back begins;
- the top and bottom edges of his near forearm, leaving the crop's left edge
  at y=1810 and y=1938 (the upper line is two lines run together: the
  sleeve's hem over the forearm's top);
- his shirt's edge meeting the trousers at (800, 2047);
- the top of his knee, whose black leaves the crop's foot between x=800 and
  x=1051; its edge there lies on a circle of radius 194 (0.39 head widths)
  centred at (906, 2190), which rests on the floor at y=2382.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from ink import Ink, composite
import drawn_legs

HERE = Path(__file__).resolve().parent
FLOOR = 2382
KNEE = (906, 2190)
KNEE_RADIUS = 194


def knee_arc(start, end, steps=8):
    """Points on the knee's front, from angle `start` to `end` (degrees,
    0 = straight ahead, 90 = straight down)."""
    return [(KNEE[0] + KNEE_RADIUS * np.cos(a), KNEE[1] + KNEE_RADIUS * np.sin(a))
            for a in np.linspace(np.radians(start), np.radians(end), steps)]


# Every shape, so variants can be tried by replacing entries.
A = dict(
    shoe=dict(heel_x=440, toe_x=58,
              top=[(1.0, 150), (0.7, 150), (0.45, 140), (0.25, 124), (0.1, 104),
                   (0.02, 78), (0.0, 46)],
              bottom=[(0.04, 8), (0.3, 0), (0.7, 0), (1.0, 0)],
              sole_inset=26, toe_cap=[(0.36, 2), (0.27, 28), (0.21, 50)]),
    trousers=[(206, 1990), (150, 2046), (120, 2120), (124, 2196), (156, 2240),
              (230, 2258), (330, 2262), (392, 2262), (404, 2272), (410, 2320),
              (418, 2382), (700, 2385)] + knee_arc(90, -42) +
             [(1033, 2040), (980, 2000), (870, 1960), (820, 2030), (800, 2047),
              (700, 2041), (500, 2030), (300, 2016)],
    trouser_whites=[([(1052, 2302), (900, 2274), (720, 2260), (540, 2262)], [3, 13, 12, 8, 2]),
                    ([(170, 2130), (214, 2176), (262, 2198)], [2, 9, 2])],
    back=[(806, 1186), (760, 1192), (700, 1214), (630, 1258), (556, 1328),
          (478, 1428), (400, 1556), (330, 1696), (272, 1826), (228, 1938),
          (206, 1994)],
    hem=[(206, 1994), (262, 2012), (380, 2022), (520, 2030), (660, 2038),
         (760, 2044), (800, 2047)],
    sleeve=dict(turn=34, at=(672, 1754), scale=1.7,
                keep=[(450, 598), (476, 596), (616, 512), (642, 516), (708, 780),
                      (716, 798), (700, 805), (508, 829), (486, 828)]),
    upper_arm=[(584, 1776), (576, 1840), (588, 1890), (614, 1928), (664, 1948),
               (740, 1947), (800, 1940)],
)

# Middle of panel 1's sleeve hem, the point the sleeve is turned about.
SLEEVE_HEM = (600, 812)


def shoe(ink, s):
    """The near shoe behind him, lying on its upper with the sole turned up
    and the toe back on the floor; its heel goes under his seat."""
    span = s['heel_x'] - s['toe_x']

    def at(f, dy):
        return (s['toe_x'] + f * span, FLOOR - dy)
    top = [at(*p) for p in s['top']]
    upper = top + [at(*p) for p in s['bottom']]
    ink.fill(upper, colour=255, wobble=0)
    ink.stroke(upper + [upper[0]], [20] * 12)
    sole = s.get('sole') or [(x, y + s['sole_inset']) for x, y in top[:6]][::-1]
    ink.stroke(sole, [4, 11, 12, 12, 12, 10][:len(sole)] + [10] * max(0, len(sole) - 6))
    ink.stroke([at(*p) for p in s['toe_cap']], [4, 12, 4])


def sleeve(size, s):
    """Panel 1's near sleeve, scaled to panel 2 and turned to his upper arm."""
    locked = Image.open(HERE / 'locked-1.png').convert('L')
    source = Image.new('L', (locked.width + 400, locked.height), 255)
    source.paste(locked, (400, 0))
    ink, _, move = drawn_legs.transplant(source, s['keep'], [], SLEEVE_HEM, s['at'], s['turn'],
                                          scale=(s['scale'], s['scale']), size=size)
    shape = Image.new('1', size, 0)
    ImageDraw.Draw(shape).polygon(
        [move(p) for p in [(472, 612), (625, 522), (700, 788), (505, 822)]], fill=1)
    return ink, np.asarray(shape)


def panel_two(image, d=A):
    w, h = image.size
    # Watterson's own crop, whole: an earlier repair had drawn over its left
    # edge where the sleeve met the elbow.
    image = image.copy()
    image.paste(Image.open(HERE / 'locked-2.png').convert('L'), (800, 0))
    ink = Ink((w, h), seed=21)
    shoe(ink, d['shoe'])
    ink.fill(d['trousers'], wobble=1.0)
    for line, widths in d['trouser_whites']:
        ink.stroke(line, widths, colour=255, wobble=0.6)
    ink.fill(d['back'] + d['hem'][1:] + [(800, 1186)], colour=255, wobble=0)
    ink.stroke(d['back'], [20, 22, 24, 24, 23, 22, 22, 21, 21, 20, 20])
    ink.stroke(d['hem'], [20, 20, 19, 18, 17, 16, 16])
    # The upper arm shows below the sleeve's hem, down to the elbow and into
    # the forearm's bottom edge where it leaves the crop.
    sleeve_ink, sleeve_shape = sleeve((w, h), d['sleeve'])
    ink.fill(d['upper_arm'] + [(800, 1812), (700, 1792), (600, 1780)], colour=255, wobble=0)
    ink.stroke(d['upper_arm'], [18, 20, 21, 21, 20, 20, 22])
    drawing = ink.mask()
    drawing[sleeve_shape] = False
    drawing |= sleeve_ink
    if d.get('sleeve_hem'):
        # Replace the transplanted hem with a drawn one of even weight.
        hem_ink = Ink((w, h), seed=23)
        lo = Image.new('1', (w, h), 0)
        ImageDraw.Draw(lo).polygon(d['sleeve_hem_clear'], fill=1)
        drawing[np.asarray(lo)] = False
        hem_ink.fill(d['sleeve_hem_clear'], colour=255, wobble=0)
        hem_ink.stroke(d['sleeve_hem'], [19] * len(d['sleeve_hem']))
        drawing |= hem_ink.mask()
    yy, xx = np.mgrid[:h, :w]
    region = (xx < 800) | ((yy >= 2060) & (xx < 1540))
    return composite(image, drawing, region)
