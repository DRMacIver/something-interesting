// Bundled font routing. Source fonts remain provisional until visual review.
import scriptManifest from './font-manifest.js';
import { requiresEgyptianLayout } from './egyptian-layout.js';
export const egyptianSignFamily = scriptManifest.fonts.find(f=>typeof f.source === 'string' && f.source.endsWith('/UniHieroglyphica.ttf'))?.family;
import emoji from './emoji-manifest.js';
import greek from './greek-manifest.js';
import grid from './grid-manifest.js';
import egyptianVariants from './egyptian-variant-manifest.js';
import cjkVariants from './cjk-variant-manifest.js';
import mathVariants from './math-variant-manifest.js';
import markedCjkVariants from './marked-cjk-variant-manifest.js';
import { graphemes } from './unicode.js';
import { joiningScript, joiningFontCharacters, variationContextScript } from './unicode-data.js';
import { emojiPolicy, routingClusters } from './emoji-routing.js';
import { nativeVariationFont, nativeSpacingVariationFont, supportsVariations, variationPairs, fontMayIgnore } from './font-variations.js';
import { annotationFontText, hasConnectedEgyptian } from './combining-annotations.js';
import { standaloneFontSpans } from './standalone-fonts.js';
import { formatFontSpans } from './format-fonts.js';
const manifest = { ...scriptManifest, fonts: [emoji, grid, egyptianVariants, cjkVariants, mathVariants, greek, ...scriptManifest.fonts, ...markedCjkVariants.fonts] };
export const variationFontFamilies = new Set(manifest.fonts.filter(f=>f.variationOnly).map(f=>f.family));

export function contains(ranges, cp) {
  let low = 0, high = ranges.length;
  while (low < high) {
    const mid = (low + high) >>> 1;
    if (cp < ranges[mid][0]) high = mid;
    else if (cp > ranges[mid][1]) low = mid + 1;
    else return true;
  }
  return false;
}

function joiningScriptOf(cp, table = joiningScript) {
  let lo = 0, hi = table.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1, [start, end, script] = table[mid];
    if (cp < start) hi = mid;
    else if (cp > end) lo = mid + 1;
    else return script;
  }
  return null;
}

const joiningScripts = new Set(joiningScript.map(row => row[2]));
const clusterScript = points => (points.some(cp => /\p{Script=Greek}/u.test(String.fromCodePoint(cp))) ? 'Greek' : null)
  ?? (points.some(cp => {const c=String.fromCodePoint(cp);return /\p{L}/u.test(c)&&/\p{Script=Cyrillic}/u.test(c);}) ? 'Cyrillic' : null)
  ?? points.filter(cp => contains(joiningFontCharacters, cp)).map(cp => joiningScriptOf(cp)).find(Boolean)
  ?? points.map(cp => joiningScriptOf(cp, variationContextScript)).find(script => script && !joiningScripts.has(script));

function fontClusters(text) {
  const nativeContext=hasConnectedEgyptian(text);
  return routingClusters(text).flatMap(cluster=>{
    const body=annotationFontText(cluster);
    // A connected native run can decline dynamic composition. Supply both its
    // original marks and the base spans used by independent annotated runs.
    return nativeContext&&body!==cluster?[cluster,body]:[body];
  });
}

export function requiredFonts(texts, inventory = manifest) {
  // CSS fallback is per character, so loading a second font for one new Arabic
  // letter alone can sever its native joining. Prefer one font for each joining
  // script's complete requested repertoire, including marks on its clusters.
  const scriptPoints = new Map();
  const scriptVariants = new Map();
  for (const text of texts) for (const cluster of graphemes(text)) {
    const points = [...cluster].map(c => c.codePointAt(0));
    const script = clusterScript(points);
    if (!script) continue;
    if (!scriptPoints.has(script)) scriptPoints.set(script, new Set());
    if (variationPairs(cluster).length) {
      if (!scriptVariants.has(script)) scriptVariants.set(script, []);
      scriptVariants.get(script).push(cluster);
    }
    for (const cp of points) if (!fontMayIgnore(inventory.behaviouralRanges, cp)) scriptPoints.get(script).add(cp);
  }
  const preferred = new Map();
  for (const [script, points] of scriptPoints) {
    if(!points.size)continue;
    if (!joiningScripts.has(script) && !scriptVariants.has(script) && !['Greek','Cyrillic'].includes(script)) continue;
    const covers = font => !font.sequences && !font.variationOnly && [...points].every(cp => contains(font.ranges, cp));
    const variants = scriptVariants.get(script) ?? [];
    // Prefer proportional handwritten alphabets over Klee's wide, fine cells.
    // The Greek companion completes WenKai's polytonic coverage, keeping an
    // accented word in the same handwriting as the rest of the passage.
    let index = ['Greek','Cyrillic'].includes(script) ? inventory.fonts.findIndex(font =>
      /\/LXGWWenKai-Regular\.ttf$/.test(font.source ?? '') && covers(font)
      && variants.every(cluster => supportsVariations(font, cluster))) : -1;
    if (index < 0) index = inventory.fonts.findIndex(font => covers(font) && variants.every(cluster => supportsVariations(font, cluster)));
    if (index < 0) index = inventory.fonts.findIndex(covers);
    if (index >= 0) preferred.set(script, index);
  }
  const selected = new Set();
  for(const text of texts)for(const span of formatFontSpans(text,inventory))selected.add(inventory.fonts.indexOf(span.font));
  for(const text of texts)for(const span of standaloneFontSpans(text,inventory))selected.add(inventory.fonts.indexOf(span.font));
  if (texts.some(requiresEgyptianLayout)) {
    const complete=inventory.fonts.findIndex(f=>typeof f.source === 'string' && f.source.endsWith('/UniHieroglyphica.ttf'));
    if (complete>=0) selected.add(complete);
  }
  const missing = new Set();
  const emojiFallbacks = new Set();
  for (const text of texts) for (const cluster of fontClusters(text)) {
    const spacingVariant=emojiPolicy(cluster)==='text'&&nativeSpacingVariationFont(cluster,inventory);
    if(spacingVariant)selected.add(inventory.fonts.indexOf(spacingVariant));
    const script = clusterScript([...cluster].map(c => c.codePointAt(0)));
    if (preferred.has(script)) { selected.add(preferred.get(script)); continue; }
    const variantCluster=cluster.replace(/([\u{13000}-\u{143ff}][\ufe00-\ufe06])\u{13440}?[\u{13447}-\u{13455}]?$/u,'$1');
    const sequence = inventory.fonts.findIndex(font => (font.sequences?.includes(cluster) || font.variationSequences?.includes(variantCluster)));
    if (sequence >= 0) { selected.add(sequence); continue; }
    if (emojiPolicy(cluster) === 'text') {
      const variationFont = nativeVariationFont(cluster, inventory);
      if (variationFont) { selected.add(inventory.fonts.indexOf(variationFont)); continue; }
    }
    const native = emojiPolicy(cluster) === 'native';
    if (native) emojiFallbacks.add(cluster);
    const eligible = font => !font.sequences && !font.variationOnly;
    // Keep native base/mark attachment in one font whenever possible.
    const points = [...cluster].map(c => c.codePointAt(0));
    if (!native && points.length > 1 && !contains(inventory.baseRanges, points[0])) {
      const whole = inventory.fonts.findIndex(font => eligible(font) && points.every(cp =>
        contains(font.ranges, cp) || fontMayIgnore(inventory.behaviouralRanges, cp)));
      if (whole >= 0) { selected.add(whole); continue; }
    }
    for (const character of cluster) {
      const cp = character.codePointAt(0);
      const override = inventory.fonts.findIndex(font => font.overrideBase && eligible(font) && contains(font.ranges, cp));
      if (override >= 0) { if (!native) selected.add(override); continue; }
      if (contains(inventory.baseRanges, cp) || fontMayIgnore(inventory.behaviouralRanges, cp)) continue;
      const index = inventory.fonts.findIndex(font => eligible(font) && contains(font.ranges, cp));
      if (index >= 0) { if (!native) selected.add(index); }
      else missing.add(cp);
    }
  }
  const priority = new Set(preferred.values());
  return { fonts: [...selected].sort((a, b) => Number(priority.has(b)) - Number(priority.has(a)) || a - b).map(i => inventory.fonts[i]),
    missing: [...missing], emojiFallbacks:[...emojiFallbacks] };
}

export function createFontLoader(fontSet, Face, inventory = manifest) {
  const pending = new Map();
  return async function load(texts) {
    const selection = requiredFonts(texts, inventory);
    await Promise.all(selection.fonts.flatMap(font => [font,...(font.companions ?? [])]).map(font => {
      if (!pending.has(font.family)) {
        const url = new URL('../' + font.file, import.meta.url);
        url.searchParams.set('v', font.sha256.slice(0, 10));
        const promise = new Face(font.family, `url("${url.href}")`).load().then(face => {
          fontSet.add(face);
        }).catch(error => {
          pending.delete(font.family); // A transient failure can be retried.
          throw error;
        });
        pending.set(font.family, promise);
      }
      return pending.get(font.family);
    }));
    return { families: selection.fonts.map(font => font.family), missing: selection.missing, emojiFallbacks:selection.emojiFallbacks };
  };
}

let browserLoader;
export function loadTextFonts(texts) {
  browserLoader ??= createFontLoader(document.fonts, FontFace);
  return browserLoader(texts);
}
