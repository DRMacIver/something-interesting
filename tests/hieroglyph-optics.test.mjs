import {test} from 'node:test';
import assert from 'node:assert/strict';
import {hieroglyphStroke,splitHieroglyphRuns,reserveEgyptianStroke} from '../js/hieroglyph-optics.js';
import {createTextMeasurer} from '../js/text-metrics.js';

test('Egyptian optical ink stays confined to its native field, including bidi overrides',()=>{
  assert.ok(Math.abs(hieroglyphStroke('𓀀',100)-1.4)<1e-12);
  assert.ok(Math.abs(hieroglyphStroke('\u202e𓀀\u202c',100)-1.4)<1e-12);
  assert.equal(hieroglyphStroke('DAD 𓀀',100),0);
  const pieces=splitHieroglyphRuns({text:'DAD 𓀀\ufe00 END',drawText:'DAD 𓀀\ufe00 END',direction:'ltr'});
  assert.deepEqual(pieces.map(p=>p.text),['DAD ','𓀀\ufe00',' END']);
});

test('source-outline strokes reserve transformed enclosure ink without moving insertions',()=>{
  const ink={width:100,advance:100,drawOffset:0,ascent:90,descent:10,glyphs:[
    {primitive:'outline',x:2,y:-90,width:300,height:500,scale:.2,stretchX:3},
    {primitive:'damage',x:3,y:-30,width:20,height:20,scale:1},
  ]};
  const result=reserveEgyptianStroke(ink,100);
  const spread=result.glyphs[0].strokeWidth*.2*3/2;
  assert.equal(result.width,100+spread*2);
  assert.equal(result.drawOffset,spread);
  assert.equal(result.ascent,90+spread);
  assert.equal(result.descent,10+spread);
  assert.equal(result.advance,100);
  assert.deepEqual(result.glyphs[1],ink.glyphs[1]);
  assert.equal(result.glyphs[0].x,ink.glyphs[0].x);
  assert.equal(result.glyphs[0].y,ink.glyphs[0].y);
});

test('mixed-dialogue measurement paints weighted Egyptian runs while keeping dialogue size',()=>{
  const ctx={measureText(t){return {width:[...t].length*10,actualBoundingBoxLeft:0,actualBoundingBoxRight:[...t].length*10,actualBoundingBoxAscent:14,actualBoundingBoxDescent:0};}};
  const measure=createTextMeasurer(ctx,s=>`${s}px Font`);
  const ink=measure.ink('DAD 𓀀 END',20);
  const native=ink.runs.find(r=>r.text==='𓀀');
  assert.equal(native.strokeWidth,.28);
  assert.equal(native.fontSize,20);
  assert.ok(ink.runs.filter(r=>r!==native).every(r=>!r.strokeWidth));
  assert.ok(ink.ascent>=14.14);
});

test('Anatolian optical weight remains finer than Egyptian ink',()=>{
  assert.equal(hieroglyphStroke('𔐀',100),1);
  assert.ok(hieroglyphStroke('𔐀',100)<hieroglyphStroke('𓀀',100));
});


test('adjacent Egyptian and Anatolian fields retain their separate optical weights',()=>{
  const ctx={measureText(t){return {width:[...t].length*10,actualBoundingBoxLeft:0,actualBoundingBoxRight:[...t].length*10,actualBoundingBoxAscent:14,actualBoundingBoxDescent:0};}};
  const ink=createTextMeasurer(ctx,s=>`${s}px Font`).ink('𓀀𔐀',20);
  assert.equal(ink.runs.find(r=>r.text==='𓀀').strokeWidth,.28);
  assert.equal(ink.runs.find(r=>r.text==='𔐀').strokeWidth,.2);
});
