# Tai Yo lettering and native placement

The pinned GNU Unifont Upper 18.0.01 donor supplies all 55 assigned characters.
It is used under OFL 1.1 with the manifest and attribution already recorded for
Tolong/Garay. No previously unlicensed Tai Yo candidate is used. The Unicode
chart is an identity reference only; none of its outlines are extracted.

## Native requirements

[Unicode 18 section 16.15](https://unicode.org/versions/Unicode18.0.0/core-spec/chapter-16/)
describes vertical top-to-bottom text with columns progressing right to left.
Embedded horizontal text rotates the script counterclockwise, yielding LTR
reading order; the code chart uses this horizontal presentation. Vowels follow
consonants in phonetic order. Five signs combine with their base; most vowels
and rhymes remain spacing letters. Preserve SIGN UE versus LETTER UE. KVO forms
are explicitly encoded; do not manufacture a KO+VO ligature. SIGN AY can express
a medial or a rhyme; repeated signs must remain distinct. Figures 16-9 and 16-10
show adjacent marks and placement within the bodies of HIGH TO and HIGH FO,
away from their long tails.

For this horizontal comic, use the documented horizontal form. This does not
claim support for independent vertical page layout. The five Mn marks are
U+1E6E3, U+1E6E6, U+1E6EE, U+1E6EF and U+1E6F5, all CCC 230 in the pinned UCD.

## Outline experiment

```sh
.venv/bin/python tools/font/prototype_unifont_lettering.py \
  build/unicode-sources/unifont/unifont_upper-18.0.01.otf \
  --script tai-yo --method strokes --output output/font-review/tai-yo-strokes
```

All 55 forms pass the unchanged component, ink-area and counter-overlap guards
without additional exceptions. The complete enlarged/small comparison was
visually inspected against the official chart. Upper/lower tone-class forms,
spacing vowels and five nonspacing signs remain distinct; this is not a
fluent-reader validation. PNG and JSON reproduce byte-for-byte in
`/tmp/tai-yo-reproduction`.

The donor uses 64-unit cells at 64 UPM. Its five marks have negative source
origins and are shifted for the specimen only, as with Garay. Their intended
zero advances must survive font compilation. Wide HIGH TO (U+1E6CD) and HIGH FO
(U+1E6D5) need body-specific attachment, not a bounding-box center over the tail.

Read-only reference review used the full core-spec PDF page 915 (zero-based
914), with figure regions rotated counterclockwise to inspect the horizontal
form. In this orientation the two marks in figure 16-9 sit next to each other,
not one above the other. The future `mkmk` attachment must move along x rather
than simply reusing Garay/Tolong's vertical stacking. The rotated figure 16-10
places the mark above the left body of the two wide letters, below their upper
tail tips. Generic top-of-bounds attachment would get both axes wrong.

Chart: https://www.unicode.org/Public/18.0.0/charts/PDF/U1E6C0.pdf
SHA256: `2b9d91eb2eada645ba7279ab3aa232ded0c74b6cdee1013f274adfc0cc0abe1f`.
The reference PDF remains in `/tmp`; it is not a distributable font source.

Next: build all 55 forms with explicit horizontal attachment anchors, side-by-side
medial/rhyme marks and preserved spacing letters. Test the published UE examples,
repeated AY and AY+ANG, wide-base positioning and absence of unwanted KVO
substitution. Then integrate font routing and inspect wrapping/export in comics.
No production Tai Yo coverage is advertised by this prototype.

## Compiled horizontal review font

`tools/font/build_tai_yo.py` now produces a 55-character review font with five
zero-advance marks and shared baseline/scale. Mark glyph origins are normalized
explicitly. Each following mark has its own class, allowing `mkmk` to place it
to the right with a 55-unit ink gap, regardless of differing mark widths. The
Unicode spelling examples and explicitly encoded KVO letters remain separate
input identities; the font has no automatic KO+VO substitution.

HIGH TO and HIGH FO use left-body anchors for the narrow UE/AY/ANG signs. The
long AU/OM drawings retain full top clearance. HIGH TO's tall ANG uses a lower
anchor than UE/AY to fit beside its high tail. The first UE/AY anchors collided
with the body; actual shaped-ink raster tests caught this even though the overall
placement looked plausible. Raising those anchors above the local body fixes
the collision while retaining the reference's left-body placement.

`tests/test_font_tai_yo.py` checks the complete repertoire and traced contours,
every combining mark on each of 31 consonants, mark advances and ink collisions,
wide-base anchors, adjacent AY/AY and AY/ANG, open/closed UE spelling, and
explicit versus decomposed KVO inputs. `tools/font/preview_tai_yo.py` renders
actual shaped output at 40px and 24px for visual review. This remains a review
font until production packaging, routing and browser/export checks are complete.

Final review-font validation: 21 tests pass in 1.52s (seven existing SWIG
warnings). This includes 155 actual shaped base/mark collision checks, all four
wide-base examples, both published adjacent-mark examples, and nine spelling/
KVO cases. The updated 40px/24px specimen was visually inspected. Independent
builds reproduce TTF and JSON byte-for-byte under `/tmp/tai-yo-font-reproduction`.
The builder and tests are ready for packaging; no delivered coverage count has
changed yet.

## Production integration

The derivative is registered by `data/font-sources/tai-yo.json` and its cached
builder verifies source/recipe/output hashes. The production TTF and JSON are
byte-identical to the independently reproduced review build. The complete
geometry suite now runs against both review TTF and delivered WOFF2, including
all 155 base/mark collisions on each. A JS regression verifies whole-cluster
selection of the Tai Yo shard, with spacing UE and adjacent medial/rhyme marks.

Validation: 146 targeted Python tests passed in 41.86s (seven existing SWIG
warnings), all 265 JavaScript tests passed, all 213 browser scenarios passed,
and 11,364 cached source files verified. Three added Tai Yo scenarios were
visually inspected: wide-body marks, Unicode spelling examples and explicit
KVO, plus mixed Latin/Arabic, punctuation and tight wrapping. Those cases have
no unmapped characters or fallback warnings; browser geometry and PNG dimension
round trips passed. This delivers the documented horizontal form used in the
comic, while specialist review and independent vertical layout remain unclaimed.
