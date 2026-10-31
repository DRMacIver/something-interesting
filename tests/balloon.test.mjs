import { test } from "node:test";
import assert from "node:assert/strict";

import { balloonOutline, balloonTail, clearOf } from "../js/balloon.js";

const line = (x, y, width, height = 10) => ({ x, y, width, height });

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

function bounds(polygon) {
  const xs = polygon.map((p) => p[0]);
  const ys = polygon.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}

const options = { padX: 10, padY: 6, radius: 8, isFree: () => true };

function enclosesLines(outline, lines) {
  for (const l of lines) {
    for (const corner of [
      [l.x, l.y],
      [l.x + l.width, l.y],
      [l.x, l.y + l.height],
      [l.x + l.width, l.y + l.height],
    ]) {
      assert.ok(inside(outline, corner), `${corner} should be inside`);
    }
  }
}

// The largest change of direction from one edge of the outline to the next,
// in degrees.
function sharpestTurn(outline) {
  let worst = 0;
  const n = outline.length;
  for (let i = 0; i < n; i++) {
    const [ax, ay] = outline[(i - 1 + n) % n];
    const [bx, by] = outline[i];
    const [cx, cy] = outline[(i + 1) % n];
    const a1 = Math.atan2(by - ay, bx - ax);
    const a2 = Math.atan2(cy - by, cx - bx);
    let turn = Math.abs(a2 - a1);
    if (turn > Math.PI) turn = 2 * Math.PI - turn;
    worst = Math.max(worst, (turn * 180) / Math.PI);
  }
  return worst;
}

test("no lines, no balloon", () => {
  assert.equal(balloonOutline([], options), null);
});

test("a short remark gets an oval", () => {
  const lines = [line(100, 100, 60, 12)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  const [x0, y0, x1, y1] = bounds(outline);
  const cx = (x0 + x1) / 2;
  const cy = (y0 + y1) / 2;
  const a = (x1 - x0) / 2;
  const b = (y1 - y0) / 2;
  for (const [x, y] of outline) {
    const r = ((x - cx) / a) ** 2 + ((y - cy) / b) ** 2;
    assert.ok(Math.abs(r - 1) < 0.02, `point ${x},${y} is off the ellipse`);
  }
});

test("a long remark's oval has blunt ends", () => {
  // A one-line remark several times as long as it is tall (in pixels, with
  // a cap height of 46).
  const cap = 46;
  const lines = [line(333, 200, 418, 72)];
  const outline = balloonOutline(lines, { padX: 0.7 * cap, padY: 0.36 * cap, radius: cap, isFree: () => true });
  enclosesLines(outline, lines);
  const r = tightest(outline, () => true);
  assert.ok(r > 0.6 * cap, `curves as tightly as ${r}`);
});

test("an oval that would hit the art becomes a tighter shape", () => {
  const lines = [line(100, 100, 60, 12)];
  const outline = balloonOutline(lines, {
    ...options,
    // Art just below the text: an oval would bulge into it.
    isFree: ([, y]) => y < 120,
  });
  enclosesLines(outline, lines);
  const [, , , y1] = bounds(outline);
  assert.ok(y1 < 120);
});

test("a block of text gets a padded outline with no corners", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  const [x0, y0, x1, y1] = bounds(outline);
  // Padded all round, give or take a gentle bow.
  assert.ok(x0 >= -10 - 4 && x0 < -9, `left ${x0}`);
  assert.ok(x1 <= 110 + 4 && x1 > 109, `right ${x1}`);
  assert.ok(y0 >= -6 - 4 && y0 < -5, `top ${y0}`);
  assert.ok(y1 <= 36 + 4 && y1 > 35, `bottom ${y1}`);
  assert.ok(sharpestTurn(outline) < 10, `turns by ${sharpestTurn(outline)}`);
});

test("even the straight sides bow out a little", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 100), line(0, 30, 100)];
  const outline = balloonOutline(lines, options);
  // Further out at the middle of each side than near its ends.
  const rightAt = (y) => Math.max(...outline.filter(([, py]) => Math.abs(py - y) < 1.5).map(([x]) => x));
  assert.ok(rightAt(20) > rightAt(4) + 0.5);
  assert.ok(rightAt(20) > rightAt(36) + 0.5);
  const bottomAt = (x) => Math.max(...outline.filter(([px]) => Math.abs(px - x) < 1.5).map(([, y]) => y));
  assert.ok(bottomAt(50) > bottomAt(5) + 0.5);
});

test("the outline sweeps in under shorter last lines", () => {
  // (Under one short line the sweep would be too shallow to be worth it:
  // see "a sweep far longer than it is deep keeps a round corner".)
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 40), line(0, 30, 40), line(0, 40, 40)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  // Not a box: the bottom right corner is cut away...
  assert.ok(!inside(outline, [105, 53]));
  // ...by a sweep, not a step: there's balloon beside the short lines.
  assert.ok(inside(outline, [70, 48]));
  assert.ok(sharpestTurn(outline) < 10);
});

test("where a sweep meets a straight side there's no corner", () => {
  const lines = [line(0, 0, 200), line(0, 10, 200), line(0, 20, 60), line(0, 30, 60), line(0, 40, 60)];
  const outline = balloonOutline(lines, options);
  assert.ok(sharpestTurn(outline) < 10, `turns by ${sharpestTurn(outline)}`);
});

test("the sides come straight down to the widest line", () => {
  // A short first line above wider ones.
  const lines = [line(0, 0, 40), line(0, 10, 100), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  // There's balloon beside the short first line, out to the full width.
  assert.ok(inside(outline, [100, 2]));
});

test("lines above the widest one aren't filled out over the art", () => {
  const lines = [line(0, 0, 40), line(0, 10, 100), line(0, 20, 100)];
  // Art 1px above the second line's padding.
  const art = ([x, y]) => x > 60 && y < 3;
  const outline = balloonOutline(lines, { ...options, isFree: (p) => !art(p) });
  for (const p of outline) assert.ok(!art(p), `${p} is on the art`);
});

test("a sweep under shorter lines is a curve, not a straight diagonal", () => {
  // Wide lines, then much shorter ones.
  const lines = [line(0, 0, 200), line(0, 10, 200), line(0, 20, 60), line(0, 30, 60), line(0, 40, 60)];
  const outline = balloonOutline(lines, options);
  // The points of the outline along the sweep, from the right-hand side
  // down to the bottom under the short lines.
  const sweep = outline.filter(([x, y]) => x > 72 && x < 208 && y > 27 && y < 55.5);
  assert.ok(sweep.length > 4);
  // On a straight line, every point would be on the line through the first
  // and last; a curve bows away from it.
  const [ax, ay] = sweep[0];
  const [bx, by] = sweep[sweep.length - 1];
  const bow = Math.max(
    ...sweep.map(([x, y]) => Math.abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / Math.hypot(bx - ax, by - ay)),
  );
  assert.ok(bow > 1.5, `bows by only ${bow}`);
});

test("a notch beside a short line is bridged", () => {
  const lines = [line(0, 0, 100), line(0, 10, 60), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  assert.ok(inside(outline, [100, 15]));
});

test("the outline keeps off the art", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 40)];
  // The art starts just clear of the last wide line's padding.
  const art = ([x, y]) => x > 60 && y > 28;
  const outline = balloonOutline(lines, { ...options, isFree: (p) => !art(p) });
  enclosesLines(outline, lines);
  assert.ok(!inside(outline, [80, 32]));
  for (const p of outline) assert.ok(!art(p), `${p} is on the art`);
});

const panel = { x0: 0, y0: 0, x1: 300, y1: 200, reach: 12 };

test("a balloon near the top of the panel runs into the border", () => {
  const lines = [line(40, 8, 100), line(40, 18, 100)];
  const outline = balloonOutline(lines, { ...options, panel });
  enclosesLines(outline, lines);
  const [x0, y0, x1] = bounds(outline);
  // It reaches well past the top edge, so only its lower part shows.
  assert.ok(y0 < -6);
  // But it's nowhere near the sides.
  assert.ok(x0 > 0 && x1 < 300);
});

test("a balloon in a top corner runs into both borders", () => {
  const lines = [line(10, 8, 100), line(10, 18, 100)];
  const outline = balloonOutline(lines, { ...options, panel });
  const [x0, y0] = bounds(outline);
  assert.ok(x0 < -6);
  assert.ok(y0 < -6);
});

test("a balloon away from the edges is closed", () => {
  const lines = [line(100, 100, 100), line(100, 110, 100)];
  const outline = balloonOutline(lines, { ...options, panel });
  const [x0, y0, x1, y1] = bounds(outline);
  assert.ok(x0 > 0 && y0 > 0 && x1 < 300 && y1 < 200);
});

const square = [
  [0, 0],
  [100, 0],
  [100, 100],
  [0, 100],
];

const tailOptions = (extra = {}) => ({
  width: 20,
  maxLength: 40,
  minLength: 10,
  gap: 5,
  isFree: () => true,
  ...extra,
});

test("the tail leaves the balloon towards the speaker", () => {
  const tail = balloonTail(square, [50, 200], tailOptions());
  assert.ok(tail);
  const [b1, b2] = tail.base;
  assert.ok(Math.abs(b1[1] - 100) < 1e-6 && Math.abs(b2[1] - 100) < 1e-6);
  assert.ok(Math.abs(Math.abs(b1[0] - b2[0]) - 20) < 1e-6);
  assert.ok(Math.abs(tail.tip[0] - 50) < 1);
  assert.ok(Math.abs(tail.tip[1] - 140) < 1);
});

test("a balloon far from its speaker gets a long tail, ending within reach of them", () => {
  // The speaker's head starts at y = 360, their mouth further on.
  const head = ([, y]) => y < 360;
  const tail = balloonTail(square, [50, 400], tailOptions({ reach: 30, isFree: head }));
  // Within reach of the head (give or take the search's steps) and clear of it.
  assert.ok(tail.tip[1] >= 325 && tail.tip[1] <= 355, `tip at ${tail.tip[1]}`);
});

test("a balloon near its speaker's head gets an ordinary tail, however far the mouth", () => {
  const head = ([, y]) => y < 160;
  const tail = balloonTail(square, [50, 400], tailOptions({ reach: 30, isFree: head }));
  assert.ok(Math.abs(tail.tip[1] - 140) < 1, `tip at ${tail.tip[1]}`);
});

test("a balloon right by the art gets an ordinary tail, even with a clear run past it to the speaker", () => {
  // A head just below the balloon's left half; the speaker's mouth is far
  // off down to the right, with nothing in the way.
  const head = ([x, y]) => !(x < 50 && y > 110);
  const tail = balloonTail(square, [400, 400], tailOptions({ reach: 30, isFree: head }));
  const base = [(tail.base[0][0] + tail.base[1][0]) / 2, (tail.base[0][1] + tail.base[1][1]) / 2];
  const length = Math.hypot(tail.tip[0] - base[0], tail.tip[1] - base[1]);
  // maxLength from the outline (the base cuts across the corner).
  assert.ok(length <= 50, `${length} long`);
});

test("only the art, not other balloons, keeps a stranded balloon's tail short", () => {
  // Another balloon just below this one's right side, which the tail must
  // keep clear of.
  const other = ([x, y]) => !(x > 75 && x < 200 && y > 105 && y < 300);
  const head = ([, y]) => y < 360;
  const tail = balloonTail(
    square,
    [50, 400],
    tailOptions({ reach: 30, isFree: (p) => head(p) && other(p), isArtFree: head }),
  );
  assert.ok(tail.tip[1] >= 325, `tip at ${tail.tip[1]}`);
});

test("art by the middle of a side, away from the corners, still keeps the tail short", () => {
  // A head just under the middle of the bottom edge; the mouth far off.
  const head = ([x, y]) => !(x > 40 && x < 60 && y > 110);
  const tail = balloonTail(square, [400, 400], tailOptions({ reach: 30, isFree: head }));
  const length = Math.hypot(tail.tip[0] - (tail.base[0][0] + tail.base[1][0]) / 2, tail.tip[1] - (tail.base[0][1] + tail.base[1][1]) / 2);
  assert.ok(length <= 50, `${length} long`);
});

test("the tail stops short of the speaker", () => {
  const tail = balloonTail(square, [50, 120], tailOptions());
  assert.ok(tail.tip[1] <= 115 + 1e-6);
});

test("the tail stops before running into the artwork", () => {
  const tail = balloonTail(square, [50, 200], tailOptions({ isFree: ([, y]) => y < 125 }));
  assert.ok(tail.tip[1] <= 120 + 1);
  assert.ok(tail.tip[1] >= 115);
});

test("there is no tail when there's no room for one", () => {
  const tail = balloonTail(square, [50, 200], tailOptions({ isFree: ([, y]) => y < 103 }));
  assert.equal(tail, null);
});

test("the tail base goes round corners", () => {
  // Speaker diagonally off the corner: the base straddles it.
  const tail = balloonTail(square, [200, 200], tailOptions());
  const [b1, b2] = tail.base;
  const onRight = (p) => Math.abs(p[0] - 100) < 1e-6;
  const onBottom = (p) => Math.abs(p[1] - 100) < 1e-6;
  assert.ok((onRight(b1) && onBottom(b2)) || (onBottom(b1) && onRight(b2)));
});

test("a tail is a straight wedge", () => {
  const head = ([x, y]) => x > 25 && x < 75 && y > 110 && y < 250;
  const tail = balloonTail(square, [50, 300], tailOptions({ isFree: (p) => !head(p) }));
  const [b1, b2] = tail.base;
  const start = [(b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2];
  // The bend point lies on the straight line from the base to the tip.
  const cross =
    (tail.tip[0] - start[0]) * (tail.bend[1] - start[1]) -
    (tail.tip[1] - start[1]) * (tail.bend[0] - start[0]);
  assert.ok(Math.abs(cross) < 1e-6);
});

test("the tail goes round a head in the way rather than into it", () => {
  // A head right under the balloon, between it and the speaker's mouth.
  const head = ([x, y]) => x > 25 && x < 75 && y > 110 && y < 250;
  const tail = balloonTail(square, [50, 300], tailOptions({ isFree: (p) => !head(p) }));
  assert.ok(tail);
  // It comes down beside the head...
  assert.ok(tail.tip[0] < 25 || tail.tip[0] > 75);
  // ...and is pointing at the mouth.
  const dx = 50 - tail.tip[0];
  const dy = 300 - tail.tip[1];
  const [b1, b2] = tail.base;
  const mx = (b1[0] + b2[0]) / 2;
  const my = (b1[1] + b2[1]) / 2;
  const cos =
    ((tail.tip[0] - mx) * dx + (tail.tip[1] - my) * dy) /
    (Math.hypot(tail.tip[0] - mx, tail.tip[1] - my) * Math.hypot(dx, dy));
  assert.ok(cos > 0.98);
});

test("a tail that would run into the art gives way to one that ends in the open", () => {
  // Hair right under the right-hand part of the balloon, with the speaker
  // just inside it. The nearest tails run straight into the hair, which
  // reads as pointing at the hair.
  const hair = ([x, y]) => x > 55 && x < 105 && y > 118 && y < 240;
  const options = tailOptions({ maxLength: 20, isFree: (p) => !hair(p) });
  const speaker = [80, 125];
  // How much shorter than it could have been the tail is.
  const shortfall = (tail) => {
    const [b1, b2] = tail.base;
    const start = [(b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2];
    const length = Math.hypot(tail.tip[0] - start[0], tail.tip[1] - start[1]);
    const room = Math.hypot(speaker[0] - start[0], speaker[1] - start[1]) - options.gap;
    return Math.min(options.maxLength, room) - length;
  };
  assert.ok(shortfall(balloonTail(square, speaker, options)) > 1, "without a penalty it is cut short");
  assert.ok(shortfall(balloonTail(square, speaker, { ...options, blockedPenalty: 20 })) < 1);
});

test("a tail points at the speaker with a clear line of sight", () => {
  // A cap of hair between the balloon and the speaker's mouth: a tail
  // stopping above the hair would point through it at the mouth.
  const hair = ([x, y]) => x > 55 && x < 105 && y > 130 && y < 160;
  const options = tailOptions({ maxLength: 15, isFree: (p) => !hair(p), blockedPenalty: 50 });
  const speaker = [60, 200];
  const over = balloonTail(square, speaker, options);
  assert.ok(over.tip[0] > 55, "without the check it stops over the hair");
  const beside = balloonTail(square, speaker, { ...options, clearSight: 10 });
  assert.ok(beside.tip[0] < 55, `tip at ${beside.tip}`);
});

// Signed turns, in degrees, from each edge of the outline to the next.
function turns(outline) {
  const n = outline.length;
  const out = [];
  for (let i = 0; i < n; i++) {
    const [ax, ay] = outline[(i - 1 + n) % n];
    const [bx, by] = outline[i];
    const [cx, cy] = outline[(i + 1) % n];
    let turn = Math.atan2(cy - by, cx - bx) - Math.atan2(by - ay, bx - ax);
    while (turn > Math.PI) turn -= 2 * Math.PI;
    while (turn < -Math.PI) turn += 2 * Math.PI;
    out.push((turn * 180) / Math.PI);
  }
  return out;
}

test("corners are rounded as fully as a circular arc", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  // The padded box's top right corner is at (110, -6). A circular arc of
  // radius r leaves (sqrt 2 - 1) r between the corner and the curve.
  const gap = Math.min(...outline.map(([x, y]) => Math.hypot(x - 110, y + 6)));
  assert.ok(gap >= 0.9 * (Math.SQRT2 - 1) * options.radius, `only ${gap} from the corner`);
});

test("small balloons get rounder corners", () => {
  const lines = [line(0, 0, 40), line(0, 10, 40), line(0, 20, 40)];
  const outline = balloonOutline(lines, { ...options, roundness: 0.4 });
  // The text is 40 by 30, so corners are rounded over 12 (more than the
  // radius of 8).
  const gap = Math.min(...outline.map(([x, y]) => Math.hypot(x - 50, y + 6)));
  assert.ok(gap >= 0.9 * (Math.SQRT2 - 1) * 12, `only ${gap} from the corner`);
});

test("without art in the way, a balloon sweeping down several steps is convex", () => {
  const lines = [line(0, 0, 200), line(0, 10, 200), line(0, 20, 150), line(0, 30, 100), line(0, 40, 60)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  const t = turns(outline);
  const sign = Math.sign(t.reduce((a, b) => a + b, 0));
  const against = Math.min(...t.map((x) => x * sign));
  assert.ok(against > -0.5, `turns back by ${against}`);
});

test("rounding never cuts into the text", () => {
  const lines = [line(40, 8, 100), line(40, 18, 100), line(40, 28, 60)];
  // Even asked for very round corners, and hanging from the top border.
  const outline = balloonOutline(lines, { ...options, roundness: 1, panel });
  enclosesLines(outline, lines);
});

test("a tail curves when that gets it round something", () => {
  // A shelf of art under the right of the balloon, with the speaker below
  // and to the right of it: straight tails have to start well to the left
  // to miss it, but one that sets off downwards and bends can get closer.
  const shelf = ([x, y]) => x > 70 && x < 200 && y > 100 && y < 115;
  const tail = balloonTail(square, [150, 160], tailOptions({ isFree: (p) => !shelf(p), curvePenalty: 5 }));
  const [b1, b2] = tail.base;
  const start = [(b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2];
  const cross =
    (tail.tip[0] - start[0]) * (tail.bend[1] - start[1]) -
    (tail.tip[1] - start[1]) * (tail.bend[0] - start[0]);
  assert.ok(Math.abs(cross) > 1, "the tail is curved");
});

// The outline with points closer than `spacing` to the last one dropped:
// between points much closer than that, rounding errors swamp the shape.
function resample(points, spacing = 2) {
  const out = [points[0]];
  for (const p of points) {
    const last = out[out.length - 1];
    if (Math.hypot(p[0] - last[0], p[1] - last[1]) >= spacing) out.push(p);
  }
  return out;
}

// The radius of the tightest curve among the outline's points that satisfy
// `where`.
function tightest(points, where) {
  const outline = resample(points);
  let best = Infinity;
  const n = outline.length;
  for (let i = 0; i < n; i++) {
    const a = outline[(i - 1 + n) % n];
    const b = outline[i];
    const c = outline[(i + 1) % n];
    if (!where(b)) continue;
    const ab = Math.hypot(b[0] - a[0], b[1] - a[1]);
    const bc = Math.hypot(c[0] - b[0], c[1] - b[1]);
    const ca = Math.hypot(a[0] - c[0], a[1] - c[1]);
    const area = Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2;
    if (area > 1e-9) best = Math.min(best, (ab * bc * ca) / (4 * area));
  }
  return best;
}

test("a sweep in under shorter last lines is one smooth curve", () => {
  // Dad's balloon in panel 2 of the example (in pixels, with a cap height
  // of 46): the second line is the widest, then three steadily shorter
  // ones, and the balloon hangs from the top border.
  const cap = 46;
  const widths = [564.6, 633.1, 578.3, 510.1, 445.9];
  const lines = widths.map((width, i) => line(32.2, 7.9 + 71.7 * i, width, 71.7));
  const outline = balloonOutline(lines, {
    padX: 0.7 * cap,
    padY: 0.36 * cap,
    radius: cap,
    isFree: () => true,
    panel: { x0: 0, y0: 0, x1: 800, y1: 1200, reach: 1.2 * cap },
  });
  enclosesLines(outline, lines);
  // From below the widest line round to the bottom it is one broad curve:
  // nowhere does it bend as tightly as twice an ordinary corner.
  const r = tightest(outline, ([x, y]) => x > 450 && y > 150 && y < 450);
  assert.ok(r > 2 * cap, `curves as tightly as ${r}`);
});

test("a last line a little narrower than the one above gets an ordinary rounded corner", () => {
  // Calvin's reply in panel 2, centred: the third line is the widest and
  // the last is a little narrower on both sides.
  const cap = 46;
  const lines = [
    line(424, 463, 312, 72),
    line(489, 535, 183, 72),
    line(405, 607, 351, 72),
    line(414, 678, 333, 72),
  ];
  const outline = balloonOutline(lines, {
    padX: 0.7 * cap,
    padY: 0.36 * cap,
    radius: cap,
    roundness: 0.3,
    isFree: () => true,
  });
  enclosesLines(outline, lines);
  // The bottom corners are as round as any other corner.
  const r = tightest(outline, ([, y]) => y > 700);
  assert.ok(r > 0.5 * cap, `curves as tightly as ${r}`);
});

test("a sweep far longer than it is deep keeps a round corner", () => {
  // A long first line and a much shorter second one: the sweep under the
  // second line is far wider than it is deep.
  const cap = 46;
  const lines = [line(40, 400, 880, 72), line(40, 472, 540, 72)];
  const outline = balloonOutline(lines, {
    padX: 0.7 * cap,
    padY: 0.36 * cap,
    radius: cap,
    roundness: 0.3,
    isFree: () => true,
  });
  enclosesLines(outline, lines);
  const r = tightest(outline, ([x]) => x > 600);
  assert.ok(r > 0.5 * cap, `curves as tightly as ${r}`);
});

test("a near-vertical side is a side, not part of a sweep that cuts across lines below it", () => {
  // Dad's wall of text in a balloon (in pixels, with a cap height of 46):
  // the top lines are a little wider than a line far below them, then the
  // last few lines are shorter.
  const cap = 46;
  const rights = [
    1533, 1489, 1526, 1426, 1378, 1533, 1468, 1399, 1420, 1420, 1259, 1341, 1371, 834, 1128, 801, 806, 783,
    1192, 1003, 1268, 1015, 1519, 1247, 1319, 993,
  ];
  const lines = rights.map((right, i) => line(618, 72 * i, right - 618, 72));
  const outline = balloonOutline(lines, {
    padX: 0.7 * cap,
    padY: 0.36 * cap,
    radius: cap,
    roundness: 0.3,
    isFree: () => true,
  });
  enclosesLines(outline, lines);
});

test("a point is clear of other balloons only outside them and a margin round them", () => {
  const clear = clearOf([square], 10);
  assert.equal(clear([50, 50]), false, "inside");
  assert.equal(clear([105, 50]), false, "within the margin");
  assert.equal(clear([115, 50]), true, "outside the margin");
  assert.equal(clear([115, 115]), true, "off a corner");
});

test("a tail kept clear of another balloon leaves from elsewhere", () => {
  // Another balloon right beside the direct route to the speaker.
  const other = [
    [110, 90],
    [200, 90],
    [200, 160],
    [110, 160],
  ];
  const clear = clearOf([other], 5);
  const tail = balloonTail(square, [150, 250], tailOptions({ isFree: clear }));
  assert.ok(tail);
  const [b1, b2] = tail.base;
  const points = [b1, b2, tail.bend, tail.tip];
  for (const p of points) assert.ok(clear(p), `${p} is too close to the other balloon`);
});
