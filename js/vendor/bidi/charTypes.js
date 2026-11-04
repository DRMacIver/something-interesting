import { bidiClass } from '../../unicode-data.js';
import { lookup } from '../linebreak/LineBreak.js';
const DATA = Object.fromEntries(['R','EN','ES','ET','AN','CS','B','S','WS','ON','BN','NSM','AL','LRO','RLO','LRE','RLE','PDF','LRI','RLI','FSI','PDI'].map(t => [t, true]));

const TYPES = {}
const TYPES_TO_NAMES = {}
TYPES.L = 1 //L is the default
TYPES_TO_NAMES[1] = 'L'
Object.keys(DATA).forEach((type, i) => {
  TYPES[type] = 1 << (i + 1)
  TYPES_TO_NAMES[TYPES[type]] = type
})
Object.freeze(TYPES)

const ISOLATE_INIT_TYPES = TYPES.LRI | TYPES.RLI | TYPES.FSI
const STRONG_TYPES = TYPES.L | TYPES.R | TYPES.AL
const NEUTRAL_ISOLATE_TYPES = TYPES.B | TYPES.S | TYPES.WS | TYPES.ON | TYPES.FSI | TYPES.LRI | TYPES.RLI | TYPES.PDI
const BN_LIKE_TYPES = TYPES.BN | TYPES.RLE | TYPES.LRE | TYPES.RLO | TYPES.LRO | TYPES.PDF
const TRAILING_TYPES = TYPES.S | TYPES.WS | TYPES.B | ISOLATE_INIT_TYPES | TYPES.PDI | BN_LIKE_TYPES

// Unicode 18 classes, including normative @missing defaults.
function getBidiCharType(char) {
  return TYPES[lookup(bidiClass, char.codePointAt(0), 'L')];
}

/**
 * Get Bidi Character Type Name
 * @param {string} char
 * @returns { "L" | "R" | "EN" | "ES" | "ET" | "AN" | "CS" | "B" | "S" | "WS" | "ON" | "BN" | "NSM" | "AL" | "LRO" | "RLO" | "LRE" | "RLE" | "PDF" | "LRI" | "RLI" | "FSI" | "PDI" }
 */
function getBidiCharTypeName(char) {
  return TYPES_TO_NAMES[getBidiCharType(char)]
}

export {
  getBidiCharType,
  getBidiCharTypeName,
  TYPES,
  TYPES_TO_NAMES,
  ISOLATE_INIT_TYPES,
  STRONG_TYPES,
  NEUTRAL_ISOLATE_TYPES,
  BN_LIKE_TYPES,
  TRAILING_TYPES
}
