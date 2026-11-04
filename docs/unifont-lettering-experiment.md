# Licensed pixel-source lettering experiment

This is review work, not production coverage. The remaining Garay, Tolong Siki
and Tai Yo gaps are unchanged.

GNU Unifont Upper 18.0.01 offers an explicitly OFL-licensed source, pinned in
`unicode-source-review.json`. The original vector candidates remain excluded.
The downloaded review file is `/tmp/unifont_upper-18.0.01.otf`.

Run:

```sh
.venv/bin/python tools/font/prototype_unifont_lettering.py /tmp/unifont_upper-18.0.01.otf
```

The script writes comparison sheets and per-character decisions under
`output/font-review/unifont-prototype/`. It preserves a shared em and baseline,
rounds the pixel outlines, and applies conservative pressure variation. Foreground
connectivity uses eight neighbours because diagonal donor pixels touch only at
corners. Candidate strokes must survive two pixels of erosion without breaking.
Each rounded candidate component must remain distinct and retain 80–120% of
its original area.
Each counter must retain at least 75% of its original area overlapping the result.
Topology and counter checks run again after pen treatment. A rejected form is explicitly labelled
NEEDS REDRAW and shown unchanged; it is not an accepted fallback.

The first experiment preserved component/counter counts but shrank counters and
looked too heavy. The stricter version rejects U+11DB1, U+11DB2, U+11DBE, U+11DC2
and U+11DC3. The other 49 pass the structural checks, but many retain angular
pixel-grid bends. None is approved for production. Edge rounding alone is
insufficient: the next experiment should reconstruct smooth stroke centre-lines,
with reviewed joins and counters, or use individually drawn paths from the licensed
reference. Do not weaken the guards merely to obtain a passing count.

## Tolong Siki behaviour and reference review

[Unicode 18 section 13.24](https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-13/)
specifies left-to-right alphabetic text, no conjuncts, spacing SELA, and marks
from other blocks. The font must support U+0303, U+0306, U+0330, U+0307, U+0324,
U+0308 and the older U+0323, U+0331 and U+0304 conventions. Marks must be routed
with Tolong bases and have native above/below attachment; cmap presence is not
sufficient. Test the eight consonant/mark examples in Table 13-11 and vowel
nasalization with following SELA. Preserve word spaces and hyphen boundaries.

The alphabet, digits and signs on pages 3–4 of
[L2/23-024](https://www.unicode.org/L2/L2023/23024-tolong-siki.pdf) were visually
compared with the source and experiment. The reference uses much rounder letters
than the pixel source. It is an identity/behaviour reference, not traced artwork;
all experimental outlines derive from the licensed Unifont source. Proposal
PUA mark mappings are superseded by the released specification above.

A second complete prototype run produced byte-identical PNG and JSON files
(compared against `/tmp/tolong-reproduction/`). No font is emitted or installed,
and no runtime routing or coverage entry is added.

## Stroke reconstruction follow-up

The `strokes` method supersedes edge rounding as the candidate for Tolong Siki.
It reconstructs paths from the native pixel skeleton, removes diagonal shortcuts
across orthogonal corners, separates paths at junctions, and rounds path bends.
Cycle paths receive a separately bounded width so small loops retain counters.
Compact detached components preserve their area as round dots instead of being
reduced to short dashes. Shared graph vertices keep joins connected.

```sh
.venv/bin/python tools/font/prototype_unifont_lettering.py /tmp/unifont_upper-18.0.01.otf --method strokes --output output/font-review/unifont-strokes
```

`unifont_strokes.py` supplies the reconstruction. `prepare_letter` in the prototype
module exposes the same deterministic candidate generation for a future font
builder. Candidate stroke widths, loop widths and pressure strength are searched
within fixed bounds; the original component-area (80–120%) and counter-overlap
(75%) requirements remain unchanged and are checked again after pressure treatment.
Only U+11DB2 needs a counter adjustment: vertices near a small counter may move
outward at most 0.3 source pixels, shared across incident paths. Larger counters
are untouched. This adjustment was visually reviewed, not accepted by count alone.

All 54 forms now pass the structural checks. The smallest retained counter overlap
is 0.75146484375; component-area ratios range from 0.80244140625 to 1.051025390625.
Every form retains nonzero pressure treatment. The full comparison sheet was
inspected enlarged and at 24px against the previously reviewed identities. The
stroke method removes the residual pixel-edge steps of the first experiment.
This is a candidate outline set, not an integrated or fluent-reader-validated font.

Four regressions pass: corners do not invent loops, a loop remains attached to its
stem, detached dots preserve area and roundness, and a half-filled counter is
rejected even when topology and total ink area still pass. A second full run
reproduced both PNG and JSON byte-for-byte under `/tmp/tolong-strokes-reproduction/`.

Next: emit a reviewed OFL derivative with all 54 forms, include and attach the nine
common marks above/below bases, retain spacing SELA/HECAKA behaviour, and validate
compiled geometry, Unicode examples, routing, wrapping and export. Unifont Upper
contains none of the nine BMP marks, so their source/drawings must be supplied
explicitly. Do not infer functioning attachment from the source's empty layout
tables. No production coverage has changed in this experiment.

## Compiled Tolong review font

`tools/font/build_tolong.py` now compiles the guarded outlines with their shared
baseline into `output/font-review/tolong/DadTolongReview.ttf`. It verifies the
Unifont donor hash and the existing pinned Noto Sans hash before building. The
nine combining marks use Noto Sans outlines, retaining both donor copyright
notices in the font. Unifont's publisher OFL text and embedded copyright are
retained in `assets/fonts/licenses/Unifont-OFL.txt`; the existing Noto-OFL.txt
covers the mark donor. These review marks have not yet received custom pen
styling.

GPOS `mark` attaches above/below marks to each base's actual bounds; `mkmk`
stacks repeated marks on their respective side. Marks have zero advances;
SELA and HECAKA retain 500-unit advances. This follows the repertoire and
spacing requirements in [Unicode 18 section 13.24](https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-13/).
The review has 54 script characters, nine marks and a space. It intentionally
has no production routing or coverage claim yet.

Reproduction and review commands:

```sh
.venv/bin/python tools/font/build_tolong.py /tmp/unifont_upper-18.0.01.otf
.venv/bin/python tools/font/preview_tolong.py
.venv/bin/python -m pytest tests/test_font_tolong.py tests/test_unifont_strokes.py -q
```

The compiled specimen `output/font-review/tolong/compiled.png` was inspected at
40px and 24px. It includes every base, all nine marks, Unicode table 13-11
examples, all six nasalized vowels followed by SELA, and mark stacks. Eighteen
checks pass (seven existing SWIG warnings): native mark geometry on every
letter, zero mark advances, both spacing signs, above/below stacking, actual
outlines and preservation of all traced components/counters, plus the four
stroke reconstruction regressions. This is mechanical and visual validation,
not fluent-reader review. Production source packaging, script routing, browser
wrapping and export remain the next integration work.

### Production integration

The Tolong derivative is now registered through `data/font-sources/tolong.json`
and packaged by `build_scripts.py`. `fetch_sources.py` restores the pinned donor
and raw publisher license; the extra Unifont copyright notice is retained with
the bundled license. The source verifier excludes donor-only fonts from its
candidate repertoire and invokes `build_registered()` for the actual derivative.
The production TTF matches the reproduced review TTF byte-for-byte. All native
mark geometry tests also run against its WOFF2. Whole-cluster routing is tested,
and the three Tolong browser specimens passed and were visually inspected.
Current checks: 59 targeted Python, 261 JavaScript, 207 browser scenarios, and
11,364 verified source files. Marks retain provisional donor styling and expert
script review remains outstanding; Garay and Tai Yo are not integrated yet.
