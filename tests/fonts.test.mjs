import test from 'node:test';
import assert from 'node:assert/strict';
import { contains, requiredFonts, createFontLoader } from '../js/fonts.js';

test('polytonic Greek stays in the handwritten Greek companion',()=>{
  const result=requiredFonts(['Καλημέρα! ἄνθρωπος ἀλήθεια Ὀδυσσεύς']);
  assert.deepEqual(result.missing,[]);
  assert.ok(result.fonts.some(f=>f.family==='Dad Handwritten Greek'));
  assert.ok(!result.fonts.some(f=>f.source?.endsWith('/NotoSans-Regular.ttf')));
});

test('ordinary Cyrillic uses proportional handwriting instead of fine full-cell lettering',()=>{
  const result=requiredFonts(['Доброе утро! Сегодня прекрасный день.']);
  assert.deepEqual(result.missing,[]);
  assert.ok(result.fonts[0].source.endsWith('/LXGWWenKai-Regular.ttf'));
  assert.ok(!result.fonts.some(f=>f.source?.endsWith('/KleeOne-Regular.ttf')));
});

const inventory = {
  baseRanges: [[32, 126]],
  fonts: [
    { family: 'Arabic', file: 'arabic.woff2', sha256: '1234567890ab', ranges: [[0x600, 0x6ff]] },
    { family: 'Han', file: 'han.woff2', sha256: 'abc123456789', ranges: [[0x4e00, 0x4eff], [0x20000, 0x20001]] },
  ],
};

test('two licensed Seal gaps load their restricted font without capturing modern aliases',()=>{
  const result=requiredFonts(['\u{3e34f} \u{3fa42}']);
  assert.deepEqual(result.missing,[]);
  assert.equal(result.fonts.length,1);
  assert.ok(result.fonts[0].source.endsWith('/LXGWSeal-Regular.ttf'));
  assert.deepEqual(result.fonts[0].ranges,[[0x3e34f,0x3e34f],[0x3fa42,0x3fa42]]);
  for(const text of ['曆','刘','鎦','A'])
    assert.ok(!requiredFonts([text]).fonts.some(f=>f.source?.endsWith('/LXGWSeal-Regular.ttf')));
});

test('Malayalam Syriac selects one native joining font for bases and vowels',()=>{
  const text=Array.from({length:11},(_,i)=>'ܒ'+String.fromCodePoint(0x860+i)+'ܲܒ').join(' ');
  const result=requiredFonts([text]);
  assert.deepEqual(result.missing,[]);
  assert.equal(result.fonts.length,1);
  assert.ok(result.fonts[0].source.endsWith('/EastSyriacMalankara.ttf'));
});

test('routing handles range edges, supplementary codepoints and deterministic ordering', () => {
  assert.equal(contains(inventory.fonts[1].ranges, 0x4eff), true);
  assert.equal(contains(inventory.fonts[1].ranges, 0x4f00), false);
  const result = requiredFonts(['𠀀一 مرحبا', '一 A'], inventory);
  assert.deepEqual(result.fonts.map(f => f.family), ['Arabic', 'Han']);
  assert.deepEqual(result.missing, []);
  assert.deepEqual(requiredFonts(['🫠'], inventory).missing, [0x1fae0]);
  assert.deepEqual(requiredFonts(['Hello'], inventory).fonts, []);
});

test('concurrent requests share loading and registration, independent of request history', async () => {
  const started = [], added = [];
  let resolve;
  const gate = new Promise(r => { resolve = r; });
  class Face {
    constructor(family, url) { this.family = family; this.url = url; }
    async load() { started.push(this); await gate; return this; }
  }
  const load = createFontLoader({ add: f => added.push(f) }, Face, inventory);
  const a = load(['مرحبا']), b = load(['مرحبا']);
  assert.equal(started.length, 1);
  assert.equal(added.length, 0);
  assert.match(started[0].url, /arabic\.woff2\?v=1234567890/);
  resolve();
  await Promise.all([a,b]);
  assert.equal(added.length, 1);
  assert.deepEqual((await load(['Plain'])).families, []);
});

test('failed font loads reject rendering prerequisites and can be retried', async () => {
  let attempts = 0;
  class Face {
    async load() { if (++attempts === 1) throw new Error('offline'); return this; }
  }
  const load = createFontLoader({ add() {} }, Face, inventory);
  await assert.rejects(load(['一']), /offline/);
  assert.deepEqual((await load(['一'])).families, ['Han']);
  assert.equal(attempts, 2);
});

test('custom emoji batch routes automatically and keeps composite fallbacks intact', () => {
  assert.ok(requiredFonts(['😀 ❤️ 👍']).fonts.some(f => f.family === 'Dad Emoji'));
  assert.ok(requiredFonts(['😀 👍🏽']).fonts.some(f => f.family === 'Dad Emoji'));
  assert.deepEqual(requiredFonts(['😀 👨‍👦']).emojiFallbacks, []);
  assert.deepEqual(requiredFonts(['😀 👨‍👦‍👦‍👦']).emojiFallbacks, ['👨‍👦‍👦‍👦']);
  assert.deepEqual(requiredFonts(['🦯 🦼 🦽']).emojiFallbacks, []);
  assert.ok(requiredFonts(['🧑‍🚀']).fonts.some(f => f.family === 'Dad Emoji'));
  assert.ok(!requiredFonts(['Plain text']).fonts.some(f => f.family === 'Dad Emoji'));
});

test('every new cuneiform numeral routes to bundled numeric fonts without fallback', () => {
  const points = [0x1246f, ...Array.from({length:11},(_,i)=>0x12475+i),
    ...Array.from({length:311},(_,i)=>0x12550+i)];
  const result = requiredFonts([String.fromCodePoint(...points)]);
  assert.deepEqual(result.missing, []);
  assert.deepEqual(result.emojiFallbacks, []);
  assert.equal(result.fonts.length, 2);
  assert.ok(result.fonts.some(f=>f.source.endsWith('/ArchaicCuneiformNumerals.ttf')));
  assert.ok(result.fonts.some(f=>f.source.endsWith('/UnicodiaCunei.ttf')));
});

test('the complete Jurchen repertoire and new Tangut ranges use bundled fonts', () => {
  const points = [...Array.from({length:914},(_,i)=>0x18e00+i),
    ...Array.from({length:51},(_,i)=>0x191a0+i), 0x187f8,0x187fa,0x18df2];
  const result = requiredFonts([String.fromCodePoint(...points)]);
  assert.deepEqual(result.missing, []);
  assert.deepEqual(result.emojiFallbacks, []);
  assert.equal(result.fonts.length, 1);
  assert.ok(result.fonts[0].source.endsWith('/UFSZeroExt.otf'));
});

test('new general combining marks stay in the base lettering with their anchors', () => {
  const marks=[0x1ac1,0x1ac2,0x1ac3,0x1ac4,0x1ac6,
    ...Array.from({length:34},(_,i)=>0x1acf+i)];
  const result=requiredFonts(marks.map(cp=>'X'+String.fromCodePoint(cp)));
  assert.deepEqual(result.missing,[]);
  assert.deepEqual(result.fonts,[]);
});

test('supplemental Cyrillic combining letter shares native base font', async () => {
  const {default: manifest} = await import('../js/font-manifest.js');
  const result = requiredFonts(['а𞂏 А𞂏'], manifest);
  assert.deepEqual(result.missing, []);
  assert.equal(result.fonts.length, 1);
  assert.ok(result.fonts[0].source.endsWith('/NotoSans-Regular.ttf'));
});

test('Dives Akuru uses its complete native font and leaves obsolete mappings unassigned', async () => {
  const {default: manifest} = await import('../js/font-manifest.js');
  const result = requiredFonts(['𑤌𑤸 𑤁 𑥐𑥑'], manifest);
  assert.deepEqual(result.missing, []);
  assert.equal(result.fonts.length, 1);
  assert.ok(result.fonts[0].source.endsWith('/unicodia/NotoSerifDivesAkuru-Regular.ttf'));
  assert.deepEqual(requiredFonts(['\u{11939}'], manifest).missing, [0x11939]);
});

test('joining scripts use one font across ordinary and supplemental letters', async () => {
  const {default: manifest} = await import('../js/font-manifest.js');
  const result = requiredFonts(['ب𐻂ب بࢗب ب𐻙ب', 'مَرْحَبًا'], manifest);
  assert.deepEqual(result.missing, []);
  assert.equal(result.fonts.length, 1);
  assert.ok(result.fonts[0].source.endsWith('/ScheherazadeNew-Regular.ttf'));
});

test('ordinary Arabic retains its preferred hand-lettered source', async () => {
  const {default: manifest} = await import('../js/font-manifest.js');
  const result = requiredFonts(['مَرْحَبًا بالعالم'], manifest);
  assert.equal(result.fonts.length, 1);
  assert.match(result.fonts[0].source, /ArefRuqaa/);
});

test('joining-font preference takes precedence over duplicate coverage in mixed-script fonts', () => {
  const sample = {
    baseRanges: [[32,126]],
    fonts: [
      {family:'Partial',ranges:[[0x628,0x628],[0x4e00,0x4e00]]},
      {family:'Complete',ranges:[[0x628,0x628],[0x10ec2,0x10ec2]]},
    ],
  };
  assert.deepEqual(requiredFonts(['一 ب𐻂ب'],sample).fonts.map(f=>f.family),['Complete','Partial']);
});

test('Arabic honorific and mathematical symbols do not break joining-font selection', async () => {
  const {default: manifest} = await import('../js/font-manifest.js');
  const result = requiredFonts(['ب𐻂ب ﯃ 𞸀'], manifest);
  assert.deepEqual(result.missing, []);
  assert.ok(result.fonts[0].source.endsWith('/ScheherazadeNew-Regular.ttf'));
  assert.ok(result.fonts.some(f=>f.source.includes('/ufs/')));
  assert.ok(!result.fonts.some(f=>f.source.includes('ArefRuqaa')));
});

test('supplemental Arabic marks share their native base and joining font', async () => {
  const {default: manifest} = await import('../js/font-manifest.js');
  const result = requiredFonts(['ب\u{10ecb}\u{10ecb} لا\u{10ef9}', 'م\u{10ef1}'], manifest);
  assert.deepEqual(result.missing, []);
  assert.equal(result.fonts.length, 1);
  assert.ok(result.fonts[0].source.endsWith('/ScheherazadeNew-Regular.ttf'));
});

test('Egyptian rotation font loads only for an advertised variation sequence', () => {
  const variant=requiredFonts(['𓄹\ufe03']);
  assert.ok(variant.fonts.some(f=>f.family==='Dad Egyptian Variants'));
  assert.ok(!requiredFonts(['𓄹']).fonts.some(f=>f.family==='Dad Egyptian Variants'));
  assert.ok(!requiredFonts(['𓀀\u{13430}𓀁']).fonts.some(f=>f.family==='Dad Egyptian Variants'));
});

test('extended Egyptian groups load complete signs alongside structured-source font entries', () => {
  const result=requiredFonts(['𓑠𓐰𓑡 𓑠𓐰𔉴︅']);
  assert.deepEqual(result.missing, []);
  assert.ok(result.fonts.some(f=>typeof f.source === 'string' && f.source.endsWith('/UniHieroglyphica.ttf')));
  assert.ok(result.fonts.some(f=>f.family==='Dad Egyptian Variants'));
});

test('mirrored rotations load their registered variation font',()=>{
  const result=requiredFonts(['𔉴\ufe05\u{13440}']);
  assert.deepEqual(result.missing,[]);
  assert.ok(result.fonts.some(f=>f.family==='Dad Egyptian Variants'));
});

test('damage modifiers preserve rotation font selection with or without mirroring',()=>{
  for(const suffix of ['\u{13447}','\u{13440}\u{13455}']) {
    const result=requiredFonts(['𔉴\ufe05'+suffix]);
    assert.deepEqual(result.missing,[]);
    assert.ok(result.fonts.some(f=>f.family==='Dad Egyptian Variants'));
  }
});

test('explicit RTL Egyptian signs load the complete outline source for reflection',()=>{
  const result=requiredFonts(['\u202e𓀀𓀁\u202c']);
  assert.ok(result.fonts.some(f=>typeof f.source==='string' && f.source.endsWith('/UniHieroglyphica.ttf')));
});

test('recovered Seal signs use their verified source and reject the mismatched candidate',()=>{
  const result=requiredFonts(['𾺦𾺉𾹙𾹑𾹇𾵨𾶟𾶻𾴥𾱌𾱝𾲚𾲧𾮜𾯪𾰌𾮱𾮽𾬵𾬕𾬟𾥨𾩉𾩾𾫮𾤿𾣐𾟭𾡚𾝭𾞸𾕿𾖡𾘅𾑒𾑢𾔟𾕂𾎱𾎳𾏇𾍷𾌻𾎆𾋧𾋽𾌐𾂖𾆗𾆼𾇧𾀪𾁳𾃧𽽲𽹹𽻥𽷎𽷼𽸖𽵣𽵥𽶤𽶥𽵑𽭭𽮢𽫝𽫟𽫪𽬃𽥑𽧄𽨕𽢓𽢿𽣯𽣳𽛏𽝵𽟐𽕏𽖴𽓕𽐍𽐔𽑫𽒠𽍕𽍺𽊦𽈜𽂋𽀥𽀬𽁢𽆂𽆘𽂨𽄢𽀐𽂇𽁕𽀇𽳡𾺴𿕶𿟬𿭥𿭦𿭲𿘎𿜑𿊸𿊹𿊺𿊻𿎐𿎒𿎓𿎔𿎕𿎖𿎗𿎘𿎙𿎚𿎜𿎝𿎞𿎟𿎠𿎡𿎣𿈔𿈕𿈖𿈗𿈘𿈝𾺯𾺰𾺱𾼬𾿅𾿆𾯸𿅜𿅞𿅡𿅢𿅣𾌲𾚛𾢈𾪊𾚚𾉞𾎔𾔿𾖭𾉝𽝦𽢊𾈟𾺳𾺶𾃲𾓪𿊃𿣽𾓩𾇣𾺘𾺵𽞩𽒸𽴪𽷲𽷳𽞨𽬎𿖱𿗱𿒂𿓱𿗍𾇑𾊘𾊥𾓭𿘃𿘄𿘅𿉽𿉾𿞝𾃴𾇥𾇦𾕮𾨺𾨻𾩙𾭭𾵷𾺓𾿓𿇮𽙫𾴺𾴻𾺲𿘢𿘣𿘥𿣼']);
  assert.deepEqual(result.missing,[]);
  assert.equal(result.fonts.length,1);
  assert.ok(result.fonts[0].source.endsWith('/DadSealRecovery-Regular.ttf'));
  const repaired=requiredFonts([String.fromCodePoint(0x3E34F)]);
  assert.deepEqual(repaired.missing,[]);
  assert.ok(repaired.fonts.every(f=>f.source.endsWith('/LXGWSeal-Regular.ttf')));
  const completed=requiredFonts([String.fromCodePoint(0x3D06C)]);
  assert.deepEqual(completed.missing,[]);
  assert.ok(completed.fonts.every(f=>f.source.endsWith('/DadSealSans-Regular.otf')));
  assert.deepEqual(requiredFonts([String.fromCodePoint(0x3FC40)]).missing,[0x3FC40]);
});


test('Tolong bases and inherited marks select one complete native font',()=>{
  const marks=[0x303,0x306,0x307,0x308,0x304,0x330,0x324,0x323,0x331];
  const text=marks.map(cp=>String.fromCodePoint(0x11db4,cp,0x11dd9)).join(' ');
  const result=requiredFonts([text]);
  assert.deepEqual(result.missing,[]);
  assert.equal(result.fonts.length,1);
  assert.ok(result.fonts[0].source.endsWith('/DadTolong.ttf'));
});

test('Garay case and all native marks select the complete Garay shard',()=>{
  const text=Array.from({length:5},(_,i)=>String.fromCodePoint(0x10d53,0x10d69+i,0x10d73,0x10d69+i)).join(' ');
  const result=requiredFonts([text]);
  assert.deepEqual(result.missing,[]);
  assert.equal(result.fonts.length,1);
  assert.ok(result.fonts[0].source.endsWith('/DadGaray.ttf'));
});

test('Tai Yo spacing letters and medial/rhyme marks use one native shard',()=>{
  const marks=[0x1e6e3,0x1e6e6,0x1e6ee,0x1e6ef,0x1e6f5];
  const text=marks.map(mark=>String.fromCodePoint(0x1e6cd,mark,0x1e6d5,mark)).join(' ')
    +' '+String.fromCodePoint(0x1e6c5,0x1e6ee,0x1e6ee,0x1e6dc,0x1e6ee,0x1e6ef,0x1e6d1,0x1e6e2,0x1e6cf);
  const result=requiredFonts([text]);
  assert.deepEqual(result.missing,[]);
  assert.equal(result.fonts.length,1);
  assert.ok(result.fonts[0].source.endsWith('/DadTaiYo.ttf'));
});

test('rendering waits for the ink companion and retries a failed companion load', async () => {
  const added=[], attempts=new Map();
  class Face {
    constructor(family) {this.family=family;}
    async load() {
      const count=(attempts.get(this.family)??0)+1;attempts.set(this.family,count);
      if(this.family==='Dad Emoji Ink' && count===1) throw new Error('ink unavailable');
      return this;
    }
  }
  const load=createFontLoader({add:face=>added.push(face.family)},Face);
  await assert.rejects(load(['😀']),/ink unavailable/);
  const result=await load(['😀']);
  assert.ok(result.families.includes('Dad Emoji'));
  assert.ok(!result.families.includes('Dad Emoji Ink'));
  assert.equal(attempts.get('Dad Emoji'),1);
  assert.equal(attempts.get('Dad Emoji Ink'),2);
  assert.ok(added.includes('Dad Emoji Ink'));
});
