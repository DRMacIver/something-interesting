import { loadComic, renderComic } from "./comic.js";
import { encodeTexts } from "./share.js";
import { categories, samples } from "./unicode-samples.js";

const gallery = document.querySelector("#gallery");
const filters = document.querySelector("#filters");
const search = document.querySelector("#search");
const summary = document.querySelector("#summary");
const empty = document.querySelector("#empty");
const cards = [];
const queue = [];
let category = "All";
let working = false;
let comicPromise;

function comic() {
  return comicPromise ??= loadComic("./").catch(error => {
    comicPromise = null;
    throw error;
  });
}

function updateSummary() {
  const visible = cards.filter(card => !card.element.hidden);
  const ready = visible.filter(card => card.ready).length;
  summary.textContent = `${visible.length} examples · ${ready} ready. Examples load as you scroll.`;
  empty.hidden = visible.length !== 0;
}

function png(canvas) {
  return new Promise((resolve, reject) => canvas.toBlob(blob => {
    if (blob) resolve(blob);
    else reject(new Error("Could not create the comic image"));
  }, "image/png"));
}

async function render(card) {
  card.status.textContent = "Rendering comic…";
  card.retry.hidden = true;
  const full = document.createElement("canvas");
  const preview = document.createElement("canvas");
  try {
    const report = await renderComic(full, await comic(), card.sample.texts);
    const original = await png(full);
    preview.width = Math.min(1200, full.width);
    preview.height = Math.round(full.height * preview.width / full.width);
    const context = preview.getContext("2d");
    context.imageSmoothingQuality = "high";
    context.drawImage(full, 0, 0, preview.width, preview.height);
    const thumbnail = await png(preview);
    card.image.width = preview.width;
    card.image.height = preview.height;
    card.image.src = URL.createObjectURL(thumbnail);
    card.image.hidden = false;
    card.download.href = URL.createObjectURL(original);
    card.download.hidden = false;
    card.ready = true;
    card.placeholder.hidden = true;
    if (report.unmappedCodepoints?.length) {
      card.status.textContent = "Some characters could not be loaded. You can retry this example.";
      card.retry.hidden = false;
    } else {
      card.status.textContent = "";
    }
  } catch (error) {
    console.error(`Could not render ${card.sample.id}`, error);
    card.status.textContent = "This example couldn’t be rendered. Please try again.";
    card.retry.hidden = false;
  } finally {
    full.width = full.height = preview.width = preview.height = 0;
    updateSummary();
  }
}

async function drain() {
  if (working) return;
  working = true;
  try {
    while (queue.length) {
      const card = queue.shift();
      if (!card.element.hidden) await render(card);
      card.queued = false;
    }
  } finally {
    working = false;
  }
}

function enqueue(card) {
  if (card.queued) return;
  card.queued = true;
  queue.push(card);
  void drain();
}

const observer = "IntersectionObserver" in window ? new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting || entry.target.hidden) continue;
    const card = cards.find(card => card.element === entry.target);
    observer.unobserve(entry.target);
    if (!card.ready) enqueue(card);
  }
}, { rootMargin: "400px" }) : null;

function applyFilter() {
  const query = search.value.normalize("NFKC").toLocaleLowerCase().trim();
  for (const card of cards) {
    card.element.hidden = (category !== "All" && category !== card.sample.category)
      || !card.searchText.includes(query);
    if (!card.element.hidden && !card.ready && !card.queued) {
      if (observer) observer.observe(card.element);
      else enqueue(card);
    }
  }
  for (const button of filters.children) button.setAttribute("aria-pressed", String(button.textContent === category));
  updateSummary();
}

for (const name of categories) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = name;
  button.addEventListener("click", () => { category = name; applyFilter(); });
  filters.append(button);
}

for (const sample of samples) {
  const element = document.createElement("article");
  element.className = "sample";
  element.id = sample.id;
  const heading = document.createElement("h2");
  heading.textContent = sample.title;
  const description = document.createElement("p");
  description.className = "description";
  description.textContent = sample.description;
  const placeholder = document.createElement("div");
  placeholder.className = "placeholder";
  placeholder.textContent = "Comic preview";
  placeholder.setAttribute("aria-hidden", "true");
  const image = document.createElement("img");
  image.hidden = true;
  image.decoding = "async";
  image.alt = `${sample.title}: a Calvin and Hobbes strip. Full dialogue is available below.`;
  const status = document.createElement("p");
  status.className = "sample-status";
  status.setAttribute("role", "status");
  const actions = document.createElement("div");
  actions.className = "sample-actions";
  const edit = document.createElement("a");
  edit.href = `index.html#${encodeTexts(sample.texts)}`;
  edit.textContent = "Edit this comic";
  const download = document.createElement("a");
  download.textContent = "Download PNG";
  download.download = `unicode-${sample.id}.png`;
  download.hidden = true;
  const retry = document.createElement("button");
  retry.type = "button";
  retry.textContent = "Retry";
  retry.hidden = true;
  const details = document.createElement("details");
  const label = document.createElement("summary");
  label.textContent = "Dialogue";
  details.append(label);
  sample.texts.forEach((text, i) => {
    const speaker = document.createElement("h3");
    speaker.textContent = i === 3 ? "Calvin · panel 2" : `Dad · panel ${i + 1}`;
    const line = document.createElement("pre");
    line.dir = "auto";
    line.textContent = text;
    details.append(speaker, line);
  });
  actions.append(edit, download, retry);
  element.append(heading, description, placeholder, image, status, actions, details);
  gallery.append(element);
  const card = { sample, element, image, placeholder, status, download, retry, ready: false, queued: false,
    searchText: [sample.title, sample.description, sample.category, ...sample.texts].join(" ").normalize("NFKC").toLocaleLowerCase() };
  retry.addEventListener("click", () => {
    if (card.queued) return;
    if (image.src) URL.revokeObjectURL(image.src);
    if (download.hasAttribute("href")) URL.revokeObjectURL(download.href);
    image.hidden = download.hidden = true;
    card.ready = false;
    enqueue(card);
  });
  cards.push(card);
}

search.addEventListener("input", applyFilter);
applyFilter();
