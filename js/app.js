import { fitPanels, tailFor } from "./layout.js";
import { balloonOutline, balloonTail } from "./balloon.js";

const CELL_WIDTH = 800;
const GUTTER = 30;
const OUTER = 30;
const PADDING = 20;
const BORDER = 5;
const INK = "#111";

// Speech balloon proportions, in multiples of the lettering's cap height,
// measured from the strip.
const BALLOON = {
  padX: 0.55,
  padY: 0.3,
  radius: 0.6,
  line: 0.1,
  tailWidth: 0.6,
  tailLength: 2.4,
  tailGap: 0.45,
};

const FONTS = [
  { family: "Dad Lettering", label: "Watterson-style (from the strips)" },
  { family: "Patrick Hand SC", label: "Patrick Hand SC" },
  { family: "Gochi Hand", label: "Gochi Hand" },
  { family: "Schoolbell", label: "Schoolbell" },
  { family: "Kalam", label: "Kalam" },
  { family: "Short Stack", label: "Short Stack" },
  { family: "Architects Daughter", label: "Architects Daughter" },
  { family: "Comic Neue", label: "Comic Neue" },
  { family: "Noto Sans Mono", label: "Monospace (classic meme)" },
];
const UPLOADED_FONT = "Uploaded Font";

const DEFAULTS = {
  // Dad's lines in panels 1-3, then Calvin's reply in panel 2.
  texts: [
    "Playing a record? I'll show you something interesting.",
    "There are two types of websites: ones with a backend, and ones " +
      "without. Everything falls into one of these two categories. " +
      "Your bank? Backend. A recipe blog? No backend.",
    "This meme generator? No backend.\n\nDespite all the text flowing " +
      "around the panels, it's just a static page.",
    "Yeah...",
  ],
  font: "Dad Lettering",
  // Percentage of the size of Watterson's lettering in the strip.
  scale: 100,
  weight: 0,
  spacing: 1.1,
  align: "center",
  caps: true,
  speech: "balloons",
  mode: "grow",
  valign: "top",
  headroom: 0,
};
const CALVIN = 3;

const $ = (id) => document.getElementById(id);
const textareas = [$("text1"), $("text2"), $("text3"), $("text4")];
const canvas = $("canvas");
const ctx = canvas.getContext("2d");

let assets = null;
let images = null;
let state = { ...DEFAULTS, texts: [...DEFAULTS.texts] };

// --- State <-> URL -------------------------------------------------------

function encodeState(s) {
  const bytes = new TextEncoder().encode(JSON.stringify(s));
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function decodeState(hash) {
  try {
    const base64 = hash.replace(/-/g, "+").replace(/_/g, "/");
    const binary = atob(base64);
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    const merged = { ...DEFAULTS, ...parsed };
    if (!Array.isArray(merged.texts) || merged.texts.length < 3) {
      merged.texts = [...DEFAULTS.texts];
    }
    // Links made before Calvin's reply was editable have three texts.
    merged.texts = DEFAULTS.texts.map((t, i) => String(merged.texts[i] ?? t));
    return merged;
  } catch {
    return null;
  }
}

function stateFromUrl() {
  const hash = location.hash.slice(1);
  return hash ? decodeState(hash) : null;
}

function saveToUrl() {
  const shareable = { ...state };
  if (shareable.font === UPLOADED_FONT) shareable.font = DEFAULTS.font;
  history.replaceState(null, "", "#" + encodeState(shareable));
}

// --- Controls ------------------------------------------------------------

function populateFonts() {
  const select = $("font");
  for (const { family, label } of FONTS) {
    const option = document.createElement("option");
    option.value = family;
    option.textContent = label;
    option.style.fontFamily = `"${family}"`;
    select.append(option);
  }
}

function showState() {
  textareas.forEach((t, i) => (t.value = state.texts[i]));
  if (![...$("font").options].some((o) => o.value === state.font)) {
    state.font = DEFAULTS.font;
  }
  $("font").value = state.font;
  $("size").value = state.scale;
  $("weight").value = state.weight;
  $("spacing").value = state.spacing;
  $("align").value = state.align;
  $("caps").checked = state.caps;
  $("speech").value = state.speech;
  $("mode").value = state.mode;
  $("valign").value = state.valign;
  $("headroom").value = state.headroom;
  showValues();
}

function showValues() {
  $("size-value").textContent = `${state.scale}%`;
  $("weight-value").textContent = state.weight.toFixed(2);
  $("spacing-value").textContent = state.spacing.toFixed(2);
  $("headroom-value").textContent = `${state.headroom}px`;
}

function readControls() {
  state.texts = textareas.map((t) => t.value);
  state.font = $("font").value;
  state.scale = Number($("size").value);
  state.weight = Number($("weight").value);
  state.spacing = Number($("spacing").value);
  state.align = $("align").value;
  state.caps = $("caps").checked;
  state.speech = $("speech").value;
  state.mode = $("mode").value;
  state.valign = $("valign").value;
  state.headroom = Number($("headroom").value);
  showValues();
}

// --- Measuring -----------------------------------------------------------

function fontString(size) {
  // Dad Lettering only covers what appears in the strips; anything else
  // falls back to the closest-looking web font.
  return `${size}px "${state.font}", "Patrick Hand SC", cursive`;
}

const widthCache = new Map();

function measure(text, size) {
  const key = `${state.font}\u0000${size}\u0000${text}`;
  let width = widthCache.get(key);
  if (width === undefined) {
    ctx.font = fontString(size);
    width = ctx.measureText(text).width;
    if (widthCache.size > 50000) widthCache.clear();
    widthCache.set(key, width);
  }
  // Stroking the letters to thicken them makes them a little wider.
  return width + state.weight;
}

// Height of the font's capitals as a fraction of its size.
function capRatio() {
  ctx.font = fontString(100);
  return ctx.measureText("H").actualBoundingBoxAscent / 100;
}

// The font size whose capitals match Watterson's lettering in the strip,
// scaled by the size setting.
function fontSizeForScale() {
  const panelScale =
    CELL_WIDTH / (assets.panels.reduce((sum, p) => sum + p.width, 0) / assets.panels.length);
  return (assets.capHeight * panelScale * (state.scale / 100)) / capRatio();
}

function displayText(text) {
  return state.caps ? text.toUpperCase() : text;
}

function setStatus(message, warning = false) {
  $("status").textContent = message;
  $("status").classList.toggle("warning", warning);
}

// --- Layout --------------------------------------------------------------

// Clearance between text and artwork. Balloons may overlap the art a
// little, as they do in the strips, so this needn't leave room for them.
function artMargin(cap) {
  return 0.4 * cap;
}

function layoutOptions(fontSize) {
  const cap = fontSize * capRatio();
  return {
    measure,
    fontSize,
    lineHeight: state.spacing,
    margin: artMargin(cap),
    align: state.align,
    cellWidth: CELL_WIDTH,
    padding: PADDING,
    valign: state.valign,
    minFontSize: 8,
  };
}

function computeLayout() {
  const specs = assets.panels.map((p) => ({
    width: p.width,
    height: p.height,
    free: p.free ?? [],
  }));
  const texts = [...state.texts.slice(0, 3).map(displayText), ""];
  const result = fitPanels(specs, texts, {
    ...layoutOptions(fontSizeForScale()),
    mode: state.mode,
    headroom: state.headroom,
  });
  result.calvin = layoutCalvin(result);
  return result;
}

// Calvin's reply goes where his balloon was in the strip, centred, and is
// made smaller if it doesn't fit there.
function layoutCalvin(result) {
  const meta = assets.panels[1];
  const [x0, y0, x1, y1] = meta.calvinRegion;
  const spec = {
    width: meta.width,
    height: meta.height,
    headroomFree: false,
    free: Array.from({ length: meta.height }, (_, row) =>
      row >= y0 && row < y1 ? [[x0, x1]] : [],
    ),
  };
  const artHeight = result.panels[1].height - result.panels[1].artTop;
  const options = layoutOptions(result.fontSize);
  return fitPanels([spec], [displayText(state.texts[CALVIN])], {
    ...options,
    // Inside his region, only the balloon itself needs room.
    margin: state.speech === "balloons" ? BALLOON.padX * result.fontSize * capRatio() : 0,
    align: "center",
    padding: 0,
    mode: "shrink",
    valign: "middle",
    headroom: result.cellHeight - artHeight,
  });
}

// --- Drawing -------------------------------------------------------------

function drawLines(layout) {
  ctx.font = fontString(layout.fontSize);
  ctx.fillStyle = INK;
  ctx.strokeStyle = INK;
  ctx.lineJoin = "round";
  ctx.lineWidth = state.weight;
  ctx.textBaseline = "alphabetic";
  // Centre the capital letters vertically in each line box.
  const capHeight = ctx.measureText("H").actualBoundingBoxAscent;
  for (const line of layout.lines) {
    const baseline = line.y + (line.height + capHeight) / 2;
    const x = line.x + state.weight / 2;
    ctx.fillText(line.text, x, baseline);
    if (state.weight > 0) ctx.strokeText(line.text, x, baseline);
  }
}

function speakerPoint(panel, point) {
  return [point[0] * panel.scale, panel.artTop + point[1] * panel.scale];
}

function drawTail(layout, panel, speaker) {
  const fontSize = layout.fontSize;
  const tail = tailFor(layout, speakerPoint(panel, speaker), {
    gap: fontSize * 0.35,
    maxLength: fontSize * 1.4,
  });
  if (!tail) return;
  const [x0, y0] = tail.from;
  const [x1, y1] = tail.to;
  // A slight bow, as if drawn with a quick flick of the pen.
  const bow = 0.12;
  const cx = (x0 + x1) / 2 - (y1 - y0) * bow;
  const cy = (y0 + y1) / 2 + (x1 - x0) * bow;
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.quadraticCurveTo(cx, cy, x1, y1);
  ctx.strokeStyle = INK;
  ctx.lineWidth = Math.max(2.5, fontSize * 0.09);
  ctx.lineCap = "round";
  ctx.stroke();
}

// Whether a point in a cell is clear of the panel's artwork.
function openAt(panel, meta, [x, y]) {
  if (y < panel.artTop) return x >= 0 && x <= panel.width;
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

function tailPath({ base: [b1, b2], tip }) {
  // Both sides bow the same way, giving the tail a slight curve.
  const bend = (from, amount) => {
    const dx = tip[0] - from[0];
    const dy = tip[1] - from[1];
    return [from[0] + dx / 2 - dy * amount, from[1] + dy / 2 + dx * amount];
  };
  ctx.moveTo(...b1);
  ctx.quadraticCurveTo(...bend(b1, 0.12), ...tip);
  ctx.quadraticCurveTo(...bend(b2, 0.12), ...b2);
  ctx.closePath();
}

// The balloons for one panel: `speeches` is a list of {layout, speaker}.
// All outlines are stroked at double width and then all are filled white,
// which leaves just the outer edge of their union: balloons that touch
// merge, and each tail opens into its balloon.
function drawBalloons(panel, meta, speeches) {
  const shapes = [];
  const isFree = (p) => openAt(panel, meta, p);
  for (const { layout, speaker } of speeches) {
    if (!layout.lines.length) continue;
    const cap = layout.fontSize * capRatio();
    const outline = balloonOutline(layout.lines, {
      padX: BALLOON.padX * cap,
      padY: BALLOON.padY * cap,
      radius: BALLOON.radius * cap,
      isFree,
    });
    shapes.push({ outline, cap });
    if (!speaker) continue;
    const target = speakerPoint(panel, speaker);
    const tail = balloonTail(outline, target, {
      width: BALLOON.tailWidth * cap,
      maxLength: BALLOON.tailLength * cap,
      gap: BALLOON.tailGap * cap,
      isFree,
    });
    if (tail) shapes.push({ tail, cap });
  }
  if (!shapes.length) return;
  const trace = (shape) => {
    ctx.beginPath();
    if (shape.outline) polygonPath(shape.outline);
    else tailPath(shape.tail);
  };
  ctx.lineJoin = "round";
  ctx.strokeStyle = INK;
  for (const shape of shapes) {
    trace(shape);
    ctx.lineWidth = 2 * BALLOON.line * shape.cap;
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
    if (meta.speakers.calvin) {
      speeches.push({ layout: result.calvin.layouts[0], speaker: meta.speakers.calvin });
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
    if (state.speech === "balloons") drawBalloons(panel, meta, speeches);
    // Where the art is black ink on white, multiplying it in keeps every
    // line of it visible even where a balloon overlaps it.
    if (meta.background === "#fff") ctx.globalCompositeOperation = "multiply";
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(images[i], 0, panel.artTop, CELL_WIDTH, meta.height * panel.scale);
    ctx.globalCompositeOperation = "source-over";
    for (const { layout, speaker } of speeches) {
      drawLines(layout);
      if (state.speech === "tails" && layout.lines.length) {
        drawTail(layout, panel, speaker);
      }
    }
    ctx.restore();

    ctx.strokeStyle = INK;
    ctx.lineWidth = BORDER;
    ctx.strokeRect(x, y, CELL_WIDTH, cellHeight);
  });

  const requested = fontSizeForScale();
  if (!result.fits) {
    setStatus(
      state.mode === "shrink"
        ? "That's too much text even at the smallest size. Add some extra space or let the panels grow."
        : "Some text doesn't fit. Try shorter words or a smaller size.",
      true,
    );
  } else if (!result.calvin.fits) {
    setStatus("Calvin's reply is too long to fit in his corner of the panel.", true);
  } else if (state.mode === "shrink" && result.fontSize < requested - 0.01) {
    const shrunk = Math.round((state.scale * result.fontSize) / requested);
    setStatus(`Text shrunk to ${shrunk}% to fit.`);
  } else {
    setStatus("");
  }
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

function onChange() {
  readControls();
  saveToUrl();
  scheduleRender();
}

async function ensureFontLoaded() {
  if (state.font === UPLOADED_FONT) return;
  try {
    await document.fonts.load(`20px "${state.font}"`, "AaBb");
  } catch {
    // Fall back to whatever the browser has; still render something.
  }
}

async function onFontChange() {
  readControls();
  saveToUrl();
  await ensureFontLoaded();
  widthCache.clear();
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
    await navigator.clipboard.write([
      new ClipboardItem({ "image/png": canvasBlob() }),
    ]);
    flash($("copy-image"), "Copied!");
  } catch {
    flash($("copy-image"), "Couldn't copy");
  }
}

async function copyLink() {
  saveToUrl();
  try {
    await navigator.clipboard.writeText(location.href);
    flash($("copy-link"), "Copied!");
  } catch {
    flash($("copy-link"), "Couldn't copy");
  }
}

async function useUploadedFont(file) {
  try {
    const face = new FontFace(UPLOADED_FONT, await file.arrayBuffer());
    await face.load();
    document.fonts.add(face);
    const select = $("font");
    let option = [...select.options].find((o) => o.value === UPLOADED_FONT);
    if (!option) {
      option = document.createElement("option");
      option.value = UPLOADED_FONT;
      select.append(option);
    }
    option.textContent = `Uploaded: ${file.name}`;
    select.value = UPLOADED_FONT;
    await onFontChange();
  } catch {
    setStatus("Couldn't read that font file.", true);
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
  populateFonts();
  state = stateFromUrl() ?? state;
  showState();

  for (const t of textareas) t.addEventListener("input", onChange);
  for (const id of ["size", "weight", "spacing", "headroom"]) {
    $(id).addEventListener("input", onChange);
  }
  for (const id of ["align", "caps", "speech", "mode", "valign"]) {
    $(id).addEventListener("change", onChange);
  }
  $("font").addEventListener("change", onFontChange);
  $("font-file").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) useUploadedFont(file);
  });
  $("download").addEventListener("click", download);
  $("copy-image").addEventListener("click", copyImage);
  $("copy-link").addEventListener("click", copyLink);
  $("reset").addEventListener("click", async () => {
    state = { ...DEFAULTS, texts: [...DEFAULTS.texts] };
    showState();
    history.replaceState(null, "", location.pathname);
    await onFontChange();
  });
  window.addEventListener("hashchange", async () => {
    const fromUrl = stateFromUrl();
    if (fromUrl) {
      state = fromUrl;
      showState();
      await onFontChange();
    }
  });

  const response = await fetch("assets/panels.json");
  assets = await response.json();
  images = await Promise.all(assets.panels.map((p) => loadImage(p.image)));
  await ensureFontLoaded();
  // Fonts other than the selected one may finish loading later.
  document.fonts.addEventListener("loadingdone", () => {
    widthCache.clear();
    scheduleRender();
  });
  render();
}

main().catch((error) => {
  console.error(error);
  setStatus("Something went wrong loading the comic.", true);
});
