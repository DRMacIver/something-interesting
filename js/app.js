import { DEFAULTS, renderComic, loadComic } from "./comic.js";
import { copyCanvas, copyText } from "./clipboard.js";
import { encodeTexts, decodeTexts } from "./share.js";

const $ = (id) => document.getElementById(id);
const textareas = [$("text1"), $("text2"), $("text3"), $("text4")];
const canvas = $("canvas");

let comic = null;
let texts = [...DEFAULTS];

// --- Texts <-> URL -------------------------------------------------------

function textsFromUrl() {
  return decodeTexts(location.hash.slice(1), DEFAULTS);
}

function saveToUrl() {
  const hash = encodeTexts(texts);
  try {
    history.replaceState(null, "", location.pathname + location.search + (hash === null ? "" : "#" + hash));
    return hash !== null;
  } catch {
    // URL limits and history throttling must not prevent preview rendering.
    return false;
  }
}

function setStatus(message, warning = false) {
  $("status").textContent = message;
  $("status").classList.toggle("warning", warning);
}

let renderRevision = 0;
let exportReady = false;
function setExportReady(ready) {
  exportReady = ready;
  $("download").disabled = !ready;
  $("copy-image").disabled = !ready;
}
async function render() {
  if (!comic) return;
  setExportReady(false);
  const revision = ++renderRevision;
  const report = await renderComic(canvas, comic, [...texts], () => revision === renderRevision).catch(error => {
    if (revision !== renderRevision) return null;
    throw error;
  });
  if (!report) return false;
  setExportReady(true);
  const { fits, clipped } = report;
  if (!fits) setStatus("Some of that text doesn't fit.", true);
  else if (clipped.length) {
    setStatus("That’s a lot! Long boxes are shortened in the image; your text is kept above.", true);
  } else setStatus("");
  return true;
}

let pending = false;
function scheduleRender() {
  ++renderRevision;
  setExportReady(false);
  if (pending) return;
  pending = true;
  requestAnimationFrame(() => {
    pending = false;
    render().catch(error => {
      console.error(error);
      setStatus("Couldn’t load the lettering. Please try again.", true);
    });
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
  if (!exportReady) return;
  const blob = await canvasBlob();
  if (!blob) {
    setStatus("This browser couldn’t export the image. Try shortening the longest box.", true);
    return;
  }
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
    if (!exportReady) return;
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
  if (!saveToUrl()) {
    setStatus("This text is too long to share as a link in this browser. You can still download the image.", true);
    return;
  }
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
  setExportReady(false);
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
  await render();
}

main().catch((error) => {
  console.error(error);
  setStatus("Something went wrong loading the comic.", true);
});
