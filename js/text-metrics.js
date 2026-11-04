import { egyptianInk } from './egyptian-layout.js';
import { nativeShapingText } from "./native-shaping.js";
import { paragraphDirection, bidiParagraph } from "./direction.js";
import { graphemes } from "./unicode.js";
import { measureGrid } from "./grid.js";
import { needsEmojiRouting, routeDirectionalRun, splitEmojiRuns } from "./emoji-routing.js";
import { hasVietnameseMarks, splitVietnameseMarks } from "./vietnamese-marks.js";
import { hasCombiningAnnotations, combiningInk } from './combining-annotations.js';
import { hasMixedHieroglyphs, hieroglyphStroke, splitHieroglyphRuns, reserveEgyptianStroke } from './hieroglyph-optics.js';
import { hasScriptOptics, scriptStroke, splitScriptRuns } from './script-optics.js';

// A quadrat compresses several detailed signs into one em. At dialogue size
// that makes each sign much smaller than adjacent ungrouped hieroglyphs.
// Enlarge pure Egyptian composed runs optically, preserving their arrangement.
export function textScale(text) {
  text=text.replace(/[\u202a-\u202e\u2066-\u2069]/gu,'');
  return /[\u{13430}-\u{1343f}]/u.test(text)
    && /^[\s\u{13000}-\u{143ff}\ufe00-\ufe06]+$/u.test(text) ? 2 : 1;
}

// Canvas advance widths omit ink outside the advance box. Reserve both, so
// accents, overlaid marks, and italic overhang cannot escape the text box.
export function createTextMeasurer(ctx, fontString) {
  const cache = new Map();
  const envelopes = new Map();
  const rawInk = (text, size, direction = paragraphDirection(text), policy = "text", nativeOnly = false, family) => {
    const key = `${size}\u0000${direction}\u0000${policy}\u0000${nativeOnly}\u0000${family ?? ''}\u0000${text}`;
    if (cache.has(key)) return cache.get(key);
    // Detailed ink drawings need more room than a capital letter to read at
    // dialogue size. Measure at the same larger size used for painting so
    // wrapping, balloon geometry and exports reserve the actual ink.
    const actualSize = size * (policy === 'custom' ? 1.4 : nativeOnly ? 1 : textScale(text));
    if (!nativeOnly) {
      const arranged=egyptianInk(text,actualSize,(t,s,p,d='ltr')=>rawInk(t,s,d,p,true),direction);
      if (arranged) {
        const optical=reserveEgyptianStroke(arranged,actualSize);
        cache.set(key,optical);return optical;
      }
    }
    ctx.font = fontString(actualSize,policy,family);
    ctx.textAlign = "left";
    ctx.direction = direction;
    ctx.textBaseline = "alphabetic";
    const font = ctx.font;
    const metrics = ctx.measureText(nativeShapingText(text));
    const finite = (value, fallback) => Number.isFinite(value) ? value : fallback;
    const advance = finite(metrics.width, 0);
    const strokeWidth = policy === "custom" ? actualSize * 0.018
      : Math.max(hieroglyphStroke(text,actualSize),scriptStroke(text,actualSize));
    const spread = strokeWidth / 2;
    const left = Math.max(0, finite(metrics.actualBoundingBoxLeft, 0) + spread);
    const right = Math.max(advance, finite(metrics.actualBoundingBoxRight, advance) + spread);
    const inkAscent = finite(metrics.actualBoundingBoxAscent, size * 0.7);
    const inkDescent = finite(metrics.actualBoundingBoxDescent, 0);
    // Emoji drawings have different internal baselines. Align their actual
    // ink centres with the lettering, rather than aligning font origins.
    let baselineOffset = 0;
    if (policy === "custom" && text.trim()) {
      const cap = rawInk("H", size, direction, "text", true);
      baselineOffset = (inkAscent - inkDescent - cap.ascent + cap.descent) / 2;
    }
    const result = {
      font,
      strokeWidth,
      fontSize: actualSize,
      width: left + right,
      advance,
      drawOffset: left,
      baselineOffset,
      ascent: Math.max(0, inkAscent + spread - baselineOffset),
      descent: Math.max(0, inkDescent + spread + baselineOffset),
    };
    cache.set(key, result);
    return result;
  };
  const composed = new Map();
  const compose = (runs, size, annotations=true) => {
    let advance = 0, left = 0, right = 0, ascent = 0, descent = 0;
    const routed=runs.flatMap(run=>{
      const arranged=annotations&&combiningInk(run.drawText??run.text,size,(body,s,d)=>{
        const override=run.drawText!==run.text;
        return compose([{text:body,drawText:override?(d==='rtl'?'\u202e':'\u202d')+body+'\u202c':body,direction:d}],s,false);
      },run.direction);
      if(arranged)return [{...run,emojiPolicy:'text',annotationMetrics:arranged}];
      return routeDirectionalRun(run).flatMap(splitEmojiRuns).flatMap(splitVietnameseMarks).flatMap(splitHieroglyphRuns).flatMap(splitScriptRuns);
    });
    const positioned = routed.map(run => {
      const metrics = run.annotationMetrics??rawInk(run.drawText,size,run.direction,run.emojiPolicy,false,run.fontFamily);
      const {annotationMetrics,...span}=run;
      const result = {...span,font:metrics.font??fontString(size,run.emojiPolicy,run.fontFamily),fontSize:metrics.fontSize,strokeWidth:metrics.strokeWidth,baselineOffset:metrics.baselineOffset??0,glyphs:metrics.glyphs,offset:advance};
      left = Math.max(left,metrics.drawOffset-advance);
      right = Math.max(right,advance+metrics.width-metrics.drawOffset);
      ascent = Math.max(ascent,metrics.ascent);
      descent = Math.max(descent,metrics.descent);
      advance += metrics.advance;
      return result;
    });
    return {fontSize:size,width:left+Math.max(advance,right),advance,drawOffset:left,
      ascent,descent,runs:positioned};
  };
  const ink = (text,size,direction=paragraphDirection(text)) => {
    if (!needsEmojiRouting(text) && !hasVietnameseMarks(text) && !hasCombiningAnnotations(text) && !hasMixedHieroglyphs(text) && !hasScriptOptics(text)) return rawInk(text,size,direction);
    const key = `${size}\u0000${direction}\u0000${text}`;
    if (!composed.has(key)) {
      const runs = bidiParagraph(text,direction).runs(0,text)
        ?? [{text,drawText:text,direction}];
      composed.set(key,compose(runs,size));
    }
    return composed.get(key);
  };
  const measure = (text, size) => ink(text, size).width;
  measure.ink = ink;
  const grids = new Map();
  measure.grid = (text, size) => {
    const key = `${size}\u0000${text}`;
    if (!grids.has(key)) grids.set(key, measureGrid(text,size,measure));
    return grids.get(key);
  };
  const directed = new Map();
  measure.forDirection = direction => {
    if (!directed.has(direction)) {
      const fn = (text, size) => ink(text, size, direction).width;
      fn.ink = (text, size) => ink(text, size, direction);
      directed.set(direction, fn);
    }
    return directed.get(direction);
  };
  measure.forParagraph = text => {
    const paragraph = bidiParagraph(text);
    const slices = new Map();
    return {
      at(start) {
        if (slices.has(start)) return slices.get(start);
        const boxes = new Map();
        const box = (content, size) => {
          const key = `${size}\u0000${content}`;
          if (boxes.has(key)) return boxes.get(key);
          const runs = paragraph.runs(start, content);
          if (!runs) return ink(content, size, paragraph.direction);
          const result = compose(runs,size);
          boxes.set(key, result);
          return result;
        };
        const fn = (content, size) => box(content, size).width;
        fn.ink = box;
        slices.set(start, fn);
        return fn;
      },
    };
  };
  // Keep one baseline/line-height per speech so balancing and moving text
  // cannot move tall marks into a shorter line slot. Include whole runs and
  // individual clusters: the latter cover forms exposed by emergency wraps.
  measure.envelope = (text, size, lineHeight = 1.2) => {
    const key = `${size}\u0000${lineHeight}\u0000${text}`;
    if (envelopes.has(key)) return envelopes.get(key);
    const cap = ink("H", size).ascent;
    let ascent = cap, descent = 0;
    for (const sample of new Set([...text.split(/\r\n|[\n\r\u2028\u2029]/), ...graphemes(text)])) {
      // Whitespace carries no painted height. Some font/browser combinations
      // return fallback ascent/descent for an empty string or a space.
      if (!sample.trim()) continue;
      const box = ink(sample, size);
      ascent = Math.max(ascent, box.ascent);
      descent = Math.max(descent, box.descent);
    }
    const height = Math.max(size * lineHeight,
      ascent + descent + size * Math.max(0, lineHeight - 1));
    const result = { height, baseline: (height + ascent - descent) / 2,
      blankHeight: size * lineHeight };
    envelopes.set(key, result);
    return result;
  };
  return measure;
}
