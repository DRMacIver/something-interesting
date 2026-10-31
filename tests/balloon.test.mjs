import { test } from "node:test";
import assert from "node:assert/strict";

import { balloonOutline, balloonTail } from "../js/balloon.js";

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

test("an oval that would hit the art becomes a tighter shape", () => {
  const lines = [line(100, 100, 60, 12)];
  const outline = balloonOutline(lines, {
    ...options,
    // Art just below the text: an oval would bulge into it.
    isFree: ([, y]) => y < 120,
  });
  enclosesLines(outline, lines);
  const [, , , y1] = bounds(outline);
  assert.ok(y1 <= 112 + 6 + 1e-6);
});

test("a block of text gets a padded outline with no corners", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  const [x0, y0, x1, y1] = bounds(outline);
  assert.ok(x0 >= -10 - 1e-6 && x0 < -9, `left ${x0}`);
  assert.ok(x1 <= 110 + 1e-6 && x1 > 109, `right ${x1}`);
  assert.ok(y0 >= -6 - 1e-6 && y0 < -5, `top ${y0}`);
  assert.ok(y1 <= 36 + 1e-6 && y1 > 35, `bottom ${y1}`);
  assert.ok(sharpestTurn(outline) < 20, `turns by ${sharpestTurn(outline)}`);
});

test("the outline sweeps in under shorter last lines", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 40)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  // Not a box: the bottom right corner is cut away...
  assert.ok(!inside(outline, [105, 33]));
  // ...by a sweep, not a step: there's balloon beside the short line.
  assert.ok(inside(outline, [70, 28]));
  assert.ok(sharpestTurn(outline) < 20);
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
