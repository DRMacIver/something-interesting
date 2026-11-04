# Emoji preparation and font assembly

The browser loads one `Dad Emoji` colour font and its existing `Dad Emoji Ink`
stroke font. The sixteen adventure drawings are replacements inside those
fonts. There is no adventure-specific runtime font or routing branch.

## Preparation inputs

`data/font-sources/dad-emoji-prepared.ttf.gz` is the reviewed existing emoji
collection promoted to a prepared vector source. The accompanying JSON pins
its compressed and decoded SFNT hashes, records its original production WOFF2 hash, and retains the old
manifest and preparation-recipe identity. It was losslessly decoded to SFNT
once and stored with ordinary lossless gzip compression; the build no longer
reconstructs WOFF2 coordinates in Python every run. The prepared source occupies
about 3.9 MiB in the repository; gzip decoding does not reinterpret glyph data.
Its existing glyph records, colour layers, metrics, cmap and GSUB tables remain
available as compiled inputs. This is a one-time migration of already-reviewed
work, not a claim that legacy raster artwork was freshly retraced.

The old artwork-processing command is retained in
`tools/font/prepare_legacy_emoji.py`. It is an explicit source-preparation tool,
not part of normal assembly. Changes to that recipe require refreshing the
prepared input and its provenance; assembly rejects a mismatched recipe hash.
Editing an older raw illustration requires an explicit preparation step to
update the prepared vector source. Assembly alone does not watch or regenerate
legacy raw illustrations. The new sixteen drawings have individual preparation
recipes and automatic cache invalidation as described below.

## Per-drawing artifacts

`tools/font/build_adventure_emoji.py` prepares the sixteen selected raster
illustrations. Each artifact contains the finished black outlines, colour-layer
outlines, RGB colours and advance width. `tools/font/emoji_glyph_cache.py` stores
these as disposable content-addressed JSON under
`build/font-cache/emoji-glyphs/`.

The key covers the actual cropped source pixels and dimensions, codepoint,
recipe hash, and relevant library versions. Hashing the source cell rather than
the entire shared atlas means editing one cell invalidates only that drawing.
Current source-file hashes are recorded separately in release provenance.
Active source selections, crop rectangles and optical settings live in
`assets/emoji-concepts/selected-sources.json`; changing a selection is not a
global recipe edit. Per-glyph preparation options such as preserving grey fade
layers are included in the relevant artifact key.
The two Hobbes drawings additionally select full 1024-pixel preparation and
Potrace curve fitting. Cubics are converted into native TrueType quadratics
with a 0.2-font-unit tolerance. These resolution/curve options and the tracer
version are included in their cache keys; other drawings retain polygon
tracing. This avoids reducing high-contrast source ink to coarse straight edges.
Corrupt/incomplete entries are rebuilt; cache writes are atomic. Clearing the
cache is safe and does not require regenerating legacy artwork.

## Assembly

Run:

```sh
.venv/bin/python tools/font/build_emoji.py
.venv/bin/python tools/version_assets.py
```

The assembler loads the prepared SFNT, requests the sixteen glyph artifacts,
replaces the corresponding existing base/variation glyphs, appends their colour
layers, and writes the normal colour/ink pair and main manifest. Existing glyph
IDs and shaping tables are retained. The ink font is derived from the same
in-memory font, avoiding a second decode of the colour web font.

Unchanged TrueType glyph records retain their compiled bytes. New records have
explicit bounds and bearings. Web packaging uses **untransformed WOFF2** and
Brotli quality 5: both are lossless. This avoids optional Python coordinate
transforms and maximum-compression work. Current files are about 3.7 MiB each,
compared with about 3.0 MiB before; the size tradeoff buys much faster builds
and avoids costly Python WOFF2 decoding in review tools.

Build receipts include preparation/assembly durations and hit/miss counts in
`output/font-review/emoji-build.json`. Use `--output-root` to write an isolated
build and `--cache-dir` to test a cold cache. No font output is used as its own
build input.

## Verification

The focused tests cover cold/warm byte equality, corrupt-cache recovery,
source/recipe invalidation, one-cell/one-glyph invalidation, unchanged legacy
glyph bytes/metrics/colour layers, preserved cmap and GSUB, colour/ink alignment,
and normal emoji font loading. Local compiled-font specimens are rendered with:

```sh
.venv/bin/python tools/emoji/render_adventure_review.py
```

`assets/emoji-concepts/production-review.json` records selected artwork,
artifact keys and final font hashes. The review PNG/SVG show actual compiled
font outlines at large and dialogue sizes; they are not browser screenshots.
