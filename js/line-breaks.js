import { egyptianSegmentInteriors } from './egyptian-layout.js';
import { Rules } from './vendor/linebreak/index.js';
import { graphemeSegments } from './unicode.js';
import { dictionaryBreaks } from './dictionary-breaks.js';
import { annotationPlan } from './combining-annotations.js';

const rules = new Rules();
const unitCache = new Map(), paragraphCache = new Map();
function remember(cache, key, value, limit) {
  if (cache.size >= limit) cache.delete(cache.keys().next().value);
  cache.set(key, value);
  return value;
}
// Keep original separators on each unit. Joining units must never manufacture
// spaces (CJK) or erase intentional internal whitespace (text diagrams).
export function breakUnits(text) {
  if (unitCache.has(text)) return unitCache.get(text);
  const boundaries = new Set([...graphemeSegments(text)].map(({index, segment}) => index + segment.length));
  const result = [];
  const interiors = egyptianSegmentInteriors(text);
  let start = 0;
  const opportunities = new Set([...rules.breaks(text)].map(({position}) => position));
  for (const position of dictionaryBreaks(text)) opportunities.add(position);
  for (const position of [...opportunities].sort((a, b) => a - b)) {
    if (!boundaries.has(position) || interiors.has(position)) continue;
    result.push(text.slice(start, position));
    start = position;
  }
  if (start < text.length) result.push(text.slice(start));
  return remember(unitCache, text, Object.freeze(result), 128);
}

export function lineContent(units, endsParagraph = false) {
  const joined = units.join('').replace(/[ \t\u200b]+$/u, '');
  const hyphen = !endsParagraph && joined.endsWith('\u00ad') ? '-' : '';
  return joined.replace(/[\u00ad\u200b]/gu, '') + hyphen;
}

export function textParagraphs(text) {
  if (paragraphCache.has(text)) return paragraphCache.get(text);
  const lines = text.replace(/\r\n/g, '\n').split(/[\n\r\v\f\u0085\u2028\u2029]/u);
  // Ignore empty outer lines, but retain indentation and internal spacing.
  while (lines.length && /^[ \t]*$/u.test(lines[0])) lines.shift();
  while (lines.length && /^[ \t]*$/u.test(lines.at(-1))) lines.pop();
  return remember(paragraphCache, text, Object.freeze(lines.map(line => {
    let column = 0, expanded = '';
    for (const {segment} of graphemeSegments(line)) {
      if (segment === '\t') {
        const spaces = 4 - column % 4;
        expanded += ' '.repeat(spaces);
        column += spaces;
      } else {
        expanded += segment;
        column++;
      }
    }
    return breakUnits(expanded);
  })), 32);
}

// Emergency word splitting still respects punctuation/glue. If the smallest
// protected unit is wider than the panel, report overflow so the comic can grow.
import { LineBreak,lookup } from './vendor/linebreak/LineBreak.js';
import { generalCategory } from './unicode-data.js';
export function emergencyBoundary(left, right) {
  if(annotationPlan(left)?.doubles.length)return false;
  // Some Mc vowels are intentionally separate UAX29 graphemes. They still
  // depend on their preceding base for typography and cannot start a line.
  if(lookup(generalCategory,right.codePointAt(0),'').startsWith('M'))return false;
  const a = LineBreak.get([...left].at(-1).codePointAt(0));
  const b = LineBreak.get(right.codePointAt(0));
  return !['OP', 'QU', 'WJ', 'GL'].includes(a)
    && !['CL', 'CP', 'EX', 'IS', 'SY', 'NS', 'IN', 'QU', 'GL', 'WJ', 'ZWJ'].includes(b);
}
