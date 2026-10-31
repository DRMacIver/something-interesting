import { fitPanels, tailFor } from "./layout.js";

const CELL_WIDTH = 640;
const GUTTER = 24;
const OUTER = 24;
const PADDING = 16;
const ART_MARGIN = 10;
const BORDER = 4;
const INK = "#111";

const FONTS = [
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
  texts: [
    "Playing a record? I'll show you something interesting.",
    "There are two types of websites: ones with a backend, and ones " +
      "without. Everything falls into one of these two categories. " +
      "Your bank? Backend. A recipe blog? No backend.",
    "This meme generator? No backend.\n\nDespite all the text flowing " +
      "around the panels, it's just a static page.",
  ],
  font: "Patrick Hand SC",
  size: 40,
  weight: 0.75,
  spacing: 1.2,
  align: "center",
  caps: true,
  tails: true,
  mode: "grow",
  valign: "top",
  headroom: 0,
};

const $ = (id) => document.getElementById(id);
const textareas = [$("text1"), $("text2"), $("text3")];
const canvas = $("canvas");
const ctx = canvas.getContext("2d");

let panels = null;
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
    if (!Array.isArray(merged.texts) || merged.texts.length !== 3) {
      merged.texts = [...DEFAULTS.texts];
    }
    merged.texts = merged.texts.map((t) => String(t));
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
  $("size").value = state.size;
  $("weight").value = state.weight;
  $("spacing").value = state.spacing;
  $("align").value = state.align;
  $("caps").checked = state.caps;
  $("tails").checked = state.tails;
  $("mode").value = state.mode;
  $("valign").value = state.valign;
  $("headroom").value = state.headroom;
  showValues();
}

function showValues() {
  $("size-value").textContent = `${state.size}px`;
  $("weight-value").textContent = state.weight.toFixed(2);
  $("spacing-value").textContent = state.spacing.toFixed(2);
  $("headroom-value").textContent = `${state.headroom}px`;
}

function readControls() {
  state.texts = textareas.map((t) => t.value);
  state.font = $("font").value;
  state.size = Number($("size").value);
  state.weight = Number($("weight").value);
  state.spacing = Number($("spacing").value);
  state.align = $("align").value;
  state.caps = $("caps").checked;
  state.tails = $("tails").checked;
  state.mode = $("mode").value;
  state.valign = $("valign").value;
  state.headroom = Number($("headroom").value);
  showValues();
}

// --- Rendering -----------------------------------------------------------

function fontString(size) {
  return `${size}px "${state.font}", cursive`;
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

function displayText(text) {
  return state.caps ? text.toUpperCase() : text;
}

function setStatus(message, warning = false) {
  $("status").textContent = message;
  $("status").classList.toggle("warning", warning);
}

function computeLayout() {
  const specs = panels.map((p) => ({
    width: p.width,
    height: p.height,
    free: p.free ?? [],
  }));
  return fitPanels(specs, [...state.texts.map(displayText), ""], {
    measure,
    fontSize: state.size,
    lineHeight: state.spacing,
    margin: ART_MARGIN,
    align: state.align,
    cellWidth: CELL_WIDTH,
    padding: PADDING,
    mode: state.mode,
    valign: state.valign,
    headroom: state.headroom,
    minFontSize: 8,
  });
}

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

function drawTail(layout, panel, mouth) {
  const fontSize = layout.fontSize;
  const tail = tailFor(
    layout,
    [mouth[0] * panel.scale, panel.artTop + mouth[1] * panel.scale],
    { gap: fontSize * 0.35, maxLength: fontSize * 1.4 },
  );
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

function render() {
  if (!panels) return;
  const result = computeLayout();
  const { cellHeight } = result;
  canvas.width = OUTER * 2 + CELL_WIDTH * 2 + GUTTER;
  canvas.height = Math.ceil(OUTER * 2 + cellHeight * 2 + GUTTER);

  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  result.panels.forEach((panel, i) => {
    const meta = panels[i];
    const layout = result.layouts[i];
    const x = OUTER + (i % 2) * (CELL_WIDTH + GUTTER);
    const y = OUTER + Math.floor(i / 2) * (cellHeight + GUTTER);

    ctx.save();
    ctx.translate(x, y);
    ctx.beginPath();
    ctx.rect(0, 0, CELL_WIDTH, cellHeight);
    ctx.clip();
    ctx.fillStyle = meta.background;
    ctx.fillRect(0, 0, CELL_WIDTH, cellHeight);
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(
      images[i],
      0,
      panel.artTop,
      CELL_WIDTH,
      meta.height * panel.scale,
    );
    drawLines(layout);
    if (state.tails && meta.mouth && layout.lines.length) {
      drawTail(layout, panel, meta.mouth);
    }
    ctx.restore();

    ctx.strokeStyle = INK;
    ctx.lineWidth = BORDER;
    ctx.strokeRect(x, y, CELL_WIDTH, cellHeight);
  });

  if (!result.fits) {
    setStatus(
      state.mode === "shrink"
        ? "That's too much text even at the smallest size. Add some extra space or let the panels grow."
        : "Some text doesn't fit. Try shorter words or a smaller size.",
      true,
    );
  } else if (state.mode === "shrink" && result.fontSize < state.size) {
    setStatus(`Text shrunk to ${result.fontSize.toFixed(1)}px to fit.`);
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
  for (const id of ["align", "caps", "tails", "mode", "valign"]) {
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
  const data = await response.json();
  images = await Promise.all(data.panels.map((p) => loadImage(p.image)));
  panels = data.panels;
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
