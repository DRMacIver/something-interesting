// A small optical ink expansion, independent of emoji sizing and colour.
// Split native fields before applying it so adjacent dialogue keeps Dad's ink.
const field = /([\u{13000}-\u{143ff}\ufe00-\ufe06]+|[\u{14400}-\u{1467f}\ufe00-\ufe06]+)/u;
const sign = /[\u{13000}-\u{1342f}\u{13460}-\u{1467f}]/u;
export const hasHieroglyphs = text => sign.test(text);
export const hasMixedHieroglyphs = text => hasHieroglyphs(text)
  && (/[^\s\u202a-\u202e\u2066-\u2069\u{13000}-\u{1467f}\ufe00-\ufe06]/u.test(text)
    || /[\u{13000}-\u{143ff}]/u.test(text) && /[\u{14400}-\u{1467f}]/u.test(text));
export const hieroglyphStroke = (text, size) => {
  if (!sign.test(text) || !/^[\s\u202a-\u202e\u2066-\u2069\u{13000}-\u{1467f}\ufe00-\ufe06]+$/u.test(text)) return 0;
  // Anatolian signs have finer internal channels: use a smaller expansion.
  return size * (/[\u{14400}-\u{1467f}]/u.test(text) ? 0.010 : 0.014);
};

export function splitHieroglyphRuns(run) {
  if (!hasHieroglyphs(run.text)) return [run];
  // Preserve explicit bidi overrides on each native fragment.
  const overridden = run.drawText !== run.text;
  return run.text.split(field).filter(Boolean).map(text => ({...run,text,
    drawText: overridden ? (run.direction === 'rtl' ? '\u202e' : '\u202d') + text + '\u202c' : text}));
}

export function reserveEgyptianStroke(ink, size) {
  // Native insertion/enclosure paths use source units. Their stroke scales
  // with exactly the same transform as their source outline. Fine components
  // receive less expansion than full-size signs.
  const glyphs = ink.glyphs.map(g => g.primitive === 'outline'
    ? {...g, strokeWidth: Math.min(size * 0.014 / g.scale,
      Math.min(g.width / (g.stretchX ?? 1), g.height) * 0.025)} : g);
  const spread = Math.max(0, ...glyphs.map(g => (g.strokeWidth ?? 0) * g.scale * Math.max(1, g.stretchX ?? 1) / 2));
  return {...ink,glyphs,width:ink.width+2*spread,drawOffset:ink.drawOffset+spread,
    ascent:ink.ascent+spread,descent:ink.descent+spread};
}
