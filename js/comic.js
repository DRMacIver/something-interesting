// Laying out and drawing the comic: the four panels, the lettering, and its
// balloons. drawComic draws onto any canvas and returns a description of
// what it drew, which the page uses to report problems and the checks page
// uses to judge the result.

import { chooseWidth, fitPanels, layoutColumn } from "./layout.js";
import { balloonOutline, balloonTail, clearOf } from "./balloon.js";

// The width of a panel's original art, and so of a cell when there isn't
// much to say. Cells with a lot to say grow, keeping the original panels'
// proportions, as far as the art (extended to the right) allows.
const CELL_WIDTH = 800;
const GUTTER = 30;
const OUTER = 30;
const BORDER = 5;
const INK = "#111";
const FONT = "Dad Lettering";
// Line spacing as a multiple of the font size, measured from the strip.
const LINE_HEIGHT = 1.1;

// Proportions of Watterson's lettering and balloons, in multiples of the
// lettering's cap height, measured from the book (docs/balloon-study.md).
// Dialogue starts this far below the top of the panel and this far in from
// its sides.
const TOP_GAP = 0.45;
const SIDE_GAP = 0.7;
export const BALLOON = {
  // Space between the lettering and the balloon line, beyond the line
  // spacing: 0.65 cap below the last line and 0.7 at the sides in all.
  padX: 0.7,
  padY: 0.36,
  radius: 1,
  // Smaller balloons are rounder: corners round over at least this share
  // of the text's shorter side.
  roundness: 0.3,
  line: 0.1,
  // A balloon comes out of the panel border rather than running alongside
  // it when it comes within about a cap of it.
  reach: 1.2,
  tailWidth: 0.4,
  tailLength: 1.3,
  tailMinLength: 0.35,
  tailGap: 0.45,
  // A balloon with more open space than this between it and its speaker
  // gets a long tail, reaching to within this of them.
  tailReach: 2,
};
// The pen stroke beside loose lettering.
const STROKE = { pad: 0.35, length: 1.2, line: 0.12 };
// Clearance between text and artwork: loose lettering can come close;
// lettering in a balloon leaves room for the balloon and a short tail.
const ART_MARGIN = 0.4;
const BALLOON_MARGIN = BALLOON.padX + 0.8;
// Text pushed aside by the art moves at most this far further away, to
// leave room for a tail.
const AWAY_LIMIT = 2;
// Short text drops down towards its speaker, stopping this far above their
// mouth.
const KEEP_GAP = 1;
// Loose lettering (the panel 3 "wall of text") only works when there's a
// lot of it: less than this many lines' worth gets a balloon instead.
const LOOSE_LINES = 3.5;

export const DEFAULTS = [
  "Vibecoding something? Let me show you something interesting.",
  "There are two types of vibecoded projects: piracy, and extremely " +
    "bespoke artisanal itch scratching. Everything falls into one or the other.",
  "A Discord clone? Piracy. A custom desktop environment? Itch scratching.\n\n" +
    "Despite literally being based on Bill Watterson's copyrighted work, drmaciver.github.io/something-interesting is itch scratching.",
  "That seems reductive.",
];
// Dad's lines in panels 1-3, then Calvin's reply in panel 2.
const CALVIN = 3;
// Calvin's reply is widened rather than going over this many lines.
const CALVIN_MAX_LINES = 4;

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

// The panel art and its description, with the lettering font loaded.
export async function loadComic(base = "") {
  const response = await fetch(base + "assets/panels.json");
  const assets = await response.json();
  const images = await Promise.all(assets.panels.map((p) => loadImage(base + p.image)));
  const signed = assets.panels.find((p) => p.signature);
  const signature = signed && (await loadImage(base + signed.signature.image));
  try {
    await document.fonts.load(`20px "${FONT}"`, "AB");
  } catch {
    // Render with whatever the browser has rather than nothing.
  }
  return { assets, images, signature };
}

function fontString(size) {
  return `${size}px "${FONT}", cursive`;
}

// Whether a point in a cell is clear of the panel's artwork (points outside
// the panel aren't).
export function openAt(panel, meta, [x, y]) {
  if (x < 0 || x > panel.width || y < 0 || y > panel.height) return false;
  if (y < panel.artTop) return true;
  const row = meta.open?.[Math.floor((y - panel.artTop) / panel.scale)];
  if (!row) return false;
  const gx = x / panel.scale;
  return row.some(([a, b]) => gx >= a && gx < b);
}

// The stretch of open space (in art pixels) containing x = `centre` on
// every row from y0 to y1, ignoring rows above the art.
function openSpan(meta, y0, y1, centre) {
  let span = [0, meta.extendedWidth];
  for (let row = Math.max(0, Math.floor(y0)); row < Math.min(meta.height, Math.ceil(y1)); row++) {
    const here = (meta.open[row] ?? []).find(([a, b]) => a <= centre && centre < b);
    if (!here) return [centre, centre];
    span = [Math.max(span[0], here[0]), Math.min(span[1], here[1])];
  }
  return span;
}

function speakerPoint(panel, point) {
  return [point[0] * panel.scale, panel.artTop + point[1] * panel.scale];
}

// Draw the comic for `texts` (Dad's lines in panels 1-3, then Calvin's
// reply) onto `canvas`, resizing it to fit. Returns what was drawn:
// {fits, cap, panels: [{x, y, panel, meta, speech, speeches}]}, where each
// speech is {who, lines, speaker, outline, tail, stroke} in cell
// coordinates.
export function drawComic(canvas, { assets, images, signature }, texts) {
  const ctx = canvas.getContext("2d");
  const widths = new Map();
  const measure = (text, size) => {
    const key = `${size}\u0000${text}`;
    let width = widths.get(key);
    if (width === undefined) {
      ctx.font = fontString(size);
      width = ctx.measureText(text).width;
      widths.set(key, width);
    }
    return width;
  };
  ctx.font = fontString(100);
  const capRatio = ctx.measureText("H").actualBoundingBoxAscent / 100;
  const panelWidth = assets.panels.reduce((sum, p) => sum + p.width, 0) / assets.panels.length;
  const cap = (assets.capHeight * CELL_WIDTH) / panelWidth;
  const fontSize = cap / capRatio;
  const lineWidth = CELL_WIDTH - 2 * SIDE_GAP * cap;

  // How each panel's dialogue is lettered: as in the original, except that
  // loose lettering is only for a lot of text.
  const speechFor = (meta, text) =>
    meta.speech === "loose" &&
    measure(text.toUpperCase(), fontSize) < LOOSE_LINES * lineWidth
      ? "balloon"
      : meta.speech;
  const speeches = assets.panels.map((meta, i) => (meta.speech ? speechFor(meta, texts[i] ?? "") : null));

  const calvinMeta = assets.panels.find((p) => p.calvinColumn);
  // The gaps are measured to the lettering itself, which sits in the middle
  // of its line's spacing.
  const leading = (LINE_HEIGHT * fontSize - cap) / 2;
  // The comic laid out with cells `cellWidth` wide.
  const layoutAt = (cellWidth) => {
    const calvin = layoutCalvin(calvinMeta, texts[CALVIN].toUpperCase(), measure, fontSize, cap, cellWidth);
    const specs = assets.panels.map((p, i) => ({
      width: p.width,
      height: p.height,
      free: p.free ?? [],
      reserved: p === calvinMeta ? calvin.reserved : [],
      margin: (speeches[i] === "balloon" ? BALLOON_MARGIN : ART_MARGIN) * cap,
      awayFromArt: speeches[i] === "balloon",
      block: speeches[i] === "balloon",
      awayLimit: AWAY_LIMIT * cap,
      drop: Boolean(p.speakers.dad),
      speakerY: p.speakers.dad?.[1],
      keepGap: KEEP_GAP * cap,
    }));
    const result = fitPanels(specs, [...texts.slice(0, 3).map((t) => t.toUpperCase()), ""], {
      measure,
      fontSize,
      lineHeight: LINE_HEIGHT,
      margin: ART_MARGIN * cap,
      align: "left",
      cellWidth,
      artWidth: CELL_WIDTH,
      padding: { x: SIDE_GAP * cap, y: Math.max(0, TOP_GAP * cap - leading) },
    });
    return { ...result, calvin };
  };
  const artHeight = Math.max(...assets.panels.map((p) => (p.height * CELL_WIDTH) / p.width));
  const maxWidth = Math.min(...assets.panels.map((p) => (p.extendedWidth * CELL_WIDTH) / p.width));
  const { width: cellWidth, result } = chooseWidth(layoutAt, {
    minWidth: CELL_WIDTH,
    maxWidth: Math.floor(maxWidth),
    aspect: CELL_WIDTH / artHeight,
    step: cap,
  });
  const { cellHeight, calvin } = result;

  // Place Calvin's lines in the panel, now that its size is known.
  const calvinIndex = assets.panels.indexOf(calvinMeta);
  const calvinPanel = result.panels[calvinIndex];
  const calvinLeft = calvin.column.left * calvinPanel.scale;
  const calvinTop =
    calvinPanel.artTop + calvinMeta.calvinColumn[2] * calvinPanel.scale - calvin.column.height;
  const calvinLines = calvin.column.lines.map((l) => ({
    ...l,
    x: calvinLeft + l.x,
    y: calvinTop + l.y,
  }));

  canvas.width = OUTER * 2 + cellWidth * 2 + GUTTER;
  canvas.height = Math.ceil(OUTER * 2 + cellHeight * 2 + GUTTER);
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const report = { fits: result.fits, cap, cellWidth, cellHeight, panels: [] };
  result.panels.forEach((panel, i) => {
    const meta = assets.panels[i];
    const said = [];
    if (meta.speakers.dad) {
      said.push({
        who: "dad",
        lines: result.layouts[i].lines,
        speaker: speakerPoint(panel, meta.speakers.dad),
      });
    }
    if (i === calvinIndex) {
      said.push({ who: "calvin", lines: calvinLines, speaker: speakerPoint(panel, meta.speakers.calvin) });
    }
    const x = OUTER + (i % 2) * (cellWidth + GUTTER);
    const y = OUTER + Math.floor(i / 2) * (cellHeight + GUTTER);

    ctx.save();
    ctx.translate(x, y);
    ctx.beginPath();
    ctx.rect(0, 0, cellWidth, cellHeight);
    ctx.clip();
    ctx.fillStyle = meta.background;
    ctx.fillRect(0, 0, cellWidth, cellHeight);
    // Calvin always has a balloon; Dad as his panel's style says.
    const ballooned = said.filter((s) => s.who === "calvin" || speeches[i] === "balloon");
    drawBalloons(ctx, panel, meta, ballooned, cap);
    // Where the art is black ink on white, multiplying it in keeps every
    // line of it visible even where a balloon overlaps it.
    if (meta.background === "#fff") ctx.globalCompositeOperation = "multiply";
    ctx.imageSmoothingQuality = "high";
    // As much of the (extended) art as the cell is wide.
    const image = images[i];
    const shown = Math.min(1, cellWidth / (meta.extendedWidth * panel.scale));
    ctx.drawImage(
      image,
      0,
      0,
      image.width * shown,
      image.height,
      0,
      panel.artTop,
      meta.extendedWidth * panel.scale * shown,
      meta.height * panel.scale,
    );
    ctx.globalCompositeOperation = "source-over";
    if (meta.signature) {
      const { right, bottom, width, height } = meta.signature;
      ctx.drawImage(
        signature,
        cellWidth - (right + width) * panel.scale,
        panel.artTop + (meta.height - bottom - height) * panel.scale,
        width * panel.scale,
        height * panel.scale,
      );
    }
    for (const speech of said) {
      drawLines(ctx, speech.lines, fontSize);
      if (!ballooned.includes(speech) && speech.lines.length) {
        speech.stroke = drawStroke(ctx, speech, panel, meta, cap);
      }
    }
    ctx.restore();

    ctx.strokeStyle = INK;
    ctx.lineWidth = BORDER;
    ctx.strokeRect(x, y, cellWidth, cellHeight);
    report.panels.push({ x, y, panel, meta, speech: speeches[i], speeches: said });
  });
  return report;
}

// Calvin's reply, lettered in a column just above his head in panel 2, in
// a cell `cellWidth` wide. It grows upwards, and the space it takes (with
// its balloon) is reserved so that Dad's text flows around it.
function layoutCalvin(meta, text, measure, fontSize, cap, cellWidth) {
  const [x0, x1, bottom] = meta.calvinColumn;
  const scale = CELL_WIDTH / meta.width;
  // His balloon floats free of the panel's sides, rather than coming near
  // enough to hang from one.
  const side = ((BALLOON.reach + 0.2) * cap) / scale;
  const padX = (BALLOON.padX * cap) / scale;
  const padY = (BALLOON.padY * cap) / scale;
  const lay = (width) =>
    layoutColumn(text, { measure, fontSize, lineHeight: LINE_HEIGHT, width: width * scale });
  // The open space, beside Dad's head, that a column `height` tall can use.
  const room = (height) => {
    const [a, b] = openSpan(meta, bottom - height / scale, bottom, (x0 + x1) / 2);
    return [Math.max(a, side) + padX, Math.min(b, cellWidth / scale - side) - padX];
  };
  // A longer reply gets a wider column rather than a tall thin one, as far
  // as the open space allows.
  let width = x1 - x0;
  let column = lay(width);
  while (column.lines.length > CALVIN_MAX_LINES) {
    const wider = width * 1.15;
    const candidate = lay(wider);
    const [a, b] = room(candidate.height);
    if (wider > b - a) break;
    width = wider;
    column = candidate;
  }
  // Centred where his balloon was, but kept within the open space.
  const [a, b] = room(column.height);
  const middle = Math.min(Math.max((x0 + x1) / 2, a + width / 2), b - width / 2);
  column.left = middle - width / 2;
  if (!column.lines.length) return { column, reserved: [] };
  const used = Math.max(...column.lines.map((l) => l.width)) / scale;
  return {
    column,
    reserved: [
      [
        middle - used / 2 - padX,
        bottom - column.height / scale - padY,
        middle + used / 2 + padX,
        bottom + padY,
      ],
    ],
  };
}

function drawLines(ctx, lines, fontSize) {
  ctx.font = fontString(fontSize);
  ctx.fillStyle = INK;
  ctx.textBaseline = "alphabetic";
  // Centre the capital letters vertically in each line box.
  const capHeight = ctx.measureText("H").actualBoundingBoxAscent;
  for (const line of lines) {
    ctx.fillText(line.text, line.x, line.y + (line.height + capHeight) / 2);
  }
}

// Lettering without a balloon gets a quick pen stroke towards the speaker,
// finding its way round the art the way a balloon's tail does: it's a tail
// for an invisible box round the text, drawn as a single line. Returns the
// stroke, if there's room for one.
function drawStroke(ctx, { lines, speaker }, panel, meta, cap) {
  const pad = STROKE.pad * cap;
  const x0 = Math.min(...lines.map((l) => l.x)) - pad;
  const x1 = Math.max(...lines.map((l) => l.x + l.width)) + pad;
  const y0 = Math.min(...lines.map((l) => l.y)) - pad;
  const y1 = Math.max(...lines.map((l) => l.y + l.height)) + pad;
  const box = [
    [x0, y0],
    [x1, y0],
    [x1, y1],
    [x0, y1],
  ];
  const tail = balloonTail(box, speaker, {
    width: 0.2 * cap,
    maxLength: STROKE.length * cap,
    minLength: 0.4 * cap,
    gap: BALLOON.tailGap * cap,
    isFree: (p) => openAt(panel, meta, p),
  });
  if (!tail) return null;
  const [b1, b2] = tail.base;
  ctx.beginPath();
  ctx.moveTo((b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2);
  ctx.quadraticCurveTo(...tail.bend, ...tail.tip);
  ctx.strokeStyle = INK;
  ctx.lineWidth = STROKE.line * cap;
  ctx.lineCap = "round";
  ctx.stroke();
  return tail;
}

function polygonPath(ctx, points) {
  ctx.moveTo(...points[0]);
  for (const p of points.slice(1)) ctx.lineTo(...p);
  ctx.closePath();
}

// A tail as a narrow wedge along its curved centre line: each side curves
// from one end of the base to the tip, alongside the centre line.
function tailPath(ctx, { base: [b1, b2], bend, tip }) {
  const mid = [(b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2];
  const side = (b) => [bend[0] + (b[0] - mid[0]) / 2, bend[1] + (b[1] - mid[1]) / 2];
  ctx.moveTo(...b1);
  ctx.quadraticCurveTo(...side(b1), ...tip);
  ctx.quadraticCurveTo(...side(b2), ...b2);
  ctx.closePath();
}

// The balloons for one panel. Each speech's outline and tail are recorded
// on it. All outlines are stroked at double width and then all are filled
// white, which leaves just the outer edge of their union: balloons that
// touch merge, and each tail opens into its balloon.
function drawBalloons(ctx, panel, meta, speeches, cap) {
  const isFree = (p) => openAt(panel, meta, p);
  // Whatever of a balloon lies outside the panel is cut off by its border.
  const inside = ([x, y]) => x >= 0 && x <= panel.width && y >= 0 && y <= panel.height;
  const shown = speeches.filter((s) => s.lines.length);
  const boxes = (speech) =>
    speech.lines.map(({ x, y, width, height }) => [
      [x, y],
      [x + width, y],
      [x + width, y + height],
      [x, y + height],
    ]);
  for (const speech of shown) {
    // A balloon keeps clear of the art, and of everyone else's lettering,
    // with room for their balloon.
    const othersText = clearOf(
      shown.filter((s) => s !== speech).flatMap(boxes),
      (BALLOON.padX + BALLOON.line + 0.2) * cap,
    );
    speech.outline = balloonOutline(speech.lines, {
      padX: BALLOON.padX * cap,
      padY: BALLOON.padY * cap,
      radius: BALLOON.radius * cap,
      roundness: BALLOON.roundness,
      ovalLines: 1,
      isFree: (p) => (!inside(p) || isFree(p)) && othersText(p),
      panel: { x0: 0, y0: 0, x1: panel.width, y1: panel.height, reach: BALLOON.reach * cap },
    });
  }
  const shapes = [];
  for (const speech of shown) {
    shapes.push(speech.outline);
    // A tail keeps clear of the other balloons as well as the art, so it
    // never seems to point at someone else's words.
    const others = clearOf(
      shown.filter((s) => s !== speech).map((s) => s.outline),
      BALLOON.tailGap * cap,
    );
    speech.tail = balloonTail(speech.outline, speech.speaker, {
      width: BALLOON.tailWidth * cap,
      maxLength: BALLOON.tailLength * cap,
      minLength: BALLOON.tailMinLength * cap,
      gap: BALLOON.tailGap * cap,
      blockedPenalty: 2 * cap,
      clearSight: 1.5 * cap,
      reach: BALLOON.tailReach * cap,
      isFree: (p) => isFree(p) && others(p),
      isArtFree: (p) => !inside(p) || isFree(p),
    });
    if (speech.tail) shapes.push(speech.tail);
  }
  const trace = (shape) => {
    ctx.beginPath();
    if (Array.isArray(shape)) polygonPath(ctx, shape);
    else tailPath(ctx, shape);
  };
  ctx.lineJoin = "round";
  ctx.strokeStyle = INK;
  ctx.lineWidth = 2 * BALLOON.line * cap;
  for (const shape of shapes) {
    trace(shape);
    ctx.stroke();
  }
  ctx.fillStyle = "#fff";
  for (const shape of shapes) {
    trace(shape);
    ctx.fill();
  }
}
