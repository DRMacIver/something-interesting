// Speech balloon geometry: an outline around a block of laid-out text, and
// a tail from it towards whoever is speaking. Pure functions, so
// they can be tested without a browser.

// The outline of a speech balloon around `lines` (boxes with x, y, width,
// height), as a closed polygon of [x, y] points, in the manner of
// Watterson's balloons: an oval round a short remark, and otherwise
// straight sides with rounded corners, cutting diagonally across ragged
// line ends. isFree([x, y]) says whether a point is clear of the artwork;
// the balloon only takes a shortcut, or an oval shape, where it stays clear.
export function balloonOutline(
  lines,
  { padX, padY, radius, isFree, ovalLines = 2 },
) {
  if (!lines.length) return null;
  if (lines.length <= ovalLines) {
    const oval = ovalAround(lines, padX, padY);
    if (oval.every(isFree) && ovalAround(lines, padX * 0.6, padY * 0.6).every(isFree)) {
      return oval;
    }
  }
  const boxes = lines.map((l) => ({
    top: l.y - padY,
    bottom: l.y + l.height + padY,
    left: l.x - padX,
    right: l.x + l.width + padX,
  }));
  const outline = [
    ...hull(envelope(boxes, 1), 1, isFree),
    ...hull(envelope(boxes, -1), -1, isFree).reverse(),
  ];
  return roundCorners(outline, radius);
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
    if (r < 0.5) {
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

function nearestOnPolygon(polygon, [mx, my]) {
  let best = null;
  for (let k = 0; k < polygon.length; k++) {
    const [ax, ay] = polygon[k];
    const [bx, by] = polygon[(k + 1) % polygon.length];
    const dx = bx - ax;
    const dy = by - ay;
    const lengthSq = dx * dx + dy * dy;
    const t = lengthSq
      ? Math.min(1, Math.max(0, ((mx - ax) * dx + (my - ay) * dy) / lengthSq))
      : 0;
    const px = ax + dx * t;
    const py = ay + dy * t;
    const distance = Math.hypot(mx - px, my - py);
    if (!best || distance < best.distance) best = { k, t, point: [px, py], distance };
  }
  return best;
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
// null if there's no room for one. The tip stops `gap` short of the speaker
// and of the first point where isFree([x, y]) is false (the artwork), and
// the tail is at most maxLength long.
export function balloonTail(polygon, speaker, { width, maxLength, gap, isFree }) {
  const nearest = nearestOnPolygon(polygon, speaker);
  if (!nearest || nearest.distance <= gap) return null;
  const [px, py] = nearest.point;
  const dx = (speaker[0] - px) / nearest.distance;
  const dy = (speaker[1] - py) / nearest.distance;
  let length = Math.min(maxLength, nearest.distance - gap);
  for (let s = 1; s <= length + gap; s += 1) {
    if (!isFree([px + dx * s, py + dy * s])) {
      length = Math.min(length, s - gap);
      break;
    }
  }
  if (length < width / 2) return null;
  return {
    base: [
      walk(polygon, nearest.k, nearest.t, -width / 2),
      walk(polygon, nearest.k, nearest.t, width / 2),
    ],
    tip: [px + dx * length, py + dy * length],
  };
}

