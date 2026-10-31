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
// spec.margin, spec.awayFromArt, spec.awayLimit, spec.block and
// spec.maxLineWidth, if given, override the layout options of the same
// names for that panel.
//
// padding keeps text away from the panel's edges: a number, or {x, y} to
// pad the sides and the top and bottom differently.
//
// The art is scaled to fill the cell's width, unless `scale` is given: a
// cell wider than its art at that scale has the rest of the art's free rows
// (art extended to the right, say) beside it.
export function makePanel(spec, cellWidth, cellHeight, padding, scale = cellWidth / spec.width) {
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
// `margin` clear of the art and reserved areas on every side, and the
// panel's padding clear of its edges.
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
  // Keep clear of the art, but not of the panel's own edges (padding does
  // that).
  intervals = intervals.map(([a, b]) => [
    a <= padX ? a : a + margin,
    b >= width - padX ? b : b - margin,
  ]);
  // Nor beside a reserved area on its right: that would be read after it.
  for (const [rx0, ry0, , ry1] of reservedAreas(panel)) {
    if (ry1 + margin > y0 && ry0 - margin < y1) {
      intervals = subtract(intervals, [rx0 - margin, Infinity]);
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
// minLineWidth (narrower gaps are skipped; defaults to 3 em), startY (where
// the first line goes; defaults to the top padding), awayFromArt and
// awayLimit (see moveAwayFromArt), drop, dropLimit and keepGap (see drop).
//
// Left-aligned text keeps a straight left edge, as Watterson's does, unless
// the art pushes some lines well aside: neighbouring lines all start where
// the furthest right of them has to, so long as that leaves each of them at
// least ALIGN_SHARE of the widest one's space.
//
// Line breaks are then chosen to even out the line lengths of each
// paragraph (see balance), and a last line left on its own beside the art,
// away from the rest of the text, counts as not fitting, as does text with
// options.block set that would squeeze into a narrower space partway down
// (see squeezed).
export function layoutText(panel, text, options) {
  let result;
  if (options.align !== "left") {
    result = flow(panel, text, options, []);
  } else {
    let minimums = [];
    result = flow(panel, text, options, minimums);
    for (let round = 0; round < 12; round++) {
      const next = alignedMinimums(result.spaces);
      if (next.every((m, i) => m === minimums[i]) && next.length === minimums.length) {
        break;
      }
      minimums = next;
      result = flow(panel, text, options, minimums);
    }
  }
  if (!result.fits) return result;
  balance(result, options);
  if (options.awayFromArt && options.align === "left") {
    moveAwayFromArt(result, panel, options.awayLimit ?? Infinity);
  }
  result = {
    ...result,
    fits: !stranded(result) && !(options.block && (squeezed(result) || gapped(result))),
  };
  if (options.drop && result.fits && result.lines.length) result = drop(panel, text, options, result);
  if (options.centreOn !== undefined && result.fits && result.lines.length) {
    centre(result, options.centreOn, options.centreSlack);
  }
  return result;
}

// A balloon sits in the middle of the room its lines have, as long as it
// still spans its speaker (at x = speakerX), or starts no more than `slack`
// past them, so that its tail can come down beside them; otherwise it
// keeps as near them as it can.
function centre({ lines }, speakerX, slack = 0) {
  const roomLeft = Math.max(...lines.map((l) => l.interval[0]));
  const roomRight = Math.min(...lines.map((l) => l.interval[1]));
  const left = Math.min(...lines.map((l) => l.x));
  const width = Math.max(...lines.map((l) => l.x + l.width)) - left;
  if (roomRight - roomLeft < width) return;
  let target = (roomLeft + roomRight - width) / 2;
  target = Math.min(Math.max(target, speakerX - width), speakerX + slack);
  target = Math.min(Math.max(target, roomLeft), roomRight - width);
  for (const line of lines) line.x += target - left;
}

// Text that has room to spare drops down towards whoever's speaking: as far
// as it can go without its lines changing (no re-wrapping round the art)
// and without its last line going below dropLimit, less keepGap; and
// without the art pushing any of its lines aside unless it pushes them all
// alike; and text whose balloon would float free of the panel's sides (see
// floatGap) only drops as far as it still would. Once there it stays
// beside them rather than moving away from the art.
function drop(panel, text, options, result) {
  const lines = result.lines.map((l) => l.text).join("\n");
  // Where each line starts relative to the first: the art may push them
  // aside together, but not one by one.
  const indents = (layout) => layout.lines.map((l) => l.x - layout.lines[0].x);
  const shape = indents(result);
  const limit = options.dropLimit ?? Infinity;
  // Whether the text, once centred, keeps floatGap clear of the panel's
  // sides (so its balloon floats free rather than hanging from one).
  const floats = (layout) => {
    if (options.floatGap === undefined) return true;
    const lines = layout.lines.map((l) => ({ ...l }));
    if (options.centreOn !== undefined) centre({ lines }, options.centreOn, options.centreSlack);
    const left = Math.min(...lines.map((l) => l.x));
    const right = Math.max(...lines.map((l) => l.x + l.width));
    return Math.min(left - panel.padX, panel.width - panel.padX - right) >= options.floatGap;
  };
  const floating = floats(result);
  const at = (offset) =>
    layoutText(panel, text, { ...options, drop: false, awayFromArt: false, startY: panel.padY + offset });
  const same = (layout) => {
    const last = layout.lines[layout.lines.length - 1];
    return (
      layout.fits &&
      layout.lines.map((l) => l.text).join("\n") === lines &&
      indents(layout).every((x, i) => Math.abs(x - shape[i]) < 1e-6) &&
      (!floating || floats(layout)) &&
      last.y + last.height <= limit + 1e-9
    );
  };
  let lo = 0;
  let hi = panel.height;
  while (hi - lo > 0.5) {
    const mid = (lo + hi) / 2;
    if (same(at(mid))) lo = mid;
    else hi = mid;
  }
  const offset = Math.max(0, lo - (options.keepGap ?? 0));
  return offset > 0 ? at(offset) : result;
}

// Watterson leaves room between a balloon and whoever it has had to make
// room for: when lines have been pushed aside by the art, move each run of
// them that share a left edge further away, as far as the tightest of them
// allows but no more than `limit`.
function moveAwayFromArt({ lines }, panel, limit) {
  let i = 0;
  while (i < lines.length) {
    let j = i;
    while (j + 1 < lines.length && Math.abs(lines[j + 1].x - lines[i].x) < 1e-6) j++;
    if (lines[i].x > panel.padX + 1e-6) {
      const run = lines.slice(i, j + 1);
      const room = Math.min(limit, ...run.map((l) => l.interval[1] - (l.x + l.width)));
      if (room > 0) for (const line of run) line.x += room;
    }
    i = j + 1;
  }
}

// Whether the last line is on its own, pushed well aside by the art from
// the line before it.
function stranded({ lines, spaces }) {
  const n = lines.length;
  if (n < 2) return false;
  const roomy = alignedMinimums([spaces[n - 2], spaces[n - 1]]);
  return roomy[0] !== roomy[1];
}

// Text lettered as one block, as in a balloon, has room of much the same
// width on every line: it doesn't narrow partway down to squeeze into a gap
// (beside someone else's balloon, say) with less than BLOCK_SHARE of the
// room of its widest line, and it has no gaps (see gapped).
const BLOCK_SHARE = 0.7;

// Whether lettering that should be one block has a gap in it partway
// down: a line pushed further down than the blank lines between paragraphs
// account for (by a long word looking for room below the art, say).
function gapped({ lines, lineHeight }) {
  for (let i = 1; i < lines.length; i++) {
    const skipped = Math.max(1, lines[i].paragraph - lines[i - 1].paragraph);
    if (lines[i].y - lines[i - 1].y > skipped * lineHeight + 1e-6) return true;
  }
  return false;
}

function squeezed({ lines }) {
  const rooms = lines.map(({ interval: [a, b] }) => b - a);
  return Math.min(...rooms) < BLOCK_SHARE * Math.max(...rooms);
}

// Re-break each paragraph's lines to even out their lengths, keeping the
// same line positions and spaces: Knuth-style, minimising the squared
// leftover space of every line but the last, with a penalty for ending on
// a lone short word. The last paragraph may use fewer lines than before.
function balance(result, { measure, fontSize, align = "center", maxLineWidth = Infinity }) {
  const { lines, spaces } = result;
  const groups = [];
  for (let i = 0; i < lines.length; i++) {
    const last = groups[groups.length - 1];
    if (last && lines[last[0]].paragraph === lines[i].paragraph) last.push(i);
    else groups.push([i]);
  }
  // Pieces of broken words, and words too long for a line, stay on their
  // own lines; the runs of lines between them are balanced separately.
  const runs = [];
  groups.forEach((group, g) => {
    let run = [];
    const finish = (endsParagraph) => {
      if (run.length) runs.push({ run, endsParagraph, final: endsParagraph && g === groups.length - 1 });
      run = [];
    };
    for (const i of group) {
      if (lines[i].piece) {
        finish(false);
        runs.push({ run: [i], fixed: true });
      } else {
        run.push(i);
      }
    }
    finish(true);
  });
  const keep = [];
  const keepSpaces = [];
  for (const { run: group, fixed, endsParagraph, final } of runs) {
    const slots = group.map((i) => lines[i]);
    const words = slots.flatMap((l) => l.text.split(" "));
    if (fixed || slots.length < 2) {
      for (const i of group) {
        keep.push(lines[i]);
        keepSpaces.push(spaces[i]);
      }
      continue;
    }
    const widthOf = (i, j) => measure(words.slice(i, j).join(" "), fontSize);
    const room = slots.map((l) => Math.min(l.interval[1] - l.interval[0], maxLineWidth));
    const n = words.length;
    const m = slots.length;
    // cost[k][j]: best cost of setting the first j words in the first k lines.
    const cost = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(Infinity));
    const from = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(-1));
    cost[0][0] = 0;
    for (let k = 1; k <= m; k++) {
      for (let j = 1; j <= n; j++) {
        for (let i = j - 1; i >= 0; i--) {
          const width = widthOf(i, j);
          if (width > room[k - 1] + 1e-9) break;
          if (cost[k - 1][i] === Infinity) continue;
          const slack = (room[k - 1] - width) / room[k - 1];
          // The last line of a paragraph can be as short as it likes,
          // as long as it isn't a lone short word.
          const here =
            j === n && endsParagraph
              ? j - i === 1 && n > 1 && width < 0.5 * room[k - 1] ? 0.2 : 0
              : slack * slack;
          if (cost[k - 1][i] + here < cost[k][j]) {
            cost[k][j] = cost[k - 1][i] + here;
            from[k][j] = i;
          }
        }
      }
    }
    let used = m;
    if (final) {
      for (let k = 1; k < m; k++) {
        if (cost[k][n] + 0.02 * k < cost[used][n] + 0.02 * used) used = k;
      }
    }
    if (cost[used][n] === Infinity) {
      for (const i of group) {
        keep.push(lines[i]);
        keepSpaces.push(spaces[i]);
      }
      continue;
    }
    const breaks = [n];
    for (let k = used, j = n; k > 0; k--) {
      j = from[k][j];
      breaks.unshift(j);
    }
    for (let k = 0; k < used; k++) {
      const slot = slots[k];
      const content = words.slice(breaks[k], breaks[k + 1]).join(" ");
      const width = measure(content, fontSize);
      const [a, b] = slot.interval;
      const x = align === "center" ? a + (b - a - width) / 2 : a;
      keep.push({ ...slot, text: content, x, width });
      keepSpaces.push(spaces[group[k]]);
    }
  }
  result.lines = keep;
  result.spaces = keepSpaces;
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
  const maxLineWidth = options.maxLineWidth ?? Infinity;
  const step = lineHeight / 4;
  const limit = panel.height - panel.padY;
  const fullWidth = panel.width - 2 * panel.padX;
  const fits = (s, width) => measure(s, fontSize) <= width;

  const lines = [];
  // The space each line had, before any alignment.
  const spaces = [];
  let y = options.startY ?? panel.padY;
  let overflow = false;

  const result = () => ({ lines, spaces, fits: !overflow, lineHeight, fontSize });

  let paragraphIndex = 0;
  const place = (words, interval, piece = false) => {
    const content = words.join(" ");
    const width = measure(content, fontSize);
    const x =
      align === "center"
        ? interval[0] + (interval[1] - interval[0] - width) / 2
        : interval[0];
    lines.push({
      text: content,
      x,
      y,
      width,
      height: lineHeight,
      interval,
      paragraph: paragraphIndex,
      piece,
    });
    y += lineHeight;
  };

  for (const paragraph of paragraphs(text)) {
    paragraphIndex++;
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
      const width = interval ? Math.min(interval[1] - interval[0], maxLineWidth) : 0;
      if (!interval || width < Math.min(minLineWidth, fullWidth)) {
        y += step;
        continue;
      }
      if (!fits(words[0], width)) {
        if (fits(words[0], interval[1] - interval[0])) {
          // Longer than a line should be, but there's room for it here on a
          // line of its own (which, like a piece of a broken word, stays
          // there when the lines around it are balanced).
          spaces.push(space);
          place([words.shift()], interval, true);
          continue;
        }
        if (fits(words[0], fullWidth)) {
          // There may be a wider gap further down.
          y += step;
          continue;
        }
        // Too long for any line: the first piece gets a line to itself.
        const piece = firstPiece(words[0], width, fits);
        words[0] = words[0].slice(piece.length);
        spaces.push(space);
        place([piece], interval, true);
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
// (but never shorter than the art), or options.cellHeight tall if that's
// given. The cells are options.cellWidth wide, with the art scaled to
// options.artWidth (by default, the cell width).
//
// Then any panel whose spec says `drop` has its text dropped down towards
// its speaker (see drop), no lower than spec.speakerY (in art pixels) less
// spec.keepGap; and if its spec says `centre`, moved across into the
// middle of its room (see centre) as long as it still spans spec.speakerX.
export function fitPanels(specs, texts, options) {
  const best = fitHeight(specs, texts, options);
  if (!best.fits) return best;
  best.layouts = best.layouts.map((layout, i) => {
    const panel = best.panels[i];
    const { spec } = panel;
    if (!spec.drop) return layout;
    return layoutText(panel, texts[i] ?? "", {
      ...panelOptions(panel, options),
      drop: true,
      dropLimit:
        spec.speakerY === undefined ? Infinity : panel.artTop + spec.speakerY * panel.scale,
      keepGap: spec.keepGap ?? 0,
      centreOn: spec.centre && spec.speakerX !== undefined ? spec.speakerX * panel.scale : undefined,
      floatGap: spec.floatGap,
      centreSlack: spec.centreSlack,
    });
  });
  return best;
}

function panelOptions(panel, options) {
  return {
    ...options,
    margin: panel.spec.margin ?? options.margin,
    awayFromArt: panel.spec.awayFromArt ?? options.awayFromArt,
    awayLimit: panel.spec.awayLimit ?? options.awayLimit,
    block: panel.spec.block ?? options.block,
    maxLineWidth: panel.spec.maxLineWidth ?? options.maxLineWidth,
  };
}

function fitHeight(specs, texts, options) {
  const { cellWidth, padding = 0, fontSize } = options;
  const artWidth = options.artWidth ?? cellWidth;
  const artHeight = Math.max(
    ...specs.map((spec) => spec.height * (artWidth / spec.width)),
  );

  const attempt = (cellHeight) => {
    const panels = specs.map((spec) =>
      makePanel(spec, cellWidth, cellHeight, padding, artWidth / spec.width),
    );
    const layouts = panels.map((panel, i) =>
      layoutText(panel, texts[i] ?? "", panelOptions(panel, options)),
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

  if (options.cellHeight !== undefined) return attempt(options.cellHeight);
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

// The width for cells that need room for text. Cells grow keeping their
// proportions (width / height = aspect) where that helps: the aim is the
// smallest cell as measured by the smallest box of those proportions that
// holds it, and among cells within SIZE_SLACK of that, the narrowest. So
// cells widen as far as it saves height (until they are in proportion),
// but text whose height doesn't come down with more width (short lines
// that don't wrap) just makes them taller. Widths go from minWidth to
// maxWidth in steps of `step`; fitAt(width) lays the comic out at a width,
// returning {cellHeight, fits}. Returns {width, result}.
const SIZE_SLACK = 0.01;

export function chooseWidth(fitAt, { minWidth, maxWidth, aspect, step }) {
  const inProportion = (result, width) => result.fits && result.cellHeight <= width / aspect + 1e-9;
  // Binary search for the narrowest width passing `ok`, given that `width`
  // (with `result`, its layout) does.
  const narrowest = (ok, { width, result: widest }) => {
    let lo = minWidth;
    let hi = width;
    let result = widest;
    while (hi - lo > step) {
      const mid = lo + Math.max(step, Math.floor((hi - lo) / 2 / step) * step);
      if (mid >= hi) break;
      const candidate = fitAt(mid);
      if (ok(candidate, mid)) {
        hi = mid;
        result = candidate;
      } else {
        lo = mid;
      }
    }
    return { width: hi, result };
  };

  const narrow = fitAt(minWidth);
  if (inProportion(narrow, minWidth) || maxWidth <= minWidth) return { width: minWidth, result: narrow };
  const wide = fitAt(maxWidth);
  // The size of the smallest cell: where it comes into proportion, or at
  // its widest if it never does.
  let size;
  let best;
  if (inProportion(wide, maxWidth)) {
    best = narrowest(inProportion, { width: maxWidth, result: wide });
    size = best.width;
  } else {
    best = { width: maxWidth, result: wide };
    size = wide.cellHeight * aspect;
  }
  const smallEnough = (result) => result.fits && result.cellHeight * aspect <= size * (1 + SIZE_SLACK);
  if (smallEnough(narrow)) return { width: minWidth, result: narrow };
  return narrowest(smallEnough, best);
}

// Which stretch of a panel's art, [start, end] in art pixels, to show in a
// cell `shown` art pixels wide. The art is spec.width wide, extended by
// spec.left (if any) on the left, to spec.extendedWidth in all: the
// original is kept in the middle as far as the extensions allow.
// Beyond a side marked openLeft or openRight there's only background, so
// the window can go on past it.
export function artWindow({ width, left = 0, extendedWidth, openLeft, openRight }, shown) {
  const extra = Math.max(0, shown - width);
  const leftRoom = openLeft ? Infinity : left;
  const rightRoom = openRight ? Infinity : extendedWidth - left - width;
  const before = Math.min(leftRoom, Math.max(extra / 2, extra - rightRoom));
  const start = left - before;
  return [start, openRight ? start + shown : Math.min(extendedWidth, start + shown)];
}

// Rows of intervals (free or open space) for art `width` wide that ends in
// plain background on the right: those that reach its edge (or its last
// whole grid cell) go on forever.
export function openBeyond(rows, width) {
  return rows.map((row) => row.map(([a, b]) => [a, b >= width - 1 ? Infinity : b]));
}

// A panel's description as seen with its art shown from x = `start` (in
// art pixels) on: everything in it that's placed across the art moved to
// match.
export function shiftedView(meta, start) {
  const rows = (r) => r && r.map((row) => row.map(([a, b]) => [a - start, b - start]));
  return {
    ...meta,
    start,
    free: rows(meta.free),
    open: rows(meta.open),
    speakers: Object.fromEntries(Object.entries(meta.speakers ?? {}).map(([k, [x, y]]) => [k, [x - start, y]])),
    ...(meta.calvinColumn && {
      calvinColumn: [meta.calvinColumn[0] - start, meta.calvinColumn[1] - start, meta.calvinColumn[2]],
    }),
  };
}
