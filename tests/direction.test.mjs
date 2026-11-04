import test from 'node:test';
import assert from 'node:assert/strict';
import { paragraphDirection, bidiParagraph } from '../js/direction.js';
import { createTextMeasurer } from '../js/text-metrics.js';
import { layoutColumn } from '../js/layout.js';

test('paragraph direction uses the first strong character outside nested isolates', () => {
  for (const text of ['123 مرحبا', '... שלום', '\u200fABC', '\u2066ABC\u2069مرحبا', '\u2066X\u2067ع\u2069\u2069שלום']) assert.equal(paragraphDirection(text), 'rtl', text);
  for (const text of ['123 abc مرحبا', '123!', '\u2067مرحبا\u2069ABC', '\u2067مرحبا', '\nשלום']) assert.equal(paragraphDirection(text), 'ltr', text);
});

test('wrapped lines retain their paragraph direction, including lines beginning with Latin', () => {
  const seen = [];
  const ctx = { measureText(text) { seen.push([text, this.direction]); return {width: text.replace(/[\u202a-\u202e]/gu, "").length}; } };
  const measure = createTextMeasurer(ctx, size => `${size}px Font`);
  const {lines} = layoutColumn('שלום abc def ghi\nEnglish שלום', {measure, fontSize: 1, lineHeight: 1, width: 8});
  const first = lines.filter(l => l.paragraph === 1);
  assert.ok(first.length > 1);
  assert.ok(first.every(l => l.direction === 'rtl'));
  assert.ok(lines.filter(l => l.paragraph === 2).every(l => l.direction === 'ltr'));
  assert.ok(seen.some(([text, dir]) => text.startsWith('\u202dabc') && dir === 'ltr'));
  measure.ink('abc', 1, 'ltr');
  measure.ink('abc', 1, 'rtl');
  assert.ok(seen.some(([text, dir]) => text === 'abc' && dir === 'ltr'));
  assert.ok(seen.some(([text, dir]) => text === 'abc' && dir === 'rtl'));
});

test('wrapped overrides, isolates and weak numbers retain paragraph context', () => {
  const override = bidiParagraph('Hello \u202eabc def ghi\u202c end');
  assert.deepEqual(override.runs(11, 'def').map(r => [r.text,r.direction]), [['def','rtl']]);
  const isolate = bidiParagraph('Hello \u2068אבג 123 xyz\u2069 end');
  assert.deepEqual(isolate.runs(11, '123 xyz').map(r => [r.text,r.direction]), [['xyz','ltr'], [' ','rtl'], ['123','ltr']]);
  const number = bidiParagraph('Hello العربية 123, 456 end');
  assert.deepEqual(number.runs(14, '123, 456').map(r => [r.text,r.direction]), [['456','ltr'], [', ','rtl'], ['123','ltr']]);
});

test('supplementary RTL letters, marks, joining and discretionary hyphens retain scalar mappings', () => {
  const text = '\u{1e900}\u{1e901} 12 אב\u200dג\u05b0';
  const p = bidiParagraph(text);
  assert.equal(p.direction, 'rtl');
  assert.deepEqual(p.runs(5, '12 אב\u200dג\u05b0').map(r => r.text), [' אב\u200dג\u05b0','12']);
  const shy = bidiParagraph('שלום abc\u00addef');
  assert.deepEqual(shy.runs(5, 'abcdef').map(r => r.text), ['abcdef']);
  assert.equal(shy.runs(5, 'abc-').map(r => r.text).join(''), 'abc-');
});

test('wrapping and balancing use source offsets, preserve text, and measure resolved runs', () => {
  const text = 'START \u202eabc def ghi jkl mno pqr\u202c END';
  const ctx = {measureText(text) {return {width: text.replace(/[\u202a-\u202e]/gu,'').length};}};
  const measure = createTextMeasurer(ctx, size => `${size}px Font`);
  const {lines} = layoutColumn(text, {measure,fontSize:1,lineHeight:1,width:9});
  assert.ok(lines.length >= 4);
  assert.equal(lines.flatMap(l => l.units).join(''), text);
  const p = bidiParagraph(text);
  for (const line of lines) {
    assert.deepEqual(line.ink.runs.map(({text,direction}) => [text,direction]), p.runs(line.sourceOffset,line.text).map(({text,direction}) => [text,direction]));
    assert.ok(line.width <= 9);
  }
  assert.ok(lines.some(line => line.sourceOffset > text.indexOf('\u202e') && line.sourceOffset < text.indexOf('\u202c') && line.ink.runs.some(r => r.direction === 'rtl')));
});

test('trailing joining controls remain in their shaping run after L1 reset', () => {
  const p = bidiParagraph('English العربية\u200d');
  const runs = p.runs(8, 'العربية\u200d');
  assert.equal(runs.length, 1);
  assert.equal(runs[0].text, 'العربية\u200d');
  assert.equal(runs[0].direction, 'rtl');
});

test('Garay keeps RTL letters and marks with LTR AN digit runs',()=>{
  const letters=String.fromCodePoint(0x10d53,0x10d69,0x10d73);
  const digits=String.fromCodePoint(0x10d41,0x10d42,0x10d43);
  const text=letters+' '+digits;
  const p=bidiParagraph(text);
  assert.equal(p.direction,'rtl');
  assert.deepEqual(p.runs(0,text).map(r=>[r.text,r.direction]),[[digits,'ltr'],[letters+' ','rtl']]);
});
