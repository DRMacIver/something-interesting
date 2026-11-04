import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {requiresFormatGlyph,fontMayIgnore,nativeVariationFont} from '../js/font-variations.js';
import {requiredFonts,contains} from '../js/fonts.js';
import {formatFontSpans} from '../js/format-fonts.js';
import {fontRuns,needsEmojiRouting} from '../js/emoji-routing.js';
import {createTextMeasurer} from '../js/text-metrics.js';
import {makeFontString} from '../js/comic.js';

const points=fs.readFileSync(new URL('../data/unicode/18.0.0/PropList.txt',import.meta.url),'utf8').split('\n').flatMap(row=>{
  const [range,property]=row.split('#')[0].split(';').map(s=>s.trim());
  if(property!=='Prepended_Concatenation_Mark')return [];
  const [a,b=a]=range.split('..').map(s=>parseInt(s,16));
  return Array.from({length:b-a+1},(_,i)=>a+i);
});

test('all pinned font-dependent format marks load a font that contains their real glyph',()=>{
  assert.equal(points.length,13);
  for(const cp of points){
    assert.ok(requiresFormatGlyph(cp));
    assert.equal(fontMayIgnore([[cp,cp]],cp),false);
    const selected=requiredFonts([String.fromCodePoint(cp)]);
    assert.deepEqual(selected.missing,[]);
    assert.ok(selected.fonts.some(f=>contains(f.ranges,cp)),cp.toString(16));
    assert.ok(!selected.fonts.some(f=>f.family==='Dad Grid'));
  }
  for(const cp of [0x61c,0x200d,0x2067])assert.equal(requiresFormatGlyph(cp),false);
  assert.deepEqual(requiredFonts(['\u061c']).fonts,[],'an empty joining repertoire must not select an arbitrary font');
});

test('format-glyph requirements cannot be hidden by a behavioural range or native variation',()=>{
  const variant={family:'Variant',ranges:[[48,48]],nativeVariations:{65024:[[48,48]]}};
  const inventory={baseRanges:[[32,126]],behaviouralRanges:[[0x600,0x600],[0xfe00,0xfe0f]],fonts:[variant]};
  assert.deepEqual(requiredFonts(['\u0600'],inventory).missing,[0x600]);
  assert.equal(nativeVariationFont('\u06000\ufe00',inventory),undefined);
  assert.equal(nativeVariationFont('0\ufe00',inventory),variant);
});

test('prefixed signs and their whole number or abbreviation paint with one native font',()=>{
  for(const text of ['\u0600123','\u06012026','\u0602456','\u0603789','\u06042026','\u0605ⲁⲃ',
    '\u06dd١٢٣','\u06dd۱۲۳','\u0890123','\u0891456','\u08e2١٢٣','\u070fܒܓܕ','ܒ\u070fܓܕ',
    '\u{110bd}१२३','\u{110cd}१२३']){
    const [span]=formatFontSpans(text);
    assert.ok(span,text);
    assert.equal(span.start,0);assert.equal(span.end,text.length);
    assert.ok([...text].every(c=>contains(span.font.ranges,c.codePointAt(0))));
    assert.ok(requiredFonts([text]).fonts.some(f=>f.family===span.font.family));
    assert.equal(needsEmojiRouting(text),true);
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'text',fontFamily:span.font.family}]);
    const ctx={measureText(){return {width:20,actualBoundingBoxAscent:15,actualBoundingBoxDescent:3};}};
    const measure=createTextMeasurer(ctx,(size,policy,family)=>makeFontString(size,[span.font.family],policy,family));
    for(const paragraph of [text,'A '+text+' X','ع '+text+' ب']){
      const painted=measure.forParagraph(paragraph).at(0).ink(paragraph,20).runs;
      const native=painted.find(r=>r.text.includes(text));
      assert.equal(native?.fontFamily,span.font.family,paragraph);
      assert.equal(native.font.split('"')[1],span.font.family);
    }
    const surrounded=fontRuns('A '+text+' X');
    assert.equal(surrounded.find(r=>r.fontFamily)?.text,text,'do not absorb adjacent prose');
  }
  assert.deepEqual(formatFontSpans('123 ordinary prose'),[]);
});

test('mixed Arabic and European digit fields remain complete after paragraph reordering',()=>{
  const text='\u06dd١٢٣ \u0890123 \u0891456',ctx={measureText(){return {width:20};}};
  const families=requiredFonts([text]).fonts.map(f=>f.family);
  const measure=createTextMeasurer(ctx,(s,p,f)=>makeFontString(s,families,p,f));
  const runs=measure.forParagraph(text).at(0).ink(text,20).runs;
  for(const field of text.split(' '))assert.ok(runs.some(r=>r.text.includes(field)&&r.fontFamily),field);
  assert.equal(runs.map(r=>r.text).join(''),text);
});
