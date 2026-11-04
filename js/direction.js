import { bidiClass } from './unicode-data.js';
import { lookup } from './vendor/linebreak/LineBreak.js';
import { prefixedNumberRanges } from './format-fonts.js';

// UAX #9 P2/P3: first strong character outside isolates sets paragraph level.
// Actual shaping/reordering is delegated to canvas; this is not a full UBA.
export function paragraphDirection(text) {
  let isolates = 0;
  for (const char of text) {
    const cls = lookup(bidiClass, char.codePointAt(0), 'L');
    if (cls === 'B') break;
    if (['LRI', 'RLI', 'FSI'].includes(cls)) isolates++;
    else if (cls === 'PDI') isolates = Math.max(0, isolates - 1);
    else if (!isolates) {
      if (cls === 'L') return 'ltr';
      if (cls === 'R' || cls === 'AL') return 'rtl';
    }
  }
  return 'ltr';
}

import { getEmbeddingLevels } from './vendor/bidi/embeddingLevels.js';
import { getBidiCharType, TRAILING_TYPES } from './vendor/bidi/charTypes.js';

// Resolve once for the whole paragraph. Returned line offsets are UTF-16,
// matching layout's source slices; the bidi engine uses Unicode scalar indices.
export function bidiParagraph(text, baseDirection) {
  const chars = Array.from(text);
  const fields=prefixedNumberRanges(chars);
  let resolved;
  if(fields.length){
    const input=[],indexes=[],starts=new Set(fields.map(f=>f.start)),ends=new Set(fields.map(f=>f.end));
    for(let i=0;i<chars.length;i++){
      if(starts.has(i))input.push('\u2066');
      indexes.push(input.length);input.push(chars[i]);
      if(ends.has(i+1))input.push('\u2069');
    }
    const shaped=getEmbeddingLevels(input,baseDirection);
    resolved={...shaped,levels:indexes.map(i=>shaped.levels[i])};
  }else resolved=getEmbeddingLevels(chars, baseDirection);
  const base = resolved.paragraphs[0]?.level ?? 0;
  const offsets = new Map();
  let offset = 0;
  chars.forEach((char, i) => { offsets.set(offset, i); offset += char.length; });
  offsets.set(offset, chars.length);
  const complex = chars.some(char => ['R', 'AL', 'AN', 'RLE', 'LRE', 'RLO', 'LRO', 'LRI', 'RLI', 'FSI', 'PDI'].includes(lookup(bidiClass, char.codePointAt(0), 'L')));
  return {
    direction: base ? 'rtl' : 'ltr',
    runs(start, content) {
      if (!complex) return null;
      let source = offsets.get(start);
      if (source === undefined) throw new Error('Bidi slice starts inside a Unicode scalar');
      const entries = [];
      const contentChars = Array.from(content);
      for (const [index, char] of contentChars.entries()) {
        // Layout removes discretionary controls and may render SHY as '-'.
        while (source < chars.length && ['\u00ad', '\u200b'].includes(chars[source])) {
          let nextVisible = source + 1;
          while (['\u00ad', '\u200b'].includes(chars[nextVisible])) nextVisible++;
          if (chars[source] === '\u00ad' && char === '-' && index === contentChars.length - 1
            && chars[nextVisible] !== '-') break;
          source++;
        }
        entries.push({char, level: resolved.levels[source] ?? base});
        source++;
      }
      // L1: whitespace/isolate formatting at a soft line end uses base level.
      for (let i = entries.length - 1; i >= 0 && (getBidiCharType(entries[i].char) & TRAILING_TYPES); i--) entries[i].level = base;
      const runs = [];
      for (const [index,{char, level}] of entries.entries()) {
        // These have already done their job in the paragraph algorithm. Keep
        // joining controls, variation selectors and other shaping characters.
        if (/[\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/u.test(char)) continue;
        const last = runs.at(-1);
        // X9 removes BN for ordering, but ZWJ/ZWNJ still affect shaping.
        // A trailing joiner reset by L1 must stay with its preceding letters.
        if (last && (last.level === level || lookup(bidiClass, char.codePointAt(0), 'L') === 'BN')) {last.text += char;last.end=index+1;}
        else runs.push({text: char, level,start:index,end:index+1});
      }
      // L2, at run granularity. Characters within a run stay in logical order
      // for native shaping. A single override prevents canvas re-resolving
      // numbers/neutrals using a different, line-local context.
      const max = Math.max(base, ...runs.map(r => r.level));
      const minOdd = Math.min(...runs.map(r => r.level | 1));
      for (let level = max; level >= minOdd; level--) {
        for (let i = 0; i < runs.length; i++) {
          if (runs[i].level < level) continue;
          let end = i + 1;
          while (end < runs.length && runs[end].level >= level) end++;
          runs.splice(i, end - i, ...runs.slice(i, end).reverse());
          i = end - 1;
        }
      }
      // Distinct levels can have the same direction (AN prefixes beside EN
      // digits in an LTR paragraph). After L2, adjacent logical fragments of
      // that direction may shape together. Reordered fragments or explicit
      // control boundaries must stay separate. Splitting here otherwise
      // prevents prefixed number signs from enclosing their following digits.
      const shaped=[];
      for(const run of runs){
        const last=shaped.at(-1);
        if(last&&last.end===run.start&&(last.level&1)===(run.level&1)){
          last.text+=run.text;last.end=run.end;
        }else shaped.push({...run});
      }
      return shaped.map(({text, level}) => ({text, direction: level & 1 ? 'rtl' : 'ltr',
        drawText: (level & 1 ? '\u202e' : '\u202d') + text + '\u202c'}));
    },
  };
}
