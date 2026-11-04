import test from 'node:test';
import assert from 'node:assert/strict';
import { requiredFonts, contains } from '../js/fonts.js';

const wenkai = f => /\/LXGWWenKai-Regular\.ttf$/.test(f.source ?? '');
test('Greek prose uses proportional handwriting for unaccented and canonical accent forms', () => {
  for (const text of ['κοσμε', 'Γειά σου κόσμε', 'Γειά σου κόσμε'.normalize('NFD'), 'ϐϑϕϖ']) {
    const selection = requiredFonts([text]);
    assert.deepEqual(selection.missing, []);
    assert.equal(selection.fonts.length, 1);
    assert.ok(wenkai(selection.fonts[0]), text);
    for (const c of text) if (!/\s/u.test(c)) assert.ok(contains(selection.fonts[0].ranges,c.codePointAt(0)));
  }
});
test('Greek source precedes overlapping CJK fonts in mixed dialogue', () => {
  const selection = requiredFonts(['Hello κόσμε 日本語 مَرْحَبًا 😀']);
  assert.deepEqual(selection.missing, []);
  const greek = selection.fonts.findIndex(wenkai);
  assert.ok(greek >= 0);
  for (let i=0; i<selection.fonts.length; i++) {
    if (/KleeOne/.test(selection.fonts[i].source ?? '')) assert.ok(greek < i);
  }
  assert.ok(selection.fonts.some(f => /ArefRuqaa/.test(f.source ?? '')));
  assert.ok(selection.fonts.some(f => f.family === 'Dad Emoji'));
});
test('polytonic Greek uses one complete proportional handwritten source', () => {
  const selection = requiredFonts(['ἄνθρωπος κόσμε']);
  assert.deepEqual(selection.missing, []);
  assert.equal(selection.fonts.length, 1);
  assert.equal(selection.fonts[0].family,'Dad Handwritten Greek');
  for (const c of 'ἄνθρωπος κόσμε'.normalize('NFD')) {
    if (!/\s/u.test(c)) assert.ok(contains(selection.fonts[0].ranges,c.codePointAt(0)));
  }
});
test('Greek variation and historic symbols remain reachable without a complete preferred face', () => {
  for (const text of ['α\u034f\u0301', '𐅀α', 'α\ufe00']) assert.deepEqual(requiredFonts([text]).missing, []);
});
