// Text must reach the font unchanged: uppercase styling belongs in glyphs,
// not a case conversion that changes mathematical or linguistic content.
// UAX #29 revision 49, extended grapheme clusters, pinned to Unicode 18.
// Bundling the data avoids silently inheriting an older browser ICU version.
import { graphemeBreak, indicConjunctBreak, extendedPictographic } from "./unicode-data.js";

function property(table, cp, fallback) {
  let lo = 0, hi = table.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >>> 1;
    const [first, last, value] = table[mid];
    if (cp < first) hi = mid - 1;
    else if (cp > last) lo = mid + 1;
    else return value;
  }
  return fallback;
}

const control = (p) => p === "Control" || p === "CR" || p === "LF";

export function* graphemeSegments(text) {
  let start = 0, offset = 0, previous = null;
  let regionalCount = 0, pictographicExtends = false, zwjAfterPictographic = false;
  let indicLinkerExtends = false;
  for (const char of text) {
    const cp = char.codePointAt(0);
    const current = property(graphemeBreak, cp, "Other");
    const incb = property(indicConjunctBreak, cp, "None");
    const pictographic = property(extendedPictographic, cp, false);
    let joins = false;
    if (previous === "CR" && current === "LF") joins = true; // GB3
    else if (control(previous) || control(current)) joins = false; // GB4/5
    else if (previous === "L" && ["L", "V", "LV", "LVT"].includes(current)) joins = true;
    else if (["LV", "V"].includes(previous) && ["V", "T"].includes(current)) joins = true;
    else if (["LVT", "T"].includes(previous) && current === "T") joins = true;
    else if (["Extend", "ZWJ", "SpacingMark"].includes(current)) joins = true;
    else if (previous === "Prepend") joins = true;
    else if (indicLinkerExtends && incb === "Consonant") joins = true; // GB9c (18.0)
    else if (zwjAfterPictographic && pictographic) joins = true; // GB11
    else if (current === "Regional_Indicator" && regionalCount % 2 === 1) joins = true;
    if (previous !== null && !joins) {
      yield { segment: text.slice(start, offset), index: start };
      start = offset;
    }
    zwjAfterPictographic = current === "ZWJ" && pictographicExtends;
    pictographicExtends = pictographic || (current === "Extend" && pictographicExtends);
    indicLinkerExtends = incb === "Linker" || (incb === "Extend" && indicLinkerExtends);
    regionalCount = current === "Regional_Indicator" ? regionalCount + 1 : 0;
    previous = current;
    offset += char.length;
  }
  if (offset > start) yield { segment: text.slice(start), index: start };
}

export function graphemes(text) {
  return Array.from(graphemeSegments(text), ({ segment }) => segment);
}

// The largest complete-grapheme prefix within a UTF-16 resource budget.
// A single enormous combining sequence may yield an empty prefix; never
// manufacture a broken surrogate, half a flag, or detached combining mark.
export function graphemePrefix(text, maxUnits) {
  if (maxUnits <= 0) return "";
  if (text.length <= maxUnits) return text;
  // One full scalar beyond the budget is enough to decide whether the last
  // cluster continues. Do not scan a million-mark cluster just to discard it.
  const bounded = text.slice(0, maxUnits + 2);
  let end = 0;
  for (const { segment, index } of graphemeSegments(bounded)) {
    if (index + segment.length > maxUnits) break;
    end = index + segment.length;
  }
  return text.slice(0, end);
}
