# Something Interesting

A static, backend-free generator for the "Calvin's dad explains there are two
types of things" meme. Type Dad's lines (and Calvin's reply) and you get the
comic, lettered the way the original strip is: the text flows around the
artwork, sits in balloons in the panels that have them, and the panels grow
to make room for long text, wider as well as taller.

## Running locally

The [custom adventure emoji set](assets/emoji-concepts/README.md) supplies sixteen
hand-drawn designs, including snow goons, dinosaurs, space objects, and the
approved Hobbes tiger forms. The Unicode sampler's **An entirely ordinary
afternoon** comic shows the complete set; the linked notes include a rendered
font review and reproducible build instructions.
The [emoji build pipeline](docs/emoji-build-pipeline.md) caches prepared glyph
assets and assembles these replacements into the main emoji font.

The page fetches its assets, so serve it over HTTP rather than opening the
file directly:

```bash
uv run tools/serve.py
```

Then open <http://localhost:8765>. (It's an ordinary static file server,
except that it tells browsers not to use cached files without checking.)

The [completed panel artwork](panels.html), at
<http://localhost:8765/panels.html>, includes all four full-resolution exports
and an adjustable overlay of each original crop. The reconstructed lower scenes
are in `assets/full-panels/`; their source comparisons and rebuild commands are
recorded in `assets/full-panels/provenance.json`. In panels 1 to 3 the scan
is kept pixel for pixel and everything outside it comes from one whole-scene
drawing per panel, made by Codex's image generation and fitted to the scan in
code: registered, bent to agree with the scan inside the crop, joined to its
lines at the crop's edges and re-inked at its line weight. In the two
close-ups Dad's shoe is Watterson's own from panel 1. The method, the fit
measurements and what was tried before are in
[tools/extensions/graft](tools/extensions/graft/README.md); rebuild with
`uv run tools/extensions/graft/build.py`. These artwork exports are
separate from the editor's layout assets.

The [Unicode sampler](sampler.html), at <http://localhost:8765/sampler.html>,
shows 25 complete comics with different scripts, emoji, mathematical letters,
combining marks and diagrams. Filter or search the examples, open one in the
editor, or download its full-size PNG. Previews render as you scroll.

## Updating assets

Every asset URL the pages use carries a hash of the file's contents
(`?v=...`), so browsers fetch a file again exactly when it has changed.
After changing the code, the stylesheet, the font or the art, run

```bash
uv run tools/version_assets.py
```

Links to the page are previewed with an image of the default comic,
`assets/preview.png`. If the default text or the art changes, open
<http://localhost:8765/tools/preview.html>, save the image it shows over
`assets/preview.png`, and run `tools/version_assets.py` again.

(`uv run pytest` fails until you do).

## Deploying

Everything is static. On GitHub, enable Pages for the repository with
"Deploy from a branch", pointing at the root of the default branch. The
link preview tags in `index.html` assume the site is at
<https://drmaciver.github.io/something-interesting/> (a repository named
`something-interesting`); change `SITE` in `tools/version_assets.py` and the
tags if it isn't.

## How it works

- `tools/build_assets.py` takes the strip from a scan of *The Indispensable
  Calvin and Hobbes* (not included in the repository; run it with
  `uv run tools/build_assets.py calvin-and-hobbes.pdf`). It cuts out the four
  panels from the scan's 1-bit ink layer, erases the lettering and balloons,
  smooths away the scan's pixelation, and records where text may go
  (`free`), where balloon tails may go (`open`) and how big Watterson's
  lettering is (`capHeight`) in `assets/panels.json`, along with how each
  panel's dialogue is lettered in the original (`speech`: in a balloon, or
  loose with a pen stroke towards Dad) and where Calvin's reply goes. Large
  solid blacks (Dad's trousers, the night in panel 4) are only in the
  scan's low resolution background layer, so they're merged in from there.
  Panels can widen to any width, so wherever the art runs off a panel's
  edge it is finished off: Dad's back and trailing leg in panel 1
  (`tools/extensions/panel1-left.png`), Dad kneeling by the record player and the
  rest of Calvin in panel 2 (`tools/extensions/panel2-{left,right}.png`), Dad's
  shoulder in panel 3 (`tools/extensions/panel3-left.png`) and, below it,
  the whole scene of Dad down on one knee and Calvin on the floor
  (`tools/extensions/panel3-below.png`, shown as far as the lettering
  leaves room), and the far end
  of Calvin's bed in panel 4 (`tools/extensions/panel4-left.png`), drawn by
  Codex's image generation
  from the panel and thresholded to the scan's 1-bit ink so that they're
  smoothed like the rest. Beyond that the panels are plain background, as
  far as they need to go; panel 4's bed stays in the middle. Watterson's
  signature is cut out of panel 4 (`assets/signature.png`) so it can sit in
  the corner however wide the panel is.
- The lettering, Dad Lettering (`assets/fonts/dad-lettering.woff2`),
  is built from Watterson's own lettering; see below.
- `js/layout.js` is the text-flow engine: it places text line by line,
  using the widest gap the art leaves free at each height, keeps a straight
  left edge unless the art pushes lines well aside, keeps a balloon's text
  in one block rather than squeezing it into a gap partway down, finds the
  smallest panel height that fits everything, and then drops short text
  down towards whoever is speaking. Panels that need more room grow
  keeping the original panels' proportions, but only as wide as saves
  height: text that won't get shorter with more width (short lines that
  don't wrap) makes them taller instead. A real wall of text that fills
  its panel is lettered loose, with a pen stroke towards Dad, as in panel 3
  of the original; given room, it gets a balloon. Balloons keep to lines
  not much longer than the original panel's, float free and centred where
  there's room; and Dad's lettering never sits to the right of Calvin's
  balloon, where it would be read after Calvin's reply.
- `js/balloon.js` shapes the speech balloons in Watterson's manner, as
  worked out in [docs/balloon-study.md](docs/balloon-study.md): balloons
  near the top of a panel hang from its border, outlines follow the text in
  smooth curves, and tails leave from wherever gives the clearest path to
  the speaker's face (running all the way down to them when the balloon
  has had to go far away).
- `js/comic.js` draws the comic on a canvas and reports what it drew;
  `js/app.js` is the page around it. The text is stored in the URL, so
  links are shareable.

## Checking the lettering

`js/checks.js` holds programmatic checks that the lettering looks
reasonable: text stays in its panel and off the art, balloons enclose their
text with room to spare, stay off the art and other balloons' text, have no
sharp corners, and have tails that point at their speaker, end near them,
aren't needlessly long and don't run into other balloons.
<http://localhost:8765/tools/checks.html> draws the comic with texts of many
lengths in each panel and runs the checks on each (`?only=<scenario name>`
shows one at full size).

## Tests

```bash
npm test
uv run pytest
```

## The font

The Unicode typography beta is ready for human playtesting. The
[agreed brief](docs/unicode-beta-brief.md), [completed plan](docs/unicode-beta-plan.md)
and [implementation audit](docs/unicode-beta-audit.json) record the scope and
limits. The original beta checkpoint accounts for 2,336 Python cases across
verified batches. Later [sampler typography refinements](docs/typography-alignment-feedback.md)
passed 373 JavaScript checks and focused font/reproduction checks.
Character inventory, native shaping, sampled
visual review and dated browser evidence are tracked separately.

`tools/unicode/outline_audit.py` separately replays actual font-stack selection
and checks positive outlines, COLR layers and isolated GSUB output. Its inventory
includes visible prepended format signs as drawing requirements as well as
behaviour requirements. A clean result is not a glyph-identity, complete
format-behaviour, contextual-shaping or style claim.

Licensed script sources and Unicode data are pinned in `data/`; custom source
and sequence builders live in `tools/font/` and `tools/unicode/`.

For local visual iteration, use `tools/font/render_specimen.py --spec <fixture>
--output <prefix>` (or `--atlas-page 1`). It writes outlined PNG/SVG specimens
and JSON with source hashes, shaping positions and ink bounds, without a server
or browser. Compare native and candidate fonts at dialogue and detail sizes;
these specimens do not execute application routing or balloon layout.

`tools/font/supplemental_recipes.json` lists the accepted source-specific pen
recipes. `supplemental_adapter.py` applies them during the script build, retaining
native shaping tables, advances and attachment frames, and records per-glyph
guard rejections. Dense CJK, Tangut and Khitan use a separate guarded finer-ink
adapter, retaining native glyphs where thinning fails component/counter checks.
The CFF adapter also verifies that decoded Type2 advances agree with hmtx,
including five documented legacy width-only repairs. All methods preserve
source provenance and explicit per-glyph decisions. Content-addressed caches
are disposable; production reports and untouched baseline fonts are retained
under `output/font-review/`.

`tools/font/build_greek.py` builds the handwritten Greek companion, including
polytonic vowels, from the retained OFL WenKai letters and Noto accent
arrangements. It preserves native letter outlines and canonical equivalents.
Rebuild it after script fonts and run `tools/version_assets.py` afterward.
`tools/font/optical_anchors.py` supplies the upper/lower letter-profile centres
used when rebuilding the extended Latin lettering.

`tools/font/build_cjk_variants.py` maps standardized CJK variation sequences to
their specified compatibility ideograph drawings, using the pinned CC0 Jigmo
archive. Rebuild it before `tools/version_assets.py`. This font is loaded only
for matching variation sequences. Its guarded finer-ink finish retains the
pinned compatibility identities; specialist reader review remains provisional.

`tools/font/build_marked_cjk_variants.py` adds separate CJK variant companions
for the app's 257 existing hand-treated accents. Build these after the script,
CJK variant and extended lettering fonts. They copy the current CJK base
drawings and their existing finish exactly, along with metrics, hints and
selectors; only added accent drawings are converted to the TrueType grid.
Native single-mark positions are recorded from the selected base font. The
companions load only when a requested accent is missing from the variant font.
Context-sensitive native variants retain their complete source shaping.

`js/standalone-fonts.js` selects a complete existing native font for joining
fields containing Tatweel: Aref Ruqaa has no extender ink or advance, so those
fields use a visible source such as Kufi rather than splitting a word across
faces. Fields without Tatweel retain their ordinary routing.

`js/combining-annotations.js` supplies dynamic layout for eight enclosing forms
and the ten double-diacritic classes. Enclosures grow around preceding accents
and enclosures; double marks span the following base outside its ordinary marks.
For a nonjoining variation cluster with a foreign nonspacing mark, the longest
supported prefix keeps its native font. Remaining marks follow canonical order,
using the selected font's own outlines for native marks displaced by the foreign
mark. Complete native clusters keep their existing shaping. Native base drawings
retain their fonts and size. The source-path catalog is
reproducible with `tools/font/build_combining_outlines.py`; source hashes,
copyrights and licences accompany its records. Joining scripts, connected
Egyptian groups, CGJ-sensitive combinations and unsupported interactions keep
their native path. These conservative fallbacks and source-specific limits are
recorded in the implementation audit; sampled style reviews do not replace
specialist reader feedback.

`tools/font/build_math_variants.py` supplies 27 explicit math alternatives from
the pinned NewComputerModern release. Its renamed derivative retains native
curves and mark layout; GUST/LPPL terms, upstream availability and change notices
are bundled in `assets/fonts/licenses/`. Ordinary math fonts retain priority
unless a run explicitly requests a variation.

`tools/font/build_seal_sans.py` supplies only the 139 Seal characters absent
from the other fonts. It retains native cubic drawings and advances, translating
the baseline by 340 units. This separate AGPL-3.0 font has its original licence,
modification notices, and [complete corresponding source](assets/fonts/sources/DadSealSans-source.zip)
bundled beside it and linked from the app footer. That download includes the
full pinned upstream project and a standalone builder tested to reproduce the
production WOFF2 byte for byte. Native Seal style and specialist reader review
remain provisional. Exports currently contain PNG pixels, not font programs.

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
   instances; they're often in heavier lettering, so the digits are
   thinned to the letters' stroke weight.
3. `build_font.py` traces the averaged bitmaps into outlines, fits side
   bearings and kerning pairs to the letter spacing measured in the book,
   and builds the font. Lowercase maps to the capitals, and a contextual
   rule gives the pronoun I its serifs, as Watterson draws it. A few glyphs
   (`:` `;` `"` `…` dashes, `/`, and `6`, a turned 9) are put together from
   others, and symbols the book has none of (`` # $ % & * + < = > @ [ \ ] ^
   _ ` { | } ~ ``) were lettered by Codex's image generation from the
   glyphs above (`tools/font/drawn.png`).

## Tests

```bash
npm test
uv run pytest
```
