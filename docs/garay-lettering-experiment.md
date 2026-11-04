# Garay lettering and shaping work

The selected source is the pinned GNU Unifont Upper 18.0.01 donor recorded in
`data/font-sources/tolong.json`, used under OFL 1.1. Earlier fonts with unclear
redistribution rights remain excluded. The experiment does not add production
coverage.

## Rendering requirements

[Unicode 18 section 19.11](https://unicode.org/versions/Unicode18.0.0/core-spec/chapter-19/)
describes Garay as right-to-left and nonjoining. Preserve upper/lowercase
consonant distinctions, including capital swashes; vowels are uncased. A trailing
handwritten swash is optional, so do not invent joining behaviour to supply it.
Spacing vowel length and EE signs must remain distinct from combining E.
Figure 19-5 supplies contextual spelling examples for KA, BA and prenasalized BA;
these are input distinctions, not substitutions the renderer should invent.

The pinned UCD contains 69 assigned characters in U+10D40..U+10D8F, including
five nonspacing marks U+10D69..U+10D6D (all CCC 230), ten digits with bidi class
AN, and distinct upper/lowercase mappings. A future font needs above-base mark
attachment, appropriate mark advances and RTL tests. It must retain obsolete
letters, the sukun, reduplication sign, hyphen and mathematical signs too.

## Source coordinates and review

The source uses 32-unit digit cells and 64-unit letter cells, at 64 UPM.
Nonspacing marks have negative x coordinates. The Tolong prototype's 48-unit
viewport is insufficient: it crops wide letters and omits mark ink entirely.
The generalized prototype uses an 80-unit square viewBox for Garay, translating
zero-advance marks by 64 units only for the specimen. It preserves the baseline
and pixel scale and asserts every source bounding box fits. Empty source masks
now fail explicitly. These display translations must not become spacing marks
in the font.

```sh
.venv/bin/python tools/font/prototype_unifont_lettering.py \
  build/unicode-sources/unifont/unifont_upper-18.0.01.otf \
  --script garay --method strokes --output output/font-review/garay-strokes
```

The same component, counter-overlap and ink-area guards apply as for Tolong.
Rejected forms are labelled and shown unchanged; they must not be presented as
finished custom lettering. The comparison preserves aspect ratio at enlarged
and small sizes. Production integration follows only after identity/style and
shaping review; the unmodified donor's empty layout tables are insufficient.

The first correctly framed run accepted 64 forms and rejected U+10D42 (digit
two), U+10D4C (vowel O), U+10D69 (combining vowel E), U+10D6F (reduplication) and
U+10D75 (small JA). A bounded width search found guarded stroke recipes for four:
0.75/0.6 for digit two and reduplication, 1.2/0.6 for vowel O, and 0.75/0.8 for
small JA (main/loop widths in source pixels). The comma-shaped combining E has
a broad head and thin tail; uniform-width skeleton reconstruction loses too
much area. It instead uses bounded contour rounding, followed by the same
pressure treatment and structural guards. A regression checks its head/tail
asymmetry as well as the unchanged component/counter constraints.

Visual comparison with the [Unicode 18 Garay chart](https://www.unicode.org/Public/18.0.0/charts/PDF/U10D40.pdf)
identified a limitation the structural guards alone missed: the skeleton recipe
for spacing vowel O retained component area but made its comma into a chevron.
It now uses the asymmetric contour method too. The chart was viewed solely as
an identity reference, never traced or used as an outline source. Remaining
forms retain recognizable digit, consonant, case-swash and symbol distinctions;
the low-resolution donor still imposes geometric compromises, so fluent-reader
review is not claimed. The final chart-to-source review does not establish
native text shaping; that requires the next font-building stage.

The spacing O's first contour candidate shortened its tail beyond the regression
limit. Reducing its smoothing scale to 24 raster pixels (from 32) retains the
tail endpoint while preserving the broader head; the combined treatment passes
the unchanged head/tail test. The combining E retains the 32-pixel recipe.
The targeted suite now passes 39 tests, including both delivered/review Tolong
geometry and seven additional Garay/viewport regressions (seven existing SWIG
warnings). The viewport change reproduced the delivered Tolong TTF byte-for-byte.

Next implementation: compile the 69 reviewed forms, normalize marks from their
negative source origins into zero-advance glyphs, add native above-base and
stacking anchors, preserve case and spacing signs, and test Figure 19-5 input
examples with RTL letter runs and left-to-right AN digit runs. The source's wide
letter cells need deliberate side-bearing/scale review at actual dialogue size.

Final result: 69 guarded candidates, zero rejected. The complete PNG and JSON
reproduce byte-for-byte in `/tmp/garay-strokes-reproduction`. The reference chart
PDF SHA256 is `499f137bc9c6903ba3b70d77b046d60214991b370ccfae9e01f48dcb6077b653`;
it was used only for visual identity comparison. No production coverage changed.

## Compiled and delivered font

`tools/font/build_garay.py` now compiles all 69 forms, including five native
combining marks. It retains a shared baseline/scale, trims excess source-cell
side bearings to 50 units per side, and gives marks zero advance with centered
above-base `mark` and `mkmk` positioning. The case swashes remain distinct
outlines; no joining behaviour or spelling substitutions are introduced.
`data/font-sources/garay.json` registers the derivative builder and references
the already hash-verified donor. Copyright and OFL terms remain retained.

The production TTF and JSON match the independently built review files exactly.
Review TTF and compressed WOFF2 both pass all native geometry, case, spacing,
Unicode figure 19-5 and shaping checks. The JS bidi test resolves Garay letters
RTL and its AN digits LTR; a separate test checks whole-cluster font selection.
`tools/font/preview_garay.py` renders actual shaped outlines at 40px and 24px,
including every case form, mark, spacing sign, symbol and digit.

Validation: 103 targeted Python tests pass in 33.84s (seven existing SWIG
warnings), all 263 JavaScript tests pass, 11,364 source files verify, and all
210 browser scenarios pass. Three Garay comic scenarios were visually inspected
for upper/lowercase marks, Unicode vowel spelling, repeated marks, spacing signs,
LTR digit runs and mixed Latin/Arabic text. The browser harness includes ink
containment, balloon geometry and PNG dimension round trips. No native-reader
or cross-browser validation is implied; the pixel donor's geometric influence
remains a provisional style limitation.
