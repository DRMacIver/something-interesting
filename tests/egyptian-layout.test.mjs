import test from 'node:test';
import assert from 'node:assert/strict';
import {parseEgyptian,layoutEgyptian,egyptianInk,egyptianSegmentInteriors} from '../js/egyptian-layout.js';
import {createTextMeasurer,textScale} from '../js/text-metrics.js';
import {layoutColumn} from '../js/layout.js';
import {reserveEgyptianStroke} from '../js/hieroglyph-optics.js';
import insertionManifest from '../js/egyptian-insertion-manifest.js';
const A='𓑠',B='𓑡',C='𓑢',V='\u{13430}',H='\u{13431}',O='\u{13436}',SB='\u{13437}',SE='\u{13438}';
const measure=(text,size,policy)=>({font:`${size}px ${policy}`,width:size*.6,advance:size*.6,drawOffset:0,ascent:size*.8,descent:size*.2});

test('Egyptian joiners follow Unicode precedence and explicit nested segments',()=>{
  const tree=parseEgyptian(A+V+B+H+C);
  assert.equal(tree.kind,'vertical');assert.equal(tree.children[1].kind,'horizontal');
  const nested=parseEgyptian(SB+A+V+B+SE+H+C);
  assert.equal(nested.kind,'horizontal');assert.equal(nested.children[0].kind,'vertical');
  assert.equal(parseEgyptian(A+H+B+O+C).children[1].kind,'overlay');
  assert.equal(parseEgyptian(A+'\u{13432}'+B).kind,'insertion');
  assert.equal(egyptianInk(A+'\u{13432}'+B,100,measure),null);
  assert.equal(parseEgyptian(SB+A+V+B),null);
  assert.equal(parseEgyptian(SB.repeat(40)+A+SE.repeat(40)),null);
});

test('horizontal, vertical and overlay groups produce distinct bounded placements',()=>{
  const h=layoutEgyptian(parseEgyptian(A+H+B),100,measure);
  const v=layoutEgyptian(parseEgyptian(A+V+B),100,measure);
  const o=layoutEgyptian(parseEgyptian(A+O+B),100,measure);
  assert.ok(h.glyphs[0].x<h.glyphs[1].x);assert.equal(h.glyphs[0].y,h.glyphs[1].y);
  assert.equal(v.glyphs[0].x,v.glyphs[1].x);assert.ok(v.glyphs[0].y<v.glyphs[1].y);
  assert.equal(o.glyphs[0].x,o.glyphs[1].x);assert.equal(o.glyphs[0].y,o.glyphs[1].y);
  assert.ok(v.width<h.width);assert.equal(v.height,100);
  for(const plan of [h,v,o])for(const g of plan.glyphs){
    assert.ok(g.x>=0 && g.x+60*g.scale<=plan.width+1e-8);
    assert.ok(g.y-80*g.scale>=-1e-8 && g.y+20*g.scale<=plan.height+1e-8);
  }
});

test('rotated signs retain their logical sequences in nested glyph plans',()=>{
  const rotated='𔉴\ufe05';
  const ink=egyptianInk(SB+A+V+rotated+SE+H+B,100,measure);
  assert.deepEqual(ink.glyphs.map(g=>g.drawText),[A,rotated,B]);
  assert.ok(ink.glyphs[1].font.includes('egyptian-variant'));
  assert.equal(egyptianInk('𓀀'+V+'𓀁',100,measure),null,'existing core composition stays native');
});

test('measurement and wrapping keep extended quadrats whole and reserve their glyph ink',()=>{
  const ctx={measureText(text){const size=parseFloat(this.font);return {width:[...text].length*size*.6,actualBoundingBoxAscent:size*.8,actualBoundingBoxDescent:size*.2};}};
  const metric=createTextMeasurer(ctx,(s,p)=>`${s}px ${p}`);
  const group=A+V+B;
  const result=layoutColumn(group+' '+group,{measure:metric,fontSize:10,width:22});
  assert.equal(result.fits,true);
  assert.equal(result.lines.map(l=>l.text).join(' '),group+' '+group);
  for(const line of result.lines){
    const glyphs=line.ink.glyphs??line.ink.runs?.flatMap(r=>r.glyphs??[]);
    assert.ok(glyphs.length);
    assert.ok(line.baseline>=line.ink.ascent && line.baseline+line.ink.descent<=line.height);
  }
});


test('adjacent quadrats stay separate without inserted text or whole-line compression',()=>{
  const one=layoutEgyptian(parseEgyptian(A+V+B),100,measure);
  const pair=layoutEgyptian(parseEgyptian(A+V+B+A+V+B),100,measure);
  assert.equal(pair.glyphs.length,4);
  assert.ok(pair.width>2*one.width);
  assert.equal(pair.height,one.height);
  assert.deepEqual(pair.glyphs.map(g=>g.drawText),[A,B,A,B]);
});


test('emergency wrapping cannot split adjacent signs inside an explicit segment',()=>{
  const group=SB+A+B+SE;
  const result=layoutColumn(group,{measure:t=>[...t].length*10,fontSize:10,width:20});
  assert.equal(result.lines.length,1);
  assert.equal(result.lines[0].text,group);
});

test('mirroring reflects native glyph ink after rotation without changing group dimensions',()=>{
  const M='\u{13440}',rotated='𔉴\ufe05';
  const asymmetric=(t,s,p)=>({...measure(t,s,p),width:70,drawOffset:5});
  const normal=layoutEgyptian(parseEgyptian(rotated+V+B),100,asymmetric);
  const mirrored=layoutEgyptian(parseEgyptian(rotated+M+V+B),100,asymmetric);
  assert.equal(normal.width,mirrored.width);
  assert.equal(normal.height,mirrored.height);
  const a=normal.glyphs[0],b=mirrored.glyphs[0];
  assert.equal(b.drawText,rotated);
  assert.equal(b.flipX,true);
  assert.ok(b.font.includes('egyptian-variant'));
  assert.equal(a.x+b.x,70*a.scale);
  assert.equal(parseEgyptian(M+A),null);
  assert.equal(parseEgyptian(A+M+M),null);
  assert.ok(egyptianInk(A+M,100,asymmetric).glyphs[0].flipX);
});

test('rotation comparisons keep the variant font on both sides of a mirrored run',()=>{
  const rotated='𔉴\ufe05';
  const ink=egyptianInk(rotated+' '+rotated+'\u{13440}',100,measure);
  const signs=ink.glyphs.filter(g=>g.drawText===rotated);
  assert.equal(signs.length,2);
  assert.ok(signs.every(g=>g.font.includes('egyptian-variant')));
  assert.equal(signs[0].flipX,false);
  assert.equal(signs[1].flipX,true);
  assert.equal(signs[0].scale,signs[1].scale);
});

test('editorial blanks reserve full and half-square space without drawing a glyph',()=>{
  for(const [text,side] of [['𓑁',100],['𓑂',50]]) {
    const box=layoutEgyptian(parseEgyptian(text),100,measure);
    assert.equal(box.width,side);assert.equal(box.height,side);
    assert.deepEqual(box.glyphs,[]);
  }
  const row=layoutEgyptian(parseEgyptian(A+'𓑁'+B),100,measure);
  assert.equal(row.glyphs.length,2);
  assert.ok(row.glyphs[1].x-row.glyphs[0].x>=100);
  assert.equal(parseEgyptian('𓑁\ufe00'),null);
});

test('lost-sign forms preserve dimensions and expanded variants remove adjacent seams',()=>{
  for(const [text,w,h] of [['𓑃',100,100],['𓑄',50,50],['𓑅',50,100],['𓑆',100,50]]) {
    const box=layoutEgyptian(parseEgyptian(text),100,measure);
    assert.equal(box.width,w);assert.equal(box.height,h);
    assert.equal(box.glyphs[0].primitive,'lost');
    assert.ok(box.glyphs[0].width<w && box.glyphs[0].height<h);
    const expanded=layoutEgyptian(parseEgyptian(text+'\ufe00'),100,measure);
    assert.equal(expanded.glyphs[0].width,w);assert.equal(expanded.glyphs[0].height,h);
  }
  const expanded=layoutEgyptian(parseEgyptian('𓑃\ufe00𓑃\ufe00'),100,measure);
  assert.equal(expanded.width,200);
  const [a,b]=expanded.glyphs;
  assert.equal(a.x+a.width*a.scale,b.x);
  const normal=layoutEgyptian(parseEgyptian('𓑃𓑃'),100,measure);
  assert.ok(normal.glyphs[0].x+normal.glyphs[0].width<normal.glyphs[1].x);
  const group=egyptianInk(A+V+'𓑃',100,measure);
  assert.ok(group.glyphs.some(g=>g.primitive==='lost'));
  assert.ok(group.glyphs.every(g=>g.y+(g.height??0)*g.scale<=group.descent));
});

test('all fifteen damage modifiers shade their named LTR quarters without changing sign geometry',()=>{
  // Quarter coordinates independently transcribed from UnicodeData names:
  // TS=(0,0), BS=(0,1), TE=(1,0), BE=(1,1).
  const expected=[['00'],['01'],['00','01'],['10'],['00','10'],['01','10'],
    ['00','01','10'],['11'],['00','11'],['01','11'],['00','01','11'],
    ['10','11'],['00','10','11'],['01','10','11'],['00','01','10','11']];
  for(let i=0;i<15;i++) {
    const modifier=String.fromCodePoint(0x13447+i);
    const base=layoutEgyptian(parseEgyptian(A),100,measure);
    const box=layoutEgyptian(parseEgyptian(A+modifier),100,measure);
    assert.equal(box.width,base.width);assert.equal(box.height,base.height);
    assert.deepEqual(box.glyphs[0],base.glyphs[0]);
    const regions=box.glyphs.filter(g=>g.primitive==='damage');
    assert.deepEqual(regions.map(g=>`${g.x?1:0}${g.y?1:0}`),expected[i]);
    for(const g of regions){
      assert.equal(g.sourceText,modifier);
      assert.equal(g.width,box.width/2);assert.equal(g.height,box.height/2);
      assert.ok(g.x+g.width<=box.width && g.y+g.height<=box.height);
    }
  }
  assert.equal(parseEgyptian('\u{13447}'+A),null);
  assert.equal(parseEgyptian(A+'\u{13447}\u{13448}'),null);
});

test('damage shades the final surface of rotated mirrored signs and stays attached in groups',()=>{
  const text='𔉴\ufe05\u{13440}\u{13447}';
  const box=layoutEgyptian(parseEgyptian(text),100,measure);
  assert.equal(box.glyphs[0].flipX,true);
  assert.ok(box.glyphs[0].font.includes('egyptian-variant'));
  assert.equal(box.glyphs[1].x,0);assert.equal(box.glyphs[1].y,0);
  const ink=egyptianInk(text+V+B,100,measure);
  const region=ink.glyphs.find(g=>g.primitive==='damage');
  assert.ok(region.scale<1);
  assert.ok(region.y>=-ink.ascent);
  assert.ok(region.y+region.height*region.scale<=ink.descent);
});

test('RTL Egyptian groups reverse horizontal positions and facing while preserving vertical order',()=>{
  for(const text of [A+H+B,A+V+B,SB+A+V+B+SE+H+C,A+' '+B]) {
    const ltr=egyptianInk(text,100,measure,'rtl');
    const glyphs=ltr.glyphs.filter(g=>g.drawText===A||g.drawText===B||g.drawText===C);
    assert.ok(glyphs.every(g=>g.flipX));
    const a=glyphs.find(g=>g.drawText===A),b=glyphs.find(g=>g.drawText===B);
    if(text.includes(V))assert.ok(a.y<b.y);
    else assert.ok(a.x>b.x);
    assert.ok(glyphs.every(g=>g.x>=0 && g.x<=ltr.width));
  }
});

test('RTL rotation reflection cancels explicit mirroring and moves start-side damage to the right',()=>{
  const text='𔉴\ufe05\u{13440}\u{13447}';
  const ltr=egyptianInk(text,100,measure),rtl=egyptianInk(text,100,measure,'rtl');
  assert.equal(ltr.width,rtl.width);assert.equal(ltr.ascent,rtl.ascent);
  assert.equal(ltr.glyphs[0].flipX,true);assert.equal(rtl.glyphs[0].flipX,false);
  assert.equal(rtl.glyphs[0].drawText,'𔉴\ufe05');
  const left=ltr.glyphs.find(g=>g.primitive==='damage'),right=rtl.glyphs.find(g=>g.primitive==='damage');
  assert.equal(left.x,0);assert.equal(right.x,rtl.width/2);
});

test('explicit bidi override dispatches ordinary Egyptian signs to mirrored drawing',()=>{
  const ctx={measureText(text){const size=parseFloat(this.font);return {width:[...text].length*size*.6,actualBoundingBoxAscent:size*.8,actualBoundingBoxDescent:size*.2};}};
  const metric=createTextMeasurer(ctx,(s,p)=>`${s}px ${p}`);
  const text='\u202e'+A+B+'\u202c';
  const box=metric.forParagraph(text).at(0).ink(text,20);
  const glyphs=box.runs.flatMap(r=>r.glyphs??[]);
  assert.equal(glyphs.length,2);assert.ok(glyphs.every(g=>g.flipX));
  assert.ok(glyphs[0].x>glyphs[1].x);
});

test('directional wrappers do not shrink Egyptian quadrats',()=>{
  const group=A+V+B;
  assert.equal(textScale(group),2);
  assert.equal(textScale('\u202e'+group+'\u202c'),textScale(group));
  assert.equal(textScale('\u202d'+group+'\u202c'),textScale(group));
});

test('native-derived insertion areas contain extended signs and nested groups',()=>{
  for(const text of ['𓆓\u{13433}'+A,'𓄂\u{13432}'+B,'𓆓\u{13433}'+SB+A+V+B+SE]) {
    const box=layoutEgyptian(parseEgyptian(text),100,measure);
    assert.equal(box.glyphs[0].primitive,'outline');
    assert.ok(box.glyphs[0].path.length>100);
    for(const g of box.glyphs.slice(1)){
      assert.ok(g.x>=0 && g.x+60*g.scale<=box.width+1e-8);
      assert.ok(g.y-80*g.scale>=-1e-8 && g.y+20*g.scale<=box.height+1e-8);
    }
    const rtl=egyptianInk(text,100,measure,'rtl');
    assert.equal(rtl.glyphs[0].flipX,true);
    assert.ok(rtl.glyphs.filter(g=>g.drawText).every(g=>g.flipX));
  }
  const tree=parseEgyptian('𓆓\u{13433}'+A+H+B);
  assert.equal(tree.kind,'horizontal');assert.equal(tree.children[0].kind,'insertion');
});

test('undocumented containers retain the logical group without inventing a cavity',()=>{
  const excluded=A+'\u{13439}'+B;
  assert.equal(egyptianInk(excluded,100,measure),null);
  const mixed=egyptianInk(A+V+B+' '+excluded,100,measure);
  assert.ok(mixed.glyphs.some(g=>g.drawText===excluded));
  assert.ok(!mixed.glyphs.some(g=>g.primitive==='outline'));
});

test('every enumerated native insertion template reaches actual container and child drawing',()=>{
  for(const entry of Object.values(insertionManifest.entries)){
    const text=String.fromCodePoint(...entry.container)+entry.controls.map(cp=>String.fromCodePoint(cp)+A).join('');
    const ink=egyptianInk(text,100,measure);
    assert.ok(ink,text);
    assert.equal(ink.glyphs.filter(g=>g.primitive==='outline').length,1,text);
    assert.equal(ink.glyphs.filter(g=>g.drawText===A).length,entry.controls.length,text);
    assert.ok(ink.width>0&&Number.isFinite(ink.ascent),text);
    assert.ok(!ink.glyphs.some(g=>g.drawText?.includes('\u{13440}')),text);
  }
});

test('enclosure controls connect native ends around extended and nested content',()=>{
  const begin='\u{1343c}',end='\u{1343d}';
  for(const text of ['𓍹'+begin+A+B+C+end+'𓍺',begin+A+end,
    '𓍹'+begin+A+begin+B+end+C+end+'𓍺','𓊆\u{1343e}'+A+V+B+'\u{1343f}𓊇']) {
    const tree=parseEgyptian(text);assert.equal(tree.kind,'enclosure');
    const box=layoutEgyptian(tree,100,measure);
    assert.equal(box.height,100);assert.ok(box.width>100);
    assert.ok(box.glyphs.some(g=>g.primitive==='outline'));
    for(const g of box.glyphs){
      if(g.primitive){assert.ok(g.x>=-1e-8);assert.ok(g.x+g.width*g.scale<=box.width+1e-8);}
      else {assert.ok(g.y-80*g.scale>=0);assert.ok(g.y+20*g.scale<=box.height+1e-8);}
    }
    const rtl=egyptianInk(text,100,measure,'rtl');
    assert.ok(rtl.glyphs.every(g=>g.flipX));assert.equal(rtl.width,box.width);
  }
  assert.equal(parseEgyptian(begin+A+'\u{1343f}'),null);
  assert.equal(parseEgyptian(begin+A),null);
  assert.equal(parseEgyptian('𓍹'+A+'𓍺').kind,'sequence');
});

test('enclosure interiors and attached ends cannot split during emergency wrapping',()=>{
  const text='𓍹\u{1343c}'+A+B+C+'\u{1343d}𓍺';
  const positions=egyptianSegmentInteriors(text);
  let offset=0;
  for(const c of [...text].slice(0,-1)){offset+=c.length;assert.ok(positions.has(offset));}
});

test('multiple insertions use one jointly shaped container and retain logical region assignments',()=>{
  const bs='\u{13433}',te='\u{13434}',be='\u{13435}';
  const forward=layoutEgyptian(parseEgyptian('𓆓'+bs+A+te+B),100,measure);
  const reverse=layoutEgyptian(parseEgyptian('𓆓'+te+B+bs+A),100,measure);
  assert.equal(forward.glyphs.filter(g=>g.primitive==='outline').length,1);
  for(const text of [A,B]){
    const a=forward.glyphs.find(g=>g.drawText===text),b=reverse.glyphs.find(g=>g.drawText===text);
    assert.deepEqual(a,b);
  }
  const texts=['𓅜'+bs+A+te+B+be+C,'𓆓'+bs+SB+A+V+B+SE+te+C];
  for(const text of texts){
    const ink=egyptianInk(text,100,measure);
    assert.ok(ink);assert.equal(ink.glyphs.filter(g=>g.primitive==='outline').length,1);
    assert.deepEqual(ink.glyphs.filter(g=>g.drawText).map(g=>g.drawText),[A,B,C]);
    const rtl=egyptianInk(text,100,measure,'rtl');assert.ok(rtl.glyphs.every(g=>g.flipX));
  }
  // An explicitly grouped left operand is not a single container sign.
  assert.equal(egyptianInk(SB+'𓆓'+bs+A+SE+te+B,100,measure),null);
  assert.equal(egyptianInk('𓆓'+bs+A+bs+B,100,measure),null);
});

test('modified insertion containers use separately probed native outlines',()=>{
  const cases=['𓀠\u{13440}\u{13433}'+A,'𓂓\ufe01\u{13439}'+B,'𓇹\ufe01\u{13440}\u{1343b}'+C];
  for(const text of cases){
    const ink=egyptianInk(text,100,measure);assert.ok(ink);
    assert.equal(ink.glyphs[0].primitive,'outline');
    assert.ok(!ink.glyphs[0].flipX,'explicit modifier is already in the source outline');
    assert.equal(ink.glyphs.filter(g=>g.drawText).length,1);
    const rtl=egyptianInk(text,100,measure,'rtl');assert.equal(rtl.glyphs[0].flipX,true);
    assert.equal(rtl.width,ink.width);
  }
  assert.ok(egyptianInk('𓆓\u{13440}\u{13433}'+A,100,measure)?.glyphs.some(g=>g.primitive==='outline'));
  assert.equal(egyptianInk('𓆓\ufe00\u{13433}'+A,100,measure),null);
});

test('native insertion geometry survives observed overlaps, overflow and all damage masks',()=>{
  for(const prefix of ['𓀐','𓆓\u{13440}']){
    const control=prefix==='𓀐'?'\u{1343b}':'\u{13433}';
    const plain=egyptianInk(prefix+control+A,100,measure);
    assert.ok(plain);
    for(let mask=1;mask<=15;mask++){
      const text=prefix+String.fromCodePoint(0x13446+mask)+control+A;
      const ink=egyptianInk(text,100,measure);
      assert.equal(ink.width,plain.width);assert.equal(ink.ascent,plain.ascent);
      assert.deepEqual(ink.glyphs.filter(g=>g.primitive==='outline'),plain.glyphs.filter(g=>g.primitive==='outline'));
      assert.deepEqual(ink.glyphs.filter(g=>g.drawText),plain.glyphs.filter(g=>g.drawText));
      assert.equal(ink.glyphs.filter(g=>g.primitive==='damage').length,mask.toString(2).replaceAll('0','').length);
      const rtl=egyptianInk(text,100,measure,'rtl');assert.equal(rtl.width,ink.width);
    }
  }
});


test('optical ink preserves all native insertion plans in both directions',()=>{
  for(const entry of Object.values(insertionManifest.entries)){
    const text=String.fromCodePoint(...entry.container)+entry.controls.map(cp=>String.fromCodePoint(cp)+A).join('');
    for(const direction of ['ltr','rtl']){
      const native=egyptianInk(text,22,measure,direction);
      const optical=reserveEgyptianStroke(native,22);
      assert.equal(optical.advance,native.advance);
      assert.ok(optical.width>=native.width);
      assert.ok(optical.ascent>=native.ascent&&optical.descent>=native.descent);
      assert.equal(optical.glyphs.length,native.glyphs.length);
      for(const [i,glyph] of optical.glyphs.entries()){
        const {strokeWidth,...geometry}=glyph;
        const {strokeWidth:previous,...original}=native.glyphs[i];
        assert.deepEqual(geometry,original);
        if(glyph.primitive==='outline')assert.ok(strokeWidth>0&&Number.isFinite(strokeWidth));
      }
    }
  }
});
