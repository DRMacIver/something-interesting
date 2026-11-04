// Aref Ruqaa has no Tatweel ink/advance, even in connected words. Select one
// complete native font for a joining field containing an extender; never split
// its Arabic/Syriac/etc. bases to insert a glyph from another face.
import manifest from './font-manifest.js';
import { graphemes } from './unicode.js';
import { generalCategory } from './unicode-data.js';
import { lookup } from './vendor/linebreak/LineBreak.js';
import { hasJoiningCharacters, variationFontContains, fontMayIgnore } from './font-variations.js';

export function standaloneFontSpans(text,inventory=manifest) {
  if(!text.includes('\u0640'))return [];
  const spans=[];let offset=0,start=0,end=0,tatweel=false;
  const flush=()=>{
    if(tatweel){
      const points=[...text.slice(start,end)].map(c=>c.codePointAt(0));
      const font=inventory.fonts.find(f=>!f.sequences&&!f.variationOnly
        &&!(typeof f.source==='string'&&f.source.endsWith('/ArefRuqaa-Regular.ttf'))
        &&variationFontContains(f.ranges,0x640)
        &&points.every(cp=>variationFontContains(f.ranges,cp)||fontMayIgnore(inventory.behaviouralRanges,cp)));
      if(font)spans.push({start,end,font});
    }
    tatweel=false;start=end;
  };
  for(const cluster of graphemes(text)){
    const points=[...cluster];
    const base=points.find(c=>!['Mn','Mc','Me','Cf'].includes(lookup(generalCategory,c.codePointAt(0),'')));
    const boundary=cluster.includes('\u200b')||base&&base!=='\u0640'&&!hasJoiningCharacters(base);
    if(boundary){flush();offset+=cluster.length;start=end=offset;continue;}
    if(start===end)start=offset;
    end=offset+cluster.length;
    tatweel ||= cluster.includes('\u0640');
    // A ZWNJ explicitly ends a joining field even when it shares a grapheme
    // with the preceding letter. ZWJ and transparent marks stay in the field.
    if(cluster.includes('\u200c'))flush();
    offset=end;
  }
  flush();return spans;
}
