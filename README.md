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

- `tools/build_assets.py` takes the strip from a scan of *The Indispensable
  Calvin and Hobbes* (not included in the repository; run it with
  `uv run tools/build_assets.py calvin-and-hobbes.pdf`). It cuts out the four
  panels from the scan's 1-bit ink layer, erases the lettering and balloons,
  smooths away the scan's pixelation, and records where text may go
  (`free`), where balloon tails may go (`open`) and how big Watterson's
  lettering is (`capHeight`) in `assets/panels.json`. Large solid blacks (Dad's trousers, the night in panel 4) are only in the
  scan's low resolution background layer, so they're merged in from there.
- The default lettering, Dad Lettering (`assets/fonts/dad-lettering.woff2`),
  is built from Watterson's own lettering; see below.
- `js/layout.js` is the text-flow engine: it places text line by line,
  using the widest gap the art leaves free at each height, and searches for
  the panel height or font size that makes everything fit.
- `js/balloon.js` shapes the speech balloons in Watterson's manner: an oval
  round a short remark, otherwise straight sides and rounded corners that
  cut across ragged line ends where the art allows.
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
   the 40 samples most like each character's most typical one. Common
   characters also get four alternative forms, each the average of a
   different six samples, which the font cycles through so repeated letters
   don't look stamped. Numbers are
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
