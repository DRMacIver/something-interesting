import { DEFAULTS, drawComic, loadComic } from "./comic.js";
import { copyCanvas, copyText } from "./clipboard.js";

const $ = (id) => document.getElementById(id);
const textareas = [$("text1"), $("text2"), $("text3"), $("text4")];
const canvas = $("canvas");

let comic = null;
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

function setStatus(message, warning = false) {
  $("status").textContent = message;
  $("status").classList.toggle("warning", warning);
}

function render() {
  if (!comic) return;
  const { fits } = drawComic(canvas, comic, texts);
  setStatus(fits ? "" : "Some of that text doesn't fit.", !fits);
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
    // Browsers only let pages use the clipboard over https or on localhost.
    const why = window.isSecureContext
      ? "This browser won't let the page copy the image."
      : "Browsers only let pages copy images when they're served over https or from localhost.";
    setStatus(`${why} Use Download PNG, or right-click the comic and copy it from there.`, true);
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

  comic = await loadComic();
  render();
}

main().catch((error) => {
  console.error(error);
  setStatus("Something went wrong loading the comic.", true);
});
