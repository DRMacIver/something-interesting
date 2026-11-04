import test from 'node:test';
import assert from 'node:assert/strict';
import {nativeVariationFont,nativeSpacingVariationFont,nativeSpacingVariationPlan} from '../js/font-variations.js';
import {requiredFonts,contains} from '../js/fonts.js';
import {fontRuns} from '../js/emoji-routing.js';
import {makeFontString} from '../js/comic.js';
import {createTextMeasurer} from '../js/text-metrics.js';
import {graphemes} from '../js/unicode.js';

test('foreign spacing vowels retain their registered nonjoining variation and bundled native fallback',()=>{
  for(const base of ['𝓏\ufe02','豈\ufe00','㐂\u{e0101}'])for(const mark of ['ः','ा','ि','ি','ெ','ொ','ါ','ើ']){
    const text=base+mark,font=nativeSpacingVariationFont(text),selection=requiredFonts([text]);
    assert.ok(font,text);
    assert.ok(selection.fonts.some(f=>f.family===font.family),text);
    assert.ok(selection.fonts.some(f=>contains(f.ranges,mark.codePointAt(0))),text);
    assert.deepEqual(selection.missing,[]);
    assert.deepEqual(selection.emojiFallbacks,[]);
    const clusters=graphemes(text);
    const plan=nativeSpacingVariationPlan(text);
    if(clusters.length===1)assert.deepEqual(fontRuns(text),plan.tail?[{text:plan.body,emojiPolicy:'text',fontFamily:font.family},{text:plan.tail,emojiPolicy:'text'}]:[{text,emojiPolicy:'text',fontFamily:font.family}]);
    else assert.deepEqual(fontRuns(text).map(r=>r.text),clusters,'retain pinned spacing-mark grapheme exceptions');
    const families=selection.fonts.map(f=>f.family);
    assert.equal(makeFontString(20,families,'text',font.family).split('"')[1],font.family);
    const ctx={measureText(){return {width:20,actualBoundingBoxAscent:20,actualBoundingBoxDescent:5};}};
    const measure=createTextMeasurer(ctx,(s,p,f)=>makeFontString(s,families,p,f));
    const paragraph='A '+text+' B',runs=measure.forParagraph(paragraph).at(0).ink(paragraph,20).runs;
    assert.ok(runs.some(r=>r.text===(clusters.length===1?plan.body:clusters[0])&&r.font.split('"')[1]===font.family),text);
    if(nativeVariationFont(text))assert.equal(font,nativeVariationFont(text),'complete native cluster takes priority');
  }
  for(const text of ['ب\ufe00ा','က\ufe00ါ','豈\ufe01ि','𝓏\ufe02िA','𝓏\ufe02ि\ufe00','1️⃣ा'])assert.equal(nativeSpacingVariationFont(text),undefined,text);
});
