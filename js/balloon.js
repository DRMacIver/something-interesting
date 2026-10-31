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
  { padX, padY, radius, isFree, ovalLines = 1, panel = null },
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
  return smooth(corners, radius, isFree);
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

// Turn a polygon into a smooth curve, the way Watterson draws balloons.
// Where the outline slants (sweeping in under shorter lines), the slant is
// replaced by a single arc bowing outwards towards where the side and the
// bottom would meet, if that keeps clear of the artwork. Then the remaining corners are rounded over about `radius`, and
// what's left is smoothed by putting points along the edges about `radius`
// apart and repeatedly cutting the corners off (Chaikin's algorithm).
function smooth(polygon, radius, isFree) {
  polygon = roundCorners(sweepArcs(polygon, isFree), radius);
  let points = [];
  const n = polygon.length;
  for (let i = 0; i < n; i++) {
    const a = polygon[i];
    const b = polygon[(i + 1) % n];
    const length = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (length < 1e-9) continue;
    const pieces = Math.max(1, Math.round(length / radius));
    for (let k = 0; k < pieces; k++) {
      const t = k / pieces;
      points.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
    }
  }
  for (let round = 0; round < 4; round++) {
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

function sweepArcs(points, isFree) {
  const n = points.length;
  const slanted = (a, b) => Math.abs(a[0] - b[0]) > 1e-6 && Math.abs(a[1] - b[1]) > 1e-6;
  const out = [];
  for (let i = 0; i < n; i++) {
    const before = points[(i - 1 + n) % n];
    const u = points[i];
    const w = points[(i + 1) % n];
    const after = points[(i + 2) % n];
    out.push(u);
    if (!slanted(u, w)) continue;
    // Where the edge coming into u, carried on, meets the edge leaving w,
    // carried back: the arc's control point.
    const d1 = [u[0] - before[0], u[1] - before[1]];
    const d2 = [after[0] - w[0], after[1] - w[1]];
    // Solve u + s d1 = w - t d2, that is s d1 + t d2 = w - u.
    const det = d1[0] * d2[1] - d1[1] * d2[0];
    if (Math.abs(det) < 1e-9) continue;
    const rx = w[0] - u[0];
    const ry = w[1] - u[1];
    const s = (rx * d2[1] - ry * d2[0]) / det;
    const t = (d1[0] * ry - d1[1] * rx) / det;
    if (s <= 0 || t <= 0) continue;
    // Halfway between that and the straight line: a moderate bow, like the
    // sweep of a pen, rather than filling the corner back in.
    const corner = [u[0] + d1[0] * s, u[1] + d1[1] * s];
    const c = [
      (u[0] + w[0]) / 4 + corner[0] / 2,
      (u[1] + w[1]) / 4 + corner[1] / 2,
    ];
    if (!triangleClear(u, c, w, isFree)) continue;
    const steps = 16;
    for (let k = 1; k < steps; k++) {
      const f = k / steps;
      const g = 1 - f;
      out.push([
        g * g * u[0] + 2 * g * f * c[0] + f * f * w[0],
        g * g * u[1] + 2 * g * f * c[1] + f * f * w[1],
      ]);
    }
  }
  return out;
}

function roundCorners(points, radius) {
  const n = points.length;
  const out = [];
  for (let i = 0; i < n; i++) {
    const p = points[(i - 1 + n) % n];
    const v = points[i];
    const q = points[(i + 1) % n];
    const lp = Math.hypot(p[0] - v[0], p[1] - v[1]);
    const lq = Math.hypot(q[0] - v[0], q[1] - v[1]);
    const r = Math.min(radius, lp / 2, lq / 2);
    if (r < 1e-6) {
      out.push(v);
      continue;
    }
    const a = [v[0] + ((p[0] - v[0]) / lp) * r, v[1] + ((p[1] - v[1]) / lp) * r];
    const b = [v[0] + ((q[0] - v[0]) / lq) * r, v[1] + ((q[1] - v[1]) / lq) * r];
    const steps = 8;
    for (let k = 0; k <= steps; k++) {
      const t = k / steps;
      const s = 1 - t;
      out.push([
        s * s * a[0] + 2 * s * t * v[0] + t * t * b[0],
        s * s * a[1] + 2 * s * t * v[1] + t * t * b[1],
      ]);
    }
  }
  return out;
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
// {base: [p, q], tip} where p and q lie on the outline `width` apart, or
// null if there's no room for one.
//
// The tail can leave from anywhere on the outline; it leaves from wherever
// lets its tip get closest to the speaker, so it goes round a head in the
// way rather than stopping at it. It points straight at the speaker, stops
// `gap` short of them and of the first point where isFree([x, y]) is false
// (the artwork), and is between minLength and maxLength long.
export function balloonTail(polygon, speaker, { width, maxLength, minLength, gap, isFree }) {
  const step = width / 4;
  let best = null;
  for (let k = 0; k < polygon.length; k++) {
    const a = polygon[k];
    const b = polygon[(k + 1) % polygon.length];
    const edge = Math.hypot(b[0] - a[0], b[1] - a[1]);
    for (let along = 0; along < edge; along += step) {
      const t = edge ? along / edge : 0;
      const p = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
      const distance = Math.hypot(speaker[0] - p[0], speaker[1] - p[1]);
      if (distance <= gap) continue;
      const dx = (speaker[0] - p[0]) / distance;
      const dy = (speaker[1] - p[1]) / distance;
      // It has to leave the balloon, not cut back across it.
      if (inside(polygon, [p[0] + dx, p[1] + dy])) continue;
      let length = Math.min(maxLength, distance - gap);
      for (let s = 1; s <= length + gap; s += 1) {
        if (!isFree([p[0] + dx * s, p[1] + dy * s])) {
          length = Math.min(length, s - gap);
          break;
        }
      }
      if (length < minLength) continue;
      const tip = [p[0] + dx * length, p[1] + dy * length];
      // Get as close to the speaker as possible; among tails that get
      // equally close, take the most direct.
      const score = Math.hypot(speaker[0] - tip[0], speaker[1] - tip[1]) + 0.05 * distance;
      if (!best || score < best.score) best = { k, t, tip, score };
    }
  }
  if (!best) return null;
  return {
    base: [
      walk(polygon, best.k, best.t, -width / 2),
      walk(polygon, best.k, best.t, width / 2),
    ],
    tip: best.tip,
  };
}
