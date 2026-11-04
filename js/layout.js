import { egyptianSegmentInteriors } from './egyptian-layout.js';
// Text layout for comic panels: flows text line by line into whatever space
// the artwork leaves free. Everything here is pure so it can be tested
// without a browser; measuring text is delegated to the caller.

import { paragraphDirection } from "./direction.js";
import { graphemes } from "./unicode.js";
import { breakUnits, lineContent, textParagraphs, emergencyBoundary } from "./line-breaks.js";
import { usesDictionaryScript } from './dictionary-breaks.js';
import { isGridText } from "./grid.js";

// A panel is a cell of a fixed width and height with the art scaled to the
// cell width and anchored to the bottom. Everything above the art is free.
//
// spec.free[row] is a list of [start, end) intervals, in art pixels, where
// text may go on that row of the art. spec.reserved is a list of
// [x0, y0, x1, y1] rectangles, in art pixels (y may be negative, above the
// art), taken up by something else, such as another character's balloon.
// spec.margin, spec.awayFromArt, spec.awayLimit, spec.block and
// spec.maxLineWidth, if given, override the layout options of the same
// names for that panel; spec.aboveSpeaker keeps the text above spec.speakerY
// less spec.keepGap. spec.keepVisible contains art-coordinate rectangles
// that reframing must never crop (for example, a character's whole head).
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
    padX: spec.padding?.x ?? padding?.x ?? padding,
    padY: spec.padding?.y ?? padding?.y ?? padding,
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

// The longest start of a word too long for a line that fits in `width`:
// only at grapheme boundaries that keep punctuation and glue attached. Normal
// punctuation opportunities have already been handled by Unicode line breaking.
function firstPiece(word, width, fits) {
  // Dictionary opportunities already separated these units. Splitting one
  // again at arbitrary graphemes can strand Myanmar spacing vowels and defeat
  // word-based Thai/Lao/Khmer/Myanmar wrapping. Grow or fit the complete word.
  if(usesDictionaryScript(word))return word;
  const clusters = graphemes(word);
  let n = 1;
  while (n < clusters.length && fits(clusters.slice(0, n + 1).join(""), width)) n++;
  const interiors = egyptianSegmentInteriors(word);
  let offset=0;const ends=clusters.map(c=>(offset+=c.length));
  const safe = k => k === clusters.length || (!interiors.has(ends[k-1]) && emergencyBoundary(clusters[k - 1], clusters[k]));
  for (let k = n; k >= 1; k--) {
    if (safe(k)) return clusters.slice(0, k).join("");
  }
  while (n < clusters.length && !safe(n)) n++;
  return clusters.slice(0, n).join("");
}

// Lay `text` out in `panel` from the top down. Returns the positioned lines,
// whether everything fitted, and the line height used.
//
// options: measure(text, fontSize), fontSize, lineHeight (a multiple of the
// font size), margin (clearance from the art), align ("left" | "center"),
// minLineWidth (narrower gaps are skipped; defaults to 3 em), startY (where
// the first line goes; defaults to the top padding), awayFromArt and
// awayLimit (see moveAwayFromArt), drop, dropLimit and keepGap (see drop).
// fitUnbreakable optionally shrinks only a protected piece that cannot fit
// at full size. Its actual fontSize and ink metrics travel with the line.
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
// (see squeezed), and text whose last line comes below options.bottomLimit.
export function layoutText(panel, text, options) {
  if (options.measure.envelope) {
    options = { ...options, lineBox: options.measure.envelope(text, options.fontSize, options.lineHeight ?? 1.2) };
  }
  let result;
  const grid = options.measure.grid && isGridText(text);
  if (grid) {
    result = flowGrid(panel, text, options);
  } else if (options.align !== "left") {
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
  if (!grid) {
    balance(result, options);
    compactInkLines(result, panel, options);
  }
  if (options.awayFromArt && options.align === "left") {
    moveAwayFromArt(result, panel, options.awayLimit ?? Infinity);
  }
  result = {
    ...result,
    fits:
      !stranded(result) &&
      !(options.block && (squeezed(result) || gapped(result))) &&
      !(options.bottomLimit !== undefined && bottom(result) > options.bottomLimit + 1e-9),
  };
  if (options.drop && result.fits && result.lines.length) result = drop(panel, text, options, result);
  if (options.centreOn !== undefined && result.fits && result.lines.length) {
    centre(result, options.centreOn, options.centreSlack);
  }
  return result;
}

// Wrapping reserves the tallest possible slot. Once the actual lines are
// known, remove surplus vertical room without moving ink into the artwork.
// A paragraph break adds half an ordinary line, independently of tall marks.
function compactInkLines(result, panel, options) {
  if (!result.lines.length || !options.measure.ink) return;
  const nominal = options.fontSize * (options.lineHeight ?? 1.2);
  const clearance = options.fontSize * Math.max(.08, (options.lineHeight ?? 1.2)-1);
  let previous;
  for (let i = 0; i < result.lines.length; i++) {
    const line = result.lines[i], ink = line.ink;
    if (!ink || line.grid) { previous = line; continue; }
    const height = Math.max(nominal, ink.ascent+ink.descent+clearance);
    const baseline = (height+ink.ascent-ink.descent)/2;
    let y = line.y;
    if (previous?.ink) {
      const blank = Math.max(0, line.paragraph-previous.paragraph-1);
      const baselineStep = Math.max(nominal, previous.ink.descent+ink.ascent+clearance);
      y = Math.max(previous.y+previous.height,
        previous.y+previous.baseline+baselineStep-baseline) + blank*nominal*.5;
      y = Math.min(y, line.y);
    }
    const interval = freeIntervals(panel,y,y+height,options.margin??0)
      .find(([a,b])=>a<=line.x+1e-6 && b>=line.x+line.width-1e-6);
    if (interval) {
      line.y=y;line.height=height;line.baseline=baseline;
      line.interval=[Math.max(line.interval[0],interval[0]),Math.min(line.interval[1],interval[1])];
      result.spaces[i]=line.interval;
    }
    previous=line;
  }
}

// A diagram is one rectangular object: rows share a cell size, origin and
// baseline spacing. It may move or shrink as a whole, but never reflow around
// artwork or centre each row independently (both would break connections).
function flowGrid(panel, text, options) {
  let size = options.fontSize;
  let block = options.measure.grid(text,size);
  const fullWidth = panel.width - 2*panel.padX;
  if (options.fitUnbreakable) {
    for (let n = 0; block.width > fullWidth && n < 32; n++) {
      size *= Math.min(0.9,fullWidth/block.width*0.98);
      block = options.measure.grid(text,size);
    }
  }
  const result = (lines,spaces,fits) => ({lines,spaces,fits,lineHeight:block.lineHeight,fontSize:size});
  if (!block.rows.length) return result([],[],true);
  if (block.width > fullWidth) {
    // Retain dimensions for Calvin's existing fit loop to scale the whole grid.
    return result(block.rows.map((line,i) => ({...line,x:panel.padX,y:panel.padY+i*block.lineHeight,
      interval:[panel.padX,panel.width-panel.padX],paragraph:1})),[],false);
  }
  const limit = panel.height - panel.padY;
  for (let y = options.startY ?? panel.padY; y + block.height <= limit; y += block.lineHeight/4) {
    const space = widest(freeIntervals(panel,y,y+block.height,options.margin ?? 0));
    if (!space || space[1]-space[0] < block.width) continue;
    const x = options.align === 'left' ? space[0] : (space[0]+space[1]-block.width)/2;
    return result(block.rows.map((line,i) => ({...line,x,y:y+i*block.lineHeight,
      interval:space,paragraph:1})),block.rows.map(()=>space),true);
  }
  return result([],[],false);
}

// A balloon sits in the middle of the room its lines have, as long as it
// still spans its speaker (at x = speakerX), or starts no more than `slack`
// past them, so that its tail can come down beside them; if it can't do
// that anywhere, it stays where it is (beside them, with room for a tail).
function centre({ lines }, speakerX, slack = 0) {
  const roomLeft = Math.max(...lines.map((l) => l.interval[0]));
  const roomRight = Math.min(...lines.map((l) => l.interval[1]));
  const left = Math.min(...lines.map((l) => l.x));
  const width = Math.max(...lines.map((l) => l.x + l.width)) - left;
  if (roomRight - roomLeft < width) return;
  // Where it may go and still span (or nearly span) the speaker.
  const lo = Math.max(roomLeft, speakerX - width);
  const hi = Math.min(roomRight - width, speakerX + slack);
  if (lo > hi) return;
  const target = Math.min(Math.max((roomLeft + roomRight - width) / 2, lo), hi);
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

// How far down the text's last line comes.
function bottom({ lines }) {
  return lines.length ? lines[lines.length - 1].y + lines[lines.length - 1].height : -Infinity;
}

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
function balance(result, { measure: baseMeasure, fontSize, align = "center", maxLineWidth = Infinity }) {
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
    const measure = baseMeasure.forDirection?.(slots[0].direction) ?? baseMeasure;
    const words = slots.flatMap((l) => l.units ?? breakUnits(l.text));
    const paragraphMeasure = baseMeasure.forParagraph?.(slots[0].sourceParagraph);
    const offsets = [slots[0].sourceOffset ?? 0];
    for (const word of words) offsets.push(offsets.at(-1) + word.length);
    const measureAt = i => paragraphMeasure?.at(offsets[i]) ?? measure;
    if (fixed || slots.length < 2) {
      for (const i of group) {
        keep.push(lines[i]);
        keepSpaces.push(spaces[i]);
      }
      continue;
    }
    const room = slots.map((l) => Math.min(l.interval[1] - l.interval[0], maxLineWidth));
    const n = words.length;
    const m = slots.length;
    // Balancing is aesthetic; the already fitted greedy lines preserve all
    // content and break rules. Bound its quadratic DP allocation/work for
    // maximum-length prose and CJK paragraphs with thousands of break units.
    if (n > 512 || (n + 1) * (m + 1) > 65536) {
      for (const i of group) {
        keep.push(lines[i]);
        keepSpaces.push(spaces[i]);
      }
      continue;
    }
    // The width of words i to j as a line: estimated from the words' own
    // widths, which is quick, or measured, which is exact (each once: the
    // search asks for the same ones over and over).
    const before = [0], endAdjustment = [0];
    for (const [i, word] of words.entries()) {
      const advance = measureAt(i)(word.replace(/[\u00ad\u200b]/gu, ''), fontSize);
      before.push(before.at(-1) + advance);
      endAdjustment.push(advance - measureAt(i)(lineContent([word], endsParagraph && i === words.length - 1), fontSize));
    }
    const estimate = (i, j) => before[j] - before[i] - endAdjustment[j];
    const widths = new Map();
    const exact = (i, j) => {
      const key = i * (n + 1) + j;
      let width = widths.get(key);
      if (width === undefined) {
        width = measureAt(i)(lineContent(words.slice(i, j), endsParagraph && j === n), fontSize);
        widths.set(key, width);
      }
      return width;
    };
    // The best breaks with widths from widthOf: {used, from}, or null if
    // there are none.
    const solve = (widthOf) => {
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
      return cost[used][n] === Infinity ? null : { used, from };
    };
    const lineBreaks = ({ used, from }) => {
      const out = [n];
      for (let k = used, j = n; k > 0; k--) {
        j = from[k][j];
        out.unshift(j);
      }
      return out;
    };
    // Estimated widths can be a little out (kerning, alternate forms), so
    // if any line chosen with them is really too long, choose again
    // exactly.
    let solved = solve(estimate);
    if (solved) {
      const b = lineBreaks(solved);
      const tooLong = b.slice(0, -1).some((i, k) => exact(i, b[k + 1]) > room[k] + 1e-9);
      if (tooLong) solved = solve(exact);
    } else {
      solved = solve(exact);
    }
    if (!solved) {
      for (const i of group) {
        keep.push(lines[i]);
        keepSpaces.push(spaces[i]);
      }
      continue;
    }
    const { used } = solved;
    const breaks = lineBreaks(solved);
    for (let k = 0; k < used; k++) {
      const slot = slots[k];
      const units = words.slice(breaks[k], breaks[k + 1]);
      const content = lineContent(units, endsParagraph && breaks[k + 1] === n);
      const lineMeasure = measureAt(breaks[k]);
      const width = lineMeasure(content, fontSize);
      const [a, b] = slot.interval;
      const x = align === "center" ? a + (b - a - width) / 2 : a;
      const ink = lineMeasure.ink?.(content, fontSize);
      keep.push({ ...slot, units, text: content, sourceOffset: offsets[breaks[k]], x, width, ink, fontSize: ink?.fontSize ?? fontSize });
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
  // The current group: how many lines, the furthest right start, the
  // nearest end, and the widest space.
  let count = 0;
  let edge = -Infinity;
  let end = Infinity;
  let widest = 0;
  const finish = () => {
    for (let k = 0; k < count; k++) out.push(edge);
    count = 0;
    edge = -Infinity;
    end = Infinity;
    widest = 0;
  };
  for (const [a, b] of spaces) {
    if (count) {
      const shortest = Math.min(end, b) - Math.max(edge, a);
      if (shortest < ALIGN_SHARE * Math.max(widest, b - a)) finish();
    }
    count++;
    edge = Math.max(edge, a);
    end = Math.min(end, b);
    widest = Math.max(widest, b - a);
  }
  if (count) finish();
  return out;
}

function flow(panel, text, options, minimums) {
  const { measure: baseMeasure, fontSize, align = "center" } = options;
  let measure = baseMeasure, direction = "ltr";
  let sourceParagraph = "", sourceOffset = 0;
  const lineHeight = options.lineBox?.height ?? fontSize * (options.lineHeight ?? 1.2);
  const margin = options.margin ?? 0;
  const minLineWidth = options.minLineWidth ?? fontSize * 3;
  const maxLineWidth = options.maxLineWidth ?? Infinity;
  const step = lineHeight / 4;
  const limit = panel.height - panel.padY;
  const fullWidth = panel.width - 2 * panel.padX;
  const fits = (s, width, endsParagraph = false) => measure(lineContent([s], endsParagraph), fontSize) <= width;

  const lines = [];
  // The space each line had, before any alignment.
  const spaces = [];
  let y = options.startY ?? panel.padY;
  let overflow = false;

  const result = () => ({ lines, spaces, fits: !overflow, lineHeight, fontSize });

  let paragraphIndex = 0;
  const place = (words, interval, piece = false, endsParagraph = false) => {
    const content = lineContent(words, endsParagraph);
    let size = fontSize;
    let width = measure(content, size);
    const room = interval[1] - interval[0];
    if (piece && options.fitUnbreakable) {
      for (let attempt = 0; width > room && attempt < 32; attempt++) {
        size *= Math.min(0.9, room / width * 0.98);
        width = measure(content, size);
      }
      if (width > room) overflow = true;
    }
    const ink = measure.ink?.(content, size);
    const x =
      align === "center"
        ? interval[0] + (interval[1] - interval[0] - width) / 2
        : interval[0];
    lines.push({
      text: content,
      units: words,
      direction,
      sourceParagraph,
      sourceOffset,
      x,
      y,
      width,
      height: lineHeight,
      baseline: size !== fontSize && ink
        ? (lineHeight + ink.ascent - ink.descent) / 2 : options.lineBox?.baseline,
      fontSize: ink?.fontSize ?? size,
      ink,
      interval,
      paragraph: paragraphIndex,
      piece,
    });
    sourceOffset += words.join("").length;
    y += lineHeight;
  };

  for (const paragraph of textParagraphs(text)) {
    paragraphIndex++;
    sourceParagraph = paragraph.join("");
    sourceOffset = 0;
    direction = paragraphDirection(sourceParagraph);
    const paragraphMeasure = baseMeasure.forParagraph?.(sourceParagraph);
    const directionMeasure = baseMeasure.forDirection?.(direction) ?? baseMeasure;
    if (paragraph.length === 0) {
      // A blank paragraph is one ordinary blank line, even when accented
      // letters elsewhere in the speech require an unusually tall line box.
      y += options.lineBox?.blankHeight ?? lineHeight;
      continue;
    }
    const words = [...paragraph];
    while (words.length) {
      measure = paragraphMeasure?.at(sourceOffset) ?? directionMeasure;
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
      if (!fits(words[0], width, words.length === 1)) {
        if (fits(words[0], interval[1] - interval[0], words.length === 1)) {
          // Longer than a line should be, but there's room for it here on a
          // line of its own (which, like a piece of a broken word, stays
          // there when the lines around it are balanced).
          spaces.push(space);
          place([words.shift()], interval, true, words.length === 0);
          continue;
        }
        if (fits(words[0], fullWidth, words.length === 1)) {
          // There may be a wider gap further down.
          y += step;
          continue;
        }
        // Too long for any line: the first piece gets a line to itself.
        const piece = firstPiece(words[0], width, fits);
        words[0] = words[0].slice(piece.length);
        if (!words[0]) words.shift();
        if (!fits(piece, width, words.length === 0) && !options.fitUnbreakable) overflow = true;
        spaces.push(space);
        place([piece], interval, true, words.length === 0);
        continue;
      }
      const line = [words.shift()];
      while (words.length && fits([...line, words[0]].join(""), width, words.length === 1)) {
        line.push(words.shift());
      }
      spaces.push(space);
      place(line, interval, false, words.length === 0);
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
  const height = lines.length ? lines[lines.length - 1].y + lines[lines.length - 1].height : 0;
  return { lines, height, lineHeight: layout.lineHeight, fontSize, fits: layout.fits };
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
    // Text in a balloon ends above its speaker's mouth, so that its tail
    // can come down to them.
    bottomLimit:
      panel.spec.aboveSpeaker && panel.spec.speakerY !== undefined
        ? panel.artTop + panel.spec.speakerY * panel.scale - (panel.spec.keepGap ?? 0)
        : options.bottomLimit,
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
      reservedAreas(panel).every(([, y0]) => y0 >= 0) &&
      (panel.spec.keepVisible ?? []).every(([x0, y0, x1, y1]) =>
        x0 * panel.scale >= 0 && x1 * panel.scale <= panel.width &&
        panel.artTop + y0 * panel.scale >= 0 &&
        panel.artTop + y1 * panel.scale <= panel.height),
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
  // Text this long is a joke, but it should still fit; this only stops the
  // search for something that never will.
  const maxExtra = options.maxExtra ?? artHeight * 2000;
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
    keepVisible: meta.keepVisible?.map(([x0, y0, x1, y1]) => [x0 - start, y0, x1 - start, y1]),
    free: rows(meta.free),
    open: rows(meta.open),
    speakers: Object.fromEntries(Object.entries(meta.speakers ?? {}).map(([k, [x, y]]) => [k, [x - start, y]])),
    ...(meta.calvinColumn && {
      calvinColumn: [meta.calvinColumn[0] - start, meta.calvinColumn[1] - start, meta.calvinColumn[2]],
    }),
  };
}
