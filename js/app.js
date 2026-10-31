import { fitPanels, layoutColumn } from "./layout.js";
import { balloonOutline, balloonTail } from "./balloon.js";
import { copyCanvas, copyText } from "./clipboard.js";

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
const BALLOON = {
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
};
// The pen stroke beside loose lettering.
const STROKE = { pad: 0.35, length: 1.2, line: 0.12 };
// Clearance between text and artwork: loose lettering can come close;
// lettering in a balloon leaves room for the balloon and a short tail.
const ART_MARGIN = 0.4;
const BALLOON_MARGIN = BALLOON.padX + 0.8;

const DEFAULTS = [
  "Playing a record? I'll show you something interesting.",
  "There are two types of websites: ones with a backend, and ones " +
    "without. Everything falls into one of these two categories. " +
    "Your bank? Backend. A recipe blog? No backend.",
  "This meme generator? No backend.\n\nDespite all the text flowing " +
    "around the panels, it's just a static page.",
  "Yeah...",
];
// Dad's lines in panels 1-3, then Calvin's reply in panel 2.
const CALVIN = 3;
// Calvin's reply is widened rather than going over this many lines.
const CALVIN_MAX_LINES = 4;

const $ = (id) => document.getElementById(id);
const textareas = [$("text1"), $("text2"), $("text3"), $("text4")];
const canvas = $("canvas");
const ctx = canvas.getContext("2d");

let assets = null;
let images = null;
let texts = [...DEFAULTS];

// --- Texts <-> URL -------------------------------------------------------

function encodeTexts(t) {
  const bytes = new TextEncoder().encode(JSON.stringify({ texts: t }));
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function textsFromUrl() {
  const hash = location.hash.slice(1);
  if (!hash) return null;
  try {
    const base64 = hash.replace(/-/g, "+").replace(/_/g, "/");
    const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    if (!Array.isArray(parsed.texts)) return null;
    // Links made before Calvin's reply was editable have three texts.
    return DEFAULTS.map((t, i) => String(parsed.texts[i] ?? t));
  } catch {
    return null;
  }
}

function saveToUrl() {
  history.replaceState(null, "", "#" + encodeTexts(texts));
}

// --- Measuring -----------------------------------------------------------

function fontString(size) {
  return `${size}px "${FONT}", cursive`;
}

const widthCache = new Map();

function measure(text, size) {
  const key = `${size}\u0000${text}`;
  let width = widthCache.get(key);
  if (width === undefined) {
    ctx.font = fontString(size);
    width = ctx.measureText(text).width;
    if (widthCache.size > 50000) widthCache.clear();
    widthCache.set(key, width);
  }
  return width;
}

// Height of the font's capitals as a fraction of its size.
function capRatio() {
  ctx.font = fontString(100);
  return ctx.measureText("H").actualBoundingBoxAscent / 100;
}

// The font size whose capitals match Watterson's lettering in the strip.
function lettering() {
  const panelWidth =
    assets.panels.reduce((sum, p) => sum + p.width, 0) / assets.panels.length;
  const cap = (assets.capHeight * CELL_WIDTH) / panelWidth;
  return { cap, fontSize: cap / capRatio() };
}

function setStatus(message, warning = false) {
  $("status").textContent = message;
  $("status").classList.toggle("warning", warning);
}

// --- Layout --------------------------------------------------------------

// Calvin's reply, lettered in a column just above his head in panel 2. It
// grows upwards, and the space it takes (with its balloon) is reserved so
// that Dad's text flows around it.
function layoutCalvin(meta, fontSize, cap) {
  const [x0, x1, bottom] = meta.calvinColumn;
  const scale = CELL_WIDTH / meta.width;
  const side = (SIDE_GAP * cap) / scale;
  const padX = (BALLOON.padX * cap) / scale;
  const padY = (BALLOON.padY * cap) / scale;
  const lay = (width) =>
    layoutColumn(texts[CALVIN].toUpperCase(), {
      measure,
      fontSize,
      lineHeight: LINE_HEIGHT,
      width: width * scale,
    });
  // The open space, beside Dad's head, that a column `height` tall can use.
  const room = (height) => {
    const [a, b] = openSpan(meta, bottom - height / scale, bottom, (x0 + x1) / 2);
    return [Math.max(a, side) + padX, Math.min(b, meta.width - side) - padX];
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

// The stretch of open space (in art pixels) containing x = `centre` on
// every row from y0 to y1, ignoring rows above the art.
function openSpan(meta, y0, y1, centre) {
  let span = [0, meta.width];
  for (let row = Math.max(0, Math.floor(y0)); row < Math.min(meta.height, Math.ceil(y1)); row++) {
    const here = (meta.open[row] ?? []).find(([a, b]) => a <= centre && centre < b);
    if (!here) return [centre, centre];
    span = [Math.max(span[0], here[0]), Math.min(span[1], here[1])];
  }
  return span;
}

function computeLayout() {
  const { cap, fontSize } = lettering();
  const calvinMeta = assets.panels.find((p) => p.calvinColumn);
  const calvin = layoutCalvin(calvinMeta, fontSize, cap);
  const specs = assets.panels.map((p) => ({
    width: p.width,
    height: p.height,
    free: p.free ?? [],
    reserved: p === calvinMeta ? calvin.reserved : [],
    margin: (p.speech === "balloon" ? BALLOON_MARGIN : ART_MARGIN) * cap,
    awayFromArt: p.speech === "balloon",
  }));
  // The gaps are measured to the lettering itself, which sits in the middle
  // of its line's spacing.
  const leading = (LINE_HEIGHT * fontSize - cap) / 2;
  const result = fitPanels(specs, [...texts.slice(0, 3).map((t) => t.toUpperCase()), ""], {
    measure,
    fontSize,
    lineHeight: LINE_HEIGHT,
    margin: ART_MARGIN * cap,
    align: "left",
    cellWidth: CELL_WIDTH,
    padding: { x: SIDE_GAP * cap, y: Math.max(0, TOP_GAP * cap - leading) },
  });

  // Place Calvin's lines in the panel, now that its size is known.
  const index = assets.panels.indexOf(calvinMeta);
  const panel = result.panels[index];
  const [, , bottom] = calvinMeta.calvinColumn;
  const left = calvin.column.left * panel.scale;
  const top = panel.artTop + bottom * panel.scale - calvin.column.height;
  result.calvin = {
    panel: index,
    layout: {
      fontSize,
      lineHeight: calvin.column.lineHeight,
      lines: calvin.column.lines.map((l) => ({ ...l, x: left + l.x, y: top + l.y })),
    },
  };
  return result;
}

// --- Drawing -------------------------------------------------------------

function drawLines(layout) {
  ctx.font = fontString(layout.fontSize);
  ctx.fillStyle = INK;
  ctx.textBaseline = "alphabetic";
  // Centre the capital letters vertically in each line box.
  const capHeight = ctx.measureText("H").actualBoundingBoxAscent;
  for (const line of layout.lines) {
    ctx.fillText(line.text, line.x, line.y + (line.height + capHeight) / 2);
  }
}

function speakerPoint(panel, point) {
  return [point[0] * panel.scale, panel.artTop + point[1] * panel.scale];
}

// Lettering without a balloon gets a quick pen stroke towards the speaker,
// finding its way round the art the way a balloon's tail does: it's a tail
// for an invisible box round the text, drawn as a single line.
function drawStroke(layout, panel, meta, speaker, cap) {
  const pad = STROKE.pad * cap;
  const x0 = Math.min(...layout.lines.map((l) => l.x)) - pad;
  const x1 = Math.max(...layout.lines.map((l) => l.x + l.width)) + pad;
  const y0 = Math.min(...layout.lines.map((l) => l.y)) - pad;
  const y1 = Math.max(...layout.lines.map((l) => l.y + l.height)) + pad;
  const box = [
    [x0, y0],
    [x1, y0],
    [x1, y1],
    [x0, y1],
  ];
  const tail = balloonTail(box, speakerPoint(panel, speaker), {
    width: 0.2 * cap,
    maxLength: STROKE.length * cap,
    minLength: 0.4 * cap,
    gap: BALLOON.tailGap * cap,
    isFree: (p) => openAt(panel, meta, p),
  });
  if (!tail) return;
  const [b1, b2] = tail.base;
  ctx.beginPath();
  ctx.moveTo((b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2);
  ctx.quadraticCurveTo(...tail.bend, ...tail.tip);
  ctx.strokeStyle = INK;
  ctx.lineWidth = STROKE.line * cap;
  ctx.lineCap = "round";
  ctx.stroke();
}

// Whether a point in a cell is clear of the panel's artwork (points outside
// the panel aren't).
function openAt(panel, meta, [x, y]) {
  if (x < 0 || x > panel.width || y < 0 || y > panel.height) return false;
  if (y < panel.artTop) return true;
  const row = meta.open?.[Math.floor((y - panel.artTop) / panel.scale)];
  if (!row) return false;
  const gx = x / panel.scale;
  return row.some(([a, b]) => gx >= a && gx < b);
}

function polygonPath(points) {
  ctx.moveTo(...points[0]);
  for (const p of points.slice(1)) ctx.lineTo(...p);
  ctx.closePath();
}

// A tail as a narrow wedge along its curved centre line: each side curves
// from one end of the base to the tip, alongside the centre line.
function tailPath({ base: [b1, b2], bend, tip }) {
  const mid = [(b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2];
  const side = (b) => [bend[0] + (b[0] - mid[0]) / 2, bend[1] + (b[1] - mid[1]) / 2];
  ctx.moveTo(...b1);
  ctx.quadraticCurveTo(...side(b1), ...tip);
  ctx.quadraticCurveTo(...side(b2), ...b2);
  ctx.closePath();
}

// The balloons for one panel: `speeches` is a list of {layout, speaker}.
// All outlines are stroked at double width and then all are filled white,
// which leaves just the outer edge of their union: balloons that touch
// merge, and each tail opens into its balloon.
function drawBalloons(panel, meta, speeches, cap) {
  const shapes = [];
  const isFree = (p) => openAt(panel, meta, p);
  // Whatever of a balloon lies outside the panel is cut off by its border.
  const inside = ([x, y]) => x >= 0 && x <= panel.width && y >= 0 && y <= panel.height;
  for (const { layout, speaker } of speeches) {
    if (!layout.lines.length) continue;
    const outline = balloonOutline(layout.lines, {
      padX: BALLOON.padX * cap,
      padY: BALLOON.padY * cap,
      radius: BALLOON.radius * cap,
      roundness: BALLOON.roundness,
      ovalLines: 1,
      isFree: (p) => !inside(p) || isFree(p),
      panel: { x0: 0, y0: 0, x1: panel.width, y1: panel.height, reach: BALLOON.reach * cap },
    });
    shapes.push(outline);
    const tail = balloonTail(outline, speakerPoint(panel, speaker), {
      width: BALLOON.tailWidth * cap,
      maxLength: BALLOON.tailLength * cap,
      minLength: BALLOON.tailMinLength * cap,
      gap: BALLOON.tailGap * cap,
      blockedPenalty: 2 * cap,
      clearSight: 1.5 * cap,
      isFree,
    });
    if (tail) shapes.push(tail);
  }
  const trace = (shape) => {
    ctx.beginPath();
    if (Array.isArray(shape)) polygonPath(shape);
    else tailPath(shape);
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

function render() {
  if (!assets) return;
  const { cap } = lettering();
  const result = computeLayout();
  const { cellHeight } = result;
  canvas.width = OUTER * 2 + CELL_WIDTH * 2 + GUTTER;
  canvas.height = Math.ceil(OUTER * 2 + cellHeight * 2 + GUTTER);

  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  result.panels.forEach((panel, i) => {
    const meta = assets.panels[i];
    const speeches = [];
    if (meta.speakers.dad) {
      speeches.push({ layout: result.layouts[i], speaker: meta.speakers.dad });
    }
    if (result.calvin.panel === i) {
      speeches.push({ layout: result.calvin.layout, speaker: meta.speakers.calvin });
    }
    const x = OUTER + (i % 2) * (CELL_WIDTH + GUTTER);
    const y = OUTER + Math.floor(i / 2) * (cellHeight + GUTTER);

    ctx.save();
    ctx.translate(x, y);
    ctx.beginPath();
    ctx.rect(0, 0, CELL_WIDTH, cellHeight);
    ctx.clip();
    ctx.fillStyle = meta.background;
    ctx.fillRect(0, 0, CELL_WIDTH, cellHeight);
    if (meta.speech === "balloon") drawBalloons(panel, meta, speeches, cap);
    // Where the art is black ink on white, multiplying it in keeps every
    // line of it visible even where a balloon overlaps it.
    if (meta.background === "#fff") ctx.globalCompositeOperation = "multiply";
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(images[i], 0, panel.artTop, CELL_WIDTH, meta.height * panel.scale);
    ctx.globalCompositeOperation = "source-over";
    for (const { layout, speaker } of speeches) {
      drawLines(layout);
      if (meta.speech === "loose" && layout.lines.length) {
        drawStroke(layout, panel, meta, speaker, cap);
      }
    }
    ctx.restore();

    ctx.strokeStyle = INK;
    ctx.lineWidth = BORDER;
    ctx.strokeRect(x, y, CELL_WIDTH, cellHeight);
  });

  setStatus(result.fits ? "" : "Some of that text doesn't fit.", !result.fits);
}

let pending = false;
function scheduleRender() {
  if (pending) return;
  pending = true;
  requestAnimationFrame(() => {
    pending = false;
    render();
  });
}

function showTexts() {
  textareas.forEach((t, i) => (t.value = texts[i]));
}

function onInput() {
  texts = textareas.map((t) => t.value);
  saveToUrl();
  scheduleRender();
}

// --- Actions -------------------------------------------------------------

function canvasBlob() {
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

function flash(button, text) {
  const original = button.dataset.label ?? button.textContent;
  button.dataset.label = original;
  button.textContent = text;
  clearTimeout(button._timer);
  button._timer = setTimeout(() => (button.textContent = original), 1600);
}

async function download() {
  render();
  const blob = await canvasBlob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "two-types-of-things.png";
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function copyImage() {
  try {
    render();
    await copyCanvas(canvas);
    flash($("copy-image"), "Copied!");
    setStatus("");
  } catch (error) {
    console.error("Couldn't copy the image:", error);
    flash($("copy-image"), "Couldn't copy");
    setStatus(
      "This browser won't let the page copy the image. Use Download PNG, or right-click the comic and copy it from there.",
      true,
    );
  }
}

async function copyLink() {
  saveToUrl();
  try {
    await copyText(location.href);
    flash($("copy-link"), "Copied!");
  } catch (error) {
    console.error("Couldn't copy the link:", error);
    flash($("copy-link"), "Couldn't copy");
  }
}

// --- Start up ------------------------------------------------------------

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

async function main() {
  texts = textsFromUrl() ?? texts;
  showTexts();

  for (const t of textareas) t.addEventListener("input", onInput);
  $("download").addEventListener("click", download);
  $("copy-image").addEventListener("click", copyImage);
  $("copy-link").addEventListener("click", copyLink);
  $("reset").addEventListener("click", () => {
    texts = [...DEFAULTS];
    showTexts();
    history.replaceState(null, "", location.pathname);
    scheduleRender();
  });
  window.addEventListener("hashchange", () => {
    const fromUrl = textsFromUrl();
    if (fromUrl) {
      texts = fromUrl;
      showTexts();
      scheduleRender();
    }
  });

  const response = await fetch("assets/panels.json");
  assets = await response.json();
  images = await Promise.all(assets.panels.map((p) => loadImage(p.image)));
  try {
    await document.fonts.load(`20px "${FONT}"`, "AB");
  } catch {
    // Render with whatever the browser has rather than nothing.
  }
  render();
}

main().catch((error) => {
  console.error(error);
  setStatus("Something went wrong loading the comic.", true);
});
