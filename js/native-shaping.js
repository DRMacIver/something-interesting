import { graphemes } from "./unicode.js";
// Shape-only aliases for older browser Unicode data and script itemization.
// Logical input, grapheme boundaries, bidi, sharing and exported metadata keep
// the original text. The bundled font's UVS entries select the same drawings.
const above = new Set([0x10ecb,0x10ece,0x10ecf,0x10ef3,0x10ef5,0x10ef7,0x10ef8,0x10ef9]);
const points = [0x10ecb,0x10ecc,0x10ecd,0x10ece,0x10ecf,...Array.from({length:10},(_,i)=>0x10ef0+i)];
const aliases = new Map(points.map((cp,i)=>[String.fromCodePoint(cp),String.fromCodePoint(above.has(cp)?0x652:0x650,0xe0100+i)]));
const crownBases = [0x628,0x67e,0x62a,0x62b,0x62c,0x62d,0x62e,0x633,0x634,0x635,0x636,0x637,0x638,0x639,0x63a,0x641,0x642,0x643,0x645,0x646,0x647,0x64a];
// ZWNJ prevents joining on the right; the known Arabic letter still joins on
// the left. UVS selects the actual crown drawing, not an ordinary letter.
crownBases.forEach((base,i)=>aliases.set(String.fromCodePoint(0x10ed9+i),'\u200c'+String.fromCodePoint(base,0xe0120+i)));
[0xB53,0xB54].forEach((cp,i)=>aliases.set(String.fromCodePoint(cp),String.fromCodePoint(0xB55,0xE0140+i)));
aliases.set('\u{11df0}','\u0981\u{e0151}');
aliases.set('\u{11df1}','\u09ac\u{e0150}');
aliases.set('\u{11b0a}','\u097e\u{e0160}');
[[0x11b60,0x111bc,0xe0180],[0x11b62,0x111b6,0xe0181],[0x11b63,0x111b7,0xe0182],[0x11b64,0x111bc,0xe0183],[0x11b66,0x111bc,0xe0184],[0x11b61,0x111b3,0xe0185],[0x11b65,0x111b3,0xe0186],[0x11b67,0x111b3,0xe0187]].forEach(([cp,base,vs])=>aliases.set(String.fromCodePoint(cp),String.fromCodePoint(base,vs)));
export function nativeShapingText(text) {
  // Cyrillic marks otherwise split from Glagolitic bases in browser shaping.
  // The inherited carrier preserves the original glyph through a font UVS.
  if(/[\u0483\u0484\u0487]/u.test(text)) text=graphemes(text).map(g=>/^[\u2c00-\u2c5f]/u.test(g)
    ? g.replace(/[\u0483\u0484\u0487]/gu,c=>"\u0303"+String.fromCodePoint(0xe0170+["\u0483","\u0484","\u0487"].indexOf(c))) : g).join("");
  // Older Indic normalizers do not split these vowels following a UVS base.
  // Apply canonical decomposition only to drawing text containing new Bengali characters.
  if(/[\u{11df0}\u{11df1}]/u.test(text)) text=text.replace(/\u09cb/g,"\u09c7\u09be").replace(/\u09cc/g,"\u09c7\u09d7");
  // Tall I/II/AU signs and reph rise over the consonant. Select the raised ring
  // only within its own Unicode grapheme, including conjuncts and reph.
  if(text.includes("\u{11df0}")) text=graphemes(text).map(g=>(/[\u09bf\u09c0\u09cc\u09d7]/u.test(g) || /[\u09b0\u09f0]\u09cd/u.test(g)) ? g.replace(/\u{11df0}/gu,"\u0981\u{e0152}") : g).join("");
  return text.replace(/[\u{11b60}-\u{11b67}\u{11b0a}\u{11df0}\u{11df1}\u0b53\u0b54\u{10ecb}-\u{10ecf}\u{10ed9}-\u{10eee}\u{10ef0}-\u{10ef9}]/gu,c=>aliases.get(c));
}
