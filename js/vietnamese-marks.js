// Generic side forms have spacing advances and need no cross-font anchor.
// Browser cluster fallback still requires a single font for base + mark; split
// only their drawing spans. Logical graphemes and wrapping remain unchanged.
export const hasVietnameseMarks = text => /[\u{16ff0}\u{16ff1}]/u.test(text);

export function splitVietnameseMarks(run) {
  if (run.emojiPolicy !== 'text' || !hasVietnameseMarks(run.text)) return [run];
  const parts = run.text.split(/([\u{16ff0}\u{16ff1}])/u).filter(Boolean);
  if (run.direction === 'rtl') parts.reverse();
  const override = run.drawText !== run.text;
  return parts.map(text => ({...run,text,
    drawText: override ? (run.direction === 'rtl' ? '\u202e' : '\u202d')+text+'\u202c' : text}));
}
