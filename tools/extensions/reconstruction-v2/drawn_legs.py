"""Dad's figure outside the scanned close-ups of panels 2 and 3, drawn in code.

The scan stops at Dad's waist in panel 2 and at his chest in panel 3, so
everything of him beyond the crops is drawn here rather than generated:
his legs and shoes in both, and in panel 3 also his back, shirt, sleeves,
arms and the hand resting on his thigh. Where Watterson drew the same
thing elsewhere in the strip it is reused instead (see transplant): the
tucked-under shoe in both is panel 1's front shoe turned over, and panel
3's resting hand is his own gesturing hand turned palm down. The drawing follows the
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
PANEL2_SHOE = (372, 2206)
PANEL2_SHOE_TURN = 181
PANEL2_SHOE_SCALE = (1.25, 1.25)


def panel_two(image):
    """Dad sits on his heels facing right, knee by the record player."""
    w, h = image.size
    ink = Ink((w, h), seed=2)
    # His near foot lies behind him on its upper, toe back on the floor and
    # sole turned up, heel under his seat. The far foot is hidden behind it.
    shoe_ink, shoe_shape = panel_one_shoe('front', PANEL2_SHOE, PANEL2_SHOE_TURN,
                                          PANEL2_SHOE_SCALE, (w, h))
    ink.paint(shoe_shape, 255)
    ink.paint(shoe_ink, 0)
    # The trousers: seat, thigh and the shin folded under it along the floor,
    # ending in a cuff at the ankle just behind the seat. The first and last
    # three points are the scanned silhouette's edges on the crop's last
    # rows, so the drawing continues it without a step.
    ink.fill([(426, 2000), (429, 2040), (432, 2058), (440, 2112), (452, 2156),
              (462, 2196), (474, 2240), (490, 2276), (540, 2306), (630, 2342),
              (760, 2374), (1000, 2384), (1200, 2380), (1282, 2362),
              (1326, 2312), (1334, 2252), (1306, 2196), (1240, 2150), (1150, 2112),
              (1090, 2082), (1051, 2058), (1033, 2040), (980, 2000), (700, 1990)],
             wobble=1.2)
    # Folds: where the thigh lies on the calf, and round the knee.
    ink.stroke([(1238, 2302), (1100, 2290), (900, 2282), (760, 2286)],
               [3, 13, 11, 6, 2], colour=255, wobble=0.8)
    ink.stroke([(1180, 2178), (1250, 2208), (1290, 2252), (1296, 2296)],
               [2, 9, 11, 3], colour=255, wobble=0.6)
    ink.stroke([(560, 2150), (640, 2178), (700, 2186)],
               [2, 8, 2], colour=255, wobble=0.6)
    # The calf, lifting off the floor towards the ankle.
    ink.stroke([(720, 2330), (620, 2300), (540, 2262)],
               [2, 9, 8, 2], colour=255, wobble=0.6)
    yy, xx = np.mgrid[:h, :w]
    region = (yy >= 2060) & (xx < 1540)
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
    over, then tilted by `angle` degrees so the fingers drape over the thigh
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


# Dad's shoes in panel 1, in the coordinates of the full panel 1 export
# (locked-1.png is that less 400px on the left). Each has a polygon around
# it that stops at the trouser hem, the segments that close it there, a
# centre to turn it about, and the line of the outline the trousers hid.
PANEL1_SHOES = {
    # The front shoe, landing heel first with its toe up and sole forward.
    'front': dict(
        keep=[(1130, 1620), (1130, 2020), (820, 2020), (820, 1900), (860, 1880),
              (905, 1868), (950, 1840), (985, 1800), (990, 1700), (1000, 1620)],
        close=[((860, 1882), (905, 1868)), ((905, 1868), (950, 1840)),
               ((950, 1840), (985, 1800)), ((985, 1800), (992, 1720))],
        centre=(975, 1845),
        hidden=[(858, 1890), (905, 1868), (950, 1840), (985, 1800), (994, 1730)]),
    # The planted back shoe in side view; only the part inside the scan.
    'back': dict(
        keep=[(400, 1872), (520, 1866), (670, 1866), (670, 2016), (400, 2016)],
        close=[((400, 1872), (400, 2016)), ((400, 1874), (520, 1868))],
        centre=(530, 1940),
        hidden=[(380, 1874), (450, 1871), (520, 1872), (560, 1880)]),
}


def panel_one_shoe(which, target, angle, scale, size):
    """One of panel 1's shoes, moved to `target` and turned by `angle`."""
    from pathlib import Path
    from PIL import Image
    shoe = PANEL1_SHOES[which]
    locked = Image.open(Path(__file__).resolve().parent / 'locked-1.png').convert('L')
    source = Image.new('L', (locked.width + 400, locked.height), 255)
    source.paste(locked, (400, 0))
    ink, shape, move = transplant(source, shoe['keep'], shoe['close'], shoe['centre'],
                                  target, angle, scale=scale, size=size)
    edge = Ink(size, seed=5)
    edge.stroke([move(p) for p in shoe['hidden']], [16, 20, 21, 20, 16])
    return ink | edge.mask(), shape


PANEL3_SHOE = (530, 2870)
PANEL3_SHOE_TURN = 178
PANEL3_SHOE_SCALE = (1.42, 1.42)

HAND_WRIST = (968, 2650)
HAND_TILT = 34
HAND_SCALE = 0.9


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
    # His foot is tucked under him on its toes, heel up under his seat and
    # sole turned back, as Watterson draws a crouching Dad: panel 1's front
    # shoe turned over, with only its toe end showing below the seat.
    shoe_ink, shoe_shape = panel_one_shoe('front', PANEL3_SHOE, PANEL3_SHOE_TURN,
                                          PANEL3_SHOE_SCALE, (w, h))
    ink.paint(shoe_shape, 255)
    ink.paint(shoe_ink, 0)
    # The seat, the thigh running towards us to the knee and the shin folded
    # back under it to the cuff.
    ink.fill([(458, 2580), (446, 2642), (457, 2700), (456, 2740), (456, 2780),
              (462, 2840), (478, 2896), (512, 2940), (566, 2978), (640, 3030),
              (720, 3074), (800, 3104), (900, 3126),
              (1050, 3134), (1200, 3132), (1317, 3120), (1357, 3100), (1394, 3060),
              (1416, 3020), (1429, 2980), (1436, 2940), (1430, 2900), (1412, 2860),
              (1376, 2806), (1310, 2748), (1220, 2700), (1120, 2660), (900, 2660),
              (600, 2640)], wobble=1.2)
    ink.stroke([(1318, 3082), (1160, 3060), (960, 3024), (780, 2986)],
               [3, 14, 12, 6, 2], colour=255, wobble=0.8)
    ink.stroke([(1262, 2884), (1336, 2910), (1384, 2956), (1398, 3002)],
               [2, 10, 11, 3], colour=255, wobble=0.6)
    ink.stroke([(560, 2800), (640, 2836), (720, 2850)],
               [2, 9, 2], colour=255, wobble=0.6)

    # The shirt, hanging loose over the trousers. Its back runs on from the
    # shoulder where it leaves the crop at (800, 1796); its far side from the
    # placket line crossing the crop's foot at x=1210.
    back = [(830, 1752), (800, 1796), (750, 1855), (690, 1940), (650, 2020),
            (610, 2095), (562, 2210), (530, 2310), (508, 2400), (494, 2490),
            (470, 2570), (452, 2632), (462, 2672)]
    hem = [(452, 2640), (474, 2684), (522, 2718), (592, 2742), (690, 2754),
           (800, 2748), (900, 2728), (980, 2700)]
    far_side = [(1217, 2000), (1210, 2059), (1190, 2105), (1150, 2165),
                (1105, 2235), (1068, 2310), (1046, 2390), (1042, 2470),
                (1050, 2560), (1068, 2650)]
    # White grounds first, so no fill covers another part's line.
    ink.fill(back + hem[1:] + [(1070, 2660)] + far_side[::-1] + [(1100, 1700)],
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

    # The near sleeve, rolled into a cuff just below where its front edge
    # leaves the crop at x=942.
    ink.stroke([(794, 1930), (772, 2000), (756, 2066)], [3, 16, 18])
    ink.stroke([(953, 2000), (942, 2059), (944, 2072)], [20, 20, 18])
    outlined(ink, [(706, 2068), (830, 2058), (946, 2072), (962, 2115), (956, 2165),
                   (850, 2156), (704, 2158), (696, 2112)])
    ink.stroke([(714, 2112), (830, 2104), (954, 2122)], [3, 11, 10, 3])
    # The upper arm hangs straight from the cuff to the elbow; the forearm
    # reaches forward from there to the hand on his thigh.
    hand_ink, hand_shape, thumb_end, palm_end = resting_hand(image, HAND_WRIST, HAND_TILT, HAND_SCALE)
    left = [(745, 2162), (734, 2240), (726, 2296), (738, 2352), (790, 2450),
            (860, 2556), thumb_end]
    right = [(900, 2164), (890, 2230), (884, 2284), (900, 2360), (938, 2458),
             (972, 2556), palm_end]
    ink.fill(left + right[::-1], colour=255, wobble=0)
    # The forearm's edges go over the hand's wrist so the two join.
    edges = Ink((w, h), seed=4)
    edges.stroke(left, [19, 20, 19, 20, 18])
    edges.stroke(right, [19, 19, 20, 18])

    yy, xx = np.mgrid[:h, :w]
    region = ((xx < 800) | (yy >= 2060)) & (xx < 1900) & ~((xx >= 1700) & (yy >= 2600))
    drawing = ink.mask()
    drawing[hand_shape] = False
    drawing |= hand_ink | edges.mask()
    return composite(image, drawing, region)
