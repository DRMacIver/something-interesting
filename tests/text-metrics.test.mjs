import { test } from "node:test";
import assert from "node:assert/strict";
import { createTextMeasurer, textScale } from "../js/text-metrics.js";
import { layoutColumn } from "../js/layout.js";

const context = () => ({
  measureText(text) {
    const size = parseFloat(this.font);
    const stacked = text.includes("\u0301");
    return { width: Array.from(text).filter(c => c !== "\u0301").length * size * 0.5,
      actualBoundingBoxAscent: size * (stacked ? 3 : 0.7),
      actualBoundingBoxDescent: size * (stacked ? 2 : 0),
      actualBoundingBoxLeft: stacked ? size * 0.3 : 0,
      actualBoundingBoxRight: Array.from(text).filter(c => c !== "\u0301").length * size * 0.5 + (stacked ? size * 0.4 : 0) };
  },
});

test("line boxes reserve both advance and left/right overhanging ink", () => {
  const measure = createTextMeasurer(context(), s => `${s}px Font`);
  assert.equal(measure("X\u0301", 10), 12);
  assert.equal(measure.ink("X\u0301", 10).drawOffset, 3);
});

test("stacked marks stay inside every line after wrapping and balancing", () => {
  const measure = createTextMeasurer(context(), s => `${s}px Font`);
  const result = layoutColumn("ONE TWO X\u0301 THREE FOUR", { measure, fontSize: 10, width: 35 });
  assert.ok(result.lines.length > 1);
  for (let i = 0; i < result.lines.length; i++) {
    const line = result.lines[i];
    const ink = measure.ink(line.text, 10);
    assert.deepEqual(line.ink, ink);
    assert.ok(line.baseline >= ink.ascent);
    assert.ok(line.baseline + ink.descent <= line.height);
    assert.ok(line.width <= 35);
    if (i) assert.ok(result.lines[i-1].y + result.lines[i-1].height <= line.y);
  }
  assert.equal(result.height, result.lines.at(-1).y + result.lines.at(-1).height);
});

test("plain capitals retain the original leading and baseline", () => {
  const measure = createTextMeasurer(context(), s => `${s}px Font`);
  assert.deepEqual(measure.envelope("PLAIN", 10, 1.2), { height: 12, baseline: 9.5, blankHeight: 12 });
});

test("composed Egyptian signs get a readable scale with matching ink and layout", () => {
  const group = '𓀀\u{13430}𓀁';
  assert.equal(textScale(group), 2);
  assert.equal(textScale('𓀀𓀁'), 1);
  assert.equal(textScale('ordinary text'), 1);
  const measure = createTextMeasurer(context(), s => `${s}px Font`);
  const result = layoutColumn(group + ' ' + group, { measure, fontSize: 10, width: 40 });
  assert.equal(result.fits, true);
  assert.equal(result.lines.length, 2);
  for (const line of result.lines) {
    assert.equal(line.fontSize, 20);
    assert.equal(line.ink.fontSize, 20);
    assert.ok(line.baseline >= line.ink.ascent);
    assert.ok(line.baseline + line.ink.descent <= line.height);
    assert.ok(line.width <= 40);
  }
});

test("custom emoji have room to read in mixed dialogue and wrapped lines", () => {
  const measure = createTextMeasurer(context(), (s,p) => `${s}px ${p}`);
  const mixed = measure.ink('A 😀 B', 20);
  const emoji = mixed.runs.find(r => r.emojiPolicy === 'custom');
  assert.equal(emoji.fontSize, 28);
  assert.ok(mixed.runs.filter(r => r.emojiPolicy === 'text').every(r => r.fontSize === 20));
  const layout = layoutColumn('A 😀 B 😀 C', {measure,fontSize:20,width:65});
  assert.ok(layout.lines.length > 1);
  for (const line of layout.lines) {
    assert.ok(line.width <= 65);
    assert.ok(line.baseline >= line.ink.ascent);
    assert.ok(line.baseline + line.ink.descent <= line.height);
    for (const run of line.ink.runs ?? []) {
      if (run.emojiPolicy === 'custom') assert.equal(run.fontSize,28);
    }
  }
});

test("each emoji ink centre follows the lettering rather than its font baseline", () => {
  const ctx = { measureText(text) {
    const size = parseFloat(this.font);
    const [a,d] = text.includes('🚲') ? [.9,-.2] : text.includes('❤') ? [.75,.05] : [.7,0];
    return {width:size,actualBoundingBoxAscent:a*size,actualBoundingBoxDescent:d*size,
      actualBoundingBoxLeft:0,actualBoundingBoxRight:size};
  }};
  const measure = createTextMeasurer(ctx,(s,p)=>`${s}px ${p}`);
  for (const text of ['A 🚲 B','A ❤️ B','A 🚲❤️ B']) {
    const metrics = measure.ink(text,20);
    const emojis = metrics.runs.filter(r=>r.emojiPolicy==='custom');
    assert.equal(emojis.length,text.includes('🚲❤️')?2:1);
    for (const emoji of emojis) {
      assert.equal(emoji.font,'28px custom');
      const own = ctx.measureText.call({font:emoji.font},emoji.drawText);
      const centre = (own.actualBoundingBoxDescent-own.actualBoundingBoxAscent)/2+emoji.baselineOffset;
      assert.ok(Math.abs(centre+7)<1e-8);
      assert.ok(metrics.descent>=Math.max(0,own.actualBoundingBoxDescent+emoji.baselineOffset));
    }
  }
});

test("taller native lettering uses the requested line height without adding Latin leading twice", () => {
  const ctx = {measureText(text) {const s=parseFloat(this.font);return {
    width:s, actualBoundingBoxAscent:!text.trim()?s*4:text==='H'?s*.7:s*.9,
    actualBoundingBoxDescent:!text.trim()?s*3:text==='H'?0:s*.1,
    actualBoundingBoxLeft:0,actualBoundingBoxRight:s};}};
  const measure=createTextMeasurer(ctx,s=>`${s}px Font`);
  const box=measure.envelope('가\n\n나',20,1.2);
  assert.ok(Math.abs(box.height-24)<1e-8);
  const one=layoutColumn('가\n나',{measure,fontSize:20,lineHeight:1.2,width:100});
  const blank=layoutColumn('가\n\n나',{measure,fontSize:20,lineHeight:1.2,width:100});
  assert.ok(Math.abs(blank.lines[1].y-one.lines[1].y-12)<1e-8);
});

test("paragraph gaps stay modest next to very tall combining marks", () => {
  const measure=createTextMeasurer(context(),s=>`${s}px Font`);
  const one=layoutColumn('X́\nA',{measure,fontSize:10,width:100});
  const blank=layoutColumn('X́\n\nA',{measure,fontSize:10,width:100});
  assert.equal(blank.lines[1].y-one.lines[1].y,6);
});

test("a tall accented line does not give ordinary lines the same tall slot",()=>{
  const measure=createTextMeasurer(context(),s=>`${s}px Font`);
  const result=layoutColumn('X́\nPLAIN\nMORE',{measure,fontSize:10,width:100});
  assert.ok(result.lines[0].height>40);
  assert.equal(result.lines[1].height,12);
  assert.equal(result.lines[2].y-result.lines[1].y,12);
  for(let i=0;i<result.lines.length;i++){
    const line=result.lines[i];
    assert.ok(line.baseline>=line.ink.ascent);
    assert.ok(line.baseline+line.ink.descent<=line.height);
    if(i)assert.ok(line.y>=result.lines[i-1].y+result.lines[i-1].height);
  }
});

test("extra pen weight is confined to Greek/Cyrillic runs and reserved in their ink bounds",()=>{
  const measure=createTextMeasurer(context(),s=>`${s}px Font`);
  const runs=measure.ink('DAD ЖЖ αβ',20).runs;
  assert.ok(runs.filter(r=>/[Жα]/u.test(r.text)).every(r=>r.strokeWidth>0));
  assert.ok(runs.filter(r=>r.text.includes('DAD')).every(r=>r.strokeWidth===0));
  const native=measure.ink('α Ⰰ҃',20).runs;
  const glagolitic=native.find(r=>r.text.includes('Ⰰ'));
  assert.ok(glagolitic.text.includes('҃'));
  assert.equal(glagolitic.strokeWidth,0);
});
