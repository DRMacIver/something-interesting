# Two Types of Things

A static, backend-free generator for the "Calvin's dad explains there are two
types of things" meme. Type Dad's lines into the first three panels and the
text flows around the artwork; long text either makes the panels taller or
shrinks the lettering to fit.

## Running locally

The page fetches its assets, so serve it over HTTP rather than opening the
file directly:

```bash
python3 -m http.server 8765
```

Then open <http://localhost:8765>.

## Deploying

Everything is static. On GitHub, enable Pages for the repository with
"Deploy from a branch", pointing at the root of the default branch.

## How it works

- `source/original-strip.png` is the original strip.
- `tools/build_assets.py` cuts out the four panels, erases Dad's lettering,
  upscales the line art, and records which parts of each panel are open
  space (white space connected to the top of the panel) in
  `assets/panels.json`. Re-run it with `uv run tools/build_assets.py`.
- The default lettering, Dad Lettering (`assets/fonts/dad-lettering.woff2`),
  is built from Watterson's own lettering; see below.
- `js/layout.js` is the text-flow engine: it places text line by line,
  using the widest gap the art leaves free at each height, and searches for
  the panel height or font size that makes everything fit.
- `js/app.js` draws the comic on a canvas and handles the controls. The
  current text and settings are stored in the URL, so links are shareable.

## The font

Dad Lettering is made from a scan of *The Indispensable Calvin and Hobbes*
(not included in the repository) in three steps:

```bash
uv run tools/font/extract.py calvin-and-hobbes.pdf build/samples.pkl
uv run tools/font/glyphs.py build/samples.pkl build/glyphs.pkl
uv run tools/font/build_font.py build/glyphs.pkl assets/fonts/dad-lettering.woff2
```

1. `extract.py` uses the scan's OCR layer to find words, splits each word's
   ink (from the scan's 1-bit lettering layer) into separate shapes, and
   keeps the words with exactly one shape per character as labelled samples.
2. `glyphs.py` drops OCR misreadings (words that aren't English, and samples
   that look like a different, better attested character), then averages
   the 40 samples most like each character's most typical one. Numbers are
   rare in the strips, so the digits 2-9 come from a few hand-picked
   instances.
3. `build_font.py` traces the averaged bitmaps into outlines, fits side
   bearings and kerning pairs to the letter spacing measured in the book,
   and builds the font. Lowercase maps to the capitals, and a contextual
   rule gives the pronoun I its serifs, as Watterson draws it. A few glyphs
   (`:` `;` `"` `…` dashes, and `6`, a turned 9) are put together from
   others.

## Tests

```bash
npm test
uv run pytest
```
