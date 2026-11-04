import test from 'node:test';
import assert from 'node:assert/strict';
import {annotationPlan,annotationFontText,combiningInk} from '../js/combining-annotations.js';
import {nativeVariationFont} from '../js/font-variations.js';
import {requiredFonts} from '../js/fonts.js';
import {createTextMeasurer} from '../js/text-metrics.js';
import {emergencyBoundary} from '../js/line-breaks.js';
import outlines from '../js/combining-outline-manifest.js';

const measure=(text,size,direction='ltr')=>({font:`${size}px test`,advance:[...text].filter(c=>!/^\p{M}$/u.test(c)).length*size*.6,width:[...text].filter(c=>!/^\p{M}$/u.test(c)).length*size*.6,drawOffset:0,ascent:size*.7,descent:0});

test('Cyrillic numeric enclosures preserve their component identities around native variants',()=>{
  for(const cp of [0x488,0x489,0xa670,0xa671,0xa672])for(const base of ['Á','㐂\u{e0101}́','𝓏\ufe02','\u{20000}\u{e0100}']){
    const mark=String.fromCodePoint(cp),text=base+mark,plan=annotationPlan(text);
    assert.equal(plan.body,base);
    const m=combiningInk(text,20,measure),glyphs=m.glyphs.filter(g=>g.codepoint===cp);
    const data=outlines.marks[cp].numericEnclosure;
    assert.equal(glyphs.length,data.parts.length);
    assert.equal(m.glyphs[0].drawText,base);assert.equal(m.glyphs[0].scale,1);
    if(base.includes('\ufe02')||base.includes('\u{e0101}')||base.includes('\u{e0100}'))assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),[nativeVariationFont(base).family]);
    for(const [i,g] of glyphs.entries()){
      assert.equal(g.scale,20);assert.equal(g.stretchX,1);
      if(data.kind!=='brackets')assert.equal(g.path,data.parts[i].path);
      // Each component clears the base rectangle, rather than overprinting
      // it or using the mark's original empty writing area as painted ink.
      const b=m.glyphs[0],left=b.x,right=b.x+12,top=-14,bottom=0;
      assert.ok(g.x+g.frame.width<=left||g.x>=right||g.y+g.frame.height<=top||g.y>=bottom,cp.toString(16));
    }
    const nested=combiningInk(text+'⃞',20,measure);
    assert.ok(nested.width>m.width&&nested.ascent>m.ascent);
    const sixteen=combiningInk(base+mark.repeat(16),20,measure);
    assert.ok(sixteen.width<m.width+20*40,'repeated numeric signs must grow linearly');
  }
});

test('dynamic enclosure follows marks and preserves the selected native variant',()=>{
  const base='㐂\u{e0101}',text=base+'́⃝';
  assert.equal(annotationFontText(text),base+'́');
  assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),[nativeVariationFont(base+'́').family]);
  const box=combiningInk(text,20,measure);
  assert.equal(box.glyphs[0].drawText,base+'́');
  assert.equal(box.glyphs[0].scale,1);
  assert.equal(box.glyphs[1].annotation,'enclosure');
  assert.ok(box.ascent>14&&box.descent>0&&box.advance>12);
});

test('foreign marks retain native CJK and math variants without replacing the base',()=>{
  for(const [base,mark] of [['㐂\u{e0101}','⃒'],['\u{20000}\u{e0100}','⃒'],['豈\ufe00','゙'],['𝓏\ufe02','゙'],['豈\ufe00','ְ'],['豈\ufe00','़']]){
    const family=nativeVariationFont(base).family,text=base+mark;
    assert.equal(annotationFontText(text),base);
    assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),[family]);
    const layout=combiningInk(text,20,measure);
    assert.equal(layout.glyphs[0].drawText,base);
    assert.equal(layout.glyphs[0].scale,1);
    assert.equal(layout.glyphs[1].codepoint,mark.codePointAt(0));
    assert.equal(layout.glyphs[1].path,outlines.marks[mark.codePointAt(0)].path);
  }
  for(const text of ['㐂\u{e01ef}⃒','ب\ufe00゙'])assert.equal(annotationPlan(text),null,text);
});

test('CGJ preserves native variation prefixes and blocks canonical reordering without ink',()=>{
  for(const base of ['𝓏\ufe02','豈\ufe00']){
    for(const [text,body,points] of [[base+'͏゙',base+'͏',[0x3099]],
      [base+'́͏゙',base+'́͏',[0x3099]],
      [base+'゙͏́',base,[0x3099,0x301]],
      [base+'゙͏́⃝͏̣',base,[0x3099,0x301,0x20dd,0x323]]]){
      const plan=annotationPlan(text);
      const family=nativeVariationFont(body).family;
      assert.equal(plan.body,body,text);
      assert.deepEqual(requiredFonts([text]).fonts.map(f=>f.family),[family]);
      const box=combiningInk(text,20,measure),marks=box.glyphs.filter(g=>g.primitive==='outline');
      assert.equal(box.glyphs[0].drawText,body);assert.equal(box.glyphs[0].scale,1);
      assert.deepEqual(marks.map(g=>g.codepoint),points);
      assert.ok(!marks.some(g=>g.codepoint===0x34f));
      for(const g of marks.filter(g=>g.nativeMarkFamily))assert.equal(g.nativeMarkFamily,family);
    }
    // Without the CGJ boundary, class8 is canonically sorted before class230;
    // with it the native acute stays inside the shaped prefix before dakuten.
    assert.equal(annotationPlan(base+'゙́').body,base);
    assert.equal(annotationPlan(base+'́͏゙').body,base+'́͏');
  }
  assert.equal(annotationPlan('㐂\u{e0101}͏゙'),null,'complete native CJK cluster stays native');
  for(const text of ['A͏⃝','ب\ufe00͏゙','𝓏\ufe02͡͏゙','𝓏͏\ufe02゙','豈\ufe00\u200d͏゙'])assert.equal(annotationPlan(text),null,text);
});

test('foreign and native accents keep canonical stack order and exact source drawings',()=>{
  const base='𝓏\ufe02',family=nativeVariationFont(base).family;
  const text=base+'゙́'; // canonical class 8 precedes acute class 230
  const plan=annotationPlan(text),layout=combiningInk(text,20,measure);
  assert.equal(plan.body,base);
  const marks=layout.glyphs.filter(g=>g.primitive==='outline');
  assert.deepEqual(marks.map(g=>g.codepoint),[0x3099,0x301]);
  assert.equal(marks[1].nativeMarkFamily,family);
  const source=outlines.variationMarks[family],row=source.marks[0x301];
  assert.equal(marks[1].path,outlines.variantDrawings[row.drawing].path);
  assert.ok(marks[1].y<marks[0].y);
  assert.equal(annotationPlan(base+'́'),null,'complete native accent shaping stays intact');
  const nested=combiningInk(text+'⃝',20,measure);
  assert.equal(nested.glyphs.at(-1).annotation,'enclosure');
  assert.ok(nested.glyphs.at(-1).y<marks[1].y);
});

test('positional combining classes override a donor glyph origin and attached marks touch',()=>{
  for(const cp of [0x31b,0x18a9,0x1df7]){
    const glyphs=combiningInk('A⃝'+String.fromCodePoint(cp),20,measure).glyphs;
    const g=glyphs.at(-1),enclosure=glyphs.find(g=>g.annotation==='enclosure');
    assert.ok(g.y+g.frame.height<=enclosure.y,'above classes must stay above even with positive source y bounds');
  }
  const glyphs=combiningInk('A⃝\u031b',20,measure).glyphs;
  assert.equal(glyphs.at(-1).y+glyphs.at(-1).frame.height,glyphs.find(g=>g.annotation==='enclosure').y);
});

test('an enclosing mark surrounds intervening accents and previous enclosures',()=>{
  const first=combiningInk('A⃝',20,measure),nested=combiningInk('A⃝́⃞',20,measure);
  const paths=nested.glyphs.filter(g=>g.primitive==='outline');
  assert.deepEqual(paths.map(p=>p.codepoint),[0x20dd,0x301,0x20de]);
  const [circle,accent,square]=paths;
  assert.ok(accent.y<circle.y);
  assert.ok(square.y<accent.y);
  assert.ok(nested.width>first.width&&nested.ascent>first.ascent);
  for(const mark of ['⃝','⃟','⃤']){
    const rings=combiningInk('A'+mark.repeat(3),20,measure).glyphs.filter(g=>g.annotation==='enclosure');
    for(let i=1;i<rings.length;i++){
      const previous=rings[i-1],outer=rings[i],bounds=outlines.marks[outer.codepoint].ring.inner.bounds;
      const [a,, ,d,e,f]=outer.contours[1].matrix;
      assert.ok(outer.x+a*bounds[0]+e<previous.x);
      assert.ok(outer.x+a*bounds[2]+e>previous.x+previous.frame.width);
      assert.ok(outer.y+d*bounds[1]+f<previous.y);
      assert.ok(outer.y+d*bounds[3]+f>previous.y+previous.frame.height);
    }
  }
  for(const mark of ['⃠','⃣']){
    const box=combiningInk('A'+mark,20,measure),base=box.glyphs[0],g=box.glyphs[1];
    const record=outlines.marks[g.codepoint],b=record.contentBounds,o=record.bounds;
    assert.ok(g.x+(b[0]-o[0])*g.scale*g.stretchX<base.x);
    assert.ok(g.x+(b[2]-o[0])*g.scale*g.stretchX>base.x+12);
    assert.ok(g.y+(b[1]-o[1])*g.scale<base.y-14);
    assert.ok(g.y+(b[3]-o[1])*g.scale>base.y);
  }
});

test('double diacritics span just the following base and float outside both stacks',()=>{
  const m=(text,size)=>({...measure(text,size),ascent:text.includes('́')?size:14});
  const result=combiningInk('a͡b́cd',20,m);
  const double=result.glyphs.find(g=>g.annotation==='double');
  assert.ok(double.y+(.184*20)<-20);
  assert.ok(double.x<6&&double.x+double.scale*double.stretchX*.756>18);
  assert.ok(double.x+double.scale*double.stretchX*.756<30,'must not extend over c/d');
  assert.equal(emergencyBoundary('日́͡','月'),false);
});

test('all ten pinned double-diacritic classes have a layout path',()=>{
  const points=Object.entries(outlines.marks).filter(([,e])=>[233,234].includes(e.ccc)).map(([cp])=>Number(cp));
  assert.equal(points.length,10);
  for(const cp of points){
    const text='a'+String.fromCodePoint(cp);
    assert.deepEqual(annotationPlan(text)?.doubles,[String.fromCodePoint(cp)]);
    assert.ok(combiningInk(text+'b',20,measure).glyphs.some(g=>g.annotation==='double'&&g.codepoint===cp));
  }
  for(const [text,ratio] of [['A⃞',1],['A⃢',2.134/1.362]]){
    const g=combiningInk(text,20,measure).glyphs.find(g=>g.annotation==='enclosure');
    const bounds=outlines.marks[g.codepoint].bounds;
    assert.ok(Math.abs((bounds[2]-bounds[0])*g.stretchX/(bounds[3]-bounds[1])-ratio)<.00001);
  }
});

test('joining scripts, exact emoji, CGJ and pathological depths retain native handling',()=>{
  for(const text of ['ب⃝','👨‍👩‍👧⃝','1️⃣','a͡͏́','A'+'⃝'.repeat(17)])assert.equal(annotationPlan(text),null,text);
  assert.equal(annotationPlan('A⃝⃞')?.operations.length,2);
  assert.equal(combiningInk('𓀀\u{13430}𓀁⃝',20,measure),null);
  for(const mark of ['⃝','⃟','⃤']){
    const one=combiningInk('A'+mark,20,measure),sixteen=combiningInk('A'+mark.repeat(16),20,measure);
    assert.ok(sixteen.width<one.width+20*8,'same enclosures grow by padding and stroke, not exponentially');
  }
});

test('measurer uses identical composed ink for wrapping and painting',()=>{
  const ctx={measureText(text){return {width:12,actualBoundingBoxAscent:14,actualBoundingBoxDescent:0};}};
  const measured=createTextMeasurer(ctx,size=>`${size}px test`).ink('A⃝',20);
  assert.equal(measured.runs.length,1);
  assert.equal(measured.runs[0].text,'A⃝');
  assert.ok(measured.runs[0].glyphs.some(g=>g.annotation==='enclosure'));
  assert.ok(measured.width>12&&measured.ascent>14);
});
