import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { DEFAULTS, drawComic } from "../js/comic.js";
import { openBeyond } from "../js/layout.js";

// The comic as loadComic gives it, without the images, drawn on a canvas
// that measures every character as 0.55 of the font size.
const assets = JSON.parse(readFileSync(new URL("../assets/panels.json", import.meta.url), "utf8"));
for (const meta of assets.panels) {
  if (!meta.openRight) continue;
  if (meta.free) meta.free = openBeyond(meta.free, meta.extendedWidth);
  if (meta.open) meta.open = openBeyond(meta.open, meta.extendedWidth);
}
const comic = { assets, images: assets.panels.map(() => ({ width: 1, height: 1 })), signature: {} };
const context = new Proxy(
  {
    font: "10px x",
    measureText(text) {
      const size = parseFloat(this.font);
      return { width: text.length * size * 0.55, actualBoundingBoxAscent: size * 0.7 };
    },
  },
  { get: (t, k) => (k in t ? t[k] : () => {}), set: (t, k, v) => ((t[k] = v), true) },
);
const canvas = () => ({ getContext: () => context, width: 0, height: 0 });

const wall = (sentence, n) => Array.from({ length: n }, () => sentence).join("\n");

test("a long speech gets a balloon after all when the panels are big enough for one", () => {
  // Panel 2 makes the panels huge; panel 3's few lines would be loose on
  // their own, but there's room for a balloon.
  const texts = [...DEFAULTS];
  texts[1] = wall("Yellow, black. Yellow, black.", 40);
  const report = drawComic(canvas(), comic, texts);
  assert.equal(report.panels[2].speech, "balloon");
});

test("a speech that fills its panel is lettered loose", () => {
  const texts = [...DEFAULTS];
  texts[2] = wall("Yellow, black. Yellow, black.", 40);
  const report = drawComic(canvas(), comic, texts);
  assert.equal(report.panels[2].speech, "loose");
});

test("a panel with room to spare shows more of its scene below", () => {
  const texts = [...DEFAULTS];
  texts[1] = wall("Yellow, black. Yellow, black.", 40);
  const report = drawComic(canvas(), comic, texts);
  const { meta } = report.panels[2];
  assert.ok(meta.height > assets.panels[2].height, `shows ${meta.height} of ${meta.extendedHeight}`);
});

test("a panel with no room to spare shows only the original art", () => {
  // Panel 3's text is what sizes the panels, so it fills its panel.
  const texts = [...DEFAULTS];
  texts[2] = wall("Yellow, black. Yellow, black.", 12);
  const report = drawComic(canvas(), comic, texts);
  assert.equal(report.panels[2].meta.height, assets.panels[2].height);
});

test("a whole film script in one box still makes a comic browsers can draw", () => {
  // About 9,000 words in short lines, like the Bee Movie script pasted
  // into one box.
  const words = "according to all known laws of aviation there is no way a bee should be able to fly".split(" ");
  const lines = [];
  for (let n = 0; n < 9000; ) {
    const k = 3 + ((lines.length * 7) % 12);
    lines.push(Array.from({ length: k }, (_, i) => words[(n + i) % words.length]).join(" "));
    n += k;
  }
  const texts = [...DEFAULTS];
  texts[1] = lines.join("\n");
  const target = canvas();
  const started = performance.now();
  const report = drawComic(target, comic, texts);
  assert.ok(performance.now() - started < 10000, "it doesn't hang the page");
  assert.equal(report.fits, true);
  // Only so much of it is lettered, ending with an ellipsis.
  assert.deepEqual(report.clipped, [1]);
  const lettered = report.panels[1].speeches.find((s) => s.who === "dad").lines;
  assert.ok(lettered[lettered.length - 1].text.endsWith("…"));
  // Safari's limits, the strictest: 16,384 pixels a side, 16.7 megapixels.
  assert.ok(target.width <= 16384 && target.height <= 16384, `${target.width} x ${target.height}`);
  assert.ok(target.width * target.height <= 16777216, `${target.width} x ${target.height}`);
});

test("a lot of text is lettered smaller, down to a limit", () => {
  const normal = drawComic(canvas(), comic, DEFAULTS).cap;
  const some = [...DEFAULTS];
  some[1] = "Yellow, black. Yellow, black. ".repeat(20);
  const lots = [...DEFAULTS];
  lots[1] = "Yellow, black. Yellow, black. ".repeat(150);
  const smaller = drawComic(canvas(), comic, some).cap;
  const smallest = drawComic(canvas(), comic, lots).cap;
  assert.ok(smaller < normal, `${smaller} vs ${normal}`);
  assert.ok(smallest < smaller, `${smallest} vs ${smaller}`);
  assert.ok(smallest >= 0.6 * normal - 1e-9, `${smallest} vs ${normal}`);
});

test("ordinary text is lettered at the original size", () => {
  const texts = [...DEFAULTS];
  texts[1] = "Every point on the record goes round once a minute but the ones near the edge have much further to go.";
  assert.equal(drawComic(canvas(), comic, texts).cap, drawComic(canvas(), comic, DEFAULTS).cap);
});
