import { bidiBrackets } from '../../unicode-data.js';
const opening = new Map(), closing = new Map();
for (const [cp, pair, type] of bidiBrackets) {
  (type === 'o' ? opening : closing).set(String.fromCodePoint(cp), String.fromCodePoint(pair));
}
export function openingToClosingBracket(char) { return opening.get(char) ?? null; }
export function closingToOpeningBracket(char) { return closing.get(char) ?? null; }
// N0: U+2329/U+232A are canonically equivalent to U+3008/U+3009.
export function getCanonicalBracket(char) {
  return char === '\u2329' ? '\u3008' : char === '\u232a' ? '\u3009' : null;
}
