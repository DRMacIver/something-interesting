import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { DEFAULTS, drawComic, makeFontString } from "../js/comic.js";
import { openBeyond } from "../js/layout.js";
import { samples } from "../js/unicode-samples.js";

test('loaded variation fonts cannot replace ordinary Han or math fallback',()=>{
  const families=['Dad CJK Variants','Dad Math Variants','Dad Egyptian Variants','Ordinary Script'];
  const ordinary=makeFontString(24,families);
  assert.equal(ordinary,'24px "Dad Lettering", "Ordinary Script", cursive');
  for(const family of ['Dad CJK Variants','Dad Math Variants']){
    const selected=makeFontString(24,families,'text',family);
    assert.ok(selected.startsWith(`24px "${family}",`));
    assert.ok(!selected.includes(family==='Dad CJK Variants'?'Dad Math Variants':'Dad CJK Variants'));
    assert.ok(!selected.includes('Dad Egyptian Variants'));
  }
  assert.ok(makeFontString(24,families,'egyptian-variant').startsWith('24px "Dad Egyptian Variants",'));
});

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

test('the adventure sampler tail descends above Dad instead of leaving the far panel edge',()=>{
 for(const units of [text=>[...text].length,text=>text.length]){
  const ctx=new Proxy({font:'10px x',measureText(text){
    const size=parseFloat(this.font);
    return {width:units(text)*size*.55,actualBoundingBoxAscent:size*.7,actualBoundingBoxDescent:0};
  }},{get:(t,k)=>k in t?t[k]:()=>{},set:(t,k,v)=>(t[k]=v,true)});
  const result=drawComic({getContext:()=>ctx},comic,samples.find(s=>s.id==='custom-adventure').texts);
  const panel=result.panels[2];const speech=panel.speeches.find(s=>s.who==='dad');
  const tail=speech.tail??speech.stroke;assert.ok(tail);
  const start=tail.base[0].map((v,i)=>(v+tail.base[1][i])/2);
  const direction=[tail.tip[0]-tail.bend[0],tail.tip[1]-tail.bend[1]];
  assert.ok(start[0]>panel.panel.width*.1,'tail starts above the head, clear of the left border');
  assert.ok(Math.abs(direction[0])/direction[1]<Math.tan(Math.PI/9),'arrives within 20 degrees of vertical');
 }
});

const wall = (sentence, n) => Array.from({ length: n }, () => sentence).join("\n");

test("short opening balloons float clear of the top border",()=>{
  for(const greeting of ['Hello!','Hi.','Καλημέρα!']){
    const report=drawComic(canvas(),comic,[greeting,'A short explanation.','Another point.','Why?']);
    assert.ok(report.fits);
    const first=report.panels[0];
    const speech=first.speeches.find(s=>s.who==='dad');
    assert.ok(Math.min(...speech.outline.map(p=>p[1]))>0,greeting);
    assert.ok(Math.max(...speech.outline.map(p=>p[0]))<first.panel.width,greeting);
  }
});

test("the renderer preserves case-sensitive Unicode text", () => {
  const sample = "α ≠ Α, ß ≠ SS, ı ≠ I, 𝑥² ≥ 0";
  const report = drawComic(canvas(), comic, [sample, "", "", ""]);
  const speech = report.panels[0].speeches.find((s) => s.who === "dad");
  assert.equal(speech.lines.map((line) => line.text).join(" "), sample);
});

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

test("reframing keeps Dad's whole head visible even with no speech", () => {
  const cluster = "👨\u200d".repeat(40) + "👨";
  const scenarios = [
    ["HELLO.", "", "", ""],
    ["HELLO.", "", "", "HELLO."],
    ["HELLO.", "", "", cluster],
    [cluster, "", "", "HELLO."],
  ];
  for (const texts of scenarios) {
    const report = drawComic(canvas(), comic, texts);
    const { panel, meta } = report.panels[2];
    assert.ok(report.fits);
    assert.ok(meta.height > assets.panels[2].height, "still reveals available lower artwork");
    for (const [x0, y0, x1, y1] of meta.keepVisible) {
      assert.ok(x0 * panel.scale >= 0 && x1 * panel.scale <= panel.width);
      assert.ok(panel.artTop + y0 * panel.scale >= 0, "hair and headroom stay inside frame");
      assert.ok(panel.artTop + y1 * panel.scale <= panel.height, "chin stays inside frame");
    }
  }
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

test("Calvin's indivisible wide cluster is preserved and fits his opening", () => {
  const cluster = "W" + "\u0301".repeat(150);
  const report = drawComic(canvas(), comic, ["HELLO", "", "", cluster]);
  const reply = report.panels.flatMap(p => p.speeches).find(s => s.who === "calvin");
  assert.equal(report.fits, true);
  assert.equal(reply.lines.map(l => l.text).join(""), cluster);
  assert.ok(reply.fontSize < report.fontSize);
  for (const line of reply.lines) {
    assert.ok(line.width <= line.interval[1] - line.interval[0] + 1e-6);
  }
});

test("Dad's oversized cluster fits without reducing surrounding lettering", () => {
  const cluster = "W" + "\u0301".repeat(150);
  const started = performance.now();
  const report = drawComic(canvas(), comic, [cluster + "\nHELLO", "", "", ""]);
  assert.ok(performance.now() - started < 3000);
  assert.equal(report.fits, true);
  const lines = report.panels[0].speeches.find(s => s.who === "dad").lines;
  assert.equal(lines[0].text, cluster);
  assert.ok(lines[0].fontSize < report.fontSize);
  assert.equal(lines[1].text, "HELLO");
  assert.equal(lines[1].fontSize, report.fontSize);
  for (const line of lines) assert.ok(line.width <= line.interval[1] - line.interval[0] + 1e-6);
});
