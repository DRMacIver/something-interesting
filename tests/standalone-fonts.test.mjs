import test from 'node:test';
import assert from 'node:assert/strict';
import {standaloneFontSpans} from '../js/standalone-fonts.js';
import {fontRuns,routeDirectionalRun} from '../js/emoji-routing.js';
import {requiredFonts} from '../js/fonts.js';
import {makeFontString} from '../js/comic.js';

test('disconnected Tatweel fields load and paint the existing visible Kufi drawing',()=>{
  for(const text of ['ـ','ـــ','ـَ','LOOK ـ HERE','ب ـ ب','ب\u200cـ','ـ\u200cب']){
    const spans=standaloneFontSpans(text);
    assert.equal(spans.length,1,text);
    const font=spans[0].font,selection=requiredFonts([text]);
    assert.ok(font.source.endsWith('/NotoKufiArabic-Regular.ttf'));
    assert.ok(selection.fonts.some(f=>f.family===font.family));
    const runs=fontRuns(text);
    assert.equal(runs.map(r=>r.text).join(''),text);
    assert.ok(runs.some(r=>r.fontFamily===font.family&&r.text.includes('ـ')));
    const stack=makeFontString(20,selection.fonts.map(f=>f.family),'text',font.family);
    assert.ok(stack.startsWith('20px "'+font.family+'"'));
  }
});

test('connected extender words, joiners and transparent marks use one complete native font',()=>{
  for(const text of ['بـب','بــب','بَـب','ب\u200dـب','ب\u061cـب','بـ\u200eب']){
    const [span]=standaloneFontSpans(text);
    assert.equal(span.start,0);assert.equal(span.end,text.length);
    assert.ok(span.font.source.endsWith('/NotoKufiArabic-Regular.ttf'));
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'text',fontFamily:span.font.family}]);
    assert.ok(requiredFonts([text]).fonts.some(f=>f.family===span.font.family));
  }
  for(const text of ['مرحبا','بب'])assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'text'}]);
  const syriac=standaloneFontSpans('ܒـܒ');
  assert.equal(syriac.length,1);assert.ok(syriac[0].font.source.endsWith('/NotoSansSyriac-Regular.ttf'));
  const run={text:'ب ـ ب',drawText:'ب ـ ب',direction:'rtl'};
  const routed=routeDirectionalRun(run);
  assert.deepEqual(routed.map(r=>r.text),[' ب','ـ','ب ']);
  assert.ok(routed[1].fontFamily);
});
