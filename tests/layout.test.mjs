import { test } from "node:test";
import assert from "node:assert/strict";

import {
  freeIntervals,
  layoutText,
  fitPanels,
  makePanel,
  layoutColumn,
  chooseWidth,
  artWindow,
  openBeyond,
  shiftedView,
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

test("margin keeps text clear of the art, not the panel edges", () => {
  const panel = panelWithHeadroom(30);
  // Nothing but panel edges: the margin doesn't apply (padding does).
  assert.deepEqual(freeIntervals(panel, 0, 10, 5), [[0, 100]]);
  // The band is 18..28 but the margin makes it reach into the art at 30,
  // which ends at x = 40.
  assert.deepEqual(freeIntervals(panel, 18, 28, 5), [[0, 35]]);
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
  const spec = { ...artRightBlocked, reserved: [[20, 10, 30, 30]] };
  const panel = makePanel(spec, 100, 80, 0);
  // Art starts at y = 30, so the reserved area covers y 40..60 and x 20..30.
  assert.deepEqual(freeIntervals(panel, 45, 50, 0), [[0, 20]]);
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
  // The reserved area starts at y = 10; within 5 of it, text keeps 5 away
  // (and the left of the interval is the panel edge, kept by padding).
  assert.deepEqual(freeIntervals(panel, 2, 7, 5), [[0, 55]]);
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
  // Beside the art, two of these words fit on a line without the margin
  // and only one with it.
  const text = "aaa ".repeat(8);
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

test("block text that would narrow sharply partway down doesn't count as fitting", () => {
  // Full width at the top, then only the left half, as beside another
  // character's balloon.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 20 ? [[0, 200]] : [[0, 100]])),
  };
  const panel = makePanel(spec, 200, 100, 0);
  const text = "aaaaaaaaa ".repeat(10);
  assert.equal(layoutText(panel, text, opts({ align: "left" })).fits, true);
  assert.equal(layoutText(panel, text, opts({ align: "left", block: true })).fits, false);
});

test("block text may sit wholly in a narrow space", () => {
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, () => [[0, 100]]),
  };
  const panel = makePanel(spec, 200, 100, 0);
  const result = layoutText(panel, "aaaaaaaaa ".repeat(6), opts({ align: "left", block: true }));
  assert.equal(result.fits, true);
});

test("lines around a broken word are still balanced", () => {
  const panel = panelWithHeadroom(100);
  // The long word has to be broken, but the lines before it can still be
  // evened out.
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee " + "x".repeat(30) + " ffff", opts());
  assert.deepEqual(result.lines.slice(0, 2).map((l) => l.text), ["aaaa bbbb cccc", "dddd eeee"]);
});

test("text pushed aside by the art can move to the far side of its space", () => {
  // Art down the whole left side of the panel.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, () => [[60, 200]]),
  };
  const panel = makePanel(spec, 200, 100, 0);
  const result = layoutText(panel, "aaaa bbbb cccc", opts({ align: "left", awayFromArt: true }));
  const right = Math.max(...result.lines.map((l) => l.x + l.width));
  assert.ok(Math.abs(right - 200) < 1e-9, `ends at ${right}`);
  assert.equal(new Set(result.lines.map((l) => l.x)).size, 1);
});

test("text that isn't pushed aside stays where it is", () => {
  const panel = panelWithHeadroom(100);
  const result = layoutText(panel, "aaaa bbbb", opts({ align: "left", awayFromArt: true }));
  assert.equal(result.lines[0].x, 0);
});

test("short text with room to spare drops down towards the art", () => {
  // Lots of headroom above the art, and only a line of text.
  const panel = panelWithHeadroom(200);
  const result = layoutText(panel, "aaaa bbbb", opts({ drop: true, keepGap: 15 }));
  assert.deepEqual(result.lines.map((l) => l.text), ["aaaa bbbb"]);
  const [line] = result.lines;
  // The art starts at y = 200; the line ends 15 above it, give or take.
  assert.ok(line.y + line.height <= 185 + 1e-9, `ends at ${line.y + line.height}`);
  assert.ok(line.y + line.height > 180, `ends at ${line.y + line.height}`);
});

test("dropping never re-wraps the text", () => {
  // The art beside the bottom of the headroom would force a narrower line.
  const panel = panelWithHeadroom(200);
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee", opts({ drop: true }));
  const plain = layoutText(panel, "aaaa bbbb cccc dddd eeee", opts());
  assert.deepEqual(result.lines.map((l) => l.text), plain.lines.map((l) => l.text));
});

test("text that fills its space stays at the top", () => {
  // Two full-width lines fill the headroom; any lower and they'd re-wrap
  // round the art.
  const panel = panelWithHeadroom(20);
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee ffff gggg hhhh", opts({ drop: true }));
  assert.equal(result.lines[0].y, 0);
});

test("text drops no lower than the limit it's given", () => {
  const panel = panelWithHeadroom(200);
  const result = layoutText(panel, "aaaa bbbb", opts({ drop: true, dropLimit: 100 }));
  const [line] = result.lines;
  assert.ok(line.y + line.height <= 100 + 1e-9);
  assert.ok(line.y + line.height > 95);
});

test("text moved away from the art goes no further than it's allowed", () => {
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, () => [[60, 200]]),
  };
  const panel = makePanel(spec, 200, 100, 0);
  const result = layoutText(panel, "aaaa", opts({ align: "left", awayFromArt: true, awayLimit: 30 }));
  assert.equal(result.lines[0].x, 90);
});

test("text dropped beside its speaker stays beside them", () => {
  // Art down the left side; the text drops down beside it.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, () => [[60, 200]]),
  };
  const panel = makePanel(spec, 200, 300, 0);
  const result = layoutText(
    panel,
    "aaaa",
    opts({ align: "left", awayFromArt: true, awayLimit: 30, drop: true, dropLimit: 250 }),
  );
  const [line] = result.lines;
  assert.ok(line.y > 200, "it has dropped");
  assert.equal(line.x, 60);
});

test("once the panels are sized, short text drops towards its speaker", () => {
  // One panel needs lots of headroom; the other only has a few words, and
  // its speaker's mouth is 10px into its art.
  const spec = { ...artRightBlocked, drop: true, speakerY: 10, keepGap: 5 };
  const result = fitPanels([artRightBlocked, spec], ["word ".repeat(40), "aaaa"], {
    ...opts(),
    cellWidth: 100,
    padding: 0,
  });
  assert.equal(result.fits, true);
  const panel = result.panels[1];
  const [line] = result.layouts[1].lines;
  const mouth = panel.artTop + 10 * panel.scale;
  assert.ok(line.y + line.height <= mouth - 5 + 1e-9, `ends at ${line.y + line.height}, mouth at ${mouth}`);
  assert.ok(line.y > 20, "it has dropped");
});

test("a panel wider than its art keeps the art at the scale it's given", () => {
  const panel = makePanel(artRightBlocked, 150, 100, 0, 1);
  assert.equal(panel.scale, 1);
  assert.equal(panel.artTop, 50);
  // The art's free rows reach past its original width; beyond them is the
  // rest of the panel.
  assert.deepEqual(freeIntervals(panel, 60, 70, 0), [[0, 40]]);
});

test("with artWidth set, wider cells give text more room beside the art", () => {
  // The art is 100 wide and free on the left, with its free rows running
  // on past it, as art extended to the right does.
  const spec = {
    width: 100,
    height: 50,
    free: Array.from({ length: 50 }, () => [[0, 40], [60, 300]]),
  };
  const options = { ...opts(), padding: 0, artWidth: 100 };
  const narrow = fitPanels([spec], ["aaaa ".repeat(20)], { ...options, cellWidth: 100 });
  const wide = fitPanels([spec], ["aaaa ".repeat(20)], { ...options, cellWidth: 200 });
  assert.equal(wide.panels[0].scale, 1);
  assert.ok(wide.cellHeight < narrow.cellHeight, `${wide.cellHeight} vs ${narrow.cellHeight}`);
});

test("cells widen in proportion as they grow taller", () => {
  // Fitting the text takes area 20000 above art 100x100, at any width.
  const heightAt = (w) => 100 + 20000 / w;
  const fitAt = (w) => ({ cellHeight: heightAt(w), fits: true });
  const { width, result } = chooseWidth(fitAt, { minWidth: 100, maxWidth: 400, aspect: 1, step: 1 });
  // Square cells: w = 100 + 20000 / w, so w is about 200 (or a little
  // less, where that's hardly any bigger).
  assert.ok(width >= 196 && width <= 200, `width ${width}`);
  assert.equal(result.cellHeight, heightAt(width));
});

test("cells keep their width when the text fits in proportion", () => {
  const fitAt = () => ({ cellHeight: 90, fits: true });
  assert.equal(chooseWidth(fitAt, { minWidth: 100, maxWidth: 400, aspect: 1, step: 1 }).width, 100);
});

test("cells widen no further than the widest they can be", () => {
  // Wider is always a little shorter, but never in proportion.
  const fitAt = (w) => ({ cellHeight: 1000 + 40000 / w, fits: true });
  const { width } = chooseWidth(fitAt, { minWidth: 100, maxWidth: 400, aspect: 1, step: 1 });
  // As wide as it can be, or near enough to make no real difference.
  assert.ok(width > 350 && width <= 400, `width ${width}`);
});

test("art extended both ways is shown centred on the original", () => {
  // 100 wide, extended 20 to the left and 20 to the right; shown 120 wide.
  assert.deepEqual(artWindow({ width: 100, left: 20, extendedWidth: 140 }, 120), [10, 130]);
});

test("art extended only to the right is shown from its left edge", () => {
  assert.deepEqual(artWindow({ width: 100, extendedWidth: 140 }, 120), [0, 120]);
});

test("art shown wider than one side's extension takes the rest from the other", () => {
  // Only 5 to spare on the right, so the rest comes from the left.
  assert.deepEqual(artWindow({ width: 100, left: 30, extendedWidth: 135 }, 130), [5, 135]);
});

test("art that ends in plain background is centred however wide it's shown", () => {
  const meta = { width: 100, left: 20, extendedWidth: 140, openLeft: true, openRight: true };
  assert.deepEqual(artWindow(meta, 300), [-80, 220]);
});

test("art open on the right only is shown from as far left as it goes", () => {
  const meta = { width: 100, extendedWidth: 140, openRight: true };
  assert.deepEqual(artWindow(meta, 300), [0, 300]);
});

test("free space reaching the end of art that ends in background goes on past it", () => {
  const rows = [[[0, 40], [60, 140]], [[0, 140]], [[10, 30]]];
  assert.deepEqual(openBeyond(rows, 140), [[[0, 40], [60, Infinity]], [[0, Infinity]], [[10, 30]]]);
});

test("cells widen no further than it takes to save height", () => {
  // The text needs 250 of height however wide the cell is beyond 150: as
  // with lines that don't wrap. Square cells would be 250 wide.
  const fitAt = (w) => ({ cellHeight: w < 150 ? 1000 : 250, fits: true });
  const { width } = chooseWidth(fitAt, { minWidth: 100, maxWidth: 400, aspect: 1, step: 1 });
  assert.equal(width, 150);
});

test("free space reaching the last whole grid cell of the art counts as reaching its edge", () => {
  // Art 597.5 grid cells wide, rounded to 598; the grid holds 597 of them.
  assert.deepEqual(openBeyond([[[10, 597]]], 598), [[[10, Infinity]]]);
});

test("nothing is lettered to the right of a reserved area, which would be read first", () => {
  // Another character's balloon in the middle of the rows y = 40..60.
  const spec = { ...artRightBlocked, reserved: [[40, -60, 60, -40]] };
  const panel = makePanel(spec, 100, 150, 0);
  assert.deepEqual(freeIntervals(panel, 45, 55, 0), [[0, 40]]);
});

test("dropping stops before a line would be pushed aside by the art", () => {
  // Art on the left from y = 50 of the art down, sloping steeply out to
  // the right like the top of a head.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 50 ? [[0, 200]] : [[(y - 50) * 6, 200]])),
  };
  const panel = makePanel(spec, 200, 300, 0);
  // A long line above a short one: lower down, the short one would be
  // pushed further aside than the long one can follow.
  const result = layoutText(panel, "a".repeat(20) + "\nbb", opts({ align: "left", drop: true }));
  assert.ok(result.lines[0].y > 100, "it has dropped");
  const [first, last] = result.lines.map((l) => l.x);
  assert.equal(last, first, "the lines keep a common left edge");
});

test("a balloon's text goes in the middle of its room, if it still spans its speaker", () => {
  const panel = panelWithHeadroom(200);
  // 60 wide in a 100 wide panel; the speaker is at x = 30.
  const result = layoutText(panel, "aaaaaaaaaaaa", opts({ align: "left", centreOn: 30 }));
  assert.equal(result.lines[0].x, 20);
});

test("a balloon's text stays as near its speaker as it can if it can't span them", () => {
  // Art down the left side; the speaker is in it, at x = 30.
  const spec = { width: 200, height: 100, free: Array.from({ length: 100 }, () => [[60, 200]]) };
  const panel = makePanel(spec, 200, 100, 0);
  const result = layoutText(panel, "aaaa", opts({ align: "left", centreOn: 30 }));
  assert.equal(result.lines[0].x, 60);
});

test("a panel seen from part way into its art has everything shifted to match", () => {
  const meta = {
    width: 100,
    free: [[[0, 40], [60, Infinity]]],
    open: [[[10, 20]]],
    speakers: { dad: [50, 5] },
    calvinColumn: [70, 90, 30],
  };
  const view = shiftedView(meta, 10);
  assert.deepEqual(view.free, [[[-10, 30], [50, Infinity]]]);
  assert.deepEqual(view.open, [[[0, 10]]]);
  assert.deepEqual(view.speakers, { dad: [40, 5] });
  assert.deepEqual(view.calvinColumn, [60, 80, 30]);
  assert.equal(view.start, 10);
  assert.equal(shiftedView(meta, 0).start, 0);
});

test("lines are no longer than maxLineWidth, however wide the space", () => {
  const panel = panelWithHeadroom(200);
  const result = layoutText(panel, "aaaa bbbb cccc dddd eeee ffff", opts({ align: "left", maxLineWidth: 50 }));
  assert.ok(result.lines.length > 1);
  for (const line of result.lines) assert.ok(line.width <= 50, `${line.text} is ${line.width} wide`);
});

test("a word longer than maxLineWidth gets a line to itself where there's space for it", () => {
  const panel = panelWithHeadroom(200);
  const result = layoutText(panel, "aaaa " + "x".repeat(14) + " bbbb", opts({ align: "left", maxLineWidth: 50 }));
  assert.equal(result.fits, true);
  assert.deepEqual(result.lines.map((l) => l.text), ["aaaa", "x".repeat(14), "bbbb"]);
});

test("a balloon that floats free drops only as far as it still floats free", () => {
  // Art on the left (a head) from y = 50 of the art down; a speaker at x = 30.
  const spec = {
    width: 200,
    height: 100,
    free: Array.from({ length: 100 }, (_, y) => (y < 50 ? [[0, 200]] : [[60, 200]])),
  };
  const panel = makePanel(spec, 200, 300, 0);
  const options = opts({ align: "left", drop: true, centreOn: 30, floatGap: 20 });
  // 130 wide: beside the head it would come within 10 of the right side.
  const wide = layoutText(panel, "a".repeat(26), options);
  assert.ok(wide.lines[0].y + wide.lines[0].height <= 250, "it stays above the head");
  // 40 wide: there's room for it to float beside the head.
  const narrow = layoutText(panel, "a".repeat(8), options);
  assert.ok(narrow.lines[0].y > 250, "it drops beside the head");
});

test("lines before a word longer than maxLineWidth are still balanced", () => {
  const panel = panelWithHeadroom(200);
  // Filling each line would leave "e" on its own before the long word.
  const text = "aaaa bbbb cccc dddd e " + "x".repeat(14);
  const result = layoutText(panel, text, opts({ align: "left", maxLineWidth: 50 }));
  const texts = result.lines.map((l) => l.text);
  assert.equal(texts[texts.length - 1], "x".repeat(14));
  assert.ok(!texts.includes("e"), texts.join(" / "));
});

test("a balloon can centre a little way past its speaker, with its tail coming down to their side", () => {
  const panel = panelWithHeadroom(200);
  // 60 wide in a 100 wide panel; the speaker is at x = 10, and the text
  // may start up to 15 past them.
  const result = layoutText(panel, "aaaaaaaaaaaa", opts({ align: "left", centreOn: 10, centreSlack: 15 }));
  assert.equal(result.lines[0].x, 20);
});

test("panels can be laid out at a given cell height", () => {
  const options = { ...opts(), cellWidth: 100, padding: 0 };
  const fixed = fitPanels([artRightBlocked], ["aaaa"], { ...options, cellHeight: 120 });
  assert.equal(fixed.cellHeight, 120);
  assert.equal(fixed.fits, true);
  const tooShort = fitPanels([artRightBlocked], ["word ".repeat(40)], { ...options, cellHeight: 50 });
  assert.equal(tooShort.fits, false);
});
