import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Rules } from '../js/vendor/linebreak/index.js';

test('Unicode 18 default line-breaking conformance corpus', () => {
  const rules = new Rules();
  const file = fs.readFileSync(new URL('../data/unicode/18.0.0/auxiliary/LineBreakTest.txt', import.meta.url), 'utf8');
  const failures = [];
  let count = 0;
  for (const row of file.split('\n')) {
    const code = row.split('#')[0].trim();
    if (!code) continue;
    let text = '', expected = [];
    for (const token of code.split(/\s+/)) {
      if (token === '÷') expected.push(text.length);
      else if (token !== '×') text += String.fromCodePoint(parseInt(token, 16));
    }
    const actual = [...rules.breaks(text)].map(b => b.position);
    count++;
    if (JSON.stringify(actual) !== JSON.stringify(expected)) failures.push({row, expected, actual});
  }
  assert.ok(count > 10000);
  assert.deepEqual(failures.slice(0, 12), [], `${failures.length} failures of ${count}`);
});

import { layoutColumn,layoutText,makePanel } from '../js/layout.js';
import { breakUnits, lineContent, textParagraphs, emergencyBoundary } from '../js/line-breaks.js';
import { dictionaryBreaks } from '../js/dictionary-breaks.js';
const column = (text, width) => layoutColumn(text, {width, fontSize: 1, lineHeight: 1, measure: s => [...s].length}).lines.map(l => l.text);

test('CJK wrapping and balancing keep punctuation attached without inserting spaces', () => {
  const text = '你好，世界。こんにちは。';
  const lines = column(text, 4);
  assert.equal(lines.join(''), text);
  assert.ok(lines.length > 1);
  assert.ok(lines.every(l => !/^[，。）」』]/u.test(l)));
  assert.ok(lines.every(l => [...l].length <= 4));
});

test('nonbreaking spaces and explicit word joiners survive line fitting', () => {
  assert.deepEqual(column('a\u00a0b c', 3), ['a\u00a0b', 'c']);
  assert.deepEqual(column('aa\u2060bb cc', 5), ['aa\u2060bb', 'cc']);
});

test('soft hyphens appear only at selected breaks and zero-width spaces stay invisible', () => {
  assert.deepEqual(column('ab\u00adcd', 3), ['ab-', 'cd']);
  assert.deepEqual(column('ab\u00adcd', 4), ['abcd']);
  assert.deepEqual(column('ab\u00ad', 2), ['ab']);
  assert.deepEqual(column('abc\u200bdef', 3), ['abc', 'def']);
});

test('all mandatory separators work and tabs retain explicit indentation', () => {
  assert.deepEqual(textParagraphs('a\r\nb\rc\u0085d\u2028e\u2029f').map(p => lineContent(p,true)), ['a','b','c','d','e','f']);
  assert.deepEqual(column('a\n\tb  c', 12), ['a', '    b  c']);
});

test('line-breaking opportunities never divide an extended grapheme', () => {
  for (const text of ['👩🏽‍🔬', '🇬🇧', 'क्ष', 'a\u0301']) assert.deepEqual(breakUnits(text), [text]);
});

test('dictionary scripts expose word opportunities without changing their text', () => {
  for (const words of [
    ['ภาษา', 'ไทย', 'เป็น', 'ภาษา', 'ที่', 'สวยงาม'],
    ['ພາສາ', 'ລາວ'],
    ['ភាសាខ្មែរ', 'ជា', 'ភាសាជាតិ'],
    ['မြန်မာဘာသာ', 'စကား'],
  ]) {
    assert.deepEqual(breakUnits(words.join('')), words);
    const width = Math.max(...words.map(word => [...word].length));
    const lines = column(words.join(''), width);
    assert.equal(lines.join(''), words.join(''));
    const boundaries = new Set();
    let end = 0;
    for (const word of words) boundaries.add(end += word.length);
    end = 0;
    for (const line of lines) assert.ok(boundaries.has(end += line.length));
  }
});

test('dictionary tailoring respects punctuation, joiners and nonbreaking spaces', () => {
  assert.deepEqual(breakUnits('(ภาษาไทย) ภาษา\u2060ไทย'), ['(ภาษา', 'ไทย) ', 'ภาษา\u2060ไทย']);
  assert.deepEqual(breakUnits('ภาษา\u00a0ไทย'), ['ภาษา\u00a0ไทย']);
  assert.deepEqual(dictionaryBreaks('hello world 你好，世界。'), []);
});

test('emergency fitting keeps dictionary words and separate spacing vowels intact',()=>{
  const measure=(text,size)=>[...text].length*size;
  for(const text of ['မြန်မာဘာသာ','ภาษา\u2060ไทย','ພາສາ\u00a0ລາວ']){
    const column=layoutColumn(text,{measure,fontSize:1,lineHeight:1,width:3});
    assert.equal(column.fits,false,'report overflow so caller can grow or reduce the column');
    const panel=makePanel({width:3,height:1,free:[]},3,20,0);
    const {lines}=layoutText(panel,text,{measure,fontSize:1,lineHeight:1,fitUnbreakable:true});
    assert.equal(lines.flatMap(l=>l.units).join(''),text);
    assert.equal(lines.length,1,text);
    assert.ok(lines[0].fontSize<1,text);
  }
  assert.equal(emergencyBoundary('သ','ာ'),false);
});

test('missing browser dictionary support retains default safe breaking', () => {
  const original = Intl.Segmenter;
  try {
    Intl.Segmenter = undefined;
    assert.deepEqual(dictionaryBreaks('ภาษาไทย'), []);
  } finally {
    Intl.Segmenter = original;
  }
});
