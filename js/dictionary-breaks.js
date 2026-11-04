import { LineBreak } from './vendor/linebreak/LineBreak.js';

// UAX14 SA tailoring. Browser word dictionaries supply opportunities only
// inside same-script SA runs; the pinned line-break and grapheme rules still
// govern punctuation, controls, spaces and cluster integrity. Script detection
// selects the dictionary without requiring a language setting from the user.
const segmenters = new Map();
function localeFor(cp) {
  if (LineBreak.get(cp) !== 'SA') return null;
  if (cp >= 0x0e00 && cp <= 0x0e7f) return 'th';
  if (cp >= 0x0e80 && cp <= 0x0eff) return 'lo';
  if (cp >= 0x1780 && cp <= 0x17ff) return 'km';
  if ((cp >= 0x1000 && cp <= 0x109f) || (cp >= 0xa9e0 && cp <= 0xa9ff)
      || (cp >= 0xaa60 && cp <= 0xaa7f)) return 'my';
  return null;
}
export const usesDictionaryScript=text=>[...text].some(c=>localeFor(c.codePointAt(0))!==null);

function segmenter(locale) {
  if (typeof Intl.Segmenter !== 'function') return null;
  if (!segmenters.has(locale)) {
    const supported = Intl.Segmenter.supportedLocalesOf([locale]).length > 0;
    segmenters.set(locale, supported ? new Intl.Segmenter(locale, { granularity: 'word' }) : null);
  }
  return segmenters.get(locale);
}

export function dictionaryBreaks(text) {
  const positions = [];
  let locale = null, start = 0, offset = 0;
  const flush = end => {
    if (!locale) return;
    const engine = segmenter(locale);
    if (!engine) return;
    for (const part of engine.segment(text.slice(start, end))) {
      if (part.index > 0) positions.push(start + part.index);
    }
  };
  for (const char of text) {
    const next = localeFor(char.codePointAt(0));
    if (next !== locale) {
      flush(offset);
      start = offset;
      locale = next;
    }
    offset += char.length;
  }
  flush(offset);
  return positions;
}
