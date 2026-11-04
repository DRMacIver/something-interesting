import test from 'node:test';
import assert from 'node:assert/strict';
import emoji from '../js/emoji-manifest.js';
import {fontRuns,emojiPolicy,emojiStrokeRatio,emojiScaleFactor} from '../js/emoji-routing.js';
import {createTextMeasurer} from '../js/text-metrics.js';
import {requiredFonts,createFontLoader} from '../js/fonts.js';
import {makeFontString} from '../js/comic.js';
const points=new Set(emoji.customArtwork.map(r=>String.fromCodePoint(parseInt(r.codepoint.slice(2),16))));
const forms=emoji.sequences.filter(text=>points.has([...text][0]) && ([...text].length===1 || [...text].length<=2 && /[\ufe0e\ufe0f]$/.test(text)));

test('the upside-down tiger keeps lighter optical ink in either direction',()=>{
  assert.equal(emojiStrokeRatio('🐅'),.002);
  assert.equal(emojiStrokeRatio('\u202e🐅\u202c'),.002);
  assert.equal(emojiStrokeRatio('🐯'),.018);
  assert.equal(emojiScaleFactor('🐅'),1.4);
  assert.equal(emojiScaleFactor('\u202e🐯\u202c'),1.4);
  assert.equal(emojiScaleFactor('😀'),1.4);
  const ctx={measureText(){return {width:20,actualBoundingBoxAscent:15,actualBoundingBoxDescent:3};}};
  const measure=createTextMeasurer(ctx,(size)=>`${size}px Font`);
  assert.equal(measure.ink('🐅',20).runs[0].strokeWidth,28*.002);
  assert.equal(measure.ink('🐅',20).runs[0].fontSize,28);
  assert.equal(measure.ink('🐯',20).runs[0].fontSize,28);
});

test('all sixteen drawings and their registered variants use the main emoji font',()=>{
  assert.equal(points.size,16);
  for(const text of forms){
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),['Dad Emoji']);
  }
});

test('custom art does not introduce companion routing for compound clusters',()=>{
  for(const text of ['🧑‍🚀','🧑🏽‍🚀','🐯\u0301','🦖‍🐅','☃️\u0301']){
    assert.ok(fontRuns(text).every(r=>!r.fontFamily),text);
  }
  const runs=fontRuns('A 🐯 😀 🚀 B');
  assert.equal(runs.map(r=>r.text).join(''),'A 🐯 😀 🚀 B');
});

test('one emoji font and its existing ink companion load for the new artwork',async()=>{
  assert.ok(makeFontString(24,['Dad Emoji'],'custom').startsWith('24px "Dad Emoji"'));
  assert.ok(!makeFontString(24,['Dad Emoji'],'text').includes('Dad Emoji'));
  const added=[];
  class Face{constructor(family){this.family=family;}async load(){return this;}}
  const loaded=await createFontLoader({add:f=>added.push(f.family)},Face)(['🐯']);
  assert.deepEqual(loaded.families,['Dad Emoji']);
  assert.deepEqual(added.sort(),['Dad Emoji','Dad Emoji Ink'].sort());
});
