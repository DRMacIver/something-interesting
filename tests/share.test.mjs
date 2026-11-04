import test from 'node:test';
import assert from 'node:assert/strict';
import {encodeTexts, decodeTexts, MAX_SHARE_TEXT} from '../js/share.js';
const defaults = ['one','two','three','four'];
test('share links round-trip original Unicode, controls and lone surrogates', () => {
  const texts = ['👩🏽‍🚀\u200fمرحبا', '\u2067אבג\u2069', 'A\u0301\n𓀀', '\ud800'];
  assert.deepEqual(decodeTexts(encodeTexts(texts), defaults), texts);
  assert.deepEqual(decodeTexts(encodeTexts(texts.slice(0,3)), defaults), [...texts.slice(0,3), 'four']);
});
test('oversized sharing is refused without truncating the original or accepting partial links', () => {
  const texts = ['x'.repeat(MAX_SHARE_TEXT),'','',''];
  assert.deepEqual(decodeTexts(encodeTexts(texts), defaults), texts);
  texts[1] = '👩🏽‍🚀';
  assert.equal(encodeTexts(texts), null);
  assert.equal(texts[0].length, MAX_SHARE_TEXT);
  for (const hash of ['!', 'a'.repeat(2_000_001), btoa('{}'), btoa('{"texts":null}')]) {
    assert.equal(decodeTexts(hash, defaults), null);
  }
});
