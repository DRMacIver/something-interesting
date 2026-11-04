import gridManifest from './grid-manifest.js';
// Structural diagrams use a spatial left-to-right grid. Labels retain their
// native shaping/direction; never reverse a joining script character by character.
import { graphemes } from './unicode.js';
import { paragraphDirection } from './direction.js';
import { gridWide, gridSimple, generalCategory } from './unicode-data.js';
import { lookup } from './vendor/linebreak/LineBreak.js';

// Use the delivered grid repertoire, including non-contiguous legacy ranges.
const gridSymbol = new RegExp('^[' + (gridManifest.structuralRanges??gridManifest.ranges).map(([a,b]) =>
  `\\u{${a.toString(16)}}` + (a===b?'':`-\\u{${b.toString(16)}}`)).join('') + ']$', 'u');
export const isGridSymbol = char => gridSymbol.test(char);
export function isGridText(text) {
  if(/[\r\n\u2028\u2029]/u.test(text)&&/^\s*\+[-=]{2,}\+/mu.test(text))return true;
  const frame=/^[│┃║┆┇┊┋╎╏┌┐└┘╔╗╚╝╭╮╰╯|+][\s\S]*[│┃║┆┇┊┋╎╏┌┐└┘╔╗╚╝╭╮╰╯|+]$/u;
  for(const row of text.split(/[\n\r\v\f\u0085\u2028\u2029]/u)){
    const cells=graphemes(row).filter(c=>!/^\s+$/u.test(c));
    const structural=cells.filter(isGridSymbol).length;
    if(!structural)continue;
    if(frame.test(row.trim()))return true;
    // Pure shading/Braille/connecting pieces are spatial even in one row.
    // Sparse inline symbols in a sentence retain proportional prose layout.
    if(cells.every(c=>isGridSymbol(c)||/^[+\-=|/\\<>^v]$/u.test(c)))return true;
    let run=0,longest=0;
    for(const c of cells){run=isGridSymbol(c)?run+1:0;longest=Math.max(longest,run);}
    if(structural/cells.length>=.35&&longest>=2)return true;
  }
  return false;
}

export function cellColumns(cluster) {
  const chars = Array.from(cluster);
  const bases = chars.filter(c => !['Mn','Mc','Me','Cf'].includes(lookup(generalCategory, c.codePointAt(0), 'Cn')));
  if (!bases.length) return chars.every(c => lookup(generalCategory,c.codePointAt(0),'Cn') === 'Cf') ? 0 : 1;
  if (bases.some(c => lookup(gridWide,c.codePointAt(0),false)) || cluster.includes('\ufe0f')
    || bases.some(c => c.codePointAt(0) >= 0x1f1e6 && c.codePointAt(0) <= 0x1f1ff)) return 2;
  return 1;
}

export function gridRows(text) {
  const rows = text.replace(/\r\n/g,'\n').split(/[\n\r\v\f\u0085\u2028\u2029]/u);
  while (rows.length && !rows[0].trim()) rows.shift();
  while (rows.length && !rows.at(-1).trim()) rows.pop();
  return rows.map(row => {
    let expanded = '', column = 0;
    for (const cluster of graphemes(row)) {
      if (cluster === '\t') {
        const count = 4 - column % 4;
        expanded += ' '.repeat(count); column += count;
      } else { expanded += cluster; column += cellColumns(cluster); }
    }
    return expanded;
  });
}

function rowTokens(row) {
  const tokens = [];
  let column = 0, word = [];
  const flush = () => {
    if (!word.length) return;
    // A complex label is one shaping/bidi field, including internal spaces:
    // rendering Arabic words separately in logical order would reverse their
    // reading order. Keep outer ASCII padding in its original cells.
    if (word.some(t => /[\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]/u.test(t.text)
      || Array.from(t.text).some(c => !lookup(gridSimple,c.codePointAt(0),false)))) {
      while (word.length && /^ +$/u.test(word[0].text)) tokens.push(word.shift());
      const tail = [];
      while (word.length && /^ +$/u.test(word.at(-1).text)) tail.unshift(word.pop());
      if (word.length) tokens.push({text:word.map(t=>t.text).join(''), column:word[0].column,
        columns:word.reduce((n,t)=>n+t.columns,0), structural:false});
      tokens.push(...tail);
    } else tokens.push(...word);
    word = [];
  };
  for (const text of graphemes(row)) {
    const structural = isGridSymbol(text);
    const columns = structural ? 1 : cellColumns(text);
    const token = {text,column,columns,structural};
    if (structural || text === '|' || text === '+') { flush(); tokens.push(token); }
    else word.push(token);
    column += columns;
  }
  flush();
  return {tokens,columns:column};
}

export function measureGrid(text, size, measure) {
  const rows = gridRows(text).map(row => ({text:row, ...rowTokens(row)}));
  const labelInk = token => measure.forParagraph?.(token.text).at(0).ink(token.text,size)
    ?? measure.ink(token.text,size,paragraphDirection(token.text));
  let ascent = size * 0.7, descent = 0;
  for (const row of rows) for (const token of row.tokens) {
    if (token.structural || !token.text.trim()) continue;
    const ink = labelInk(token);
    ascent = Math.max(ascent,ink.ascent); descent = Math.max(descent,ink.descent);
  }
  const height = Math.max(size * 1.1, ascent + descent + size * 0.15);
  const baseline = (height - ascent - descent)/2 + ascent;
  // The legacy donor uses square cells; preserve constructed circles and faces.
  const squareCells=[...text].some(c=>gridManifest.squareCellRanges?.some(([a,b])=>a<=c.codePointAt(0)&&c.codePointAt(0)<=b));
  const cellWidth = height * (squareCells ? 1 : 0.6);
  const columns = Math.max(0,...rows.map(r=>r.columns));
  return {width:columns*cellWidth, height:rows.length*height, lineHeight:height,
    rows:rows.map(row => {
      const runs = [];
      for (const token of row.tokens) {
        if (!token.text.trim() || !token.columns) continue;
        const fontSize = token.structural ? height : size;
        const direction = token.structural ? 'ltr' : paragraphDirection(token.text);
        const ink = token.structural ? measure.ink(token.text,fontSize,direction) : labelInk(token);
        const room = token.columns*cellWidth;
        const scaleX = token.structural ? cellWidth/(height*0.6) : Math.min(1,room / Math.max(ink.width,1e-9));
        const offset = token.column*cellWidth + (room-ink.width*scaleX)/2 + ink.drawOffset*scaleX;
        for (const native of ink.runs ?? [{drawText:token.text,text:token.text,direction,offset:0,font:ink.font}]) {
          runs.push({...native, fontSize:ink.fontSize ?? fontSize,
            offset:offset+native.offset*scaleX, scaleX,
            baselineOffset:token.structural ? height*0.8-baseline : 0});
        }
      }
      return {text:row.text,units:[row.text],direction:'ltr',width:columns*cellWidth,height,
        fontSize:size,baseline,grid:true,
        ink:{fontSize:size,width:columns*cellWidth,advance:columns*cellWidth,drawOffset:0,
          ascent:baseline,descent:height-baseline,runs}};
    })};
}
