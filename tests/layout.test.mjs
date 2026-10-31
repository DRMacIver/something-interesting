import { test } from "node:test";
import assert from "node:assert/strict";

import {
  freeIntervals,
  layoutText,
  fitPanels,
  makePanel,
  tailFor,
} from "../js/layout.js";

// Every character is half the font size wide, spaces included.
const measure = (text, fontSize) => text.length * fontSize * 0.5;

// A 100x50 piece of art whose right-hand side (x >= 40) is blocked.
const artRightBlocked = {
  width: 100,
  height: 50,
  free: Array.from({ length: 50 }, () => [[0, 40]]),
};

function panelWithHeadroom(headroom, spec = artRightBlocked) {
  return makePanel(spec, 100, spec.height + headroom, 0);
}

const opts = (extra = {}) => ({
  measure,
  fontSize: 10,
  lineHeight: 1,
  margin: 0,
  align: "left",
  ...extra,
});

test("headroom above the art is entirely free", () => {
  const panel = panelWithHeadroom(30);
  assert.deepEqual(freeIntervals(panel, 0, 20, 0), [[0, 100]]);
});

test("rows inside the art use the art's free intervals", () => {
  const panel = panelWithHeadroom(30);
  assert.deepEqual(freeIntervals(panel, 40, 50, 0), [[0, 40]]);
});

test("a band spanning headroom and art gets the intersection", () => {
  const panel = panelWithHeadroom(30);
  assert.deepEqual(freeIntervals(panel, 25, 35, 0), [[0, 40]]);
});

test("margin shrinks intervals horizontally and widens the band", () => {
  const panel = panelWithHeadroom(30);
  assert.deepEqual(freeIntervals(panel, 0, 10, 5), [[5, 95]]);
  // The band is 18..28 but the margin makes it reach into the art at 30.
  assert.deepEqual(freeIntervals(panel, 18, 28, 5), [[5, 35]]);
});

test("padding keeps text away from the panel edges", () => {
  const panel = makePanel(artRightBlocked, 100, 80, 7);
  assert.deepEqual(freeIntervals(panel, 7, 17, 0), [[7, 93]]);
});

test("art is scaled to the cell width", () => {
  const panel = makePanel(artRightBlocked, 200, 100, 0);
  // Art is 100 tall once scaled, so it fills the whole cell.
  assert.deepEqual(freeIntervals(panel, 10, 20, 0), [[0, 80]]);
});

test("rows with no free space block the whole band", () => {
  const spec = {
    width: 100,
    height: 50,
    free: Array.from({ length: 50 }, (_, y) => (y === 10 ? [] : [[0, 100]])),
  };
  const panel = makePanel(spec, 100, 50, 0);
  assert.deepEqual(freeIntervals(panel, 5, 15, 0), []);
  assert.deepEqual(freeIntervals(panel, 11, 20, 0), [[0, 100]]);
});

test("multiple free intervals survive intersection", () => {
  const spec = {
    width: 100,
    height: 10,
    free: Array.from({ length: 10 }, () => [[0, 30], [50, 100]]),
  };
  const panel = makePanel(spec, 100, 10, 0);
  assert.deepEqual(freeIntervals(panel, 0, 10, 0), [[0, 30], [50, 100]]);
});

test("text wraps to the available width", () => {
  const panel = panelWithHeadroom(100);
  // 100px wide at 5px per char = 20 chars per line.
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee ffff", opts());
  assert.equal(result.fits, true);
  assert.deepEqual(
    result.lines.map((l) => l.text),
    ["aaaa bbbb cccc dddd", "eeee ffff"],
  );
  assert.deepEqual(
    result.lines.map((l) => [l.x, l.y]),
    [
      [0, 0],
      [0, 10],
    ],
  );
});

test("text flows around the art", () => {
  const panel = panelWithHeadroom(10);
  // First line is in the headroom and can be 20 chars wide; after that the
  // art leaves only 40px = 8 chars.
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee ffff", opts());
  assert.equal(result.fits, true);
  assert.deepEqual(
    result.lines.map((l) => l.text),
    ["aaaa bbbb cccc dddd", "eeee", "ffff"],
  );
  for (const line of result.lines.slice(1)) {
    assert.ok(line.x + line.width <= 40);
  }
});

test("centred text is centred within its own interval", () => {
  const panel = panelWithHeadroom(10);
  const result = layoutText(
    panel,
    "aaaa bbbb cccc dddd eeee",
    opts({ align: "center" }),
  );
  assert.deepEqual(
    result.lines.map((l) => [l.text, l.x]),
    [
      ["aaaa bbbb cccc dddd", 2.5],
      ["eeee", 10],
    ],
  );
});

test("explicit newlines start new lines and blank lines leave a gap", () => {
  const panel = panelWithHeadroom(100);
  const result = layoutText(panel, "aa\nbb\n\ncc", opts());
  assert.deepEqual(
    result.lines.map((l) => [l.text, l.y]),
    [
      ["aa", 0],
      ["bb", 10],
      ["cc", 30],
    ],
  );
});

test("leading and trailing whitespace is ignored", () => {
  const panel = panelWithHeadroom(100);
  const result = layoutText(panel, "\n  aa   bb  \n\n", opts());
  assert.deepEqual(
    result.lines.map((l) => l.text),
    ["aa bb"],
  );
});

test("words too long for any line are broken", () => {
  const panel = panelWithHeadroom(100);
  const result = layoutText(panel, "a".repeat(45), opts());
  assert.equal(result.fits, true);
  assert.deepEqual(
    result.lines.map((l) => l.text.length),
    [20, 20, 5],
  );
});

test("a word that only fits in a wider space waits for one", () => {
  // Free space is narrow at the top and wide further down.
  const spec = {
    width: 100,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 20 ? [[0, 30]] : [[0, 100]])),
  };
  const panel = makePanel(spec, 100, 100, 0);
  const result = layoutText(panel, "aaaaaaaaaa", opts());
  assert.equal(result.fits, true);
  assert.equal(result.lines.length, 1);
  assert.ok(result.lines[0].y >= 20);
});

test("text that runs out of space does not fit", () => {
  const panel = panelWithHeadroom(0);
  const result = layoutText(panel, "word ".repeat(100), opts());
  assert.equal(result.fits, false);
});

test("empty text fits trivially", () => {
  const panel = panelWithHeadroom(0);
  const result = layoutText(panel, "   ", opts());
  assert.equal(result.fits, true);
  assert.deepEqual(result.lines, []);
});

test("growing finds the smallest headroom that fits every panel", () => {
  const texts = ["aaaa", "word ".repeat(30)];
  const result = fitPanels([artRightBlocked, artRightBlocked], texts, {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "grow",
    step: 1,
  });
  assert.equal(result.fits, true);
  assert.equal(result.fontSize, 10);
  assert.ok(result.layouts.every((l) => l.fits));
  // One pixel less and it no longer fits.
  const smaller = layoutText(
    makePanel(artRightBlocked, 100, result.cellHeight - 1, 0),
    texts[1],
    opts(),
  );
  assert.equal(smaller.fits, false);
});

test("growing never shrinks below the art", () => {
  const result = fitPanels([artRightBlocked], ["hi"], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "grow",
  });
  assert.equal(result.cellHeight, 50);
});

test("extra headroom is added on top of the art", () => {
  const result = fitPanels([artRightBlocked], ["hi"], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "shrink",
    headroom: 25,
  });
  assert.equal(result.cellHeight, 75);
});

test("shrinking finds a font size that fits", () => {
  const text = "word ".repeat(30);
  const result = fitPanels([artRightBlocked], [text], {
    ...opts({ fontSize: 40 }),
    cellWidth: 100,
    padding: 0,
    mode: "shrink",
    headroom: 0,
  });
  assert.equal(result.fits, true);
  assert.ok(result.fontSize < 40);
  assert.equal(result.cellHeight, 50);
  const bigger = layoutText(
    makePanel(artRightBlocked, 100, 50, 0),
    text,
    opts({ fontSize: result.fontSize + 0.5 }),
  );
  assert.equal(bigger.fits, false);
});

test("shrinking keeps the requested size when the text already fits", () => {
  const result = fitPanels([artRightBlocked], ["hi"], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "shrink",
    headroom: 0,
  });
  assert.equal(result.fontSize, 10);
});

test("panels with different art sizes share a cell height", () => {
  const short = { width: 100, height: 20, free: Array.from({ length: 20 }, () => [[0, 100]]) };
  const result = fitPanels([artRightBlocked, short], ["", ""], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "grow",
  });
  assert.equal(result.cellHeight, 50);
  assert.equal(result.panels[1].artTop, 30);
});

test("the tail starts below the text and points at the mouth", () => {
  const panel = panelWithHeadroom(100);
  const layout = layoutText(panel, "aaaa", opts());
  // Line box is x 0..20, y 0..10.
  const tail = tailFor(layout, [60, 100], { gap: 2, maxLength: 20 });
  assert.ok(tail.from[1] > 10);
  assert.ok(tail.to[0] > tail.from[0]);
  assert.ok(tail.to[1] > tail.from[1]);
  const length = Math.hypot(tail.to[0] - tail.from[0], tail.to[1] - tail.from[1]);
  assert.ok(length <= 20 + 1e-9);
});

test("there is no tail without text", () => {
  const panel = panelWithHeadroom(100);
  const layout = layoutText(panel, "", opts());
  assert.equal(tailFor(layout, [60, 100], { gap: 2, maxLength: 20 }), null);
});

test("layout can start lower down", () => {
  const panel = panelWithHeadroom(100);
  const result = layoutText(panel, "aa", opts({ startY: 25 }));
  assert.equal(result.lines[0].y, 25);
});

test("bottom alignment moves text as far down as it will go", () => {
  const result = fitPanels([artRightBlocked], ["aaaa bb"], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "shrink",
    headroom: 30,
    valign: "bottom",
  });
  const [line] = result.layouts[0].lines;
  // The single line has to stay in the 40px-wide gap beside the art, and it
  // can go right down to the bottom of the panel.
  assert.equal(line.text, "aaaa bb");
  assert.ok(line.y + line.height <= 80);
  assert.ok(line.y + line.height > 79);
  assert.ok(result.layouts[0].fits);
});

test("middle alignment splits the difference", () => {
  const base = {
    ...opts(),
    cellWidth: 100,
    padding: 0,
    mode: "shrink",
    headroom: 30,
  };
  // Text too wide for the gap beside the art, so it must stay in the headroom.
  const text = "a".repeat(15);
  const top = fitPanels([artRightBlocked], [text], { ...base, valign: "top" });
  const bottom = fitPanels([artRightBlocked], [text], { ...base, valign: "bottom" });
  const middle = fitPanels([artRightBlocked], [text], { ...base, valign: "middle" });
  const y = (r) => r.layouts[0].lines[0].y;
  assert.equal(y(top), 0);
  assert.ok(Math.abs(y(bottom) - 20) < 0.5);
  assert.ok(Math.abs(y(middle) - y(bottom) / 2) < 0.5);
});
