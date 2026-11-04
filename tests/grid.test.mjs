import test from 'node:test';
import gridManifest from '../js/grid-manifest.js';
import assert from 'node:assert/strict';

test('grid lookup ranges are ordered and every delete checker form loads its custom drawing',()=>{
  for(let i=1;i<gridManifest.ranges.length;i++)assert.ok(gridManifest.ranges[i-1][1]<gridManifest.ranges[i][0]);
  for(const cp of [0x2427,0x2428,0x2429]){
    const result=requiredFonts([String.fromCodePoint(cp)]);
    assert.deepEqual(result.missing,[]);
    assert.ok(result.fonts.some(f=>f.family==='Dad Grid'));
  }
});
import {isGridSymbol,isGridText,cellColumns,gridRows} from '../js/grid.js';
import {createTextMeasurer} from '../js/text-metrics.js';
import {layoutColumn,layoutText,makePanel} from '../js/layout.js';
import {requiredFonts} from '../js/fonts.js';
const ctx = {font:'10px Font',measureText(text) {
  const size=parseFloat(this.font);
  return {width:[...text].length*size*0.6,actualBoundingBoxAscent:size*0.7,actualBoundingBoxDescent:0};
}};
const measure = createTextMeasurer(ctx,size=>`${size}px Font`);

test('automatic diagram detection leaves ordinary prose alone', () => {
  for (const text of ['┌─┐\n│A│\n└─┘','⠁⠂⠄','█ ░▒▓','+---+\n| x |\n+---+']) assert.equal(isGridText(text),true);
  for (const text of ['Hello\nworld','a+b=c','A — B','| maybe |','☐ task',
    'Use ─ as a rule in this sentence.','This Braille letter is ⠁ and this is ⠂.',
    'A single █ can represent a filled cell.','A long sentence mentioning ░▒▓ still needs normal wrapping.']) assert.equal(isGridText(text),false,text);
  for(const text of ['A──B','│a long native label│','┌───┐\n│ x │\n└───┘'])assert.equal(isGridText(text),true,text);
  assert.ok(requiredFonts(['┌─┐ ⠁']).fonts.some(f=>f.family==='Dad Grid'));
});

test('inline structural symbols wrap as prose while their custom drawing font still loads',()=>{
  const text='A long sentence with a █ symbol and Braille ⠁ inside ordinary dialogue.';
  const {lines}=layoutColumn(text,{measure,fontSize:10,width:90});
  assert.ok(lines.length>1);
  assert.ok(lines.every(line=>!line.grid));
  assert.equal(lines.flatMap(l=>l.units).join(''),text);
  assert.ok(requiredFonts([text]).fonts.some(f=>f.family==='Dad Grid'));
});

test('cell counts use fullwidth, halfwidth, graphemes, emoji and real tab stops', () => {
  for (const [text,n] of [['Ａ',2],['界',2],['ｶ',1],['e\u0301',1],['👩🏽‍🚀',2],['🇫🇷',2],['\u2067',0]]) assert.equal(cellColumns(text),n,text);
  assert.deepEqual(gridRows('界\tA\ne\u0301\tB\n\nEND'), ['界  A','e\u0301   B','','END']);
});

test('diagram rows keep one origin, rectangular extent, all spaces and blank rows', () => {
  const text = '┌────┐\n│ A  │\n│    │\n└────┘\n\n   ⠁';
  const {lines,fits}=layoutColumn(text,{measure,fontSize:10,width:100});
  assert.equal(fits,true);
  assert.equal(lines.map(l=>l.text).join('\n'),text);
  assert.equal(new Set(lines.map(l=>l.x)).size,1);
  assert.equal(new Set(lines.map(l=>l.width)).size,1);
  for(let i=1;i<lines.length;i++) assert.ok(Math.abs(lines[i].y-lines[i-1].y-lines[i].height)<1e-9);
  assert.ok(lines.every(l=>l.grid));
});

test('a diagram never reflows or breaks apart when it is wider than the panel', () => {
  const text='┌───────────┐\n│abcdef     │\n└───────────┘';
  const narrow=layoutColumn(text,{measure,fontSize:10,width:30});
  assert.equal(narrow.fits,false);
  assert.equal(narrow.lines.map(l=>l.text).join('\n'),text);
  const panel=makePanel({width:30,height:1,free:[]},30,200,0);
  const fitted=layoutText(panel,text,{measure,fontSize:10,fitUnbreakable:true});
  assert.equal(fitted.fits,true);
  assert.equal(fitted.lines.map(l=>l.text).join('\n'),text);
  assert.ok(fitted.lines.every(l=>l.width<=30 && l.fontSize<10));
  assert.equal(new Set(fitted.lines.map(l=>l.fontSize)).size,1);
});

test('native words remain intact and combining marks never become separate cells', () => {
  const block=measure.grid('│مرحبا بالعالم│\n│e\u0301   │',10);
  assert.ok(block.rows[0].ink.runs.some(r=>r.text==='مرحبا بالعالم' && r.direction==='rtl'));
  assert.ok(block.rows[1].ink.runs.some(r=>r.drawText==='e\u0301'));
  assert.ok(!block.rows[1].ink.runs.some(r=>r.drawText==='\u0301'));
});

test('complex labels resolve mixed direction as a field without moving structural cells', () => {
  const block=measure.grid('│مرحبا 123 عالم│',10);
  const runs=block.rows[0].ink.runs;
  assert.equal(runs[0].text,'│');
  assert.equal(runs.at(-1).text,'│');
  assert.deepEqual(runs.slice(1,-1).map(r=>r.text),[' عالم','123','مرحبا ']);
  assert.ok(runs.every((r,i)=>!i || r.offset>=runs[i-1].offset));
});

test('CJK and fullwidth labels occupy individual two-cell slots', () => {
  const block=measure.grid('│界 Ａ│',10);
  const runs=block.rows[0].ink.runs;
  assert.deepEqual(runs.map(r=>r.text),['│','界','Ａ','│']);
  const width=block.lineHeight*0.6;
  assert.ok(Math.abs(runs.at(-1).offset-6*width)<1e-6);
});


test('legacy structural symbols trigger exact one-cell grids without pictorial capture', () => {
  for (const cp of [0x1cc20,0x1cc2f,0x1cd00,0x1ce1a,0x1ce90,0x1fb00,0x1fbd0]) {
    const text=String.fromCodePoint(cp);
    assert.ok(isGridSymbol(text));
    assert.ok(isGridText(text));
    assert.equal(cellColumns(text),1);
    assert.ok(requiredFonts([text]).fonts.some(f=>f.family==='Dad Grid'));
  }
  for (const cp of [0x1cc00,0x1cc50,0x1ccf0,0x1fbf0]) {
    assert.equal(isGridSymbol(String.fromCodePoint(cp)),false);
    assert.equal(isGridText(String.fromCodePoint(cp)),false);
  }
});

test('legacy connecting pieces trigger grids while standalone pictures stay in prose',()=>{
  for(const cp of [0x1cc05,0x1cc30,0x1cca6,0x1ccb2,0x1cde6,0x1fbe0]) assert.ok(isGridSymbol(String.fromCodePoint(cp)));
  for(const cp of [0x1cc00,0x1cc4a,0x1cc92,0x1ccd6,0x1f8b2]) {
    const c=String.fromCodePoint(cp);
    assert.equal(isGridSymbol(c),false);
    assert.equal(isGridText('LOOK '+c),false);
    assert.ok(requiredFonts([c]).fonts.some(f=>f.family==='Dad Grid'));
  }
});

test('legacy constructions preserve square source cells and align mixed box edges',()=>{
  const block=measure.grid('𜰰𜰱𜰲𜰳\n𜰴𜰵𜰶𜰷\n𜰸𜰹𜰺𜰻\n𜰼𜰽𜰾𜰿',10);
  assert.equal(block.width,block.height);
  assert.ok(block.rows.every(row=>row.ink.runs.every(run=>Math.abs(run.scaleX-5/3)<1e-8)));
  const mixed=measure.grid('─𜰉─',10);
  assert.equal(mixed.width,3*mixed.lineHeight);
  assert.deepEqual(mixed.rows[0].ink.runs.map(r=>r.offset),[0,mixed.lineHeight,2*mixed.lineHeight]);
  const ordinary=measure.grid('───',10);
  assert.ok(Math.abs(ordinary.width-3*ordinary.lineHeight*.6)<1e-8);
});
