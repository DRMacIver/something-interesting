import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { getEmbeddingLevels } from '../js/vendor/bidi/embeddingLevels.js';
import { getReorderedIndices } from '../js/vendor/bidi/reordering.js';
const data = name => readFileSync(new URL(`../data/unicode/18.0.0/${name}.txt`, import.meta.url), 'utf8').split('\n');
const numbers = text => text.trim() ? text.trim().split(/\s+/).map(x => x === 'x' ? x : Number(x)) : [];
function check(input, direction, levels, order, label, paragraphLevel) {
  const result = getEmbeddingLevels(input, direction);
  assert.equal(result.levels.length, levels.length, label);
  for (let i = 0; i < levels.length; i++) {
    if (levels[i] !== 'x') assert.equal(result.levels[i], levels[i], `${label}, level ${i}`);
  }
  if (paragraphLevel !== undefined) assert.equal(result.paragraphs[0].level, paragraphLevel, label);
  const actual = getReorderedIndices(input, result).filter(i => levels[i] !== 'x');
  assert.deepEqual(actual, order, label);
}
test('Unicode 18 BidiCharacterTest: paragraph levels, resolved levels and reordering', () => {
  let count = 0;
  for (const [i, raw] of data('BidiCharacterTest').entries()) {
    const line = raw.split('#')[0].trim();
    if (!line) continue;
    const [codes, dir, base, levels, order] = line.split(';');
    const input = codes.trim().split(/\s+/).map(cp => String.fromCodePoint(parseInt(cp, 16))).join('');
    check(input, ['ltr', 'rtl', 'auto'][Number(dir)], numbers(levels), numbers(order), `BidiCharacterTest:${i+1}`, Number(base));
    count++;
  }
  assert.ok(count > 90000);
});
test('Unicode 18 BidiTest: every class sequence and applicable paragraph direction', () => {
  const reps = Object.fromEntries(Object.entries({L:0x41,R:0x5d0,EN:0x30,ES:0x2b,ET:0x23,AN:0x660,CS:0x2c,B:0x2029,S:9,WS:32,ON:0x21,BN:0xad,NSM:0x36f,AL:0x6d5,LRO:0x202d,RLO:0x202e,LRE:0x202a,RLE:0x202b,PDF:0x202c,LRI:0x2066,RLI:0x2067,FSI:0x2068,PDI:0x2069}).map(([type, cp]) => [type,String.fromCodePoint(cp)]));
  let levels, order, count = 0;
  for (const [i, raw] of data('BidiTest').entries()) {
    const line = raw.split('#')[0].trim();
    if (!line) continue;
    if (line.startsWith('@Levels:')) { levels = numbers(line.slice(8)); continue; }
    if (line.startsWith('@Reorder:')) { order = numbers(line.slice(9)); continue; }
    if (line.startsWith('@')) continue;
    const [types, bits] = line.split(';');
    const input = types.trim().split(/\s+/).map(t => reps[t]).join('');
    for (const [bit, dir] of ['auto','ltr','rtl'].entries()) {
      if (Number(bits) & (1 << bit)) {
        check(input, dir, levels, order, `BidiTest:${i+1} ${dir}`);
        count++;
      }
    }
  }
  assert.ok(count > 700000);
});

test('L1 resets trailing whitespace relative to a wrapped substring, without mutating paragraph levels', () => {
  const text = 'אבג abc   אבג';
  const result = getEmbeddingLevels(text);
  const before = [...result.levels];
  // Only abc and its spaces are on this line: abc stays LTR, spaces move
  // to the left under the RTL paragraph level at this soft line ending.
  const indices = getReorderedIndices(text, result, 4, 9).slice(4,10);
  assert.deepEqual(indices, [9,8,7,4,5,6]);
  assert.deepEqual([...result.levels], before);
});
