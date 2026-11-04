import test from 'node:test';
import assert from 'node:assert/strict';
import {nativeShapingText} from '../js/native-shaping.js';

test('new Arabic marks use known categories and unique UVS drawings only at shaping time',()=>{
  const input='ب\u{10ecb}\u{10ecc}';
  assert.equal(nativeShapingText(input),'ب\u0652\u{e0100}\u0650\u{e0101}');
  assert.equal(input,'ب\u{10ecb}\u{10ecc}');
  assert.equal(nativeShapingText('مَرْحَبًا A𓀀 🧑‍🚀'),'مَرْحَبًا A𓀀 🧑‍🚀');
});

test('crown letters use a right-side join barrier and their own UVS glyphs',()=>{
  assert.equal(nativeShapingText('ب𐻙ب'),'ب\u200cب\u{e0120}ب');
  assert.equal(nativeShapingText('𐻮'),'\u200cي\u{e0135}');
  assert.equal(nativeShapingText('𐻑 𐻉'),'𐻑 𐻉');
});

test('historical Odia dots inherit overline shaping with distinct UVS drawings',()=>{
  assert.equal(nativeShapingText('କା\u0b53 ଅ\u0b54'),'କା\u0b55\u{e0140} ଅ\u0b55\u{e0141}');
  assert.equal(nativeShapingText('କ୕ ଓଡ଼ିଆ'),'କ୕ ଓଡ଼ିଆ');
});

test('alternate Bengali BA uses BA behavior while selecting its diagonal drawing',()=>{
  assert.equal(nativeShapingText('\u{11df1}ু ম্\u{11df1}'),'ব\u{e0150}ু ম্ব\u{e0150}');
  assert.equal(nativeShapingText('বু ৰু'),'বু ৰু');
});

test('alternate BA splits canonical O and AU vowels for older Indic normalizers',()=>{
  const text='\u{11df1}ো \u{11df1}ৌ';
  assert.equal(nativeShapingText(text),'ব\u{e0150}ো ব\u{e0150}ৌ');
  assert.equal(text,'\u{11df1}ো \u{11df1}ৌ');
  assert.equal(nativeShapingText('বো বৌ'),'বো বৌ');
});

test('Bengali historical anusvara selects a raised ring only in its own tall cluster',()=>{
  assert.equal(nativeShapingText('ক\u{11df0} কি\u{11df0} কী\u{11df0} র্ক\u{11df0}'),
    'কঁ\u{e0151} কিঁ\u{e0152} কীঁ\u{e0152} র্কঁ\u{e0152}');
  assert.equal(nativeShapingText('কিক\u{11df0}'),'কিকঁ\u{e0151}');
  assert.equal(nativeShapingText('কো\u{11df0} কৌ\u{11df0}'),'কোঁ\u{e0151} কৌঁ\u{e0152}');
  assert.equal(nativeShapingText('কিঁ কং'),'কিঁ কং');
});

test('alternate Devanagari DDDA keeps implosive shaping and its own drawing',()=>{
  const original='\u{11b0a}ु र्\u{11b0a}';
  assert.equal(nativeShapingText(original),'ॾ\u{e0160}ु र्ॾ\u{e0160}');
  assert.equal(original,'\u{11b0a}ु र्\u{11b0a}');
  assert.equal(nativeShapingText('द दु ॾ ॾु'),'द दु ॾ ॾु');
});

test('Cyrillic marks stay in Glagolitic shaping runs without changing other text',()=>{
  const input='Ⱍ҃ Ⱟ҄ ⱟ҇ А҃ ҃';
  assert.equal(nativeShapingText(input),'Ⱍ\u0303\u{e0170} Ⱟ\u0303\u{e0171} ⱟ\u0303\u{e0172} А҃ ҃');
  assert.equal(input,'Ⱍ҃ Ⱟ҄ ⱟ҇ А҃ ҃');
  assert.equal(nativeShapingText('Ⱟ̃҃'),'Ⱟ̃\u0303\u{e0170}');
  assert.equal(nativeShapingText('Ⱟ\n҃'),'Ⱟ\n҃');
  assert.equal(nativeShapingText(nativeShapingText(input)),nativeShapingText(input));
});

test('Kashmiri Sharada vowel aliases retain native category and exact glyph selection',()=>{
  const cps=[0x11b60,0x11b61,0x11b62,0x11b63,0x11b64,0x11b65,0x11b66,0x11b67];
  const bases=[0x111bc,0x111b3,0x111b6,0x111b7,0x111bc,0x111b3,0x111bc,0x111b3];
  const selectors=[0xe0180,0xe0185,0xe0181,0xe0182,0xe0183,0xe0186,0xe0184,0xe0187];
  cps.forEach((cp,i)=>assert.equal(nativeShapingText('𑆑'+String.fromCodePoint(cp)), '𑆑'+String.fromCodePoint(bases[i],selectors[i])));
  const native='𑆑𑆶 𑆑𑆳 𑆑𑆼';assert.equal(nativeShapingText(native),native);
  const value='𑆘𑭢 𑆨𑇀𑆘𑭡';assert.equal(nativeShapingText(nativeShapingText(value)),nativeShapingText(value));
});
