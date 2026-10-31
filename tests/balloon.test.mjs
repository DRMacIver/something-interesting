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

test("an oval that would hit the art becomes a rounded box", () => {
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

test("a block of text gets a box with straight sides and round corners", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  const [x0, y0, x1, y1] = bounds(outline);
  assert.equal(x0, -10);
  assert.equal(x1, 110);
  assert.equal(y0, -6);
  assert.equal(y1, 36);
  // Straight top edge between the corners.
  const top = outline.filter(([, y]) => Math.abs(y - y0) < 1e-9);
  const span = Math.max(...top.map((p) => p[0])) - Math.min(...top.map((p) => p[0]));
  assert.ok(span >= 120 - 2 * 8 - 1e-6);
  // The very corner is cut off.
  assert.ok(!inside(outline, [-9, -5]));
});

test("ragged line ends are joined by a straight edge", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 40)];
  const outline = balloonOutline(lines, options);
  enclosesLines(outline, lines);
  // Beside the short last line, the edge runs diagonally rather than in a
  // step, so this point near the step's inner corner is inside.
  assert.ok(inside(outline, [80, 26]));
});

test("an edge that would cross the art keeps to the text instead", () => {
  const lines = [line(0, 0, 100), line(0, 10, 100), line(0, 20, 40)];
  // The art starts just clear of the last wide line's padding.
  const art = ([x, y]) => x > 60 && y > 28;
  const outline = balloonOutline(lines, {
    ...options,
    isFree: (p) => !art(p),
  });
  enclosesLines(outline, lines);
  assert.ok(!inside(outline, [80, 30]));
  for (const p of outline) assert.ok(!art(p), `${p} is on the art`);
});

test("a notch beside a short line is bridged", () => {
  const lines = [line(0, 0, 100), line(0, 10, 60), line(0, 20, 100)];
  const outline = balloonOutline(lines, options);
  assert.ok(inside(outline, [100, 15]));
});

const square = [
  [0, 0],
  [100, 0],
  [100, 100],
  [0, 100],
];

test("the tail leaves the balloon towards the speaker", () => {
  const tail = balloonTail(square, [50, 200], {
    width: 20,
    maxLength: 40,
    gap: 5,
    isFree: () => true,
  });
  assert.ok(tail);
  const [b1, b2] = tail.base;
  assert.ok(Math.abs(b1[1] - 100) < 1e-6 && Math.abs(b2[1] - 100) < 1e-6);
  assert.ok(Math.abs(Math.abs(b1[0] - b2[0]) - 20) < 1e-6);
  assert.ok(Math.abs(tail.tip[0] - 50) < 1e-6);
  assert.ok(Math.abs(tail.tip[1] - 140) < 1e-6);
});

test("the tail stops short of the speaker", () => {
  const tail = balloonTail(square, [50, 120], {
    width: 20,
    maxLength: 40,
    gap: 5,
    isFree: () => true,
  });
  assert.ok(tail.tip[1] <= 115 + 1e-6);
});

test("the tail stops before running into the artwork", () => {
  const tail = balloonTail(square, [50, 200], {
    width: 20,
    maxLength: 40,
    gap: 5,
    isFree: ([, y]) => y < 125,
  });
  assert.ok(tail.tip[1] <= 120 + 1);
  assert.ok(tail.tip[1] >= 115);
});

test("there is no tail when there's no room for one", () => {
  const tail = balloonTail(square, [50, 200], {
    width: 20,
    maxLength: 40,
    gap: 5,
    isFree: ([, y]) => y < 103,
  });
  assert.equal(tail, null);
});

test("the tail base goes round corners", () => {
  // Speaker diagonally off the corner: the base straddles it.
  const tail = balloonTail(square, [200, 200], {
    width: 20,
    maxLength: 40,
    gap: 5,
    isFree: () => true,
  });
  const [b1, b2] = tail.base;
  const onRight = (p) => Math.abs(p[0] - 100) < 1e-6;
  const onBottom = (p) => Math.abs(p[1] - 100) < 1e-6;
  assert.ok((onRight(b1) && onBottom(b2)) || (onBottom(b1) && onRight(b2)));
});
