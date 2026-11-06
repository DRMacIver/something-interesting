"""Dad's kneeling legs and shoes in panels 2 and 3, drawn programmatically.

The scan stops at Dad's waist in both close-ups, so everything below the
crop is drawn here in code rather than generated. The drawing follows the
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


def polygon_mask(size, points):
    from PIL import Image, ImageDraw
    image = Image.new('1', size, 0)
    ImageDraw.Draw(image).polygon(points, fill=1)
    return np.asarray(image)


def panel_three(image):
    """Dad kneels turned towards us, his near hand resting on his thigh.

    The shirt and hand above the trousers are kept; the trousers below them,
    the knee and the trailing shoe are drawn here.
    """
    w, h = image.size
    ink = Ink((w, h), seed=3)
    # The near foot trails behind him, toe on the floor and its sole turned
    # back towards the left, so we see it foreshortened under his seat.
    shoe(ink, heel=(612, 2846), angle=124, scale=1.08, flip=True, foreshorten=0.6)
    # The seat, the thigh running towards us to the knee and the shin folded
    # back under it to the cuff. The right-hand contour, from the fingertips
    # round the knee, is the existing silhouette's.
    ink.fill([(458, 2580), (446, 2642), (457, 2700), (456, 2740), (456, 2780),
              (466, 2820), (488, 2860), (528, 2896), (590, 2924), (640, 2944),
              (628, 2980), (668, 3030), (720, 3070), (800, 3104), (900, 3126),
              (1050, 3134), (1200, 3132), (1317, 3120), (1357, 3100), (1394, 3060),
              (1416, 3020), (1429, 2980), (1436, 2940), (1430, 2900), (1412, 2860),
              (1382, 2820), (1362, 2800), (1337, 2780), (1306, 2740), (1268, 2700),
              (1201, 2660), (1100, 2690), (800, 2700), (600, 2640)], wobble=1.2)
    # Folds: the thigh's underside over the shin, round the knee and the hip.
    ink.stroke([(1318, 3082), (1160, 3060), (960, 3024), (780, 2986)],
               [3, 14, 12, 6, 2], colour=255, wobble=0.8)
    ink.stroke([(1262, 2884), (1336, 2910), (1384, 2956), (1398, 3002)],
               [2, 10, 11, 3], colour=255, wobble=0.6)
    ink.stroke([(560, 2800), (640, 2836), (720, 2850)],
               [2, 9, 2], colour=255, wobble=0.6)
    # Keep the shirt above its hem and the whole hand.
    keep = polygon_mask((w, h), [
        (0, 0), (w, 0), (w, 2790), (1372, 2790), (1352, 2852), (1150, 2852),
        (1090, 2812), (1000, 2772), (900, 2756), (780, 2752), (700, 2752),
        (620, 2746), (570, 2724), (536, 2702), (512, 2682), (490, 2662),
        (477, 2642), (0, 2642)])
    yy, xx = np.mgrid[:h, :w]
    region = ~keep & (xx < 1480)
    return composite(image, ink.mask(), region)
