// Text layout for comic panels: flows text line by line into whatever space
// the artwork leaves free. Everything here is pure so it can be tested
// without a browser; measuring text is delegated to the caller.

// A panel is a cell of a fixed width and height with the art scaled to the
// cell width and anchored to the bottom. Everything above the art is free.
//
// spec.free[row] is a list of [start, end) intervals, in art pixels, where
// text may go on that row of the art.
export function makePanel(spec, cellWidth, cellHeight, padding) {
  const scale = cellWidth / spec.width;
  const artHeight = spec.height * scale;
  return {
    spec,
    width: cellWidth,
    height: cellHeight,
    padding,
    scale,
    artTop: cellHeight - artHeight,
  };
}

function intersect(a, b) {
  const out = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    const start = Math.max(a[i][0], b[j][0]);
    const end = Math.min(a[i][1], b[j][1]);
    if (start < end) out.push([start, end]);
    if (a[i][1] < b[j][1]) i++;
    else j++;
  }
  return out;
}

// The horizontal intervals where a line occupying y0..y1 may go, keeping
// `margin` clear of the art on every side and `padding` clear of the panel
// edges.
export function freeIntervals(panel, y0, y1, margin) {
  const { padding, width, scale, artTop, spec } = panel;
  let intervals = [[padding, width - padding]];
  const top = y0 - margin;
  const bottom = y1 + margin;
  if (bottom > artTop) {
    const firstRow = Math.max(0, Math.floor((top - artTop) / scale));
    const lastRow = Math.min(
      spec.height - 1,
      Math.ceil((bottom - artTop) / scale) - 1,
    );
    for (let row = firstRow; row <= lastRow && intervals.length; row++) {
      const free = (spec.free[row] || []).map(([a, b]) => [
        a * scale,
        b * scale,
      ]);
      intervals = intersect(intervals, free);
    }
  }
  return intervals
    .map(([a, b]) => [Math.max(a + margin, padding), Math.min(b - margin, width - padding)])
    .filter(([a, b]) => b > a);
}

function widest(intervals) {
  let best = null;
  for (const interval of intervals) {
    if (!best || interval[1] - interval[0] > best[1] - best[0]) best = interval;
  }
  return best;
}

function paragraphs(text) {
  return text
    .trim()
    .split("\n")
    .map((line) => line.split(/\s+/).filter(Boolean));
}

// Split a word that is too long for any line into pieces that fit `width`.
function breakWord(word, width, fits) {
  const pieces = [];
  let rest = word;
  while (rest.length) {
    let n = 1;
    while (n < rest.length && fits(rest.slice(0, n + 1), width)) n++;
    pieces.push(rest.slice(0, n));
    rest = rest.slice(n);
  }
  return pieces;
}

// Lay `text` out in `panel` from the top down. Returns the positioned lines,
// whether everything fitted, and the line height used.
//
// options: measure(text, fontSize), fontSize, lineHeight (a multiple of the
// font size), margin (clearance from the art), align ("left" | "center"),
// minLineWidth (narrower gaps are skipped; defaults to 3 em), startY (where
// the first line goes; defaults to the top padding).
export function layoutText(panel, text, options) {
  const { measure, fontSize, align = "center" } = options;
  const lineHeight = fontSize * (options.lineHeight ?? 1.2);
  const margin = options.margin ?? 0;
  const minLineWidth = options.minLineWidth ?? fontSize * 3;
  const step = lineHeight / 4;
  const limit = panel.height - panel.padding;
  const fullWidth = panel.width - 2 * panel.padding;
  const fits = (s, width) => measure(s, fontSize) <= width;

  const lines = [];
  let y = options.startY ?? panel.padding;
  let overflow = false;

  const result = () => ({ lines, fits: !overflow, lineHeight, fontSize });

  const place = (words, interval) => {
    const content = words.join(" ");
    const width = measure(content, fontSize);
    const x =
      align === "center"
        ? interval[0] + (interval[1] - interval[0] - width) / 2
        : interval[0];
    lines.push({ text: content, x, y, width, height: lineHeight });
    y += lineHeight;
  };

  for (const paragraph of paragraphs(text)) {
    if (paragraph.length === 0) {
      y += lineHeight;
      continue;
    }
    const words = [...paragraph];
    while (words.length) {
      if (y + lineHeight > limit) {
        overflow = true;
        return result();
      }
      const interval = widest(freeIntervals(panel, y, y + lineHeight, margin));
      const width = interval ? interval[1] - interval[0] : 0;
      if (!interval || width < Math.min(minLineWidth, fullWidth)) {
        y += step;
        continue;
      }
      if (!fits(words[0], width)) {
        if (fits(words[0], fullWidth)) {
          // There may be a wider gap further down.
          y += step;
          continue;
        }
        words.splice(0, 1, ...breakWord(words[0], width, fits));
      }
      const line = [words.shift()];
      while (words.length && fits([...line, words[0]].join(" "), width)) {
        line.push(words.shift());
      }
      place(line, interval);
    }
  }
  return result();
}

// Lay out one text per panel spec, sharing a cell size and font size.
//
// mode "grow": keep the font size and make the cells as short as possible
// while still fitting every text (but never shorter than the art plus
// `headroom`).
// mode "shrink": keep the cells at the art height plus `headroom` and use the
// largest font size (up to the requested one) that fits every text.
//
// valign: "top" puts text at the top of each panel, "bottom" moves it as far
// down as it can go while still fitting, "middle" halfway between the two.
export function fitPanels(specs, texts, options) {
  const best = fitTop(specs, texts, options);
  const valign = options.valign ?? "top";
  if (valign === "top" || !best.fits) return best;
  const share = valign === "middle" ? 0.5 : 1;
  best.layouts = best.layouts.map((layout, i) => {
    if (!layout.lines.length) return layout;
    const panel = best.panels[i];
    const at = (offset) =>
      layoutText(panel, texts[i], {
        ...options,
        fontSize: best.fontSize,
        startY: panel.padding + offset,
      });
    let lo = 0;
    let hi = panel.height;
    while (hi - lo > 0.5) {
      const mid = (lo + hi) / 2;
      if (at(mid).fits) lo = mid;
      else hi = mid;
    }
    return at(lo * share);
  });
  return best;
}

function fitTop(specs, texts, options) {
  const { cellWidth, padding = 0, mode = "grow", headroom = 0 } = options;
  const artHeight = Math.max(
    ...specs.map((spec) => spec.height * (cellWidth / spec.width)),
  );

  const attempt = (cellHeight, fontSize) => {
    const panels = specs.map((spec) =>
      makePanel(spec, cellWidth, cellHeight, padding),
    );
    const layouts = panels.map((panel, i) =>
      layoutText(panel, texts[i] ?? "", { ...options, fontSize }),
    );
    return {
      cellHeight,
      fontSize,
      panels,
      layouts,
      fits: layouts.every((layout) => layout.fits),
    };
  };

  if (mode === "shrink") {
    const cellHeight = artHeight + headroom;
    let best = attempt(cellHeight, options.fontSize);
    if (best.fits) return best;
    let lo = options.minFontSize ?? 4;
    let hi = options.fontSize;
    best = attempt(cellHeight, lo);
    if (!best.fits) return best;
    while (hi - lo > 0.25) {
      const mid = (lo + hi) / 2;
      const candidate = attempt(cellHeight, mid);
      if (candidate.fits) {
        lo = mid;
        best = candidate;
      } else {
        hi = mid;
      }
    }
    return best;
  }

  const fontSize = options.fontSize;
  const step = options.step ?? fontSize / 2;
  const base = artHeight + headroom;
  let best = attempt(base, fontSize);
  if (best.fits) return best;

  // Double the extra height until it fits, then binary search back down.
  const maxExtra = options.maxExtra ?? artHeight * 50;
  let lo = 0;
  let hi = step;
  for (;;) {
    const candidate = attempt(base + hi, fontSize);
    if (candidate.fits) {
      best = candidate;
      break;
    }
    if (hi >= maxExtra) return candidate;
    lo = hi;
    hi *= 2;
  }
  while (hi - lo > step) {
    const mid = lo + Math.ceil((hi - lo) / 2 / step) * step;
    if (mid >= hi) break;
    const candidate = attempt(base + mid, fontSize);
    if (candidate.fits) {
      hi = mid;
      best = candidate;
    } else {
      lo = mid;
    }
  }
  return best;
}

// A short speech tail from the edge of the text towards the speaker's mouth,
// or null if there is no text. Returns {from, to} in cell coordinates.
export function tailFor(layout, mouth, { gap, maxLength }) {
  if (!layout.lines.length) return null;
  const [mx, my] = mouth;
  let best = null;
  for (const line of layout.lines) {
    const px = Math.min(Math.max(mx, line.x), line.x + line.width);
    const py = Math.min(Math.max(my, line.y), line.y + line.height);
    const distance = Math.hypot(mx - px, my - py);
    if (!best || distance < best.distance) best = { px, py, distance };
  }
  const { px, py, distance } = best;
  if (distance <= 2 * gap) return null;
  const dx = (mx - px) / distance;
  const dy = (my - py) / distance;
  const length = Math.min(maxLength, (distance - 2 * gap) * 0.6);
  const from = [px + dx * gap, py + dy * gap];
  return { from, to: [from[0] + dx * length, from[1] + dy * length] };
}
