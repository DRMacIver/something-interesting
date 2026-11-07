"""Dad in panel 3 outside the scanned crop, from a ChatGPT drawing.

dad3-chatgpt.webp is a full drawing of Dad kneeling in this panel's pose,
made with ChatGPT from the strip. It is placed over the scan by its head
(matched to Watterson's head and glasses by chamfer matching, see
REGISTRATION), then warped gently so that each of its lines that crosses the
crop's edge meets the scan's own line there (CONTROLS); points far from the
crop stay put. Only its ink outside the crop is used: inside it, the scan
is kept exactly.

All coordinates are pixels of the full-panel export, where the scan sits
at (800, 0) and is 1574 x 2060.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw
from scipy import ndimage
from scipy.interpolate import RBFInterpolator

from ink import Ink

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'dad3-chatgpt.webp'
CROP = (800, 0, 2374, 2060)

# The drawing's pixel (u, v) lands at s*R(theta)(u, v) + (tx, ty).
REGISTRATION = dict(scale=1.9241, theta=-0.012514, tx=125.34, ty=815.49)

# (where a line of the registered drawing is, where the scan's line is).
# Along the crop's foot (y=2060) and left edge (x=800), plus a point just
# inside for each, so the lines also leave the crop in the scan's direction.
CONTROLS = [
    # Shoulder and back, leaving the left edge.
    ((800, 1848), (800, 1796)), ((820, 1818), (820, 1770)),
    # The near sleeve's back line, whose top would otherwise be cut by the crop.
    ((822, 1912), (776, 1896)), ((808, 1990), (768, 1980)),
    # The near sleeve's inner line.
    ((1006, 2000), (953, 2000)), ((1000, 2060), (942, 2060)), ((990, 2160), (936, 2160)),
    # The placket's two lines.
    ((1186, 2060), (1210, 2060)), ((1218, 2060), (1249, 2060)),
    # The far shoulder, running on into the far sleeve.
    ((1346, 2060), (1420, 2060)), ((1318, 2040), (1376, 2040)),
    # The gesturing forearm's two edges.
    ((1712, 2000), (1738, 2000)), ((1643, 2060), (1681, 2060)),
    ((1817, 2040), (1819, 2040)), ((1774, 2060), (1803, 2060)),
]
# Points that stay where they are: the legs, the floor and well clear of the crop.
FIXED = [(300, 2500), (300, 3100), (900, 3150), (1500, 3150), (2100, 3100),
         (1300, 2750), (700, 2700), (2300, 2500), (100, 1500), (2900, 1500),
         (2900, 3500), (100, 3500), (1500, 3600)]
# The drawing's hand is a little lower than Watterson's: what of it shows
# below the crop is cut away.
HAND_BELOW_CROP = (1850, 2060, 2374, 2200)
# The drawing's floor marks are not in the strip (Watterson draws no floor
# here): they are whitened out of the source, in its own pixels.
# The shirt's front edge ends in a little outward hook where it meets the
# near arm (Codex: "an arbitrary hooked projection"): it is whitened and the
# edge drawn straight on into the arm instead, in the source's pixels.
HEM_HOOK = [(457, 802), (492, 802), (492, 846), (450, 846), (449, 834)]
HEM_EDGE = [(468, 788), (459, 812), (446, 840)]
FLOOR_MARKS = [[(25, 1138), (93, 1138), (93, 1182), (25, 1182)],
               [(703, 1128), (830, 1128), (830, 1178), (703, 1178)]]


# The drawing's far sleeve ended in a long straight hem and a pointed corner
# hanging below the arm, so it read as a flap laid over it. Its hem,
# underside and the elbow are erased (paths, widths) and redrawn: a shorter
# sleeve with a rounded cap running on from the scan's shoulder line, a hem
# the arm fills, a short stretch of upper arm from the hem to the inside of
# the elbow, and one curve under the elbow into the forearm. Chosen over
# five rounds of Codex A/B critique.
FAR_SLEEVE_ERASE = [
    ([(1165, 2215), (1225, 2250), (1290, 2300)], 48),
    ([(1290, 2300), (1360, 2242), (1420, 2192), (1452, 2163)], 46),
    ([(1352, 2262), (1400, 2283), (1445, 2310), (1486, 2340), (1530, 2318),
      (1565, 2296), (1598, 2278), (1626, 2262)], 46),
    ([(1490, 2108), (1490, 2150), (1530, 2162), (1560, 2152)], 40),
    ([(1452, 2130), (1468, 2142)], 22),
    ([(1436, 2078), (1462, 2100), (1482, 2116)], 34),
]
FAR_SLEEVE_DRAW = [
    # Underside, from the shirt's far side.
    ([(1118, 2196), (1170, 2204), (1226, 2210), (1272, 2212), (1294, 2208)], [18, 18, 19, 19, 18]),
    # Hem.
    ([(1288, 2214), (1330, 2206), (1376, 2186), (1416, 2162), (1448, 2142)], [20, 21, 21, 20, 19]),
    # Cap, from the scan's shoulder line.
    ([(1420, 2060), (1440, 2074), (1458, 2092), (1462, 2114), (1450, 2140)], [19, 19, 19, 19, 18]),
    # The upper arm's top, out of the hem to the inside of the elbow.
    ([(1436, 2158), (1464, 2167), (1494, 2172)], [11, 12, 13]),
    # The forearm's top edge, down to the inside of the elbow.
    ([(1600, 2128), (1566, 2148), (1530, 2163), (1494, 2172)], [20, 20, 19, 18]),
    # Under the upper arm and elbow, into the forearm.
    ([(1302, 2214), (1356, 2248), (1414, 2278), (1462, 2298), (1490, 2300), (1516, 2291),
      (1556, 2273), (1600, 2255), (1640, 2241), (1662, 2232)], [18, 19, 19, 20, 20, 20, 20, 20, 20, 20]),
]


def registered(size):
    """The drawing placed over the scan by its head, as a grey image."""
    r = REGISTRATION
    c, s = np.cos(r['theta']), np.sin(r['theta'])
    forward = np.array([[r['scale'] * c, -r['scale'] * s, r['tx']],
                        [r['scale'] * s, r['scale'] * c, r['ty']], [0, 0, 1]])
    inverse = np.linalg.inv(forward)
    image = Image.open(SOURCE).convert('L')
    draw = ImageDraw.Draw(image)
    for marks in FLOOR_MARKS + [HEM_HOOK]:
        draw.polygon(marks, fill=255)
    # Drawn at four times the source's size and shrunk to grey, so it is
    # antialiased like the source's own lines and enlarges as smoothly.
    edge = Ink((4 * image.width, 4 * image.height), seed=7)
    edge.stroke([(4 * x, 4 * y) for x, y in HEM_EDGE], [36, 40, 40])
    cover = Image.fromarray(np.where(edge.mask(), 0, 255).astype(np.uint8))
    image = ImageChops.darker(image, cover.resize(image.size, Image.BOX))
    return image.transform(size, Image.AFFINE, tuple(inverse[:2].ravel()),
                           resample=Image.BICUBIC, fillcolor=255)


def warped(size, step=8):
    """The registered drawing warped so its lines meet the scan's at the crop."""
    grey = np.asarray(registered(size), float)
    targets = np.array([t for _, t in CONTROLS] + FIXED, float)
    sources = np.array([s for s, _ in CONTROLS] + FIXED, float)
    # For each output point, where to read the registered drawing.
    lookup = RBFInterpolator(targets, sources - targets, kernel='thin_plate_spline')
    w, h = size
    gy, gx = np.mgrid[0:h + step:step, 0:w + step:step]
    shift = lookup(np.stack([gx.ravel(), gy.ravel()], 1)).reshape(*gx.shape, 2)
    yy, xx = np.mgrid[:h, :w]
    dx = ndimage.map_coordinates(shift[..., 0], [yy / step, xx / step], order=1)
    dy = ndimage.map_coordinates(shift[..., 1], [yy / step, xx / step], order=1)
    return ndimage.map_coordinates(grey, [yy + dy, xx + dx], order=1, cval=255) < 128


def cleaned(ink):
    """Remove what shows of the drawing's hand below the crop."""
    x0, y0, x1, y1 = HAND_BELOW_CROP
    ink[y0:y1, x0:x1] = False
    return ink


def panel_three(image):
    """Ink Dad outside the scanned crop over `image`: the warped drawing with
    its far sleeve redrawn, plus the ends of the two shirt folds that the
    scan cuts off at its foot."""
    w, h = image.size
    drawing = cleaned(warped((w, h)))
    folds = Ink((w, h), seed=5)
    folds.stroke([(1345, 2000), (1330, 2059), (1310, 2080), (1282, 2094)], [10, 10, 8, 3])
    folds.stroke([(1372, 2045), (1384, 2059), (1389, 2072), (1392, 2082)], [12, 11, 6, 2])
    drawing |= folds.mask()
    erase = Ink((w, h), seed=11)
    for path, width in FAR_SLEEVE_ERASE:
        erase.stroke(path, [width] * len(path), wobble=0)
    drawing &= ~erase.mask()
    sleeve = Ink((w, h), seed=12)
    for path, widths in FAR_SLEEVE_DRAW:
        sleeve.stroke(path, widths)
    drawing |= sleeve.mask()
    a = np.asarray(image).copy()
    yy, xx = np.mgrid[:h, :w]
    x0, y0, x1, y1 = CROP
    outside = ~((xx >= x0) & (xx < x1) & (yy < y1))
    # Inked over what is there, so Calvin and the player stay.
    a[outside & drawing] = 0
    return Image.fromarray(a)
