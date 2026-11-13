"""Graft a whole-scene drawing onto a scanned close-up.

The scanned panels are close-ups: Watterson's crop ends at Dad's chest. An
image model can draw the whole scene well when left free to redraw it, but
it cannot hold the scan's pixels fixed. So the drawing (the *candidate*) is
fitted to the scan here instead:

1. `register` finds the scale, turn and shift at which the candidate lies
   over the scan (correlation over a range of scales, then a chamfer fit);
   `fit_figures` then fits each separate figure in the scan on its own,
   since the model draws each at its own size, and `between` blends them.
2. `flow` measures how the candidate still differs from the scan inside
   the crop and bends it to agree, fading the bend out away from the crop.
3. `snap` slides the candidate along each edge of the crop so its lines
   leave the crop exactly where the scan's do; `push_out` moves clear of
   the crop any line the candidate draws along its edge, which pasting the
   scan back would otherwise slice lengthways.
4. `reink` gives what is left of the candidate the scan's line weight, cuts
   it to the scan's 1-bit grid and smooths it as the scan was smoothed.

The scan is then pasted back, untouched. `graft` runs all four and reports
how well the candidate fitted, so candidates can be ranked by measurement.

Registration works on the scan's own grid (half the export size); `Frame`
says how much paper to add around the crop.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, optimize
from skimage.feature import match_template
from skimage.morphology import skeletonize
from skimage.registration import optical_flow_tvl1

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import build_assets  # noqa: E402

CAP = 25.0  # distances beyond this (scan px) all count the same


@dataclass
class Frame:
    """Paper around the crop, in scan pixels, and rows at the crop's top to
    leave out of the fit (empty space where the lettering was)."""
    left: int
    right: int
    below: int
    skip: int = 0


def to_ink(image, threshold=128):
    return np.asarray(image.convert('L')) < threshold


def soft(mask, sigma):
    return ndimage.gaussian_filter(mask.astype(np.float32), sigma)


def capped_distance(mask):
    return np.minimum(ndimage.distance_transform_edt(~mask), CAP)


# --- 1. similarity fit ------------------------------------------------------

def coarse(scan, cand, scales, keep=4):
    """The best few (correlation, scale, dx, dy) at which the candidate,
    scaled, covers the scan. Windows holding far less or far more ink than
    the scan are ignored: correlation means nothing on blank paper."""
    template = soft(scan, 3)
    amount = template.sum()
    box = np.ones(scan.shape, np.float32)
    found = []
    for scale in scales:
        size = (round(cand.shape[1] * scale), round(cand.shape[0] * scale))
        if size[0] <= scan.shape[1] or size[1] <= scan.shape[0]:
            continue
        resized = np.asarray(Image.fromarray(cand.astype(np.float32)).resize(size, Image.BILINEAR))
        resized = ndimage.gaussian_filter(resized, 3)
        score = match_template(resized, template)
        window = ndimage.uniform_filter(resized, scan.shape, mode='constant') * box.size
        oy, ox = scan.shape[0] // 2, scan.shape[1] // 2
        window = window[oy:oy + score.shape[0], ox:ox + score.shape[1]]
        score[(window < 0.5 * amount) | (window > 2.5 * amount)] = -1
        y, x = np.unravel_index(np.argmax(score), score.shape)
        found.append((float(score[y, x]), float(scale), -float(x), -float(y)))
    return sorted(found, reverse=True)[:keep]


def to_scan(points, params):
    """Candidate (x, y) points in scan coordinates."""
    scale, theta, tx, ty = params
    c, s = scale * np.cos(theta), scale * np.sin(theta)
    x, y = points[:, 0], points[:, 1]
    return np.stack([c * x - s * y + tx, s * x + c * y + ty], 1)


def to_candidate(points, params):
    scale, theta, tx, ty = params
    c, s = np.cos(theta) / scale, np.sin(theta) / scale
    x, y = points[:, 0] - tx, points[:, 1] - ty
    return np.stack([c * x + s * y, -s * x + c * y], 1)


def sample(image, points, outside):
    return ndimage.map_coordinates(image, [points[:, 1], points[:, 0]], order=1,
                                   mode='constant', cval=outside)


def refine(scan, cand, start, seed=0, near=None, prior=0.0):
    """Chamfer fit from a start (scale, turn, dx, dy). Distances are sampled
    at a few thousand ink points each way, so each step is cheap. `near`
    keeps only the candidate ink that starts within that many px of the
    scan's (to fit one figure of several); `prior` charges for straying
    from the start."""
    rng = np.random.default_rng(seed)
    start = np.array(start, dtype=np.float64)

    def points(mask, n):
        ys, xs = np.nonzero(mask)
        pick = rng.choice(len(xs), min(n, len(xs)), replace=False)
        return np.stack([xs[pick], ys[pick]], 1).astype(np.float64)

    scan_points, cand_points = points(scan, 6000), points(cand, 20000)
    scan_distance = capped_distance(scan).astype(np.float32)
    cand_distance = ndimage.distance_transform_edt(~cand).astype(np.float32)
    h, w = scan.shape
    if near is not None:
        reach = ndimage.distance_transform_edt(~scan).astype(np.float32)
        cand_points = cand_points[sample(reach, to_scan(cand_points, start), 1e6) < near]

    def cost(p):
        there = to_scan(cand_points, p)
        inside = (there[:, 0] >= 0) & (there[:, 0] < w) & (there[:, 1] >= 0) & (there[:, 1] < h)
        if inside.sum() < 200:
            return 2 * CAP
        forward = sample(scan_distance, there[inside], CAP).mean()
        back = np.minimum(sample(cand_distance, to_candidate(scan_points, p), CAP) * p[0], CAP).mean()
        strayed = ((p[0] / start[0] - 1) / 0.15) ** 2 + ((p[1] - start[1]) / 0.1) ** 2 \
            + ((p[2] - start[2]) ** 2 + (p[3] - start[3]) ** 2) / 60.0 ** 2
        return (forward + back) / 2 + prior * strayed

    unit = np.array([start[0], 0.02, 10.0, 10.0])
    offset = np.array([0.0, start[1], 0.0, 0.0])
    x0 = np.array([1.0, 0.0, start[2] / 10, start[3] / 10])
    result = optimize.minimize(lambda x: cost(x * unit + offset), x0, method='Powell',
                               options=dict(xtol=1e-4, ftol=1e-5))
    return result.x * unit + offset, float(result.fun)


def register(scan, cand, scales):
    """(params, cost): candidate → scan as scale, turn, shift."""
    best = None
    for _, scale, dx, dy in coarse(scan, cand, scales):
        params, cost = refine(scan, cand, (scale, 0.0, dx, dy))
        if best is None or cost < best[1]:
            best = (params, cost)
    if best is None:
        raise ValueError('candidate is too small to cover the scan at any scale tried')
    return best


def place(cand, params, shape, origin=(0.0, 0.0), zoom=1):
    """The candidate (as float coverage) drawn in a frame of `shape` whose
    top-left corner is at `origin` in scan coordinates, `zoom` times the
    scan's size."""
    scale, theta, tx, ty = params
    c, s = np.cos(theta) / (scale * zoom), np.sin(theta) / (scale * zoom)
    # frame (row, col) → candidate (row, col)
    matrix = np.array([[c, -s], [s, c]])
    shift = np.array([origin[1] - ty, origin[0] - tx])
    offset = np.array([[c * zoom, -s * zoom], [s * zoom, c * zoom]]) @ shift
    return ndimage.affine_transform(cand.astype(np.float32), matrix, offset=offset,
                                    output_shape=shape, order=1, cval=0.0)


def figures(scan, share=0.12, gap=10):
    """The scan's ink split into its separate figures (masks): groups of
    ink more than `gap` px apart. Groups with less than `share` of the ink
    go with the nearest larger one."""
    labels, count = ndimage.label(ndimage.binary_dilation(scan, iterations=gap))
    labels = labels * scan
    sizes = ndimage.sum(scan, labels, range(1, count + 1))
    large = [i + 1 for i, size in enumerate(sizes) if size >= share * scan.sum()]
    if len(large) < 2:
        return [scan]
    nearest = np.argmin([ndimage.distance_transform_edt(labels != i) for i in large], axis=0)
    return [scan & (nearest == k) for k in range(len(large))]


def local_start(part, cand, params, ratios=np.linspace(0.6, 1.5, 19), search=90):
    """Where one figure of the scan lies in the candidate, allowing it a
    size of its own: (scale, turn, dx, dy), by correlation over `ratios` of
    the whole scan's scale and `search` px either way."""
    ys, xs = np.nonzero(part)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    template = soft(part[y0:y1, x0:x1], 3)
    centre = to_candidate(np.array([[(x0 + x1) / 2, (y0 + y1) / 2]]), params)[0]
    best = None
    for ratio in ratios:
        scale = params[0] * ratio
        size = (round(cand.shape[1] * scale), round(cand.shape[0] * scale))
        resized = np.asarray(Image.fromarray(cand.astype(np.float32)).resize(size, Image.BILINEAR))
        left = int(centre[0] * scale - (x1 - x0) / 2) - search
        top = int(centre[1] * scale - (y1 - y0) / 2) - search
        window = np.zeros((y1 - y0 + 2 * search, x1 - x0 + 2 * search), np.float32)
        a, b = max(top, 0), max(left, 0)
        piece = resized[a:top + window.shape[0], b:left + window.shape[1]]
        window[a - top:a - top + piece.shape[0], b - left:b - left + piece.shape[1]] = piece
        score = match_template(ndimage.gaussian_filter(window, 3), template)
        y, x = np.unravel_index(np.argmax(score), score.shape)
        if best is None or score[y, x] > best[0]:
            best = (score[y, x], np.array([scale, params[1], x0 - (left + x), y0 - (top + y)], dtype=np.float64))
    return best[1]


def fit_figures(scan, cand, params):
    """[(mask, params)]: each figure of the scan with its own fit. The model
    draws each figure at its own size (Calvin a third too big beside Dad,
    say), so one fit for all of them leaves the smaller ones out of place.
    A figure keeps the whole scan's fit unless its own covers it better."""
    parts = figures(scan)
    if len(parts) == 1:
        return [(scan, np.array(params))]
    distance = ndimage.distance_transform_edt(~cand).astype(np.float32)

    def miss(part, p):
        ys, xs = np.nonzero(part)
        points = np.stack([xs, ys], 1).astype(np.float64)
        return np.minimum(sample(distance, to_candidate(points, p), CAP) * p[0], CAP).mean()

    fits = []
    for part in parts:
        own, _ = refine(part, cand, local_start(part, cand, params), near=40, prior=0.05)
        fits.append((part, own if miss(part, own) < miss(part, params) else np.array(params)))
    return fits


def between(fits, params, shape, frame):
    """A field over the frame that takes the candidate, placed by the
    whole-scan fit, to where each figure's own fit puts it: every point
    follows the figures in proportion to how near it is to their ink."""
    rows, cols = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float64)
    where = np.stack([cols.ravel() - frame.left, rows.ravel()], 1)
    total = np.zeros(shape)
    field = np.zeros((2,) + shape)
    for mask, own in fits:
        there = to_scan(to_candidate(where, own), params) - where
        inked = np.zeros(shape, bool)
        inked[:mask.shape[0], frame.left:frame.left + mask.shape[1]] = mask
        weight = 1.0 / (ndimage.distance_transform_edt(~inked) + 8.0) ** 2
        field[0] += weight * there[:, 1].reshape(shape)
        field[1] += weight * there[:, 0].reshape(shape)
        total += weight
    return (field / total).astype(np.float32)


# --- 2. non-rigid agreement inside the crop ---------------------------------

def flow(scan, placed, frame):
    """A field f over the frame with placed(x + f(x)) ≈ scan(x) inside the
    crop: measured near the scan's ink, spread smoothly over the crop, and
    faded out beyond it so limbs far from the crop are not dragged about."""
    h, w = scan.shape
    crop = (slice(0, h), slice(frame.left, frame.left + w))
    v, u = optical_flow_tvl1(soft(scan, 2.0), soft(placed[crop] > 0.5, 2.0),
                             attachment=20, tightness=0.3, num_warp=8, num_iter=15)
    near = ndimage.distance_transform_edt(~scan) < 30
    weight = np.zeros(placed.shape, np.float32)
    field = np.zeros((2,) + placed.shape, np.float32)
    weight[crop] = near
    for i, part in enumerate((v, u)):
        field[i][crop] = ndimage.gaussian_filter(part, 4) * near
    sigma = 45
    spread = np.stack([ndimage.gaussian_filter(f, sigma) for f in field])
    spread /= np.maximum(ndimage.gaussian_filter(weight, sigma), 1e-4)
    inside = np.zeros(placed.shape, bool)
    inside[crop] = True
    fade = np.exp(-ndimage.distance_transform_edt(~inside) / 200.0)
    return spread * fade


def warp(image, field):
    rows, cols = np.mgrid[0:image.shape[0], 0:image.shape[1]].astype(np.float32)
    return ndimage.map_coordinates(image, [rows + field[0], cols + field[1]], order=1,
                                   mode='constant', cval=0.0)


# --- 3. lines meet at the crop's edge ---------------------------------------

SOLID = 20  # an ink run this long (scan px) along the crop's edge is a solid black, not a line


def edges(line):
    """(position, polarity, solid) of each ink edge along a 1-D boolean
    profile: `solid` if the ink it bounds is a solid black. Ink that runs
    off either end of the profile counts as solid: there is no telling how
    far it goes, and at a corner of the crop it is usually a black mass."""
    step = np.diff(line.astype(np.int8))
    places = np.flatnonzero(step)
    found = []
    for k, i in enumerate(places):
        if step[i] > 0:   # ink starts: it runs to the next edge, or off the end
            solid = k + 1 == len(places) or places[k + 1] - i >= SOLID
        else:             # ink ends: it began at the previous edge, or before the start
            solid = k == 0 or i - places[k - 1] >= SOLID
        found.append((i + 0.5, int(step[i]), bool(solid)))
    return found


def match_edges(scan_line, cand_line, reach, solid_reach=110):
    """Pairs (position, shift) taking the candidate's ink edges to the
    scan's along one side of the crop, and how many of each were left
    unmatched. Matches are mutual nearest neighbours of the same polarity.
    The edges of solid blacks are matched first and may be far apart: a
    black the candidate draws too large would otherwise be cut off flat by
    the crop. Then any match that would fold the drawing over is dropped,
    lines before solids."""
    ours, theirs = edges(scan_line), edges(cand_line)
    pairs = []  # (position, shift, solid)
    taken_a, taken_b = set(), set()
    for solid, limit in ((True, solid_reach), (False, reach)):
        for polarity in (1, -1):
            a = [(i, p) for i, (p, s, big) in enumerate(ours)
                 if s == polarity and i not in taken_a and (big or not solid)]
            b = [(j, p) for j, (p, s, big) in enumerate(theirs)
                 if s == polarity and j not in taken_b and (big or not solid)]
            if not a or not b:
                continue
            gaps = np.abs(np.array([p for _, p in a])[:, None] - np.array([p for _, p in b])[None, :])
            for row, col in enumerate(gaps.argmin(1)):
                if gaps[row, col] <= limit and gaps[:, col].argmin() == row:
                    pairs.append((a[row][1], b[col][1] - a[row][1], solid))
                    taken_a.add(a[row][0])
                    taken_b.add(b[col][0])
    pairs.sort()
    folded = True
    while folded:
        folded = False
        for first, second in zip(pairs, pairs[1:]):
            if abs(second[1] - first[1]) > 0.6 * (second[0] - first[0]) + 1.0:
                if first[2] != second[2]:
                    drop = second if first[2] else first
                else:
                    drop = first if abs(first[1]) > abs(second[1]) else second
                pairs.remove(drop)
                folded = True
                break
    return [(p, d) for p, d, _ in pairs], len(ours) - len(pairs), len(theirs) - len(pairs)


def shift_profile(pairs, length, tail=40):
    """The shift at every position along a side: through the matched edges,
    easing to nothing beyond the outermost and inside long gaps, over
    `tail` px or twice the shift if that is more (so nothing folds)."""
    if not pairs:
        return np.zeros(length, np.float32)

    def ease(shift):
        return max(tail, 2 * abs(shift))

    xs, ds = [pairs[0][0] - ease(pairs[0][1])], [0.0]
    for (p0, d0), (p1, d1) in zip(pairs, pairs[1:] + [(None, None)]):
        xs.append(p0)
        ds.append(d0)
        if p1 is not None and p1 - p0 > ease(d0) + ease(d1):
            xs += [p0 + ease(d0), p1 - ease(d1)]
            ds += [0.0, 0.0]
    xs.append(pairs[-1][0] + ease(pairs[-1][1]))
    ds.append(0.0)
    profile = np.interp(np.arange(length), xs, ds)
    return ndimage.gaussian_filter1d(profile, 2.0).astype(np.float32)


def sides(scan, cand, frame):
    """For each side of the crop the candidate continues past: the scan's
    profile just inside it and the candidate's on the same line."""
    h, w = scan.shape
    left = frame.left
    inner = cand[:h, left:left + w]
    found = []
    if frame.below:
        found.append(('bottom', scan[h - 2], inner[h - 2]))
    if frame.left:
        found.append(('left', scan[:, 1], inner[:, 1]))
    if frame.right:
        found.append(('right', scan[:, w - 2], inner[:, w - 2]))
    return found


def snap(scan, warped, frame, reach=14, depth=50.0, solid_reach=110):
    """A field that slides the candidate along each side of the crop so its
    lines cross where the scan's do, dying away with distance from the
    side. Returns (field, matched, scan edges unmatched, candidate edges
    unmatched)."""
    h, w = scan.shape
    left = frame.left
    field = np.zeros((2,) + warped.shape, np.float32)
    counts = np.zeros(3, int)
    rows, cols = np.mgrid[0:warped.shape[0], 0:warped.shape[1]]
    for side, scan_line, cand_line in sides(scan, warped > 0.5, frame):
        pairs, lost, extra = match_edges(scan_line, cand_line, reach, solid_reach)
        counts += (len(pairs), lost, extra)
        profile = shift_profile(pairs, len(scan_line))
        deep = np.maximum(depth, 2 * np.abs(profile))  # a long slide dies away slowly
        if side == 'bottom':
            along = np.clip(cols - left, 0, w - 1)
            away = np.abs(rows - h) + np.maximum(left - cols, 0) + np.maximum(cols - left - w, 0)
            field[1] += profile[along] * np.exp(-away / deep[along])
        else:
            edge = left if side == 'left' else left + w
            along = np.clip(rows, 0, h - 1)
            away = np.abs(cols - edge) + np.maximum(rows - h, 0)
            field[0] += profile[along] * np.exp(-away / deep[along])
    return field, int(counts[0]), int(counts[1]), int(counts[2])


def runs(line, least):
    """[(start, end)] of the stretches of a 1-D boolean profile at least
    `least` long."""
    step = np.diff(np.concatenate([[0], line.astype(np.int8), [0]]))
    return [(a, b) for a, b in zip(np.flatnonzero(step > 0), np.flatnonzero(step < 0)) if b - a >= least]


def push_out(scan, warped, frame, weight, least=24, ease=12, depth=40.0):
    """A field that moves clear of the crop any line the candidate draws
    *along* its edge, where the scan has only paper: pasting the scan back
    would slice such a line lengthways (a sleeve hem drawn down the crop's
    side, say). It is slid outward until it stands whole just outside,
    easing to nothing at the ends of the stretch, where real lines cross."""
    h, w = scan.shape
    left = frame.left
    cand = warped > 0.5
    field = np.zeros((2,) + warped.shape, np.float32)
    rows, cols = np.mgrid[0:warped.shape[0], 0:warped.shape[1]]
    # per side: the scan along its edge, and the candidate going outward
    # and inward from that edge
    found = []
    inner = cand[:h, left:left + w]
    if frame.left:
        found.append((scan[:, :3].any(1), cand[:h, left - 40:left][:, ::-1], inner[:, :40], 'left'))
    if frame.right:
        found.append((scan[:, -3:].any(1), cand[:h, left + w:left + w + 40], inner[:, -40:][:, ::-1], 'right'))
    if frame.below:
        found.append((scan[-3:].any(0), cand[h:h + 40, left:left + w].T, inner[-40:][::-1].T, 'below'))

    def reach(profile):
        """How far the ink runs from the edge, along the stretch (median)."""
        return float(np.median(np.where(profile.all(1), profile.shape[1], profile.argmin(1))))

    for paper, outward, inward, side in found:
        paper = ~ndimage.binary_dilation(paper, iterations=2)
        for a, b in runs(outward[:, 0] & paper, least):
            showing, hidden = reach(outward[a:b]), reach(inward[a:b])
            if showing + hidden > 2.2 * weight:
                continue  # a solid black, not a line
            shift = hidden + max(3.0, weight / 2)  # what the crop hides of it, and some air
            along = np.arange(len(paper))
            taper = np.clip(np.minimum(along - a, b - along) / ease, 0, 1)
            if side == 'below':
                away = np.maximum(rows - h, 0)
                field[0] -= shift * taper[np.clip(cols - left, 0, w - 1)] * np.exp(-away / depth) * (rows >= h - 1)
            else:
                edge = left if side == 'left' else left + w
                away = np.abs(cols - edge)
                outside = cols < edge if side == 'left' else cols >= edge
                sign = 1 if side == 'left' else -1
                field[1] += sign * shift * taper[np.clip(rows, 0, h - 1)] * np.exp(-away / depth) * outside * (rows < h)
    return field


# --- 4. the scan's ink ------------------------------------------------------

def line_weight(ink):
    """Typical width of the thin lines of a drawing (the mean of the middle
    half of the widths along their centre lines); solid blacks don't count."""
    widths = 2 * ndimage.distance_transform_edt(ink)[skeletonize(ink)]
    widths = np.sort(widths[(widths > 1) & (widths < 20)])
    if not len(widths):
        return 0.0
    return float(widths[len(widths) // 4:max(len(widths) * 3 // 4, len(widths) // 4 + 1)].mean())


def reink(coverage, target, where):
    """Coverage at twice the scan's size → 1-bit ink on the scan's grid, its
    lines thinned or thickened until those in `where` weigh `target`."""
    ink = coverage > 0.5
    signed = ndimage.distance_transform_edt(~ink) - ndimage.distance_transform_edt(ink)
    h, w = ink.shape

    def cut(offset):
        return (signed < offset).reshape(h // 2, 2, w // 2, 2).mean((1, 3)) >= 0.5

    low, high = -8.0, 8.0  # export px per side
    for _ in range(7):
        middle = (low + high) / 2
        if line_weight(cut(middle) & where) > target:
            high = middle
        else:
            low = middle
    return cut((low + high) / 2)


# --- the whole thing --------------------------------------------------------

@dataclass
class Report:
    scale: float
    theta: float
    tx: float
    ty: float
    fit_rigid: float      # mean chamfer distance inside the crop, scan px
    fit_warped: float
    edges_matched: int
    edges_lost: int       # scan lines that reach the crop's edge and stop
    edges_extra: int      # candidate lines that start at the crop's edge
    weight_scan: float
    weight_before: float
    weight_after: float
    seam: int             # export px along the crop's edge where ink meets paper
    clipped: bool         # the candidate's own frame cuts through its drawing

    def as_dict(self):
        return asdict(self)


def chamfer(a, b):
    if not a.any() or not b.any():
        return CAP
    return float(capped_distance(b)[a].mean() + capped_distance(a)[b].mean()) / 2


def cut_along(scan, cand, frame):
    """How much of the crop's edge would have the scan's ink on one side
    and the candidate's paper on the other, or the reverse (scan px)."""
    h, w = scan.shape
    left = frame.left
    total = 0
    if frame.below:
        total += int((scan[h - 2] != cand[h + 1, left:left + w]).sum())
    if frame.left:
        total += int((scan[:, 1] != cand[:h, left - 2]).sum())
    if frame.right:
        total += int((scan[:, w - 2] != cand[:h, left + w + 1]).sum())
    return total


def seam_mismatch(panel, size, x0, frame, apart=3):
    """How much of the crop's edge has ink on one side and paper on the
    other, in export px. Lines crossing it squarely add almost nothing; a
    black cut off flat along it adds its whole length."""
    ink = np.asarray(panel) < 128
    w, h = size
    total = 0
    if frame.below:
        total += int((ink[h - apart, x0:x0 + w] != ink[h + apart, x0:x0 + w]).sum())
    if frame.left:
        total += int((ink[:h, x0 + apart] != ink[:h, x0 - apart]).sum())
    if frame.right:
        total += int((ink[:h, x0 + w - apart] != ink[:h, x0 + w + apart]).sum())
    return total


def graft(scan_image, cand_image, frame, scales=None):
    """(panel, report): the export-size panel with the scan pasted at
    (2 * frame.left, 0), and how well the candidate fitted."""
    if scales is None:
        scales = np.linspace(0.6, 2.4, 37)
    scan_image = scan_image.convert('L')
    scan = to_ink(scan_image.resize((scan_image.width // 2, scan_image.height // 2), Image.LANCZOS))
    cand = to_ink(cand_image, 140)
    h, w = scan.shape

    params, _ = register(scan[frame.skip:], cand, scales)
    params[3] += frame.skip
    shape = (h + frame.below, w + frame.left + frame.right)
    origin = (-frame.left, 0)
    crop = (slice(0, h), slice(frame.left, frame.left + w))
    placed = place(cand, params, shape, origin)
    fit_rigid = chamfer(scan, placed[crop] > 0.5)

    field = between(fit_figures(scan, cand, params), params, shape, frame)
    field += flow(scan, warp(placed, field), frame)

    def snapped(solid_reach):
        """The field with the crop's edges snapped, and what it achieves."""
        result = field.copy()
        for _ in range(3):
            result += snap(scan, warp(placed, result), frame, solid_reach=solid_reach)[0]
        warped = warp(placed, result)
        fit = chamfer(scan, warped[crop] > 0.5)
        return result, warped, fit, cut_along(scan, warped > 0.5, frame)

    # Sliding solid blacks a long way mends a black cut off flat by the
    # crop, but a wrong match tears the drawing: keep it only if it leaves
    # less of a cut and the fit inside the crop no worse.
    field, warped, fit_warped, cut = snapped(14)
    far = snapped(110)
    if far[3] < cut and far[2] <= fit_warped + 0.15:
        field, warped, fit_warped, cut = far
    outside = np.ones(shape, bool)
    outside[crop] = False
    field = field + push_out(scan, warped, frame, line_weight((warped > 0.5) & outside))
    warped = warp(placed, field)
    _, matched, lost, extra = snap(scan, warped, frame)

    # again at twice the size, where the ink is finally cut
    big_shape = (shape[0] * 2, shape[1] * 2)
    big_field = np.stack([
        np.asarray(Image.fromarray(f).resize(big_shape[::-1], Image.BILINEAR)) * 2 for f in field])
    coverage = ndimage.gaussian_filter(warp(place(cand, params, big_shape, origin, zoom=2), big_field), 1.0)

    weight_scan = line_weight(scan)
    before = line_weight((warped > 0.5) & outside)
    ink = reink(coverage, weight_scan, outside)
    after = line_weight(ink & outside)

    panel = np.asarray(build_assets.smooth(ink)).copy()
    x0 = frame.left * 2
    panel[:scan_image.height, x0:x0 + scan_image.width] = np.asarray(scan_image)

    seam = seam_mismatch(panel, scan_image.size, x0, frame)
    border = np.concatenate([cand[0], cand[-1], cand[:, 0], cand[:, -1]])
    report = Report(float(params[0]), float(params[1]), float(params[2]), float(params[3]),
                    fit_rigid, fit_warped, matched, lost, extra,
                    weight_scan, before, after, seam, bool(border.mean() > 0.002))
    return Image.fromarray(panel), report
