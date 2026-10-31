// Text layout for comic panels: flows text line by line into whatever space
// the artwork leaves free. Everything here is pure so it can be tested
// without a browser; measuring text is delegated to the caller.

// A panel is a cell of a fixed width and height with the art scaled to the
// cell width and anchored to the bottom. Everything above the art is free.
//
// spec.free[row] is a list of [start, end) intervals, in art pixels, where
// text may go on that row of the art. spec.reserved is a list of
// [x0, y0, x1, y1] rectangles, in art pixels (y may be negative, above the
// art), taken up by something else, such as another character's balloon.
// spec.margin, if given, is how far its text keeps from the art, in place
// of the layout's default.
//
// padding keeps text away from the panel's edges: a number, or {x, y} to
// pad the sides and the top and bottom differently.
export function makePanel(spec, cellWidth, cellHeight, padding) {
  const scale = cellWidth / spec.width;
  const artHeight = spec.height * scale;
  return {
    spec,
    width: cellWidth,
    height: cellHeight,
    padX: padding?.x ?? padding,
    padY: padding?.y ?? padding,
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

function subtract(intervals, [x0, x1]) {
  return intervals.flatMap(([a, b]) => {
    if (x1 <= a || x0 >= b) return [[a, b]];
    const out = [];
    if (x0 > a) out.push([a, x0]);
    if (x1 < b) out.push([x1, b]);
    return out;
  });
}

// The reserved rectangles of a panel in cell coordinates.
export function reservedAreas(panel) {
  const { scale, artTop, spec } = panel;
  return (spec.reserved ?? []).map(([x0, y0, x1, y1]) => [
    x0 * scale,
    artTop + y0 * scale,
    x1 * scale,
    artTop + y1 * scale,
  ]);
}

// The horizontal intervals where a line occupying y0..y1 may go, keeping
// `margin` clear of the art and reserved areas on every side and `padding`
// clear of the panel edges.
export function freeIntervals(panel, y0, y1, margin) {
  const { padX, width, scale, artTop, spec } = panel;
  let intervals = [[padX, width - padX]];
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
  intervals = intervals.map(([a, b]) => [a + margin, b - margin]);
  for (const [rx0, ry0, rx1, ry1] of reservedAreas(panel)) {
    if (ry1 + margin > y0 && ry0 - margin < y1) {
      intervals = subtract(intervals, [rx0 - margin, rx1 + margin]);
    }
  }
  return intervals
    .map(([a, b]) => [Math.max(a, padX), Math.min(b, width - padX)])
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

// The longest start of a word too long for a line that fits in `width`:
// preferably ending just after punctuation (as in a web address), otherwise
// wherever it has to.
function firstPiece(word, width, fits) {
  let n = 1;
  while (n < word.length && fits(word.slice(0, n + 1), width)) n++;
  for (let k = n; k > 1; k--) {
    if ("/.-_?&=,:".includes(word[k - 1])) return word.slice(0, k);
  }
  return word.slice(0, n);
}

// Lay `text` out in `panel` from the top down. Returns the positioned lines,
// whether everything fitted, and the line height used.
//
// options: measure(text, fontSize), fontSize, lineHeight (a multiple of the
// font size), margin (clearance from the art), align ("left" | "center"),
// minLineWidth (narrower gaps are skipped; defaults to 3 em).
//
// Left-aligned text keeps a straight left edge, as Watterson's does, unless
// the art pushes some lines well aside: neighbouring lines all start where
// the furthest right of them has to, so long as that leaves each of them at
// least ALIGN_SHARE of the widest one's space.
export function layoutText(panel, text, options) {
  if (options.align !== "left") return flow(panel, text, options, []);
  let minimums = [];
  let result = flow(panel, text, options, minimums);
  for (let round = 0; round < 12; round++) {
    const next = alignedMinimums(result.spaces);
    if (next.every((m, i) => m === minimums[i]) && next.length === minimums.length) {
      break;
    }
    minimums = next;
    result = flow(panel, text, options, minimums);
  }
  return result;
}

const ALIGN_SHARE = 0.5;

// The left edge for each line: the furthest right start among a run of
// neighbouring lines' spaces ([start, end]), where starting them all there
// still leaves each enough room.
function alignedMinimums(spaces) {
  const out = [];
  let group = [];
  const edge = (g) => Math.max(...g.map(([a]) => a));
  const roomy = (g) => {
    const shortest = Math.min(...g.map(([, b]) => b)) - edge(g);
    const widest = Math.max(...g.map(([a, b]) => b - a));
    return shortest >= ALIGN_SHARE * widest;
  };
  const finish = () => {
    for (let k = 0; k < group.length; k++) out.push(edge(group));
    group = [];
  };
  for (const space of spaces) {
    if (group.length && !roomy([...group, space])) finish();
    group.push(space);
  }
  if (group.length) finish();
  return out;
}

function flow(panel, text, options, minimums) {
  const { measure, fontSize, align = "center" } = options;
  const lineHeight = fontSize * (options.lineHeight ?? 1.2);
  const margin = options.margin ?? 0;
  const minLineWidth = options.minLineWidth ?? fontSize * 3;
  const step = lineHeight / 4;
  const limit = panel.height - panel.padY;
  const fullWidth = panel.width - 2 * panel.padX;
  const fits = (s, width) => measure(s, fontSize) <= width;

  const lines = [];
  // The space each line had, before any alignment.
  const spaces = [];
  let y = panel.padY;
  let overflow = false;

  const result = () => ({ lines, spaces, fits: !overflow, lineHeight, fontSize });

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
      const space = widest(freeIntervals(panel, y, y + lineHeight, margin));
      // Lines beyond those seen last time go with the last group.
      const minimum = minimums.length
        ? minimums[Math.min(lines.length, minimums.length - 1)]
        : -Infinity;
      const interval = space && [Math.max(space[0], minimum), space[1]];
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
        // Too long for any line: the first piece gets a line to itself.
        const piece = firstPiece(words[0], width, fits);
        words[0] = words[0].slice(piece.length);
        spaces.push(space);
        place([piece], interval);
        continue;
      }
      const line = [words.shift()];
      while (words.length && fits([...line, words[0]].join(" "), width)) {
        line.push(words.shift());
      }
      spaces.push(space);
      place(line, interval);
    }
  }
  return result();
}

// Lay text out in a column of the given width, each line centred, from
// y = 0 down. Returns the lines and the total height.
export function layoutColumn(text, { measure, fontSize, lineHeight = 1.2, width }) {
  const spec = { width, height: 1, free: [] };
  const panel = makePanel(spec, width, Infinity, 0);
  const layout = layoutText(panel, text, {
    measure,
    fontSize,
    lineHeight,
    align: "center",
    minLineWidth: 0,
  });
  const lines = layout.lines;
  const height = lines.length ? lines[lines.length - 1].y + layout.lineHeight : 0;
  return { lines, height, lineHeight: layout.lineHeight, fontSize };
}

// Lay out one text per panel spec, sharing a cell size, with the cells as
// short as possible while still fitting every text and every reserved area
// (but never shorter than the art).
export function fitPanels(specs, texts, options) {
  const { cellWidth, padding = 0, fontSize } = options;
  const artHeight = Math.max(
    ...specs.map((spec) => spec.height * (cellWidth / spec.width)),
  );

  const attempt = (cellHeight) => {
    const panels = specs.map((spec) =>
      makePanel(spec, cellWidth, cellHeight, padding),
    );
    const layouts = panels.map((panel, i) =>
      layoutText(panel, texts[i] ?? "", {
        ...options,
        margin: panel.spec.margin ?? options.margin,
      }),
    );
    const inside = panels.every((panel) =>
      reservedAreas(panel).every(([, y0]) => y0 >= 0),
    );
    return {
      cellHeight,
      fontSize,
      panels,
      layouts,
      fits: inside && layouts.every((layout) => layout.fits),
    };
  };

  const step = options.step ?? fontSize / 2;
  let best = attempt(artHeight);
  if (best.fits) return best;

  // Double the extra height until it fits, then binary search back down.
  const maxExtra = options.maxExtra ?? artHeight * 50;
  let lo = 0;
  let hi = step;
  for (;;) {
    const candidate = attempt(artHeight + hi);
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
    const candidate = attempt(artHeight + mid);
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
