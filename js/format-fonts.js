// Unicode 18 §9.2/9.3: prefixed signs shape with the following number or
// Syriac abbreviation. Per-character CSS fallback loses that interaction.
import manifest from './font-manifest.js';
import { generalCategory, bidiClass } from './unicode-data.js';
import { lookup } from './vendor/linebreak/LineBreak.js';
import { requiresFormatGlyph, variationFontContains, fontMayIgnore } from './font-variations.js';

export const hasFormatSigns=text=>[...text].some(c=>requiresFormatGlyph(c.codePointAt(0)));

// Numeric format fields are graphical units, even when European digits
// resolve differently from an AN prefix. Isolate only those complete fields
// for paragraph ordering; preserve the user's logical text and controls.
export function prefixedNumberRanges(chars) {
  const result=[];
  for(let start=0;start<chars.length;start++){
    const cp=chars[start].codePointAt(0);
    if(!requiresFormatGlyph(cp)||lookup(bidiClass,cp,'')!=='AN')continue;
    let end=start+1;
    while(end<chars.length&&lookup(generalCategory,chars[end].codePointAt(0),'')==='Nd')end++;
    if(end>start+1)result.push({start,end});
  }
  return result;
}

export function formatFontSpans(text,inventory=manifest) {
  if(!hasFormatSigns(text))return [];
  const chars=[...text],offsets=[0],spans=[];
  for(const c of chars)offsets.push(offsets.at(-1)+c.length);
  const category=c=>lookup(generalCategory,c.codePointAt(0),'');
  const syriac=c=>/[\u0710-\u074f\u0860-\u086f\u200c\u200d]/u.test(c);
  for(let i=0;i<chars.length;i++){
    const cp=chars[i].codePointAt(0);
    if(!requiresFormatGlyph(cp))continue;
    let start=i,end=i+1;
    if(cp===0x70f){
      // Keep the whole joined word, including letters before SAM, in one face.
      while(start>0&&syriac(chars[start-1]))start--;
      while(end<chars.length&&syriac(chars[end]))end++;
    }else{
      while(end<chars.length&&(/^[NM]/.test(category(chars[end]))
        ||cp===0x605&&/[\u2c80-\u2cff\u03e2-\u03ef]/u.test(chars[end])))end++;
    }
    const points=chars.slice(start,end).map(c=>c.codePointAt(0));
    const font=inventory.fonts.find(f=>!f.sequences&&!f.variationOnly
      &&points.every(p=>variationFontContains(f.ranges,p)||fontMayIgnore(inventory.behaviouralRanges,p)));
    if(font)spans.push({start:offsets[start],end:offsets[end],font});
  }
  return spans;
}
