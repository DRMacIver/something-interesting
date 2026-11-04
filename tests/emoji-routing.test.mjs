import test from 'node:test';
import assert from 'node:assert/strict';

test('a leading keycap combining mark is text rather than an unsupported emoji',()=>{
  assert.equal(emojiPolicy('\u20e3'),'text');
  assert.equal(emojiPolicy('\u20e3\u20e3'),'text');
  assert.equal(emojiPolicy(' \u20e3'),'text');
  assert.equal(emojiPolicy('A\u20e3'),'text');
  const loaded=requiredFonts(['\u20e3']);
  assert.deepEqual(loaded.missing,[]);
  assert.deepEqual(loaded.emojiFallbacks,[]);
  assert.ok(loaded.fonts.length>0);
});
import {readFileSync} from 'node:fs';
import emoji from '../js/emoji-manifest.js';
import {emojiPolicy,fontRuns,routeDirectionalRun} from '../js/emoji-routing.js';
import {createTextMeasurer} from '../js/text-metrics.js';
import {requiredFonts} from '../js/fonts.js';
import {layoutColumn} from '../js/layout.js';

test('custom selection is exact and never captures part of an unsupported cluster', () => {
  for(const text of emoji.sequences) assert.equal(emojiPolicy(text),'custom',text);
  for(const text of ['👨‍👦‍👦‍👦','👨‍👩‍👧‍👦‍👦','🏳️‍🌈‍🌈','🐦‍🔥‍🔥','🇦🇦','😀\u0301']) assert.equal(emojiPolicy(text),'native',text);
  assert.equal(emojiPolicy('☎︎'),'custom', 'registered text form now has a custom monochrome drawing');
  assert.equal(emojiPolicy('😀\ufe0e'),'native', 'unregistered VS15 must not invent text presentation');
  assert.deepEqual(fontRuns('A😀👨‍👦‍👦‍👦B').map(r=>[r.text,r.emojiPolicy]),[['A','text'],['😀','custom'],['👨‍👦‍👦‍👦','native'],['B','text']]);
});

test('standalone components are visible without capturing unknown flags or malformed compounds',()=>{
  const points=[...Array.from({length:26},(_,i)=>0x1f1e6+i),...Array.from({length:5},(_,i)=>0x1f3fb+i),...Array.from({length:4},(_,i)=>0x1f9b0+i)];
  for(const cp of points){
    const text=String.fromCodePoint(cp);
    assert.equal(emojiPolicy(text),'custom',text);
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    assert.ok(!emoji.componentOnly.includes(cp));
  }
  for(const text of ['🇦🇦','🇦🏻','🏻🏼','🦰\u200d🦱','👍🏻🏼']){
    assert.equal(emojiPolicy(text),'native',text);
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'native'}]);
  }
  for(const text of ['🇬🇧','👍🏻','🧑🏽‍🦰'])assert.equal(emojiPolicy(text),'custom',text);
});

test('space-attached standalone tones keep whitespace and load custom swatches',()=>{
  for(const space of [' ','\u00a0','\u2003'])for(const tone of [...'🏻🏼🏽🏾🏿']){
    const text='A'+space+tone+' B';
    const runs=fontRuns(text);
    assert.equal(runs.map(r=>r.text).join(''),text);
    assert.deepEqual(runs.map(r=>[r.text,r.emojiPolicy]),[['A'+space,'text'],[tone,'custom'],[' B','text']]);
    const selection=requiredFonts([text]);
    assert.deepEqual(selection.missing,[]);
    assert.deepEqual(selection.emojiFallbacks,[]);
    assert.ok(selection.fonts.some(f=>f.family==='Dad Emoji'));
  }
  for(const text of [' 🏽🏾',' 🏽\u200d'])assert.ok(fontRuns(text).every(r=>r.emojiPolicy==='native'));
});

test('every pinned emoji sequence stays intact during font routing', () => {
  const supported=new Set(emoji.sequences);
  for(const file of ['emoji-sequences','emoji-zwj-sequences']) {
    const data=readFileSync(new URL(`../data/unicode/18.0.0/emoji/${file}.txt`,import.meta.url),'utf8');
    for(const line of data.split('\n')) {
      const body=line.split('#')[0].trim(); if(!body) continue;
      const points=body.split(';')[0].trim();
      const texts=[];
      if(points.includes('..')) {
        const [start,end]=points.split('..').map(cp=>parseInt(cp,16));
        for(let cp=start;cp<=end;cp++) texts.push(String.fromCodePoint(cp));
      } else texts.push(points.split(/\s+/).map(cp=>String.fromCodePoint(parseInt(cp,16))).join(''));
      for(const text of texts) {
        const runs=fontRuns(text);
        assert.equal(runs.length,1,line); assert.equal(runs[0].text,text,line);
        assert.equal(runs[0].emojiPolicy,supported.has(text)?'custom':'native',line);
      }
    }
  }
});

test('font spans inside RTL runs follow visual order without reversing clusters', () => {
  const runs=routeDirectionalRun({text:'א😀👨‍👦‍👦‍👦ב',drawText:'\u202eא😀👨‍👦‍👦‍👦ב\u202c',direction:'rtl'});
  assert.deepEqual(runs.map(r=>r.text),['ב','👨‍👦‍👦‍👦','😀','א']);
  assert.ok(runs.every(r=>r.drawText==='\u202e'+r.text+'\u202c'));
});

test('measurement and wrapping retain each font policy and its actual metrics', () => {
  const ctx={measureText(text){const size=parseFloat(this.font);return {width:[...text.replace(/[\u202a-\u202e]/gu,'')].length*size,
    actualBoundingBoxAscent:size*(this.font.includes('custom')?1.1:0.7),actualBoundingBoxDescent:size*0.1};}};
  const measure=createTextMeasurer(ctx,(size,policy)=>`${size}px ${policy}`);
  const {lines}=layoutColumn('A 😀 👨‍👦‍👦‍👦 B',{measure,fontSize:10,width:100});
  const runs=lines.flatMap(l=>l.ink.runs??[]);
  assert.ok(runs.some(r=>r.font==='14px custom' && r.text.includes('😀')));
  assert.ok(runs.some(r=>r.font==='10px native' && r.text==='👨‍👦‍👦‍👦'));
  assert.ok(lines.every(l=>l.baseline>=l.ink.ascent && l.height>=l.baseline+l.ink.descent));
});


test('keycap sequences route as complete custom clusters without capturing plain text', () => {
  for (const c of '#*0123456789') {
    assert.equal(emojiPolicy(c),'text');
    assert.equal(emojiPolicy(c+'\ufe0e'),'text');
    for (const selector of ['', '\ufe0f']) assert.equal(emojiPolicy(c+selector+'\u20e3'),'custom');
    assert.equal(emojiPolicy(c+'\ufe0f'),'native');
  }
});

test('hand modifiers use exact custom pairs without capturing malformed clusters',()=>{
  for (const hand of [...'✊✋🖐🖖👌🤌🤏✌🤞🫰🤟🤘🤙👈👉👆🖕👇☝👎👊🤛🤜🤚👋🫱🫲🫳🫴🫵🫶🫷🫸👏👐🙌🙏🤲🤝']) {
    assert.equal(emojiPolicy(hand),'custom');
    for (const tone of [...'🏻🏼🏽🏾🏿']) {
      assert.equal(emojiPolicy(hand+tone),'custom');
      assert.deepEqual(fontRuns(hand+tone),[{text:hand+tone,emojiPolicy:'custom'}]);
      assert.equal(emojiPolicy(hand+tone+tone),'native');
    }
  }
});

test('standalone Egyptian rotations have a separate font policy without breaking quadrats', async () => {
  const {default:variants}=await import('../js/egyptian-variant-manifest.js');
  for (const sequence of variants.variationSequences) {
    assert.deepEqual(fontRuns(sequence).map(r=>r.emojiPolicy),['egyptian-variant']);
    assert.deepEqual(fontRuns([...sequence][0]).map(r=>r.emojiPolicy),['text']);
  }
  assert.equal(fontRuns('𓄹 𓄹\ufe03')[0].emojiPolicy,'egyptian-variant', 'unrotated comparison uses the same native drawing');
  const composed='𓀀\u{13430}𓄹\ufe03';
  assert.deepEqual(fontRuns(composed),[{text:composed,emojiPolicy:'text'}]);
});

test('compound-only components and unregistered forms do not become custom drawings', () => {
  for (const cp of emoji.componentOnly) {
    const symbol=String.fromCodePoint(cp);
    assert.notEqual(emojiPolicy(symbol),'custom',symbol);
    assert.notEqual(emojiPolicy(symbol+'\ufe0f'),'custom',symbol);
  }
  for (const text of ['😶‍🌫︎','🙂‍↔︎','🙂‍↕︎','🐻‍❄︎','⛓︎‍💥','🐈‍⬜']) {
    assert.notEqual(emojiPolicy(text),'custom',text);
  }
  assert.deepEqual(fontRuns('😮‍💨😵‍💫').map(r=>[r.text,r.emojiPolicy]),[['😮‍💨😵‍💫','custom']]);
});

test('building drawings use the custom font as whole emoji clusters', () => {
  for (const symbol of [...'🏠🏡🏢🏣🏤🏥🏦🏨🏩🏪🏫🏬🏭🏯🏰💒⛪🕌🛕🕍⛩🕋⛲🛖']) {
    assert.equal(emojiPolicy(symbol),'custom',symbol);
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
});

test('landscape and travel drawings use the custom font', () => {
  for (const symbol of [...'🏔⛰🌋🗻🏕🏖🏜🏝🏞🏟🏛🏗🏘🏚🌁🌃🏙🌄🌅🌆🌇🌉♨🎠🎡🎢🗼🗽🗾🗺🌐🧭']) {
    assert.equal(emojiPolicy(symbol),'custom',symbol);
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
});


test('timepieces and stationery use custom whole-cluster drawings', () => {
  for (const symbol of [...'⌚⏰⏱⏲🕰⌛⏳✏✒🖋🖊🖌🖍📝💼📁📂🗂📅📆🗒🗓📇📋📌📍📎🖇📏📐✂🗃🗄🗑']) {
    assert.equal(emojiPolicy(symbol),'custom',symbol);
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
});


test('produce and coloured apples use custom whole-cluster drawings', () => {
  for (const symbol of [...'🍇🍈🍉🍊🍋🍌🍍🥭🍐🍑🍒🍓🫐🥝🍅🫒🥥🥑🍆🥔🥕🌽🌶🫑🥒🥬🥦🧄🧅🥜🫘🌰🫚🫛🍎🍏']) {
    assert.equal(emojiPolicy(symbol),'custom',symbol);
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
});

test('lime and brown mushroom remain exact custom sequences', () => {
  for (const sequence of ['🍋‍🟩','🍄‍🟫']) {
    assert.equal(emojiPolicy(sequence),'custom');
    assert.deepEqual(fontRuns(sequence),[{text:sequence,emojiPolicy:'custom'}]);
    assert.equal(emojiPolicy(sequence+'\ufe0e'),'native');
  }
  for (const sequence of ['🍋‍🟫','🍄‍🟩']) assert.equal(emojiPolicy(sequence),'native');
});

test('mixed handshakes retain tone order and reject unregistered combinations',()=>{
  for (const a of [...'🏻🏼🏽🏾🏿']) for (const b of [...'🏻🏼🏽🏾🏿']) {
    const text='🫱'+a+'‍🫲'+b;
    assert.equal(emojiPolicy(text),a===b?'native':'custom');
    if(a!==b) assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    for(const bad of ['🫲'+a+'‍🫱'+b,text+'\ufe0f',text+'\ufe0e',text+a])
      assert.equal(emojiPolicy(bad),'native');
  }
});


test('clothing draws whole clusters and promotes the service-dog vest',()=>{
  for(const symbol of [...'👑👒🎩🎓🧢🪖⛑🧣🧤🧥🧦👔👕👖👗👘🥻🩱🩲🩳👙👚👛👜👝🎒🩴👞👟🥾🥿👠👡🩰👢🥼🦺🥽']) {
    assert.equal(emojiPolicy(symbol),'custom');
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
  assert.ok(!emoji.componentOnly.includes(0x1f9ba));
  assert.equal(emojiPolicy('🐕‍🦺'),'custom');
  assert.equal(emojiPolicy('🦺‍🐕'),'native');
  for(const symbol of ['⛑','🎓']) for(const vs of ['\ufe0e','\ufe0f'])
    assert.equal(emojiPolicy(symbol+vs),'custom');
  assert.equal(emojiPolicy('👕\ufe0e'),'native');
});


test('electronics use exact custom bases and registered selectors',()=>{
  for(const symbol of [...'📱📲☎📞📟📠🔋🪫🔌💻🖥🖨⌨🖱🖲💽💾💿📀🧮🎥🎞📽🎬📺📷📸📹📼🔍🔎🕯💡🔦🏮🪔']) {
    assert.equal(emojiPolicy(symbol),'custom');
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
  for(const symbol of ['☎','⌨','🖥','🖨','🖱','🖲','🎞','📽','🕯'])
    for(const vs of ['\ufe0e','\ufe0f']) assert.equal(emojiPolicy(symbol+vs),'custom');
  assert.equal(emojiPolicy('📱\ufe0e'),'native');
});


test('celebrations use exact custom bases and registered selectors',()=>{
  for(const symbol of [...'🎀🎁🎃🎄🎆🎇🧨🎈🎉🎊🎋🎍🎎🎏🎐🎑🎟🎫']) {
    assert.equal(emojiPolicy(symbol),'custom');
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
  for(const sequence of ["🎟︎", "🎟️"])
    assert.equal(emojiPolicy(sequence),'custom');
  assert.equal(emojiPolicy('🧨\ufe0e'),'native');
});


test('games toys and art supplies use exact custom bases and registered selectors',()=>{
  for(const symbol of [...'🎯🪀🪁🎱🔮🪄🎮🕹🎰🎲🧩🧸🪅🪩🪆🃏🎴🎭🖼🎨🧵🪡🧶🪢🎪']) {
    assert.equal(emojiPolicy(symbol),'custom');
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
  for(const sequence of ["🎭︎", "🎭️", "🎮︎", "🎮️", "🕹︎", "🕹️", "🖼︎", "🖼️"])
    assert.equal(emojiPolicy(sequence),'custom');
  assert.equal(emojiPolicy('🧸\ufe0e'),'native');
});


test('household and scientific objects use exact custom bases and registered selectors',()=>{
  for(const symbol of [...'🚪🛗🪞🪟🛏🛋🪑🚽🪠🚿🛁🪒🧴🧷🧹🧺🧻🪣🧼🫧🪥🧽🛒🧳⚗🧪🧫🧬🔬🔭📡🩺🩻🩼💊💉']) {
    assert.equal(emojiPolicy(symbol),'custom');
    assert.deepEqual(fontRuns(symbol),[{text:symbol,emojiPolicy:'custom'}]);
  }
  for(const sequence of ["⚗︎", "⚗️", "🛋︎", "🛋️", "🛏︎", "🛏️"])
    assert.equal(emojiPolicy(sequence),'custom');
  assert.equal(emojiPolicy('🧬\ufe0e'),'native');
});


test('people and exact tones use custom drawings without swallowing astronaut sequences',()=>{
  for(const person of [...'👶🧒👦👧🧑👨👩🧓👴👵🧔']) {
    for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
      const text=person+tone;
      assert.equal(emojiPolicy(text),'custom');
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    }
  }
  for(const tone of ['',...'🏻🏼🏽🏾🏿']) assert.equal(emojiPolicy('🧑'+tone+'‍🚀'),'custom');
  assert.equal(emojiPolicy('🧑\ufe0e'),'native');
  // A supported person prefix must not split a unregistered longer ZWJ form.
  for(const text of ['🧑🏽‍🦽‍🦯','👩🏿‍🦯‍🦼','👨🏻‍🦼‍🦽']) {
    assert.equal(emojiPolicy(text),'native');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'native'}]);
  }
});


test('person hair and gender forms support all registered qualification and tone variants',()=>{
  for(const text of ["👨‍🦰", "👨‍🦱", "👨‍🦲", "👨‍🦳", "👨🏻‍🦰", "👨🏻‍🦱", "👨🏻‍🦲", "👨🏻‍🦳", "👨🏼‍🦰", "👨🏼‍🦱", "👨🏼‍🦲", "👨🏼‍🦳", "👨🏽‍🦰", "👨🏽‍🦱", "👨🏽‍🦲", "👨🏽‍🦳", "👨🏾‍🦰", "👨🏾‍🦱", "👨🏾‍🦲", "👨🏾‍🦳", "👨🏿‍🦰", "👨🏿‍🦱", "👨🏿‍🦲", "👨🏿‍🦳", "👩‍🦰", "👩‍🦱", "👩‍🦲", "👩‍🦳", "👩🏻‍🦰", "👩🏻‍🦱", "👩🏻‍🦲", "👩🏻‍🦳", "👩🏼‍🦰", "👩🏼‍🦱", "👩🏼‍🦲", "👩🏼‍🦳", "👩🏽‍🦰", "👩🏽‍🦱", "👩🏽‍🦲", "👩🏽‍🦳", "👩🏾‍🦰", "👩🏾‍🦱", "👩🏾‍🦲", "👩🏾‍🦳", "👩🏿‍🦰", "👩🏿‍🦱", "👩🏿‍🦲", "👩🏿‍🦳", "👱", "👱‍♀", "👱‍♀️", "👱‍♂", "👱‍♂️", "👱🏻", "👱🏻‍♀", "👱🏻‍♀️", "👱🏻‍♂", "👱🏻‍♂️", "👱🏼", "👱🏼‍♀", "👱🏼‍♀️", "👱🏼‍♂", "👱🏼‍♂️", "👱🏽", "👱🏽‍♀", "👱🏽‍♀️", "👱🏽‍♂", "👱🏽‍♂️", "👱🏾", "👱🏾‍♀", "👱🏾‍♀️", "👱🏾‍♂", "👱🏾‍♂️", "👱🏿", "👱🏿‍♀", "👱🏿‍♀️", "👱🏿‍♂", "👱🏿‍♂️", "🧑‍🦰", "🧑‍🦱", "🧑‍🦲", "🧑‍🦳", "🧑🏻‍🦰", "🧑🏻‍🦱", "🧑🏻‍🦲", "🧑🏻‍🦳", "🧑🏼‍🦰", "🧑🏼‍🦱", "🧑🏼‍🦲", "🧑🏼‍🦳", "🧑🏽‍🦰", "🧑🏽‍🦱", "🧑🏽‍🦲", "🧑🏽‍🦳", "🧑🏾‍🦰", "🧑🏾‍🦱", "🧑🏾‍🦲", "🧑🏾‍🦳", "🧑🏿‍🦰", "🧑🏿‍🦱", "🧑🏿‍🦲", "🧑🏿‍🦳", "🧔‍♀", "🧔‍♀️", "🧔‍♂", "🧔‍♂️", "🧔🏻‍♀", "🧔🏻‍♀️", "🧔🏻‍♂", "🧔🏻‍♂️", "🧔🏼‍♀", "🧔🏼‍♀️", "🧔🏼‍♂", "🧔🏼‍♂️", "🧔🏽‍♀", "🧔🏽‍♀️", "🧔🏽‍♂", "🧔🏽‍♂️", "🧔🏾‍♀", "🧔🏾‍♀️", "🧔🏾‍♂", "🧔🏾‍♂️", "🧔🏿‍♀", "🧔🏿‍♀️", "🧔🏿‍♂", "🧔🏿‍♂️"]) {
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});


test('occupation forms support every registered qualification and tone variant',()=>{
  for(const text of ["👨‍⚕", "👨‍⚕️", "👨‍⚖", "👨‍⚖️", "👨‍✈", "👨‍✈️", "👨‍🌾", "👨‍🍳", "👨‍🎓", "👨‍🎤", "👨‍🎨", "👨‍🏫", "👨‍🏭", "👨‍💻", "👨‍💼", "👨‍🔧", "👨‍🔬", "👨‍🚀", "👨‍🚒", "👨🏻‍⚕", "👨🏻‍⚕️", "👨🏻‍⚖", "👨🏻‍⚖️", "👨🏻‍✈", "👨🏻‍✈️", "👨🏻‍🌾", "👨🏻‍🍳", "👨🏻‍🎓", "👨🏻‍🎤", "👨🏻‍🎨", "👨🏻‍🏫", "👨🏻‍🏭", "👨🏻‍💻", "👨🏻‍💼", "👨🏻‍🔧", "👨🏻‍🔬", "👨🏻‍🚀", "👨🏻‍🚒", "👨🏼‍⚕", "👨🏼‍⚕️", "👨🏼‍⚖", "👨🏼‍⚖️", "👨🏼‍✈", "👨🏼‍✈️", "👨🏼‍🌾", "👨🏼‍🍳", "👨🏼‍🎓", "👨🏼‍🎤", "👨🏼‍🎨", "👨🏼‍🏫", "👨🏼‍🏭", "👨🏼‍💻", "👨🏼‍💼", "👨🏼‍🔧", "👨🏼‍🔬", "👨🏼‍🚀", "👨🏼‍🚒", "👨🏽‍⚕", "👨🏽‍⚕️", "👨🏽‍⚖", "👨🏽‍⚖️", "👨🏽‍✈", "👨🏽‍✈️", "👨🏽‍🌾", "👨🏽‍🍳", "👨🏽‍🎓", "👨🏽‍🎤", "👨🏽‍🎨", "👨🏽‍🏫", "👨🏽‍🏭", "👨🏽‍💻", "👨🏽‍💼", "👨🏽‍🔧", "👨🏽‍🔬", "👨🏽‍🚀", "👨🏽‍🚒", "👨🏾‍⚕", "👨🏾‍⚕️", "👨🏾‍⚖", "👨🏾‍⚖️", "👨🏾‍✈", "👨🏾‍✈️", "👨🏾‍🌾", "👨🏾‍🍳", "👨🏾‍🎓", "👨🏾‍🎤", "👨🏾‍🎨", "👨🏾‍🏫", "👨🏾‍🏭", "👨🏾‍💻", "👨🏾‍💼", "👨🏾‍🔧", "👨🏾‍🔬", "👨🏾‍🚀", "👨🏾‍🚒", "👨🏿‍⚕", "👨🏿‍⚕️", "👨🏿‍⚖", "👨🏿‍⚖️", "👨🏿‍✈", "👨🏿‍✈️", "👨🏿‍🌾", "👨🏿‍🍳", "👨🏿‍🎓", "👨🏿‍🎤", "👨🏿‍🎨", "👨🏿‍🏫", "👨🏿‍🏭", "👨🏿‍💻", "👨🏿‍💼", "👨🏿‍🔧", "👨🏿‍🔬", "👨🏿‍🚀", "👨🏿‍🚒", "👩‍⚕", "👩‍⚕️", "👩‍⚖", "👩‍⚖️", "👩‍✈", "👩‍✈️", "👩‍🌾", "👩‍🍳", "👩‍🎓", "👩‍🎤", "👩‍🎨", "👩‍🏫", "👩‍🏭", "👩‍💻", "👩‍💼", "👩‍🔧", "👩‍🔬", "👩‍🚀", "👩‍🚒", "👩🏻‍⚕", "👩🏻‍⚕️", "👩🏻‍⚖", "👩🏻‍⚖️", "👩🏻‍✈", "👩🏻‍✈️", "👩🏻‍🌾", "👩🏻‍🍳", "👩🏻‍🎓", "👩🏻‍🎤", "👩🏻‍🎨", "👩🏻‍🏫", "👩🏻‍🏭", "👩🏻‍💻", "👩🏻‍💼", "👩🏻‍🔧", "👩🏻‍🔬", "👩🏻‍🚀", "👩🏻‍🚒", "👩🏼‍⚕", "👩🏼‍⚕️", "👩🏼‍⚖", "👩🏼‍⚖️", "👩🏼‍✈", "👩🏼‍✈️", "👩🏼‍🌾", "👩🏼‍🍳", "👩🏼‍🎓", "👩🏼‍🎤", "👩🏼‍🎨", "👩🏼‍🏫", "👩🏼‍🏭", "👩🏼‍💻", "👩🏼‍💼", "👩🏼‍🔧", "👩🏼‍🔬", "👩🏼‍🚀", "👩🏼‍🚒", "👩🏽‍⚕", "👩🏽‍⚕️", "👩🏽‍⚖", "👩🏽‍⚖️", "👩🏽‍✈", "👩🏽‍✈️", "👩🏽‍🌾", "👩🏽‍🍳", "👩🏽‍🎓", "👩🏽‍🎤", "👩🏽‍🎨", "👩🏽‍🏫", "👩🏽‍🏭", "👩🏽‍💻", "👩🏽‍💼", "👩🏽‍🔧", "👩🏽‍🔬", "👩🏽‍🚀", "👩🏽‍🚒", "👩🏾‍⚕", "👩🏾‍⚕️", "👩🏾‍⚖", "👩🏾‍⚖️", "👩🏾‍✈", "👩🏾‍✈️", "👩🏾‍🌾", "👩🏾‍🍳", "👩🏾‍🎓", "👩🏾‍🎤", "👩🏾‍🎨", "👩🏾‍🏫", "👩🏾‍🏭", "👩🏾‍💻", "👩🏾‍💼", "👩🏾‍🔧", "👩🏾‍🔬", "👩🏾‍🚀", "👩🏾‍🚒", "👩🏿‍⚕", "👩🏿‍⚕️", "👩🏿‍⚖", "👩🏿‍⚖️", "👩🏿‍✈", "👩🏿‍✈️", "👩🏿‍🌾", "👩🏿‍🍳", "👩🏿‍🎓", "👩🏿‍🎤", "👩🏿‍🎨", "👩🏿‍🏫", "👩🏿‍🏭", "👩🏿‍💻", "👩🏿‍💼", "👩🏿‍🔧", "👩🏿‍🔬", "👩🏿‍🚀", "👩🏿‍🚒", "🧑‍⚕", "🧑‍⚕️", "🧑‍⚖", "🧑‍⚖️", "🧑‍✈", "🧑‍✈️", "🧑‍🌾", "🧑‍🍳", "🧑‍🎓", "🧑‍🎤", "🧑‍🎨", "🧑‍🏫", "🧑‍🏭", "🧑‍💻", "🧑‍💼", "🧑‍🔧", "🧑‍🔬", "🧑‍🚒", "🧑🏻‍⚕", "🧑🏻‍⚕️", "🧑🏻‍⚖", "🧑🏻‍⚖️", "🧑🏻‍✈", "🧑🏻‍✈️", "🧑🏻‍🌾", "🧑🏻‍🍳", "🧑🏻‍🎓", "🧑🏻‍🎤", "🧑🏻‍🎨", "🧑🏻‍🏫", "🧑🏻‍🏭", "🧑🏻‍💻", "🧑🏻‍💼", "🧑🏻‍🔧", "🧑🏻‍🔬", "🧑🏻‍🚒", "🧑🏼‍⚕", "🧑🏼‍⚕️", "🧑🏼‍⚖", "🧑🏼‍⚖️", "🧑🏼‍✈", "🧑🏼‍✈️", "🧑🏼‍🌾", "🧑🏼‍🍳", "🧑🏼‍🎓", "🧑🏼‍🎤", "🧑🏼‍🎨", "🧑🏼‍🏫", "🧑🏼‍🏭", "🧑🏼‍💻", "🧑🏼‍💼", "🧑🏼‍🔧", "🧑🏼‍🔬", "🧑🏼‍🚒", "🧑🏽‍⚕", "🧑🏽‍⚕️", "🧑🏽‍⚖", "🧑🏽‍⚖️", "🧑🏽‍✈", "🧑🏽‍✈️", "🧑🏽‍🌾", "🧑🏽‍🍳", "🧑🏽‍🎓", "🧑🏽‍🎤", "🧑🏽‍🎨", "🧑🏽‍🏫", "🧑🏽‍🏭", "🧑🏽‍💻", "🧑🏽‍💼", "🧑🏽‍🔧", "🧑🏽‍🔬", "🧑🏽‍🚒", "🧑🏾‍⚕", "🧑🏾‍⚕️", "🧑🏾‍⚖", "🧑🏾‍⚖️", "🧑🏾‍✈", "🧑🏾‍✈️", "🧑🏾‍🌾", "🧑🏾‍🍳", "🧑🏾‍🎓", "🧑🏾‍🎤", "🧑🏾‍🎨", "🧑🏾‍🏫", "🧑🏾‍🏭", "🧑🏾‍💻", "🧑🏾‍💼", "🧑🏾‍🔧", "🧑🏾‍🔬", "🧑🏾‍🚒", "🧑🏿‍⚕", "🧑🏿‍⚕️", "🧑🏿‍⚖", "🧑🏿‍⚖️", "🧑🏿‍✈", "🧑🏿‍✈️", "🧑🏿‍🌾", "🧑🏿‍🍳", "🧑🏿‍🎓", "🧑🏿‍🎤", "🧑🏿‍🎨", "🧑🏿‍🏫", "🧑🏿‍🏭", "🧑🏿‍💻", "🧑🏿‍💼", "🧑🏿‍🔧", "🧑🏿‍🔬", "🧑🏿‍🚒"]) {
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});


test('outlined role forms support every registered qualification and tone variant',()=>{
  for(const text of ["👮", "👮‍♀", "👮‍♀️", "👮‍♂", "👮‍♂️", "👮🏻", "👮🏻‍♀", "👮🏻‍♀️", "👮🏻‍♂", "👮🏻‍♂️", "👮🏼", "👮🏼‍♀", "👮🏼‍♀️", "👮🏼‍♂", "👮🏼‍♂️", "👮🏽", "👮🏽‍♀", "👮🏽‍♀️", "👮🏽‍♂", "👮🏽‍♂️", "👮🏾", "👮🏾‍♀", "👮🏾‍♀️", "👮🏾‍♂", "👮🏾‍♂️", "👮🏿", "👮🏿‍♀", "👮🏿‍♀️", "👮🏿‍♂", "👮🏿‍♂️", "👰", "👰‍♀", "👰‍♀️", "👰‍♂", "👰‍♂️", "👰🏻", "👰🏻‍♀", "👰🏻‍♀️", "👰🏻‍♂", "👰🏻‍♂️", "👰🏼", "👰🏼‍♀", "👰🏼‍♀️", "👰🏼‍♂", "👰🏼‍♂️", "👰🏽", "👰🏽‍♀", "👰🏽‍♀️", "👰🏽‍♂", "👰🏽‍♂️", "👰🏾", "👰🏾‍♀", "👰🏾‍♀️", "👰🏾‍♂", "👰🏾‍♂️", "👰🏿", "👰🏿‍♀", "👰🏿‍♀️", "👰🏿‍♂", "👰🏿‍♂️", "👲", "👲🏻", "👲🏼", "👲🏽", "👲🏾", "👲🏿", "👳", "👳‍♀", "👳‍♀️", "👳‍♂", "👳‍♂️", "👳🏻", "👳🏻‍♀", "👳🏻‍♀️", "👳🏻‍♂", "👳🏻‍♂️", "👳🏼", "👳🏼‍♀", "👳🏼‍♀️", "👳🏼‍♂", "👳🏼‍♂️", "👳🏽", "👳🏽‍♀", "👳🏽‍♀️", "👳🏽‍♂", "👳🏽‍♂️", "👳🏾", "👳🏾‍♀", "👳🏾‍♀️", "👳🏾‍♂", "👳🏾‍♂️", "👳🏿", "👳🏿‍♀", "👳🏿‍♀️", "👳🏿‍♂", "👳🏿‍♂️", "👷", "👷‍♀", "👷‍♀️", "👷‍♂", "👷‍♂️", "👷🏻", "👷🏻‍♀", "👷🏻‍♀️", "👷🏻‍♂", "👷🏻‍♂️", "👷🏼", "👷🏼‍♀", "👷🏼‍♀️", "👷🏼‍♂", "👷🏼‍♂️", "👷🏽", "👷🏽‍♀", "👷🏽‍♀️", "👷🏽‍♂", "👷🏽‍♂️", "👷🏾", "👷🏾‍♀", "👷🏾‍♀️", "👷🏾‍♂", "👷🏾‍♂️", "👷🏿", "👷🏿‍♀", "👷🏿‍♀️", "👷🏿‍♂", "👷🏿‍♂️", "👸", "👸🏻", "👸🏼", "👸🏽", "👸🏾", "👸🏿", "💂", "💂‍♀", "💂‍♀️", "💂‍♂", "💂‍♂️", "💂🏻", "💂🏻‍♀", "💂🏻‍♀️", "💂🏻‍♂", "💂🏻‍♂️", "💂🏼", "💂🏼‍♀", "💂🏼‍♀️", "💂🏼‍♂", "💂🏼‍♂️", "💂🏽", "💂🏽‍♀", "💂🏽‍♀️", "💂🏽‍♂", "💂🏽‍♂️", "💂🏾", "💂🏾‍♀", "💂🏾‍♀️", "💂🏾‍♂", "💂🏾‍♂️", "💂🏿", "💂🏿‍♀", "💂🏿‍♀️", "💂🏿‍♂", "💂🏿‍♂️", "🕵", "🕵‍♀", "🕵‍♀️", "🕵‍♂", "🕵‍♂️", "🕵️", "🕵️‍♀", "🕵️‍♀️", "🕵️‍♂", "🕵️‍♂️", "🕵🏻", "🕵🏻‍♀", "🕵🏻‍♀️", "🕵🏻‍♂", "🕵🏻‍♂️", "🕵🏼", "🕵🏼‍♀", "🕵🏼‍♀️", "🕵🏼‍♂", "🕵🏼‍♂️", "🕵🏽", "🕵🏽‍♀", "🕵🏽‍♀️", "🕵🏽‍♂", "🕵🏽‍♂️", "🕵🏾", "🕵🏾‍♀", "🕵🏾‍♀️", "🕵🏾‍♂", "🕵🏾‍♂️", "🕵🏿", "🕵🏿‍♀", "🕵🏿‍♀️", "🕵🏿‍♂", "🕵🏿‍♂️", "🤴", "🤴🏻", "🤴🏼", "🤴🏽", "🤴🏾", "🤴🏿", "🤵", "🤵‍♀", "🤵‍♀️", "🤵‍♂", "🤵‍♂️", "🤵🏻", "🤵🏻‍♀", "🤵🏻‍♀️", "🤵🏻‍♂", "🤵🏻‍♂️", "🤵🏼", "🤵🏼‍♀", "🤵🏼‍♀️", "🤵🏼‍♂", "🤵🏼‍♂️", "🤵🏽", "🤵🏽‍♀", "🤵🏽‍♀️", "🤵🏽‍♂", "🤵🏽‍♂️", "🤵🏾", "🤵🏾‍♀", "🤵🏾‍♀️", "🤵🏾‍♂", "🤵🏾‍♂️", "🤵🏿", "🤵🏿‍♀", "🤵🏿‍♀️", "🤵🏿‍♂", "🤵🏿‍♂️", "🥷", "🥷🏻", "🥷🏼", "🥷🏽", "🥷🏾", "🥷🏿", "🧕", "🧕🏻", "🧕🏼", "🧕🏽", "🧕🏾", "🧕🏿", "🫅", "🫅🏻", "🫅🏼", "🫅🏽", "🫅🏾", "🫅🏿"]) {
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});


test('detailed pregnancy and feeding forms route with every skin tone',()=>{
  for(const text of ["👩‍🍼", "👩🏻‍🍼", "👩🏼‍🍼", "👩🏽‍🍼", "👩🏾‍🍼", "👩🏿‍🍼", "🧑‍🍼", "🧑🏻‍🍼", "🧑🏼‍🍼", "🧑🏽‍🍼", "🧑🏾‍🍼", "🧑🏿‍🍼", "🤱", "🤱🏻", "🤱🏼", "🤱🏽", "🤱🏾", "🤱🏿", "🤰", "🤰🏻", "🤰🏼", "🤰🏽", "🤰🏾", "🤰🏿", "🫃", "🫃🏻", "🫃🏼", "🫃🏽", "🫃🏾", "🫃🏿", "🫄", "🫄🏻", "🫄🏼", "🫄🏽", "🫄🏾", "🫄🏿", "👨‍🍼", "👨🏻‍🍼", "👨🏼‍🍼", "👨🏽‍🍼", "👨🏾‍🍼", "👨🏿‍🍼"]) {
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('new SVG emoji keep their identities beside related existing drawings', () => {
  for(const text of ['🪾','🫆','🫝','🪉','🪊','🪏']) assert.equal(emojiPolicy(text),'custom');
  assert.deepEqual(fontRuns('🪾 🌳 🫆 👆 🫝 🥒').filter(r=>r.emojiPolicy==='custom').map(r=>r.text).join('').replaceAll(' ',''),'🪾🌳🫆👆🫝🥒');
});

test('standalone rocket and transport variants do not split astronaut clusters', () => {
  for(const text of [...'🚀🚁🚉🚊🚋🚏🚒🚓🚖🚞🚟🚠🚡🛴🛵🛫🛬🛝🛞🛟🛢','🛢️','🛢︎']) assert.equal(emojiPolicy(text),'custom');
  for(const person of ['🧑','👨','👩']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const sequence=person+tone+'‍🚀';assert.equal(emojiPolicy(sequence),'custom');
    assert.deepEqual(fontRuns('🚀 '+sequence+' 🚀').filter(r=>r.emojiPolicy==='custom').map(r=>r.text),['🚀',sequence,'🚀']);
  }
});

test('directional thumbs retain every skin tone as a custom grapheme',()=>{
  for(const base of ['🫹','🫺']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const text=base+tone;
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
  for(const text of ['🫌','🪎']) assert.equal(emojiPolicy(text),'custom');
});

test('person gesture gender and tone forms retain a single custom cluster',()=>{
  for(const base of [...'💁🙅🙆🙋🙍🙎🙇🤦🤷🧏']) for(const gender of ['','‍♂️','‍♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const text=base+tone+gender;
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('activity tones, genders and directions route as one custom cluster', () => {
  for(const base of [...'🏃🚶🧎🧍']) for(const gender of ['','‍♂️','‍♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) for(const direction of (base==='🧍'?['']:['','‍➡️'])) {
    const text=base+tone+gender+direction;
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('individual dancers retain all custom skin-tone forms',()=>{
  for(const base of ['💃','🕺']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const text=base+tone;assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('sauna, climbing and bunny-ear dancers retain all custom gender and skin-tone forms',()=>{
  for(const base of ['🧖','🧗','👯']) for(const gender of ['','‍♂️','‍♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const text=base+tone+gender;assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('mobility devices retain custom tones, genders and both directions',()=>{
  for(const person of [...'🧑👨👩']) for(const aid of [...'🦯🦼🦽']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) for(const direction of ['','‍➡️']) {
    const text=person+tone+'‍'+aid+direction;assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('remaining activity forms and independent bunny tones route exactly',()=>{
  const check=text=>{assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);};
  for(const base of ['💆','💇']) for(const gender of ['','‍♂️','‍♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) check(base+tone+gender);
  for(const tone of ['',...'🏻🏼🏽🏾🏿']) {check('🧑'+tone+'‍🩰');check('🕴'+tone);}
  check('🕴️');
  for(const person of [...'🧑👨👩']) for(const a of [...'🏻🏼🏽🏾🏿']) for(const b of [...'🏻🏼🏽🏾🏿']) if(a!==b) check(person+a+'‍🐰‍'+person+b);
});


test('resting people retain skin tones and meditation gender forms',()=>{
  for(const base of ['🧘','🛀','🛌']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    for(const gender of (base==='🧘'?['','‍♂️','‍♀️']:[''])) {
      const text=base+tone+gender;
      assert.equal(emojiPolicy(text),'custom');
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    }
  }
});


test('body parts retain skin modifiers and exact eye presentation forms',()=>{
  const check=text=>{assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);};
  for(const base of [...'💪👂🦻👃🦵🦶']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) check(base+tone);
  for(const base of [...'🧠🦷🦴👀👁👅👄🫦🫀🫁🦾🦿']) check(base);
  check('👁️');check('👁︎');
  check('👁️‍🗨️');
  assert.equal(emojiPolicy('👁️‍🔥'),'native');
  assert.deepEqual(fontRuns('👁️‍🔥'),[{text:'👁️‍🔥',emojiPolicy:'native'}]);
});

test('juggling gender and skin-tone sequences route as whole custom drawings',()=>{
  for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const text='🤹'+tone+gender;
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});

test('clothed sport drawings retain skier presentation without inventing modifiers',()=>{
  for(const text of ['🤺','⛷','⛷︎','⛷️']) {
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
  for(const base of ['🤺','⛷']) for(const tone of [...'🏻🏼🏽🏾🏿']) {
    const text=base+tone;
    assert.equal(emojiPolicy(text),'native');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'native'}]);
  }
});

test('fully covered snowboarder consumes each standard tone sequence',()=>{
  for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    const text='🏂'+tone;
    assert.equal(emojiPolicy(text),'custom');
    assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
});


test('golf and horse racing preserve whole standard forms and presentation',()=>{
  for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
    for(const text of ['🏇'+tone, ...['', '\u200d♂','\u200d♂️','\u200d♀','\u200d♀️'].map(g=>'🏌'+tone+g)]) {
      assert.equal(emojiPolicy(text),'custom');
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    }
  }
  for(const text of ['🏌︎','🏌️','🏌️‍♂️','🏌️‍♀️']) assert.equal(emojiPolicy(text),'custom');
});


test('swimming basketball and weightlifting keep standard gender tone and presentation forms whole',()=>{
  for(const base of ['🏊','⛹','🏋']) {
    for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
      const text=base+tone+gender;
      assert.equal(emojiPolicy(text),'custom');
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    }
    for(const selector of ['︎','️']) assert.equal(emojiPolicy(base+selector),'custom');
  }
});


test('rowing and surfing keep standard gender and tone sequences whole',()=>{
  for(const base of ['🚣','🏄']) {
    for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
      const text=base+tone+gender;
      assert.equal(emojiPolicy(text),'custom');
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    }
  }
  for(const selector of ['︎','️']) assert.equal(emojiPolicy('🏄'+selector),'custom');
});


test('cycling, cartwheel, handball and water polo keep gender and tone sequences whole',()=>{
  for(const base of ['🚴','🚵','🤸','🤾','🤽']) {
    for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
      const text=base+tone+gender;
      assert.equal(emojiPolicy(text),'custom');
      assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
    }
  }
});


test('wrestling, Santa and mages keep standard tones and mixed pairs whole',()=>{
  const check=text=>{assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);};
  for(const base of ['🤼','🧙']) for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) check(base+tone+gender);
  for(const base of ['🎅','🤶','🧑']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) check(base+tone+(base==='🧑'?'\u200d🎄':''));
  for(const person of ['🧑','👨','👩']) for(const a of [...'🏻🏼🏽🏾🏿']) for(const b of [...'🏻🏼🏽🏾🏿']) if(a!==b) check(person+a+'\u200d🫯\u200d'+person+b);
});


test('vampires and elves retain all tone and gender qualification forms',()=>{
 for(const base of ['🧛','🧝']) for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
  const text=base+tone+gender;
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('fairies, merpeople and superheroes retain all tone and gender qualification forms',()=>{
 for(const base of ['🧚','🧜','🦸']) for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
  const text=base+tone+gender;
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});

test('fantasy beings retain their qualified forms without inventing human skin tones',()=>{
 for(const base of ['🧞','🧟']) for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) {
  const text=base+gender;
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  for(const tone of '🏻🏼🏽🏾🏿') assert.notEqual(emojiPolicy(base+tone+gender),'custom');
 }
 assert.equal(emojiPolicy('🧌'),'custom');
 for(const gender of ['', '\u200d♂', '\u200d♂️', '\u200d♀', '\u200d♀️']) for(const tone of ['',...'🏻🏼🏽🏾🏿']) {
  const text='🦹'+tone+gender;
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('reviewed symbol tiles and baby angels retain exact qualification and tone forms',()=>{
 for(const file of ['noto-emoji-symbol-tiles-svg','noto-emoji-baby-angel-svg']) {
  const sources=JSON.parse(readFileSync(new URL('../data/font-sources/'+file+'.json',import.meta.url),'utf8'));
  for(const source of sources.files) for(const text of source.include_sequences) {
   assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  }
 }
 for(const text of ['🚶‍➡️','🚶🏿‍♀️‍➡️','🙂‍↔️','🙂‍↕️']) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('reviewed symbol marks retain qualification and compound gender routing',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-symbol-marks-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
 for(const text of ['👩‍⚕️','🧑🏿‍⚖️','🏃🏽‍♀️','🧟‍♂️','🧞‍♀️']) assert.equal(emojiPolicy(text),'custom');
});


test('reviewed signs retain qualification and compound medical routing',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-signs-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
 for(const text of ['🧑‍⚕️','👩🏻‍⚕️','👨🏿‍⚕️','🧑🏽‍⚕️']) assert.equal(emojiPolicy(text),'custom');
});


test('reviewed expressions route every qualification and retain earlier compounds',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-expressions-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
 for(const text of ['😮‍💨','😵‍💫','⛓️‍💥']) assert.equal(emojiPolicy(text),'custom');
});


test('reviewed geometric signs retain semantic size and qualification',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-geometric-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }

});


test('reviewed hand props route all exact tone and presentation forms',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-hand-props-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences||[]) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('reviewed person symbols route exact neutral family sequences',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-person-symbols-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('reviewed game and medical symbols retain exact qualification and mending-heart routing',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-game-medical-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
 for(const text of ['❤‍🩹','❤️‍🩹']) assert.equal(emojiPolicy(text),'custom');
});


test('reviewed sound and music controls retain exact custom qualification forms',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-sound-controls-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('reviewed award and event symbols retain exact custom qualification forms',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-awards-events-svg.json',import.meta.url),'utf8'));
 for(const source of sources.files) for(const text of source.include_sequences) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
 }
});


test('holding-hands families preserve all 104 standard forms and adjacent people',()=>{
 const sources=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-holding-hands-svg.json',import.meta.url),'utf8'));
 const forms=sources.files.flatMap(source=>source.include_sequences??[]);
 assert.equal(forms.length,104);
 for(const text of forms) {
  assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);
  assert.ok(fontRuns('🧑🏻'+text+'👩🏿').every(run=>run.emojiPolicy==='custom'));
 }
});


for (const [family,count] of [['family-tiles',25],['couples',404]]) {
 test(`all reviewed ${family} qualification forms use custom emoji`,()=>{
  const source=JSON.parse(readFileSync(new URL(`../data/font-sources/noto-emoji-${family}-svg.json`,import.meta.url),'utf8'));
  const forms=source.files.flatMap(entry=>entry.include_sequences??[]);assert.equal(forms.length,count);
  for(const text of forms){assert.equal(emojiPolicy(text),'custom');assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);}
 });
}

for (const [kind,count] of [['general',14],['regional',262]]) {
 test(`all ${kind} flags route as exact custom clusters`,()=>{
  const spec=JSON.parse(readFileSync(new URL(`../data/font-sources/noto-emoji-${kind}-flags-svg.json`,import.meta.url),'utf8'));
  const forms=spec.files.flatMap(e=>e.include_sequences??[]);assert.equal(forms.length,count);
  for(const text of forms){assert.equal(emojiPolicy(text),'custom',text);assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);}
 });
}
test('unregistered regional pairs and incomplete flag clusters retain native routing',()=>{
 assert.equal(emojiPolicy('🇬'),'custom','the standalone regional-indicator character now has a reviewed drawing');
 for(const text of ['🇦🇦','🏴\u{e007a}\u{e007a}\u{e007f}','🏳️‍🌈‍🌈']) assert.equal(emojiPolicy(text),'native',text);
 assert.ok(fontRuns('🏴🏴‍☠️🏴🏳️🏳️‍🌈🏳️‍⚧️🏳️🇬🇧🇺🇸').every(r=>r.emojiPolicy==='custom'));
});


test('all 34 reviewed book and mail qualification forms route as custom emoji',()=>{
 const spec=JSON.parse(readFileSync(new URL('../data/font-sources/noto-emoji-book-mail-svg.json',import.meta.url),'utf8'));
 const forms=spec.files.flatMap(e=>e.include_sequences??[]);assert.equal(forms.length,34);
 for(const text of forms){assert.equal(emojiPolicy(text),'custom',text);assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);}
});

test('book and mail boundaries preserve exact routing without capturing malformed clusters',()=>{
 assert.ok(fontRuns('📬📪✉️✉🗳️🗳🇬🇧').every(r=>r.emojiPolicy==='custom'));
 for(const text of ['✉️‍📦','📖🏻']) assert.equal(emojiPolicy(text),'native',text);
});


test('all 21 money and accessory qualification forms route as exact custom emoji',()=>{
 const forms=['money','clothing'].flatMap(family=>JSON.parse(readFileSync(new URL(`../data/font-sources/noto-emoji-${family}-svg.json`,import.meta.url),'utf8')).files.flatMap(e=>e.include_sequences??[]));
 assert.equal(forms.length,21);
 for(const text of forms){assert.equal(emojiPolicy(text),'custom',text);assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);}
});

test('money and accessory boundaries do not capture malformed clusters',()=>{
 assert.ok(fontRuns('🇬🇧📖💵💹📬👓🕶️🛍️').every(r=>r.emojiPolicy==='custom'));
 for(const text of ['💵🏻','🕶️‍💎']) assert.equal(emojiPolicy(text),'native',text);
});


test('all 79 final object forms route as exact custom emoji',()=>{
 const families=['office-locks','tools-instruments','places-weather','other-objects','globes','phoenix','air-water','road-infrastructure','ground-vehicles'];
 const forms=families.flatMap(family=>JSON.parse(readFileSync(new URL(`../data/font-sources/noto-emoji-${family}-svg.json`,import.meta.url),'utf8')).files.flatMap(e=>e.include_sequences??[]));
 assert.equal(forms.length,79);
 for(const text of forms){assert.equal(emojiPolicy(text),'custom',text);assert.deepEqual(fontRuns(text),[{text,emojiPolicy:'custom'}]);}
 for(const text of ['🐦‍🔥‍🔥','🚲🏻','🌏‍🌍','🚑️‍🚒'])assert.equal(emojiPolicy(text),'native',text);
 assert.ok(fontRuns('🐦‍🔥🐦🔥🚲⛽🛼🇬🇧').every(r=>r.emojiPolicy==='custom'));
});
