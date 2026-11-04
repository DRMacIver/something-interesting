import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { nativeVariationFont, variationPairs, supportsVariations, hasJoiningCharacters } from '../js/font-variations.js';
import { requiredFonts } from '../js/fonts.js';
import { fontRuns } from '../js/emoji-routing.js';
import { createTextMeasurer } from '../js/text-metrics.js';
import cjkVariants from '../js/cjk-variant-manifest.js';
import mathVariants from '../js/math-variant-manifest.js';
import markedCjkVariants from '../js/marked-cjk-variant-manifest.js';
import {parseEgyptian,requiresEgyptianLayout} from '../js/egyptian-layout.js';

test('CJK variants with foreign accents select a complete companion and retain native mark routing',()=>{
  assert.equal(markedCjkVariants.fonts.length,92);
  for(const sequence of ['㐂\u{e0101}','\u{20000}\u{e0100}','\u{30654}\u{e0101}','豈\ufe00']){
    const original=nativeVariationFont(sequence);
    for(const suffix of ['\u0301','\u0323','\u0302\u0307','\u0323\u0302\u0307','\u1ab0']){
      const text=sequence+suffix;
      const selected=nativeVariationFont(text);
      assert.equal(selected?.baseVariantFamily,original.family,text);
      assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),[selected.family],text);
      assert.deepEqual(fontRuns('A'+text+'B').map(r=>[r.text,r.fontFamily]),[['A',undefined],[text,selected.family],['B',undefined]],text);
    }
    if(original.family!=='Dad CJK Variants')
      assert.equal(nativeVariationFont(sequence+'\u3099')?.family,original.family,sequence);
    // Enclosing circle uses dynamic layout, not a falsely complete font.
    assert.equal(nativeVariationFont(sequence+'\u20dd'),undefined);
    assert.ok(!requiredFonts([Array.from(sequence)[0]]).fonts.some(f=>f.baseVariantFamily));
    assert.equal(nativeVariationFont(Array.from(sequence)[0]+'\u{e01ef}\u0301'),undefined);
  }
  for(const sequence of cjkVariants.variationSequences)
    assert.equal(nativeVariationFont(sequence+'\u0301')?.baseVariantFamily,'Dad CJK Variants',sequence);
});

test('supplementary IVS retain their variant font with native Jigmo CJK marks',()=>{
  for(const [base,selector] of [[0x20000,0xe0100],[0x30654,0xe0101]]){
    const sequence=String.fromCodePoint(base,selector);
    const original=nativeVariationFont(sequence);
    assert.ok(original,sequence);
    for(const mark of [0x302a,0x302b,0x302c,0x302d,0x302e,0x302f,0x3099,0x309a]){
      const text=sequence+String.fromCodePoint(mark);
      const selected=nativeVariationFont(text);
      assert.equal(selected?.family,original.family,text);
      assert.ok(selected.additionalSources.some(s=>s.source.endsWith('/Jigmo.ttf')),text);
      assert.ok(requiredFonts([text]).fonts.some(f=>f.family===selected.family),text);
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'text',fontFamily:selected.family}]);
    }
    assert.equal(nativeVariationFont(String.fromCodePoint(base,0xe01ef,0x3099)),undefined);
  }
});

test('every standardized pair has a native, contextual or Egyptian routing path',()=>{
  const rows=readFileSync(new URL('../data/unicode/18.0.0/StandardizedVariants.txt',import.meta.url),'utf8')
    .split('\n').map(s=>s.split('#')[0].trim()).filter(Boolean)
    .map(s=>s.split(';')[0].trim().split(/\s+/).map(v=>parseInt(v,16)));
  const counts={native:0,contextual:0,egyptianRotations:0,egyptianEditorial:0};
  for(const [cp,selector] of rows){
    const text=String.fromCodePoint(cp,selector);
    const source=cp>=0x1800&&cp<=0x18af?'Mongolian':cp>=0xa840&&cp<=0xa87f?'PhagsPa':cp>=0x10ac0&&cp<=0x10aff?'Manichaean':undefined;
    const loaded=requiredFonts([text]).fonts;
    const runs=fontRuns(text);
    assert.equal(runs.map(r=>r.text).join(''),text);
    if(source){
      counts.contextual++;
      assert.ok(loaded.some(f=>f.source?.endsWith(`/NotoSans${source}-Regular.ttf`)),text);
    }else if(runs.every(r=>r.emojiPolicy==='egyptian-variant')){
      counts.egyptianRotations++;
      assert.ok(loaded.some(f=>f.family==='Dad Egyptian Variants'),text);
    }else if(requiresEgyptianLayout(text)){
      counts.egyptianEditorial++;
      assert.ok(cp>=0x13443&&cp<=0x13446&&selector===0xfe00,text);
      assert.ok(loaded.some(f=>f.source?.endsWith('/egyptian-text/eot.ttf')),text);
      assert.equal(parseEgyptian(text)?.kind,'lost',text);
      assert.equal(parseEgyptian(text)?.expanded,true,text);
    }else{
      counts.native++;
      const family=nativeVariationFont(text)?.family;
      assert.ok(family,text);
      assert.ok(loaded.some(f=>f.family===family),text);
      if(hasJoiningCharacters(text))assert.equal(runs.length,1,text);
      else assert.ok(runs.some(r=>r.fontFamily===family),text);
    }
  }
  assert.equal(rows.length,1437);
  assert.deepEqual(counts,{native:1163,contextual:128,egyptianRotations:142,egyptianEditorial:4});
});

test('horizontal Sibe quotes load the licensed narrow forms with explicit provenance',()=>{
  for(const base of [...'‘’“”']){
    const selected=nativeVariationFont(base+'\ufe02');
    assert.ok(selected?.source.endsWith('/LXGWWenKai-Regular.ttf'));
    assert.ok(selected.variationDerivations.some(d=>d.sequence===base+'\ufe02' && d.drawingSequence===base+'\ufe00'));
    assert.deepEqual(requiredFonts([base+'\ufe02']).fonts.map(f=>f.family),[selected.family]);
    assert.equal(fontRuns(base+'\ufe02')[0].fontFamily,selected.family);
    assert.equal(nativeVariationFont(base+'\ufe02\u0301')?.family,selected.family);
  }
});

test('fullwidth zero keeps its explicit native variation and marked IVD retains source marks',()=>{
  for(const text of ['０\ufe00','０\ufe00\u0301','㐂\u{e0101}\u3099']){
    const selected=nativeVariationFont(text);
    assert.ok(selected,text);
    assert.ok(requiredFonts([text]).fonts.some(f=>f.family===selected.family));
    assert.equal(fontRuns(text)[0].fontFamily,selected.family);
  }
});

test('explicit math alternatives use their documented variant font and preserve accented clusters',()=>{
  assert.equal(mathVariants.variationSequences.length,37);
  for(const text of mathVariants.variationSequences){
    for(const suffix of ['', '\u0301','\u0302\u0307']){
      assert.equal(nativeVariationFont(text+suffix)?.family,'Dad Math Variants');
      assert.deepEqual(requiredFonts([text+suffix]).fonts.map(f=>f.family),['Dad Math Variants']);
      assert.equal(fontRuns(text+suffix)[0].fontFamily,'Dad Math Variants');
    }
    const base=Array.from(text)[0];
    assert.ok(!requiredFonts([base]).fonts.some(f=>f.family==='Dad Math Variants'));
  }
  assert.notEqual(nativeVariationFont('ℋ\ufe00')?.family,'Dad Math Variants');
  assert.equal(nativeVariationFont('ℋ\ufe01')?.family,'Dad Math Variants');
  assert.equal(nativeVariationFont('𝓏\ufe02')?.family,'Dad Math Variants');
  for(const selector of ['\ufe00','\ufe01'])
    assert.notEqual(nativeVariationFont('𝓏'+selector)?.family,'Dad Math Variants');
});

test('all standardized CJK pairs select their exact variant font without changing ordinary Han', () => {
  assert.equal(cjkVariants.variationSequences.length,1002);
  for (const text of cjkVariants.variationSequences) {
    const base=Array.from(text)[0];
    assert.equal(nativeVariationFont(text)?.family,'Dad CJK Variants',text);
    assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),['Dad CJK Variants'],text);
    assert.deepEqual(fontRuns('A'+text+'B').map(r=>[r.text,r.fontFamily]),[['A',undefined],[text,'Dad CJK Variants'],['B',undefined]],text);
    assert.ok(!requiredFonts([base]).fonts.some(f=>f.family==='Dad CJK Variants'),text);
    assert.ok(!requiredFonts([base+'\ufe0d']).fonts.some(f=>f.family==='Dad CJK Variants'),text);
  }
});

test('variation selection requires the exact selector and complete cluster repertoire', () => {
  const plain = {family:'Plain', ranges:[[32,126]]};
  const variants = {family:'Variants', ranges:[[32,126]], nativeVariations:{65024:[[48,48]]}};
  const marked = {...variants,family:'Marked',ranges:[[32,126],[0x301,0x301]]};
  const inventory = {baseRanges:[[32,126]],behaviouralRanges:[[0xfe00,0xfe0f]],fonts:[plain,variants,marked]};
  assert.deepEqual(variationPairs('0\ufe00'), [[48,65024]]);
  assert.equal(supportsVariations(variants,'0\ufe01'), false);
  assert.equal(nativeVariationFont('0',inventory), undefined);
  assert.equal(nativeVariationFont('0\ufe00',inventory), variants);
  assert.equal(nativeVariationFont('0\ufe00\u0301',inventory), marked);
  assert.equal(nativeVariationFont('1\ufe00',inventory), undefined);
  assert.deepEqual(requiredFonts(['A0\ufe00B'],inventory).fonts,[variants]);
  assert.deepEqual(requiredFonts(['A0B'],inventory).fonts,[]);
});

test('joining-script variants select one font covering all requested letters', () => {
  const ordinary = {family:'Ordinary',ranges:[[0x1000,0x109f]]};
  const partial = {family:'Partial',ranges:[[0x1000,0x1000]],nativeVariations:{65024:[[0x1000,0x1000]]}};
  const complete = {...partial,family:'Complete',ranges:ordinary.ranges};
  const inventory = {baseRanges:[[32,126]],behaviouralRanges:[[0xfe00,0xfe0f]],fonts:[ordinary,partial,complete]};
  assert.deepEqual(requiredFonts(['က\ufe00ခ'],inventory).fonts,[complete]);
  assert.deepEqual(requiredFonts(['ကခ'],inventory).fonts,[ordinary]);
  assert.deepEqual(fontRuns('က\ufe00ခ'),[{text:'က\ufe00ခ',emojiPolicy:'text'}]);
});

test('unsupported selectors preserve input without assigning another variant', () => {
  const font = {family:'Variants',ranges:[[48,48]],nativeVariations:{65024:[[48,48]]}};
  assert.equal(nativeVariationFont('0\ufe01',{fonts:[font]}),undefined);
  assert.deepEqual(fontRuns('A\ufe0dB'),[{text:'A\ufe0dB',emojiPolicy:'text'}]);
});

test('real math and quote variants load and measure in their selected fonts', () => {
  for (const text of ['0\ufe00','\u2018\ufe00','\u2019\ufe01','㐂\u{e0101}']) {
    const font = nativeVariationFont(text);
    assert.ok(font,text);
    assert.ok(requiredFonts([text]).fonts.some(f=>f.family===font.family));
    const runs = fontRuns('A'+text+'B');
    assert.equal(runs.length,3,text);
    assert.deepEqual(runs.map(r=>r.text),['A',text,'B']);
    assert.equal(runs[1].fontFamily,font.family);
    assert.ok(!runs[0].fontFamily && !runs[2].fontFamily);
    const ctx = {measureText(){return {width:10,actualBoundingBoxAscent:7,actualBoundingBoxDescent:2};}};
    const measure = createTextMeasurer(ctx,(size,policy,family)=>`${size}px "${family??'Dad Lettering'}"`);
    const measured = measure.ink('A'+text+'B',12);
    assert.equal(measured.runs[1].font,`12px "${font.family}"`);
    assert.equal(measured.runs[0].font,'12px "Dad Lettering"');
    assert.equal(measured.runs[2].font,'12px "Dad Lettering"');
  }
});
