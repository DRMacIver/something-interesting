"""Dad's figure outside the scanned close-ups of panels 2 and 3, drawn in code.

The scan stops at Dad's waist in panel 2 and at his chest in panel 3, so
everything of him beyond the crops is drawn here rather than generated:
his legs and shoes in both, and in panel 3 also his back, shirt, sleeves,
arms and the hand resting on his thigh. The drawing follows the
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


def panel_two(image):
    """Dad sits on his heels facing right, knee by the record player."""
    w, h = image.size
    ink = Ink((w, h), seed=2)
    # His near foot lies behind him on its upper, toe back on the floor and
    # sole turned up, heel under his seat. The far foot is hidden behind it.
    shoe(ink, heel=(600, 2270), angle=176, scale=0.86, flip=True)
    # The trousers: seat, thigh and the shin folded under it along the floor,
    # ending in a cuff at the ankle just behind the seat. The first and last
    # three points are the scanned silhouette's edges on the crop's last
    # rows, so the drawing continues it without a step.
    ink.fill([(426, 2000), (429, 2040), (432, 2058), (440, 2112), (458, 2160),
              (488, 2196), (504, 2214), (478, 2236), (462, 2280), (460, 2336),
              (474, 2376), (800, 2382), (1000, 2384), (1200, 2380), (1282, 2362),
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
    yy, xx = np.mgrid[:h, :w]
    region = (yy >= 2060) & (xx < 1540)
    return composite(image, ink.mask(), region)


def outlined(ink, points, width=OUTLINE + 2):
    """A white shape with a closed ink outline."""
    ink.fill(points, colour=255, wobble=0)
    ink.stroke(points, [width, width * 1.1, width * 0.95, width * 1.15, width], closed=True)


HAND = [  # (centre line, width): back of the hand, then far to near fingers
    ([(965, 2640), (1050, 2690), (1130, 2730)], 96),
    ([(1150, 2700), (1230, 2735), (1300, 2790)], 40),
    ([(1135, 2722), (1215, 2762), (1275, 2825)], 44),
    ([(1110, 2745), (1185, 2790), (1235, 2855)], 46),
    ([(1080, 2765), (1140, 2810), (1175, 2862)], 44),
    ([(1000, 2715), (1030, 2765), (1052, 2805)], 42),
]


def hand_outline(ink):
    for points, width in HAND:
        ink.stroke(points, [width + 2 * OUTLINE], wobble=1.0)


def hand_fill(ink):
    for points, width in HAND:
        ink.stroke(points, [width], colour=255, wobble=0.6)


def hand_gaps(ink):
    for gap in ([(1175, 2735), (1240, 2770), (1288, 2812)],
                [(1150, 2757), (1210, 2795), (1255, 2846)],
                [(1118, 2780), (1162, 2820), (1200, 2862)],
                [(1045, 2775), (1065, 2805)]):
        ink.stroke(gap, [3, 12, 14, 6])


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
    shoe(ink, heel=(612, 2846), angle=124, scale=1.08, flip=True, foreshorten=0.6)
    # The seat, the thigh running towards us to the knee and the shin folded
    # back under it to the cuff.
    ink.fill([(458, 2580), (446, 2642), (457, 2700), (456, 2740), (456, 2780),
              (466, 2820), (488, 2860), (528, 2896), (590, 2924), (640, 2944),
              (628, 2980), (668, 3030), (720, 3070), (800, 3104), (900, 3126),
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

    # The near sleeve, rolled into a cuff above the elbow.
    ink.stroke([(794, 1930), (772, 2000), (752, 2090)], [3, 16, 18])
    ink.stroke([(953, 2000), (942, 2059), (936, 2094)], [20, 20, 18])
    outlined(ink, [(708, 2094), (830, 2080), (948, 2098), (966, 2150), (958, 2206),
                   (850, 2194), (706, 2192), (698, 2142)])
    ink.stroke([(716, 2150), (830, 2142), (956, 2160)], [3, 11, 10, 3])
    # The near arm hangs from the cuff, bends a little at the elbow and
    # reaches forward to the thigh.
    left = [(745, 2196), (738, 2300), (714, 2400), (708, 2445), (734, 2506),
            (800, 2580), (880, 2640), (930, 2662)]
    right = [(900, 2202), (880, 2300), (864, 2380), (862, 2440), (898, 2516),
             (946, 2582), (962, 2598)]
    hand_outline(ink)
    ink.fill(left + [(960, 2700), (1010, 2690)] + right[::-1], colour=255, wobble=0)
    hand_fill(ink)
    ink.stroke(left, [19, 20, 19, 20, 18])
    ink.stroke(right, [19, 19, 20, 18])
    hand_gaps(ink)

    yy, xx = np.mgrid[:h, :w]
    region = ((xx < 800) | (yy >= 2060)) & (xx < 1900) & ~((xx >= 1700) & (yy >= 2600))
    return composite(image, ink.mask(), region)
