// Copying to the clipboard as reliably as browsers allow.

// A Blob of a data: URL's contents, made synchronously.
export function dataUrlToBlob(url) {
  const [header, data] = url.split(",");
  const type = header.slice("data:".length).split(";")[0];
  const binary = atob(data);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new Blob([bytes], { type });
}

// Copy a canvas's picture as a PNG. The PNG is made synchronously, so the
// clipboard gets it within the click that asked for it: some browsers
// refuse an image that's still being encoded once the click is over.
export async function copyCanvas(canvas) {
  if (!navigator.clipboard?.write || typeof ClipboardItem === "undefined") {
    throw new Error("This browser can't copy images from a page.");
  }
  const blob = dataUrlToBlob(canvas.toDataURL("image/png"));
  await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
}

// Copy some text, falling back to the old copy command where the page isn't
// allowed to use the clipboard API.
export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return;
  } catch (error) {
    const field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    document.body.append(field);
    field.select();
    const copied = document.execCommand("copy");
    field.remove();
    if (!copied) throw error;
  }
}
