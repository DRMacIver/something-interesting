// Sharing keeps the full original text, independently of image truncation.
// Bound serialization before allocating UTF-8/base64 buffers for huge pastes.
export const MAX_SHARE_TEXT = 250_000;
const MAX_SHARE_HASH = 2_000_000;

export function encodeTexts(texts) {
  if (texts.reduce((n, text) => n + text.length, 0) > MAX_SHARE_TEXT) return null;
  const bytes = new TextEncoder().encode(JSON.stringify({texts}));
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function decodeTexts(hash, defaults) {
  if (!hash || hash.length > MAX_SHARE_HASH) return null;
  try {
    const bytes = Uint8Array.from(atob(hash.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    if (!Array.isArray(parsed.texts)) return null;
    // Older links contain Dad's three texts only.
    const texts = defaults.map((text, i) => String(parsed.texts[i] ?? text));
    return texts.reduce((n, text) => n + text.length, 0) <= MAX_SHARE_TEXT ? texts : null;
  } catch {
    return null;
  }
}
