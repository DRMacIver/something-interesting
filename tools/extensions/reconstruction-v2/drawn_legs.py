"""Dad's figure outside the scanned close-ups of panels 2 and 3, drawn in code.

The scan stops at Dad's waist in panel 2 and at his chest in panel 3, so
everything of him beyond the crops is drawn here rather than generated:
his legs and shoes in both, and in panel 3 also his back, shirt, sleeves,
arms and the hand resting on his thigh. Where Watterson drew the same
thing elsewhere in the strip it is reused instead (see transplant): panel
2's trailing shoe is panel 1's planted shoe turned sole up, and panel 3's
resting hand is his own gesturing hand turned palm down. The drawing follows the
strip itself: Dad's trousers are a flat black silhouette with a few thin
white folds, as in panel 1, and his shoes are panel 1's white shoes with a
heavy outline, a sole line just inside it and a small heel notch. Sizes come
from panel 1 scaled to each close-up by head width (Dad's head is about
290px wide in panel 1, 493px in panel 2 and 562px in panel 3). He sits back
on his heels, as in Watterson's kneeling Dad on page 8, with his feet laid
flat behind him and the soles turned up.

All coordinates are pixels of the full-panel exports.
"""
import numpy as np

from ink import Ink, composite

OUTLINE = 17

# Panel 1's white shoe in its own frame: u runs from the back of the heel to
# the toe, v from the collar (negative) to the sole (positive). In panel 1 it
# is about 300px long; at the close-ups' scale it is about 500px.
SHOE = dict(
    outline=[(0, 70), (-14, 0), (10, -66), (70, -96), (190, -112), (320, -106),
             (420, -84), (492, -36), (504, 20), (470, 70), (340, 94), (180, 98)],
    sole=[(34, 52), (170, 64), (330, 62), (448, 40)],
    heel_notch=[(150, 90), (154, 76), (150, 60)],
    toe_cap=[(350, -104), (382, -56), (424, -12), (478, 2)],
)


def place(points, heel, angle, scale=1.0, flip=False, foreshorten=1.0):
    """Points in the shoe's frame placed with its heel at `heel`, its toe in
    direction `angle` (degrees, image coordinates), sole on the left of the
    heel-to-toe direction unless `flip`. `foreshorten` shortens the shoe
    when it points away from the viewer."""
    u = np.array([np.cos(np.radians(angle)), np.sin(np.radians(angle))])
    v = np.array([u[1], -u[0]]) * (-1 if flip else 1)
    return [tuple(np.asarray(heel) + scale * (a * foreshorten * u + b * v))
            for a, b in points]


def shoe(ink, heel, angle, scale=1.0, flip=False, foreshorten=1.0, width=22):
    """A white shoe: outline, a sole line inside it and the cap at the toe."""
    parts = {k: place(v, heel, angle, scale, flip, foreshorten) for k, v in SHOE.items()}
    ink.fill(parts['outline'], colour=255, wobble=0)
    ink.stroke(parts['outline'], [width, width * 1.3, width * 1.1, width * 1.4, width],
               closed=True)
    ink.stroke(parts['sole'], [3, 12, 13, 10, 3])
    ink.stroke(parts['heel_notch'], [4, 12, 4])
    ink.stroke(parts['toe_cap'], [3, 11, 10, 2])


def thin_underarm(image):
    """Bring the line under Dad's arm in panel 2 back to the scan's weight.

    The earlier elbow repair (upper-2.png) thickened the arm's underside
    into a wedge of black that read as a stray bit of trouser above a gap.
    In the scan the line is about 20px; keep that much of it, from its top.
    """
    a = np.asarray(image).copy()
    for x in range(UNDERARM[0], UNDERARM[1]):
        column = a[UNDERARM[2]:UNDERARM[3], x] < 128
        top = np.argmax(column)
        if not column[top]:
            continue
        end = top + np.argmin(column[top:]) if not column[top:].all() else len(column)
        # Taper into the shirt's hem at the left, where the gap closes.
        weight = 21 + max(0, 790 - x) * 0.9
        if end - top > weight and end < len(column):
            a[UNDERARM[2] + top + int(weight):UNDERARM[2] + end + 2, x] = 255
    from PIL import Image, ImageFilter
    # Smooth the new edge as the rest of the art is smoothed.
    result = Image.fromarray(a)
    box = (UNDERARM[0] - 4, UNDERARM[2], UNDERARM[1] + 4, UNDERARM[3])
    edge = result.crop(box).filter(ImageFilter.GaussianBlur(2))
    edge = edge.point(lambda v: 0 if v < 100 else 255 if v > 156 else int((v - 100) * 255 / 56))
    result.paste(edge, box[:2])
    return result


# Columns and rows of the underarm line in the panel 2 export.
UNDERARM = (730, 1000, 1880, 1960)
PANEL2_SHOE = (300, 2256)
PANEL2_SHOE_TURN = 180
PANEL2_SHOE_SCALE = (1.7, 1.7)


def panel_two(image):
    """Dad sits back on his heels facing right, knee by the record player."""
    w, h = image.size
    ink = Ink((w, h), seed=2)
    # His near foot trails behind him, toe on the floor and heel up under his
    # seat, the sole turned back: the same shoe as in panel 3, seen side on.
    shoe(ink, heel=(450, 2214), angle=150, scale=0.84, flip=True, foreshorten=0.62)
    # The trousers. In the scan the top of his knee is just under his
    # forearm, its front already turning down at the crop's foot (x=1051),
    # so the knee comes straight down to the floor there. His seat rounds
    # out behind him over his heels and the shin lies under the thigh.
    ink.fill([(428, 1962), (420, 2000), (400, 2048), (378, 2104), (366, 2160),
              (370, 2214), (392, 2252), (432, 2262), (452, 2290), (452, 2340),
              (466, 2380), (700, 2385), (900, 2386), (990, 2383), (1040, 2370),
              (1076, 2338), (1096, 2280), (1100, 2210), (1088, 2140), (1068, 2092),
              (1051, 2058), (1033, 2040), (980, 2000), (720, 1990), (720, 1962)],
             wobble=1.2)
    # Folds: where the thigh lies on the shin, the front of the knee and the seat.
    ink.stroke([(1066, 2262), (960, 2240), (820, 2234), (680, 2246)],
               [3, 14, 12, 8, 3], colour=255, wobble=0.8)
    ink.stroke([(1030, 2120), (1056, 2170), (1064, 2222)],
               [2, 9, 3], colour=255, wobble=0.6)
    ink.stroke([(470, 2120), (560, 2160), (640, 2172)],
               [2, 9, 2], colour=255, wobble=0.6)
    yy, xx = np.mgrid[:h, :w]
    region = ((yy >= 2060) & (xx < 1540)) | ((yy >= 1966) & (xx < 700))
    return composite(thin_underarm(image), ink.mask(), region)


def outlined(ink, points, width=OUTLINE + 2):
    """A white shape with a closed ink outline."""
    ink.fill(points, colour=255, wobble=0)
    ink.stroke(points, [width, width * 1.1, width * 0.95, width * 1.15, width], closed=True)


# The scanned gesturing hand in panel 3: its bounding box and the wrist, where
# the two lines of the forearm reach the thumb (A) and the palm (B).
SCAN_HAND_BOX = (1585, 1770, 2200, 2080)
SCAN_WRIST = ((1792, 1960), (1875, 2007))
# Where the thumb joins the palm: up from the wrist's thumb end to the palm's top.
SCAN_THUMB_BASE = ((1838, 1860), (1846, 1770))


def transplant(source, keep, closing, pivot, target, angle, flip=False,
               scale=(1.0, 1.0), axis=0.0, size=None):
    """Move a piece of Watterson's own ink to a new place and pose.

    `keep` is a polygon around the piece in `source`, `closing` a list of
    segments that close its outline where `keep` cuts it off (so its inside
    can be filled). The piece is optionally flipped top to bottom about
    `pivot`, scaled by `scale` along and across the direction `axis`
    (degrees), turned by `angle` degrees and moved so `pivot` lands on
    `target`. Returns its ink and filled silhouette as masks of `size`, and
    the function mapping source points to their new places.
    """
    from PIL import Image, ImageDraw
    from scipy import ndimage
    mask = Image.new('L', source.size, 0)
    ImageDraw.Draw(mask).polygon(keep, fill=255)
    ink = (np.asarray(source.convert('L')) < 128) & (np.asarray(mask) > 0)
    closed = Image.fromarray(ink)
    for segment in closing:
        ImageDraw.Draw(closed).line(segment, fill=1, width=14)
    silhouette = ndimage.binary_fill_holes(np.asarray(closed))
    def turn(degrees):
        t = np.radians(degrees)
        return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    stretch = turn(axis) @ np.diag(scale) @ turn(-axis)
    forward = turn(angle) @ stretch @ np.diag([1, -1 if flip else 1])
    inverse = np.linalg.inv(forward)
    pivot, target = np.asarray(pivot, float), np.asarray(target, float)
    w, h = size
    xs, ys = zip(*keep)
    reach = max(np.hypot(x - pivot[0], y - pivot[1]) for x, y in keep) * max(scale) + 10
    yy, xx = np.mgrid[max(0, int(target[1] - reach)):min(h, int(target[1] + reach)),
                      max(0, int(target[0] - reach)):min(w, int(target[0] + reach))]
    src = inverse @ np.stack([xx.ravel() - target[0], yy.ravel() - target[1]]) + pivot[:, None]
    out = []
    for layer in (ink, silhouette):
        sampled = ndimage.map_coordinates(layer.astype(float), [src[1], src[0]], order=1, cval=0)
        full = np.zeros((h, w), bool)
        full[yy.ravel(), xx.ravel()] = sampled > 0.5
        out.append(full)
    return out[0], out[1], lambda point: tuple(forward @ (np.asarray(point) - pivot) + target)


def resting_hand(image, target, angle, scale=1.0):
    """Panel 3's scanned open hand, turned palm down to rest on the thigh.

    The hand is flipped top to bottom about its wrist, which turns the palm
    over, then tilted by `angle` degrees so the fingers lie along the thigh
    towards the knee, with the wrist's midpoint at `target`. Its thumb is
    left out: on a hand resting palm down it lies along the inside of the
    thigh, out of sight. Returns the hand's ink and silhouette, and where
    the wrist's thumb and palm ends land.
    """
    x0, y0, x1, y1 = SCAN_HAND_BOX
    a, b = SCAN_WRIST
    c, d = SCAN_THUMB_BASE
    # The hand without its thumb: right of the thumb's base (cut a little
    # inside it, clear of the thumb's own outline), beyond the wrist.
    a = (a[0] + 14, a[1] + 4)
    c, d = (c[0] + 10, c[1]), (d[0] + 10, d[1])
    keep = [c, d, (x1, y0), (x1, y1), (b[0] + 80, b[1] + 60), b, a]
    middle = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    ink, shape, move = transplant(image, keep, [(a, b), (a, c)], middle, target,
                                  angle, flip=True, scale=(scale, scale), size=image.size)
    # Ink the side of the hand where the thumb was cut away.
    edge = Ink(image.size, seed=6)
    edge.stroke([move(a), move(((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)), move(c)],
                [20, 22, 20])
    return ink | edge.mask(), shape, move(a), move(b)


def resting_thumb(image, target, angle, scale, bend):
    """The scanned hand's thumb, moved with the hand by `resting_hand` and
    then turned `bend` degrees about its base, so it lies alongside the
    fingers on the thigh instead of sticking out backwards."""
    x0, y0, x1, y1 = SCAN_HAND_BOX
    a, b = SCAN_WRIST
    c, d = SCAN_THUMB_BASE
    middle = np.array([(a[0] + b[0] + 28) / 2, (a[1] + b[1] + 8) / 2])
    keep = [(x0, y0), (d[0] + 2, d[1]), (c[0] + 2, c[1]), (a[0] + 2, a[1]), (x0, a[1] + 60)]
    def turn(degrees):
        t = np.radians(degrees)
        return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    # Where the thumb's base lands with the hand, and the target that turns
    # the whole thumb a further `bend` about it.
    hand = turn(angle) @ np.diag([1, -1]) * scale
    base = hand @ (np.array([(a[0] + c[0]) / 2, (a[1] + c[1]) / 2]) - middle) + target
    moved = turn(bend) @ (np.asarray(target, float) - base) + base
    ink, shape, _ = transplant(image, keep, [(a, c)], middle, moved, angle + bend,
                               flip=True, scale=(scale, scale), size=image.size)
    return ink, shape


# Dad's planted back shoe in panel 1, in side view, in the coordinates of
# the full panel 1 export. Only the part inside the scanned crop (x >= 400)
# is used; the trouser leg covers its top at the heel, so `keep` stops just
# under the trouser's hem.
PANEL1_SHOE_KEEP = [(400, 1872), (520, 1866), (670, 1866), (670, 2016), (400, 2016)]
PANEL1_SHOE_CLOSE = [((400, 1872), (400, 2016)), ((400, 1874), (520, 1868))]
PANEL1_SHOE_CENTRE = (530, 1940)
PANEL1_SHOE_HIDDEN_TOP = [(380, 1874), (450, 1871), (520, 1872), (560, 1880)]


def panel_one_shoe(target, angle, scale, size):
    """Panel 1's planted shoe, turned over to lie behind Dad, sole up."""
    from pathlib import Path
    from PIL import Image
    locked = Image.open(Path(__file__).resolve().parent / 'locked-1.png').convert('L')
    source = Image.new('L', (locked.width + 400, locked.height), 255)
    source.paste(locked, (400, 0))
    ink, shape, move = transplant(source, PANEL1_SHOE_KEEP, PANEL1_SHOE_CLOSE,
                                  PANEL1_SHOE_CENTRE, target, angle, scale=scale, size=size)
    # Ink the top of the shoe where panel 1's trouser hem hid it.
    edge = Ink(size, seed=5)
    edge.stroke([move(p) for p in PANEL1_SHOE_HIDDEN_TOP], [18, 22, 22, 20])
    return ink | edge.mask(), shape


HAND_WRIST = (1000, 2700)
HAND_TILT = 28
HAND_SCALE = 0.95
THUMB_BEND = -80


def panel_three(image):
    """Dad kneels turned towards us, gesturing with his far hand and resting
    the near one on his thigh.

    Everything of him outside the scanned crop (left of x=800 and below
    y=2060) is drawn here: his back and shirt, the rolled near sleeve, the
    hanging arm and hand, the far side of his shirt, the far sleeve and the
    gesturing arm down to its elbow, and his trousers and shoe. Lines that
    leave the crop are continued from where they cross its edge.
    """
    w, h = image.size
    ink = Ink((w, h), seed=3)
    # The near foot trails behind him, toe on the floor and its sole turned
    # back towards the left, so we see it foreshortened under his seat.
    shoe(ink, heel=(610, 2980), angle=124, scale=1.08, flip=True, foreshorten=0.6)
    # The seat, the thigh running towards us to the knee and the shin folded
    # back under it to the cuff.
    # Panel 1 makes his legs about 3.4 head widths long, so on his heels his
    # hip is about a head width above the floor. He is nearer us than Calvin,
    # so he meets the floor lower in the panel than Calvin does.
    ink.fill([(458, 2580), (446, 2642), (457, 2700), (452, 2780), (450, 2860),
              (462, 2940), (490, 3010), (540, 3062), (600, 3110), (680, 3170),
              (780, 3230), (900, 3272), (1050, 3290), (1200, 3292), (1300, 3280),
              (1370, 3245), (1410, 3185), (1425, 3110), (1415, 3030), (1380, 2955),
              (1320, 2885), (1240, 2825), (1140, 2775), (1040, 2745), (950, 2725),
              (880, 2712), (700, 2700), (600, 2650)], wobble=1.2)
    # Folds: the thigh's underside lying on the shin, and round the knee.
    ink.stroke([(1330, 3256), (1150, 3226), (950, 3180), (780, 3120)],
               [3, 14, 12, 6, 2], colour=255, wobble=0.8)
    ink.stroke([(1270, 2930), (1350, 2982), (1394, 3060), (1404, 3130)],
               [2, 10, 11, 3], colour=255, wobble=0.6)
    ink.stroke([(560, 2810), (640, 2846), (720, 2860)],
               [2, 9, 2], colour=255, wobble=0.6)

    # The shirt, hanging loose over the trousers. Its back runs on from the
    # shoulder where it leaves the crop at (800, 1796); its far side from the
    # placket line crossing the crop's foot at x=1210.
    back = [(830, 1752), (800, 1796), (750, 1855), (690, 1940), (650, 2020),
            (610, 2095), (562, 2210), (530, 2310), (508, 2400), (494, 2490),
            (470, 2570), (452, 2632), (462, 2672)]
    hem = [(452, 2640), (474, 2684), (522, 2718), (592, 2742), (690, 2754),
           (800, 2748), (900, 2740), (1000, 2748), (1090, 2760)]
    far_side = [(1217, 2000), (1210, 2059), (1190, 2105), (1150, 2165),
                (1105, 2235), (1068, 2310), (1046, 2390), (1042, 2470),
                (1050, 2560), (1066, 2660), (1086, 2756)]
    # White grounds first, so no fill covers another part's line.
    ink.fill(back + hem[1:] + [(1086, 2756)] + far_side[::-1] + [(1100, 1700)],
             colour=255, wobble=0)
    ink.fill([(1200, 2110), (1250, 2242), (1330, 2282), (1480, 2334), (1570, 2300),
              (1799, 2059), (1680, 2059), (1500, 2192), (1452, 2100), (1419, 2059),
              (1210, 2059)], colour=255, wobble=0)
    ink.stroke(back, [24, 22, 22, 21, 20])
    ink.stroke(hem, [20, 21, 19, 18])
    ink.stroke(far_side, [30, 26, 21, 20, 19, 19])
    # The placket's right-hand line runs down into the far side.
    ink.stroke([(1282, 2000), (1249, 2059), (1225, 2088), (1198, 2112)], [15, 15, 14])
    # Folds in the loose shirt.
    for fold, widths in (([(662, 2278), (626, 2334), (592, 2392)], [3, 14, 4]),
                         ([(702, 2378), (642, 2420), (584, 2458)], [3, 13, 3]),
                         ([(702, 2568), (632, 2600), (562, 2614)], [3, 13, 3]),
                         ([(1064, 2300), (1022, 2328), (986, 2344)], [3, 12, 3]),
                         ([(1042, 2404), (1002, 2432), (968, 2446)], [3, 11, 3])):
        ink.stroke(fold, widths)

    # The far sleeve and the gesturing arm. The arm's two edges and the
    # sleeve's top continue the lines crossing the crop's foot at x=1680,
    # 1799 and 1419.
    ink.stroke([(1198, 2106), (1222, 2176), (1250, 2242)], [16, 18, 17])
    ink.stroke([(1250, 2244), (1300, 2198), (1370, 2144), (1442, 2104)], [17, 18, 16])
    ink.stroke([(1360, 2030), (1400, 2049), (1419, 2059), (1440, 2076), (1452, 2102)],
               [19, 19, 18, 16])
    ink.stroke([(1372, 2045), (1384, 2059), (1396, 2086), (1404, 2120)], [12, 11, 6])
    ink.stroke([(1345, 2000), (1330, 2059), (1300, 2080), (1252, 2096)], [10, 10, 9, 3])
    ink.stroke([(1452, 2102), (1486, 2148), (1502, 2192)], [16, 15, 12])
    ink.stroke([(1738, 2000), (1680, 2059), (1600, 2116), (1532, 2164), (1500, 2194)],
               [22, 22, 20, 18, 12])
    ink.stroke([(1262, 2250), (1330, 2282), (1420, 2318), (1480, 2336), (1524, 2330),
                (1572, 2298), (1640, 2234), (1722, 2148), (1799, 2059), (1846, 2005)],
               [18, 20, 21, 22, 22, 21, 22, 23])

    # The near sleeve, as Dad's sleeves are drawn in panels 1 and 2: long
    # and loose, nearly to the elbow and about twice the arm's width, with a
    # turned-up cuff. Its front edge is the line leaving the crop at x=942;
    # its back edge leaves his back below the shoulder.
    hand_ink, hand_shape, thumb_end, palm_end = resting_hand(image, HAND_WRIST, HAND_TILT, HAND_SCALE)
    thumb_ink, thumb_shape = resting_thumb(image, HAND_WRIST, HAND_TILT, HAND_SCALE, THUMB_BEND)
    # The arm below the sleeve: a short stretch of upper arm, the elbow, and
    # the forearm reaching forward along his thigh to the hand.
    left = [(721, 2392), (714, 2440), (722, 2496), (760, 2560), (830, 2630), thumb_end]
    right = [(901, 2390), (896, 2430), (924, 2500), (962, 2580), palm_end]
    ink.fill(left + right[::-1], colour=255, wobble=0)
    sleeve_back = [(728, 1900), (700, 2000), (682, 2120), (670, 2240), (664, 2330)]
    sleeve_front = [(953, 2000), (942, 2059), (946, 2150), (956, 2250), (964, 2330)]
    ink.fill(sleeve_back + sleeve_front[::-1], colour=255, wobble=0)
    ink.stroke(sleeve_back, [4, 18, 20, 20, 19])
    ink.stroke(sleeve_front, [20, 20, 20, 19, 19])
    ink.stroke([(860, 2160), (852, 2230), (842, 2280)], [3, 12, 3])
    outlined(ink, [(660, 2318), (810, 2306), (968, 2322), (978, 2352), (972, 2388),
                   (810, 2376), (658, 2386), (650, 2352)])
    # The forearm's edges go over the hand's wrist so the two join.
    edges = Ink((w, h), seed=4)
    edges.stroke(left, [19, 20, 19, 20, 18])
    edges.stroke(right, [19, 19, 20, 18])

    yy, xx = np.mgrid[:h, :w]
    region = ((xx < 800) | (yy >= 2060)) & (xx < 1900) & ~((xx >= 1440) & (yy >= 2600))
    drawing = ink.mask()
    drawing[thumb_shape] = False
    drawing |= thumb_ink
    drawing[hand_shape] = False
    drawing |= hand_ink | edges.mask()
    return composite(image, drawing, region)
