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
