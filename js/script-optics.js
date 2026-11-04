// Give the finer handwritten alphabets comparable pen weight to Dad's Latin.
// Keep complete native words together so their own shaping/mark attachment runs.
import { graphemes } from './unicode.js';
const letters = '\\u0370-\\u03ff\\u1f00-\\u1fff\\u0400-\\u052f\\u1c80-\\u1c8f\\u2de0-\\u2dff\\ua640-\\ua69f\\u{1e030}-\\u{1e08f}';
const alphabet = new RegExp('['+letters+']', 'u');
const onlyAlphabet = new RegExp('^[\\s\\p{P}\\p{M}\\u202a-\\u202e\\u2066-\\u2069'+letters+']+$', 'u');
const letter = c => alphabet.test(c) && /\p{L}/u.test(c);
export const hasScriptOptics = text => alphabet.test(text) && [...text].some(letter);
export const scriptStroke = (text, size) => hasScriptOptics(text) && onlyAlphabet.test(text)
  ? size * (/[\u0400-\u052f\u1c80-\u1c8f\ua640-\ua69f]/u.test(text) ? .024 : .018) : 0;

export function splitScriptRuns(run) {
  if (run.emojiPolicy !== 'text' || !hasScriptOptics(run.text)) return [run];
  const override = run.drawText !== run.text;
  const parts = [];
  for (const cluster of graphemes(run.text)) {
    const weighted = letter([...cluster][0]);
    if (parts.at(-1)?.weighted === weighted) parts.at(-1).text += cluster;
    else parts.push({text:cluster,weighted});
  }
  return parts.map(({text}) => ({...run, text,
    drawText: override ? (run.direction === 'rtl' ? '\u202e' : '\u202d')+text+'\u202c' : text}));
}
