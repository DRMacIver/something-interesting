// Adapter for the upstream rules; use our pinned Unicode 18 tables.
import { lineBreak, generalCategory, extendedPictographic } from '../../unicode-data.js';
export function lookup(table, cp, fallback) {
  let low = 0, high = table.length;
  while (low < high) {
    const mid = (low + high) >>> 1;
    if (cp < table[mid][0]) high = mid;
    else if (cp > table[mid][1]) low = mid + 1;
    else return table[mid][2];
  }
  return fallback;
}
const classes = ['AI','AK','AL','AP','AS','B2','BA','BB','BK','CB','CJ','CL','CM','CP','CR','EB','EM','EX','GL','H2','H3','HH','HL','HY','ID','IN','IS','JL','JT','JV','LF','NL','NS','NU','OP','PO','PR','QU','RI','SA','SG','SP','SY','VF','VI','WJ','XX','ZW','ZWJ'];
export const names = Object.fromEntries(classes.map(c => [c,c]));
export const values = names;
export const LineBreak = { get: cp => lookup(lineBreak, cp, 'XX') };
export const category = char => lookup(generalCategory, char.codePointAt(0), 'Cn');
export const pictographic = char => lookup(extendedPictographic, char.codePointAt(0), false);
