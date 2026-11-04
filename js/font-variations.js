// Native UVS support is distinct from ordinary character coverage.
import scriptManifest from './font-manifest.js';
import cjkVariants from './cjk-variant-manifest.js';
import mathVariants from './math-variant-manifest.js';
import markedCjkVariants from './marked-cjk-variant-manifest.js';
import { joiningFontCharacters, variationContextScript, fontDependentFormat, generalCategory } from './unicode-data.js';
import { lookup } from './vendor/linebreak/LineBreak.js';

export const variationFontContains = (ranges, cp) => {
  let low = 0, high = ranges?.length ?? 0;
  while (low < high) {
    const mid = (low + high) >>> 1;
    if (cp < ranges[mid][0]) high = mid;
    else if (cp > ranges[mid][1]) low = mid + 1;
    else return true;
  }
  return false;
};
const contains=variationFontContains;
export const requiresFormatGlyph=cp=>contains(fontDependentFormat,cp);
// A format character can require both behaviour and a visible source glyph.
export const fontMayIgnore=(ranges,cp)=>contains(ranges,cp)&&!requiresFormatGlyph(cp);

export const isVariationSelector = cp => (cp >= 0xfe00 && cp <= 0xfe0f)
  || (cp >= 0xe0100 && cp <= 0xe01ef);
export const hasVariationSelectors = text => /[\ufe00-\ufe0f\u{e0100}-\u{e01ef}]/u.test(text);
export const hasJoiningCharacters = text => Array.from(text).some(c =>
  contains(joiningFontCharacters, c.codePointAt(0)) || contains(variationContextScript, c.codePointAt(0)));

export function variationPairs(text) {
  const points = Array.from(text, c => c.codePointAt(0));
  return points.flatMap((cp, i) => i > 0 && isVariationSelector(cp)
    && !isVariationSelector(points[i-1]) ? [[points[i-1], cp]] : []);
}

export function supportsVariations(font, text) {
  const pairs = variationPairs(text);
  return pairs.length > 0 && pairs.every(([base, selector]) =>
    contains(font.nativeVariations?.[selector], base));
}

const variationInventory = {...scriptManifest, fonts:[cjkVariants, mathVariants, ...scriptManifest.fonts, ...markedCjkVariants.fonts]};

export function nativeVariationCandidates(cluster, inventory=variationInventory) {
  return hasVariationSelectors(cluster) ? inventory.fonts.filter(font=>!font.sequences&&supportsVariations(font,cluster)) : [];
}

export function nativeVariationFont(cluster, inventory = variationInventory) {
  if (!hasVariationSelectors(cluster)) return undefined;
  return inventory.fonts.find(font => !font.sequences
    && supportsVariations(font, cluster)
    && Array.from(cluster, c => c.codePointAt(0)).every(cp => isVariationSelector(cp)
      || fontMayIgnore(inventory.behaviouralRanges, cp) || contains(font.ranges, cp)));
}

// Foreign spacing vowels need their source shaper (including prebase/split
// forms), not the geometric Mn compositor. Keep a registered nonjoining UVS
// prefix intact, and shape the unsupported tail in its own native fragment.
// A complete native cluster stays together; load missing mark sources too.
// Never apply this to connected native bases or unregistered selectors.
export function nativeSpacingVariationPlan(cluster,inventory=variationInventory) {
  const chars=[...cluster];
  if(!hasVariationSelectors(cluster)||hasJoiningCharacters(chars[0]??'')
    ||!isVariationSelector(chars[1]?.codePointAt(0))
    ||!chars.slice(2).every(c=>lookup(generalCategory,c.codePointAt(0),'').startsWith('M'))
    ||!chars.some(c=>lookup(generalCategory,c.codePointAt(0),'')==='Mc'))return undefined;
  const complete=nativeVariationFont(cluster,inventory);
  if(complete)return {font:complete,body:cluster,tail:''};
  let best;
  for(const font of nativeVariationCandidates(cluster,inventory)){
    const index=chars.findIndex(c=>!isVariationSelector(c.codePointAt(0))
      &&!fontMayIgnore(inventory.behaviouralRanges,c.codePointAt(0))
      &&!contains(font.ranges,c.codePointAt(0)));
    if(index>1&&chars.slice(index).every(c=>lookup(generalCategory,c.codePointAt(0),'').startsWith('M'))
      &&(!best||index>best.index))best={font,index};
  }
  return best?{font:best.font,body:chars.slice(0,best.index).join(''),tail:chars.slice(best.index).join('')}:undefined;
}
export const nativeSpacingVariationFont=(cluster,inventory)=>nativeSpacingVariationPlan(cluster,inventory)?.font;
