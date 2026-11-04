import emoji from './emoji-manifest.js';
import egyptianVariants from './egyptian-variant-manifest.js';
const rotations = new Set(egyptianVariants.variationSequences);
const rotationBases = new Set(egyptianVariants.ranges.map(([cp])=>String.fromCodePoint(cp)));
const hasRotation = text => /[\u{13000}-\u{143ff}][\ufe00-\ufe06]/u.test(text);
import { emojiPresentation, emojiVariationBases } from './unicode-data.js';
import { graphemes } from './unicode.js';
import { lookup } from './vendor/linebreak/LineBreak.js';
import { hasVariationSelectors, nativeVariationFont, nativeSpacingVariationPlan, hasJoiningCharacters } from './font-variations.js';
import { standaloneFontSpans } from './standalone-fonts.js';
import { formatFontSpans, hasFormatSigns } from './format-fonts.js';

const supported = new Set(emoji.sequences);
const opticsFor = text => emoji.customOptics?.[text.replace(/[\u202a-\u202e\u2066-\u2069]/gu,'')];
export function emojiStrokeRatio(text) {
  return opticsFor(text)?.strokeRatio ?? .018;
}
export const emojiScaleFactor = text => opticsFor(text)?.scale ?? 1.4;
const spacedTone = /^([\p{Zs}])([\u{1f3fb}-\u{1f3ff}])$/u;

// GB9 groups a modifier with a preceding space. A space is not a skin-tone
// base: keep its advance and route the registered standalone swatch separately.
// Other modifier/ZWJ clusters retain exact whole-grapheme routing.
export function routingClusters(text) {
  return graphemes(text).flatMap(cluster=>{
    const match=spacedTone.exec(cluster);
    return match && supported.has(match[2]) ? [match[1],match[2]] : [cluster];
  });
}
const textVariants = new Set(emojiVariationBases);
const escape = cp => `\\u{${cp.toString(16)}}`;
const routing = new RegExp(`[${emojiPresentation.map(([a,b]) => escape(a)+(a===b?'':'-'+escape(b))).join('')}${emoji.ranges.filter(([a])=>!emoji.componentOnly.includes(a)).map(([a])=>escape(a)).join('')}\\ufe0f\\u20e3]`,'u');
// Also dispatch registered standalone Egyptian variants to their own font.
export const needsEmojiRouting = text => routing.test(text) || hasRotation(text) || hasVariationSelectors(text) || text.includes('\u0640') || hasFormatSigns(text);

// Exact whole-grapheme matches only. A known component does not authorize
// overriding any part of a skin-tone, ZWJ, tag, flag or keycap sequence.
export function emojiPolicy(cluster) {
  if (supported.has(cluster)) return 'custom';
  const chars = Array.from(cluster);
  if (chars[1] === '\ufe0e' && textVariants.has(chars[0].codePointAt(0))) return 'text';
  // Valid keycap emoji were handled by the exact sequence set above. An
  // enclosing keycap alone, on whitespace or on another text base is text.
  if (cluster.includes('\ufe0f')
    || Array.from(cluster).some(c => lookup(emojiPresentation,c.codePointAt(0),false))) return 'native';
  return 'text';
}

export function fontRuns(text) {
  if (!needsEmojiRouting(text)) return [{text,emojiPolicy:'text'}];
  const result = [];
  const append=part=>{
    const last=result.at(-1);
    if(last?.emojiPolicy===part.emojiPolicy&&last.fontFamily===part.fontFamily)last.text+=part.text;
    else result.push(part);
  };
  // Do not split native quadrat shaping to insert a standalone rotation.
  // The shared Egyptian layout path measures and paints these complete groups.
  const composedEgyptian = /[\u{13430}-\u{13455}]/u.test(text);
  const compareRotations = hasRotation(text);
  const standalone=[...formatFontSpans(text),...standaloneFontSpans(text)];let offset=0;
  for (const cluster of routingClusters(text)) {
    const policy = !composedEgyptian && (rotations.has(cluster) || (compareRotations && rotationBases.has(cluster))) ? 'egyptian-variant' : emojiPolicy(cluster);
    // Joining scripts use the whole-repertoire font chosen by requiredFonts.
    // Splitting one UVS cluster from its neighbours would sever native joins.
    const joining = hasJoiningCharacters(cluster);
    const explicit=standalone.find(span=>span.start<=offset&&span.end>offset)?.font.family;
    const spacing=policy==='text'&&!composedEgyptian?nativeSpacingVariationPlan(cluster):undefined;
    if(!explicit&&spacing?.tail){
      append({text:spacing.body,emojiPolicy:'text',fontFamily:spacing.font.family});
      append({text:spacing.tail,emojiPolicy:'text'});
      offset+=cluster.length;continue;
    }
    const family = explicit??spacing?.font.family??(policy === 'text' && !joining && !composedEgyptian
      ? nativeVariationFont(cluster)?.family : undefined);
    append({text:cluster,emojiPolicy:policy,...(family ? {fontFamily:family} : {})});
    offset+=cluster.length;
  }
  return result;
}

// Input runs are in visual order, with logical text inside each run. Splitting
// a right-to-left run into font spans also reverses the order of those spans.
export function routeDirectionalRun(run) {
  const parts = fontRuns(run.text);
  if (run.direction === 'rtl') parts.reverse();
  const override = run.drawText !== run.text;
  return parts.map(part => ({...part,direction:run.direction,
    drawText:override ? (run.direction==='rtl'?'\u202e':'\u202d')+part.text+'\u202c' : part.text}));
}

// Each drawing has its own optical centre. Keep ZWJ, flag and modifier
// sequences whole while allowing adjacent emoji to sit at different offsets.
export function splitEmojiRuns(run) {
  if (run.emojiPolicy !== 'custom') return [run];
  const parts = routingClusters(run.text);
  if (run.direction === 'rtl') parts.reverse();
  const override = run.drawText !== run.text;
  return parts.map(text => ({...run,text,
    drawText:override ? (run.direction==='rtl'?'\u202e':'\u202d')+text+'\u202c' : text}));
}
