// Speech balloon geometry: an outline around a block of laid-out text, and
// a tail from it towards whoever is speaking, drawn the way Watterson draws
// them (see docs/balloon-study.md). Pure functions, so they can be tested
// without a browser.

// The outline of a speech balloon around `lines` (boxes with x, y, width,
// height), as a closed polygon of [x, y] points: an oval round a short
// remark standing on its own, and otherwise a smooth outline following the
// text, sweeping in under shorter lines wherever that keeps clear of the
// artwork, with no corners. isFree([x, y]) says whether a point is clear of
// the artwork.
//
// If `panel` ({x0, y0, x1, y1, reach}) is given, a balloon whose padded text
// comes within `reach` of one of the panel's edges runs out past that edge,
// so that once the panel is clipped it hangs from the border.
export function balloonOutline(
  lines,
  { padX, padY, radius, isFree, ovalLines = 1, panel = null, bow = 0.03, roundness = 0 },
) {
  if (!lines.length) return null;
  const boxes = lines.map((l) => ({
    top: l.y - padY,
    bottom: l.y + l.height + padY,
    left: l.x - padX,
    right: l.x + l.width + padX,
  }));
  const attached = panel ? attachToEdges(boxes, panel, radius) : false;
  if (!attached && lines.length <= ovalLines) {
    const oval = ovalAround(lines, padX, padY);
    if (oval.every(isFree) && ovalAround(lines, padX * 0.6, padY * 0.6).every(isFree)) {
      return oval;
    }
  }
  fillAboveWidest(boxes, isFree);
  const corners = [
    ...hull(envelope(boxes, 1), 1, isFree),
    ...hull(envelope(boxes, -1), -1, isFree).reverse(),
  ];
  // Smaller balloons are rounder: corners are rounded over at least
  // `roundness` of the text block's shorter side. But a circular corner
  // cuts (sqrt 2 - 1) of its radius off the corner, which mustn't reach the
  // text, so no more than the padding allows.
  const textWidth = Math.max(...lines.map((l) => l.x + l.width)) - Math.min(...lines.map((l) => l.x));
  const textHeight = Math.max(...lines.map((l) => l.y + l.height)) - Math.min(...lines.map((l) => l.y));
  const roundest = (0.8 * Math.hypot(padX, padY)) / (Math.SQRT2 - 1);
  const rounding = Math.min(roundest, Math.max(radius, roundness * Math.min(textWidth, textHeight)));
  const { polygon, sweeps } = mergeSweeps(simplify(corners), isFree);
  return smooth(polygon, rounding, isFree, bow, sweeps);
}

// Push out past the panel's edges any box sides that come within reach of
// them. Returns whether any did.
function attachToEdges(boxes, panel, radius) {
  const beyond = 4 * radius;
  let attached = false;
  for (const b of boxes) {
    if (b.top - panel.y0 < panel.reach) {
      b.top = panel.y0 - beyond;
      attached = true;
    }
    if (panel.y1 - b.bottom < panel.reach) {
      b.bottom = panel.y1 + beyond;
      attached = true;
    }
    if (b.left - panel.x0 < panel.reach) {
      b.left = panel.x0 - beyond;
      attached = true;
    }
    if (panel.x1 - b.right < panel.reach) {
      b.right = panel.x1 + beyond;
      attached = true;
    }
  }
  return attached;
}

// Like Watterson's, the balloon's sides come straight down to its widest
// line, and only sweep in under shorter lines below that: widen each line's
// box to the widest of the lines below it, unless that would cover art.
function fillAboveWidest(boxes, isFree) {
  let right = -Infinity;
  let left = Infinity;
  for (let i = boxes.length - 1; i >= 0; i--) {
    const b = boxes[i];
    right = Math.max(right, b.right);
    left = Math.min(left, b.left);
    if (rectangleClear(b.right, b.top, right, b.bottom, isFree)) b.right = right;
    if (rectangleClear(left, b.top, b.left, b.bottom, isFree)) b.left = left;
  }
}

// Whether the rectangle x0..x1, y0..y1 is clear of the artwork.
function rectangleClear(x0, y0, x1, y1, isFree) {
  if (x1 <= x0) return true;
  for (let x = x0; x <= x1; x += 2) {
    for (let y = y0; y <= y1; y += 2) {
      if (!isFree([x, y])) return false;
    }
  }
  return isFree([x1, y1]);
}

// The outer edge of the padded line boxes on one side (1 for right, -1 for
// left), as a staircase of points from top to bottom.
function envelope(boxes, side) {
  const ys = [...new Set(boxes.flatMap((b) => [b.top, b.bottom]))].sort((a, b) => a - b);
  const points = [];
  for (let k = 0; k < ys.length - 1; k++) {
    const mid = (ys[k] + ys[k + 1]) / 2;
    const covering = boxes.filter((b) => b.top <= mid && b.bottom >= mid);
    // Gaps between paragraphs are bridged by the hull.
    if (!covering.length) continue;
    const edge = side > 0
      ? Math.max(...covering.map((b) => b.right))
      : Math.min(...covering.map((b) => b.left));
    points.push([edge, ys[k]], [edge, ys[k + 1]]);
  }
  return points;
}

// One side of the balloon, from top to bottom: drop any corner that a
// straight edge can cut across without crossing the artwork. `side` is 1 for
// the right-hand side and -1 for the left.
function hull(points, side, isFree) {
  const stack = [];
  for (const c of points) {
    while (stack.length >= 2) {
      const a = stack[stack.length - 2];
      const b = stack[stack.length - 1];
      const across =
        c[1] - a[1] < 1e-9
          ? side > 0
            ? Math.max(a[0], c[0])
            : Math.min(a[0], c[0])
          : a[0] + ((c[0] - a[0]) * (b[1] - a[1])) / (c[1] - a[1]);
      const inward = side * (b[0] - across) <= 1e-9;
      if (!inward || !triangleClear(a, b, c, isFree)) break;
      stack.pop();
    }
    stack.push(c);
  }
  return stack;
}

// Whether the triangle a, b, c (the area a shortcut from a to c would add)
// is clear of the artwork.
function triangleClear(a, b, c, isFree) {
  const size = Math.max(
    Math.hypot(c[0] - a[0], c[1] - a[1]),
    Math.hypot(b[0] - a[0], b[1] - a[1]),
    Math.hypot(c[0] - b[0], c[1] - b[1]),
  );
  const steps = Math.max(2, Math.ceil(size / 2));
  for (let i = 0; i <= steps; i++) {
    for (let j = 0; j <= steps - i; j++) {
      const u = i / steps;
      const v = j / steps;
      const w = 1 - u - v;
      const p = [a[0] * w + b[0] * u + c[0] * v, a[1] * w + b[1] * u + c[1] * v];
      if (!isFree(p)) return false;
    }
  }
  return true;
}

// Drop repeated points and points in the middle of straight runs.
function simplify(points) {
  const same = (a, b) => Math.abs(a[0] - b[0]) < 1e-9 && Math.abs(a[1] - b[1]) < 1e-9;
  const distinct = points.filter((v, i) => !same(v, points[(i + 1) % points.length]));
  const n = distinct.length;
  return distinct.filter((v, i) => {
    const p = distinct[(i - 1 + n) % n];
    const q = distinct[(i + 1) % n];
    const cross = (v[0] - p[0]) * (q[1] - v[1]) - (v[1] - p[1]) * (q[0] - v[0]);
    return Math.abs(cross) > 1e-9;
  });
}

// Turn the corners of the outline into a smooth curve, the way Watterson
// draws balloons. Every corner becomes a circular arc over about `radius`,
// or over half of a slanting edge (where the balloon sweeps in under
// shorter lines), so that a run of steps becomes one continuous curve.
// What's left of each edge bows gently outwards, by `bow` of its length (no
// pen line of his is ruler-straight), but never so much that it turns back
// against the corners either side of it, and never onto the artwork.
// Finally the joins are smoothed by cutting corners off (Chaikin's
// algorithm).
// Where the outline sweeps in under shorter lines it goes down a run of
// slanting edges. Rounding each of their corners separately makes a curve
// that bends, straightens and bends again; Watterson draws the sweep as one
// curve. So replace each such run, where the art allows, by the single
// corner where the edges either side of it would meet if carried on; that
// corner is then rounded right round (see smooth). Returns the new polygon
// and, for each such corner's index, the corners it replaced, which the
// rounding must keep inside the balloon.
function mergeSweeps(points, isFree) {
  const n = points.length;
  const slanted = (a, b) => Math.abs(a[0] - b[0]) > 1e-6 && Math.abs(a[1] - b[1]) > 1e-6;
  const sweeps = new Map();
  // Start just after a corner, so that no run wraps round the end.
  const start = points.findIndex((v, i) => !slanted(points[(i - 1 + n) % n], v));
  if (start < 0) return { polygon: points, sweeps };
  const at = (i) => points[(start + i) % n];
  const out = [];
  let i = 0;
  while (i < n) {
    if (!slanted(at(i), at(i + 1))) {
      out.push(at(i));
      i++;
      continue;
    }
    let j = i;
    while (j < n && slanted(at(j), at(j + 1))) j++;
    const run = [];
    for (let k = i; k <= j; k++) run.push(at(k));
    const corner = meeting(at(i - 1 + n), run[0], run[run.length - 1], at(j + 1));
    const clear =
      corner && run.every((a, k) => k === 0 || triangleClear(run[k - 1], a, corner, isFree));
    if (clear) {
      sweeps.set(out.length, run);
      out.push(corner);
    } else {
      out.push(...run);
    }
    i = j + 1;
  }
  return { polygon: out, sweeps };
}

// Where the line through `before` and u, carried on past u, meets the line
// through w and `after`, carried back past w; null if they don't.
function meeting(before, u, w, after) {
  const d1 = [u[0] - before[0], u[1] - before[1]];
  const d2 = [after[0] - w[0], after[1] - w[1]];
  // Solve u + s d1 = w - t d2, that is s d1 + t d2 = w - u.
  const det = d1[0] * d2[1] - d1[1] * d2[0];
  if (Math.abs(det) < 1e-9) return null;
  const rx = w[0] - u[0];
  const ry = w[1] - u[1];
  const s = (rx * d2[1] - ry * d2[0]) / det;
  const t = (d1[0] * ry - d1[1] * rx) / det;
  if (s <= 0 || t <= 0) return null;
  return [u[0] + d1[0] * s, u[1] + d1[1] * s];
}

function smooth(polygon, radius, isFree, bow, sweeps = new Map()) {
  const n = polygon.length;
  const outward = outwardSign(polygon);
  const slanted = (a, b) => Math.abs(a[0] - b[0]) > 1e-6 && Math.abs(a[1] - b[1]) > 1e-6;
  const corners = polygon.map((v, i) => {
    const p = polygon[(i - 1 + n) % n];
    const q = polygon[(i + 1) % n];
    const lp = Math.hypot(p[0] - v[0], p[1] - v[1]);
    const lq = Math.hypot(q[0] - v[0], q[1] - v[1]);
    const turn = turnAngle(p, v, q);
    const at = (rp, rq) => ({
      v,
      turn,
      before: lp ? [v[0] + ((p[0] - v[0]) / lp) * rp, v[1] + ((p[1] - v[1]) / lp) * rp] : v,
      after: lq ? [v[0] + ((q[0] - v[0]) / lq) * rq, v[1] + ((q[1] - v[1]) / lq) * rq] : v,
    });
    if (sweeps.has(i)) {
      // A sweep: drawn below as one curve from where it starts to where it
      // ends.
      const run = sweeps.get(i);
      return { v, turn, before: run[0], after: run[run.length - 1], run };
    }
    const rp = slanted(p, v) ? lp / 2 : Math.min(radius, lp / 2);
    const rq = slanted(v, q) ? lq / 2 : Math.min(radius, lq / 2);
    return at(rp, rq);
  });
  // Each edge between roundings, bowed out a little.
  const edges = corners.map((corner, i) => {
    const next = corners[(i + 1) % n];
    const a = corner.after;
    const b = next.before;
    const length = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const along = polygon[(i + 1) % n];
    const v = corner.v;
    const span = Math.hypot(along[0] - v[0], along[1] - v[1]);
    const direction = [(along[0] - v[0]) / span, (along[1] - v[1]) / span];
    if (length < 1e-6) return { a, b, control: a, start: direction, end: direction };
    const normal = [((b[1] - a[1]) / length) * outward, (-(b[0] - a[0]) / length) * outward];
    // A quadratic bowing by h leaves its ends at atan(4h / length) to the
    // straight line; keep that to half the turn at the corner either side,
    // so the outline stays convex there.
    const tilt = Math.min(Math.abs(corner.turn), Math.abs(next.turn)) / 2;
    const amount = Math.min(bow * length, radius / 2, (length * Math.tan(tilt)) / 4);
    const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    let control = mid;
    for (const share of [1, 0.5, 0.25]) {
      const c = [mid[0] + normal[0] * amount * 2 * share, mid[1] + normal[1] * amount * 2 * share];
      if (triangleClear(a, c, b, isFree)) {
        control = c;
        break;
      }
    }
    const unit = (from, to) => {
      const d = Math.hypot(to[0] - from[0], to[1] - from[1]);
      return [(to[0] - from[0]) / d, (to[1] - from[1]) / d];
    };
    return { a, b, control, start: unit(a, control), end: unit(control, b) };
  });
  const out = [];
  for (let i = 0; i < n; i++) {
    const { v, before, after, run } = corners[i];
    if (run) {
      out.push(...sweepCurve(v, run, edges[(i - 1 + n) % n].end, edges[i].start, isFree));
    } else {
      // Round the corner with an arc that leaves the incoming edge, and
      // joins the outgoing one, along their own directions.
      const into = edges[(i - 1 + n) % n].end;
      const outOf = edges[i].start;
      const turn = Math.abs(Math.atan2(into[0] * outOf[1] - into[1] * outOf[0], into[0] * outOf[0] + into[1] * outOf[1]));
      // A circular arc's control points sit this far along its tangents.
      const k = turn < 1e-6 ? 0 : (4 / 3) * Math.tan(turn / 4) / Math.tan(turn / 2);
      const rIn = Math.hypot(v[0] - before[0], v[1] - before[1]);
      const rOut = Math.hypot(v[0] - after[0], v[1] - after[1]);
      const c1 = [before[0] + into[0] * rIn * k, before[1] + into[1] * rIn * k];
      const c2 = [after[0] - outOf[0] * rOut * k, after[1] - outOf[1] * rOut * k];
      out.push(...cubic(before, c1, c2, after, 12));
    }
    const { a, b, control } = edges[i];
    if (Math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-6) {
      out.push(...quadratic(a, control, b, 16).slice(1, -1));
    }
  }
  // Where two roundings meet, one curve starts where the last ended.
  let points = out.filter((p, i) => {
    const q = out[(i + 1) % out.length];
    return Math.hypot(q[0] - p[0], q[1] - p[1]) > 1e-6;
  });
  for (let round = 0; round < 2; round++) {
    const next = [];
    for (let i = 0; i < points.length; i++) {
      const a = points[i];
      const b = points[(i + 1) % points.length];
      next.push([0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]]);
      next.push([0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]]);
    }
    points = next;
  }
  return points;
}

// How far the direction turns at v, going from p to v to q, in radians.
function turnAngle(p, v, q) {
  let turn = Math.atan2(q[1] - v[1], q[0] - v[0]) - Math.atan2(v[1] - p[1], v[0] - p[0]);
  while (turn > Math.PI) turn -= 2 * Math.PI;
  while (turn < -Math.PI) turn += 2 * Math.PI;
  return turn;
}

// A sweep round corner v from the first point of `run` to the last: one
// curve that leaves the edge before it and joins the edge after it along
// their own directions (`into` and `outOf`), bowing out towards v only as
// far as it must to keep the corners of the lines it sweeps round (the rest
// of `run`) inside the balloon.
function sweepCurve(v, run, into, outOf, isFree) {
  const u = run[0];
  const w = run[run.length - 1];
  const reachU = Math.hypot(v[0] - u[0], v[1] - u[1]);
  const reachW = Math.hypot(v[0] - w[0], v[1] - w[1]);
  let curve = null;
  for (const pull of [0.5, 0.6, 0.7, 0.8, 0.9, 1]) {
    curve = cubic(
      u,
      [u[0] + into[0] * reachU * pull, u[1] + into[1] * reachU * pull],
      [w[0] - outOf[0] * reachW * pull, w[1] - outOf[1] * reachW * pull],
      w,
      32,
    );
    const cut = [...curve, v];
    const keeps = run.every((point) => !inside(cut, point) || nearCurve(curve, point, 1.5));
    if (keeps && curve.every(isFree)) break;
  }
  return curve;
}

function nearCurve(curve, point, distance) {
  return curve.some(([x, y]) => Math.hypot(x - point[0], y - point[1]) <= distance);
}

// Points along the quadratic curve from a to b with control point c.
function quadratic(a, c, b, steps) {
  const points = [];
  for (let k = 0; k <= steps; k++) {
    const t = k / steps;
    const s = 1 - t;
    points.push([
      s * s * a[0] + 2 * s * t * c[0] + t * t * b[0],
      s * s * a[1] + 2 * s * t * c[1] + t * t * b[1],
    ]);
  }
  return points;
}

// Points along the cubic curve from a to b with control points c1 and c2.
function cubic(a, c1, c2, b, steps) {
  const points = [];
  for (let k = 0; k <= steps; k++) {
    const t = k / steps;
    const s = 1 - t;
    points.push([
      s * s * s * a[0] + 3 * s * s * t * c1[0] + 3 * s * t * t * c2[0] + t * t * t * b[0],
      s * s * s * a[1] + 3 * s * s * t * c1[1] + 3 * s * t * t * c2[1] + t * t * t * b[1],
    ]);
  }
  return points;
}

// 1 if an edge's left-hand normal, (dy, -dx), points out of the polygon,
// -1 if it points in.
function outwardSign(polygon) {
  let area = 0;
  for (let i = 0; i < polygon.length; i++) {
    const [ax, ay] = polygon[i];
    const [bx, by] = polygon[(i + 1) % polygon.length];
    area += ax * by - bx * ay;
  }
  return area > 0 ? 1 : -1;
}

function ovalAround(lines, padX, padY) {
  const x0 = Math.min(...lines.map((l) => l.x));
  const y0 = Math.min(...lines.map((l) => l.y));
  const x1 = Math.max(...lines.map((l) => l.x + l.width));
  const y1 = Math.max(...lines.map((l) => l.y + l.height));
  const cx = (x0 + x1) / 2;
  const cy = (y0 + y1) / 2;
  const hx = (x1 - x0) / 2;
  const hy = (y1 - y0) / 2;
  // Tall enough to leave room above and below the text, then just wide
  // enough for the ellipse to clear the text's corners.
  const b = hy * 1.45 + padY;
  const a = hx / Math.sqrt(1 - (hy / b) ** 2) + padX * 0.5;
  const points = [];
  const n = 96;
  for (let k = 0; k < n; k++) {
    const t = (2 * Math.PI * k) / n;
    points.push([cx + a * Math.cos(t), cy + b * Math.sin(t)]);
  }
  return points;
}

function inside(polygon, [px, py]) {
  let result = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) {
      result = !result;
    }
  }
  return result;
}

// The point `distance` along the polygon's perimeter from parameter t of
// edge k (backwards if distance is negative).
function walk(polygon, k, t, distance) {
  const n = polygon.length;
  const edge = (e) => {
    const a = polygon[((e % n) + n) % n];
    const b = polygon[(((e + 1) % n) + n) % n];
    return [a, b, Math.hypot(b[0] - a[0], b[1] - a[1])];
  };
  let [a, b, length] = edge(k);
  let position = t * length;
  let remaining = distance;
  let e = k;
  for (let guard = 0; guard < 4 * n; guard++) {
    if (remaining >= 0 && position + remaining <= length) {
      position += remaining;
      break;
    }
    if (remaining < 0 && position + remaining >= 0) {
      position += remaining;
      break;
    }
    if (remaining >= 0) {
      remaining -= length - position;
      e += 1;
      [a, b, length] = edge(e);
      position = 0;
    } else {
      remaining += position;
      e -= 1;
      [a, b, length] = edge(e);
      position = length;
    }
  }
  const s = length ? position / length : 0;
  return [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s];
}

// A tail for the balloon with outline `polygon`, pointing at `speaker`:
// {base: [p, q], bend, tip} where p and q lie on the outline `width` apart,
// or null if there's no room for one. Its centre line is the curve from the
// middle of the base to the tip with control point `bend`. Like Watterson's
// tails it is usually a straight wedge pointing at the speaker, but where
// that helps it get round something it can instead set off straight out of
// the balloon and curve round towards them; a curved tail counts
// curvePenalty (by default its width) further from the speaker, so it's
// only used when it gets usefully closer.
//
// The tail can leave from anywhere on the outline; it leaves from wherever
// lets its tip get closest to the speaker, so it goes round a head in the
// way rather than stopping at it. Its tip stops `gap` short of the speaker
// and of anywhere isFree([x, y]) is false (the artwork), and it is between
// minLength and maxLength long, unless the balloon is stranded, with no
// art within `reach` of it and so much open space on the way to the
// speaker that it takes a longer tail to end within `reach` of them (or of
// the art in the way, which is usually their head).
// isArtFree(point) says whether a point is clear of the art alone (by
// default, isFree).
// A tail cut short by the art reads as
// pointing at whatever it ran into, and so does one that points at the
// speaker through some of the art (other than the last clearSight of the
// way, round the speaker's mouth itself), so such tails count
// blockedPenalty further from the speaker than they really are.
export function balloonTail(
  polygon,
  speaker,
  {
    width,
    maxLength,
    minLength,
    gap,
    isFree,
    blockedPenalty = 0,
    clearSight = null,
    curvePenalty = width,
    reach = Infinity,
    isArtFree = isFree,
  },
) {
  const step = width / 4;
  const outward = outwardSign(polygon);
  const stranded =
    reach < Infinity && !resampled(polygon, step).some((v) => artWithin(v, reach, 2 * step, isArtFree));
  let best = null;
  // Try starting points every `step` along the outline.
  let along = 0;
  for (let k = 0; k < polygon.length; k++) {
    const a = polygon[k];
    const b = polygon[(k + 1) % polygon.length];
    const edge = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (edge < 1e-9) continue;
    const normal = [((b[1] - a[1]) / edge) * outward, (-(b[0] - a[0]) / edge) * outward];
    for (; along < edge; along += step) {
      const t = along / edge;
      const p = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
      const distance = Math.hypot(speaker[0] - p[0], speaker[1] - p[1]);
      if (distance <= gap) continue;
      const dx = (speaker[0] - p[0]) / distance;
      const dy = (speaker[1] - p[1]) / distance;
      // It has to head out of the balloon, not along or back across it.
      if (dx * normal[0] + dy * normal[1] < 0.2) continue;
      // The longest tail, up to maxLength (or as far as reach needs), whose
      // curve keeps clear of the art and stops short of the speaker.
      let open = 0;
      if (stranded && distance - reach > maxLength) {
        while (open < distance && isFree([p[0] + dx * open, p[1] + dy * open])) open += step;
      }
      const full = Math.min(Math.max(maxLength, open - reach), distance - gap);
      for (const curved of [false, true]) {
        let length = full;
        let shape = null;
        while (length >= minLength) {
          shape = tailShape(p, [dx, dy], length, curved ? normal : null);
          if (curveClear(shape, gap, isFree)) break;
          shape = null;
          length -= step;
        }
        if (!shape) continue;
        // Get as close to the speaker as possible; among tails that get
        // equally close, take the most direct.
        const miss = Math.hypot(speaker[0] - shape.tip[0], speaker[1] - shape.tip[1]);
        const blocked =
          length < full - 1e-9 ||
          (clearSight !== null && !sightClear(shape.tip, speaker, clearSight, isFree))
            ? blockedPenalty
            : 0;
        const score = miss + blocked + (curved ? curvePenalty : 0) + 0.05 * distance;
        if (!best || score < best.score) best = { k, t, ...shape, score };
      }
    }
    // Carry the walk on round the next edge.
    along -= edge;
  }
  if (!best) return null;
  return {
    base: [
      walk(polygon, best.k, best.t, -width / 2),
      walk(polygon, best.k, best.t, width / 2),
    ],
    bend: best.bend,
    tip: best.tip,
  };
}

// The points of a polygon, leaving out any closer than `spacing` to the
// last one kept.
function resampled(polygon, spacing) {
  const out = [polygon[0]];
  for (const p of polygon) {
    const last = out[out.length - 1];
    if (Math.hypot(p[0] - last[0], p[1] - last[1]) >= spacing) out.push(p);
  }
  return out;
}

// Whether there's any art (anywhere isArtFree is false) within `radius` of
// a point, looking every `step`.
function artWithin([px, py], radius, step, isArtFree) {
  for (let r = step; r <= radius; r += step) {
    const n = Math.max(8, Math.ceil((2 * Math.PI * r) / step));
    for (let k = 0; k < n; k++) {
      const a = (2 * Math.PI * k) / n;
      if (!isArtFree([px + r * Math.cos(a), py + r * Math.sin(a)])) return true;
    }
  }
  return false;
}

// A tail `length` long from p, ending up heading along `direction`: straight,
// or if `normal` is given, setting off along it and curving round.
function tailShape(p, direction, length, normal = null) {
  const tip = [p[0] + direction[0] * length, p[1] + direction[1] * length];
  const towards = normal ?? direction;
  const bend = [p[0] + towards[0] * length * 0.5, p[1] + towards[1] * length * 0.5];
  return { tip, bend, start: p };
}

// Whether the straight line from a tail's tip to the speaker is clear of
// the art, apart from the last `slack` of it.
function sightClear(tip, speaker, slack, isFree) {
  const dx = speaker[0] - tip[0];
  const dy = speaker[1] - tip[1];
  const d = Math.hypot(dx, dy);
  for (let s = 1; s < d - slack; s += 1) {
    if (!isFree([tip[0] + (dx / d) * s, tip[1] + (dy / d) * s])) return false;
  }
  return true;
}

// Whether a tail's curve, and a little way beyond its tip, is clear of the
// art.
function curveClear({ start, bend, tip }, gap, isFree) {
  const points = quadratic(start, bend, tip, 24).slice(1);
  const dx = tip[0] - bend[0];
  const dy = tip[1] - bend[1];
  const d = Math.hypot(dx, dy) || 1;
  for (let s = 1; s <= gap; s += 1) points.push([tip[0] + (dx / d) * s, tip[1] + (dy / d) * s]);
  return points.every(isFree);
}

// Whether points are clear of all the `polygons` (other balloons, say):
// outside them and at least `margin` from their edges. Tails ask this of a
// great many points, so it's worked out once on a grid half the margin
// across, and looked up.
export function clearOf(polygons, margin) {
  const cell = Math.max(margin / 2, 0.5);
  const grids = polygons.map((polygon) => {
    const outline = coarsen(polygon, cell);
    const xs = polygon.map((p) => p[0]);
    const ys = polygon.map((p) => p[1]);
    const x0 = Math.min(...xs) - margin;
    const y0 = Math.min(...ys) - margin;
    const w = Math.ceil((Math.max(...xs) + margin - x0) / cell) + 1;
    const h = Math.ceil((Math.max(...ys) + margin - y0) / cell) + 1;
    const blocked = new Uint8Array(w * h);
    for (let j = 0; j < h; j++) {
      for (let i = 0; i < w; i++) {
        const p = [x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell];
        blocked[j * w + i] = inside(outline, p) || distanceTo(outline, p) < margin ? 1 : 0;
      }
    }
    return { x0, y0, w, h, blocked };
  });
  return ([px, py]) =>
    grids.every(({ x0, y0, w, h, blocked }) => {
      const i = Math.floor((px - x0) / cell);
      const j = Math.floor((py - y0) / cell);
      return i < 0 || j < 0 || i >= w || j >= h || !blocked[j * w + i];
    });
}

// The polygon with points closer than `spacing` to the last one dropped.
function coarsen(points, spacing) {
  const out = [points[0]];
  for (const p of points) {
    const last = out[out.length - 1];
    if (Math.hypot(p[0] - last[0], p[1] - last[1]) >= spacing) out.push(p);
  }
  return out;
}

function distanceTo(polygon, [px, py]) {
  let best = Infinity;
  for (let k = 0; k < polygon.length; k++) {
    const [ax, ay] = polygon[k];
    const [bx, by] = polygon[(k + 1) % polygon.length];
    const dx = bx - ax;
    const dy = by - ay;
    const lengthSq = dx * dx + dy * dy;
    const t = lengthSq ? Math.min(1, Math.max(0, ((px - ax) * dx + (py - ay) * dy) / lengthSq)) : 0;
    best = Math.min(best, Math.hypot(px - (ax + dx * t), py - (ay + dy * t)));
  }
  return best;
}
