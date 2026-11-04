import test from 'node:test';
import assert from 'node:assert/strict';
import { createTextMeasurer } from '../js/text-metrics.js';
import { graphemes } from '../js/unicode.js';
import { breakUnits } from '../js/line-breaks.js';
import { splitVietnameseMarks } from '../js/vietnamese-marks.js';

test('Vietnamese side marks paint separately while logical clusters stay intact',()=>{
  const calls=[];
  const ctx={measureText(text){calls.push(text);return {width:text==='𖿰'?340:text==='𖿱'?220:1000,actualBoundingBoxAscent:800,actualBoundingBoxDescent:0};}};
  const measure=createTextMeasurer(ctx,size=>`${size}px test`);
  for (const [text,width] of [['日𖿰',1340],['外𖿱',1220]]) {
    assert.deepEqual(graphemes(text),[text]);
    assert.equal(breakUnits(text).length,1);
    const result=measure.ink(text,1000,'ltr');
    assert.equal(result.advance,width);
    assert.equal(result.runs[1].offset,1000);
    assert.equal(result.runs.map(r=>r.text).join(''),text);
    assert.ok(!calls.includes(text),'avoid browser whole-cluster font fallback');
  }
});

test('drawing splits retain explicit bidi overrides and leave emoji clusters intact',()=>{
  const run={text:'日𖿰',drawText:'\u202e日𖿰\u202c',direction:'rtl',emojiPolicy:'text'};
  assert.deepEqual(splitVietnameseMarks(run).map(r=>r.drawText),['\u202e𖿰\u202c','\u202e日\u202c']);
  const emoji={text:'😀𖿰',drawText:'😀𖿰',direction:'ltr',emojiPolicy:'native'};
  assert.deepEqual(splitVietnameseMarks(emoji),[emoji]);
});
