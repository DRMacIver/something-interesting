import { test } from "node:test";
import assert from "node:assert/strict";

import {
  freeIntervals,
  layoutText,
  fitPanels,
  makePanel,
  layoutColumn,
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
      });
  assert.equal(result.cellHeight, 50);
});

test("panels with different art sizes share a cell height", () => {
  const short = { width: 100, height: 20, free: Array.from({ length: 20 }, () => [[0, 100]]) };
  const result = fitPanels([artRightBlocked, short], ["", ""], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
      });
  assert.equal(result.cellHeight, 50);
  assert.equal(result.panels[1].artTop, 30);
});

test("reserved areas are kept clear of text", () => {
  const spec = { ...artRightBlocked, reserved: [[0, 10, 20, 30]] };
  const panel = makePanel(spec, 100, 80, 0);
  // Art starts at y = 30, so the reserved area covers y 40..60 and x 0..20.
  assert.deepEqual(freeIntervals(panel, 45, 50, 0), [[20, 40]]);
  assert.deepEqual(freeIntervals(panel, 35, 38, 0), [[0, 40]]);
});

test("reserved areas can reach above the art", () => {
  const spec = { ...artRightBlocked, reserved: [[60, -20, 100, 10]] };
  const panel = makePanel(spec, 100, 80, 0);
  assert.deepEqual(freeIntervals(panel, 15, 20, 0), [[0, 60]]);
});

test("the margin keeps text clear of reserved areas too", () => {
  const spec = { ...artRightBlocked, reserved: [[60, -20, 100, 10]] };
  const panel = makePanel(spec, 100, 80, 0);
  // The reserved area starts at y = 10; within 5 of it, text keeps 5 away.
  assert.deepEqual(freeIntervals(panel, 2, 7, 5), [[5, 55]]);
});

test("panels grow until their reserved areas are inside them", () => {
  // The reserved area starts 25px above the top of the art.
  const spec = { ...artRightBlocked, reserved: [[60, -25, 100, 10]] };
  const result = fitPanels([spec], [""], { ...opts(), cellWidth: 100, padding: 0, step: 1 });
  assert.equal(result.fits, true);
  assert.equal(result.cellHeight, 75);
});

test("a column wraps text to its width and centres each line", () => {
  const { lines, height } = layoutColumn("aaa bbb ccc d", {
    measure,
    fontSize: 10,
    lineHeight: 1,
    width: 30,
  });
  assert.deepEqual(
    lines.map((l) => [l.text, l.x, l.y]),
    [
      ["aaa", 7.5, 0],
      ["bbb", 7.5, 10],
      ["ccc d", 2.5, 20],
    ],
  );
  assert.equal(height, 30);
});

test("a column breaks words longer than its width", () => {
  const { lines } = layoutColumn("a".repeat(12), {
    measure,
    fontSize: 10,
    lineHeight: 1,
    width: 40,
  });
  assert.deepEqual(lines.map((l) => l.text.length), [8, 4]);
});

test("an empty column has no lines", () => {
  const { lines, height } = layoutColumn("  ", { measure, fontSize: 10, lineHeight: 1, width: 40 });
  assert.deepEqual(lines, []);
  assert.equal(height, 0);
});

test("long words break after punctuation where they can", () => {
  const panel = panelWithHeadroom(100);
  // 20 characters fit on a line.
  const result = layoutText(panel, "example.github.io/something-interesting", opts());
  assert.deepEqual(
    result.lines.map((l) => l.text),
    ["example.github.io/", "something-", "interesting"],
  );
});

// Art whose right edge creeps rightwards as it goes down, like the back of
// a head: at row y it covers x < y / 2.
const slopedArt = {
  width: 200,
  height: 100,
  free: Array.from({ length: 100 }, (_, y) => [[Math.floor(y / 2), 200]]),
};

test("left-aligned lines share a left edge where the art only nudges them", () => {
  const panel = makePanel(slopedArt, 200, 100, 0);
  const result = layoutText(panel, "aaaa ".repeat(30), opts({ align: "left" }));
  const lefts = new Set(result.lines.map((l) => l.x));
  assert.equal(lefts.size, 1);
  // ...and that edge clears the art for every line.
  for (const line of result.lines) {
    const lastRow = line.y + line.height - 1;
    assert.ok(line.x >= Math.floor(lastRow / 2));
  }
});

test("lines keep a shared left edge when that still leaves them half the width", () => {
  // Free across the full width at the top, only right of x = 90 below.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 30 ? [[0, 200]] : [[90, 200]])),
  };
  const panel = makePanel(spec, 200, 100, 0);
  const result = layoutText(panel, "aaaa ".repeat(30), opts({ align: "left" }));
  assert.deepEqual(new Set(result.lines.map((l) => l.x)), new Set([90]));
});

test("lines pushed well aside by the art keep their own left edge", () => {
  // Free across the full width at the top, only right of x = 120 below.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 30 ? [[0, 200]] : [[120, 200]])),
  };
  const panel = makePanel(spec, 200, 100, 0);
  const result = layoutText(panel, "aaaa ".repeat(30), opts({ align: "left" }));
  const lefts = result.lines.map((l) => l.x);
  assert.equal(lefts[0], 0);
  assert.equal(lefts[lefts.length - 1], 120);
});

test("a panel can keep its text further from the art than the default", () => {
  const text = "aaaa ".repeat(6);
  const base = { ...opts(), cellWidth: 100, padding: 0, margin: 0 };
  const near = fitPanels([artRightBlocked], [text], base);
  const far = fitPanels([{ ...artRightBlocked, margin: 10 }], [text], base);
  // With more clearance, lines beside the art have less room, so the
  // panel has to grow more.
  assert.ok(far.cellHeight > near.cellHeight);
});

test("padding can differ across and down", () => {
  const panel = makePanel(artRightBlocked, 100, 80, { x: 7, y: 3 });
  assert.deepEqual(freeIntervals(panel, 3, 13, 0), [[7, 93]]);
  const result = layoutText(panel, "aa", opts());
  assert.equal(result.lines[0].x, 7);
  assert.equal(result.lines[0].y, 3);
});

test("line breaks are balanced rather than leaving a lone word", () => {
  const panel = panelWithHeadroom(100);
  // Filling each line greedily would give "aaaa bbbb cccc dddd" / "eeee".
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee", opts());
  assert.deepEqual(
    result.lines.map((l) => l.text),
    ["aaaa bbbb cccc", "dddd eeee"],
  );
});

test("balancing never makes a line too long for its space", () => {
  const panel = panelWithHeadroom(10);
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee ffff gggg", opts({ align: "left" }));
  for (const line of result.lines) {
    const [[a, b]] = freeIntervals(panel, line.y, line.y + line.height, 0);
    assert.ok(line.x >= a - 1e-9 && line.x + line.width <= b + 1e-9, line.text);
  }
});

test("a last line stranded on its own beside the art doesn't count as fitting", () => {
  // Full width at the top, then only a narrow gap on the right.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 20 ? [[0, 200]] : [[150, 200]])),
  };
  const panel = makePanel(spec, 200, 100, 0);
  // Two full lines, and one word left over for the gap beside the art.
  const text = "aaaaaaaaa ".repeat(8) + "bbbb";
  const result = layoutText(panel, text, opts({ align: "left" }));
  assert.equal(result.fits, false);
});

test("lines around a broken word are still balanced", () => {
  const panel = panelWithHeadroom(100);
  // The long word has to be broken, but the lines before it can still be
  // evened out.
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee " + "x".repeat(30) + " ffff", opts());
  assert.deepEqual(result.lines.slice(0, 2).map((l) => l.text), ["aaaa bbbb cccc", "dddd eeee"]);
});
