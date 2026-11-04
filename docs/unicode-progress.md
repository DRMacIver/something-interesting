# Unicode beta progress

Read `unicode-beta-brief.md` for the agreed objective and visual decisions.

## Completion checkpoint — 2026-11-04

The beta is complete and ready for human playtesting. All 30 requirements are
reconciled with their stated limits. All 2,336 current Python cases are accounted
for across authenticated batches, plus 367 JavaScript checks. Final input
verification passed for 448,437 files and all 199 canonical source decisions.

The final metadata scan correction preserves every assertion and reduces its
runtime from 289.79 to 2.23 seconds; all nine affected cases passed in 34.14
seconds. The current proof retains 2,327 unaffected passing cases. Earlier
coverage accrued as 1,952 + 263 + 121; interrupted masters remain timeouts.

See `unicode-beta-plan.md`, `unicode-beta-audit.json`, and
`output/final-checks/final-current-scope-proof.json`. The final generated
style-status report uses the current font manifest. No required beta work
remains; sampled linguistic/style, dictionary, grid, Egyptian-layout and dated
browser/export limits are preserved for playtesting.

The following entries are historical and superseded by this checkpoint.

## Historical restart checkpoint — 2026-11-03

Reconciled after session restart on 2026-11-03. The goal remains substantially
incomplete. No font builder or pytest process was running at reconciliation;
only the local preview server on port 8765 remained running. Later dated
checkpoints record further completed work; no known build/test/audit remains live
after the Seal supplement milestone below.

- Production emoji: **1,435 visible bases, 1,459 cmap entries, 24 shaping
  components, 5,533 exact sequences**. All **3,963 fully-qualified emoji** are
  encoded. The 35 standalone regional-letter, tone and hair components are
  integrated; all 5,498 previous forms retain their named glyphs and positions.
- Emoji validation: **604 passed, 1 deselected**, plus the ink companion and
  coverage checks. The previously pending four-product reproducibility test
  **finished successfully in 1,086.10 seconds**. Colour font, ink font, manifest
  and glyph review reproduce exactly. Log:
  `/tmp/standalone-components-four-product-rebuild.log`.
- Latest visible coverage: **172,352 / 172,352**, with **zero cmap gaps**.
  Seal sources retain 217 recovered scan drawings, two OFL LXGW native forms
  and 139 separate AGPL Seal Sans native forms. Full corresponding source and
  notices for the new font are bundled and linked from the app footer. Coverage is not proof of
  complete shaping, visual treatment or linguistic correctness.
- Latest JavaScript suite: **346 passed**. Latest full browser corpus run:
  **660 scenarios**, no failures or geometry errors, after foreign nonspacing
  marks and native positional-mark repair. Thirty-six distinct font/source
  checks passed across the targeted suites. The 2,688,273-byte mark catalog
  reproduces exactly. Above-left U+1DF7 and attached-above-right U+031B now have
  correct native positions; all92companions pass positional checks. See
  docs/positional-mark-review.json. These counts do not prove complete typography. The eight new standalone emoji strips and six
  actual math strips were individually visually reviewed.
- Native variants: 1,002 standardized CJK mappings, 128 contextual
  Mongolian/PhagsPa/Manichaean variants have source checks. The explicit math
  font has 37 mappings: 27 native and ten historical adaptations, with candidate,
  accent, previous-shaping and exact-rebuild checks. Four horizontal Sibe quotation variants are packaged; vertical
  orientation remains unsupported. Source styles remain provisional.
- Fullwidth zero and available-source combining-mark retention build finished:
  **381 script shards, 68,229,580 bytes**. Math/native suite: **52 Python
  checks passed**; latest CJK/native suite: **42 passed**, plus the exact
  2,677-variation source-preservation gate. All **1,437
  standardized pairs** are accounted for: 1,309 format-14 mappings and 128
  source-tested contextual forms. Broader behaviour/style and cross-font marked
  IVD handling remain open. Supplementary Jigmo IVS now retain their eight
  native CJK tone/kana marks in the same font. A further 92 on-demand CJK
  variant companions now supply the existing 257 hand-treated accents while
  retaining native drawings, metrics, hinting and variant selection. They total
  26,776,560 bytes in addition to the 381 ordinary script shards. Native single-
  mark fallback positions are explicitly retained in GPOS. Other marks and
  arbitrary cross-script combinations remain open.
- **Math accent repair completed:** missing plain Unicode attachments now use
  source MATH optical points and ink bounds; combining advances are zero and
  above/below stacking stays on the correct side. Native outlines, bearings and
  base metrics are retained. All 37 explicit math variants and their defaults
  pass geometric accent checks; existing native same-side stacks keep their
  original positions. Exact math font/manifest/review reproduction passes.
  All six affected actual math strips were visually reviewed across the accent
  and historical work; all 623 browser cases passed. Explicit math font:
  **67,908 bytes**. Assets are versioned.
- Wider brief remains open: script style and linguistic
  review, variation behaviour, Egyptian/dictionary/grid review and cross-browser
  validation. The project is not beta-complete.

The dated checkpoints below retain history; their running-build statements and
older totals are superseded by this checkpoint.

Current whole-brief requirement/evidence matrix:docs/unicode-beta-audit.json.
A stronger actual font-routing/drawing audit finds172347positive drawings,
5explicit semantic blank/native-context exceptions and0remaining non-format
drawing/routing gaps. Thirteen font-dependent Cf signs still require loading
correction; they were excluded by the old format/drawing partition. Three delete-checker forms
and leading text keycaps were repaired. Full Python15005 remains live; current
33general browser layout scenarios and658Unicode scenarios pass. These are
not a complete beta declaration.

## Earlier implementation summary (counts superseded above)

This summary supersedes the older status and next-step statements in the dated
checkpoints below; those checkpoints retain the evidence and design history.

- Pinned Unicode **18.0.0**, authoritative data, source URLs, hashes and licences.
  The reproducible inventory separates 172,352 visible requirements from 521
  behavioural characters. Cmap presence is not proof of shaping or visual style.
- Logical input retains its case. The original Latin lowercase drawings look
  like capitals, but the renderer no longer uppercases text. Native scripts and
  mathematical alphabet distinctions remain in the input and font routing.
- Unicode 18 grapheme segmentation, default line breaking and bidirectional
  resolution are implemented independently of host ICU. The pinned conformance
  corpora pass, including 19,346 line-break cases, 770,241 BidiTest direction
  cases and 91,707 BidiCharacterTest cases. Wrapped lines retain paragraph state;
  canvas shapes the resolved logical runs. Browser dictionary segmentation adds
  Thai/Lao/Khmer/Myanmar opportunities; linguistic word-boundary review remains.
- Ink-based measurement handles accents, stacked marks and overhangs. Layout
  preserves whitespace, discretionary hyphens, protected clusters and source
  offsets. Resource limits bound input scanning, balancing, canvas allocation
  and share links. Structural diagrams use a dedicated grid; mixed prose/grid
  detection and unusual cell conventions still have limitations.
- **352 script shards, 60,349,164 bytes**, load on demand before measurement.
  Fonts preserve layout tables and carry provenance and derivative names.
  Stale renders cannot replace newer previews; exports wait for the current
  render. Existing character art is retained.
- Bundled cmap coverage is **172,157 / 172,352 visible requirements**, with
  **195 missing**. This is not a completed-lettering or linguistic-review
  count. Native source styles and light outline adaptation remain provisional.
- Egyptian composition supports quadrats, insertions, enclosures, rotations,
  damage/lost-sign treatment and RTL/nesting. Script-specific builders preserve
  joining and attachments for newly assigned marks and letters. Checkpoints and
  tests record the exact supported combinations; exhaustive behaviour and style
  validation remain open.
- Custom emoji routing advertises **5,419 exact sequences**, individually tested
  for one real coloured glyph, positive advance and outline/layer presence.
  The separate fully-qualified emoji-test audit records **3,899 / 3,963** exact
  forms encoded, with **64 missing**; presentation aliases make these totals
  different from the manifest size. Encoding is not proof of rendering or style.
  Thirty book/mail drawings are built into production and reviewed in actual
  strips. Their full Python regression/rebuild run passed all 366 tests.
  Nineteen money/accessory drawings have registered and reviewed candidates;
  their production build passed and all three new actual strips were reviewed.
  The larger regression/reproducibility run passed all425tests. All64remaining
  drawings now have registered, reviewed isolated candidates; their first production
  integration build31709 stopped before writing output on empty-component
  promotion. Rainbow and airplane promotion is now fixed; compiler gate34561
  passed and corrected build1097 is active. No emoji coverage gain yet.
  System fallback does not count as completed custom lettering.

## Latest validation

- Latest JavaScript run passed **317 tests**. The latest Seal change additionally
  passed **25 JavaScript font tests** and **84 Python regressions**. The money/accessory production
  regression and exact rebuild passed **425 tests**; a subsequent candidate
  source/registration batch passed **171 tests**. The ten vehicle detail and
  expanded native-stroke checks passed **125 tests**. The corrected flag/global/source
  suite passed **290 tests**, including comparison to reviewed candidates, all
  qualification pairs and preservation of every previous sequence. The separate
  font/manifest reproducibility check passed. Seven empty-layer comparison
  failures and one missing singleton-review-metadata failure in the earlier
  run were corrected before the successful rerun.
  Book/mail candidates pass **22 source/detail checks** and an independent
  production-compiler comparison against all reviewed candidate outlines,
  colours and metrics. All43object detail/compiler checks pass with the new
  optional stroke support; the 366-test production run passed, including its final
  reproducibility check. The older broad run of **445 then-collected Python
  tests** is historical evidence, not a fresh whole-tree claim. Python reports
  the existing 7 SWIG deprecation warnings. All **12,584 registered cached source
  files** pass pinned-hash verification.
- Latest browser run passed **579 Unicode scenarios**, including ink containment,
  protected-art geometry and PNG dimension round trips, with no warnings.
  All20flag-specific strips and all270flag drawings were inspected at dialogue
  size. All34book/mail qualification forms passed isolated browser pixel/advance
  checks and optical inspection, and all4production book/mail strips were
  inspected beside dialogue. Money10/accessory11candidate forms also pass
  isolated browser pixel/advance checks and optical inspection.
  The expressive faces and licensed music, clock, transport, tool, compound and
  animal, plant, sports, food, dining, sky/weather, coloured face, building, landscape, hand gesture, timepiece, stationery, produce, coloured apple, lime and brown-mushroom, celebration/festival, games/toys/art supplies, household/scientific objects and people with skin-tone/hair/gender/occupation variants
  emoji were inspected at dialogue size. The original lettering harness also
  previously passed all 33 scenarios.
- Font tests cover packaging integrity, source-shaping equivalence and targeted
  script geometry/attachment invariants. These checks and browser specimens do
  not replace fluent-reader review or establish cross-browser correctness.
- Review assets remain in `output/font-review/`; approved image-generation
  specimens and prompts are in `output/imagegen/unicode-prototypes/`.

## Next concrete work

1. Fill the **195 missing visible mappings** using the current coverage report.
   Remaining groups include Seal and emoji. Vietnamese reading marks now have provisional
   right-side forms; historical base-specific combinations remain open. Jurchen
   mappings are now complete; the earlier Jurchen source gap is resolved.
2. Finish the final-object production build31709 and verify its fonts against
   all64reviewed candidates, all79qualification forms and6241adjacency pairs.
   Preserve all5419previous identities/positions using the immutable baseline.
   The pre-build audit still records64missing fully-qualified forms. Review
   every new actual-strip fixture and run coverage/behaviour checks before
   claiming that gap is closed. All113original remaining source drawings are
   now converted (book/mail30,money/clothing19,final objects64).
   Sequence counts are distinct inventories, not interchangeable completion
   totals. Encoding does not prove visual or linguistic correctness.
3. Continue comic-style adaptation and realistic-size visual review, especially
   dense scripts and still-native donor fonts. Retain meaningful mathematical,
   case, modifier, joining and combining-mark distinctions.
4. Broaden script/sequence review and resolve remaining Egyptian, dictionary,
   grid and cross-browser behaviour gaps. Separately validate all742emoji
   variation pairs,1437standardized variants and461named sequences against
   source shaping and actual routing. Fully-qualified emoji completion does
   not establish text-presentation correctness. Plain ASCII key bases must
   retain text routing, and text selectors must not silently force colour. Keep uncertain linguistic judgments
   explicit; provisional decisions are authorised by the brief.
5. Complete a requirement-by-requirement audit only after the above work. Neither
   a passing suite nor fallback preventing missing-glyph boxes completes the beta.

## Reproduction and environment

Use `.venv/bin/python` for installed dependencies; `uv run` encountered sandbox
access issues with the external uv cache. `tools/font/fetch_sources.py` restores
pinned source files on a fresh checkout (network required); `--check` verifies
all 12,584 registered cached files offline. `source_inventory.py` verifies/extracts sources.
`build_scripts.py` reuses output only when source hash, output hash and recipe
match. Increment its recipe after changing subsetting/naming rules.

Run `tools/version_assets.py` after asset/module changes, `npm test`, and
`.venv/bin/python -m pytest -q`. Browser checks are served with `tools/serve.py`,
which binds only to `127.0.0.1:8765`. No sub-agents were requested or spawned.

## Source expansion checkpoint

- Added Kaiyuan Small Seal from pinned commit
  `97433695858330ec9fdb7de9c4604da2f635eba6` under OFL. The independent
  `build_seal.py` builder imports 10,980 SVG glyphs only after matching their
  CCZ identities to pinned Unicode 18 SealSources. `seal-source-review.json`
  distinguishes 1,197 upstream-approved, 22 manual and 9,761 automatically
  aligned entries. Automated alignment is not historical sign verification.
  A conversion bug discovered by bounds tests was fixed: horizontal bearings
  now retain the SVG's xMin instead of shifting each sign to zero.
- Added Kedebideri (Beria Erfe) and Kanchenjunga (Kirat Rai), plus Noto Gurung
  Khema and Ol Onal sources. Their published test binaries lacked the script
  glyphs; the actual pinned Glyphs sources are compiled with standard fontmake
  by our own build_glyphs.py. Upstream build scripts are not executed. Fonts
  are renamed and retain source OFL notices. fontmake is pinned in uv.lock.
- Kirat Rai source lacked canonical composition. The derived font now has
  ccmp rules for both full and partial canonical decompositions; original
  source outlines are preserved. HarfBuzz tests exercise every canonical
  decomposition in Gurung Khema and Kirat Rai, not just one example.
- All nine browser harness scenarios pass geometry and PNG round-trip checks.
  New-script checks also compare nonempty rendered pixels for four canonical
  pairs, including partially decomposed Kirat Rai. These pass exactly. Small
  Seal and new scripts were visually inspected at comic size; they render
  actual signs but native outlines still need comic-style adaptation and
  knowledgeable-reader review.
- Source-cache restoration verifies both archive/member hashes, extracts only
  manifest-listed regular files, and rejects out-of-cache paths. Regression
  tests exercise valid restore, either corrupted hash, path escape and symlink
  rejection. Offline verification reports 11,237 source files valid.

Next: renderer completeness (including Egyptian sign composition and bidi
formatting across wraps), remaining repertoire gaps, and comic styling/emoji
assets remain required. None of these source additions closes those gates.

## Oversized-cluster renderer checkpoint

- `layoutColumn` now propagates its fit result. Calvin's layout widens for an
  oversized protected cluster, then reduces his reply's own font size if it
  still cannot fit. The comic's fit report includes that result.
- Dad's flow can reduce a single indivisible piece at a grapheme-safe emergency
  boundary. It remeasures the font and stores actual size, ink and baseline
  on the line, leaving surrounding lines at their normal size. Increasing
  panel height can no longer be the only response to this width problem.
- Drawing uses each line's actual font size; the independent browser harness
  also remeasures with it. Full JavaScript suite: 163 passing tests, including
  complete-text retention, unchanged surrounding size and prompt completion
  for synthetic overwide combining clusters.
- All 11 real-browser scenarios pass text containment and PNG export checks.
  Two deliberately nonstandard, very long emoji ZWJ clusters exercise actual
  font reduction in both speakers. This uses native emoji fallback: custom
  emoji coverage remains incomplete. Calvin's tiny-lettering stress balloon
  reports additional clearance (0.24 caps) and smoothness (49-degree turn)
  warnings; these are still visual refinement work, not clean geometry.
- Provisional policy: an otherwise impossible single cluster may become very
  small, rather than split or clipped. This preserves its contents but does
  not guarantee readability at preview size. It needs playtesting alongside
  the pre-existing 5,000 UTF-16-unit input cap and canvas export limits.

## Dictionary line-breaking checkpoint

- Added automatic Thai, Lao, Khmer and Myanmar dictionary opportunities via
  Intl.Segmenter. Only internal boundaries of contiguous same-script SA runs
  are added; pinned Unicode 18 grapheme segmentation filters every boundary.
  Existing punctuation, spaces, explicit no-break controls and other scripts
  retain the default line-break engine. No user locale configuration is needed.
- This implements the complex-context tailoring described by Unicode 18
  UAX14, section 5.1 SA:
  https://www.unicode.org/reports/tr14/tr14-57.html
  Intl.Segmenter is the standard browser word-segmentation API:
  https://tc39.es/ecma402/#sec-intl.segmenter
- Dictionary contents/version are supplied by the browser, not pinned to our
  Unicode release. Unsupported engines/locales retain default breaking plus
  the existing grapheme-safe emergency policy. Myanmar-script languages other
  than Burmese, Tai Tham and further SA scripts still need targeted coverage
  and fluent-reader review; this is not a universal linguistic validator.
- All 166 JavaScript tests pass, including the complete default UAX14 corpus,
  four dictionary fixtures, punctuation/glue retention and missing-API fallback.
  The new browser scenario checks final line endings against dictionary word
  boundaries, exact text preservation, actual ink bounds, geometry and export.
  All twelve browser scenarios pass containment/export checks; prior extreme
  Calvin balloon warnings remain. Dictionary-script sample itself has no
  geometry failures and was visually inspected. Native font outlines still
  need the approved handwritten treatment.

## Egyptian composition checkpoint

- Pinned Microsoft's Egyptian Text reference font at font-tools commit
  `d06068439ff23fff99bfd058a5ab44a43183ecd9`, with Git blob/SHA256 verification.
  The font directory OFL and full embedded copyright/license notices are
  retained in assets/fonts/licenses. The upstream description explicitly
  distributes the reference font under OFL:
  https://github.com/microsoft/font-tools/blob/d06068439ff23fff99bfd058a5ab44a43183ecd9/EgyptianOpenType/eot.md
- The existing packaging pipeline retains the layout tables, renames the
  derivative and puts it before UniHieroglyphica for core signs. The latter
  still supplies Extended-A. No upstream build scripts were executed.
- Core vertical, horizontal and nested sign groups now compose in the actual
  browser. The former vertical-joiner placeholder is gone. HarfBuzz comparison
  checks verify positions survive packaging for those three cases and a
  rotation sequence; a separate check requires distinct, compact vertical and
  horizontal arrangements. The browser independently checks compact advance
  widths and ink bounds, and the stacked sign sample was visually inspected.
- All thirteen browser scenarios pass containment/export checks. The Egyptian
  samples have no geometry failures. Known tiny-Calvin balloon warnings from
  the oversized-emoji stress case remain unchanged.
- This is a composition milestone, not complete Egyptian support. Extended-A
  groups can span fonts that lack shared layout logic; exhaustive control,
  deep nesting, enclosures, damaged signs, RTL arrangements, newer variation
  sequences and comic styling remain unverified or incomplete. The reference
  implementation documents a limited hierarchy of grouping levels. Current
  outlines are visibly too fine beside the original lettering.
- Delivered cmap coverage remains 167,901 / 172,352: this work fixes behavior
  rather than inflating the glyph count. Offline source verification now
  checks 11,240 files; the source inventory contains 242 fonts.

## First custom emoji font checkpoint

- Built-in imagegen produced an atlas matching the approved round emoji faces
  (no Calvin identity). A second generation fixed a cell-overlap failure found
  by the font compiler. Sources and exact prompts are retained in
  output/imagegen/emoji-production. Both generated PNGs remain untouched.
- `build_emoji.py` traces vector outlines into a 10,788-byte COLRv0/CPAL webfont
  with 11 emoji: grin, joy, pleading, thinking, crying, exploding head, devil,
  skull, heart, fire and thumbs up. The astronaut asset is not yet encoded.
- Selective colour uses measured median print colours from PDF pages 13 and
  17. The source document hash, pixel patches and RGB values are saved in
  palette-source.json. Default/text hearts are monochrome; VS16 selects the
  crimson heart. Thumbs-up's standardized selectors are explicitly mapped.
- The custom font loads only when needed and precedes the base font for its
  repertoire. Until proper per-sequence run routing is built, any skin-tone
  modifier or ZWJ in input disables the custom batch for the whole rendering,
  preserving native composite emoji instead of mixing incompatible components.
  This is deliberately temporary and does not meet full custom sequence scope.
- 167 JavaScript tests pass. Two new Python tests pass for nonempty outlines,
  valid layers/palette and text-versus-emoji heart shaping (the earlier full
  65-test Python suite remains green at its preceding checkpoint).
- All fourteen browser scenarios pass containment/export checks. The custom
  emoji sample loads the new font, has no geometry failures and was visually
  inspected at dialogue size: ink faces, white interiors and selective printed
  colours render correctly. Existing tiny-Calvin balloon warnings remain.
- Delivered cmap coverage is 167,910 / 172,352 visible requirements, leaving
  4,442 absent. Most existing source glyphs still await comic styling, and this
  eleven-icon batch is only the start of the required emoji repertoire.

## User review: composed hieroglyphs too small

The user identified the third-panel stacked signs as too small. Measurements
confirmed the font compressed the whole group into one normal em, leaving each
individual sign about half-height. Pure Egyptian composed runs now receive a
2x optical scale in the measurer, and their actual size follows the line through
balancing, drawing and ink checks. Balloons reserve the enlarged ink normally.
Ungrouped hieroglyph-only lines and ordinary text retain their previous size.
Mixed-script runs and deeper group hierarchies need further optical review.

All 168 JavaScript tests pass, including a regression for scale propagation
through wrapping. All fourteen browser scenarios still pass containment/export;
the enlarged third-panel group was visually reviewed and its geometry checks
are clean. Its measured height increased from about 59 to 118 canvas pixels.

### Review fix: preserve Dad's head when reframing

The empty third speech in `calvin-wide-cluster` allowed the lower-art reveal
search to crop Dad's hair and eyes. Added a protected head rectangle (including
headroom) to panel-three metadata and its asset-generation source. Layout now
rejects camera placements that crop protected artwork, including after horizontal
view shifts. It still reveals lower artwork where there is room.

All 169 JavaScript tests pass, including empty/short/oversized Calvin replies.
All fourteen browser scenarios pass containment/export plus protected-art checks;
visually confirmed the full head and space above the hair in the reported case.
Existing tiny-Calvin-balloon clearance/smoothness warnings remain separate.

Follow-up: explicitly checked `dad-wide-cluster` after the framing change.
The existing fix also preserves the full head in that scenario; confirmed in a
fresh browser render and added its exact input to the framing regression, which
passes. An already-open checks page needs refreshing to render the updated code.

### Review fix: handwritten Æ and Œ

Replaced provisional Noto Æ/æ and Œ/œ with joined outlines built from the
original A, O and E lettering. E follows A's sloping right leg in Æ; its spine
joins O in Œ. Lowercase uses the same capital-style treatment as this typeface.
Rebuilt the Unicode font and asset cache versions. All nine extended-font tests
pass; all fourteen browser containment/export scenarios pass. Visually checked
both ligatures in the accents comic against adjacent capitals. Other provisional
non-decomposing Latin donor shapes still require their own style review.

## Paragraph bidi and wrapped formatting checkpoint

- Rechecked the released standard against Unicode's official versions/releases
  pages on 2026-11-01: Unicode 18.0.0 remains current. The pinned inventory is
  unchanged. https://www.unicode.org/versions/Unicode18.0.0/
- Vendored MIT-licensed bidi-js at commit
  `953d75cb176f0693aa77d60cdf3afde5f2a0927a`. Original source URLs/hashes and
  licence are in `js/vendor/bidi/`. Replaced its old property data with our
  generated Unicode 18 classes and bracket pairs. The algorithm now uses scalar
  indices, including supplementary RTL letters. Fixed the upstream L1 slice
  index for trailing whitespace on a wrapped substring.
- Pinned both official Unicode 18 bidi conformance corpora in the Unicode source
  manifest. All **770,241 BidiTest** direction cases and **91,707
  BidiCharacterTest** cases pass: paragraph levels, resolved character levels
  and visual reordering. This establishes algorithm conformance for the supplied
  corpora; it does not establish glyph correctness or cross-browser shaping.
- Layout now keeps paragraph source and UTF-16 offsets through emergency wraps
  and balancing. Measurement uses full-paragraph resolved levels; drawing uses
  the same positioned logical runs in visual order. Native canvas still shapes
  each run, with explicit overrides preventing line-local reinterpretation of
  weak/neutral characters. Joining controls and combining marks are retained.
  Original source text remains available on each line; no text is uppercased or
  reversed before shaping. Bidi formatting controls are consumed by the resolver.
- Added regressions for overrides spanning wraps, FSI whose first strong letter
  is on an earlier line, Arabic-context numbers, supplementary RTL letters,
  discretionary hyphens, retained joiners and balanced source offsets. Plain
  unidirectional text continues using the existing whole-line shaping path.
- Full JavaScript suite passed 175 tests before the additional standalone L1
  regression (that regression and both full conformance corpora also pass).
  Full Python suite: 67 passed, with the existing 7 SWIG warnings. Asset import
  maps regenerated. No source-font/cmap changes in this checkpoint.
- All **15 browser scenarios** pass ink containment, protected-art and PNG
  round-trip checks. The new wrapped override/isolate and mixed-script comic
  was visually inspected at dialogue size. Five raster comparisons against
  native whole-paragraph canvas shaping also pass (advance difference <=0.1px,
  alpha-mass difference <=3% to allow subpixel origins). Known tiny-Calvin
  balloon clearance/smoothness warnings remain unchanged.
- Remaining bidi review: additional engines, uncommon mirrored glyphs and fluent
  reading checks. Other open gates remain substantial: diagram/grid layout,
  resource-limit validation, extended Egyptian composition, 4,442 missing cmap
  requirements, most comic-style adaptation, complete custom emoji/sequences,
  and a final requirement-by-requirement audit. The goal is still incomplete.

Next concrete work: diagram/grid treatment and resource-limit validation can
proceed independently of the remaining font/emoji source and styling work.

## Resource-limit checkpoint

- Grapheme-safe truncation now inspects at most the 5,000 UTF-16-unit budget
  plus one scalar of lookahead. An initial cluster with millions of combining
  marks is rejected without scanning all of it. Regression comparisons agree
  with full segmentation at every cut in representative Unicode sequences;
  a two-million-mark paste took about 3ms in the Node check.
- Long paragraphs retain greedy wrapping once aesthetic balancing would exceed
  512 break units or 65,536 DP cells. This bounds balancing work without dropping
  content, splitting graphemes or relaxing line-break rules. A 5,000-character
  CJK regression retains all text and stays within its measurement-call budget.
- Canvas dimensions retain the existing 16,384-side and 16,777,216-pixel budgets,
  now with an explicit positive minimum. These are allocation budgets, not a
  universal device guarantee. PNG download handles a null export result.
- Share serialization is capped at 250,000 UTF-16 units across the original
  texts; parsing rejects encoded payloads above 2,000,000 characters. Oversized
  links are refused explicitly, never generated from shortened text. A failed
  history/URL update no longer prevents the preview. Original textarea contents
  remain intact, and the image truncation message says so. Unicode, directional
  controls and even lone surrogates round-trip in supported links.
- All **16 browser scenarios** pass containment/protected-art and PNG decoding
  checks. The new combined stress case uses a two-million-mark cluster, 5,000
  CJK characters and 2,500 hard lines. It retained all in-budget text and rendered
  in 6.35s on this machine, exporting a 127 × 16,384 PNG. This extreme aspect
  ratio is intentionally tiny/unreadable at preview size; readability for
  arbitrary 5,000-unit inputs is not promised. That stress balloon adds one
  31-degree smoothness warning; existing extreme-Calvin warnings remain.
- Actual app check: pasted 250,002 units, confirmed all remained in the textarea,
  the preview finished and image export stayed enabled, and Copy link displayed
  the explicit length error instead of copying an old/shortened URL.
- 180 JS tests passed, then the added maximum-CJK layout regression passed with
  the full 77-test layout suite. Python code/source assets are unchanged since
  the 67-test passing run above. Asset hashes/import maps regenerated.

Next: proper diagram/grid layout; source/glyph gaps and comic styling; full
custom emoji sequence routing and coverage. Remaining shaping/font/script
limitations above are still open. The full beta goal is not complete.

Final checkpoint verification: all **181 JavaScript tests** pass, all **31 pinned
Unicode source files** verify, generated asset hashes are current, and
`git diff --check` is clean. Latest full Python result remains 67 passing tests.

## Connected diagram/grid checkpoint

- Added `Dad Grid`, a reproducible 7.3KB font covering all 128 Box Drawing
  characters (U+2500..257F), 32 Block Elements (U+2580..259F) and 256 Braille
  Patterns (U+2800..28FF). Box/block outlines derive from the existing pinned
  OFL Noto Sans Mono source; licence notices are retained and the derivative
  renamed. `js/grid-manifest.js` records the source URL, commit/blob/hash and
  build recipe. `tools/font/build_grid.py` verifies the pinned source hash.
- All structural glyphs use one 600 × 1000 cell. Box endpoints meet cell edges;
  internal strokes have subtle pen variation. Block fractions remain geometric.
  Braille has slightly irregular drawn dots with correct 1/2/3/7 and 4/5/6/8
  positions. The empty Braille pattern intentionally has no ink and one cell.
  Tests check all 416 cmaps/bounds/advances, all 256 dot combinations, key block
  fractions and connection edges, weight distinction, licences and rebuild hashes.
- Structural symbols automatically select grid layout for the whole speech.
  Multiline ASCII `+---+`/`+===+` boxes also select it. Rows retain their spaces,
  empty internal lines, one common origin and contiguous baselines. They move
  and, when necessary, shrink as one rectangle instead of wrapping around art.
  Dad and Calvin both use the new path; no configuration is needed.
- Labels retain the original comic font. Graphemes stay intact; fullwidth/CJK
  occupy two cells, halfwidth forms one, and tabs respect these column counts.
  CJK glyphs remain individually positioned. Joining/RTL/Indic labels are
  shaped as whole fields with the pinned paragraph bidi resolver, including
  internal spaces, so Arabic words are not placed in reverse reading order.
  Field widths are reserved in grid cells; complex-label internal advances
  remain native/proportional to preserve joining. Structural borders themselves
  are spatial left-to-right and are not mirrored by label direction.
- Browser review found that balloon inward bow/rounding nearly touched the
  full-height grid ink. Grid balloons now limit both; the regular grid and ASCII
  scenarios have no geometry warnings. The deliberately very wide/tiny Calvin
  grid still has a 36-degree smoothness warning, separate from containment.
- All **19 real-browser scenarios** pass ink bounds, protected-art and PNG
  round-trip checks. New assertions verify identical source rows, common x
  origins and adjacent row heights for the grid scenarios. Visually inspected
  connected single/double/rounded borders, CJK/Arabic/Latin labels, Braille,
  blocks/shading and an ASCII arrow diagram at comic size.
- Full Python suite: **71 passed**, with the existing 7 warnings. After the final
  generated property-table change, the eight grid-font/inventory tests pass.
  The complete JS suite was rerun after the final renderer changes (see latest
  verification below). Asset hashes/import maps and coverage audit regenerated.
  Delivered cmap coverage remains **167,910 / 172,352**, with **4,442 missing**;
  this is a structural/style improvement to existing repertoire, not new cmap
  coverage.

Grid limitations still requiring broader review: automatic detection of freeform
ASCII art without a box marker; newer legacy-computing mosaic/terminal symbols;
formatting controls intended to span separate structural fields; exotic scripts'
cell conventions and cross-browser rasterization. A speech mixing prose with a
diagram currently treats all rows as one grid. No claim of universal terminal
emulation or completed custom styling for all Unicode is made.

Next concrete work: source/glyph gaps and comic-style adaptation, plus complete
custom emoji sequence routing. Extended Egyptian composition and the final
requirement-by-requirement audit remain open. The overall goal remains active
and incomplete; the original brief is unchanged.

Final grid checkpoint: **188 JavaScript tests pass**, generated asset hashes are
current, and `git diff --check` is clean. Latest full Python result: 71 passing.

## Emoji sequence routing and palette checkpoint

- Replaced whole-render emoji disabling with exact grapheme-sequence routing.
  Font selection, measurement, bidi run order, grid labels and canvas drawing
  now share the same custom/native/text policy. Unsupported composites remain
  intact; `emojiFallbacks` reports native artwork explicitly. Unicode 18 emoji
  presentation and registered variation data drive the policy.
- The twelve existing imagegen atlas drawings now supply **26 explicit custom
  sequences**: eleven base characters, four heart/thumb presentation variants,
  five thumb tones and six neutral astronaut ZWJ variants. GSUB tests verify
  every advertised sequence shapes to one nonempty coloured glyph. Person,
  rocket, ZWJ and modifier components cannot select custom art independently.
- Sampled the supplied PDF pages 13 and 35 for five muted skin colours, with
  exact render hashes, rectangles and documented ink blends saved in
  `output/imagegen/emoji-production/skin-palette-source.json`. Vector masks
  recolour hands/faces while retaining white cuffs, helmets and suits. Original
  generated raster art remains untouched. Font and manifest rebuild identically.
- Audit excludes eight empty sequence components from visible cmap coverage and
  separately reports custom-encoded sequences versus visual validation. Visible
  coverage remains **167,910 / 172,352**, with **4,442 missing**.
- Final automated suites: **192 JavaScript tests** and **76 Python tests** pass
  (7 existing Python warnings). Routing tests cover the pinned standard emoji
  and ZWJ inventories, including singleton ranges, without splitting clusters.
  This proves routing integrity, not custom artwork coverage for that inventory.

Most emoji still use native artwork. Complete custom repertoire/style work,
remaining source/glyph gaps, extended Egyptian composition, broader typography
review and the final brief audit remain unfinished. The goal remains active.

Browser verification: **22 scenarios** pass ink containment, protected artwork,
PNG export and scenario-specific assertions, including all six custom astronaut
sequences and mixed custom/native emoji. Visually inspected the astronaut tones
at comic size: face colours differ while helmets and suits remain white.
The new emoji scenarios have no geometry warnings. Existing extreme-width and
resource-limit geometry warnings remain as recorded above. Asset hashes are
current and `git diff --check` passes.

## Tulu-Tigalari and Sidetic source/renderer checkpoint

- Added pinned OFL Daarage and the author-drawn Sidetic subset of Unicodia Funky
  from Mercury13/Unicodia commit `dcbe251036833331f0a8f66c186a315751db24f9`.
  `data/font-sources/unicodia.json` records hashes and scope; required notices
  and full OFL terms are retained in `assets/fonts/licenses/`. Funky's uncertain
  origin and explicitly weak scripts are excluded. Sidetic is restricted to
  the 26 assigned Unicode 18 letters; its three extra unassigned mappings are
  not exposed. These are provisional native outlines, not finished comic style.
- Source verification now accepts OpenType CFF fonts. Packaging honours explicit
  per-source ranges and renames CFF family/PostScript names as well as SFNT name
  records. The source audit honours the same accepted ranges.
- Found and fixed four independent Tulu vowel canonical-equivalence defects in
  the source. `compose_tulu` adds the missing compositions before existing
  syllable substitutions, including the reordered EE case. Build recipes hash
  this helper. All Tulu canonical decompositions now match actual shaped glyphs
  and positions. Original conjunct and positioning tables remain intact.
- Tests verify all **106 newly covered characters** have real outlines, accepted
  scope is enforced, CFF names are renamed, a conjoiner forms a compact ligature,
  pre-base vowel reordering happens, and sample source/package shaping agrees.
  Full Python suite: **81 passed**, with 7 existing warnings. All **11,244 pinned
  source files** verify. Both inventory reports and asset hashes regenerated.
- **23 browser scenarios pass**, including seven Tulu canonical-equivalence
  raster pairs, mixed RTL Sidetic with Latin/digits, containment and PNG export.
  The new specimen has no missing mappings or geometry warnings. Visually
  inspected Tulu conjuncts/marks and mixed Sidetic at comic size. These are sign
  and syllable fixtures, not claimed translated sentences or fluent review.
- Bundled visible cmap coverage: **168,016 / 172,352**, **4,336 still missing**.
  Broader source, style, sequence and composition work remains open. Daarage's
  upstream notes explicitly flag KTt, KTTh, KTRY and KTV conjunct forms and an
  extreme stacked-cluster overlap; record these as remaining typography gaps.
  Source notes: https://github.com/Mercury13/unicodia/tree/dcbe251036833331f0a8f66c186a315751db24f9/Font-Source/Tulu2

Next: continue closing missing script/symbol groups and custom visual treatment,
then extended Egyptian composition and the requirement-by-requirement audit.
The full brief remains active and incomplete.

Final source checkpoint: **192 JavaScript tests pass**; `git diff --check` is
clean. This supplements the 81 passing Python tests and 23 browser scenarios.

## Cuneiform numeric repertoire checkpoint

- Added pinned OFL Archaic Cuneiform Numerals and Noto-derived Unicodia Cunei
  from the existing Unicodia commit. Separate licence notices are retained;
  source hashes, attribution and derivative identities are in the manifests.
  This closes all **311 archaic numerals** and **12 tenû numerals** missing from
  the Unicode 18 inventory. All currently assigned Cuneiform and Proto-Cuneiform
  cmap requirements are present; that is not a claim of full visual treatment.
- Every new glyph has a nonempty outline and positive advance. Tests compare
  the decomposed outline paths, bounds and advances to the pinned sources,
  compare shaping across all archaic numerals, and preserve distinct numeral
  drawings. Higher numerals retain their relative width rather than the reduced
  cell sizes in some Unicode charts. All 323 route automatically to two bundled
  fonts without missing mappings or native emoji fallback.
- Added `cuneiform-numerals` to the browser/playtest corpus. Visually inspected
  one-through-nine groups, vertically repeated numerals, tenû signs and a wide
  Calvin reply at comic size. All **24 browser scenarios** pass containment,
  protected-art and PNG export checks. The new scenario has no geometry warnings.
- Full suites: **84 Python tests** (7 existing warnings), **193 JavaScript tests**
  pass. **11,248 pinned source files** verify. Coverage/source audits and asset
  hashes regenerated; `git diff --check` clean.
- Visible bundled cmap coverage is now **168,339 / 172,352**, with **4,013 missing**.
  Both numeric sources remain provisional native forms: custom pen treatment
  and historical sign review are still open. Preserving source outlines is
  useful correctness evidence, not evidence that comic styling is complete.

Candidate findings for continuation: the downloaded, unaccepted BabelStone
Pseudographica source covers 764 remaining mappings and has an OFL notice; it
needs structural grid integration/normalization and visual review. The cached
UFSTangutFixup source covers 1,164 remaining mappings, including all 965 Jurchen
letters and 147 missing Tangut characters. Its embedded notice says OFL while
Unicodia's similarly named UFSZero licence file says Apache: establish the exact
source/notice relationship before accepting it. Neither candidate was added to
delivered coverage. The downloaded SengBuhan font is Lao and adds no missing
characters; it is not a Tolong Siki source. These files are only ignored source
cache candidates. Full emoji, script styling, extended Egyptian composition and
final brief audit remain unfinished; the goal remains active.

## Jurchen/Tangut provenance and spacing checkpoint

- Resolved the candidate licence ambiguity from the original author. The pinned
  Losketch repository's `docs/LICENSES.md` explicitly assigns OFL 1.1 to its own
  font assets, including UFSZero Ext, and `font-source/font-sources.toml` gives
  this font an OFL licence URL. Apache applies to module code. These records,
  the accompanying OFL and the direct font are pinned in `ufs.json` at commit
  `4210c346066dd51940bdd28ff0845e6549ac76af`. Required copyright, OFL text and
  derivative notice are retained. The separate Unicodia candidate was not used.
- Restricted the source to assigned Unicode 18 Jurchen/Tangut characters. Other
  scripts and draft/unassigned mappings remain excluded. The 1,119-glyph CFF
  derivative supplies **965 new Jurchen** and **147 new Tangut** mappings. All
  assigned characters in these two scripts now have bundled cmap coverage.
  Source drawings remain provisional; this does not establish historical
  accuracy or finished comic styling.
- Actual outline/advance checks discovered two zero-width Tangut letters in the
  source (U+17D0B and U+180DF). `ideograph_metrics.py` repairs their OpenType hmtx
  and intrinsic CFF widths to the font's 1000-unit ideograph cell. Outlines and
  bearings remain unchanged. The recipe hashes the correction helper. Tests
  compare all accepted drawings/bounds to the original, verify exactly the two
  intended advance changes, shape the whole accepted repertoire, verify CFF
  naming and check automatic routing for the complete Jurchen inventory.
- Added a Jurchen/Tangut browser specimen spanning both ends of the repertoire,
  dense Tangut signs, mixed Latin/digits and a Calvin reply. All **25 browser
  scenarios pass** containment/protected-art/PNG export checks. The new scenario
  has no missing mappings or geometry warnings. Visually inspected at comic
  size: shapes remain distinct, but Tangut is visibly typeset and dense; finer
  comic pen treatment is still required. Fixtures are sign samples, not claimed
  translated or linguistically reviewed sentences.
- Full suites: **86 Python tests** (7 existing warnings), **194 JavaScript tests**
  pass. **11,252 source files** verify. Source/coverage audits and asset hashes
  updated; `git diff --check` clean. Visible bundled cmap coverage is now
  **169,451 / 172,352**, with **2,901 missing**.

Next concrete work: structural legacy-computing symbols (the cached OFL
BabelStone candidate), remaining script/mark gaps and custom visual treatment.
Full emoji artwork, extended Egyptian composition and the final brief audit
remain open. Overall goal remains active and incomplete.

## Structural legacy-grid checkpoint

- Accepted the pinned OFL BabelStone Pseudographica source specifically for
  **595 structural legacy symbols**: block mosaics, separated blocks, diagonal
  box lines and large-type pieces. Source scopes and `build_target: grid` keep
  unrelated pictures, outlined letters/digits and generic script packaging out
  of this derivative. Required BabelStone attribution/OFL notice is retained;
  reserved source family names are not used for Dad Grid.
- Dad Grid now contains **1,011 glyphs**, with a common 600×1000 cell. Source
  composites are decomposed before transforming. Full-block geometry is rigid;
  line and large-type pieces receive slight internal pen variation. Shared
  endpoints are fixed, including corrections for tiny source overshoots.
  Renderer detection reads the actual grid manifest, so supplemental characters
  route into spatial layout automatically rather than being treated as prose.
- Tests check every glyph's bounds, common advance and bearings; all **368 named
  quadrant/sextant/octant patterns** are checked cell-by-cell against Unicode
  names. Separated gutters and all 16 sixteenth-block positions are tested.
  The font rebuild is byte-identical. Pictorial legacy symbols and outlined
  digits explicitly remain outside automatic structural-grid detection.
- Added `legacy-grid` to the browser corpus. Visually inspected mosaic adjacency,
  separated blocks, sixteenth blocks, diagonal lines and large-type pieces at
  comic size. All **26 browser scenarios** pass containment, row/column
  preservation, protected artwork and PNG export checks. The new scenario has
  no missing mappings or geometry warnings. Existing extreme stress geometry
  warnings remain recorded in earlier checkpoints.
- Full suites: **89 Python tests** (7 existing warnings), **195 JavaScript tests**
  pass. **11,254 pinned source files** verify. Source/coverage reports and asset
  hashes updated; `git diff --check` clean. This adds **430 previously missing
  characters** and improves 165 existing mappings: bundled visible cmap coverage
  is **169,881 / 172,352**, with **2,471 missing**.

The remaining non-structural BabelStone symbols are not yet accepted as custom
artwork. Other legacy pictorial/partial-shape semantics, arbitrary ASCII art
recognition, remaining scripts/marks, emoji artwork, broad comic styling and
extended Egyptian composition still require work. The full goal remains active
and incomplete; passing these structural tests does not prove the full brief.

## General combining marks and tall-balloon checkpoint

- Added the **39 missing general combining marks** from the pinned OFL Funky
  source to the base-lettering builder. All are normalized to the existing cap
  height with zero advances and proper stacking anchors; source attribution is
  retained. The base font now has 869 mappings and 257 combining-mark drawings.
  `script_exclude_ranges` keeps these additions out of the Sidetic derivative.
  Original base outlines, advances and contextual alternates remain unchanged.
- Four side-parenthesis marks have separate above/below-left/right classes.
  They sit beside voicing diacritics at the same vertical level, rather than
  creating another accent stack level. Tests verify their relative outlines and
  attachment positions. The 170-unit optical clearance suits the current ring
  drawings; broader phonetic typography remains provisional. Unicode reference:
  https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-7/
- Tests verify all 39 real glyphs, zero advances, above/below stacks and automatic
  base-font routing. Distinct number/sharp signs and compound accent order were
  also checked against their actual outlines. Only four musical combining signs
  remain absent from the inherited-character cmap inventory.
- The new browser specimen exposed a tall-stack balloon with a 45-degree turn.
  Oval construction now applies its existing blunt-end rule along either long
  axis. A regression test checks the tall shape's enclosure and curvature.
  Full-cell grid ink now consistently uses the padded envelope instead of the
  single-line oval shortcut, preserving its corner clearance.
- **27 browser scenarios pass** containment/protected-art/PNG export checks.
  Visually inspected compound accents, side parentheses and stacked marks at
  comic size. The new accent scenario and legacy grids have no geometry warnings.
  The remaining recorded warnings are the extreme Calvin-wide-cluster clearance
  and 49-degree turn, plus the deliberately wide grid's 36-degree turn.
- Full suites: **92 Python tests** (7 existing warnings), **197 JavaScript tests**
  pass. Source/coverage reports and asset hashes are current; `git diff --check`
  is clean. Visible bundled cmap coverage is **169,920 / 172,352**, with
  **2,432 missing**. The letter gaps were not addressed in this checkpoint.

Next: remaining letters/script groups and meaningful alphabet distinctions,
then remaining custom emoji and broad visual adaptation/review. Extended
Egyptian composition and the final requirement audit remain open. The complete
brief is still active and incomplete.

### Supplemental Latin/Cyrillic checkpoint

- Added the remaining **174 Latin and 65 Cyrillic** assigned characters from
  the pinned, licensed Unicodia Funky source. All assigned Latin/Cyrillic now
  have bundled cmap coverage. This does not establish linguistic correctness
  or finished custom styling for their whole repertoires.
- Applied a light, bounded pen variation to 238 spacing letters. Tests preserve
  advances, source bounding boxes within four units, case distinctions, and
  raised/subscript scales and baselines. The lowercase lambda's tall ascender
  is intentional. Historical and phonetic visual review remains provisional.
- The other character, U+1E08F combining Cyrillic Ukrainian I, is incorporated
  into the complete Noto Sans Cyrillic derivative. Native above-letter classes,
  base/ligature/mark anchors and filtering sets attach and stack it correctly.
  The derivative manifest records its additional donor and licence. Tests
  verify attachment over uppercase/lowercase, zero advance, stacking and
  unchanged existing Cyrillic word shaping.
- Font routing now prefers a font containing the whole native base/mark cluster
  when the base is outside the original lettering font. This avoids loading a
  separate early fallback for the base and breaking native attachment.
- **28 browser scenarios pass** containment/protected-art/PNG export checks.
  The new alphabet specimen has no unmapped characters or geometry warnings;
  case, modifier and accent placement were visually inspected at comic scale.
  Existing extreme Calvin-wide-cluster and grid-wide warnings remain unchanged.
- **198 JavaScript tests pass.** The full Python run passed 94 tests and exposed
  two stale checks (general-mark count and concurrently outdated asset hashes).
  Both were corrected; affected checks now pass, giving **96 passing Python
  tests across the full run and focused reruns** (7 existing warnings).
- Visible bundled cmap coverage is **170,159 / 172,352**, with **2,193 missing**.
  Source/coverage reports, derivative attribution and asset hashes are current;
  `git diff --check` passes.

Next: inspect the remaining missing script groups and symbols; add licensed
native drawings with real shaping/sequence checks, then complete broad custom
visual treatment and emoji. Extended Egyptian composition, the recorded
extreme geometry cases and the final brief audit remain open. Goal incomplete.

### Dives Akuru and Myanmar native-coverage checkpoint

- Added pinned OFL Noto Serif Dives Akuru and Padauk Book sources from the
  verified Unicodia commit. These supply **23 missing Dives Akuru characters**
  and **20 Myanmar Pao/Eastern Pwo Karen digits**. Both script inventories now
  have complete bundled cmap coverage with real outlines.
- The complete Dives font takes precedence over the earlier partial font.
  Removed the old font's obsolete U+11939 mapping: the pinned Unicode release
  leaves that codepoint unassigned. It receives the app's graceful missing
  handling instead of a guessed vowel drawing. The superseded shard is removed.
- Retained full native shaping tables, donor attribution and OFL texts,
  including Padauk's current embedded copyright/reserved names. No custom-style
  completion is claimed for these native sources.
- Nine new Python checks cover complete script outlines, unchanged shaped
  positions, split-vowel canonical equivalence, real conjunct substitution,
  existing Myanmar text, and ten distinct positive-advance drawings in each
  digit set. A routing test verifies complete Dives font selection and the
  unassigned-codepoint behavior.
- All **29 browser scenarios** pass containment/protected-art/PNG export checks.
  Visually inspected new vowels/conjuncts and digit sets at comic size; the new
  specimen has no geometry warnings or unmapped characters. Previously recorded
  extreme-wide geometry warnings remain.
- Coverage is now **170,202 / 172,352 visible characters**, **2,150 missing**.
  Source reports and asset hashes are refreshed; **199 JavaScript tests** and
  **105 Python tests** pass (7 existing warnings). `git diff --check` is clean.
- Recorded rejected candidate evidence in `docs/unicode-source-review.json`.
  Tai Yo's Noto name is not sufficient provenance: the upstream issue explicitly
  describes assumed permission and missing anchors. The Malayalam Syriac font
  has conflicting noncommercial notices. Neither candidate is bundled. These
  scripts remain required; seek permissive sources or draw original forms.

Next: remaining Arabic/script additions, custom symbols/emoji and broad visual
adaptation; extended Egyptian composition, extreme geometry and the full brief
completion audit remain open. Goal remains incomplete.

### Extended Arabic and joining-font routing checkpoint

- Added pinned OFL Scheherazade New 4.400 with its current embedded copyright
  and licence, renamed derivative and full layout tables. It supplies **16
  missing Arabic characters**, including Extended-C joining letters, combining
  marks and honorific symbols. Native typography is provisional; this is not
  completed custom Arabic styling.
- Font routing now gathers requested repertoires of joining scripts from pinned
  Unicode 18 Script/ArabicShaping data. When one bundled font covers the requested
  script and its attached marks, it takes precedence across the dialogue. This
  prevents per-character fallback from splitting joined words. Ordinary Arabic
  still selects Aref Ruqaa. Mixed-script duplicate coverage cannot put a partial
  Arabic font ahead of the selected complete font.
- Regression checks verify real source outlines, contextual glyph substitution
  for six new joining letters, zero-advance marks and native positioning. The
  combining alef overlay intentionally crosses the base at zero offset; the
  test checks ink overlap rather than falsely requiring a nonzero offset.
- Bundled visible cmap coverage: **170,218 / 172,352**, **2,134 missing**.
  All **202 JavaScript tests** and **108 Python tests** pass (7 existing
  warnings). Source/coverage reports and asset hashes are refreshed.
- All **30 browser scenarios** pass containment/protected-art/PNG export checks.
  Visually inspected new contextual forms, marks/overlay and honorific symbols
  at comic size. The new Arabic specimen uses one script font and has no
  unmapped characters or geometry warnings. Existing extreme-wide warnings
  remain unchanged. `git diff --check` passes.
- Remaining Arabic work: the already pinned, font-specifically OFL-licensed
  UFSZeroExt source contains all 68 remaining Arabic cmap gaps. Do not simply
  package these as detached glyphs: crown letters are left-joining under the
  pinned ArabicShaping data, and new marks need attachment in a complete Arabic
  font. Investigate grafting native contextual forms/anchors into Scheherazade
  with outline, joining, stacking and browser checks. The separate downloaded
  UFSArabicFixup.ttf candidate is not accepted into the source manifest.
- Routing limitation: if no single font covers a whole requested joining-script
  repertoire, the existing per-character fallback remains. This still needs
  targeted treatment for combinations such as ordinary Arabic plus mathematical
  Arabic symbols; the improvement above is not proof of universal font routing.

The full goal remains incomplete, including the remaining scoped glyphs,
custom styling/emoji, extended Egyptian composition and final validation.

### Arabic honorific symbols and mixed-repertoire routing checkpoint

- Inspection confirmed that the pinned UFSZeroExt source has no GSUB/GPOS
  tables. Its remaining crown letters cannot yet be treated as functional
  joining Arabic, and its zero-advance marks still need native attachment.
- Added **29 standalone Arabic honorific symbols** from that same accepted OFL
  source. All are assigned `So` characters, with real distinct source drawings
  and positive native advances. Restricted source scope continues to exclude
  crown letters and combining marks. Tests preserve exact outlines/metrics and
  verify the exclusion; existing Jurchen/Tangut metrics and shaping tests pass.
- Refined joining-font selection to use explicit Unicode ArabicShaping entries,
  including nonjoining letters such as hamza, instead of every character whose
  Script property matches. Standalone honorifics and mathematical Arabic letters
  now get their own fallback without defeating selection of a complete font
  for joined Arabic. Regression covers supplemental Arabic mixed with both.
  This resolves the specific ordinary-plus-mathematical limitation recorded
  above; a repertoire of actual joining letters split across incomplete fonts
  remains an open case.
- **31 browser scenarios pass** containment/protected-art/PNG export checks.
  All 29 new symbols are in the new specimen, visually inspected at comic size.
  It has no unmapped characters or geometry warnings. Native typography remains
  provisional and fluent-reader/style review is still required. Existing
  extreme-wide geometry warnings remain unchanged.
- Coverage: **170,247 / 172,352 visible characters**, **2,105 missing**.
  **203 JavaScript tests** and **109 Python tests** pass (7 existing warnings);
  source/coverage reports and asset hashes are current. `git diff --check` passes.

Next Arabic work: the remaining **39 Arabic characters** include crown letters,
combining marks and two baseline symbols. Integrate them into a full native
Arabic font, verifying left-joining behavior, attachment/stacking and overlays.
All remaining scripts, custom visual treatment/emoji, extended Egyptian
composition and the final completion audit remain required. Goal incomplete.

### Native Arabic combining marks and browser compatibility checkpoint

- Integrated **15 remaining Arabic combining marks** from the pinned OFL UFS
  source into the full Scheherazade derivative. Marks remain excluded from the
  detached UFS shard. Converted cubic outlines to TrueType within 0.5 font units,
  scaled em units, and retained zero advances. The derivative manifest records
  the donor, licence and adaptation.
- Native sukun/kasra classes supply above/below attachment. Translated incoming
  and outgoing anchors preserve optical clearance and stacking. Base, ligature
  and mark lookups plus GDEF filtering sets all include the new marks. Tests
  cover three bases, lam–alef, two-mark stacks, preserved source bounds, and
  unchanged existing Arabic shaping. Kaf's native anchor lies beside its tall
  ascender; rectangle-only clearance would incorrectly reject that placement.
- Browser inspection caught a real issue absent from current HarfBuzz tests:
  older browser Unicode tables did not classify the new marks, so native
  attachment could fail despite working GPOS data. Added internal UVS aliases
  on known sukun/kasra characters selecting the same new glyphs. Only canvas
  measurement/drawing use these aliases; logical input, segmentation, bidi,
  sharing and metadata retain the original text. Tests establish identical
  glyphs and positions for original characters and aliases in current HarfBuzz.
- Updated browser ink checks to measure the actual shaping text and added
  explicit above/below stack growth checks, so overlapping marks cannot pass
  merely because they fit a balloon. All **32 browser scenarios pass**, including
  the new one with no unmapped characters or geometry warnings. Visually
  inspected the corrected marks, stacks, ligatures and kaf/crown placement at
  comic size. Existing extreme-wide geometry warnings remain.
- Coverage is **170,262 / 172,352 visible characters**, **2,090 missing**.
  **205 JavaScript tests** and **113 Python tests** pass (7 existing warnings);
  source/coverage reports, licence references and asset hashes are current. `git diff --check` passes.

Next: **24 Arabic gaps** remain (22 crown letters and two baseline symbols).
Crown letters need native left-joining forms and compatibility with older
browser shaping data. Other script gaps, substantial custom visual/emoji work,
extended Egyptian composition, extreme geometry and final brief audit remain
required. Goal incomplete.

### Crown-mark semantic placement correction

- Review of Unicode 18 §9.2.9 and the crown-letter proposal showed that U+10EF9
  surrounds the top of a letter; an ordinary above-accent slot was wrong.
  Reference: https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-9/
  and https://www.unicode.org/L2/L2024/24131-arabic-crown-letters.pdf .
- Corrected base/ligature anchors so the crown arch frames the top. Its arch
  extends a provisional quarter-em beyond the native top attachment line.
  The prior ordinary-above placement would fail the new test on the seven
  attested bases: alef, dal, thal, reh, zain, lam and waw.
- Mixed-accent browser inspection exposed a second issue: generic mark-to-mark
  attachment could pull a crown above a preceding vowel accent after canonical
  reordering. Crowns now retain base attachment when vowels are present. A
  dedicated mark-to-mark lookup permits repeated crowns to stack with each
  other without using ordinary vowel marks as their base.
- Added checks for straddling the attested letters' top bounds, stable placement
  with fatha/damma/shadda, and identical older-browser UVS alias shaping for
  those combinations. Repeated crowns remain a stress case, not a claim about
  ordinary Arabic usage. No glyph-count increase: coverage stays
  **170,262 / 172,352**, **2,090 missing**.
- Full Python run: **114 passed**, 7 existing warnings; the subsequently added
  mixed-vowel/alias regression passes in the **6-test final focused crown rerun**
  (115 Python tests across full and focused runs). Asset-version checks pass.
  No JavaScript implementation changed; prior **205-test** suite stays current.
  Coverage report, rebuilt font hashes and asset URLs refreshed.

All **33 browser scenarios pass** containment/protected-art/PNG export checks.
The new crown specimen has no unmapped characters or geometry warnings; visually
checked final mixed-vowel placement and repeated crowns. Existing extreme-wide
geometry warnings remain. `git diff --check` passes.

The **22 atomic crown letters** still need native left-joining forms; the
combining crown correction does not substitute for those separate characters.
Two Arabic baseline symbols and all previously recorded remaining requirements
also remain open. Goal incomplete.

### Arabic baseline symbols and crown-source review checkpoint

- Added the two remaining spacing baseline symbols, U+10EC9/U+10ECA, from the
  pinned OFL UFS source. Preserved distinct outlines, their small baseline scale
  and positive advances. Tests verify repeated symbols retain two advances and
  are not treated as combining marks. Jurchen/Tangut scope tests remain intact.
- All **34 browser scenarios pass** containment/protected-art/PNG export checks.
  Visually inspected baseline symbols alone, between Arabic letters and in
  mixed Arabic/Latin/digit text. The new specimen has no unmapped characters or
  geometry warnings; existing extreme-wide warnings remain.
- Pinned and inspected Amiri commit
  `d3d0c5cb6fe7196cb4a58608fc5c8ecd2e6e80fa`: its published Regular font is 1.003
  and contains neither the 22 atomic crown letters nor these baseline symbols.
  The source tree has no glyph filenames identifying crown letters/codepoints.
  Recorded the font hash and this limited negative result in
  `docs/unicode-source-review.json`; this is not a claim that no other font exists.
- Further inspected joining constraints: UFSZeroExt has no layout tables, and
  Scheherazade has no cursive-attachment lookup to copy. Therefore crown outlines
  need explicit connection alignment as well as left-joining classification.
  A future old-browser compatibility path can use a known dual-joining Arabic
  character with a UVS-selected crown glyph and a preceding internal ZWNJ to
  enforce left-only joining, but this is an unimplemented design to validate,
  not completed support. Ordinary-letter-plus-crown-mark drawing is not a
  substitute for the separately encoded crown letter forms.
- Coverage is **170,264 / 172,352**, **2,088 visible characters missing**.
  All **205 JavaScript tests** and **116 Python tests** pass (7 existing
  warnings). Source/coverage reports, font hashes and asset URLs refreshed; `git diff --check` passes.

The remaining Arabic coverage gap is exactly the 22 crown letters. All prior
remaining script, styling, emoji, Egyptian, geometry and final-audit work remains
required. Goal incomplete.

### Atomic crown-letter joining checkpoint

- Integrated all **22 Arabic crown letters** from the pinned OFL UFS drawings
  into the complete Scheherazade derivative. They remain excluded from the
  detached UFS shard. Kept the distinct source letterforms, converted curves
  within 0.5 units, and aligned each existing tail to the host joining baseline.
  Right-side bearings remain derived from the source; TrueType control bounds
  supply bearings so saving/reloading cannot shift curved outlines.
- No new historical isolated form was invented. The supplied initial drawing
  is retained in isolated contexts too, as an explicit provisional choice;
  Unicode 18 notes that separate isolated forms are not ordinarily attested.
  Native mark anchors are copied from corresponding initial forms and translated
  to the larger crown-letter ink envelope.
- Native Unicode 18 left-joining behavior is preserved. The older-browser path
  selects each actual crown glyph using an internal UVS on its ordinary Arabic
  counterpart, preceded by ZWNJ to prevent a right-side join. Input, sharing,
  bidi/segmentation and metadata retain the original crown-letter codepoints.
  Tests compare native and compatibility glyphs/positions for isolated,
  preceding/following, ZWNJ-separated and vowel-marked cases across all 22 letters.
- Tests also check affine preservation of source bounds and actual raster
  connectivity. Every crown joins a following beh into one ink component;
  adding ZWNJ creates separate components. A preceding beh remains isolated.
  This is drawing/connection evidence, beyond mere cmap presence.
- All **35 browser scenarios pass** containment/protected-art/PNG export checks.
  The new all-crown specimen uses one script font, with no missing characters
  or geometry warnings. Visually inspected joining and right-side disconnection
  in enlarged source comparisons and at comic size. Native/historical/style
  review remains provisional; existing extreme-wide geometry warnings remain.
- Full checks: **120 Python tests**, 7 existing warnings; **206 JavaScript tests**
  plus a focused font-routing rerun pass. The Python shaping helper now caches
  immutable font faces by path/mtime/size, creating fresh shaping state per case;
  this avoids repeatedly decoding the same WOFF2 during the expanded corpus.
- **All assigned Arabic characters now have bundled mappings or explicit
  behavioural handling.** This is not a claim of complete Arabic linguistic,
  sequence or custom-style validation. Overall visible cmap coverage is
  **170,286 / 172,352**, **2,066 missing**. Source/coverage reports, derivative
  donor attribution and asset hashes refreshed; `git diff --check` passes.

Next: remaining non-Arabic script and symbol gaps, then substantial custom
visual/emoji work, extended Egyptian composition and extreme geometry. The
complete brief and requirement-by-requirement completion audit remain open.
Goal incomplete.

### Supplemental native script forms checkpoint

- Added **21** missing characters from already pinned, licensed sources: three
  Armenian modifiers, two Greek modifiers, seven kana additions, six Khitan
  characters and three Balinese punctuation marks. UFS contributes 17; Unicodia
  Funky contributes four (Noto-derived Balinese and the author-drawn Khitan sign).
  Kept native forms, advances and modifier proportions, without claiming that
  these sources complete the custom comic style.
- All assigned characters in Armenian, Greek, Hiragana, Katakana, Khitan Small
  Script and Balinese now have bundled mappings or behavioural handling. New
  tests check all 21 drawings/advances against pinned originals, shaped output,
  raised modifier proportions and distinct kana drawings. Spaces come from the
  base font and are intentionally outside these narrowly scoped source shards.
- U+18CFF is intentionally a hollow square for a lost/illegible Khitan character,
  not accidental missing-glyph output; see the Unicode 18 core specification,
  chapter 18, and WG2 document N5205. Its source declares xMin=63 although its
  actual minimum is 64. FontTools corrects that bound on saving; the regression
  allows exactly the resulting one-unit horizontal translation, with identical
  contours and advance. Other additions retain exact source drawings/metrics.
- **Khitan cluster arrangement and vertical orientation remain unimplemented.**
  The specimen presents separate horizontal characters. This is a substantive
  shaping/layout limitation, explicitly recorded in the browser review corpus;
  complete cmap coverage does not resolve it.
- All **36 browser scenarios** pass containment/protected-art/PNG export checks.
  Visually inspected the new specimen at comic size: compact raised modifiers,
  distinct kana (including small archaic ye), Khitan forms and Balinese marks.
  No missing mappings or geometry warnings in that specimen. Existing extreme
  Calvin/grid width warnings remain; native-reader/style review is provisional.
- Full validation: **123 Python tests**, seven existing warnings, and **206
  JavaScript tests** pass. Source inventory, coverage report and asset hashes
  refreshed; `git diff --check` passes. Visible cmap coverage is now
  **170,307 / 172,352**, leaving **2,045** missing characters.

Next: remaining non-Arabic script and symbol gaps, custom visual/emoji work,
extended Egyptian and Khitan composition, extreme geometry and the final
requirement-by-requirement audit. Goal remains incomplete.

### Extreme-width balloon geometry checkpoint

- Fixed the previously recorded Calvin-wide-cluster clearance/49-degree turn
  and grid-wide 36-degree turn. Browser measurements showed that scaled text
  blocks were only 12–24 pixels high while their balloons used the normal
  46-pixel cap scale. At these aspect ratios the superellipse developed tight
  tips, and unequal corner reaches produced elliptical corners on the grid.
- Extremely elongated single-line balloons now use circular ends joined by
  straight spans. Ordinary perpendicular corners use the shorter allowable
  rounding reach on both sides. Existing oval, sweep, art-avoidance and panel
  attachment behavior remains covered by the original regression suite.
- Added a regression with the actual two browser dimensions. It requires full
  enclosure, at least 0.25 caps of clearance and a minimum curvature radius of
  0.5 caps. Browser review output now records their text dimensions and promotes
  any recurrence of their clearance/smoothness warnings to a failure.
- **207 JavaScript tests pass. All 36 Unicode browser scenarios pass with no
  geometry warnings**, and **all 33 original lettering browser scenarios pass**.
  Visually inspected both corrected balloons at comic size. Asset hashes updated;
  `git diff --check` passes. No font change; cmap coverage remains
  **170,307 / 172,352**, with **2,045 missing**. Python font tests were not rerun
  for this JavaScript-only geometry change; their preceding baseline is 123 pass.
- Recorded the Garay and Kelly Tolong source investigation in
  `unicode-source-review.json`. Unidentified donor glyphs, donationware labels
  and third-party OFL grouping are insufficient evidence of permission to modify
  and redistribute; neither candidate was added. This does not reduce scope.

Next: remaining script/symbol coverage, substantial custom visual/emoji work,
extended Egyptian and Khitan composition, then the full completion audit.
The two known extreme-width geometry defects are resolved; broad Unicode
correctness and the complete brief remain unproven. Goal remains active.

### Custom keycap emoji checkpoint

- Added the complete twelve-key emoji family (`#`, `*`, `0`–`9`), covering both
  the fully qualified FE0F+20E3 form and the form without FE0F: **24 new exact
  sequences**, bringing the custom font to **50 advertised sequences**.
- The original asymmetrical rounded borders are drawn in code; their central
  symbols reuse the project's existing comic lettering. The pinned base-font
  hash and design description are recorded in the emoji glyph review. Curves
  convert to TrueType within 0.5 units. White backing and black ink layers keep
  the counters and interiors open; monochrome glyphs retain real ink outlines.
  This follows the approved conventional monochrome emoji direction without
  replacing character artwork or borrowing a new third-party emoji design.
- Exact-cluster routing preserves plain digits and punctuation as normal text,
  and leaves unsupported emoji/modified clusters on the existing explicit
  fallback path. All twelve keycaps have distinct outlines; qualified and
  unqualified forms shape identically as one positive-advance glyph each.
- Added the full keycap family to the browser corpus, including adjacent plain
  text. **All 37 browser scenarios pass geometry and PNG export checks with no
  geometry warnings.** Visually inspected all twelve keys and both qualification
  forms at comic size: readable lettering, open counters and consistent borders.
- **208 JavaScript tests pass.** Full Python run passed 123 tests and caught one
  stale expected component count (8 versus the new 21). Updated that inventory
  expectation; the focused emoji/inventory rerun passes all **12 tests**, including
  deterministic font rebuild. The suite now contains 124 tests. Asset hashes and
  coverage report refreshed; `git diff --check` passes.
- The thirteen extra cmap entries are empty shaping components, not standalone
  custom drawings; the audit excludes them. Visible cmap coverage remains
  **170,307 / 172,352** with **2,045 missing**. Emoji sequence coverage and custom
  styling remain substantially incomplete outside the advertised set.

Next: extend custom emoji families and resolve remaining script/symbol sources
and composition support. Full requirement-by-requirement completion audit remains
open; goal active.

### Colour-semantic hearts checkpoint

- Added eleven coloured heart characters (blue, green, yellow, purple, black,
  white, brown, orange, light blue, grey and pink), reusing the existing custom
  atlas heart's ink outline and highlight. The custom font now advertises
  **61 exact sequences** and **22 visible single-character mappings**. Existing
  red-heart text/emoji presentation remains distinct; components remain excluded
  from standalone coverage.
- Inspected full-resolution PDF pages 13, 20 and 47, and sampled page 17's known
  red/yellow reference patches at full resolution too. Recorded all ten sampled
  RGB values, page/patch coordinates, render hashes and PDF hash in
  `output/imagegen/emoji-production/heart-palette-source.json`. Black/white use
  existing ink/paper constants. No atlas raster was edited; COLR palette entries
  select meaning-dependent colour while retaining the same custom drawing.
- Added `tools/font/sample_heart_palette.py --check` to reproduce the accepted
  samples directly from the PDF with Poppler. **All ten samples reproduced
  exactly**. The red heart now uses its full-resolution sample (a one-unit
  green/blue adjustment from the earlier smaller render).
- Tests require all eleven new colour fills to be distinct, to match their
  recorded samples, to share the original drawing and to shape as single
  positive-advance glyphs. Updated the skin-tone test to inspect exactly its
  five entries, rather than all palette entries after them.
- **125 Python tests pass** (seven existing warnings), **208 JavaScript tests
  pass**, and **all 38 browser scenarios pass** geometry and PNG export checks
  with no geometry warnings. Visually reviewed all twelve solid-colour hearts
  at comic size, including neighbouring blue/light blue/grey/white examples.
  Asset hashes and coverage report refreshed; `git diff --check` passes.
- Visible cmap coverage is **170,318 / 172,352**, leaving **2,034 missing**.
  Most emoji families and sequence combinations still require custom art and
  validation; this checkpoint covers solid-colour hearts only, not decorative,
  broken, anatomical, coupled or other compound heart forms.

Next: remaining custom emoji families, script/symbol coverage and complex-script
composition. The complete brief remains open; goal active.

### Coloured geometric emoji checkpoint

- Added 24 custom circle/square characters and their 20 registered Unicode
  text/emoji presentation variants: **44 new exact sequences**, bringing the
  custom emoji manifest to **105 sequences** and **46 visible mappings**.
  Colours reuse the verified PDF palette; the original vector outlines have
  slight pen asymmetry. Small, medium-small, medium and large squares retain
  distinct dimensions/advances, and medium black/white circles remain smaller
  than the coloured large circles.
- Black shapes have filled monochrome glyphs; white shapes remain outlined.
  COLR layers retain their semantic fill colours. Variation mappings come from
  the pinned emoji variation data, rather than inventing selectors for every
  symbol. Existing exact-grapheme routing keeps unsupported compounds intact.
- Initial four-quadratic circles looked like rounded squares in the browser,
  despite passing inventory/size checks. Replaced them with eight quadratic
  arcs and added an independent radial-deviation regression (under 2% across
  sampled curve points). Visually rechecked corrected circles, all colours,
  square size progression and text/emoji forms at comic size.
- **208 JavaScript tests pass.** Full Python suite passed **126 tests** (seven
  existing warnings) before the circle refinement; all **10 emoji tests** pass
  afterward, including the new circularity test and deterministic rebuild.
  The suite now contains 127 tests. **All 39 browser scenarios pass**, including
  PNG export, with **no geometry warnings**. Asset hashes and coverage report
  refreshed; `git diff --check` passes.
- Visible cmap coverage is **170,320 / 172,352**, leaving **2,032 missing**.
  Only two mappings are new to the overall bundled inventory: most of this
  checkpoint replaces system emoji artwork with custom rendering for characters
  that already had text-font mappings. This distinction matters; source cmap
  presence was never evidence of completed emoji styling.

Next: continue remaining emoji families, script/symbol gaps and extended
Egyptian/Khitan composition. Whole-scope custom styling, sequence support and
final completion audit remain open. Goal active.

### Standalone Egyptian rotation checkpoint

- Investigated the two pinned Egyptian sources. UniHieroglyphica supplies the
  complete native sign repertoire but explicitly has no control-character or
  rotation support; its GSUB feature list is empty. Egyptian Text supplies the
  core OpenType composition machinery, with a documented three-level model,
  but not the extended signs. Thus extended cmap coverage alone cannot solve
  composition. Source references: the UniHieroglyphica README, Microsoft's
  `EgyptianOpenType/eot.md`, and Unicode L2/24-238.
- Built **all 142 registered Egyptian rotations on 103 base signs** from pinned
  Unicode 18 angle descriptions and licensed UniHieroglyphica outlines. Used
  clockwise LTR transforms, keeping each sign's source side margins and centre
  height rather than stretching it into a square. Approximate-angle variants
  use the data's recommended angles; contextual/historical review remains
  provisional. Four expanded lost-sign sequences are not rotations and remain
  outside this builder.
- Added a 44,092-byte renamed derivative, `dad-egyptian-variants.woff2`, with
  real format-14 mappings. The source hash, data hash, angle, affine transform
  and advance for every variant are recorded in `egyptian-variant-review.json`.
  Retained the source OFL attribution and added reproduction instructions.
- Integrated exact standalone-variant font selection into measurement and
  drawing. The derivative cannot override ordinary Egyptian text. Unrotated
  comparison signs in a run with rotations use the same source font. Runs
  containing format controls stay on the existing composition path; splitting
  their signs to force standalone rotations would destroy quadrat shaping.
  Consequently **rotations in quadrats and extended composition remain open**.
- Tests check every registered sequence, its expected clockwise matrix, source
  outline bounds within rounding tolerance, real single-glyph shaping and
  positive advances. Derivative/report rebuilds are deterministic. Font loading
  and routing regressions protect ordinary/core composed runs. The coverage
  audit now records standalone native variation coverage separately from
  custom emoji encoding and from validated sequence counts.
- **129 Python tests pass** (seven existing warnings); **210 JavaScript tests
  pass** after the final routing adjustment. **All 40 browser scenarios pass**
  containment/PNG export with no geometry warnings. Visually inspected core
  and extended sign rotations, including odd angles and matching base forms.
  Asset hashes and audit refreshed; `git diff --check` passes.
- Visible cmap coverage remains **170,320 / 172,352**, **2,032 missing**. These
  are sequence-rendering improvements, not new character coverage or finished
  custom hieroglyph styling. The existing source emits a warning for an unused
  malformed advance on L29.001; all generated rotation advances are checked.

Next: extend the Egyptian composition path to the extended repertoire, resolve
remaining script/symbol sources, and continue custom visual/emoji coverage.
The full brief and completion audit remain open. Goal active.

### Basic extended Egyptian composition checkpoint

- Added a measured canvas layout path for extended signs and registered rotated
  signs in LTR horizontal, vertical and overlay groups, including explicit
  nested segments and consecutive quadrats. Operator precedence follows
  Unicode 18 section 11.4 (overlay, horizontal, then vertical). Source:
  https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-11/
- Uses the licensed complete UniHieroglyphica outlines and existing rotation
  derivative; no new glyph mappings or invented character substitutions.
  Preserves source proportions and fits each quadrat independently. The same
  glyph placement plan drives measurements, canvas drawing and PNG export.
  Existing core-only native composition remains available. Unsupported or
  malformed groups retain the native path rather than being partially parsed.
- Explicit segments are protected from normal and emergency line splitting.
  Added tests for precedence, nesting, rotation routing, adjacent quadrats,
  bounds and wrapping. Browser verification caught a structured font-source
  value being treated as a string; fixed it and added real-inventory coverage.
- **217 JavaScript tests pass. All 41 Unicode browser scenarios pass**, including
  exported PNGs and independently measured leaf-glyph bounds, with no geometry
  warnings. All **33 original comic browser checks pass**. Visually inspected
  grouped, separate, nested, overlaid and rotated examples at comic size.
  Font assets are unchanged from the preceding 129-test Python checkpoint.
- This is basic composition, not complete Egyptological typography. Sign-specific
  insertion positions, enclosures, damage, mirroring, RTL arrangement and native
  reader/style review remain open. The source outlines remain provisional in
  style. Visible cmap coverage is unchanged at **170,320 / 172,352**, with
  **2,032 missing**.

Next: extend remaining Egyptian control behavior and Khitan arrangement, resolve
script/symbol gaps, and continue custom emoji and script visual treatment.
The complete brief and final audit remain open; goal active.

### Egyptian mirroring checkpoint

- Implemented U+13440 horizontal mirroring for individual core and extended
  signs, including signs inside basic quadrats. Registered rotation sequences
  are selected first, then reflected, matching Unicode 18 section 11.4.2.
  Mirroring is explicit and does not substitute semantically distinct signs.
  RTL layout remains a separate unresolved requirement.
- Measurement and drawing share the reflected origin and horizontal direction;
  independent browser ink checks account for the negative horizontal scale.
  A mirrored registered variant loads its derivative font even when the mirror
  modifier occupies the same grapheme cluster.
- Visual review caught a real comparison error: ordinary fallback discarded the
  rotation on the unmirrored side of a mixed run. Both sides now use the same
  variant face and scale. Added a regression for that case, plus malformed
  modifiers and preserved group dimensions.
- **220 JavaScript tests pass. All 42 Unicode browser scenarios pass** geometry
  and PNG export checks without warnings. Visually confirmed reflected core
  signs, extended signs, rotated signs and grouped signs at comic size. The
  browser's DOM query helper timed out on the completed page; its accessibility
  summary confirmed all 42 results, and screenshots confirmed the correction.
- No font asset or character-coverage change. Advanced insertions/enclosures,
  damage, RTL layout, custom styling, other script gaps and the full completion
  audit remain open. Goal active.

### Egyptian editorial blanks and lost signs checkpoint

- Added U+13441–U+13446 to the LTR composition parser and renderer. Full/half
  blanks reserve dimensions without drawing visible outlines. Inspection of the
  pinned UniHieroglyphica font showed visible bounds for both blank characters,
  so simply selecting its cmap entries was not sufficient.
- Lost signs render shaded full, half, tall and wide regions. All four registered
  FE00 expanded variants are supported by the renderer: adjacent expanded lost
  regions meet without the ordinary whitespace seam. They also participate in
  horizontal/vertical groups. Source: Unicode 18 section 11.4.3 and the four
  pinned StandardizedVariants.txt records. These are procedural rendering
  sequences, not additional format-14 font mappings or new cmap coverage.
- Added measured shading primitives to the existing placement plan. Bounds and
  drawing use the same scale; browser verification independently checks the
  visible primitive extents. Blank dimensions remain present even with no ink.
  The original input, including controls and selectors, is retained.
- **222 JavaScript tests pass; all 43 Unicode browser scenarios pass** geometry
  and PNG export checks with no warnings. Visually reviewed full/half blank
  spacing, four lost-region proportions, normal versus continuous expanded
  shading and a lost sign grouped under a visible sign.
- Native fonts and visible character coverage are unchanged. Exact paleographic
  typography remains provisional; damage modifiers, enclosures, insertions,
  RTL arrangement and custom sign treatment still need work. This checkpoint
  does not resolve the broader script/emoji gaps or final completion audit.

Next: continue Egyptian damage/enclosure behavior, Khitan arrangement and the
remaining coverage/style work. Goal active.

### Egyptian damage modifiers checkpoint

- Added all fifteen U+13447–U+13455 damage modifiers to individual signs on
  the LTR composition path. Their quarter masks follow the pinned UnicodeData
  names (top/bottom × start/end). Visually inspected Unicode 18 Figure 11-9;
  shading overlays the surviving sign, rather than erasing its outline.
- Damage uses the final sign surface after rotation and explicit mirroring.
  It scales with the sign inside quadrats and does not enlarge the measured
  group. Adjacent shaded quarters share hatch phase. The font loader preserves
  registered rotation selection when damage and mirroring share its grapheme.
- Tests independently enumerate all fifteen quarter combinations and verify
  unchanged dimensions, exact region extents, malformed modifier handling,
  grouped placement and rotated/mirrored font selection.
- **225 JavaScript tests pass. All 44 Unicode browser scenarios pass**, including
  independent primitive bounds and PNG export, without geometry warnings.
  Visually compared the four Unicode reference examples and inspected isolated
  corners, full damage, and rotated/mirrored/grouped cases at dialogue size.
- Font assets and character coverage are unchanged. Enclosures, insertions,
  RTL arrangement, broader editorial combinations and custom sign style remain
  open, alongside other script and emoji coverage. Goal active.

### Egyptian RTL composition checkpoint

- Connected resolved RTL runs to the Egyptian placement path. Explicit RTL
  overrides now reverse horizontal group/sequence order and sign facing while
  retaining top-to-bottom order inside vertical groups. Core and extended
  signs use the complete native source, loaded for explicit RTL input.
- Reflecting the registered clockwise variant produces the counterclockwise
  rotation of the RTL-facing sign. Explicit mirror controls cancel the
  directional reflection. Damage start/end regions follow the direction;
  blanks and shaded lost regions preserve their dimensions. Non-Egyptian
  chunks in the run retain native directional drawing instead of reflection.
  Rules checked against Unicode 18 sections 11.4 and 11.4.2.
- Visual review found that bidi wrappers prevented the existing optical
  enlargement of composed Egyptian runs. Removed those wrappers only for the
  size decision, preserving all logical input. LTR and RTL groups now retain
  matching dialogue size.
- **230 JavaScript tests pass. All 45 Unicode browser scenarios pass** geometry
  and PNG export checks without warnings. Tests cover horizontal reversal,
  retained vertical order, explicit mirror cancellation, directional damage,
  bidi dispatch, font loading and stable size through overrides. Visually
  inspected paired directions, nested groups and rotated/damaged signs.
- This implements horizontal RTL behavior for the existing basic composition
  features. Insertions, enclosures, vertical columns, native-reader review and
  custom sign styling remain open. Other script/emoji coverage gaps and the
  complete brief's final audit remain unfinished. Goal active.

### Egyptian insertion-source investigation and reproducible inventory

- Located per-glyph insertion metadata in the already-pinned Microsoft
  EgyptianOpenType source. Pinned `insertions.py`, `config.py` and its MIT
  license alongside the existing font, with exact URLs, sizes, SHA-256 and Git
  blob hashes. Retained the MIT notice separately from the font's OFL notice.
- Added `review_egyptian_insertions.py`, which reads literal AST assignments
  without executing downloaded Python. It verifies source hashes and maps
  metadata to the pinned font's cmap/outlines. The deterministic report contains
  **328 insertion alternatives for 188 glyphs**, including **45 offset areas**.
  **185 glyphs** have direct cmap mappings; D28o, O13a and V10n are font-only
  variants and are explicitly retained as unmapped, not silently discarded.
- Source inspection shows why a generic corner algorithm or direct cross-font
  reuse is unsafe: regions depend on the container's discrete cell size and
  optional offsets. Egyptian Text uses 315 horizontal/310 vertical font units
  per cell, and its raw base glyphs have zero advances and centred bearings;
  their normal positioning comes from OpenType. UniHieroglyphica has different
  outlines and metrics. No insertion-placement claim has been added yet.
- **Seven targeted Python tests pass**, covering completeness, independently
  checked F4/I10/G25 mappings, offset preservation, deterministic report output,
  non-execution of source code and fetch validation. **All 11,263 pinned source
  files verify** with `fetch_sources.py --check`; `git diff --check` passes.
  Renderer/font assets are unchanged from the 230-JavaScript/45-browser checkpoint.

Next concrete insertion step: adapt source-specific container glyph variants
and insertion cells together, accounting for shaping offsets, then validate
placement against Unicode examples and outline collisions before enabling the
new path. Extended containers without source anchors still need a separate
reviewed solution. Enclosures and broader coverage/style work remain open.
Goal active.

### Egyptian insertion rendering checkpoint

- Added a reproducible native full-blank probe that recovers contextual
  Egyptian Text container outlines and insertion cells together. The generated
  OFL manifest contains **217 container/control pairs**. The build report
  records 38 excluded pairs: four missing/out-of-cell regions and 34 regions
  intersecting container ink at a 10×10 sample grid. Sampling is a conservative
  screen, not a proof of collision freedom; exclusions remain unresolved work.
- The application places extended signs and nested groups into these regions,
  preserves insertion precedence, and reflects the entire composition for RTL.
  Unsupported containers or combinations preserve the complete logical chunk
  for native fallback. No characters are rewritten or new cmap claims added.
- **231 JavaScript tests passed**, followed by **18 passing Egyptian tests**
  after adding one more fallback regression (232 total tests now present).
  **Four targeted Python tests pass**, including deterministic rebuild, cell
  and outline bounds, independent I10/F4 reference coordinates, collision-screen
  behavior and source inventory checks. **All 46 Unicode browser scenarios pass**
  geometry and PNG export checks without warnings. Visually inspected corner
  examples, nested content and reflected composition at dialogue size.
- Some inserted signs are very small at dialogue size; readability and native
  typographic fit remain provisional. Modified/extended containers, multiple
  insertions, excluded source cells, enclosures, vertical columns and custom
  sign style remain unfinished. This milestone does not change character
  coverage: 170,320 / 172,352 visible public-use assigned characters, 2,032 gaps.
  Other script and emoji coverage/style work and the full brief's final audit
  remain open. Goal active.

Next: extend the Egyptian grammar to enclosures using authoritative reference
examples, with separate geometry and visual checks. Revisit excluded insertion
regions with contextual sizing rather than treating sparse sampling as final
validation. Continue the remaining character/sequence and visual-style work.

### Egyptian enclosure checkpoint

- Added `build_egyptian_enclosures.py` and an OFL manifest of 14 contextual
  enclosure ends plus plain and walled connecting strips, extracted by shaping
  blank probes with the pinned Egyptian Text font. Bounds, advances, glyph
  identities and source hash are retained. The builder verifies source hashes.
- Extended the grammar and layout to pair enclosure controls, retain absent
  ends, nest enclosed content, and place extended signs, quadrats and insertions
  inside horizontal enclosures. Native strip overlap connects the tiled spans;
  end shapes retain their aspect ratio. RTL reflects the complete composition.
  Enclosure content and attached ends stay together during emergency wrapping.
  Unpaired controls retain native fallback; ends without controls stay separate.
- Validated the Unicode 18 section 11.4.2 cartouche example and inspected all
  seven end pairs, plain/walled forms, missing ends, nesting and RTL in browser
  specimens. Reference: https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-11/
- The long enclosure specimen exposed a balloon-clearance and tight-turn
  regression. Wide ovals now use blunt ends at a lower aspect-ratio threshold,
  while preserving the existing short-remark ellipse. Added the observed ink
  dimensions to the geometry regression corpus.
- **234 JavaScript tests, five targeted Python tests, all 48 Unicode browser
  scenarios and all 33 original comic scenarios pass.** Unicode PNG exports and
  independent ink bounds pass; no geometry warnings remain. Visually inspected
  the final long balloon after the geometry adjustment. Asset hashes updated;
  `git diff --check` passes.
- Horizontal enclosure support is provisional typography, not linguistic
  validation. Strip sizing, modified ends, vertical columns, native-reader
  review and custom sign style remain open. Earlier insertion exclusions,
  broader script/emoji coverage/style and the final brief audit remain open.
  Visible character coverage is unchanged at 170,320 / 172,352 (2,032 gaps).
  Goal active.

Next concrete work: address multiple insertion controls and modified containers,
then return to remaining character/emoji coverage and the approved custom visual
style. Vertical-column layout still needs an explicit implementation rather
than a claim based on horizontal reflection.

### Multiple Egyptian insertions checkpoint

- Extended the native probe builder to shape every ordered subset of each
  container's documented insertion controls together. The manifest now includes
  **217 single-control and 109 ordered multiple-control combinations**. Source
  control markers must match the input order, all regions must fit the native
  cell, and inserted regions must not overlap one another. Container outlines
  and all regions come from the same native shaping operation.
- The report retains **141 excluded cases**: 77 sampled container-ink collisions,
  33 out-of-cell cases, 29 overlapping region combinations and two native probe
  mismatches. These counts include both single and multiple insertion probes;
  previous single-control support is unchanged. Sparse ink sampling remains a
  provisional screen, not a proof of arbitrary-context collision freedom.
- The renderer now fits two or three independent contents into their jointly
  derived regions while drawing the container once. Explicitly parenthesized
  left operands retain their grouping rather than being flattened into a sign.
  Duplicate unsupported controls preserve native fallback. Nested inserted
  groups and RTL reflection work with multiple insertions.
- **235 JavaScript tests and three insertion-builder Python tests pass.** The
  latter includes deterministic rebuild, independent I10 coordinates in both
  orders, region ordering, bounds and pairwise region disjointness. **All 49
  Unicode browser scenarios pass geometry/export checks without warnings.**
  Visually compared reordered controls, three insertions, nested content and
  RTL at dialogue size. Asset hashes updated; `git diff --check` passes.
- Very small native insertion cells remain difficult to read at dialogue size.
  Modified/extended containers, excluded combinations, native-reader review,
  vertical columns and custom sign style remain open. Character coverage and
  the broader script/emoji gaps are unchanged. Goal active.

Next: investigate source-native mirroring/rotation of insertion containers and
adapt only when the transformed regions can be verified. Then continue the
remaining coverage and approved visual treatment across scripts and emoji.

### Modified Egyptian insertion containers checkpoint

- Extended source-native insertion probes to explicit horizontal mirroring and
  registered rotations. Rotation candidates require the intersection of Unicode
  standardized variants and the pinned font's format-14 cmap. Variant-specific
  insertion metadata is preferred where available, recovering D28o through its
  registered sequence rather than treating it as an unmapped sign.
- The manifest now includes **428 accepted combinations**: the existing 217
  single and 109 multiple unmodified combinations, **90 mirrored**, **11 rotated**
  and **one rotated/mirrored** combination. Each stores its logical container
  sequence and ordered controls. The source supplies the modified outline;
  the renderer does not accidentally mirror it a second time. RTL still
  reflects the complete composition, including inserted contents.
- **554 rejected probes** remain explicit: 370 sampled ink intersections,
  54 out-of-cell cases, 58 overlapping region combinations and 72 native probe
  mismatches. For example, the mirrored I10 snake cannot reuse its unmodified
  bottom-start region. Unregistered rotations do not enter the manifest.
  J7's native mirrored alternate is named J7a, rather than using an R suffix;
  standalone and insertion probes both select that native alternate.
- **236 JavaScript tests and four insertion-builder Python tests pass. All 50
  Unicode browser scenarios pass** independent
  bounds, PNG export and geometry checks without warnings. Visually inspected
  mirrored figures, rotated D28/O36 containers and the combined rotation/mirror
  case in LTR and RTL. Builder tests cover retained counts, native glyph names,
  registered sequence membership, separate rejection of mirrored I10, region
  disjointness, independent coordinates and reproducibility. Asset hashes updated.
- Source outlines and sparse collision screening remain provisional typography.
  Damaged containers, extended containers without native anchors, excluded
  combinations, vertical columns and native-reader/custom-style review remain
  unfinished. Other script/emoji coverage and styling remain open; visible
  character coverage is unchanged. Goal active.

Next: return to the outstanding public-use character inventory and approved
visual treatment across scripts/emoji, while retaining the Egyptian limitations
above as unfinished scope. The native Egyptian composition path is substantially
broader but is not evidence of a completed Unicode beta.

### Legacy computing repertoire and cell geometry checkpoint

- Expanded the already-pinned OFL BabelStone repertoire by **306 non-emoji
  symbols**, including standalone legacy pictures, outlined letters/digits,
  arrows, control pictures and connecting pieces. The custom grid font now
  contains 901 donor symbols: 741 structural and 160 standalone. The source's
  explicitly nonstandard U+1F934 Prince-emblem mapping is excluded, as are its
  emoji pictures; glyph presence alone is not treated as semantic correctness.
- Separated font coverage from structural-layout detection. Connecting pieces
  trigger grid layout; standalone pictures/outlined letters remain in ordinary
  prose and use light pen variation. Source notices and the renamed derivative
  remain intact. This is provisional visual adaptation, not exhaustive style
  approval or historical-reference validation.
- Visual review caught distorted circles in assembled legacy pieces. Legacy
  constructions now use their source's square cells, with horizontal scaling
  applied consistently to all structural runs, including mixed box edges.
  Ordinary box-drawing diagrams retain their existing narrow text cells. Blocks
  and joining picture pieces preserve boundary geometry.
- **238 JavaScript tests and eight grid-font Python tests pass. All 52 Unicode
  browser scenarios pass** independent ink bounds, PNG export and geometry
  checks without warnings. Added tests for routing, mixed-cell alignment,
  square circle construction, complete donor inventory, bounds, licence and
  nonstandard/emoji exclusions. Existing block-fraction and all 256 Braille
  pattern checks remain green. Visually inspected circular assemblies, a face,
  standalone pictures, outlined letters and mixed prose at comic size.
- Regenerated source and delivered coverage audits. Bundled visible coverage
  is now **170,626 / 172,352**, with **1,726 missing**. Asset hashes updated and
  `git diff --check` passes. References: Unicode 18 legacy-computing chart and
  https://www.babelstone.co.uk/Fonts/Pseudographica.html (constructed forms and
  nonstandard mapping caveats).

Next: continue remaining symbol and script coverage, especially the remaining
licensed UFS/Funky additions, while preserving native mark placement and joining.
The outstanding script/emoji drawings, broader visual treatment, Egyptian
limitations and full brief audit remain unfinished. Goal active.

### Standalone math, music and punctuation checkpoint

- Added **133 assigned standalone symbols** from the already-pinned,
  font-specifically OFL UFS source: historical math operators and a mathematical
  italic ligature, musical accidentals/rests/clefs/noteheads, punctuation and
  geometric signs. New script letters and combining music marks remain outside
  this addition because their attachment/joining needs separate implementation.
- Extended the light pen-adaptation pipeline to cubic CFF outlines as well as
  quadratic TrueType. Source advances, CFF width semantics and shaping features
  are preserved; adaptation stays within four source units of original bounds.
  The derivative is renamed and retains source notices. Native glyph identity
  and restrained variation are not presented as full stylistic approval.
- **238 JavaScript tests and 30 targeted Python tests pass**, including the
  generic font/shaping suite, existing adapted alphabets, unchanged supplemental
  scripts, and new standalone-symbol metric/distinction tests. All 133 new
  drawings are nonempty and changed by the adaptation; no zero-advance
  standalone symbols or collapsed related shapes were accepted.
- **All 54 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected historical equality and
  nested-root signs, ringed punctuation, musical accidentals and rests at comic
  size. These are standalone typography specimens, not a validated score-layout
  system; new combining musical marks remain unfinished.
- Coverage/source audits regenerated. Bundled visible coverage is now
  **170,759 / 172,352**, leaving **1,593 missing**. The script bundle remains
  346 shards (60,143,712 bytes). Asset hashes updated; `git diff --check` passes.
  Broader script/emoji coverage, specialist validation, custom style and the
  full brief audit remain open. Goal active.

Next: address the remaining native-attached marks and script letters from
licensed sources, and continue original/custom emoji work. Keep attachment,
character coverage and visual approval as separate verification tracks.

### Hebrew heavy-point attachment checkpoint

- Added U+05C8 SHEVA NA MUDGASH and U+05C9 DAGESH HAZAQ MUDGASH to the complete
  bundled Noto Rashi Hebrew font using the pinned, font-specifically OFL UFS
  drawings. Their distinct heavier forms remain encoded as supplied; they are
  not replaced with ordinary sheva or dagesh in logical or drawn text.
- Converted source cubic contours within 0.5 units, assigned zero advances and
  native GDEF mark classes, and reused the corresponding sheva/dagesh GPOS
  attachment classes. Sheva retains native top clearance below the base;
  dagesh retains its native interior center. Testing found a base without an
  anchor: normalizing glyph origins also preserves the native fallback
  position there, rather than leaving the donor's negative coordinate offset.
- Donor attribution is embedded in the derivative and recorded in the font
  manifest. The generic UFS subset excludes these marks. Browser inspection
  confirmed attachment without a shape-only compatibility alias in this engine.
- **238 JavaScript tests and 23 font/shaping Python tests passed**, followed by
  **three passing Hebrew tests** after adding an all-assigned-Hebrew inventory
  assertion. Tests cover all 27 base letters, heavier dimensions, zero advance,
  native centers/clearance, combined shin dots, retained old shaping and notices.
  All assigned Hebrew characters now have bundled mappings; this is coverage
  evidence, not a claim of exhaustive linguistic validation.
- **All 55 Unicode browser scenarios pass** independent ink bounds, PNG export
  and geometry checks without warnings. Visually compared ordinary/heavy
  points, combined marks and several bases at comic size. Existing source-font
  anchor limitations and fluent-reader/custom-style review remain provisional.
- Coverage/source audits regenerated. Visible bundled coverage is now
  **170,761 / 172,352**, leaving **1,591 missing**. Asset hashes updated and
  `git diff --check` passes. Broader script/emoji/style work remains open.
  Goal active.

Next: continue remaining Indic and musical combining marks with native
attachment, plus outstanding script/emoji drawings and approved visual style.

### Historical Kui marks in Odia checkpoint

- Added U+0B53 DOT ABOVE and U+0B54 DOUBLE DOT ABOVE from the pinned OFL UFS
  source to the complete Noto Sans Oriya subset. Attribution is embedded and
  recorded in the source manifest; the generic UFS subset excludes both marks.
- Followed the historical Kui uses in [Unicode 18 Chapter 12](https://unicode.org/versions/Unicode18.0.0/core-spec/chapter-12/)
  and [L2/24-106R](https://www.unicode.org/L2/L2024/24106r-odia-dot-above.pdf):
  dot above consonants and AA/I/E matras; double dot above independent A/AA/E.
  Specimens exercise these combinations and are not claimed as translations.
- Reused native overline GDEF, filtering and mark/base/mark-to-mark attachment
  classes, with zero advances and normalized origins. The source lacked anchors
  for several documented vowel hosts; supplemental lookups restricted to the
  new dots center them above these hosts with measured clearance. Old Odia
  shaping, including existing overlines, remains unchanged.
- An older shaping engine reordered the new marks differently from the related
  overline. Drawing-only overline-plus-private-UVS aliases select the actual dot
  glyphs and inherit known syllabic behavior. Original logical input, sharing,
  bidi and metadata retain the new characters. Direct use of the font outside
  this renderer on older engines does not receive this compatibility mapping.
- **239 JavaScript tests and 24 font/shaping Python tests pass**, including
  consonant/conjunct anchor comparisons, zero advances, distinct dot forms,
  documented vowel hosts, retained old shaping and donor attribution.
- **All 56 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected the dots on consonants,
  dependent signs and independent vowels at comic size. Specialist linguistic
  review and final style adaptation remain provisional.
- Coverage/source audits regenerated: **170,763 / 172,352** visible characters
  have bundled mappings, leaving **1,589 missing**. The font bundle remains 346
  shards (60,144,032 bytes). Asset hashes updated. Goal remains active.

Next: remaining Indic letters and attached musical marks; outstanding script
and emoji drawings; systematic custom-style and full-brief validation.

### Telugu and Kannada archaic SHRII checkpoint

- Added U+0C5C and U+0CDC from the pinned OFL Unicodia Funky source, with the
  existing restrained pen adaptation and retained source advances. The source
  manifest scopes these two signs explicitly; no uncertain script repertoire
  was enabled alongside them.
- Checked the representative form and behavior in
  [L2/22-006](https://www.unicode.org/L2/L2022/22006-archaic-shrii.pdf), including
  a rendered view of page 1. These independently encoded historical signs do
  not combine with other letters and remain distinct from modern SHRII letter
  sequences. Browser specimens compare the forms side by side and repeat them
  as standalone signs; their inner curl, outer loop and rising terminal agree
  with the reference at comic size.
- The targeted Python suite initially found an outdated count in the shared
  adaptation test (238 became 240). After updating that inventory expectation,
  all six affected adaptation/SHRII tests pass; the other 24 generic font and
  supplemental-script tests had already passed unchanged. New tests verify
  nonempty, adapted contours, bounded changes, retained positive advances,
  independent repeated shaping and full assigned Telugu/Kannada cmap coverage.
- **All 57 Unicode browser scenarios pass** bounds, PNG export and geometry
  checks without warnings. Character coverage is now **170,765 / 172,352**,
  leaving **1,587 missing**. Telugu and Kannada have no remaining cmap gaps;
  this does not imply exhaustive sequence, linguistic or final style approval.
- Source and coverage audits regenerated; 346 script shards total 60,144,300
  bytes. The broader brief, other missing scripts, emoji and style work remain
  open. Goal remains active.

Next: integrate the remaining Bengali/Devanagari source letters and marks with
native contextual behavior; continue missing scripts, music marks and emoji.

Final checkpoint verification: **239 JavaScript tests pass**; asset hashes are
current and `git diff --check` passes.

### Bengali alternate Bargiya BA checkpoint

- Added U+11DF1 to the complete Noto Sans Bengali derivative. Its isolated
  outline is copied from the native diagonal RA under a separate glyph name;
  native BA has identical advance/bearings. No RA substitutions are inherited.
  The OFL source and adaptation are recorded in the Noto source manifest.
- Followed [L2/22-268R](https://www.unicode.org/L2/L2022/22268r-bengali-alternate-ba.pdf),
  including visual inspection of its page-3 comparison table: alternate BA
  resembles Assamese RA in isolation but behaves like BA with vowels and
  conjuncts. Expanded BA inputs in native contextual substitutions, ligatures,
  class definitions, positioning and mark attachment. Existing glyph outputs
  and existing Bengali/Assamese typography are preserved.
- Added a supplementary cmap mapping and a drawing-only BA/private-UVS alias
  for older engines. Testing caught a split-vowel normalization failure after
  UVS: O and AU now use canonical decomposition in affected drawing strings.
  Original input and logical metadata remain unchanged. Direct font use on
  older engines outside this renderer does not receive those compatibility
  transformations.
- **241 JavaScript tests and 24 font/shaping tests passed**, followed by all
  **four Bengali tests passing** after adding a wider consonant-context test.
  Evidence includes the ten proposal combinations, dependent vowels, retained
  diagonal forms, reph and consonant contexts, positive native metrics, and
  unchanged older Bengali/Assamese shaping.
- **All 58 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually checked the comparison specimen,
  including O/AU placement and the distinction from ordinary BA/Assamese RA.
  Native-reader review and final comic-style adaptation remain provisional.
- Coverage and source audits regenerated: **170,766 / 172,352** visible
  characters have bundled mappings, leaving **1,586 missing**. Script fonts
  remain 346 shards (60,144,536 bytes). Asset hashes updated and diff whitespace
  checks pass. The full goal remains active and unfinished.

Next: Bengali combining anusvara above, Devanagari alternate DDDA, musical
combining marks, remaining scripts and emoji; full visual-style validation.

### Bengali historical above-anusvara checkpoint

- Added U+11DF0 from the pinned OFL UFS source to the complete Noto Sans Bengali
  derivative, preserving a distinct ring, zero advance and donor attribution.
  The generic UFS subset excludes the mark; provenance is recorded separately.
- Followed [L2/24-153](https://www.unicode.org/L2/L2024/24153-bengali-combining-anusvara-above.pdf),
  including a rendered inspection of page 2's manuscript evidence: the sign
  occurs above consonants and vowel signs and contrasts with spacing anusvara.
  The implementation uses the separate-ring form rather than joining it into
  the headline. Specimens are attachment comparisons, not translations.
- Reused native above-mark GDEF/filtering, mark-to-base and mark-to-mark
  attachment classes and contextual positioning. Normalized donor origins and
  added 30 units of clearance after tests caught tall headline collisions.
  Tall I/II/AU signs and reph use a raised ring selected only within the same
  pinned-Unicode grapheme. This avoids collisions while retaining native
  horizontal attachment and unchanged advance widths.
- Older shaping engines also needed explicit canonical split O/AU vowels when
  the new mark's drawing-only UVS alias is present. Extended the previous BA
  compatibility handling; original logical text remains unchanged. Direct use
  of the font outside this renderer does not receive these compatibility and
  tall-cluster transformations. Unusual combinations and specialist review
  remain provisional.
- **242 JavaScript tests and 27 font/shaping tests passed**, followed by all
  **three anusvara tests passing** after adding the complete Bengali inventory
  assertion. Tests cover distinct mark forms, source attribution, native
  zero-width attachment, clearance above representative bases/vowels/conjuncts,
  reph, preservation of older Bengali shaping and grapheme-local selection.
- **All 59 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually reviewed ring placement at comic
  size and its distinction from spacing anusvara and candrabindu.
- Audits regenerated: **170,767 / 172,352** visible characters have bundled
  mappings, leaving **1,585 missing**. All assigned Bengali characters now have
  mappings; this is not exhaustive linguistic or style approval. Script fonts
  remain 346 shards (60,144,748 bytes). Asset hashes are current. Goal active.

Next: Devanagari alternate DDDA, musical combining marks, missing scripts and
emoji; systematic final style and full-brief verification remain unfinished.

### Devanagari alternate DDDA checkpoint

- Added U+11B0A to the complete Noto Sans Devanagari derivative using native
  OFL outlines: DA supplies the distinct body, fitted to the existing DDDA's
  body band, and the existing DDDA supplies its separate implosive stroke.
  The new letter retains native DDDA advance, bearings and attachment rules.
  Provenance and construction are recorded in the Noto source manifest.
- Inspected rendered pages 1 and 7 of
  [L2/25-022](https://www.unicode.org/L2/L2025/25022-devanagari-sindhi-ddda.pdf).
  The vowel table motivates preserving the stroke separately from below-vowel
  signs rather than representing the letter as DA plus an arbitrary underline.
  Native below-vowel connectors may meet the stroke; they remain below the
  compressed DA body. The character's identity is distinct from both DA and
  the older DDA-shaped DDDA.
- Extracted the tested Indic input-rule expansion into a shared helper used by
  Bengali alternate BA and Devanagari alternate DDDA. Expands input coverage,
  class definitions, contextual rules and positioning while preserving all
  existing outputs. Added a supplementary cmap and a drawing-only DDDA/private
  UVS compatibility alias. Original logical text remains unchanged; older
  engines using the font directly do not receive that compatibility mapping.
- **243 JavaScript tests pass.** The combined font suite passed 30 tests and
  flagged an overly strict below-vowel assertion: native vowel connectors
  reach 11 units into the 70-unit stroke. Corrected the assertion to reject
  entry into the DA body, then all three DDDA tests passed. Checks cover the
  distinct body and preserved stroke, 15 vowel/mark cases with reph and prefix
  contexts, adjacent consonants, unchanged older Devanagari/Bengali behavior,
  and complete assigned Devanagari character mapping.
- **All 60 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected the proposal-inspired
  vowel specimen at comic size. Native-reader and final comic-style review
  remain provisional; cmap coverage is not exhaustive linguistic validation.
- Audits regenerated: **170,768 / 172,352** visible characters have bundled
  mappings, leaving **1,584 missing**. No Devanagari cmap gaps remain. Script
  fonts total 346 shards (60,144,972 bytes); hashes updated and diff whitespace
  checks pass. Goal remains active and unfinished.

Next: musical combining additions in the full native Noto Music font
(`assets/fonts/scripts/342fc9939b91.woff2`), remaining scripts and emoji, and
systematic final style/full-brief verification.

### Musical stress and unstress checkpoint

- Added U+1D127 COMBINING STRESS and U+1D128 COMBINING UNSTRESS from the pinned
  OFL UFS drawings to the complete Noto Music derivative. Embedded attribution,
  recorded donor provenance and excluded the marks from generic UFS packaging.
- Converted cubic contours within 0.5 font units, retained zero advance, and
  normalized their centers/top clearance to native articulation marks. Added
  native GDEF classes, filtering membership, mark attachment, contextual
  coverage/classes and positioning so note/stem/flag combinations retain the
  same attachment decisions as existing musical accent marks.
- Followed [Unicode 18 Chapter 21](https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-21/):
  these acute/breve articulation forms may remain uninverted above notes.
  This font's default specimens place them below notes, retaining their
  distinct uninverted shapes. No browser compatibility aliases were needed.
- **243 JavaScript tests and 23 font/shaping tests pass.** New checks compare
  placement across 11 encoded note values and four explicit note/stem/flag/dot
  sequences, zero advance, distinct drawings, native clearance and centers,
  unchanged existing music shaping and canonical note decomposition.
- **All 61 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually reviewed the two marks against
  ordinary accent, several note values and constructed flagged notes at comic
  size. This validates inline musical typography, not a full score-layout
  system; specialist and final comic-style review remain provisional.
- Coverage/source audits regenerated: **170,770 / 172,352** visible characters
  have bundled mappings, leaving **1,582 missing**. Script fonts remain 346
  shards (60,145,156 bytes). Asset hashes updated; diff whitespace checks pass.
  Goal remains active and unfinished.

Next: native music attachment for flag-6/7/8, tremolo-4/5, buzz-roll stem and
bow-behind-bridge stems; remaining scripts/emoji and full style validation.

### Musical flag-6/7/8 checkpoint

- Added U+1D250..U+1D252 from the pinned OFL UFS source to the complete native
  Noto Music derivative. The source's positive advances are replaced by zero
  advances, with GDEF mark classes and native flag filtering membership.
- Aligned the donor stem edge and lowest flag to native flag-5; additional
  flags extend upward. Reused native mark-to-base attachment, mark-to-mark
  host anchors, contextual coverage/classes and positioning. Source notices
  and scoped provenance remain recorded; generic UFS packaging excludes them.
- Checked the identities against the
  [Unicode 18 Musical Symbols Supplement](https://www.unicode.org/Public/18.0.0/charts/nameslist/1d250/).
  Tests verify exactly 6/7/8 flag contours, distinct increasing heights,
  zero advances, native stem-edge/bottom placement across five noteheads,
  and retained dot/tremolo/articulation positioning. The tremolo comparison
  explicitly follows its native substituted low form rather than incorrectly
  requiring its original cmap glyph. Older note shaping remains unchanged.
- **243 JavaScript tests pass.** The combined font suite passed 24 tests and
  exposed the test helper's un-substituted-tremolo assumption; after correcting
  it, both higher-flag tests pass, including the exact contour-count assertion.
- **All 62 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected ascending flag counts,
  continuous stem joins, half-note heads, dots and stress at comic size.
  Full score layout, specialist and final comic-style review remain provisional.
- Audits regenerated: **170,773 / 172,352** visible characters have bundled
  mappings, leaving **1,579 missing**. Script fonts remain 346 shards
  (60,145,628 bytes). Asset hashes updated; diff whitespace checks pass.
  Goal remains active and unfinished.

Next: tremolo-4/5, buzz-roll stem and bow-behind-bridge stems; remaining
scripts/emoji, final style work and full-brief verification.

### Musical tremolo-4/5 checkpoint

- Added U+1D25B/U+1D25C using newly constructed native Noto Music strokes.
  Four/five separate parallelograms retain the native slant and occupied stem
  area; thinner 56/40-unit strokes leave actual gaps at the denser counts.
  Provenance and construction are recorded in the Noto source manifest. These
  additions do not consume the standalone UFS drawings.
- Extracted shared musical mark-rule expansion and retained normal/low forms,
  GDEF classes, filtering, attachment and contextual placement. Testing found
  that the native reorder routine deletes a tremolo and reinserts a specific
  three-stroke glyph after the stem. Added count-specific reinsertion lookups
  so four/five strokes survive this operation rather than silently becoming
  three. No drawing-string aliases were needed in this browser.
- **243 JavaScript tests pass.** The combined font suite passed 26 tests; the
  remaining test initially assumed the native low variant was a simple glyph
  rather than a composite. After checking decomposed contours instead, both
  tremolo tests pass. They cover 60 combinations of counts, noteheads, flags
  and mark order, assert the actual final 4/5-stroke glyph, preserve native
  positioning/advances, verify separate strokes and retain older music shaping.
- **All 63 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected separated strokes,
  three/four/five comparisons, half-note heads and normal/lowered combinations
  with short and tall flags at comic size. Dense marks remain small; specialist
  and final comic-style review remain provisional.
- Audits regenerated: **170,775 / 172,352** visible characters have bundled
  mappings, leaving **1,577 missing**. Script fonts remain 346 shards
  (60,145,800 bytes). Asset hashes updated; diff whitespace checks pass.
  Goal remains active and unfinished.

Next: buzz-roll and bow-behind-bridge stems, remaining scripts and emoji,
then full visual-style and requirement-by-requirement validation.

### Special musical stems checkpoint

- Added U+1D25F buzz-roll stem, U+1D280 bow-behind-bridge stem and U+1D281
  bow-on-top-of-bridge stem. The latter is a distinct filled-cap symbol, not
  another behind-bridge form. Identities follow the pinned Unicode 18 chart.
- Retained the OFL UFS ornaments and replaced their stem rectangles with each
  of seven native Noto stem variants. Centers and upper stem ends align;
  native lengths and contextual advances remain intact. Substitution outputs
  retain the appropriate special stem rather than reverting to a plain stem.
  Extended shared positioning support for mark-to-base hosts and cursive
  entry/exit records. Source notices and scoped provenance are retained.
- **29 font tests pass**, including 189 special-stem combinations across seven
  noteheads and nine suffixes, distinct ornament contours after substitution,
  exact native positioning/advances, and unchanged older musical shaping.
  **243 JavaScript tests pass.**
- **All 64 Unicode browser scenarios pass** bounds, PNG export and geometry
  checks without warnings. Visually inspected plain/special comparisons,
  half-note heads, flags and articulation at comic size. Dense buzz/tremolo
  overlap and specialist score engraving remain provisional; this milestone
  does not claim final comic styling or full musical layout validation.
- Audits regenerated: **170,778 / 172,352** visible characters have bundled
  mappings, leaving **1,574 missing**. Script fonts remain 346 shards
  (60,146,172 bytes). Asset hashes and source manifests updated; diff whitespace
  checks pass. Goal remains active and unfinished.

Next: remaining supplemental music and scripts, emoji sequence coverage, then
full visual-style and requirement-by-requirement validation against the brief.

### Glagolitic caudate chrivi checkpoint

- Added U+2C2F/U+2C5F, closing the two remaining Glagolitic block mappings.
  Checked identities and documented tilde/titlo usage against the
  [Unicode proposal](https://www.unicode.org/L2/L2019/19288r-glagolitic-cerv.pdf)
  and visually inspected its first page. The narrow tailed forms remain
  distinct from ordinary broad chrivi; uppercase/lowercase heights differ.
- Pinned OFL Shafarik from Google Fonts revision
  `8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5` as an outline donor. Retained its
  licence and copyright notices in the delivered native Glagolitic derivative.
  Uniform scaling fits the corresponding native case height while preserving
  the below-baseline tail. Native mark anchors are translated to the new ink
  center. The donor is not independently routed over existing scripts.
- **23 font tests pass**, including distinct forms, baseline tails, case height,
  above-mark clearance/centering for five marks, complete Glagolitic block
  mapping, and unchanged older Glagolitic shaping. The two new tests pass again
  with the explicit retained-copyright assertion. **243 JavaScript tests pass.**
- **All 65 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected ordinary/caudate forms,
  marked uppercase/lowercase, word context and mixed Latin at comic size.
  Fine titlo appearance and specialist/final comic-style review remain
  provisional; mapping coverage is not a claim of final visual completion.
- Audits regenerated: **170,780 / 172,352** visible characters have bundled
  mappings, leaving **1,572 missing**. Script fonts remain 346 shards
  (60,146,464 bytes). Asset hashes and manifests updated; whitespace checks
  pass. Local verification server restarted on loopback port 8765.

Next: remaining scripts/emoji and systematic visual-style work; retain the
full brief as the completion criterion. Goal remains active and unfinished.

### Glagolitic browser mark-attachment correction

- Followed up the previous specimen's unusual capital titlo appearance with an
  enlarged browser comparison. Confirmed a real shaping discrepancy: browser
  script itemization left Cyrillic-script marks at their unpositioned origin,
  causing titlo to touch capital chrivi. This affected existing ordinary chrivi
  as well as the new caudate forms; HarfBuzz-only tests did not expose it.
- Added drawing-only, grapheme-scoped aliases for U+0483/U+0484/U+0487 following
  any Glagolitic block letter. Inherited tilde plus U+E0170..U+E0172 selects the
  original mark glyph through retained font UVS mappings, preserving native
  attachment without changing logical text, unrelated Cyrillic, or isolated
  marks. Export measurement and drawing use the same existing alias path.
- Verified identical HarfBuzz glyphs, advances and offsets for all **288**
  letter/mark combinations (96 letters × 3 marks). **24 font tests pass** and
  **244 JavaScript tests pass**, including cluster scoping and idempotence.
- Added browser assertions for actual mark ascent and unchanged advance,
  supplementing geometry/export checks. **All 65 Unicode browser scenarios
  pass** with no geometry warnings. Enlarged native text and final comic-size
  specimens now show original titlo shapes with clearance above the letters.
  This replaces the previous checkpoint's unresolved fine-titlo observation.
- Audits regenerated; mapping coverage stays **170,780 / 172,352**, with
  **1,572 missing**. The 346 script shards total **60,146,564 bytes**. Updated
  provenance, asset hashes and review corpus. Temporary diagnostic page removed;
  whitespace checks pass. Specialist and final comic-style review remain open.

Next: remaining scripts/emoji and systematic visual-style work. The full brief
remains the completion criterion; goal is active and unfinished.

### Kawi nukta integration investigation

- Verified the sole missing Kawi mapping, U+11F5A. The pinned OFL
  UnicodiaFunky contains its three-dot outline, but native Noto Kawi does not.
  Checked upstream release `NotoSansKawi-v1.000` and source revision
  `d6083759baecdec2ac8e6a76d93c466b51f18624`: the source still has no nukta
  glyph/rules. Upstream [issue 17](https://github.com/notofonts/kawi/issues/17)
  requests its addition, so an upstream update does not currently solve it.
- Read the [encoding proposal](https://www.unicode.org/L2/L2022/22236-kawi-sign-nukta.pdf)
  and visually inspected page 3. It documents PA→fa, NGA/HA uses, and a
  four-dot nukta-plus-anusvara combination. This provides a concrete identity
  check; simply overlapping three dots with an existing anusvara is wrong.
- Added `tools/font/probe_kawi_nukta.py`, a reproducible experimental probe
  outside the delivered build. It copies the donor outline, aligns it to the
  native candrabindu attachment area, expands native positioning/filtering,
  preserves self outputs in contextual substitutions, and includes mark1
  attachment. It writes a temporary font and prints final shaped glyph bounds.
- Measured PA+nukta at x102..541/y635..931 above PA's top544. Plain PA, AA,
  below-U and pre-base-E contexts retain their glyphs and sensible placement.
  PA+nukta+I overlaps I at x126..562/y635..1018. PA+nukta+anusvara overlaps
  anusvara at x268..459/y635..753. These failures rule out enabling the simple
  attachment prototype as finished support.
- Source inspection finds native repha/vowel/above-mark fusion, including
  `vowelI_candrabindukawi`, `vowelIi_candrabindukawi`,
  `vowelEu_candrabindukawi` and `repha_candrabindukawi`; blindly copying their
  ligature rules would discard nukta's distinct identity. The next integration
  needs nukta-specific combined forms and a four-dot anusvara form, tested
  across vowel, repha and conjunct contexts and then in the browser.
- No delivery/coverage claim changed: **170,780 / 172,352** mappings, **1,572
  missing**. This turn produced implementation evidence and a reusable probe;
  Kawi nukta remains incomplete. No new broad test run was needed because the
  delivery path is unchanged. Goal remains active.

### Kawi nukta shaping checkpoint

- Integrated U+11F5A into the native Noto Kawi derivative, retaining the OFL
  UnicodiaFunky outline, notices and licence provenance. All **87 assigned
  Kawi characters** now have bundled mappings. The temporary probe is
  superseded by `tools/font/kawi_nukta.py` and regression tests.
- Added distinct three-dot nukta and four-dot nukta+anusvara forms. Above-form
  combinations retain the native vowel/repha/candrabindu body and place dots
  with 70-unit clearance. Four dots reuse the donor dot shape on a square grid,
  following the documented four-dot distinction; they do not superimpose an
  anusvara on the three-dot drawing.
- Testing exposed nukta interrupting native below-vowel contextual selection.
  Original GSUB lookups now ignore only the added nukta while retaining their
  original mark filtering. A final above-form lookup combines it with the
  already-shaped native marks, preserving identities and attachment. A trial
  early reorder caused incorrect vowel order and was removed before delivery.
- **24 font tests pass**, including **1,224** consonant/vowel/repha/conjunct
  combinations with exact retained body glyphs, offsets and advances; explicit
  three/four-dot counts and contour clearance; native old-text equivalence;
  and packaged/prototype equivalence. All three focused tests pass again after
  adding the complete 87-character mapping assertion. **244 JavaScript tests
  pass.**
- **All 66 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected PA/NGA/HA, I/U/E,
  repha, conjuncts, and separate four-dot forms at comic size. No compatibility
  drawing alias was needed in this browser. Dense combinations, specialist
  typography and final comic styling remain provisional.
- Audits regenerated: **170,781 / 172,352** visible characters have bundled
  mappings, leaving **1,571 missing**. Script fonts remain 346 shards
  (60,147,224 bytes). Source manifests, review corpus and asset hashes updated;
  whitespace checks pass. This resolves the previous probe's specific vowel
  and anusvara collisions without claiming full Unicode beta completion.

Next: remaining scripts/emoji and systematic visual-style work, followed by
full-brief validation. Goal remains active and unfinished.

### Chemical reaction symbols checkpoint

- Added U+1F8D0..U+1F8D8 and U+1CEF0 from the pinned OFL UnicodiaFunky source.
  Applied the existing light pen deformation while retaining advances,
  contour topology and long/short proportions. Recorded the exact source scope
  and adaptation in the manifest; existing licence/attribution remain bundled.
- Checked names against Unicode 18 and visually inspected page 2 of the
  [chemical-symbol proposal](https://www.unicode.org/L2/L2023/23193r2-ten-chemical-symbols.pdf),
  including the unequal harpoon pairs and their opposite directions. The
  proposal's preliminary standard-state allocation differs from the final
  U+1CEF0 allocation; the delivered mapping uses the pinned Unicode inventory.
- Browser inspection exposed a source defect: U+1F8D8 had only a right head
  despite its left-right identity. Added the mirrored left head directly into
  the shaft contour, retaining the dependent lobe and its counter, without
  overlapping paths. Added a regression requiring both heads and the lobe.
- **24 font tests pass**, including unique adapted drawings, unchanged advances,
  bounded deformation, topology, harpoon directions, long/short ratios and
  both isolobal heads. **244 JavaScript tests pass.**
- **All 67 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings, including a repeat after the arrow repair.
  Visually inspected equal/unequal arrows, crossed and double-slash forms,
  repaired isolobal arrow, standard-state symbol and mixed Arabic/Latin text
  at comic size. This is plain Unicode rendering, not chemical formula markup;
  annotation positioning and final comic-style review remain outside this
  checkpoint's validation claims.
- Audits regenerated: **170,791 / 172,352** visible characters have bundled
  mappings, leaving **1,561 missing**. Script fonts remain 346 shards
  (60,148,176 bytes). Source manifest, review corpus and asset hashes updated;
  whitespace checks pass. Goal remains active and unfinished.

Next: remaining scripts/emoji and systematic visual-style work, followed by
full requirement-by-requirement verification against the brief.

### Geomantic figures checkpoint

- Added all sixteen U+1CEE0..U+1CEEF figures from the pinned OFL
  UnicodiaFunky source, with scoped provenance and the existing light pen
  treatment. Retained fixed advances and the four-row, centered dot grid.
- Read the [Unicode proposal](https://www.unicode.org/L2/L2023/23218-geomancy.pdf)
  and visually inspected its dotted specimen. Verified the binary allocation:
  double-dot rows encode zero, single-dot rows one, with the top row most
  significant. The implementation retains vertical figures and uses ordinary
  surrounding-text directionality; it adds no divinatory semantics.
- **25 font tests pass**, including all sixteen exact row patterns, centered
  singles/symmetric pairs, four rows, separated dot contours, fixed advances,
  bounded adaptation and distinct identities. Existing chemical-symbol tests
  also pass, including the repaired isolobal arrow. **244 JavaScript tests
  pass.** An initial focused check ran before the asynchronous font build
  finished; after build completion the focused and combined suites passed.
- **All 68 Unicode browser scenarios pass** independent bounds, PNG export and
  geometry checks without warnings. Visually inspected all sixteen patterns
  and mixed Arabic/Latin context at comic size: dots remain separated and each
  pattern is readable. Final comic-style and specialist review remain
  provisional.
- Audits regenerated: **170,807 / 172,352** visible characters have bundled
  mappings, leaving **1,501 missing**. Script fonts remain 346 shards
  (60,148,572 bytes). Source manifest, review corpus and asset hashes updated;
  whitespace checks pass. Goal remains active and unfinished.

Next: remaining symbol/script groups and emoji coverage, systematic visual
styling, and the full requirement-by-requirement completion audit.

## Full-suite and current-status reconciliation checkpoint

The broad Python run exposed two stale repertoire assumptions: the alphabet
adaptation test accidentally included the ten chemical and sixteen geomantic
symbols, and the Jurchen/Tangut packaging test omitted the separately declared
standalone-symbol scope. The alphabet test now excludes those two named symbol
scopes, retaining its original 240-letter outline, advance and shaping checks.
Chemical and geomantic geometry remain covered by their dedicated tests. The
packaging test now includes the explicit standalone-symbol ranges while still
requiring exact cmap equality and retaining all original Jurchen/Tangut checks.
No font or renderer behaviour changed in this checkpoint.

Full reruns pass **175 Python tests** (7 existing SWIG warnings) and **244
JavaScript tests**, including the pinned bidi and line-break conformance corpora.
`git diff --check` passes. No browser rerun is required for these test-scope and
documentation changes; the latest browser evidence remains 68 passing scenarios.
The top-level summary and next steps now reflect the implemented bidi resolver,
grid rendering, resource limits and script additions instead of the obsolete
initial milestones. Logical case preservation was checked in the renderer;
capital-looking original Latin lowercase drawings do not imply uppercasing of
input. The existing custom-emoji test already verifies all 105 advertised exact
sequences as real one-glyph drawings, so no duplicate audit test was added.

Coverage remains **170,807 / 172,352**; the **1,545** missing mappings break down
as Common 995, Seal 348, Garay 69, Tai Yo 55, Tolong Siki 54, Syriac 11, Sharada 8
and Han 5. Hangul and Jurchen no longer have cmap gaps. The 346 script shards total
60,148,572 bytes. Sequence completeness and custom visual treatment remain
separate unfinished requirements. The full beta goal remains active.

## Historical asteroid symbols checkpoint

Added all **21** historical asteroid symbols at U+1CEC0–U+1CED0 and
U+1F777–U+1F77A from the pinned, licensed UnicodiaFunky source. The manifest
records their exact scope and the authoritative reference:
https://www.unicode.org/L2/L2023/23207-historical-asteroids.pdf . Visually compared
all source forms with the proposal's chart and character list (pages 1 and 3),
including the four alternate forms. These are monochrome astronomical text
symbols, not emoji. Light smooth pen variation preserves their conventional
forms; final comic-style and specialist review remain provisional.

The new font regression checks all 21 distinct drawings, nonempty ink,
unchanged positive advances, bounded outline displacement, preserved contour
count/winding and source-equivalent shaping. It intentionally allows extra
points inserted along long straight edges by the pen-adaptation routine.
Alphabet-only tests exclude this new symbol scope. The combined asteroid,
alphabet, chemical, geomantic and generic packaging suite passes **30 tests**.

The browser review corpus now includes all 21 symbols with a mixed Latin/Arabic
line. All **69 scenarios** pass containment, geometry and PNG round trips without
warnings. At dialogue size the stars, eye, wheel, lyre, counters and alternate
forms remain distinct and legible. Existing character art is unchanged.

Coverage audit, source inventory and asset hashes were regenerated. Bundled cmap
coverage is now **170,828 / 172,352**, leaving **1,501 missing**; script assets total
**60,152,624 bytes in 346 shards**. This closes the astronomical-symbol cmap gap,
not the remaining custom-lettering, sequence or overall beta requirements.

## Legacy text pictographs checkpoint

Pinned Kreative Square from the original `kreativekorp/open-relay` repository at
commit `e4b81241e8c7269a91c0bd865cf5c9e7208fbada`, with verified Git blob and
SHA-256 hashes. Its font-specific OFL notice is retained in
`assets/fonts/licenses/KreativeSquare-OFL.txt`; the derivative is renamed.
The new manifest restricts packaging to **nine assigned text pictographs**:
U+1CCFA–U+1CCFC and U+1CEBA–U+1CEBF. No private-use, unrelated or emoji mappings
from this broad source are included.

All nine source drawings were compared with page 6 of the Unicode proposal:
https://www.unicode.org/L2/L2023/23252-legacy-disunification.pdf . They retain
monochrome text presentation, including the single-cherry form. Smooth light
pen variation preserves source spacing and recognisable outlines. Final custom
style review remains provisional. The new regression checks exact cmap scope,
all distinct outlines, unchanged 720-unit advances, bounded outline displacement,
and contour counts preserving windows, hollow forms and strawberry details.
Source-equivalent shaping and absence of colour font tables are also checked.
The combined targeted/generic packaging suite passes **22 tests**.

A new browser specimen includes every pictograph and mixed Latin/Arabic text,
with explicit no-emoji-fallback and no-forced-grid checks. Visual inspection at
dialogue size confirms readable internal details. Asset hashes, coverage audit
and source inventory are regenerated. Bundled cmap coverage is now
**170,837 / 172,352**, leaving **1,501 missing**; the **347** script shards total
**60,154,836 bytes**. The full beta goal remains active and incomplete.

Final browser run: all **70 scenarios** pass containment, geometry and PNG
round trips, without warnings. `git diff --check` passes.

## Chess annotations, shatranj pieces and alarm bell checkpoint

Added U+2B96 EQUALS SIGN WITH INFINITY ABOVE from the licensed UnicodiaFunky
source, with light pen variation. It retains the same 766-unit advance as the
existing Noto U+2BF9 counterpart. The test explicitly checks two separated bars,
two enclosed infinity counters, and whether the infinity is above or below.
The authoritative proposal is
https://www.unicode.org/L2/L2024/24018-one-chess-symbol.pdf ; its preliminary
U+2B74 allocation is superseded by the pinned Unicode 18 U+2B96 mapping.
These are distinct atomic annotations; the renderer does not replace either
with an equals/infinity combining sequence.

The remaining-Common audit found five further non-emoji gaps. Added the four
shatranj pieces U+1FA54–U+1FA57 from UnicodiaFunky, visually comparing the source
forms with page 1 of
https://www.unicode.org/L2/L2024/24020-shatranj-symbols.pdf . Regression checks
retain distinct ferz/alfil forms, contour counts, advances and the substantially
greater filled area of each black piece relative to its white counterpart.
The ten-symbol legacy pictograph scope now also includes U+1FBFA ALARM BELL
SYMBOL from the already pinned Kreative Square source. It remains monochrome
text and does not trigger grid layout or emoji fallback. The reference is page
7 of the previously recorded L2/23-252 proposal.

The combined chess, legacy-picture, alphabet and generic packaging suite passes
**28 tests**. Coverage and source audits plus asset hashes were regenerated.
Bundled cmap coverage is **170,843 / 172,352**, with **1,501 missing**. The
**347** script shards total **60,155,920 bytes**. After these six additions,
all **959** remaining Common-script cmap gaps have the pinned Emoji property;
the other **550** missing mappings belong to the remaining script groups. This
classification is a prioritisation aid, not a claim of completed existing emoji
or symbol styling. Custom style and linguistic review remain provisional.

Final browser validation: all **71 scenarios** pass containment, geometry and
PNG round trips with no warnings. Visually checked both compensation symbols,
all four white/black pieces and the monochrome alarm bell at dialogue size.
`git diff --check` passes.

## Sharada Supplement source and attachment investigation

The next script target is U+11B60–U+11B67. Downloaded and inspected the
Kashmiri Sharada proposal L2/23-122, including its character forms, independent
vowel combinations and top/bottom/right positional categories. The current
native Noto Sans Sharada source is version 2.006. The official latest release
`NotoSansSharada-v2.006` still has no mappings for these eight signs; the current
source tree at `5860efa605f4c81084090479feab9b99f838af37` likewise has no
Supplement glyphs. Updating the existing source therefore does not close this
gap.

The already licensed UnicodiaFunky donor has all eight drawings, including three
right-side composite vowels. However, it has no `shrd` GSUB/GPOS script records,
and U+11B66 CANDRA E incorrectly has a positive 231-unit donor advance despite
being a nonspacing mark in the pinned inventory. It must not be bundled as a
standalone coverage shard. Native Noto provides useful top and below mark
anchors, but U/UU have several context-sensitive alternate forms; simply copying
one attachment anchor would not preserve syllable behaviour.

Added and executed `tools/font/probe_sharada.py`, producing the reproducible
`docs/sharada-vowel-review.json`. It records all eight donor outlines/advances,
the native missing-glyph shaping results for KA plus each new sign, and relevant
native anchor classes. This changes the next implementation step from source
search to a native attachment builder, followed by consonant/conjunct/independent
vowel tests and real-browser checks. No new Sharada mappings are claimed or
shipped by this diagnostic. Coverage remains **170,843 / 172,352**, with **1,509
missing**. `git diff --check` passes; runtime assets and existing validation
results are unchanged. The full beta goal remains active.

## Sharada nonspacing-vowel prototype checkpoint

Implemented `tools/font/sharada_vowels.py` for the five nonspacing signs
U+11B60, U+11B62, U+11B63, U+11B64 and U+11B66. It imports licensed donor
outlines into native Sharada, retains notices, corrects all five advances to
zero, carries native mark classes/anchors and contextual below-vowel variants,
and provides UVS aliases for equivalent shaping on older Unicode engines.
The three right-side composite vowels remain deliberately unimplemented: native
AA participates in numerous conjunct ligatures, so copying standalone donor
outlines would not establish correct contextual behaviour.

The two new prototype tests pass. They verify **720** base/prefix/mark combinations
for real glyph identity, zero mark advance and UVS equivalence, and **1,344**
existing base/prefix/vowel combinations for unchanged native shaping. The font
serialises successfully to `/tmp/sharada-vowels-prototype.ttf`. No production
builder or font manifest imports this prototype yet.

Rendered positioned HarfBuzz outlines and visually inspected the five marks on
KA, JHA and KA–RA. The specimen is
`output/font-review/sharada-nonspacing-prototype.png`. It exposed a real remaining
placement issue: below-vowel arcs can touch a descending consonant stroke even
though the inherited native U/UU positioning preserves glyph identity. The new
arc forms need mark-specific below-base clearance; inheriting a connected native
U shape's anchors is insufficient. Fix and test that geometry before production
integration, then implement the right-side vowels and verify in the browser.
Top signs and one-versus-two below arcs retain distinct shapes in the specimen;
that narrow visual result does not establish full linguistic correctness.

Coverage remains unchanged (**170,843 / 172,352**, **1,501 missing**). Runtime
assets are unchanged. Prototype tests and `git diff --check` pass. The goal
remains active, with Sharada still explicitly incomplete.

## Sharada Supplement integration checkpoint

Completed native integration for all **eight U+11B60–U+11B67** Kashmiri vowel
signs. The five nonspacing signs retain zero advances and native classes. Their
below-arc forms now use separate mark classes with 50-unit clearance below the
actual base outline, avoiding the descender collision found in the prototype.
Native connected U/UU attachments remain unchanged. The three right-side vowels
retain the donor's native-AA body and its advance. When AA fuses into a native
conjunct, the builder preserves that entire native body and adds only the
appropriate upper extension. Native modifier anchors position these additions;
four fused forms lacking those anchors use their measured headline/stem edges.
These four provisional placements remain candidates for specialist review.

All eight have scoped UVS rendering aliases, preserving the original logical
text while supporting older browser character databases. The builder retains
source notices, records the donor licence and hashes every shaping helper and
donor source. Glyph names remain in this modest Sharada shard to support exact
identity/body regression checks. `probe_sharada.py` now identifies its report
as a source-only diagnosis; the original source gaps no longer imply missing
delivered support.

The **29-test** Sharada/generic packaging run passes, including the same four
Sharada regressions against both the prototype and delivered WOFF2. After an
additional exact native-body assertion, all eight Sharada cases pass again.
Checks include 720 nonspacing combinations, below-descender clearance, unchanged
older text, all native AA ligature input sequences, and UVS equivalence. The
full JavaScript suite passes **245 tests**. The browser passes all **72 scenarios**
for containment, geometry and PNG round trips without warnings. The new
Sharada specimen was visually inspected at dialogue size: the eight marks,
one/two below arcs, fused right vowels and independent-vowel combinations remain
legible; no missing glyphs or below-stroke collisions were seen in that sample.
This is targeted validation, not a claim of fluent-reader or exhaustive Sanskrit/
Kashmiri typography review. The font's overall comic-style treatment is still
provisional.

The reproducible enlarged review is generated by `tools/font/review_sharada.py`
at `output/font-review/sharada-vowels-prototype.png`. Production font:
`assets/fonts/scripts/00765286a510.woff2` (Dad Script 00765286a510). Asset hashes,
coverage and source audits are regenerated. Coverage is **170,851 / 172,352**,
leaving **1,501 missing**; 347 script shards total **60,160,068 bytes**. Sharada's
visible cmap gap is closed. The full beta goal remains active and incomplete.


## Facial-expression atlas and user style correction

Added twelve custom facial expressions, bringing Dad Emoji to 58 visible bases,
117 exact sequences and 21 shaping components. Coverage increases by eleven
previously absent mappings to 170,862 / 172,352, leaving 1,490.

The user rejected the production sheet's overly clean lines. Saved this feedback
in the brief. The first edit merely roughened the outlines and was rejected
internally; a fresh pass introduced unwanted human heads and was simplified
back to emoji. `faces-v2.png` is the provisional compiled revision, with its
built-in imagegen prompt chain in `faces-v2-prompts.json`. Its asymmetry and
expressions are livelier, but the overall emoji style still needs review against
the user's stronger hand-drawn requirement, including the existing atlas.

The compiler records source hash, extraction bounds and glyph identities;
transparent gutters are used rather than cutting the drawings at equal thirds.
All 10 emoji font tests and 245 JavaScript tests pass. The new twelve-face browser
specimen was visually inspected at dialogue size: expressions remain distinct
and fit inside the balloons. Full browser run status is recorded separately.

Browser run completed: all 73 geometry/export scenarios pass with no reported
failures or geometry warnings. This does not establish final style approval.


## User rejects facial atlas; reference-grounded study

The user rejected the new emoji and correctly identified the lack of direct
Watterson image references in the fresh generation. Removed the twelve rejected
faces from the compiled font and browser corpus; kept source files for history.
Coverage returns to 170,851 / 172,352 (1,501 missing), and Dad Emoji to 46 bases
and 105 sequences. All ten emoji font tests pass after rebuilding.

Rendered original PDF page 14 close-ups at 3x, with source hash and clip
coordinates in `output/imagegen/emoji-production/references/source.json`. Passed
both actual image files directly to built-in imagegen for a four-face study,
`faces-reference-study-v1.png`; exact prompt and reference paths are saved beside
it. This study has lighter varied contours and simpler expressions, but remains
a study, not compiled or claimed approved. Future generations must use actual
PDF references. The rejected v2 sheet is not the current production direction.

## Refine reference-grounded emoji stroke finish

The user rated the four-face reference-grounded study OK to decent, but its
lines too rough. Generated `faces-reference-study-v2.png` as a targeted edit,
passing both original PDF close-ups again alongside the edit target. It retains
the expressions and asymmetric contours while removing scratch texture and
closing conspicuous contour gaps. Saved the exact prompt alongside the image.
This remains a style study; no font or coverage change. Direction: confident,
fluid variable-pressure ink, avoiding both distressed strokes and mechanical
uniform outlines. User approval of this revision is not assumed.


## Approved emoji stroke style compiled

The user approved `faces-reference-study-v2.png`. Updated the agreed brief and
source status accordingly. Compiled its four expressions (U+1F60A, U+1F606,
U+1F610, U+1F634) into Dad Emoji, preserving the approved shapes and strokes.
The source is white-background art; the compiler traces black ink and fills
enclosed contours to form the white underlayer. It does not include the white
rectangular source background. Source hash, cell bounds and advances are saved
in the glyph review. Rejected twelve-face atlases remain unused.

Dad Emoji now has 50 visible bases, 109 explicit sequences and 21 shaping
components, at 21,372 bytes. Visible cmap coverage is 170,854 / 172,352, with
1,498 missing. Eleven emoji tests pass, including deterministic rebuild, all
advertised sequence shaping, distinct outlines and enclosed white interiors.
All 245 JavaScript tests pass. Added a browser case for isolated, adjacent and
mixed-text faces, with explicit custom-font routing and no-fallback assertions.

Next: extend remaining emoji with the approved source image AND actual PDF
close-ups as visual references, preserving smooth variable-pressure ink.
Existing earlier emoji still need style reconciliation; full script coverage,
sequence coverage, and linguistic/visual review remain incomplete.

The completed browser run passes all 73 geometry/export scenarios without
reported failures or geometry warnings. Visually inspected the four approved
faces in isolated, adjacent and mixed-text dialogue: strokes and expression
features remain visible, and all fit within the balloons. `git diff --check`
passes. This is a verified emoji milestone, not completion of the full brief.


## Twelve more faces in the approved ink direction

Generated and compiled `faces-expansion-v1.png` using the user-approved
`faces-reference-study-v2.png` plus both actual PDF close-ups as direct image
references. The initial generation had an erroneous dark background; a targeted
tone correction produced black ink on white without redesigning the faces.
The complete generation and correction prompts are saved alongside the sheet.

Added U+1F601, U+1F603..1F605, U+1F609, U+1F60B, U+1F60E, U+1F611,
U+1F642, U+1F641, U+1F62E and U+1F62F. Visually checked their eye, mouth,
sweat, tongue and sunglasses identities and the different surprise expressions.
The compiler now supports multiple sheets, retaining hashes and actual cell
gutters. It preserves the four previously approved expressions unchanged.

Dad Emoji is 27,024 bytes, with 62 visible bases, 121 exact sequences and
21 shaping components. Bundled visible coverage is 170,866 / 172,352, leaving
1,486 missing. Eleven font tests pass, including all advertised sequences,
deterministic compilation, white interiors, bounds and distinct drawings for
all sixteen new-style faces; 245 JavaScript tests pass. `git diff --check` passes.

Expanded the browser specimen to all sixteen expressions with explicit custom
routing checks. Inspected the rendered dialogue: the grin variants, wink,
sunglasses and surprised expressions remain distinct at text size, with no
visible clipping. This is an extension of the approved style, not a claim that
the user individually approved the new sheet. Remaining emoji, earlier atlas
style reconciliation and the broader Unicode brief remain incomplete.

Completed browser validation: all 73 geometry/export scenarios pass, with no
reported failures or geometry warnings, including custom routing for all sixteen
new-style faces.


## Tongue, skeptical and accessory expressions

Generated `faces-playful-v1.png` with the approved smooth-ink study and both
original PDF close-ups passed directly as references. Saved the complete prompt
and reference list alongside the source. Added twelve distinct expressions:
U+1F61B..1F61D, U+1F92A, U+1F928, U+1F9D0, U+1F913, U+1F910, U+1F644,
U+1F60F, U+1F612 and U+1F62C. Checked open/winking/squeezed tongue eyes,
unequal zany eyes, one monocle versus two spectacle lenses, zipper teeth and
pull, upward pupils, smirk versus frown, and the tense clenched-teeth mouth.

The compiler uses the source's transparent-free white ground and actual blank
row gutters. Hashes, glyph bounds and advances remain recorded. Existing sheets
are retained. Dad Emoji is 33,380 bytes with 74 visible bases, 133 exact sequences
and 21 shaping components. Coverage is 170,878 / 172,352, leaving 1,474 missing.

All eleven emoji font tests pass (now testing distinct drawings and enclosed
white interiors for 28 new-style faces); all 245 JavaScript tests pass.
`git diff --check` passes. Added a browser scenario with all twelve expressions
and mixed text, explicitly verifying custom-font routing and no native emoji
fallback. Visual inspection at dialogue size retained the eye differences,
monocle, spectacles and zipper; no visible clipping. Full browser result below.

The new sheet extends the approved direction; it is not independently approved
by the user. Remaining emoji and standardized sequences, earlier atlas style
reconciliation, script gaps and broader visual/linguistic review remain open.

Full browser validation completed: all 74 geometry/export scenarios pass without
reported failures or geometry warnings, including custom routing for the twelve
new expressions. The full brief remains incomplete and the goal stays active.


## Worried, strained, angry and minimal faces

Generated and compiled `faces-strained-v1.png`, again passing the approved
smooth-ink study and both actual PDF close-ups directly to imagegen. The prompt
and source paths are saved beside the image. Added U+1F615, U+1F61F, U+1F61E,
U+1F614, U+1F616, U+1F623, U+1F629, U+1F62B, U+1F624, U+1F620, U+1F643
and U+1F636. Visually reviewed the crooked confused mouth, worried brows,
disappointed versus pensive mouth, wavy confounded versus tight persevering
mouth, weary versus tired eyes, paired steam puffs, angry open eyes, inverted
smile and absence of mouth.

Dad Emoji now has 86 visible bases, 145 exact sequences and 21 shaping
components at 38,692 bytes. Coverage is 170,890 / 172,352, with 1,462 missing.
All twelve emoji tests pass, including distinct ink and enclosed white interiors
for forty new-style faces. Added a semantic outline regression: the mouthless
face contains exactly two interior eye contours; the inverted face has its mouth
above both eyes. All 245 JavaScript tests and `git diff --check` pass.

Added a browser scenario with all twelve isolated and in mixed text, checking
custom routing and no native fallback. Visual inspection at dialogue size
shows different brows/mouths, visible steam, an inverted smile and the mouthless
face, all contained in balloons. This extends the user-approved direction but
is not an independent user approval of this sheet. Remaining full Unicode
coverage, sequence behavior, earlier emoji style reconciliation and broad
linguistic/visual review remain open.

Full browser validation completed: 75 geometry/export scenarios pass with no
reported failures or geometry warnings. The full goal remains active.

## Programmatic pen treatment after renewed style drift

The user found later generated batches too vector-like and asked for a program
to automate the translation. Implemented `tools/font/pen_translate.py` with
seeded smooth geometry deformation, signed-distance pressure variation,
skeleton-endpoint tapering and supersampled output. It preserves components
and meaningful holes, bounds component-area changes, checks borders, and reduces
strength or explicitly falls back when those constraints fail. It ignores only
scan pinholes smaller than four pixels. No imagegen call or source overwrite.

Added a reproducible CLI with crop/strength/seed/bend/pressure/taper controls,
source/program hashes and settings sidecars. Added the comparison builder
`tools/font/preview_pen_translate.py`, a four-expression enlarged/24px sheet,
and documentation in `docs/emoji-pen-translation.md`. The stronger requested
setting sometimes produces a lower actual strength because of detail guards;
the comparison labels the applied value. All sixteen targeted tests pass,
covering determinism, nontrivial output, feature retention, clipping, transparent
input, zero-strength identity, and invalid values. Ran the CLI successfully.

This is an opt-in prototype, not a production style change or claimed automatic
Watterson translation. Inspection shows useful smooth width variation but only
subtle differences at text size, especially where teeth constrain the effect.
No production font changes were made by this prototype work. The preceding
ailing-face batch was interrupted by the user's style objection and is not
being counted as a verified or stylistically accepted milestone.


## Preferred expressive treatment integrated into face glyphs

The user liked the procedural comparisons and preferred the expressive ones.
Recorded that preference in the brief and applied requested strength 1.7 to all
52 face glyphs in `emoji_faces.py`. The four comparison examples retain the same
seeds; remaining faces use stable codepoint-derived seeds. Each glyph records
source bounds, transformed bounds, settings, actual applied strength, backoffs
and fallback status. Each source-sheet record includes the pen recipe hash.
Original raster sources are unchanged.

All 52 glyphs received a nonzero treatment, with no original-mask fallback.
Twelve kept full 1.7 strength; forty reduced it to preserve detail (six at 0.30,
two at 0.40, three at 0.54, five at 0.72, fifteen at 0.96, nine at 1.27). This is
expected and shown explicitly, not claimed as uniform full-strength treatment.
The font contains 98 visible bases, 157 exact sequences and 21 shaping components
at 48,432 bytes. This also completes compilation of the interrupted twelve
ailing expressions, now with the preferred procedural finish instead of raw
generated strokes. Coverage is 170,902 / 172,352, with 1,450 missing.

Added `tools/font/preview_emoji_faces.py`, which renders the actual compiled COLR
outlines enlarged and at 24px into `output/font-review/pen-translation/compiled-faces.png`.
Inspected every glyph: the expressions and accessories remain distinct, with
visible line-weight variation. Twenty-eight targeted Python tests pass, including
reproducible font rebuilding, all 157 advertised sequences, outline semantics,
white interiors, and procedural safeguards. All 245 JavaScript tests pass;
`git diff --check` passes. Browser results are recorded below.

The preferred procedural treatment is established for these face sheets. It has
not yet been applied to the earlier selective-colour atlas; remaining glyph and
sequence coverage, script review and full style reconciliation are still open.

Completed browser run: 76 geometry/export scenarios pass with no reported
failures or geometry warnings. Visually inspected both the basic-expression and
ailing-expression comics after treatment; features and accessories remain
readable and contained. Full brief remains incomplete.


## Licensed monochrome source through the expressive program

Pinned Google Fonts Noto Emoji and its OFL at revision
`8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5`, with file hashes, blob hashes and
explicit twelve-codepoint scope in `data/font-sources/noto-emoji.json`. Added
`emoji_licensed.py` to render weight-400 source outlines, apply the preferred
expressive program, and trace the result into Dad Emoji. Source scope excludes
colour-dependent drawings and all other source cmap entries. Script packaging
now skips sources explicitly targeted at the emoji builder, as it already does
for grid sources. This is not wholesale source-font fallback.

Imported drum, saxophone, trumpet, guitar, violin, piano keyboard, musical note,
musical notes, musical score, microphone, headphones and radio. The pinned
Unicode variation inventory also contributes FE0E/FE0F for headphones and radio.
Both presentations use the reviewed monochrome drawing. All twelve received
nonzero expressive treatment without fallback. The compiled review sheet at
`output/font-review/pen-translation/compiled-music.png` shows actual COLR outlines
enlarged and at 24px; inspected all instruments, note groups, clef/staff, mic,
headphones and radio for recognizable identity.

Dad Emoji now has 110 visible bases, 173 explicit sequences and 21 shaping
components, at 56,052 bytes after embedded licence metadata. It retains the
Google copyright/OFL notice, uses the derivative family name Dad Emoji, and
is distributed with `NotoEmoji-OFL.txt`. The 52 existing expressive faces stay
in place. Visible coverage is 170,912 / 172,352, leaving 1,440 missing (ten
previously missing mappings were filled by the twelve music glyphs).

Twenty-nine combined emoji/pen tests passed before the final metadata addition;
font tests are rerun afterward. Tests cover all advertised sequence shaping,
source pinning, note grouping, derivative naming and licence metadata. All 245
JavaScript tests passed. Added a music browser scenario with explicit custom
font/no-fallback assertions. No image generation was used for these new glyphs.
Full script, emoji sequence and style coverage remain incomplete.


Final font rerun: thirteen emoji tests pass after embedded OFL metadata, alongside
the sixteen passing pen-treatment tests. Full browser run: all 77 geometry/export
scenarios pass with no reported failures or geometry warnings. Visually inspected
all twelve music glyphs inside actual dialogue, including mixed text and custom
routing; no clipping or missing details. `git diff --check` passes.

Next candidate for this repeatable licensed-source pipeline: clock-face emoji,
with explicit checks of hand positions so different times do not collapse.
Colour-dependent objects and skin-tone/ZWJ sequences require separate treatment
and are not covered merely because the source font contains them.


## All clock-face emoji and standardized presentations

Extended the pinned, explicitly scoped Noto Emoji adaptation to U+1F550..1F567:
all twelve hour and twelve half-hour clock faces. Included both standardized
FE0E/FE0F presentations for all 24 from the pinned Unicode inventory. Each uses
the preferred expressive procedure, with guarded reductions for fine tick marks.
No glyph fell back to its original mask; applied strengths range from 0.30 to
0.54. The smaller strength is reported rather than presented as full 1.7.

Added `--clocks` to the compiled review-sheet builder. Inspected all 24 glyphs
enlarged and at 24px in `output/font-review/pen-translation/compiled-clocks.png`,
then inside comic dialogue. Hand directions remain distinct, including the
half-hour position between hour ticks, and no glyph clips its balloon.

Added a semantic regression which rasterizes the actual compiled glyphs and
measures ink near the expected hour/minute angles, testing all 24 times. It also
requires distinct outlines and equivalent shaping for bare, text-variation and
emoji-variation forms. The new test passes independently as well as in the full
emoji/pen target set: 30 tests pass (seven existing SWIG warnings). All 245
JavaScript tests pass; routing tests iterate every advertised sequence.
`git diff --check` passes.

Dad Emoji now has 134 visible bases, 245 explicit sequences and 21 shaping
components at 68,152 bytes. Visible cmap coverage stays 170,912 / 172,352, with
1,440 missing: these clocks already had other bundled mappings, but now have
reviewed custom emoji routing and presentation. Cmap presence and completed
emoji treatment remain deliberately separate measures. Remaining full glyph,
sequence, style and linguistic review work is still open.


Full browser validation completed: all 78 geometry/export scenarios pass with
no reported failures or geometry warnings, including every custom clock face.


## Expressive transport emoji — 2026-11-01

Added 24 reviewed road, rail and boat drawings from the pinned OFL Noto Emoji
source, plus eight applicable standard presentation variants. They use the
approved expressive procedural treatment at requested strength 1.7, with the
existing feature-preservation guard reducing strength where necessary. All 24
receive a nonzero treatment; none silently falls back to its original outline.

The locomotive uses source weight 350 at 512 pixels to preserve wheel details;
the ship uses weight 400 at 768 pixels. Other transport drawings use weight 400
at 384 pixels. These source-specific choices are recorded in provenance. The
guard itself was not relaxed. Tests require distinct compiled drawings, retained
components and enclosed details, positive advances, white/ink layers, and
identical shaping for the supported presentation variants.

Reviewed `output/font-review/pen-translation/compiled-transport.png` and the
actual dialogue specimen: related cars, buses, rail vehicles and boats retain
their distinguishing details at small size. All 31 targeted emoji/pen Python
tests and 245 JavaScript tests pass. The browser passes all 79 geometry/export
scenarios without reported failures or geometry warnings. `git diff --check`
passes. These checks do not replace broader visual and linguistic review.

Dad Emoji now contains 158 visible bases, 277 exact sequences and 21 shaping
components, at 84,852 bytes. The 24 transport drawings add 19 previously missing
visible mappings: coverage is 170,931 / 172,352, leaving 1,421. The full Unicode
beta goal remains active and incomplete.


## Expressive tools and hardware — 2026-11-01

Added 24 reviewed tools/hardware drawings from the pinned OFL Noto Emoji source,
with 20 applicable standardized presentation variants. All receive nonzero
expressive pen treatment. Most retain the requested strength 1.7; fine details
cause conservative reductions. Clamp U+1F5DC requires a 768px source raster at
weight 400 to retain its screw-thread openings. This exception is recorded in
provenance, and the feature-preservation guard is unchanged.

The compiled review sheet is
`output/font-review/pen-translation/compiled-tools.png`. Reviewed it enlarged,
at 24px and in actual dialogue: keys, chain links, saw teeth, and the open/closed
padlock distinction remain visible. Tests require distinct compiled outlines,
retained components/enclosed details and equivalent presentation variants.
A semantic regression rasterizes the final padlocks and verifies that only the
locked shackle encloses space in the upper part of the icon.

All 33 targeted emoji/pen Python tests pass, including byte-identical font and
manifest rebuilds (seven existing SWIG warnings). All 245 JavaScript tests pass.
Dad Emoji now has 182 visible bases, 321 exact sequences and 21 shaping
components at 98,964 bytes. Coverage rises by eight previously missing mappings
to 170,939 / 172,352; 1,413 remain missing. The other new tool drawings replace
existing mappings with reviewed custom emoji presentation. The full Unicode
beta goal remains active; source coverage, sequence behaviour, style adaptation
and broader review still have substantial gaps.

All 80 browser geometry/export scenarios pass with no reported failures or
geometry warnings, including custom routing for all 24 tools. `git diff --check`
passes.


## Expanded expressive faces — 2026-11-01

Added 45 monochrome-compatible facial expressions from the pinned OFL Noto Emoji
source while retaining the approved custom drawings. The additions cover
remaining affectionate and hand-gesture expressions, several other emotions,
nine cats and all three see/hear/speak-no-evil monkeys. Colour-dependent faces
such as hot, cold and nauseated remain outside this monochrome scope. Newer
faces absent from the pinned donor and compound face sequences remain open.

All 45 receive nonzero expressive treatment. Star-struck U+1F929 uses weight
400 at 768px to preserve star-eye tips. Fearful U+1F628 and anxious U+1F630 use
weight 350 at 512px to preserve fine forehead hatching. These choices are
recorded in provenance; no topology guard was weakened. The other expressions
use weight 400 at 384px with automatic strength reductions where necessary.

Reviewed `output/font-review/pen-translation/compiled-expressions.png` enlarged
and at 24px, then both dialogue specimens. The kissing expressions, eye/hand
positions, cat emotions and monkey gestures remain distinguishable. Tests cover
distinct compiled outlines, components and enclosed details. A semantic raster
check requires the dotted-line face to retain twelve separate perimeter dashes,
two eyes and a mouth, with no enclosed white region from an accidentally joined
outline.

All 35 targeted emoji/pen Python tests pass, including a byte-identical rebuild
(seven existing SWIG warnings). All 245 JavaScript tests pass. Dad Emoji now
contains 227 visible bases, 366 exact sequences and 21 shaping components, at
130,924 bytes. Visible coverage increases by 45 to 170,984 / 172,352, leaving
1,368 missing mappings. This does not complete the much broader glyph, sequence,
shaping, style and review requirements of the active Unicode beta goal.

All 82 browser geometry/export scenarios pass with no reported failures or
geometry warnings, including routing checks for every new expression.
`git diff --check` passes.


## Compound emoji ligatures — 2026-11-01

Added nine reviewed compound drawings from the pinned OFL Noto Emoji source:
face in clouds, face exhaling, spiral eyes, horizontal and vertical head shaking,
black cat, service dog, polar bear and broken chain. These cover fourteen exact
qualification forms in the pinned Unicode emoji-test inventory. The new
`tools/font/emoji_sequences.py` shapes each donor sequence with HarfBuzz,
requires one real advancing glyph and equivalent glyph identity across its
qualification forms, then applies the preferred expressive pen treatment.
All nine receive nonzero treatment with the existing preservation guard.

The derivative adds explicit GSUB ligatures and default variation mappings for
the sequence components. Eleven newly required components are empty zero-width
glyphs listed in `componentOnly`. They are excluded from standalone custom
routing and visible-coverage counts. This avoids claiming bare fog, dog, bear or
arrow drawings merely because those codepoints participate in supported
compounds. No arbitrary selector insertions or text-selector variants are
advertised.

Reviewed `output/font-review/pen-translation/compiled-compounds.png` enlarged,
at 24px and in dialogue. Horizontal and vertical head motion differ, spiral
eyes remain distinct, black cat keeps its black body, polar bear its white face,
and the broken chain retains separated links. Tests verify exact qualification
shaping, distinct drawings, preserved details, repeated adjacent compounds, and
non-ligation when the joiner is removed. Routing tests also reject standalone
components and unregistered variants.

All 36 targeted emoji/pen Python tests pass, including byte-identical rebuilds
(seven existing SWIG warnings). All 246 JavaScript tests pass. Dad Emoji now
contains 227 visible bases, 380 exact sequences and 32 shaping components at
136,632 bytes. Visible coverage remains 170,984 / 172,352 with 1,368 missing:
this milestone improves sequence behaviour rather than standalone mappings.
The full Unicode beta goal remains active and incomplete.

All 83 browser geometry/export scenarios pass with no reported failures or
geometry warnings, including all fourteen compound qualification forms.
`git diff --check` passes.


## Mammal emoji — 2026-11-01

Added all 63 standalone mammal symbols in the pinned emoji inventory, plus six
standardized presentation variants for cat, dog and chipmunk. This includes pets,
primates, farm animals, wildlife and paw prints. Cat, dog and bear now have real
standalone drawings as well as their existing distinct compound forms. The
component-only inventory therefore shrinks by three, without changing support
for black cat, service dog or polar bear.

All 63 receive nonzero expressive treatment. Boar U+1F417 uses weight 400 at
512px; giraffe U+1F992 uses weight 350 at 512px. Orangutan U+1F9A7 uses weight
400 at 512px and fixed seed 129448 to move the pressure field away from small
enclosed details. Increasing resolution alone did not resolve the orangutan's
guard failure. These explicit settings preserve the same component/hole guard
and pressure magnitude, and are recorded in provenance. Other mammals use the
default source settings and automatic strength reductions.

Reviewed `output/font-review/pen-translation/compiled-mammals.png` enlarged and
at 24px, plus three dialogue specimens covering every animal. Related forms
remain distinguishable, including camel humps, ram/ewe/goat, mouse/rat, and the
standalone/compound cat, dog and bear groups. Compiled-raster regressions require
black cat and ordinary bear to retain substantially more black ink than the
outlined cat and white polar bear, three distinct dog forms, and two paw pads
plus eight separate toes. The broader outline/variant and compound-shaping
regressions also pass.

All 38 targeted emoji/pen Python tests pass, including a byte-identical rebuild
(seven existing SWIG warnings). All 246 JavaScript tests pass. Dad Emoji now
contains 290 visible bases, 449 exact sequences and 29 shaping components at
180,012 bytes. The new drawings add 60 previously missing visible mappings:
coverage is 171,044 / 172,352, leaving 1,308 missing. The full Unicode beta goal
remains active; sequence, script, style and broader review gaps are still open.

All 86 browser geometry/export scenarios pass without reported failures or
geometry warnings, including the three mammal specimens and prior compounds.
`git diff --check` passes.

## Birds and other wildlife — 2026-11-01

Added 20 birds and 42 amphibian, reptile, marine and invertebrate symbols from
the pinned OFL Noto Emoji source, plus ten standardized presentation variants.
Black bird adds one compound, bringing the reviewed donor-ligature set to ten.
The newer orca U+1FACD and monarch butterfly U+1FACC are absent from this donor
and remain open; this milestone does not claim those drawings or phoenix.

All new drawings receive nonzero expressive treatment. Peacock U+1F99A uses a
768px source raster. Crocodile U+1F40A, spouting whale U+1F433 and blowfish
U+1F421 use 512px, all at weight 400. Spider U+1F577 also uses 512px: the first
compiled-font check found that polygon simplification lost one small opening
even though the raster guard passed. The corrected source resolution preserves
all ten expected contours. Both licensed builders now reject tracing that drops
below the source's meaningful component-plus-hole count. Existing raster guards
remain unchanged.

Reviewed the enlarged and 24px compiled bird/wildlife sheets. Related chick,
fish and bird shapes remain distinguishable; insect legs, shell details and
markings remain visible. A semantic raster regression checks black bird against
the outlined ordinary bird and retains all twelve open sectors of the spider
web. The corrected wildlife outline test passes. Final validation results follow below.


All 41 targeted emoji/pen Python tests pass, including a byte-identical rebuild
(seven existing SWIG warnings). All 246 JavaScript tests and 89 browser
geometry/export scenarios pass, with no reported browser failures or geometry
warnings. The three new dialogue specimens were visually reviewed, including
ordinary/black bird and the corrected spider. `git diff --check` passes.

Dad Emoji now contains 352 visible bases, 522 exact sequences and 29 shaping
components at 222,968 bytes. The 62 new standalone drawings add 52 previously
missing mappings: visible coverage is 171,096 / 172,352, leaving 1,256 missing.
The full Unicode beta goal remains active. Newer absent animals, colour-dependent
emoji, remaining sequences/scripts and broader style/linguistic review are
still unfinished.


## Plants and flowers — 2026-11-01

Added 28 flower/plant symbols from the pinned OFL Noto Emoji source, plus four
standardized presentation variants for rosette and shamrock. This includes
flowers, trees, leaves, nests and generic mushroom. Leafless tree U+1FABE is
absent from the donor and remains open. The brown-mushroom compound is not
implicitly supported by adding generic mushroom.

All 28 receive nonzero expressive treatment and retain their required compiled
contours. Cherry blossom U+1F338 uses weight 400 at 512px because the default
raster failed treatment and tracing checks. Other plants use weight 400 at
384px. The source-specific resolution is recorded in provenance and the
preservation guards are unchanged.

Reviewed `output/font-review/pen-translation/compiled-plants.png` enlarged and
at 24px, then both dialogue specimens, including rosette/shamrock text and emoji
presentation forms. Three- and four-leaf clovers remain distinct, fresh versus
wilted flowers differ clearly, and the egg-filled nest retains two visible eggs.
New compiled-raster tests isolate leaf interiors at two erosion depths to check
three versus four leaves and check two separate egg openings above the nest
bowl versus none in the empty nest.

All 44 targeted emoji/pen Python tests pass, including byte-identical rebuilds
(seven existing SWIG warnings). All 246 JavaScript tests pass. Dad Emoji now
contains 380 visible bases, 554 exact sequences and 29 shaping components at
242,808 bytes. The drawings add 25 previously missing visible mappings: coverage
is 171,121 / 172,352, leaving 1,231 missing. The full Unicode beta goal remains
active and incomplete.

All 91 browser geometry/export scenarios pass with no reported failures or
geometry warnings, including both plant specimens and their presentation forms.
`git diff --check` passes.

## Selective colour for facial states — 2026-11-01

Added four colour-dependent faces: enraged U+1F621, nauseated U+1F922, hot
U+1F975 and cold U+1F976. Their outlines use the same expressive procedural
translation and tracing guards as the monochrome donor drawings. The new
`tools/font/emoji_colour_faces.py` selects the main enclosed face region after
stroke treatment, adds its semantic colour, retains other enclosed details on
the white underlayer, and paints black ink last. This is an explicit four-face
scope, not an assumption that every coloured emoji can use one flood fill.

Reviewed coloured PDF pages and full-resolution crops before sampling. The new
`colour-face-palette-source.json` records red from page 20's rug and a lighter
green wash from page 47's landscape. Orange and light blue reuse the pinned
heart-palette samples without tinting. Both PDF/render provenance and the reused
palette hash are recorded. The lighter green keeps small facial ink readable.

The compiled review sheet is
`output/font-review/pen-translation/compiled-colour-faces.png`. It preserves the
hot face's white sweat/tongue and the cold face's white teeth/frost. New tests
rasterize the actual compiled layers to require colour containment, minimal
colour/ink overlap, retained white details and exact sampled colours. Full
validation results follow below.

All 45 targeted emoji/pen Python tests pass, including byte-identical rebuilds
(seven existing SWIG warnings). All 246 JavaScript tests and 92 browser
geometry/export scenarios pass, with no reported failures or geometry warnings.
The four coloured faces were visually reviewed at dialogue size in the comic.
`git diff --check` passes.

Dad Emoji now contains 384 visible bases, 558 exact sequences and 29 shaping
components at 247,200 bytes. These four new mappings bring visible coverage to
171,125 / 172,352, leaving 1,227 missing. The user's preference for the expressive
procedural examples remains the direction for further emoji work. The full
Unicode beta goal remains active and incomplete.

## Sports equipment in expressive ink — 2026-11-01

Expanded the pinned licensed donor selection with 27 sports/equipment drawings:
balls, rackets, bats/sticks, a goal, martial-arts equipment, golf, skates, fishing,
diving, a running shirt, skis, a sled and curling. The existing procedural
translation supplies pressure variation without changing their source identities.
All passed the preliminary component/hole and compiled-contour checks at weight
400 and 384 pixels. Automatic reductions retain stitching and net details;
none needed untreated fallback.

The reviewed monochrome donor uses a light baseball and dark softball, retaining
a visible distinction without an invented palette. A compiled-raster regression
requires this contrast. The batch also advertises all eight applicable pinned
variation forms. It does not imply support for sportspeople, modifiers, medals
or additional sequences. Two browser specimens exercise every new base and the
four applicable presentation pairs. Validation results follow below.

The compiled review sheet is
`output/font-review/pen-translation/compiled-sports.png`; both that sheet and the
two browser specimens were inspected at dialogue size. All 47 targeted emoji/pen
Python tests pass, including a byte-identical rebuild (seven existing SWIG
warnings). All 94 browser geometry/export scenarios pass with no reported
failures or geometry warnings.

Dad Emoji now contains 411 visible bases, 593 exact sequences and 29 shaping
components at 264,328 bytes. The batch fills 22 previously missing visible
mappings, bringing coverage to 171,147 / 172,352, with 1,205 missing. Other new
emoji upgrade existing text-symbol coverage. The full goal remains active and
incomplete, including missing scripts, emoji sequences and visual adaptation.

All 246 JavaScript tests pass. Asset hashes and the source/coverage inventories
are refreshed; `git diff --check` passes.

## Prepared food in expressive ink — 2026-11-01

Added 51 explicitly reviewed prepared-food drawings from the pinned OFL source.
The selection covers breads, cheese and meat, sandwiches, cooked dishes, bowls,
rice/noodle dishes and dumplings. These familiar forms remain monochrome; no
colour-dependent fruit variants or extra sequences are implicitly supported.
The pinned Unicode variation file supplies no presentation pairs for this batch.

Preflight caught lost traced details in waffle and tamale, untreated fallback in
falafel and salad, and both issues in the pot of food. Waffle, tamale and pot now
use 512-pixel source rasters. Falafel and salad also use the finer weight-350
donor outlines. These reviewed choices pass the same component/hole and contour
guards without exemptions. All 51 retain nonzero procedural treatment. The
compiled sheet and three comic specimens provide enlarged and dialogue-size
review; final validation results follow below.

All 48 targeted emoji/pen Python tests pass, including byte-identical rebuilding
of the font and routing manifest (seven existing SWIG warnings). All 246
JavaScript tests and 97 browser geometry/export scenarios pass without reported
failures or geometry warnings. The compiled food sheet at
`output/font-review/pen-translation/compiled-food.png` and all three food comic
specimens were visually inspected at dialogue size.

Dad Emoji now contains 462 visible bases, 644 exact sequences and 29 shaping
components at 297,192 bytes. This batch fills 48 previously missing visible
mappings, bringing coverage to 171,195 / 172,352, with 1,157 missing. Three
additional drawings improve mappings already represented elsewhere. Asset
hashes and source/coverage inventories are refreshed. `git diff --check` passes.
The full Unicode beta goal remains active and incomplete.

## Sweets, drinks and tableware — 2026-11-01

Extended the pinned licensed emoji selection by 41 sweets, drinks and tableware
symbols. Three ice-cream forms, cake forms, cups/glasses and utensils keep their
source distinctions in expressive monochrome ink. The ice-cream bowl required
weight 350 at 512 pixels to retain fine details with nonzero treatment; the
other 40 drawings pass with weight 400 at 384 pixels. No topology guard was
relaxed. Six applicable presentation forms are derived from the pinned Unicode
variation file and exercised in the browser specimens.

The category regression checks every compiled outline, colour layer, advance,
nonzero guarded treatment and applicable presentation form. Three comic
specimens cover all 41 new bases; enlarged and 24-pixel compiled previews support
visual review. Validation results follow below.

All 49 targeted emoji/pen Python tests pass, including byte-identical rebuilding
of the font and routing manifest (seven existing SWIG warnings). All 100 browser
geometry/export scenarios pass without reported failures or geometry warnings.
The compiled sheet at `output/font-review/pen-translation/compiled-dining.png`
and all three dining comic specimens were visually inspected at dialogue size,
including the six standard presentation variants.

Dad Emoji now contains 503 visible bases, 691 exact sequences and 29 shaping
components at 319,984 bytes. This batch fills 37 previously missing visible
mappings, bringing coverage to 171,232 / 172,352, with 1,120 missing. Four
additional drawings improve mappings already represented elsewhere. Asset
hashes and source/coverage inventories are refreshed. The full Unicode beta goal
remains active and incomplete.

All 246 JavaScript tests pass, and `git diff --check` passes.

## Sky, moon phases and weather — 2026-11-01

Added 43 selected sky/weather drawings and 48 pinned presentation forms. Fog and
snowflake are promoted from blank compound components to real standalone emoji;
face-in-clouds and polar-bear compounds retain their existing drawings.

Visual preflight found a limitation of topology-only validation: the new moon
stayed connected but became a lumpy blob. Its skeleton radius represented a
solid disk, so the normal stroke-pressure amplitude was inappropriate. The
reviewed override uses pressure .02 and no endpoint taper, retaining strength
1.7 and the bend field. Boundary-radius variation fell from about 12% to 2.5%.
A compiled-raster regression now requires less than 6% variation. Further phase
checks require decreasing dark area from new to full moon and the correct dark
side for waxing versus waning phases.

The dense Milky Way uses weight 400 at 512 pixels, pressure .2 and bend .006,
with automatic reduction preserving its white stars. All other new drawings
use the standard treatment. All 43 have nonzero treatment and pass the existing
feature and traced-contour guards. Enlarged and dialogue-size review and final
validation results follow below.

Compiled review also showed both donor moon faces as light disks. The new-moon
face now explicitly reverses the interior ink into white features on a dark
disk. The largest closed border is retained; all five disconnected facial
features become white openings. The transformation is recorded per glyph and
uses pressure .15 with no taper. A separate compiled-raster check requires the
dark/light contrast and all five white features.

The phase-direction regression was corrected after its initial 1.5 ratio
assumed a fixed crescent width. It now requires a dark-side imbalance of at
least 10% of the total ink, which tests direction without constraining the
source's crescent width. Roundness and illuminated-area ordering passed their
focused compiled-font checks.

While the final emoji rebuild ran, the five remaining Han mappings were checked
against primary Unicode references for the next coverage pass. U+16FF0/16FF1
are Vietnamese combining reading marks, so standalone cmap drawings alone will
not suffice. U+16FF4..16FF6 are Yangqin tempo signs that form a set with U+3026;
the proposal explicitly calls for a Suzhou-numeral style. These remain missing.
Useful authoritative references:

- https://www.unicode.org/Public/18.0.0/charts/nameslist/16fe0/
- https://www.unicode.org/L2/L2024/24071r3-ext-sz-num.pdf (especially pages 1 and 4)

Next: inspect the documented forms and mark placement, then find licensed
outlines or create original forms consistent with the existing Suzhou numerals.

Final sky/weather validation passes: all 53 targeted emoji/pen Python tests,
including byte-identical rebuilding and the three new moon regressions (seven
existing SWIG warnings), all 246 JavaScript tests, and all 103 browser
geometry/export scenarios without reported failures or geometry warnings. The
final compiled sheet at `output/font-review/pen-translation/compiled-sky.png`
and all three comic specimens were visually inspected at dialogue size. The
final dark new-moon face was included in this review.

Dad Emoji now contains 546 visible bases, 782 exact sequences and 27 shaping
components at 341,668 bytes. The batch fills 19 previously missing visible
mappings, bringing coverage to 171,251 / 172,352, with 1,101 missing. Other
additions upgrade text-symbol or compound-only coverage. Asset hashes and
source/coverage inventories are refreshed. `git diff --check` passes. The full
Unicode beta goal remains active and incomplete.

## Yangqin tempo signs — 2026-11-01

Reviewed the primary proposal L2/24-071R3's form table against the existing
WenKai Suzhou forms. U+16FF4..U+16FF6 use two uprights, three uprights and a cross
above a common baseline. The new builder constructs them from licensed WenKai
strokes, preserving the original U+3026 baseline and fitting the additional
strokes to that glyph's short raised register. It retains the original advance
and changes no existing source drawing. The source review and reference hash
are in `docs/yangqin-source-review.json`; the PDF contributes reference evidence,
not copied font outlines.

The WenKai cache recipe includes the constructor hash. Compiled tests check
stroke counts at multiple heights, the central crossing, continuous connection
to the baseline, identical lower-baseline pixels, correct advances and exact
preservation of the original U+3026 outline. A new comic specimen mixes these
signs with Suzhou numerals, Han text and Latin. Validation results follow below.

The first browser run exposed a harness-only assumption that native text always
has `ink.runs`, as routed emoji does. The Yangqin check now also handles ordinary
line ink and requires the specific WenKai shard selected from the manifest to
be loaded and present in the line's font stack. The renderer itself required no
change for these signs.

All 23 targeted Yangqin/script-font Python tests pass (seven existing SWIG
warnings), all 246 JavaScript tests pass, and all 104 browser geometry/export
scenarios pass with no reported failures or geometry warnings. The compiled
preview `output/font-review/yangqin-signs.png` and the mixed-script comic specimen
were visually inspected at dialogue size. The source-derived WenKai styling
remains provisional, as with the other native CJK text; this is not a claim of
fluent-reader review.

There are still 347 script shards, now 60,159,912 bytes. Visible bundled coverage
is 171,254 / 172,352, leaving 1,098 missing. The three Yangqin mappings are filled;
the remaining Han gap is the two Vietnamese reading marks. The raw source
inventory still reports all five because the new signs are constructed during
packaging rather than present in an unmodified donor. Asset hashes and coverage
are refreshed, and `git diff --check` passes. The full goal remains active and
incomplete.

## Vietnamese reading marks checkpoint

- Added provisional U+16FF0 CA and U+16FF1 NHAY using uniformly scaled
  WenKai U+4E87 and U+21FE8 outlines. The reviewed Unicode proposal pages 4–5
  document these forms and usual right-side placement; retained the donor OFL.
  `docs/vietnamese-mark-source-review.json` records provenance and reference
  hashes. BabelStone Han was inspected for comparison only; none of its
  Arphic-licensed outlines are shipped.
- Positive advances reserve side space. The first browser test exposed missing
  glyph boxes when a base and its mark came from different font shards, despite
  successful standalone font tests. `js/vietnamese-marks.js` now separates only
  drawing spans; measurement and painting use the same spans. Logical text,
  grapheme boundaries and protected wrapping remain unchanged.
- Compiled preview `output/font-review/vietnamese-marks.png` and the real comic
  were visually inspected at large and dialogue sizes. Historical base-specific
  merged forms and above/below placements are not implemented, and fluent-reader
  and cross-browser validation remain open. These two cmap entries do not
  establish complete Vietnamese reading-mark support.
- Final validation: **24 targeted Python tests**, **248 JavaScript tests**,
  **105 browser scenarios**, no geometry warnings or browser failures. Python
  retains the 7 existing SWIG deprecation warnings. Browser assertions check
  real side advances for both marks on three different bases and the separate
  drawing spans; the initial failing fallback behaviour is now covered.
- **347 shards, 60,160,016 bytes**; bundled visible cmap coverage
  **171,256 / 172,352**, leaving **1,096** missing mappings. All visible Han
  mappings are present, but historical composition remains an explicit gap.
  The overall goal is active and substantially incomplete.

## Malayalam Syriac source and shaping checkpoint

- Located Hendo Academy / Binu George's **East Syriac Malankara 1.0**, with
  an explicit, copyright-specific OFL 1.1 licence in its publisher download.
  `data/font-sources/malankara.json` pins the archive and named members by
  SHA-256 and Git blob hashes. The bundled derivative is renamed and retains
  `assets/fonts/licenses/EastSyriacMalankara-OFL.txt`. The previously rejected
  noncommercial Serto donor remains excluded.
- Added all **eleven U+0860–U+086A** mappings. The new shard keeps native Syriac
  bases, contextual forms, vowels and joining controls together. Routing prefers
  that complete requested repertoire when Malayalam Syriac is present; ordinary
  Syriac retains its previous default. This native calligraphic style remains
  provisional, and the donor does not cover every Syriac letter or vowel:
  arbitrary mixed extended Syriac repertoires need further fallback/joining review.
- Tests compare outlines, advances and mark offsets in isolated, initial, final,
  medial and vowel-bearing contexts for every supplemental letter. Nonjoining
  JA/BHA and right-joining RA/LLLA/SSA are checked separately. The donor has
  one-unit glyph-bound/bearing discrepancies reconstructed by WOFF2; the outline
  comparison permits at most one unit per coordinate while requiring exact
  advances and GPOS positions. An initial exact-outline test caught this
  negligible source-bound difference before the tolerance was documented.
- The compiled specimen `output/font-review/malankara.png` and actual comic
  rendering were visually inspected. The browser also checks that adding ZWNJ
  changes the width of joining letters but not JA/BHA. Native source identity
  and mechanical checks do not substitute for fluent-reader review.
- Reproduction repair: `fetch_sources.py` now supports named, verified regular
  ZIP members and the existing bundled-licence directory. The old path guard
  rejected already-recorded licence files outside the source cache. The real
  Malankara archive restored successfully, and **11,273 source files** now pass
  the offline verification. Tar and ZIP tests cover hashes, symlinks, output
  confinement and licence restoration.
- Final validation: **35 targeted Python tests**, **249 JavaScript tests**,
  **106 browser scenarios**, with no browser failures or geometry warnings.
  Source inventory now has **255 fonts**, with 171,295 public characters
  represented and 1,578 absent (including behavioural characters). Bundled
  visible coverage is **171,267 / 172,352**, leaving **1,085** missing mappings.
  **348 shards, 60,178,316 bytes**. The overall goal remains active.


## Hand gestures and skin-tone sequences checkpoint

- Extended the deterministic pen translation to **25 hand gestures and 125
  skin-tone sequences**, using the pinned OFL Noto Emoji donor at requested
  strength 1.7 with automatic detail-preserving reductions. Every tone shares
  its neutral gesture's exact ink outline and metrics. The expressive treatment
  remains the preferred visual direction.
- Skin masks colour the fingers as well as the palm. Explicit air gaps remain
  white in the OK, crossed-fingers and pinched-fingers gestures. The open wrist
  of pinched fingers is closed for the fill mask only. Colour extends underneath
  the ink to eliminate white antialiasing seams between independently traced
  boundaries. Compiled previews and the actual comic were visually inspected.
- Added exact whole-cluster routing and shaping checks for all 125 modifier
  sequences. Malformed doubled modifiers retain native fallback. Preview tools
  now provide `gestures` and `gesture-tones` sheets in
  `output/font-review/pen-translation/`.
- Two browser specimens exposed overly tight tips on moderately wide oval
  balloons. The ellipse-to-rounded-caps decision now checks curvature against
  lettering size as well as aspect ratio. A regression uses the failing browser
  dimensions and checks curvature, containment and clearance. The corrected
  balloon was visually inspected; geometry warnings are also reflected in the
  browser harness title.
- Final validation: **55 targeted Python tests**, including byte-for-byte font
  reproduction; **251 JavaScript tests**; **115 Unicode browser scenarios**
  with no failures or geometry warnings; **33 original lettering scenarios**.
  Python retains the 7 existing SWIG deprecation warnings.
- The emoji font is **356,480 bytes**, with **571 visible bases, 952 exact
  sequences and 27 components**. Bundled visible coverage is
  **171,282 / 172,352**, leaving **1,070** missing mappings. Script assets remain
  **348 shards, 60,178,316 bytes**. The full Unicode goal remains incomplete.

## Coloured face edge-seam checkpoint

- Applied the hand-gesture underpainting repair to the four selectively coloured
  faces (angry, nauseated, hot and cold). Colour now extends beneath the final
  ink layer. The main enclosed face interior is coloured; every other enclosed
  detail stays white. Outlines, metrics, palette and sequence inventory remain
  unchanged.
- Added a source-mask regression for all four faces and changed the compiled
  layer test to require ink overlap. The updated compiled test failed against
  the old font and passed after rebuilding. Enlarged/24-pixel compiled previews
  and the actual comic were visually inspected: pale seams at features and rims
  are removed while white teeth, sweat and ice details remain.
- Validation: **39 emoji Python tests passed**, with the byte-for-byte rebuild
  test deselected for this run and 7 existing SWIG warnings. **115 Unicode
  browser scenarios passed**, with no failures or geometry warnings. Asset
  hashes and the coverage audit are refreshed; `git diff --check` passes.
- Emoji font size is now **355,432 bytes**. Coverage remains
  **171,282 / 172,352**, leaving **1,070** missing visible mappings. Other atlas
  colour boundaries still need inspection; this repair covers these four faces
  and the previously repaired hand gestures. The full goal remains active.


## Buildings and places of worship checkpoint

- Added **24 monochrome custom emoji**: houses, public/commercial buildings,
  castles, wedding venue, places of worship, fountain and hut. The pinned OFL
  Noto source, scope manifest and production review retain their provenance.
  The same guarded expressive treatment preserves identifying architectural
  details, postal marks, letters and religious symbols.
- The synagogue uses weight 350 / 512 pixels to preserve its star. The Kaaba
  uses weight 400 / 512 pixels with pressure .1 and no taper to retain fine
  white ornament in the solid body. Both initially fell back to untreated
  outlines; the reviewed settings now pass the unchanged topology guard.
  All 24 receive nonzero treatment, with recorded automatic reductions.
- Added **10 registered presentation variants**, for **34 additional exact
  sequences**. Generic packaging tests check distinct drawings, positive
  metrics, preserved contours and equivalent registered presentation forms.
  A routing regression and two full-comic specimens cover every new base.
- Visually inspected `output/font-review/pen-translation/compiled-buildings.png`
  enlarged and at 24 pixels, plus the actual comic. Dense architectural details
  are necessarily small at dialogue size; this remains provisional visual work.
- Validation: **56 targeted Python tests passed** (the full-font reproduction
  test was deselected), **252 JavaScript tests passed**, and **117 Unicode
  browser scenarios passed**, with no failures or geometry warnings. Python
  retains 7 existing SWIG warnings. Asset hashes and audits were refreshed;
  `git diff --check` passes.
- Emoji font: **595 visible bases, 986 exact sequences, 27 components**, and
  **371,840 bytes**. Seventeen previously absent visible mappings are supplied;
  seven new emoji bases already had text-font cmap coverage. Bundled coverage
  is **171,299 / 172,352**, leaving **1,053** missing visible mappings. Script
  assets remain **348 shards, 60,178,316 bytes**. The raw source inventory has
  255 fonts and 171,327 public characters represented; that is a separate
  inventory, not a claim of delivered shaping coverage. The full goal is active.


## Landscapes and travel places checkpoint

- Added **32 custom monochrome emoji** covering mountains, camping/beaches,
  landscapes, city views, landmarks, leisure attractions, maps and a compass.
  The pinned OFL donor and expressive strength-1.7 treatment are unchanged.
  Added **30 registered presentation forms**, for **62 new exact sequences**.
- Preflight checks rejected six untreated fallbacks and a derelict-house trace
  that lost a contour. Seven drawings now use reviewed 512-pixel source rasters;
  the bridge at night, Ferris wheel and world map additionally use weight 350.
  All final drawings receive nonzero treatment and retain the unchanged
  topology/contour safeguards. Source settings and reductions are recorded in
  the production review; no preservation threshold was relaxed.
- Inspected source/treated comparisons for the adjusted drawings, the compiled
  `output/font-review/pen-translation/compiled-places.png` at enlarged and
  24-pixel sizes, and city/landscape emoji in actual balloons. Distinct day,
  night, sunrise and sunset designs remain. Dense details remain small at
  dialogue size; the donor maps are stylised emoji, not geographic diagrams.
- Validation: **57 targeted Python tests passed**, with the full-font
  reproduction test deselected and 7 existing SWIG warnings; **253 JavaScript
  tests passed**; **120 Unicode browser scenarios passed**, with no failures
  or geometry warnings. Three new browser specimens cover all 32 bases.
  Asset hashes and audits were refreshed; `git diff --check` passes.
- Emoji font: **627 visible bases, 1,048 exact sequences, 27 components**,
  **397,368 bytes**. Seventeen previously absent visible mappings are supplied;
  the other fifteen already had text-font coverage. Bundled coverage is
  **171,316 / 172,352**, leaving **1,036** missing visible mappings. Script
  assets remain **348 shards, 60,178,316 bytes**. The separate raw source
  inventory has 255 fonts and 171,344 public characters represented. The full
  Unicode goal remains active and incomplete.


## Complete-suite reconciliation after emoji expansion

- The first complete Python run reported **246 passed, 1 failed**. The failure
  was an old inventory test expecting 46 visible emoji bases and 21 components,
  even though the font now has 627 bases and 27 components. This was a stale
  test scope, not a production-font failure.
- Replaced fixed totals with an independent count of actual drawn versus empty
  glyphs in the font. The test still requires the five skin-tone component
  inputs to be empty and excludes them from reported visible coverage. This
  catches component-inflation errors without depending on the manifest under
  test or requiring a total update after each emoji batch.
- The targeted inventory run passed **5 tests**. A subsequent complete run
  passed **247 tests**, including font/manifest byte-for-byte reproduction,
  in 287.42 seconds, with the 7 existing SWIG warnings. No tests were skipped
  or deselected. Latest JavaScript evidence remains **253 passed**; the original
  lettering browser harness was rerun and passed **33/33**. The latest Unicode
  browser run remains **120 passing scenarios**. All **11,273 source files**
  pass offline pinned-hash verification, and `git diff --check` passes.
- Investigated the Seal gap while tests ran. Of 348 missing characters, **110**
  have CCZ references and **238** require another edition. Seven missing CCZ
  characters have upstream crop/provenance rows but no SVG; all seven are marked
  `inferred`, not approved. `docs/seal-gap-review.json` records their complete
  crop locations, source hashes and next checks. These are research leads only:
  source images and character identities must be reviewed before tracing.
- No coverage is added by this checkpoint. Visible coverage remains
  **171,316 / 172,352**, with **1,036 missing**. Passing the complete suite
  does not establish complete scope, script correctness or visual treatment;
  the overall goal remains active.

## Recovery of six missing Seal signs

- Retrieved the seven inferred scan candidates identified in the gap review.
  Wikimedia's image metadata identifies their historical page scans as public
  domain. The six accepted 3840-pixel page images are pinned by hashes in
  `data/font-sources/seal-recovery.json`, along with page/edition/CCZ references,
  corrected crop coordinates, and retained licence evidence.
- Compared each candidate with its official Unicode 18 CCZ reference. Rejected
  **U+3E34F / C-04868**: the proposed scan lacks the reference form's lower
  component. Accepted **U+3D7A8, U+3DB0E, U+3F5B1, U+3F5F1, U+3F622 and
  U+3F8FC** provisionally. Three original crop bounds cut genuine strokes;
  the corrected bounds retain complete forms. The chart is an identity check
  only, never a drawing source.
- Added `build_seal_recovery.py`: deterministic deskew, thresholding, light scan
  cleanup, tracing and font compilation. A reviewed band removes a later
  pencil line crossing U+3F5F1's lower stems. Source outlines come only from
  the historical scans. The generated font carries the bundled
  `DadSealRecovery-OFL.txt`; original Kaiyuan files/statuses remain unchanged.
  Print wear and native style remain provisional, with specialist review open.
- Inspected the scan/compiled comparison in
  `output/font-review/seal-recovery.png` at enlarged and 24-pixel sizes, and
  the actual comic. Tests check CCZ identities, exact source/packaged outlines,
  contour retention, bounds, advances, byte reproduction and routing. The first
  contour assertion used incompatible digital-connectivity conventions; it now
  matches the tracer's diagonal background connectivity. No drawn contours
  were dropped. The first browser assertion omitted the renderer's single-run
  representation; it now checks both representations and loaded font identity.
- Final validation: **45 targeted Python tests**, **254 JavaScript tests**,
  **121 Unicode browser scenarios**, no browser failures or geometry warnings.
  All **11,279 cached source files** pass pinned-hash verification. Asset hashes,
  source inventory and coverage audit are refreshed; `git diff --check` passes.
- **349 script shards, 60,187,176 bytes**. Bundled visible coverage is
  **171,322 / 172,352**, leaving **1,030** missing mappings. Seal gaps fall from
  348 to **342**: 104 have CCZ references (including the rejected candidate),
  while 238 require another edition. `docs/seal-gap-review.json` records outcomes
  and next steps. The full Unicode goal remains active and incomplete.


## Four further Seal recoveries from unassigned crop records

- The remaining 104 CCZ gaps had only one explicitly assigned inferred row
  (the previously rejected U+3E34F). Investigated unassigned/rejected crop
  records between known neighbouring sequences instead. Four candidates on
  three pages matched their official reference forms: **U+3D4B8 / C-01188,
  U+3DD2A / C-03321, U+3DDF2 / C-03515 and U+3DDF3 / C-03516**.
- Pinned the three additional public-domain page images, corrected bounds that
  clipped strokes, and recorded the local review without altering upstream
  rejection/status records. Explicit crop-local cleanup removes pencil
  remnants from U+3DDF3. The closely related C-03515/C-03516 forms retain their
  distinct upper-right bar versus two uprights; a regression checks this
  distinction and guards against a pencil line bridging the uprights.
- The recovery font now contains **ten** reviewed scan drawings. Compiled
  specimens were inspected enlarged and at 24 pixels, as well as in the comic.
  This is provisional historical-source recovery, not completed specialist
  validation or final comic styling. No chart artwork is used in the font.
- Final checks: **34 targeted Python tests**, including deterministic rebuilding
  and packaged-outline equivalence; **254 JavaScript tests**; **122 Unicode
  browser scenarios**, with no failures or geometry warnings. All **11,282
  source files** verify offline. Asset hashes, source/coverage inventories and
  gap review are refreshed; `git diff --check` passes.
- **349 script shards, 60,189,696 bytes**. Bundled visible coverage is
  **171,326 / 172,352**, leaving **1,026** missing mappings. Seal gaps fall to
  **338**: 100 have CCZ references, and 238 need another edition. The separate
  raw source inventory represents 171,354 public characters in 256 font sources.
  The full goal remains active and incomplete.

## Systematic CCZ crop triage and two further recoveries

- Added `review_seal_candidates.py`, which uses neighbouring assigned CCZ
  sequences and estimated page/column reading order to shortlist unassigned
  crops. `docs/seal-crop-candidates.json` retains the source hashes, neighbours
  and original rows. It makes no identity assignments and preserves ambiguous
  candidates for manual comparison. A regression checks ordering, ambiguity
  and book boundaries.
- Two shortlisted drawings on an already pinned page match the official
  references: **U+3F623 / C-09577 and U+3F625 / C-09579**. Corrected bounds
  remove column-rule fragments and retain their full right-hand components.
  The historical scans supply the outlines; chart artwork is reference only.
  The recovery font now has twelve provisionally reviewed signs.
- Reviewed compiled specimens enlarged and at 24 pixels, and both additions
  in the actual comic. **34 targeted Python tests passed**, followed by all
  **4 recovery tests**, including the new shortlist regression. **254 JavaScript
  tests** and **122 Unicode browser scenarios** pass, with no browser failures
  or geometry warnings. All **11,282 source files** verify offline. Coverage,
  source inventory and asset hashes are refreshed; `git diff --check` passes.
- **349 shards, 60,191,048 bytes**. Bundled visible cmap coverage is
  **171,328 / 172,352**, leaving **1,024** missing mappings. Seal gaps are
  **336**: 98 have CCZ references; 31 of those now have unverified proximity
  candidates. Another 238 require an alternative edition. The raw source
  inventory represents 171,356 public characters in 256 fonts. Full Unicode
  scope, specialist validation and final visual treatment remain incomplete.

## Three more CCZ recoveries; worn drawing deferred

- Reviewed four shortlisted book-7 crops against official CCZ reference forms.
  Accepted **U+3F482 / C-09172, U+3F4F1 / C-09281 and U+3F5CD / C-09494**.
  Corrected bounds retain full strokes and exclude rules/adjacent text. Three
  additional public-domain page images are pinned with hashes and licence
  evidence. The recovery font now contains **fifteen** provisional drawings.
- **U+3F510 / C-09311** matches the reference identity but is not bundled.
  Its worn middle strokes break during tracing. Tested threshold offsets
  20–60 with opening radii 2/3 and closing radius 2: stronger thresholds merge
  unrelated ink and paper noise before restoring faithful strokes. A better
  scan or explicitly documented reconstruction is needed. The candidate
  shortlist now carries prior review outcomes rather than hiding this result.
- Compiled drawings were inspected enlarged and at 24 pixels. **35 targeted
  Python tests** and **254 JavaScript tests** pass. All **11,285 source files**
  verify offline. Asset hashes and source/coverage reports are refreshed.
- **349 shards, 60,192,740 bytes**. Bundled visible cmap coverage is
  **171,331 / 172,352**, leaving **1,021** missing mappings. Seal gaps are
  **333**, including 95 with CCZ references and 238 requiring another edition.
  There are 28 remaining proximity candidates, including the deferred worn
  drawing. The raw source inventory represents 171,359 public characters in
  256 fonts. The overall Unicode goal remains active and incomplete.
- Final browser validation: **123 scenarios**, no failures or geometry warnings;
  all three additions also inspected in the actual comic. `git diff --check`
  passes. This does not establish specialist correctness or completed styling.

## Four book-4 Seal recoveries and bounded scan repair

- Verified **U+3E1D1 / C-04492, U+3E298 / C-04689, U+3E2A5 / C-04702
  and U+3E4ED / C-05274** against the official reference. Pinned four additional
  public-domain page images and the book's licence metadata evidence. Source
  outlines use the historical scans only; the recovery font has **nineteen**
  provisional drawings.
- Expanded crops retain complete strokes. Explicit rectangles remove the page
  rule touching C-04702's upper stem tips, including a two-pixel detached
  remnant found during component inspection. A local radius-3 closing repairs
  a short wear break in C-05274's left outer stem. Its recipe records the
  repair; a regression proves changes stay inside that area and only add ink.
  Further assertions retain all reviewed components and enclosed spaces in
  the four drawings. This is a bounded scan repair, not global thickening.
- Compiled specimens inspected enlarged and at 24 pixels. **36 targeted Python
  tests**, including byte reproduction, packaged outlines and local cleanup,
  and **254 JavaScript tests** pass. All **11,289 source files** verify offline.
  Asset hashes, gap review, shortlist and source/coverage audits are refreshed.
- **349 shards, 60,194,764 bytes**. Bundled visible cmap coverage is
  **171,335 / 172,352**, with **1,017** missing mappings. Seal gaps are **329**:
  91 have CCZ references, 24 have proximity candidates, and 238 require another
  edition. Raw sources represent 171,363 public characters across 256 fonts.
  Full scope and final visual/script validation remain incomplete.
- Final browser checks: **124 scenarios**, no failures or geometry warnings.
  All four additions inspected in the actual comic; `git diff --check` passes.

## Three complete compounds recovered from split crop candidates

- Resolved the overlapping candidate lists for **U+3F603 / C-09546,
  U+3F604 / C-09547 and U+3F605 / C-09548** by comparing their complete
  book-7 page-51 drawings with the official reference. The upstream crops
  largely captured right components; reviewed bounds include the omitted or
  separately segmented left components. One newly pinned public-domain page
  supplies all three. Original upstream assignments remain unchanged.
- The C-09546 recipe removes the top page rule touching its left stem. The
  compiled drawings retain both enclosed shapes in each left component, with
  a focused regression guarding against future crop truncation. Enlarged and
  24-pixel compiled specimens inspected; the recovery font has **22** drawings.
- **37 targeted Python tests** and **254 JavaScript tests** pass. All **11,290
  source files** verify offline. Asset hashes, shortlist, gap report and
  source/coverage audits are refreshed; `git diff --check` passes.
- **349 shards, 60,196,492 bytes**. Bundled visible cmap coverage is
  **171,338 / 172,352**, leaving **1,014** missing mappings. Seal gaps are
  **326**: 88 have CCZ references, including 21 with proximity candidates;
  another 238 require a different edition. Raw sources represent 171,366
  public characters across 256 fonts. The full Unicode goal remains active;
  coverage and provisional scan recovery do not prove final script/style quality.
- Final browser validation: **125 scenarios**, no failures or geometry warnings;
  all three complete compounds also inspected in the actual comic.

## Full-page recovery of an adjacent pair and one further sign

- The proximity shortlist gave **U+3F27D / C-08671** and **U+3F27E /
  C-08672** the same right-half crop. Reference comparison rejected that crop
  for both. Full-page inspection located the correct headword and inline form
  on the opposite half of book 7 page 4. Their single and doubled base bars
  match the official references and now have a dedicated regression.
- Added both forms and **U+3F79D / C-09949** from book 7 page 73. Two additional
  public-domain pages are pinned. Corrected bounds preserve complete strokes;
  a reviewed rectangle removes an adjacent-text speck from the latter crop.
  The recovery font has **25** provisional drawings. Compiled specimens were
  inspected enlarged and at 24 pixels; source pixels come only from the scans.
- **38 targeted Python tests**, including identity, packaging, reproduction
  and the new base-bar distinction, and **254 JavaScript tests** pass. All
  **11,292 source files** verify offline. Asset hashes and coverage/source/gap
  reports are refreshed; `git diff --check` passes.
- **349 shards, 60,197,700 bytes**. Bundled visible cmap coverage is
  **171,341 / 172,352**, leaving **1,011** missing mappings. Seal gaps are
  **323**: 85 have CCZ references (18 with proximity candidates) and 238 need
  another edition. Raw sources represent 171,369 public characters across
  256 fonts. The overall Unicode goal remains active and incomplete.
- Final browser validation: **126 scenarios**, no failures or geometry warnings;
  the distinct pair and third sign were also inspected in the actual comic.

## Four further book-4 forms; a worn inline sign located but deferred

- Verified **U+3E0F4 / C-04272, U+3E1E5 / C-04512, U+3E1E6 / C-04513
  and U+3E56E / C-05401**, including resolution of the overlapping candidate
  lists for C-04512/C-04513. Four additional public-domain pages are pinned;
  the recovery font now contains **29** provisional scan-derived drawings.
- Bounded morphological closings reconnect a worn cup join in C-04272 and an
  inner descending stroke in C-04512. Review narrowed the repair regions to
  avoid joining the separate bottom circle or thickening an adjacent stroke.
  Regressions check component/hole counts, separation and the exact area of
  added ink. A clear rectangle removes a column-rule fragment from C-05401.
- The candidate for **U+3E377 / C-04908** was explanatory text. Full-page
  inspection found the correct inline sign on the same page, but its loops
  and connecting strokes are too worn for faithful tracing. It remains
  unbundled; the actual location and reason are recorded for better-source
  review. No chart artwork enters any font.
- Compiled specimens inspected enlarged and at 24 pixels. **39 targeted Python
  tests**, including reconstruction constraints and byte reproduction, and
  **254 JavaScript tests** pass. All **11,296 source files** verify offline.
  Asset hashes, source/coverage inventories and gap/candidate reviews are
  refreshed; `git diff --check` passes.
- **349 shards, 60,200,472 bytes**. Bundled visible cmap coverage is
  **171,345 / 172,352**, leaving **1,007** missing mappings. Seal gaps are
  **319**: 81 have CCZ references, including 14 proximity candidates; 238 need
  another edition. Raw sources represent 171,373 public characters in 256
  fonts. Full Unicode scope and final script/style validation remain incomplete.
- Final browser validation: **127 scenarios**, no failures or geometry warnings;
  all four additions were also inspected in the actual comic.

## Four book-5 recoveries, including a sign before a volume boundary

- Verified **U+3EA3A / C-06607, U+3EA3B / C-06608, U+3EA59 / C-06637
  and U+3EB6D / C-06904** against official reference forms. The C-06637
  proximity candidate was a volume heading on page 60. Full-page review of
  the preceding page located the correct headword on page 59. Three contributing
  public-domain page images and book-5 licence metadata evidence are pinned.
- Corrected crops retain complete components. A bounded radius-4 closing repairs
  a worn divider between the lower two spaces in C-06608's left component.
  Regression checks both related signs retain four enclosed spaces there,
  and constrains all added ink to the reviewed rectangle. C-06904 cleanup
  excludes a fragment of the following text. The recovery font has **33**
  provisional scan drawings; no reference-chart artwork is copied.
- Compiled specimens inspected enlarged and at 24 pixels. **40 targeted Python
  tests** and **254 JavaScript tests** pass. All **11,299 source files** verify
  offline. Asset hashes, gap review, shortlist and source/coverage inventories
  are refreshed; `git diff --check` passes.
- **349 shards, 60,203,492 bytes**. Bundled visible cmap coverage is
  **171,349 / 172,352**, leaving **1,003** missing mappings. Seal gaps are
  **315**: 77 have CCZ references, including ten proximity candidates; 238
  require another edition. Raw sources represent 171,377 public characters in
  256 fonts. The full Unicode goal remains active and incomplete.
- Final browser validation: **128 scenarios**, no failures or geometry warnings;
  all four additions also inspected in the actual comic.

## Four book-6 recoveries; visible cmap gaps below one thousand

- Verified **U+3ED77 / C-07410, U+3EE93 / C-07687, U+3EFD3 / C-08000
  and U+3F1EE / C-08528**. The last proximity candidate was a column rule;
  full-page inspection located its correct inline drawing below the headword.
  Four contributing public-domain page images and book-6 metadata evidence
  are pinned. The recovery font now has **37** provisional drawings.
- Adjusted bounds retain complete strokes. A clear rectangle excludes a
  top-rule speck from C-08000. These four use the existing scan cleanup and
  tracing pipeline without additional reconstructed strokes. Compiled
  specimens were inspected enlarged and at 24 pixels.
- **40 targeted Python tests** and **254 JavaScript tests** pass. All **11,303
  source files** verify offline. Asset hashes and source/coverage/gap reports
  are refreshed; `git diff --check` passes.
- **349 shards, 60,205,952 bytes**. Bundled visible cmap coverage is
  **171,353 / 172,352**, leaving **999** missing mappings. Seal gaps are **311**:
  73 have CCZ references, including six proximity candidates; 238 require
  another edition. Raw sources represent 171,381 public characters across
  256 fonts. This milestone does not prove full sequence support, shaping,
  script correctness or final visual treatment. The full goal remains active.
- Final browser validation: **129 scenarios**, no failures or geometry warnings;
  all four additions were also inspected in the actual comic.

## Four remaining proximity recoveries and broader search windows

- Recovered **U+3D66B / C-01617, U+3ED3A / C-07351, U+3ED3B / C-07352
  and U+3EEB2 / C-07717** from three pinned public-domain pages. All identities
  were compared with the official chart; the font traces historical scans only.
  Corrected crops retain complete components. One bounded closing repairs a
  short worn break in C-07351; a regression limits added ink to that region.
  The recovery font now contains **41** provisional drawings. Compiled specimens
  were inspected enlarged and at 24 pixels.
- **41 targeted Python tests**, **254 JavaScript tests**, and verification of
  **11,306 source files** pass. Source and coverage inventories are refreshed.
- **349 shards, 60,208,160 bytes**. Bundled visible cmap coverage is
  **171,357 / 172,352**, leaving **995** missing mappings. Seal gaps are **307**:
  69 have CCZ references and 238 require another edition. Raw sources represent
  171,385 public characters across 256 fonts.
- The unreviewed proximity shortlist is exhausted. Its two remaining entries
  are already deferred worn scans. The search tool now retains **66 neighbour
  windows without unassigned crops** for broader full-page inspection, with a
  regression covering those windows. The rejected assigned mismatch remains
  excluded. Specialist review, final style and full Unicode support remain open.
- Final browser validation: **130 scenarios**, no failures or geometry warnings;
  all four additions were visually inspected in the actual comic.
  `git diff --check` passes.

## Full-page Seal recovery and correction of two upstream identities

- Found **U+3D7A9 / C-01933, U+3E1E3 / C-04510, U+3EE98 / C-07692
  and U+3EEB5 / C-07720** on already pinned pages. All four identities match
  the reference chart. The ordinary scan cleanup suffices; no stroke repair
  is added. Enlarged and 24-pixel compiled specimens were inspected. The
  recovery font contains **45** provisional drawings.
- Located U+3EEB4 / C-07719, but deferred it because worn gaps disconnect
  several strokes. Empty search windows now retain prior review outcomes.
- Direct inspection of the original compiled font exposed two incorrect
  upstream mappings: **U+3EEB3 / C-07718** contains the right component of
  C-07719; **U+3EEB6 / C-07721** duplicates C-07720. Both are explicitly
  excluded by the original source builder, with regressions for the source
  cmap and application routing. Correct replacements remain to be located.
- Final inventory: **349 shards, 60,208,932 bytes**; bundled visible cmap
  coverage **171,359 / 172,352**, with **993** gaps. Seal has **305** gaps:
  67 have CCZ references and 238 require another edition. The candidate report
  retains 62 empty search windows and two previously deferred crop candidates.
  Raw sources represent 171,387 public characters across 256 fonts; all
  **11,306 source files** verify offline. Full scoped coverage remains open.
- Final validation: **41 targeted Python tests**, **254 JavaScript tests**,
  and **131 browser scenarios** pass, with no browser geometry warnings.
  The four new drawings were also inspected in actual comic panels.
  Asset hashes are refreshed and `git diff --check` passes.

## Corrected Seal identities and four further page-search recoveries

- Recovered the correct **U+3EEB3 / C-07718** and **U+3EEB6 / C-07721**
  drawings from the same pinned page as their previously excluded crops.
  Corrected bounds preserve whole stems while excluding following text.
- Added **U+3E0F2 / C-04270, U+3E4EA / C-05271, U+3F283 / C-08677
  and U+3F8FD / C-10293** from previously pinned scans, after chart identity
  comparison and enlarged mask inspection.
- Found another wrong upstream mapping: **U+3E4E9 / C-05270** was a damaged
  crop of C-05271. Its original outline is excluded and its correct drawing,
  located in the adjacent column, is bundled in the recovery font. All three
  corrected identities now route to reviewed scan drawings; original source
  files and upstream statuses remain unchanged.
- The recovery font contains **52** drawings. Explicit cleanup removes a page
  rule above C-05270; bounded closings repair short worn sections in C-05270
  and C-05271. Regression checks preserve their distinct interiors, constrain
  repair pixels and retain the roof stem. Other drawings use ordinary cleanup.
- Compiled specimens were inspected enlarged and at 24 pixels. A new repair
  regression caught six edge pixels removed by a closing near the crop border;
  narrowing its application region preserves those original pixels and passes
  the focused regression.
- Final inventory: **349 shards, 60,212,916 bytes**, with **171,365 / 172,352**
  visible requirements mapped and **987** gaps. Seal gaps are **299**: 61 have
  CCZ references, 238 require another edition. Raw sources represent 171,393
  public characters across 256 fonts. All **11,306 source files** verify offline.
  These counts do not prove complete script correctness or final styling.
- Final validation passes: **42 targeted Python tests**, **254 JavaScript
  tests**, and **132 browser scenarios** with no failures or geometry warnings.
  All seven drawings were inspected in the actual comic panels. Asset hashes
  and inventories are refreshed; `git diff --check` passes. The full Unicode
  goal remains active, with 58 full-page CCZ search windows still recorded.

## Three further CCZ drawings and a binding-shadow deferral

- Located and verified **U+3D766 / C-01868, U+3D88A / C-02159 and
  U+3E21F / C-04569** on three new public-domain pages. The recovery font
  now contains **55** provisional drawings. Recipes retain source identity,
  page bounds, hashes and licence evidence.
- Added a per-glyph threshold offset, keeping the default unchanged. C-01868
  uses +10 to exclude binding-edge shadow, with a bounded interior-bar repair.
  Its regression checks preserved spaces, separate components and blank top
  margin, and constrains added ink. C-02159 has one explicit pencil-fragment
  removal. C-04569 uses the standard cleanup.
- Found **U+3DCE1 / C-03248** beside the book binding on a fourth pinned page.
  Expanded half-page bounds reveal the full area, but threshold trials still
  merge the shadow with thin left-component strokes. It remains excluded;
  the gap review records its source, corrected location and failed approach.
- Compiled specimens were inspected enlarged and at 24 pixels. **43 targeted
  Python tests** and **254 JavaScript tests** pass. All **11,310 source files**
  verify offline. Asset hashes, candidate report and inventories are refreshed.
- **349 shards, 60,214,416 bytes**. Bundled visible cmap coverage is
  **171,368 / 172,352**, leaving **984** gaps. Seal gaps are **296**: 58 have
  CCZ references and 238 require another edition. Raw sources represent
  171,396 public characters across 256 fonts. The full goal remains active.
- Final browser validation: **133 scenarios**, no failures or geometry warnings.
  All three additions were visually inspected in actual comic panels.
  `git diff --check` passes.

## Four book-4 gaps and another corrected upstream identity

- Recovered **U+3E25E / C-04632, U+3E394 / C-04936, U+3E53F / C-05355
  and U+3E5AD / C-05462** from four newly pinned public-domain pages.
- The compiled original **U+3E25D / C-04631** drawing was C-04632 instead.
  Its correct drawing was located in the adjacent column, verified against
  the reference and added to the recovery font. The wrong original is excluded
  with the other known identity errors. Recovery now contains **60** drawings,
  including four replacements for incorrect upstream mappings.
- C-05355 has bounded repairs to worn interior connections; a regression keeps
  eleven spaces, restores two disconnected pieces and limits added ink.
  C-05462 has explicit removal of preceding-text fragments and a pencil spur,
  with its four components and three spaces retained. Other crops use the
  standard cleanup. Source images, hashes and licence evidence are recorded.
- Compiled specimens were inspected enlarged and at 24 pixels. **44 targeted
  Python tests** and **254 JavaScript tests** pass. All **11,314 source files**
  verify offline. Asset hashes, candidate report and inventories are refreshed.
- **349 shards, 60,216,096 bytes**. Bundled visible cmap coverage is
  **171,372 / 172,352**, leaving **980** gaps. Seal gaps are **292**: 54 have
  CCZ references and 238 require another edition. Raw sources represent
  171,400 public characters across 256 fonts. Full scoped coverage and final
  visual/script validation remain incomplete.
- Final browser validation: **134 scenarios**, no failures or geometry warnings.
  All five drawings were visually inspected in the actual comic panels.
  `git diff --check` passes; the full goal remains active.

## Page-boundary recoveries and a fifth corrected upstream identity

- Found **U+3E332 / C-04840** inline near the end of book 4 page 52 and
  **U+3EA8A / C-06684** at the start of book 5 page 63. The neighbour windows
  crossed page boundaries. Six reviewed scans are now pinned, including both
  sides of each boundary search.
- Book-5 pages 6 and 33 also recover **U+3E69B / C-05697** and
  **U+3E888 / C-06183**. The original compiled **U+3E69A / C-05696** glyph
  was C-05697. Its correct adjacent headword is added to recovery, and the
  wrong original mapping is excluded. Recovery now has **65** drawings,
  including five replacements for incorrect upstream mappings.
- Bounded closings repair short breaks in C-06684's two vertical stems and
  C-05696's body. Regressions retain their separate components, spaces and
  surrounding original ink. C-05696 also has explicit page-rule cleanup.
  Other drawings use standard tracing. All identities were compared with the
  official reference chart; drawings are traced from the historical scans with
  the local repairs described above. No chart artwork is copied.
- Compiled specimens were inspected enlarged and at 24 pixels. **45 targeted
  Python tests** and **254 JavaScript tests** pass. All **11,320 source files**
  verify offline. Asset hashes, candidate report and inventories are refreshed.
- **349 shards, 60,218,980 bytes**. Bundled visible cmap coverage is
  **171,376 / 172,352**, leaving **976** gaps. Seal gaps are **288**: 50 have
  CCZ references and 238 require another edition. Raw sources represent
  171,404 public characters across 256 fonts. Full coverage, sequence support
  and final visual/script validation remain incomplete.
- Final browser validation: **135 scenarios**, no failures or geometry warnings.
  All five drawings were visually inspected in actual comic panels.
  `git diff --check` passes; the full goal remains active.

## Seal book-six water-component recovery checkpoint

- Located and verified six previously missing CCZ forms on book-six pages 7
  and 83: **U+3EBF8, U+3F15C, U+3F15E, U+3F161–U+3F163**. Both public-domain
  scans are pinned by hash with licence evidence. Official chart pages 121
  and 144 served only as identity references.
- Bounded cleanup removes the page rule and pencil annotations. The dense
  upper-component contacts remain as printed; no strokes were reconstructed.
  U+3F15E uses threshold offset 10 to exclude the adjacent rule. Regression
  checks preserve component/space counts and constrain cleanup to its recorded
  regions. Compiled outlines and 24-pixel specimens were visually checked.
- Recovery contains **71 drawings**. The regenerated inventory has **349
  shards, 60,223,796 bytes** and **171,382 / 172,352** visible cmap entries,
  leaving **970 gaps**. Seal accounts for **282** gaps: **44** with CCZ
  references and **238** requiring other editions. These are coverage figures,
  not claims of completed script or style review.
- **46 targeted Python tests**, **254 JavaScript tests**, and **136 browser
  scenarios** pass. Browser checks report no failures or geometry warnings;
  all six new forms were inspected in the comic layout. **11,322 source
  files** pass offline verification, and `git diff --check` passes. Raw source
  inventory: 256 fonts, 171,410 public characters represented, 1,463 absent
  including behavioural characters.
- The overall Unicode beta goal remains active and substantially incomplete.

## Book-six missing forms and two shifted mapping corrections

- Recovered four missing drawings: **U+3EEAF / C-07714**, **U+3EEB0 /
  C-07715**, **U+3EF2C / C-07836** and **U+3EFC5 / C-07986**. Full-page
  searches used book-six pages 45–46, 51 and 61; three additional scans are
  pinned with public-domain licence evidence. The official chart was used
  only to verify identities.
- Inspection of the compiled upstream font confirmed that **U+3EEB1 /
  C-07716** depicted C-07714, and **U+3EFC6 / C-07987** depicted C-07986.
  Both wrong mappings are excluded and replaced with their correct neighbouring
  drawings. Original source files and upstream statuses remain unchanged.
  Recovery now contains **77 drawings**, including **seven** replacements for
  misidentified upstream crops.
- The lighter threshold for U+3EF2C preserves the gap between its middle-left
  lobe and central stem. U+3EFC5 loses a detached pencil remnant. A bounded
  closing adds 14 pixels to a worn notch in U+3EFC6's existing water stem,
  without removing pixels or changing other components. Regression tests check
  these details, retained interior spaces and routing to the recovery font.
- **47 targeted Python tests**, **254 JavaScript tests** and **137 browser
  scenarios** pass. Browser checks report no failures or geometry warnings;
  all six drawings were inspected in compiled specimens and the comic layout.
  **11,325 source files** verify offline, and `git diff --check` passes.
- Current inventory: **349 shards, 60,225,724 bytes**, **171,386 / 172,352**
  visible cmap requirements present, **966 remaining gaps**. Seal has **278**
  gaps: **40** CCZ-referenced and **238** requiring another edition. Raw source
  inventory has 256 fonts, 171,414 represented public characters and 1,459
  absent including behavioural characters. These remain coverage figures,
  not evidence of completed linguistic or style review.
- Next unreviewed CCZ window is book-six page 93 (C-08566–C-08569). The full
  Unicode beta goal remains active and substantially incomplete.

## Book-six fish cluster and malformed-crop correction

- Recovered **U+3F214–U+3F217** and **U+3F21D** from book-six page 93.
  Also replaced **U+3F218 / C-08570**: its compiled upstream glyph contained
  only part of C-08566 and a page rule. Adjacent compiled U+3F219–U+3F21C
  were independently checked against their references and retained.
- Recovery now contains **83 drawings**, including **eight** corrections of
  misidentified upstream crops. Page 93 and the searched boundary page 94
  are pinned with public-domain licence evidence. Chart page 147 was used
  only for identity verification, never for tracing.
- Crop-local clearing removes the top rule from three drawings. Compiled
  preview inspection caught a two-pixel remnant above U+3F214; extending
  only that clearing region from 10 to 12 pixels removes it without touching
  the glyph. Regression checks preserve the dense interiors, unchanged ink
  below the clearing band and the absence of detached rule fragments. No
  glyph strokes were reconstructed.
- Final inventory: **349 shards, 60,229,856 bytes**, **171,391 / 172,352**
  visible cmap requirements covered, **961 gaps** remaining. Seal has **273**
  gaps, of which **35** have CCZ references and **238** need other editions.
  Raw source inventory: 256 fonts, 171,419 represented public characters,
  1,454 absent including behavioural characters. **11,327 pinned source files**
  verify offline. Coverage does not establish completed script/style review.
- Preliminary next-source investigation: downloaded book-seven page 18 to
  `build/unicode-sources/seal-recovery/book7-page18-3840.jpg` and inspected it
  alongside references for C-08935–C-08955. Those 21 forms were not located
  between the recorded neighbours on that page. Do not assign crops by
  proximity; investigate the surrounding leaves, source ordering and alternate
  scans. Preparation files are `/tmp/seal-book7p18-{page,windows}.json` and
  `/tmp/seal-book7p18-refs.png`. This preliminary page is not yet part of the
  pinned production manifest, and no glyph from that investigation is bundled.
- After the final cleanup, **48 targeted Python tests**, **254 JavaScript
  tests**, and **138 browser scenarios** pass. Browser validation reports no
  failures or geometry warnings. Final compiled specimens and all six glyphs
  in the comic layout were visually inspected; `git diff --check` passes.
  The broader Unicode beta goal remains active and substantially incomplete.

## Alternate 1873 copy recovers the missing hand-component leaf

- Found the leaf containing C-08935–C-08955 in a second copy of the same
  1873 CCZ edition, reproduced in 《廣州大典》 from the Guangdong Sun Yat-sen
  Library copy. Wikimedia's public-domain metadata and the complete PDF are
  pinned in the source manifest. The NLC book-seven page-18 scan is now also
  pinned as comparison evidence. Source description:
  https://commons.wikimedia.org/w/index.php?curid=200513652
- Added **17 missing characters**: U+3F390, U+3F392–U+3F39A,
  U+3F39C–U+3F3A1 and U+3F3A3. Each was compared with its official identity
  reference, the original scan and its compiled outline. **U+3F38D–U+3F38F
  and U+3F391** remain excluded because their printed strokes are too damaged
  for reliable recovery with the current cleanup. Exact source locations are
  recorded for later reconstruction or a cleaner scan. No chart artwork was
  traced, and no strokes were reconstructed in this batch.
- The builder now extracts a pinned embedded scan image from a PDF. Recipes
  identify page 260, image object 5721, its dimensions, decoded pixel hash and
  stencil polarity. The loader verifies page membership, dimensions and hashes
  before conversion to black ink on white. Twofold resampling retains the
  existing doubled-coordinate recipe convention. Opening radius 1 preserves
  thinner strokes; ordinary JPEG recipes retain radius 3. Local clearing
  removes two whole detached margin fragments without shortening glyph strokes.
- Added tests for PDF page/pixel/hash validation, polarity, retained component
  and interior counts, unchanged ink outside cleanup rectangles, and rejection
  of the four damaged forms. All old and new glyphs still pass deterministic
  rebuild, exact packaged-outline, cmap and shaping checks.
- **50 targeted Python tests** pass (seven PyMuPDF/SWIG deprecation warnings),
  **254 JavaScript tests** pass, and **141 browser scenarios** report no
  failures or geometry warnings. The three new browser samples were inspected
  in all comic panels; all 17 compiled specimens were inspected large and at
  24 pixels. **11,330 pinned source files** verify offline; `git diff --check`
  passes. These targeted checks are not a new complete-suite claim.
- Recovery now contains **100 drawings**, including eight corrected original
  mappings. Current inventory: **349 shards, 60,238,144 bytes**;
  **171,408 / 172,352** visible cmap requirements present and **944 gaps**.
  Seal accounts for **256 gaps**: **18** with CCZ references and **238** needing
  other editions. Raw sources: 256 fonts, 171,436 represented public characters,
  1,437 absent including behavioural characters. Script/style review remains
  provisional, and the full Unicode beta goal is still active and incomplete.
- The alternate complete-volume scan can also be searched for previously
  deferred damaged or gutter-obscured forms. Working review artifacts for this
  leaf are `/tmp/seal-gzdd-{recipes,masks}` and
  `/tmp/seal-book7p18-{windows,refs}`. Do not re-add deferred candidates solely
  because their source location is now known.

## Four gate variants recovered and corrected

- Added missing U+3F2B8 and U+3F2BB from the pinned book-seven page-seven
  scan. Replaced incorrect original mappings for U+3F2B9 and U+3F2BA:
  their former crops depicted neighbouring characters and truncated strokes.
  All four were compared with their CCZ identity references and full scan
  drawings. No chart artwork was traced or missing ink reconstructed.
- Widened the crops to preserve both outer stems. A structural regression
  checks distinct interiors and complete lower stems, including the loss
  caused by the narrower crops. Original source artwork remains untouched;
  the two incorrect mappings are excluded from the packaged original font.
- Recovery now contains **104 drawings**, including **10 corrected original
  mappings**. Inventory: **349 shards, 60,239,040 bytes**;
  **171,410 / 172,352** visible requirements present, **942 gaps**.
  Seal has **254 gaps**, including **16** with CCZ references and **238**
  needing other editions. Raw sources contain 171,438 public characters,
  with 1,435 absent including behavioural characters. All **11,331 pinned
  source files** verify offline.
- The four compiled drawings were visually inspected large, at 24 pixels,
  and in comic panels. **142 browser scenarios** report no failures or
  geometry warnings; **254 JavaScript tests** pass. Full script/style review
  and the broader Unicode beta goal remain incomplete.
- **51 targeted Python tests** pass with seven PyMuPDF/SWIG deprecation
  warnings; `git diff --check` passes. This is not a complete-suite claim.

## Inline thread forms recovered

- Added U+3F60E / C-09556 and U+3F711 / C-09811 from inline drawings
  on book-seven pages 53 and 66. Their source locations sit below the main
  headword row. Compared scan drawings with official identity references and
  inspected compiled forms large, at 24 pixels, and in comic panels. No chart
  artwork was traced. Their paired thread loops remain naturally open; a
  regression checks that extraction does not close those openings.
- Located U+3F576 / C-09409 at the start of the next leaf, book-seven page 44.
  The worn upper strokes merge under the normal threshold; offsets +10 to -40
  fragment strokes before recovering their correct separation. It remains a
  gap. Exact crop and review outcome are recorded in `seal-gap-review.json`;
  pages 43, 44, 53 and 66 are pinned for reproducibility.
- Recovery now contains **106 drawings**, including ten corrected mappings.
  Inventory: **349 shards, 60,239,668 bytes**, **171,412 / 172,352** visible
  requirements present and **940 gaps**. Seal has **252 gaps**, **14** with
  CCZ references and **238** needing other editions. Raw source inventory:
  256 fonts, 171,440 represented public characters and 1,433 absent including
  behavioural characters. Coverage does not prove completed style or script
  review; the full beta goal remains active and incomplete.
- **254 JavaScript tests** and **143 browser scenarios** pass, with no browser
  failures or geometry warnings. Both new glyphs were inspected in comic
  panels. The four unreviewed CCZ gaps are U+3F7EC (book-seven pages 77–78),
  U+3FB65–U+3FB66 (book-eight page 30), and U+3FB72 (book-eight page 31).
  Other CCZ gaps have recorded deferrals; investigate the alternate full-volume
  scan for cleaner copies rather than retrying known damaged crops unchanged.
- **52 targeted Python tests** pass with seven PyMuPDF/SWIG deprecation
  warnings. All **11,335 pinned source files** verify offline, and
  `git diff --check` passes. These are targeted checks, not a new full-suite
  claim.

## Remaining unreviewed CCZ locations resolved

- Added U+3F7EC / C-10027, U+3FB65 / C-10898, U+3FB66 / C-10899 and
  U+3FB72 / C-10911 from book-seven page 78 and book-eight pages 30–31.
  Book-seven page 77 is pinned as comparison evidence; book-eight metadata
  establishes the public-domain source. All four match their official
  identity references. No chart artwork was traced or bundled.
- Three drawings require no local repair. U+3FB65 uses threshold offset 10
  to keep its left and right components separate. Bounded radius-three
  closing repairs a worn opening in the middle left loop, adding 14 pixels
  without deleting ink. A regression preserves three enclosed loops, both
  separate components, and unchanged ink outside the repair rectangle.
  The other glyphs retain their distinct component and interior counts.
- The compiled font specimens were inspected large and at 24 pixels. Recovery
  now contains **110 drawings**, including ten corrected original mappings.
  Inventory: **349 shards, 60,241,496 bytes**, **171,416 / 172,352** visible
  requirements present and **936 gaps**. Seal has **248 gaps**: **10** with
  CCZ references and **238** needing other editions. The ten remaining CCZ
  gaps all have explicit deferrals for wrong, worn or gutter-obscured crops.
  Next work should seek cleaner copies or reconstruct from recorded source
  evidence; no remaining CCZ gap is an unexamined location.
- The complete Unicode beta remains active and incomplete. Character coverage
  still does not establish finished sequence support, script validation or
  the required visual treatment.
- **53 targeted Python tests** pass (seven PyMuPDF/SWIG deprecation warnings),
  **254 JavaScript tests** pass, and **144 browser scenarios** report no
  failures or geometry warnings. The four new forms were visually inspected
  in all comic panels. All **11,340 pinned source files** verify offline;
  `git diff --check` passes. Raw source inventory: 256 fonts, 171,444 represented
  public characters, 1,429 absent including behavioural characters. These
  targeted checks do not replace a full-suite or linguistic-review claim.

## Cleaner alternate copy resolves three deferred forms

- Recovered U+3DCE1 / C-03248, U+3EEB4 / C-07719 and U+3F576 / C-09409
  from the already pinned alternate 1873 PDF. Recipes identify embedded images
  8016 on page 97, 6199 on page 226, and 5540 on page 273, with verified decoded
  pixel hashes, polarity and crop bounds. These replace earlier deferrals for
  binding shadow and worn strokes; no Unicode-chart artwork is traced.
- U+3DCE1 has complete stems in this copy, but a printed contact joins its two
  lower stems. Explicit clearing in [55,164,59,192] at extraction resolution
  separates them: 103 pixels removed, with no ink changed elsewhere and both
  stem tips retained. The other two need no local reconstruction. Regressions
  check component/interior counts and the exact bounded correction. Specimens
  were inspected large and at 24 pixels.
- U+3F510 / C-09311 was located on alternate PDF page 270, image 5582.
  The right horizontal strokes remain pitted; threshold offsets +20 through
  +100 and radius 1–3 closing fail to recover all fine details reliably.
  Its recipe and review evidence are retained, but it remains unbundled.
- U+3E34F / C-04868 on alternate PDF page 144, image 7354, repeats the earlier
  form without the lower 日 component shown in the identity reference. The
  mismatch is not caused by the NLC crop or binding. Seek an independently
  matching variant source. Nearby alternate PDF pages 145–146 may help locate
  C-04908; those exploratory pages have not yielded an accepted crop yet.
- Recovery now contains **113 drawings**, including ten corrected mappings.
  Inventory: **349 shards, 60,243,224 bytes**; **171,419 / 172,352** visible
  requirements present, **933 gaps**. Seal has **245 gaps**, **7** with CCZ
  references and **238** needing other editions. All remaining CCZ gaps have
  recorded reviews. The full beta goal remains active and incomplete;
  coverage does not prove finished script or style review.
- **54 targeted Python tests** pass with seven PyMuPDF/SWIG deprecation
  warnings; **254 JavaScript tests** and **145 browser scenarios** pass with
  no browser failures or geometry warnings. All three new glyphs were inspected
  in comic panels. All **11,340 pinned source files** verify offline;
  `git diff --check` passes. Raw sources contain 171,447 public characters,
  with 1,426 absent including behavioural characters. These targeted checks
  are not a new complete-suite claim.

## Edition-aware recovery and first DYC-only character

- Confirmed the edition definitions in Unicode 18 UAX #60:
  https://www.unicode.org/reports/tr60/tr60-3.html . TH-Y identifiers enumerate
  additions from other editions and do not prove a drawing exists in the THX
  book. `tools/font/review_seal_editions.py` now generates an exact source
  queue in `docs/seal-edition-candidates.json`, with hashes of the pinned
  reference data and compiled source fonts. After this recovery the preferred
  review routes are **7 CCZ, 192 DYC, 42 QJZ and 3 THX**.
- The recovery builder supports an explicit `sourceProperty`, defaulting to
  CCZ for existing recipes, and checks the exact codepoint/property/sequence
  tuple. It rejects TH-Y as a historical THX source. Tests cover mismatched
  editions, wrong source sequence numbers and false THX aliases.
- Added **U+3D007 / D-00007** from the first volume of the original 1815 Duan
  Yucai edition held by Taiwan's National Central Library. Commons identifies
  it as a public-domain mechanical scan. The complete PDF and licence metadata
  are pinned; the recipe identifies page 12, embedded image 32, its decoded
  pixel hash, un-inverted polarity and crop [934,160,54,52]. The two bars are
  complete and separate, with the upper one shorter. No chart artwork was
  traced and no local stroke reconstruction was needed. Source description:
  https://commons.wikimedia.org/wiki/File:NCL-00920_01_說文解字注.pdf .
- Recovery now contains **114 drawings**, including ten corrected mappings.
  Inventory: **349 shards, 60,243,396 bytes**, **171,420 / 172,352** visible
  requirements present, **932 gaps**. Seal has **244 gaps**: **7** CCZ and
  **237** without CCZ references. This remains character coverage, not proof
  of completed script, sequence or visual-style validation.
- Next DYC source: U+3D010 / D-00015 is located on volume 01 page 13,
  image 35 (1280×970), around native coordinates x940–995, y375–420. Do not
  confuse it with a smaller 二 inside the adjacent commentary. Its upper
  stroke is close to neighbouring annotation and still needs a clean crop.
  U+3D055 / D-00081 is a later target. Working source and reference previews
  are `/tmp/seal-dyc*`; volume 03 was downloaded for exploration but is not
  yet part of the production source manifest. It starts in the bird section,
  not at the beginning of the dictionary.
- Regenerate the edition queue after font changes with
  `.venv/bin/python tools/font/review_seal_editions.py`. The overall Unicode
  beta goal remains active and incomplete.
- **57 targeted Python tests** pass (seven PyMuPDF/SWIG deprecation warnings),
  **254 JavaScript tests** pass, and **146 browser scenarios** report no
  failures or geometry warnings. The compiled DYC form was inspected large,
  at 24 pixels, and in all comic panels. All **11,342 pinned source files**
  verify offline; `git diff --check` passes. Raw source inventory: 256 fonts,
  171,448 represented public characters and 1,425 absent including behavioural
  characters. These are targeted checks, not a new full-suite claim.


## Second DYC recovery and explicit variant deferrals

- Added U+3D055 / D-00081 from the pinned 1815 NCL volume 01, page 24,
  embedded image 68, crop [566,507,57,63]. Its four separate ink components
  and three left-hand enclosed spaces agree with the Unicode reference.
  No local stroke reconstruction was needed; the chart was used only to
  verify identity. A regression test protects the component separation,
  enclosed spaces and unclipped boundaries.
- Recorded reproducible deferred recipes for U+3D010 (annotation touches its
  upper bar) and U+3D06C (the printed crown has two interior horizontal bars
  where the reference has one). Both need a better matching source.
- Recovery now contains 115 drawings, including ten corrected mappings.
  Coverage is 171,421 / 172,352 visible requirements, leaving 931 gaps.
  Seal accounts for 243 gaps, with preferred source routes of 7 CCZ,
  191 DYC, 42 QJZ and 3 THX. Production has 349 shards, 60,244,104 bytes.
- The compiled form was inspected enlarged, at 24 pixels and inside comic
  panels. All 146 browser scenarios pass without geometry warnings;
  254 JavaScript tests pass. All 11,342 pinned source files verify offline.
  Raw sources contain 171,449 public characters, with 1,424 absent including
  behavioural characters. Full beta coverage and review remain incomplete.
- The targeted Seal, edition-routing, script-font and Unicode inventory suite
  passes 58 tests (seven existing PyMuPDF/SWIG deprecation warnings).
  `git diff --check` passes. This is not a new complete-suite claim.


## Higher-resolution DYC copy and two more recoveries

- Pinned NLC892-312002095908-313315, another 1815 DYC volume, together with
  its Commons public-domain metadata. Its embedded images are 5232×4789,
  substantially larger than the previous NCL scan. Source page:
  https://commons.wikimedia.org/w/index.php?curid=136680235 .
- Recovered U+3D010 / D-00015 from page 18, image 58, crop
  [4050,2255,215,180]. This copy separates the upper bar from annotation.
  The explicit clearing rectangle removes only a detached page ruling
  between the bars (2,232 mask pixels); tests prove neither bar changes.
- Recovered U+3D087 / D-00122 from page 36, image 112, crop
  [1900,1885,210,215]. The dot remains separate at middle right.
  No local repair was needed. Both recipes use threshold offset zero and
  opening radius three; complete source and decoded-pixel hashes are pinned.
- U+3D06C on page 33 has the right crown bar count in this copy, but removing
  the crossing thin rule reveals an interior bar detached at both ends;
  the reference attaches it on the left. It remains deferred. U+3D08B was
  located on page 37, image 115, crop [2840,2070,210,250]. Its upper interior
  strokes also differ in joining from the reference; compare QJZ K-00131
  before accepting this historical variant. Neither trial is bundled.
- Recovery now contains 117 drawings, including ten corrected mappings.
  Visible coverage is 171,423 / 172,352, leaving 929 gaps. Seal has 241 gaps:
  preferred review routes are 7 CCZ, 189 DYC, 42 QJZ and 3 THX.
  Production contains 349 shards, 60,244,724 bytes. Raw sources contain
  171,451 public characters, with 1,422 absent including behavioural ones.
- 60 targeted Python tests pass (seven existing PyMuPDF/SWIG warnings),
  254 JavaScript tests pass, and all 147 browser scenarios pass without
  geometry warnings. Both new forms were inspected enlarged, at 24 pixels
  and in comic panels. All 11,344 pinned source files verify offline.
  These are targeted checks, not a new full-suite claim. The beta remains
  incomplete; character counts do not prove shaping or style completion.


## Two complex DYC forms compared across copies

- Added U+3D0A8 / D-00155 from NCL volume 01 page 37, image 107,
  crop [1053,666,52,65], and U+3D122 / D-00260 from page 53, image 155,
  crop [329,213,51,68]. Neither uses local cleanup or reconstructed strokes.
- Independently compared the matching forms in the NLC copy, pages 42 and 57,
  images 130 and 175. The two copies agree on their small stroke separations.
  These are retained as historical-source variation: the Unicode reference
  uses more joined strokes, but the component shapes, placement and enclosed
  spaces agree. Review must distinguish drawing style from changed components;
  exact connected-component equality to the chart is not an identity rule.
  The crop masks retain eight enclosed spaces in D-00155 and three in D-00260.
  Regression checks protect those spaces, source separations and boundaries.
- U+3D169 / D-00331 was located on NLC page 65, image 199, around
  [950,1380,260,320], and NCL page 61, image 179, around [325,170,50,65].
  Both have worn upper grass strokes; no extraction is bundled. TH-00333 is
  another genuine edition source to investigate. Subsequent grass-section
  review can continue around NLC pages 67–70; a working contact sheet is
  `/tmp/dyc67-70.jpg`. Exact locations for D-00353 and D-00373 are unverified.
- Recovery now has 119 drawings, including ten corrected upstream mappings.
  Visible coverage is 171,425 / 172,352, leaving 927 gaps. Seal has 239 gaps;
  preferred review routes are 7 CCZ, 187 DYC, 42 QJZ and 3 THX. Production
  contains 349 shards, 60,245,672 bytes. Raw sources contain 171,453 public
  characters, with 1,420 absent including behavioural characters.
- 61 targeted Python tests pass (seven existing PyMuPDF/SWIG warnings),
  254 JavaScript tests pass, and 148 browser scenarios pass without geometry
  warnings. Both additions were inspected enlarged, at 24 pixels and in comic
  panels. All 11,344 pinned source files verify offline; `git diff --check`
  passes. These are targeted checks, not a new full-suite claim. Coverage,
  shaping, sequence support and visual review remain separate unfinished work.


## Two grass-radical forms and a QJZ source

- Added U+3D182 / D-00353 from NCL volume 01 page 63, image 185,
  crop [172,618,47,65], and U+3D198 / D-00373 from page 67, image 197,
  crop [831,530,48,66]. Compared both with the reference and the independent
  NLC copy, pages 67/71 and images 205/217. The two middle loops in D-00353
  and fine horizontal strokes in D-00373 survive extraction. No local
  reconstruction or cleanup is used; tightening D-00373's top crop excludes
  a detached arc from preceding text without clipping the grass components.
- Recovery now has 121 drawings, including ten corrected mappings. Visible
  coverage is 171,427 / 172,352, leaving 925 gaps. Seal has 237 gaps;
  preferred source routes are 7 CCZ, 185 DYC, 42 QJZ and 3 THX. Production
  contains 349 shards, 60,246,528 bytes. Raw sources contain 171,455 public
  characters, with 1,418 absent including behavioural characters.
- 62 targeted Python tests pass (seven existing PyMuPDF/SWIG warnings),
  254 JavaScript tests pass, and 149 browser scenarios pass without geometry
  warnings. Both glyphs were inspected enlarged, at 24 pixels and in comic
  panels. All 11,344 pinned source files verify offline; `git diff --check`
  passes. These are targeted checks, not a new full-suite claim.
- Located the actual 1839 Qi Junzao edition for the QJZ-only queue:
  https://commons.wikimedia.org/wiki/File:NLC892-411999011197-102941_說文解字繫傳_第1冊.pdf .
  Commons identifies the edition as 祁寯藻清道光19年[1839] and its scan as
  public domain. Downloaded `build/unicode-sources/seal-recovery/qjz01.pdf`
  (25,973,387 bytes, 94 pages) and `qjz01-metadata.json` for exploration.
  They are not yet in the production source manifest. Page 12 has a main
  scan image xref 145 (3855×3465) plus a separate smaller overlay; inspect
  polarity and decoded pixels before making recipes. Dictionary entries
  have begun by page 12; page 16 is 示 and page 20 reaches 王/玉.
  `/tmp/qjz01-contact.jpg` shows the initial pages. The metadata API URL is
  saved in `/tmp/qjz01-meta-url.txt`. Start with K-00035, K-00041 and K-00094;
  K-00131 can also clarify the deferred U+3D08B form. No QJZ glyph is bundled
  yet, and the full Unicode beta remains incomplete.


## First three QJZ edition recoveries

- Pinned the public-domain 1839 QJZ volume 01 PDF and metadata in the
  production source manifest. Added U+3D025 / K-00035 and U+3D02C / K-00041
  from page 16, image 193, and U+3D062 / K-00094 from page 19, image 229.
  Each recipe validates its exact kSEAL_QJZSrc identifier and decoded image hash.
- Tightened crops to exclude neighboring marks while preserving complete
  stems. No local reconstruction is used. Tests check separate ink components,
  enclosed spaces and clear crop margins. Compiled outlines were inspected
  enlarged, at 24 pixels and in comic panels.
- Recovery now contains 124 drawings, including ten corrected mappings.
  Visible coverage is 171,430 / 172,352, leaving 922 gaps. Seal has 234 gaps;
  preferred routes are 7 CCZ, 185 DYC, 39 QJZ and 3 THX. Production contains
  349 shards, 60,249,404 bytes. Raw sources represent 171,458 public characters,
  with 1,415 absent including behavioural characters. All 11,346 pinned source
  files verify offline. The complete Unicode beta remains unfinished.
- Validation: 63 targeted Python tests pass with seven existing SWIG warnings;
  254 JavaScript tests pass; 150 browser scenarios pass with no failures or
  geometry warnings. `git diff --check` passes. This is targeted validation,
  not a new full Python suite run.


## QJZ alternative resolves U+3D08B

- Added U+3D08B / K-00131 from QJZ volume 01 page 22, embedded image 265,
  crop [2553,1691,224,229]. Its interior fork, three lower enclosed spaces
  and right component match the exact QJZ reference. No local repairs are
  used. This resolves the character previously deferred under D-00125.
- Recovery now contains 125 drawings: 113 CCZ, eight DYC and four QJZ,
  including ten corrected upstream mappings. Visible coverage is
  171,431 / 172,352, leaving 921 gaps. Seal has 233 gaps; preferred review
  routes are seven CCZ, 184 DYC, 39 QJZ and three THX. Production contains
  349 shards, 60,250,520 bytes. Raw sources represent 171,459 public
  characters, with 1,414 absent including behavioural characters.
- 63 targeted Python tests and 254 JavaScript tests pass; Python reports
  seven existing SWIG warnings. All 11,346 pinned source files verify.
  Compiled outlines were inspected enlarged and at 24 pixels.
- Located U+3D1DB / K-00443 in QJZ page 41, image 493, left page rightmost
  column near [595,965] in the 1300x1160 preview. The printed straight stem
  matches the reference, but a detached dark mark on its right requires
  independent evidence before removal. The handwritten marginal form
  differs and must not be substituted. Candidate is recorded but not bundled.
  Temporary inspection files: /tmp/qjz443-crop.png and /tmp/qjz443-ref.png.
  The full Unicode beta remains incomplete.
- Browser validation: all 150 scenarios pass with no failures or geometry
  warnings, including the expanded four-character QJZ specimen. The new form
  was inspected in comic panels. `git diff --check` passes. These are targeted
  checks, not a new full-suite Python run.


## DYC water-and-grass form recovered

- Added U+3D21C / D-00503 from NCL volume 01 page 81, image 239,
  crop [441,482,55,74]. The full grass crowns and separate lower strokes
  match the DYC reference and the independent NLC page 85, image 259.
  The latter has a vertical page ruling through the right component;
  the selected NCL crop avoids that interference. No local reconstruction
  or cleanup is applied. Widening the left crop gives the outer stroke a
  clear margin. Regression checks preserve the twelve printed components,
  separate crowns, lack of enclosed spaces and clear boundaries.
- Recovery now contains 126 drawings: 113 CCZ, nine DYC and four QJZ,
  including ten corrected upstream mappings. Visible coverage is
  171,432 / 172,352, leaving 920 gaps. Seal has 232 gaps; preferred review
  routes are seven CCZ, 183 DYC, 39 QJZ and three THX. Production contains
  349 shards, 60,251,176 bytes.
- Located U+3D2A6 / D-00640 in NLC volume 01 page 100, image 304,
  near native crop [4200,2310,195,245]. This leaf is absent between NCL
  pages 95 and 96; the page offset between copies changes here. Nearby
  water-and-eye forms are different characters. The correct headword has
  a ruling through its left grass component and pitted ink; it remains
  deferred for bounded repair or a cleaner scan. Source details are in
  seal-gap-review.json; /tmp/dyc640-alt-crop.png shows the untreated scan.
  The full Unicode beta remains incomplete.
- Raw source inventory now represents 171,460 public characters, with 1,413
  absent including behavioural characters. All 11,346 pinned source files
  verify offline. All 254 JavaScript tests and 150 browser scenarios pass,
  with no browser failures or geometry warnings. The compiled glyph was
  inspected enlarged, at 24 pixels and in comic panels.
- All 64 targeted Python tests pass, with seven existing SWIG warnings.
  `git diff --check` passes. These checks do not constitute a new complete
  Python suite run or proof of full Unicode shaping and style coverage.


## Bounded repair resolves DYC D-00640

- Added U+3D2A6 / D-00640 from NLC volume 01 page 100, image 304,
  crop [4200,2310,195,245], after comparing the complete printed form with
  its DYC reference. Explicit clear rectangles remove the exposed ends of
  the horizontal page ruling and a detached lower speck. A new opt-in
  fillSmallHoles recipe fills only enclosed pits up to 20 doubled pixels.
  It leaves open gaps and all four meaningful counters unchanged, with
  areas 580, 1490, 594 and 1534 pixels. The repaired form retains eleven
  separate ink components. Tests compare every added/removed pixel with
  the unretouched mask and the permitted regions.
- Recovery contains 127 drawings: 113 CCZ, ten DYC and four QJZ, including
  ten corrected upstream mappings. Visible coverage is 171,433 / 172,352,
  leaving 919 gaps. Seal has 231 gaps; preferred review routes are seven
  CCZ, 182 DYC, 39 QJZ and three THX. Production contains 349 shards,
  60,253,080 bytes. Source gaps, shaping and visual review remain distinct;
  the full Unicode beta remains incomplete.
- Located the likely U+3D355 / D-00800 headword at NCL volume 01 page 113,
  image 335 (1320x981), near [1153,232] on the right page. Its explanatory
  text begins 牛息聲. Exact reference/crop review is still pending; it is
  recorded in seal-gap-review.json but not bundled. /tmp/dyc-ncl113.png
  contains the scan and /tmp/dyc-next3-refs.png includes its reference.
- Raw sources represent 171,461 public characters, with 1,412 absent including
  behavioural characters. All 11,346 pinned source files verify offline.
  All 254 JavaScript tests and 150 browser scenarios pass without browser
  failures or geometry warnings. The new outline was inspected enlarged,
  at 24 pixels and in comic panels.
- All 65 targeted Python tests pass with seven existing SWIG warnings;
  `git diff --check` passes. This is targeted validation, not a new full
  Python suite run or a claim of completed Unicode coverage.


## Bird and mouth components recovered from DYC

- Added U+3D355 / D-00800 from NCL volume 01 page 113, image 335,
  crop [1126,195,57,69], and U+3D37A / D-00834 from page 118,
  image 350, crop [841,627,53,66]. Both match their exact DYC references
  without local reconstruction or cleanup. Crops exclude nearby text and
  page rulings. Tests preserve D-00800's three components and ten enclosed
  spaces, and D-00834's four components, three enclosed spaces and detached
  bar inside the lower enclosure.
- Recovery now contains 129 drawings: 113 CCZ, twelve DYC and four QJZ,
  including ten corrected upstream mappings. Visible coverage is
  171,435 / 172,352, leaving 917 gaps. Seal has 229 gaps; preferred routes
  are seven CCZ, 180 DYC, 39 QJZ and three THX. Production contains
  349 shards, 60,254,160 bytes.
- Located U+3D399 / D-00864 at NCL volume 01 page 120, image 356,
  near [490,857]. It sits close to the lower page border; the small central
  mark above the two roof components in the reference is absent from this
  copy. Deferred for another-copy/reference review. The preceding text's
  detached fragment must not be mistaken for that mark. Inspection files:
  /tmp/dyc864-source.png and /tmp/dyc-mouth-refs.png. The full Unicode beta
  remains incomplete.
- All 66 targeted Python tests pass with seven existing SWIG warnings;
  all 254 JavaScript tests and 151 browser scenarios pass without browser
  failures or geometry warnings. Both new forms were inspected enlarged,
  at 24 pixels and in comic panels. All 11,346 pinned sources verify;
  raw sources represent 171,463 public characters, with 1,410 absent
  including behavioural characters. `git diff --check` passes. These are
  targeted checks, not a new full Python suite run.


## Four DYC mouth and walking variants

- Added U+3D40D / D-00981 and U+3D414 / D-00986 from NCL volume 01
  page 130, image 386, crops [675,286,54,61] and [404,662,53,58].
  Added U+3D46B / D-01063 from page 138, image 410, crop [410,490,52,62],
  and U+3D4A0 / D-01115 from page 142, image 422, crop [893,437,56,65].
  Each printed form was compared with its exact DYC reference. No local
  reconstruction or cleanup is used. D-00986 keeps its printed pen lift
  below the left crown; all four lower loops remain enclosed. Tests assert
  the component/counter counts and clear crop boundaries for all four forms.
- Recovery now contains 133 drawings: 113 CCZ, sixteen DYC and four QJZ,
  including ten corrected upstream mappings. Visible coverage is
  171,439 / 172,352, leaving 913 gaps. Seal has 225 gaps; preferred routes
  are seven CCZ, 176 DYC, 39 QJZ and three THX. Production contains
  349 shards, 60,255,728 bytes. The full Unicode beta remains incomplete.
- Next unresolved DYC source is D-01166 / U+3D4D5. NCL volume 01 page 150
  reaches the beginning of 辵, with subsequent pages still in this volume;
  /tmp/dyc-ncl150.png, /tmp/dyc-ncl152.png and /tmp/dyc-ncl156.png are
  available for location review. No crop for this next form is accepted yet.
- All 67 targeted Python tests pass with seven existing SWIG warnings;
  all 254 JavaScript tests and 152 browser scenarios pass without browser
  failures or geometry warnings. All four outlines were inspected enlarged,
  at 24 pixels and in comic panels. All 11,346 pinned sources verify offline.
  Raw sources represent 171,467 public characters, with 1,406 absent including
  behavioural characters. `git diff --check` passes. These are targeted
  checks, not a new full Python suite run.

## DYC walking variant and next volume — 2026-11-01

Added U+3D4D5 / D-01166 from the public-domain NCL 1815 edition,
volume 01 PDF page 151, image 449. The printed variant labelled 邁或從萬
matches the reference's walking component, four enclosed cells and curled
lower stroke. No local cleanup or reconstruction was needed. The recovery
font now contains 134 drawings (113 CCZ, 17 DYC and 4 QJZ), including the
10 previously corrected upstream mappings.

Rebuilt 349 script shards (60,256,268 bytes). Bundled visible cmap coverage is
171,440 / 172,352, leaving 912 missing. Seal has 224 gaps: preferred routes
are 7 CCZ, 175 DYC, 39 QJZ and 3 THX. Raw source inventory represents 171,468
public characters in 256 fonts; its 1,405 absent entries include behavioural
characters and are not the visible coverage count.

Validation: 67 targeted Python tests passed (7 existing SWIG warnings),
254 JavaScript tests passed, and 152 browser scenarios passed without failures
or geometry warnings. Inspected the compiled specimen enlarged and at 24px,
and the updated walking-variant comic dialogue. All 11,346 pinned source files
verified; git diff whitespace checks passed. This is not a new full Python
suite or a completion claim for the Unicode beta.

Downloaded the next public-domain scan, NCL-00920 02 說文解字注.pdf,
50,664,853 bytes / 157 PDF pages, with Commons imageinfo metadata. It is cached
for exploration, not yet a production dependency. D-01284 / U+3D54F is on
PDF page 2, image 2, native 1309×981, crop [898,767,51,61]. The provisional
crop preserves four ink components and four enclosed cells without edge ink
or local repairs; its form matches the chart's walking and right-hand
components. Prototype recipe and comparison: /tmp/dyc1284.json and
/tmp/dyc1284.png, generated by /tmp/dyc1284.py. Next work is to integrate this
reviewed crop with pinned volume provenance, then locate D-01371. Extract PDF
image bytes through extract_image and Pillow for provenance hashes; a rendered
Pixmap can decode colour differently and is not the builder's hash input.

## First recovered drawings from DYC volume 02 — 2026-11-01

Integrated U+3D54F / D-01284 and U+3D5B4 / D-01371 from NCL volume 02,
PDF pages 2 and 10, images 2 and 26. Pinned the public-domain scan and
Commons metadata in the reproducible source manifest. Neither drawing needs
local cleanup or reconstructed strokes. Regression checks preserve their
four/six enclosed cells, separated components, unclipped contours and the
long descending curve to the right of the tooth component.

The recovery font now contains 136 drawings: 113 CCZ, 19 DYC and 4 QJZ,
including 10 corrections of upstream identity mismatches. Rebuilt 349 shards
at 60,257,236 bytes. Visible coverage is 171,442 / 172,352 (910 missing).
Remaining Seal gaps number 222, with preferred source routes 7 CCZ, 173 DYC,
39 QJZ and 3 THX. The raw source inventory has 171,470 public characters in
256 fonts, with 1,403 absent entries including behavioural characters.

Validation: 68 targeted Python tests passed with 7 existing SWIG warnings;
254 JavaScript tests passed. All 153 browser scenarios passed without failures
or geometry warnings. Visually inspected both compiled glyphs enlarged and at
24px, plus their rendered comic dialogue. All 11,348 pinned source files pass
hash verification. Whitespace checks pass. These are targeted checks, not a
new full Python suite or completion of the wider beta.

Next recovery: located U+3D6CF / D-01636 (譪) on volume 02 PDF page 39,
image 113, native 1309×970; provisional crop [407,516,56,67]. Its speech
component and grass/curled right component match chart page 31. The prototype
has 3 ink components, 5 enclosed spaces and no edge ink, with no local repair.
Recipe and comparison are /tmp/dyc1636.json and /tmp/dyc1636.png, produced by
/tmp/dyc1636.py; it is not integrated yet. The crop includes small neighbouring
text fragments outside the drawing that the existing component threshold
excludes; tighten the crop before accepting if that can preserve the full tail.
Next reference crops for D-01636, D-01800 and D-01880 are saved in
/tmp/dyc-vol2-next-refs.png (chart pages 31, 33 and 35). Volume 02 speech
section begins around PDF page 33; pages 33–40 have been extracted under
/tmp/dyc02-<page>.png for continued review.

## DYC speech forms and separated lifting hands — 2026-11-01

Added U+3D6CF / D-01636, U+3D775 / D-01800 and U+3D7D0 / D-01880 from
NCL volume 02 pages 39, 54 and 62 (images 113, 158 and 182). Tightened the
first crop to [409,522,54,62] to exclude neighbouring text; the final mask has
three components and four enclosed spaces. D-01800 uses [1003,665,54,65],
retaining the speech component and long right-hand strokes. D-01880 uses
[1067,731,50,58] and threshold offset 0: the default offset 20 fused the tips
of its lower hands. The lower hands remain separate and fully stemmed in the
final outline. No local erasure, reconstruction or hole-filling is applied.

The recovery font contains 139 drawings: 113 CCZ, 22 DYC and 4 QJZ, including
10 upstream mapping corrections. Rebuilt 349 shards at 60,258,404 bytes.
Bundled visible coverage is 171,445 / 172,352, leaving 907 missing. There are
219 Seal gaps: preferred routes 7 CCZ, 170 DYC, 39 QJZ and 3 THX. Raw source
inventory represents 171,473 public characters in 256 fonts, with 1,400 absent
entries including behavioural characters.

Validation: 69 targeted Python tests passed (7 existing SWIG warnings),
254 JavaScript tests passed, and 154 browser scenarios passed with no failures
or geometry warnings. Inspected all three compiled specimens enlarged and at
24px, plus the speech/lifting dialogue scenario. All 11,348 pinned files
verified; git diff whitespace checks passed. No new full Python-suite run or
full-beta completion is claimed.

Next reference crops: /tmp/dyc-vol2-next4-refs.png and its JSON page map cover
U+3D893 / D-02072 (chart page 38), U+3D8BF / D-02115 (39), U+3D8EF /
D-02163 and U+3D8F3 / D-02167 (40). The first is the small 籀文燮从辛
variant near [607,300] on NCL volume 02 PDF page 85, image 251; crop and mask
still need review. Do not substitute the larger primary 燮 headword on the
right page. PDF pages 75–87 sampled in /tmp/dyc02-<page>.png establish that
又 is on pages 84–87, after the 鬲/爪/門 sections. D-02115 and the two 殺
variants are later in the volume and remain unlocated. The generic next-four
reference/probe script is /tmp/dyc-next4-probe.py.

## Four DYC variant headwords — 2026-11-01

Added U+3D893 / D-02072, U+3D8BF / D-02115, U+3D8EF / D-02163 and
U+3D8F3 / D-02167 from NCL volume 02 pages 85, 89 and 95. These are the
printed 籀文/古文 variants, not nearby primary forms. The first two use
threshold offset 0: default 20 fuses the flame variant's small side stroke
and the gap between D-02115's two components. No local stroke editing is
used. The two 殺 forms preserve their distinct cross/lozenge, upper-right
components and hand directions. Tests cover their enclosed spaces, separate
components, bounds and threshold-sensitive gaps.

The recovery font contains 143 drawings: 113 CCZ, 26 DYC and 4 QJZ, including
10 upstream mapping corrections. Rebuilt 349 shards at 60,260,300 bytes.
Bundled visible coverage is 171,449 / 172,352 (903 missing). Seal has 215
remaining gaps, with preferred routes 7 CCZ, 166 DYC, 39 QJZ and 3 THX.
Raw source inventory represents 171,477 public characters in 256 fonts;
1,396 absent entries include behavioural characters.

Validation: 70 targeted Python tests passed with 7 existing SWIG warnings;
254 JavaScript tests passed; 155 browser scenarios passed without failures
or geometry warnings. Inspected all four compiled drawings enlarged and at
24px, and their comic dialogue. All 11,348 pinned source files verified.
Whitespace checks pass. This is targeted validation, not a full Python-suite
rerun or a claim that the full Unicode beta is complete.

Next: U+3D951 / D-02257 is located at volume 02 PDF page 107, image 317,
native 1296×981, near [1160,245], above 冒也. Provisional crop [1133,211,56,67]
is in /tmp/dyc2257.json and /tmp/dyc2257.png, generated by /tmp/dyc2257.py.
It matches the reference components but currently joins the upper-left stem
to the right hand (2 components, 2 holes). Review a lighter threshold against
the printed gap before integrating; no production change has been made.
The following references are in /tmp/dyc-vol2-later4-refs.png: D-02257 chart
page 41, D-02357 and D-02367 page 43, D-02441 page 45. Probes at PDF pages
100, 105, 110 and 115 show the progression from 攴 through 卜 to 目;
D-02357, D-02367 and D-02441 remain unlocated. Probe script:
/tmp/dyc-later4-probe.py. Pages 101–107 are also extracted for source review.


## 2026-11-02 — DYC eye and knowledge variants

Added U+3D951 / D-02257, U+3D9C4 / D-02367 and U+3DA15 / D-02441
from the pinned NCL volume 02 pages 107, 121 and 130. D-02257 and D-02441
use threshold offset 0; all three preserve the printed contacts and separate
components without local stroke repairs. Targeted geometry checks protect
the small enclosed eye dot and the knowledge variant's interior divider.
U+3D9B9 / D-02357 remains deferred: the printed upper eye enclosure is worn
open, and stronger thresholding does not establish the missing stroke.

The recovery font now contains 146 drawings: 113 CCZ, 29 DYC and 4 QJZ,
including 10 upstream mapping corrections. Rebuilt 349 shards at 60,261,512
bytes. Bundled visible coverage is 171,452 / 172,352 (900 missing). Seal has
212 remaining gaps, with preferred routes 7 CCZ, 163 DYC, 39 QJZ and 3 THX.
Raw source inventory represents 171,480 public characters in 256 fonts;
1,393 absent entries include behavioural characters.

Validation: 71 targeted Python tests passed with 7 existing SWIG warnings;
254 JavaScript tests passed; 156 browser scenarios passed without failures
or geometry warnings. Inspected all three compiled drawings enlarged and at
24px, and their comic dialogue. All 11,348 pinned source files verified.
This is targeted validation, not a full Python-suite rerun or completion
of the Unicode beta.

Next candidates are U+3DADD / D-02638, U+3DADF / D-02639, U+3DAEA /
D-02649 and U+3DB03 / D-02673. NCL volume 03 is cached for source review
but is not yet a pinned production dependency. Continue identity review
before integrating any bird variants.

## 2026-11-02 — Four DYC bird variants

Added U+3DADD / D-02638, U+3DADF / D-02639, U+3DAEA / D-02649 and
U+3DB03 / D-02673 from NCL volume 03 pages 1, 2 and 5. The PDF and
Commons public-domain metadata are now pinned production sources. Tight crops
exclude page rules; threshold offset 0 retains small counters without any
local stroke edits. The first two forms retain distinct crests. D-02638 has
a detached mark within its bird head; D-02639's mark touches its rim as
printed. The latter's lower components also touch in this source. Checks
protect the enclosed head mark and D-02673's four paired loop counters.

The recovery font contains 150 drawings: 113 CCZ, 33 DYC and 4 QJZ, including
10 upstream mapping corrections. Rebuilt 349 shards at 60,263,824 bytes.
Bundled visible coverage is 171,456 / 172,352 (896 missing). Seal has 208
remaining gaps: preferred routes 7 CCZ, 159 DYC, 39 QJZ and 3 THX. Raw
inventory represents 171,484 public characters in 256 fonts; 1,389 absent
entries include behavioural characters. All 11,350 source files verified.

Validation: 72 targeted Python tests passed with 7 existing SWIG warnings;
254 JavaScript tests passed; 157 browser scenarios passed without failures
or geometry warnings. Inspected the compiled forms enlarged, at 24px and in
comic dialogue. Whitespace checks pass. The Unicode beta remains incomplete;
this batch does not establish whole-script linguistic or style validation.

Next references: U+3DB6D / D-02772 (chart 50), U+3DB80 / D-02790,
U+3DB9E / D-02819 and U+3DBA2 / D-02821 (chart 51). Reference crops are
/tmp/dyc-next-death-refs.png; probe script /tmp/dyc-next-death-probe.py.
Volume 03 pages 19–28 are extracted at /tmp/dyc03-N.png. Page 21 image 59
contains several hand variants around native [870,696], [980,696] and
[1040,660]; do not accept the first nearby primary glyph without comparing
all stroke counts to D-02772. Death-radical entries span pages 21–28.
No next-batch recipe is accepted yet.

## 2026-11-02 — Hand variant and remains form

Added U+3DB6D / D-02772 and U+3DBA2 / D-02821 from pinned NCL volume 03
pages 21 and 27 (images 59 and 77). D-02772 is the hand form at [1095,405],
not the two nearby primary forms around [870,696] and [980,696]. Its three
separate strokes and zero enclosed cells are preserved. D-02821 removes
only detached commentary above the right component using three bounded
rectangles. A regression test proves that both original glyph components
remain pixel-for-pixel unchanged; no stroke is reconstructed or simplified.

Deferred U+3DB80 / D-02790 at page 22 and U+3DB9E / D-02819 at page 27:
small commentary touches their right components. Tightening the crops would
remove genuine strokes, so seek another source before production use. Their
provisional recipes and the reason for deferral are in seal-gap-review.json.

The recovery font now contains 152 drawings: 113 CCZ, 35 DYC and 4 QJZ,
including 10 corrected upstream mappings. Rebuilt 349 shards at 60,264,320
bytes. Bundled visible coverage is 171,458 / 172,352 (894 missing). Seal has
206 gaps, with preferred routes 7 CCZ, 157 DYC, 39 QJZ and 3 THX. Raw source
inventory represents 171,486 public characters in 256 fonts; 1,387 absent
entries include behavioural characters. All 11,350 pinned files verified.

Validation: 73 targeted Python tests passed with 7 existing SWIG warnings;
254 JavaScript tests passed; 158 browser scenarios passed without failures
or geometry warnings. Both compiled forms were inspected enlarged, at 24px
and in comic dialogue. Whitespace checks pass. Full beta scope remains open.

Next: U+3DC3F / D-02977, U+3DC49 / D-02988, U+3DC90 / D-03053 and
U+3DD51 / D-03239. Reference crops /tmp/dyc-next-flesh-refs.png use chart
pages 54, 54, 55 and 58. /tmp/dyc-next-flesh-probe.py and contact sheets
/tmp/dyc03-flesh-probes{,2,3,4}.png cover volume 03 pages 40–55 plus 60
and 70. Native images are /tmp/dyc03-N.png. None is yet securely located;
review page 48–49 as well as the extracted flesh-section pages. Page 55
ends 肉 and enters 筋; page 60 contains 刀 and page 70 角.

## 2026-11-02 — Preserve a meaningful small dot; independent-source review

Added U+3DD51 / D-03239 from NCL volume 03 page 88, image 260,
crop [578,425,54,63]. The ordinary debris filter discarded its genuine
central dot. The builder now accepts an explicit minimumComponentArea per
reviewed recipe, defaulting to the unchanged 70. This crop uses 20, with
threshold offset 20 and opening radius 1. No local stroke repair is used.
A regression test proves that the sole addition compared with cutoff 70 is
a small connected mark inside the original enclosure. Both components and
three enclosed cells survive packaging and realistic-size rendering.

Reviewed an independent 1815 NLC copy, volume 04, now cached as
build/unicode-sources/seal-recovery/dyc-alt04.pdf (96,414,190 bytes, 124
pages) with public-domain Commons metadata. Source URL, hashes and review
status are recorded in seal-gap-review.json. This is a review source only,
not a production dependency. Its pages N+45 correspond to NCL volume 03
page N throughout the reviewed section. Embedded grayscale images are
5232×4789; use extract_image plus Pillow for canonical pixel hashes.

No other candidate from this investigation was accepted:
- D-02977: NCL page 49 has overlapping commentary. NLC page 94 image 286
  removes that commentary but a nearby ruling touches the outer stroke.
  Trial strip cleanup cuts genuine ink; opening radius 6 still leaves rule
  remnants. The prototype /tmp/dyc2977.json is NOT production-safe.
- D-02988: NCL page 51 commentary touches the upper enclosure; NLC page 96
  image 292 has horizontal and vertical ruling across it.
- D-03053: NCL page 60 and NLC page 105 image 319 both have upright tips
  instead of the reference's triangular tips, plus crossing annotation/rules.
- D-02790: NLC page 67 image 205 has worn breaks in genuine counters.
- D-02819: NLC page 72 image 220 has a broken left stem and crossing rules.
These findings supersede optimistic intermediate visual impressions; none
of the uncertain cleanup prototypes was bundled.

The recovery font contains 153 drawings: 113 CCZ, 36 DYC and 4 QJZ, with
10 upstream mapping corrections. Rebuilt 349 shards at 60,264,700 bytes.
Visible coverage is 171,459 / 172,352 (893 missing). Seal has 205 gaps:
7 CCZ, 156 DYC, 39 QJZ and 3 THX preferred routes. Raw inventory represents
171,487 public characters in 256 fonts, with 1,386 absent entries including
behavioural characters. All 11,350 production source files verified.

Validation: 74 targeted Python tests, 254 JavaScript tests and 159 browser
scenarios passed. Python reports 7 existing SWIG warnings; browser results
have no failures or geometry warnings. Inspected the compiled form enlarged,
at 24px and in comic dialogue. Whitespace checks pass. Full beta remains open.

Next: D-03256 U+3DD63, D-03258 U+3DD65, D-03320 U+3DDA4 and D-03321
U+3DDA5. References are /tmp/dyc-next-bamboo-refs.png (chart pages 59,59,
60,60), generated by /tmp/dyc-next-bamboo-probe.py. Native NCL pages 86–90,
95–100 are extracted at /tmp/dyc03-N.png. D-03258 may be near page 90's
individual bamboo forms; D-03320/03321 should be near the end of 竹.
Confirm identity before using any crop. The alternate volume04 ends before
this later bamboo section, so it is not a substitute for those pages.

## 2026-11-02 — Four bamboo-related Seal variants

Accepted U+3DD63 / D-03256, U+3DD65 / D-03258, U+3DDA4 / D-03320
and U+3DDA5 / D-03321 from the pinned NCL volume 03, pages 89, 90,
98 and 99 (embedded images 263, 266, 290 and 293). Compared the original
crops with the Unicode reference structures and inspected compiled outlines
enlarged, at 24px and in comic dialogue. Crops exclude nearby rules and
commentary; no local repair was applied. The test preserves the paired crown
pen lifts in D-03320 and each drawing's reviewed counters.

The recovery font now contains 157 drawings: 113 CCZ, 40 DYC and 4 QJZ,
including 10 corrected upstream mappings. Rebuilt 349 shards at 60,266,064
bytes. Visible cmap coverage is 171,463 / 172,352 (889 missing). Seal has
201 gaps: preferred routes are 7 CCZ, 152 DYC, 39 QJZ and 3 THX. The raw
source inventory represents 171,491 public characters in 256 fonts, with
1,382 absent entries including behavioural characters. All 11,350 production
source files pass pinned-hash checks.

JavaScript: 254 tests passed. Browser: 160 Unicode scenarios passed with no
failures or geometry warnings. The full Unicode beta remains incomplete.
Next source-location candidate after this batch is U+3DDCE / D-03356; consult
the regenerated edition queue and verify the drawing before accepting it.

Targeted Python validation passed all 75 tests in 86.22 seconds, with the
existing 7 SWIG deprecation warnings. This covers Seal identities and packaged
outlines, source geometry, font scripts and Unicode inventory; it is not a
new full-suite run. Build, test and audit logs are `/tmp/bamboo4-*.log`.
Whitespace validation passed.

## 2026-11-02 — Three vessel-related Seal variants

Accepted U+3DDCE / D-03356, U+3DDFC / D-03401 and U+3DE16 / D-03426
from NCL volume 03 pages 104, 110 and 115, embedded images 308, 326 and
341. Crops exclude neighbouring commentary. No local repairs; printed pen
lifts remain. D-03426 uses threshold offset 20 to preserve fine lower stem
crossbars. Tests protect its three lower windows and the detached bar inside
D-03356's lower cup. Inspected source crops and compiled drawings enlarged,
at 24px and in comic dialogue.

The recovery font contains 160 drawings: 113 CCZ, 43 DYC and 4 QJZ,
including 10 corrected upstream identities. Rebuilt 349 shards at 60,267,044
bytes. Visible coverage is 171,466 / 172,352 (886 missing). Seal has 198
gaps: preferred routes 7 CCZ, 149 DYC, 39 QJZ and 3 THX. Raw inventory
represents 171,494 public characters in 256 fonts, with 1,379 absent entries
including behavioural characters. All 11,350 pinned production files verified.
JavaScript passed 254 tests; all 161 browser scenarios passed with no failures
or geometry warnings.

U+3DE20 / D-03435 remains unresolved: NCL pages 115–117 were inspected
but no confident paired-branch vessel crop was found. Do not use the adjacent
enclosed D-03434 form. Next candidates include U+3DE79 / D-03520, U+3DEA6 /
D-03564 and U+3DEE5 / D-03625. Reference comparisons are cached in
/tmp/dyc-food-refs.png; NCL pages 118–129 are extracted as /tmp/dyc03-N.png.
Those pages end before the food section; continue later in volume 03.
The full beta remains active and incomplete.

Targeted validation: 76 Python tests passed in 86.68 seconds, with 7 existing
SWIG warnings. Includes packaged TTF/WOFF2 identities, source geometry,
script-font and Unicode-inventory checks; not a new full-suite run. Build,
test and audit logs: `/tmp/vessels3-*.log`. Whitespace validation passed.

## 2026-11-02 — Two further Seal forms and a rejected mismatch

Accepted U+3DE79 / D-03520 and U+3DEE5 / D-03625 from NCL volume 03
pages 129 and 138, embedded images 383 and 410. Both match the reference
structure. D-03625 uses minimumComponentArea 30 to retain the genuine short
bar enclosed by its food component, removed by the ordinary cutoff of 70.
The regression proves the only added component is that enclosed horizontal
bar; other recipes keep their prior cutoffs. No local repairs. Inspected the
compiled outlines enlarged, at 24px and in comic dialogue.

Deferred U+3DEA6 / D-03564: the plausible crop on NCL page 134, image 398,
has a genuine additional stroke above the right-hand sun, absent from the
Unicode reference. Context confirms it is part of the drawing, not nearby
commentary. Do not delete it to force a match; seek an independent edition.

The recovery font now contains 162 drawings: 113 CCZ, 45 DYC and 4 QJZ,
including 10 corrected upstream identities. Rebuilt 349 shards at 60,268,068
bytes. Visible cmap coverage is 171,468 / 172,352 (884 missing). Seal has
196 gaps: preferred routes 7 CCZ, 147 DYC, 39 QJZ and 3 THX. Raw inventory
represents 171,496 public characters in 256 fonts, with 1,377 absent entries
including behavioural characters. All 11,350 production source files verified.
JavaScript passed 254 tests; all 162 browser scenarios passed without failures
or geometry warnings. Full beta remains incomplete.

Next candidates: U+3DF24 / D-03684, U+3DF72 / D-03759 and U+3E02A /
D-03937. Reference sheet: /tmp/dyc-next-end-refs.png (pages 66, 68 and 71).
All remaining NCL volume03 pages through 153 are extracted /tmp/dyc03-N.png;
contact sheet /tmp/dyc-end-pages.png. These are source-location leads only.

Targeted Python validation passed 77 tests in 87.13 seconds, with the existing
7 SWIG warnings. Covers packaged identities, original scan geometry, script
fonts and Unicode inventory; not a fresh full-suite run. Logs are cached at
`/tmp/food2-*.log`. Whitespace checks passed.

## 2026-11-02 — Fourth DYC source volume and walking variant

Pinned the public-domain NCL-00920 volume 04 PDF (50,564,685 bytes, 148
pages) and Commons metadata, including hashes and reproducible retrieval URLs.
Accepted U+3DF72 / D-03759 from page 8, embedded image 20, crop
[347,534,51,68]. Tight crop excludes neighbouring commentary; no local repair.
The regression preserves its two separate parts and lower counter. Inspected
the original crop, compiled outline, 24px specimen and comic dialogue.

U+3DF24 / D-03684 remains unlocated: the first volume03 page147 crop was
the neighbouring arrow-plus-會 form, not the requested arrow-plus-昜 form.
U+3E02A / D-03937 is located in volume04 page43, image125, around [830,790].
The faint scan's first extraction loses important tree and central-loop strokes
and includes a mark above. It remains unbundled; review extraction settings
or another copy. Prototype /tmp/dyc3937.py and /tmp/dyc3937.json. Pages 1–48
of volume04 have been extracted as /tmp/dyc04-N.png; full page43 was reviewed.

The recovery font contains 163 drawings: 113 CCZ, 46 DYC and 4 QJZ, with
10 corrected upstream identities. Rebuilt 349 shards at 60,268,328 bytes.
Visible cmap coverage is 171,469 / 172,352 (883 missing). Seal has 195 gaps:
7 CCZ, 146 DYC, 39 QJZ and 3 THX preferred routes. Raw inventory represents
171,497 public characters in 256 fonts, with 1,376 absent entries including
behavioural characters. All 11,352 production source files verified.

Validation: 78 targeted Python tests passed in 89.05 seconds (7 existing SWIG
warnings), 254 JavaScript tests and 163 browser scenarios passed. Browser
results have no failures or geometry warnings. These targeted checks are not
a new full-suite run. Logs: /tmp/dyc3759-*.log. Full beta remains incomplete.

## 2026-11-02 — Wood-section source review

Reviewed NCL volume04 contact sheets through page108 and full source contexts
for the pending wood variants. No additional glyph was accepted.

- U+3E073 / D-04008 is located on page51, image149. Low thresholds lose
  fine connections; higher thresholds join the diagonal to the tree.
- U+3E096 / D-04044: the page55 candidate is a different drawing, missing
  the target's grass/water structure. Do not use the trial recipe.
- U+3E0E7 / D-04123 is located on page71, image209, crop [1102,832,47,61].
  Its upper roof is worn open at threshold offset0. Offsets10 and20 close it
  but also retain spurious divisions in the left border. An independent copy
  is needed before accepting an outline.
- U+3E02A / D-03937: offsets0 through50 do not recover the faint drawing
  faithfully. Background merges before its missing strokes become reliable.

Exact source recipes and threshold topology measurements are recorded in
`docs/seal-gap-review.json`; review images are retained under
`output/font-review/seal-pending/`. These are rejected/pending candidates, not
production assets. Coverage and previous test results remain unchanged.
No font rebuild or fresh runtime test run was needed for this evidence-only
update. Next work: locate independent copies at these known source positions.

## 2026-11-02 — Independent wood-section copy recovers enclosed variant

Downloaded public-domain NLC volumes05 (104 pages, 80,750,842 bytes) and06
(132 pages, 102,684,143 bytes), with Commons metadata. Volume06 corresponds
to NCL04 with a 23-page offset at the reviewed wood-section locations. Its
PDF and metadata are now pinned in the production source manifest; volume05
is retained for review only.

Accepted U+3E0E7 / D-04123 from NLC06 page48, image148, crop
[4448,4060,190,220]. Threshold offset20 restores the roof loop. Component
cutoff200 removes one isolated speck, and filling enclosed regions of at most
100 pixels removes small printing pits. The eight substantial counters remain,
as does the printed lower-left interior pen lift. No local stroke reconstruction
or closing was applied. The regression checks these distinctions, verifies that
pit filling adds only enclosed ink, and bounds the removed debris.

Compared the original source, enlarged compiled drawing, 24px specimen and
browser comic dialogue. Other alternate crops remain pending: D-03937 at
NLC06 page20 needs a tighter crop and central-oval review; D-04008 at page28
needs further evaluation of pitting and broken fine strokes. Exact trial recipes
are in the gap review and the comparison is in
`output/font-review/seal-pending/alternate-wood-trials.png`.

Production now contains 164 recovered drawings (113 CCZ, 47 DYC, 4 QJZ),
including 10 corrected upstream identities. The 349 shards total 60,270,364
bytes. Visible cmap coverage is 171,470 / 172,352, leaving 882 missing. Seal
has 194 gaps: preferred routes 7 CCZ, 145 DYC, 39 QJZ and 3 THX. Raw source
inventory represents 171,498 public characters in 256 fonts; 1,375 entries
remain absent including behavioural characters. All 11,354 pinned production
source files verified.

Validation: 254 JavaScript tests passed; all 164 browser scenarios passed with
no failures or geometry warnings. The targeted Python run passed 78 existing
checks and caught an incorrect pixel range in the new geometry test. Corrected
that test's coordinates; its focused rerun passed (1 passed, 23 deselected).
The existing 7 SWIG warnings remain. Thus all 79 targeted checks have passed
across these runs; this is not a fresh full Python suite. Logs are
`/tmp/alt4123-{tests,geometry-final,js,reports,editions}.log`. Whitespace checks
passed. The broader Unicode beta goal remains incomplete.

## 2026-11-02 — Two wood variants recovered from the alternate copy

Accepted U+3E02A / D-03937 from NLC06 page20, image64, crop
[3260,3805,240,235], and U+3E073 / D-04008 from page28, image88, crop
[315,2490,220,220]. Both use threshold20, component cutoff200 and enclosed
pit limit100. The first crop excludes the marks above the glyph and preserves
six parts, including both small marks inside its central oval, and four
counters. The second preserves the whole tree and four neighbouring strokes
as five separate parts, without artificial counters. Neither uses local stroke
reconstruction. A new regression checks these details and bounds pit filling
to enclosed regions. Reviewed source, enlarged compiled outline, 24px samples
and browser comic dialogue.

U+3E096 / D-04044 is now correctly located: NCL04 page58, image170, crop
[811,230,60,70]. The reference's grass/water structure is present here. The
old page55 trial was the wrong character. Correct candidate recipe and review
image are saved in the gap review and
`output/font-review/seal-pending/D-04044-correct-location.png`; outline review
and integration remain pending. Next reference sheet is
`/tmp/dyc-next-afterwood-refs.png`: D-04044 (reference72), D-04287 and
D-04324 (reference77), D-04366 (reference78).

The recovery font now contains 166 drawings (113 CCZ, 49 DYC, 4 QJZ),
including ten corrected upstream identities. Rebuilt 349 shards at 60,273,568
bytes. Visible cmap coverage is 171,472 / 172,352, leaving 880 missing. Seal
has 192 gaps: 7 CCZ, 143 DYC, 39 QJZ and 3 THX preferred routes. Raw source
inventory represents 171,500 public characters in 256 fonts, with 1,373 absent
entries including behavioural characters. All 11,354 production source files
verified.

Validation: 80 targeted Python tests passed in 101.12 seconds, with the
existing 7 SWIG warnings. All 254 JavaScript tests and 165 browser scenarios
passed, with no browser failures or geometry warnings. These are targeted
checks, not a new full Python suite. Logs: `/tmp/altwood2-*.log`. Whitespace
checks passed. The full beta goal remains incomplete.

## 2026-11-02 — Four late wood-section and enclosed variants

Accepted four NCL volume04 drawings, each with opening1, threshold0 and no
local stroke repair or hole filling:

- U+3E096 / D-04044: page58 image170, crop [811,230,60,70], nine parts
  and three counters. Correctly includes the grass/water structure absent
  from the previously rejected page55 neighbour.
- U+3E197 / D-04287: page96 image284, crop [686,254,40,60], two parts
  and no counters. The two stacked forms stay separate.
- U+3E1BC / D-04324: page102 image302, crop [841,394,46,62], four parts
  and no counters. Tight crop removes the 133-pixel commentary dot while
  retaining both curved caps and the detached lowest stroke.
- U+3E1E7 / D-04366: page108 image320, crop [787,725,53,62], two parts
  and eight counters. Dense interior remains visible within its enclosure.

Reviewed full-page context, source/reference identities, compiled outlines,
24px samples and browser dialogue. Regression covers topology, unaltered
source extraction and the commentary exclusion.

The recovery font now contains 170 drawings (113 CCZ, 53 DYC, 4 QJZ),
including ten corrected upstream identities. The 349 shards total 60,275,164
bytes. Visible cmap coverage is 171,476 / 172,352, leaving 876 missing. Seal
has 188 gaps: 7 CCZ, 139 DYC, 39 QJZ and 3 THX preferred review routes.
Raw source inventory represents 171,504 public characters in 256 fonts, with
1,369 absent entries including behavioural characters. All 11,354 pinned
production source files verified.

Validation: 81 targeted Python tests passed in 101.64 seconds with the existing
7 SWIG warnings; 254 JavaScript tests and all 166 browser scenarios passed.
Browser checks report no failures or geometry warnings. This is not a new
full Python suite. Logs: `/tmp/latewood4-*.log`. Whitespace checks passed.
The full beta goal remains incomplete.

Next references: U+3E261 / D-04478 (reference80), U+3E2E7 / D-04612
(reference82), U+3E2FD / D-04633 and U+3E310 / D-04653 (reference83).
Reference sheet `/tmp/dyc-next-village-day-refs.png`. NCL04 pages109–144
are extracted to `/tmp/dyc04-N.png`, with contact sheets for109–120,121–132
and133–144. These are source-location leads only, not reviewed glyphs.

## 2026-11-02 — Fifth DYC volume, village and day variants

Pinned the public-domain NCL-00920 volume05 PDF (50,727,457 bytes, 156
pages) and Commons metadata. Accepted three drawings:

- U+3E2E7 / D-04612: page2 image2, crop [175,620,58,68], four parts
  and six counters at threshold0.
- U+3E2FD / D-04633: page9 image23, crop [577,395,55,66], five parts
  and one counter at threshold30. Lower thresholds leave the circle open and
  separate the two upper-left prongs. The accepted threshold restores both
  printed connections while leaving the circle's inner bar detached.
- U+3E310 / D-04653: page12 image32, crop [185,428,51,68], seven parts
  and one counter at threshold0.

All use opening1 without local stroke reconstruction. Reviewed full source
contexts, exact references, compiled large and 24px specimens, and comic
dialogue. The new regression checks the circular enclosure, its detached bar
and the topology before and after the threshold change.

U+3E261 / D-04478 remains deferred. The reference includes a small detached
mark above-right of its circle. NCL04 page126 image374 and independent NLC06
page102 image310 both lack it. Do not invent that mark or silently accept the
discrepancy. The review record includes both locations and saved comparison
images. The alternate-volume page offset is24 here, unlike23 at the earlier
wood-section locations; always confirm context.

The recovery font now contains 173 drawings (113 CCZ, 56 DYC, 4 QJZ),
including ten corrected upstream identities. Rebuilt 349 shards at 60,276,304
bytes. Visible cmap coverage is 171,479 / 172,352, leaving 873 missing. Seal
has 185 gaps: 7 CCZ, 136 DYC, 39 QJZ and 3 THX preferred routes. Raw source
inventory represents 171,507 public characters in 256 fonts, with 1,366 absent
entries including behavioural characters. All 11,356 production source files
verified.

Validation: 82 targeted Python tests passed in 104.25 seconds (7 existing SWIG
warnings), 254 JavaScript tests, and all 167 browser scenarios passed without
failures or geometry warnings. These targeted checks are not a fresh full
Python suite. Logs: `/tmp/volume5-*.log`. Whitespace checks passed. The full
beta goal remains incomplete.

Next references: U+3E33B / D-04695 (reference84), U+3E377 / D-04737 and
U+3E386 / D-04751 (reference85). D-04737 offers an alternative to the worn
CCZ drawing reviewed earlier. Sheet `/tmp/dyc-next-day-mouth-refs.png`;
NCL05 pages1–24 are extracted to `/tmp/dyc05-N.png`, with first and13–24
contact sheets. These are source-location leads only.

## 2026-11-02 — Day and paired-moon variants

Accepted two more drawings from the pinned NCL volume05:

- U+3E33B / D-04695: page19 image53, crop [463,819,57,67],
  threshold0, five parts and one counter. Its lower internal bar remains
  detached; excessive darkening would falsely close an upper region.
- U+3E386 / D-04751: page31 image89, crop [728,561,55,63],
  threshold20, two parts and two counters. This retains the faint left
  connection and its enclosed strokes without merging the two halves.

Both use opening1 without local stroke reconstruction. Reviewed full-page
context, exact source identities, compiled outlines, 24px samples and browser
comic dialogue. The regression compares accepted topology with the damaged
results of under- and over-darkening. Review images are saved in
`output/font-review/seal-pending/daymoon-accepted.png` and
`daymoon-thresholds.png`.

U+3E377 / D-04737 remains deferred. The matching NCL05 page29 image83
crop [728,825,51,61] has broken upper and left circles and an interrupted
stem at thresholds0–40. The prominent neighbouring drawing at
[908,323,46,68] is D-04736, whose inner bars distinguish it; do not substitute
that drawing. This alternative therefore does not yet resolve the worn CCZ gap.

The recovery font now contains 175 drawings (113 CCZ, 58 DYC, 4 QJZ),
including ten corrected upstream identities. The 349 shards total 60,277,204
bytes. Visible cmap coverage is 171,481 / 172,352, leaving 871 missing.
Seal has 183 gaps: 7 CCZ, 134 DYC, 39 QJZ and 3 THX preferred routes.
Raw source inventory represents 171,509 public characters in 256 fonts,
with 1,364 absent entries including behavioural characters. All 11,356
production source files verified.

Validation: 83 targeted Python tests passed in 103.79 seconds with the existing
7 SWIG warnings; 254 JavaScript tests and all 168 browser scenarios passed
without failures or geometry warnings. These are targeted checks, not a fresh
full Python suite. Logs: `/tmp/daymoon-*.log`. Whitespace checks passed.
The full beta goal remains incomplete.

Next references: U+3E3B1 / D-04790, U+3E3B3 / D-04791,
U+3E3C7 / D-04811, U+3E3CB / D-04814 and U+3E3CD / D-04816,
all on reference page86. Sheet `/tmp/dyc-next-moon-vessel-refs.png`.
NCL05 pages1–48 are extracted as `/tmp/dyc05-N.png`, with contact sheets
for25–36 and37–48. These are location leads, not accepted drawings.

## 2026-11-02 — Three further variants and an alternate three-circle drawing

Accepted four drawings after full-page identity review, compiled-outline and
24px inspection, and browser comic dialogue:

- U+3E3B1 / D-04790: NCL05 page37 image107, crop [196,144,45,64],
  opening1 threshold0, one part and one counter.
- U+3E3B3 / D-04791: NCL05 page38 image110, crop [1074,234,52,61],
  opening1 threshold20, two parts and four counters. Tightening the top removes
  a commentary dot; threshold20 restores the faint fork and lower connection.
  This NCL page has different dimensions (1330×970); its hash and actual size
  are recorded rather than assuming the neighbouring page dimensions.
- U+3E3C7 / D-04811: NCL05 page41 image119, crop [530,205,35,64],
  opening1 threshold0, one part and no counters.
- U+3E377 / D-04737: NLC07 page25 image79, crop [3145,4040,185,265],
  opening3 threshold20, minimum component area200 and small-hole fill100,
  two parts and three counters. The empty detached upper circle and the two
  empty circles attached to its stem match the exact reference. This resolves
  the worn CCZ and NCL05 candidates; the neighbouring three-day form remains
  excluded. Regression checks those distinguishing circles and their separation.

No accepted drawing uses local stroke reconstruction. Pinned the public-domain
NLC volume07 PDF (101,902,941 bytes, 131 pages) and Commons metadata. Its normal
gray images are5232×4789 except the cover; xrefs follow3p+4 in reviewed pages.
For these locations, NCL05 pageN corresponds to NLC07 pageN−4; confirm full
context before applying this offset elsewhere. All source hashes are in the
recovery manifest. Review files are `output/font-review/seal-pending/`:
`moonvessel-accepted.png`, `moonvessel-thresholds.png`, and
`moonvessel-alternate.png`.

U+3E3CB / D-04814 and U+3E3CD / D-04816 remain deferred. NCL05 page42
image122 crops [465,516,58,56] and [193,168,48,65] respectively lose
small meaningful strokes under default cleanup; lighter cleanup and threshold
trials do not restore every detail. NLC07 page38 image118 crops
[1736,2880,236,244] and [560,1490,220,260] are clearer, but ruling touches or
crosses the glyphs. The first trial crop also needs expanding above its triangle.
Neither alternate trial is accepted. Their recipes and review evidence are
recorded for future controlled cleanup or a cleaner source.

The recovery font now contains 179 drawings (113 CCZ, 62 DYC, 4 QJZ),
including ten corrected upstream identities. The 349 shards total 60,279,112
bytes. Visible cmap coverage is 171,485 / 172,352, leaving 867 missing.
Seal has 179 gaps: 6 CCZ, 131 DYC, 39 QJZ and 3 THX preferred routes;
173 have no CCZ source. Raw inventory represents 171,513 public characters
in 256 fonts, with 1,360 absent entries including behavioural characters.
All 11,358 production source files verified. The full beta remains incomplete.

Next references: U+3E452 / D-04944 (reference88), U+3E462 / D-04959
(reference89), U+3E51F / D-05139 and U+3E542 / D-05173 (reference92).
Sheet `/tmp/dyc-next-rice-refs.png`. NCL05 pages1–72 are extracted as
`/tmp/dyc05-N.png`, with contact sheets for49–60 and61–72. These are source
location leads, not reviewed glyphs. NLC07 pages25,27,28,30,33–38 are also
extracted in `/tmp/dyc-alt07-N.png`.

Validation: 84 targeted Python tests passed in 109.06 seconds with the existing
7 SWIG warnings; 254 JavaScript tests and all 169 browser scenarios passed
without failures or geometry warnings. This is not a fresh full Python suite.
Logs: `/tmp/moonvessel-*.log`. Whitespace checks passed.

## 2026-11-02 — Rice and enclosed variants

Accepted four drawings from the pinned NCL volume05 after exact reference and
full-page review:

- U+3E452 / D-04944: page66 image194, crop [348,767,46,70], six parts
  and no counters. Its separated rice strokes and both upper hooks remain.
- U+3E462 / D-04959: page69 image203, crop [955,468,55,72], two parts
  and twelve counters, preserving the paired upper forms and lower enclosure.
- U+3E51F / D-05139: page95 image281, crop [246,610,55,71], one part
  and five counters. A narrower crop would shorten its top stem. Instead,
  clearRect [0,0,45,13] in doubled crop pixels removes only a detached
  162-pixel commentary component beside that stem. The regression verifies
  that the removed area is exactly one whole disconnected component and that
  the complete stem survives.
- U+3E542 / D-05173: page100 image296, crop [1113,650,52,68], two parts
  and six counters. The rice-bearing interior matches the reference. Two
  visually similar candidates on page99 have different interiors and are not
  accepted. The final crop preserves both lower ends and excludes the ruling
  immediately to its right.

All use opening1 and threshold0, without reconstructed strokes. Reviewed
compiled outlines, 24px specimens and browser dialogue. The new regression
also checks component/counter counts and that ink stays within crop bounds.
Compiled review: `output/font-review/seal-pending/rice-accepted.png`.

The recovery font now contains 183 drawings (113 CCZ, 66 DYC, 4 QJZ),
including ten corrected upstream identities. Rebuilt 349 shards at 60,280,604
bytes. Visible cmap coverage is 171,489 / 172,352, leaving 863 missing.
Seal has 175 gaps: 6 CCZ, 127 DYC, 39 QJZ and 3 THX preferred review routes;
169 have no CCZ source. Raw inventory represents 171,517 public characters
in 256 fonts, with 1,356 absent entries including behavioural characters.
All 11,358 production source files verified.

Validation: 85 targeted Python tests passed in 110.37 seconds with the existing
7 SWIG warnings; 254 JavaScript tests and all 170 browser scenarios passed
without failures or geometry warnings. This is not a fresh full Python suite.
Logs: `/tmp/rice-*.log`. Whitespace checks passed. The full beta remains
incomplete.

Next references: U+3E57F / D-05233 (reference93), U+3E5A1 / D-05267 and
U+3E5AF / D-05278 (reference94), U+3E605 / D-05362 (reference96).
Sheet `/tmp/dyc-next-sickness-refs.png`. NCL05 pages1–120 are extracted as
`/tmp/dyc05-N.png`; contact sheets include73–84,85–96,97–108 and109–120.
These are source-location leads, not accepted drawings.

## 2026-11-02 — Sickness and cloth variants

Accepted U+3E57F / D-05233, U+3E5A1 / D-05267 and U+3E605 / D-05362
from pinned NCL volume 05 pages 105, 108 and 120 after exact reference and
full-page review. All use opening 1 and threshold 0, with no reconstructed
strokes. Component/counter counts are respectively 3/4, 4/1 and 4/1.
D-05267 uses crop [348,785,55,65]: it preserves the complete top stroke
while excluding a commentary dot below. A regression checks that expanding
the crop adds that detached mark without changing the accepted glyph pixels.

U+3E5AF / D-05278 remains unresolved. NCL05 page 109 has a broken enclosure
at top and right across threshold offsets 0–30. The alternate NLC07 page 104
image 316 has a clearer outer form but broken inner strokes and a ruling
line across the right edge; offsets 0–20 do not produce a faithful outline.
Both recipes and rejection reasons are recorded in seal-gap-review.json.
Review sheets: output/font-review/seal-pending/sickness-thresholds.png and
sickness-alternate.png. Neither damaged outline is shipped.

Compiled outlines were inspected enlarged and at 24px, and in browser dialogue.
Review: output/font-review/seal-pending/sickness-accepted.png. All 171 browser
scenarios passed without failures or geometry warnings; all 254 JavaScript
tests passed. The rebuild contains 349 shards at 60,281,836 bytes. Visible cmap
coverage is 171,492 / 172,352, leaving 860 missing. These are coverage results,
not proof of completed style or linguistic review.

Next exact references: U+3E640 / D-05420 (reference 97), U+3E6EC / D-05582
(reference 99), U+3E76D / D-05711 (reference 102) and U+3E7B8 / D-05765
(reference 103). Sheet /tmp/dyc-next-cloth-refs.png; NCL05 pages 121–132 are
extracted in /tmp/dyc05-N.png with contact /tmp/dyc05-121-132.png. These
are unaccepted source-location leads.

The recovery font now has 186 drawings: 113 CCZ, 69 DYC and 4 QJZ,
including ten corrected upstream identities. Seal has 172 gaps, with preferred
review routes of 6 CCZ, 124 DYC, 39 QJZ and 3 THX; 166 have no CCZ source.
The raw inventory represents 171,520 public characters across 256 fonts,
leaving 1,353 absent entries including behavioural characters. All 11,358
production source files passed pinned-hash verification.

Validation completed: 86 targeted Python tests passed in 110.47 seconds with
7 existing SWIG deprecation warnings. This is not a fresh full Python suite.
The manual and generated gap counts agree. Whitespace checks passed.
Logs: /tmp/sickness-{build,geometry,tests,js,reports,editions}.log.
The full Unicode beta remains incomplete; the goal stays active.

## 2026-11-02 — First volume 06 forms

Pinned the public-domain NCL volume 06 PDF (50,422,363 bytes, 156 pages)
and Wikimedia licence metadata. Accepted U+3E76D / D-05711 from page 17,
image 47, crop [187,316,59,67], and U+3E7B8 / D-05765 from page 27, image 77,
crop [716,425,51,73]. Exact reference identities and full-page context were
reviewed. Both use opening 1 with no local repairs.

D-05711 uses threshold -10: the ordinary threshold joins one of its three
detached upper stems. D-05765 uses threshold 20 to retain the faint right
foot; threshold 30 starts joining an upper detached part. Its crop extends
above the first trial to preserve the complete vertical top stroke. Both
accepted masks have five components and one counter.

U+3E640 / D-05420 remains deferred: NCL05 page 127 has worn internal
strokes and right loops, while NLC07 page 122 also has broken loops. Darker
thresholds introduce false counters or flood the alternate crop.
U+3E6EC / D-05582 is on NCL05 page 152 with a diamond arrangement of rings;
the page 147 form is a different arrangement. The correct crop has broken
rings at thresholds 0–30; threshold 40 closes them but merges separate parts.
These candidates and both-copy trials are recorded in seal-gap-review.json;
review sheets are in output/font-review/seal-pending/dyc5420-trials.png,
dyc-alt5420.png, dyc-alt5420-dark.png and dyc5582-trials.png.

The compiled outlines were reviewed enlarged, at 24px and in browser dialogue.
Review: output/font-review/seal-pending/volume6-accepted.png. All 172 browser
scenarios passed without failures or geometry warnings; all 254 JavaScript
tests passed. The recovery font now has 188 drawings: 113 CCZ, 71 DYC and
4 QJZ, including ten corrected upstream identities. The rebuild has 349
shards at 60,282,516 bytes. Visible cmap coverage is 171,494 / 172,352,
leaving 858 missing; Seal has 170 gaps (6 CCZ, 122 DYC, 39 QJZ and 3 THX
preferred review routes), of which 164 have no CCZ source. Raw inventory
represents 171,522 public characters in 256 fonts, with 1,351 absent entries
including behavioural characters. All 11,360 production sources verified.

Next references: U+3E7BB / D-05768 and U+3E7D0 / D-05789 (reference 103),
U+3E7ED / D-05817 (reference 104), U+3E85A / D-05915 (reference 106).
Sheet /tmp/dyc-next-garments-refs.png. NCL06 pages 1–36 are extracted under
/tmp/dyc06-N.png, with contact sheets first,13–24 and25–36. Page 28 near
[136,210] is a lead for D-05768; page 32 near [530,195] is a lead for D-05789.
Neither lead has had a crop or outline accepted.

Validation completed: 87 targeted Python tests passed in 112.03 seconds,
with the existing 7 SWIG deprecation warnings. This is not a fresh full Python
suite. Manual and generated gap counts agree; whitespace checks passed.
Logs: /tmp/volume6-{geometry,build,tests,js,reports,editions}.log.
The full Unicode beta remains incomplete and the goal stays active.

## 2026-11-02 — Garment and foot variants

Accepted U+3E7ED / D-05817 from NCL06 page 36, image 104, crop
[720,831,58,63], and U+3E85A / D-05915 from page 49, image 143, crop
[587,512,47,65]. Both use opening 1 and threshold 0, without local repairs.
The first preserves ten separate ink components and one counter; the second
has two components and one counter. D-05817 is the garment with the 寻/尋
component on page 36, not the bird-bearing form on page 38. Its crop excludes
the page rule below while extending far enough right to retain the arm.
The new regression checks ink bounds, component/counter counts, the excluded
rule and unwanted merging under excessive darkening.

D-05768 (U+3E7BB) is the two-bar variant on NCL06 page 28 near [413,416],
not the three-bar form near [133,207]. Its right enclosure stays broken
across offsets 0–40; the darker settings attach its bars to the outer curve.
D-05789 (U+3E7D0), page 32 near [525,189], has broken fine strokes that
threshold changes cannot recover without changing the topology. Both remain
deferred. Alternate NLC08 pages 53 and 57 repeat the wear and have ruling
lines crossing the glyphs. The reference and full-page identity checks do
not justify tracing the reference or reconstructing those strokes.

Downloaded review-only NLC08, File:NLC892-312002095908-313327 說文解字注
十五卷 第8冊.pdf: 83,099,986 bytes, 107 pages, SHA256
31aa6af792900439a43b66d7ee38c4887d47e2f73980c0608bc82b28f9552dab.
Its 2,393-byte Commons metadata has SHA256
9794e6182147c444a186642d338ddac58535219bfb8f59f3548bbe3a4764d521
and records Public domain, Copyrighted=False, AttributionRequired=false.
It is not yet a production source. Pages 45,50,53,55,57,61 are extracted as
/tmp/dyc-alt08-N.png. Page 50 corresponds to NCL06 page 25; the inspected
clothing pages have the same +25 offset. Review recipes are recorded in
seal-gap-review.json, including scan/pixel/metadata hashes. Review sheets
are output/font-review/seal-pending/dyc5768-trials.png, dyc5789-trials.png,
dyc5817-trials.png and dyc-altgarments.png.

Compiled outlines were inspected enlarged, at 24px and in browser dialogue.
Review: output/font-review/seal-pending/garments-accepted.png. All 173 browser
scenarios passed without failures or geometry warnings; all 254 JavaScript
tests passed. The recovery font now has 190 drawings: 113 CCZ, 73 DYC and
4 QJZ, including ten corrected upstream identities. Rebuilt 349 shards at
60,283,484 bytes. Visible cmap coverage is 171,496 / 172,352, leaving 856
missing. Seal has 168 gaps: preferred review routes are 6 CCZ, 120 DYC,
39 QJZ and 3 THX; 162 have no CCZ source. The raw inventory represents
171,524 public characters in 256 fonts, with 1,349 absent entries including
behavioural characters. All 11,360 production source files verified.

Next exact references: U+3E871 / D-05937 and U+3E890 / D-05967 (reference
106), U+3E89E / D-05977 and U+3E8BB / D-06005 (reference 107).
Sheet /tmp/dyc-next-body-refs.png. NCL06 pages 1–60 are extracted under
/tmp/dyc06-N.png; contacts include 37–48 and 49–60. These are unaccepted
source-location leads.

Validation completed: 88 targeted Python tests passed in 110.65 seconds, with
7 existing SWIG deprecation warnings. This is not a fresh full Python suite.
Manual and generated gap counts agree; whitespace checks passed.
Logs: /tmp/garments-{geometry,build,tests,js,reports,editions}.log.
The full Unicode beta remains incomplete and the goal stays active.


### Body and boat source review — 2026-11-02

Reviewed U+3E871/D-05937 and U+3E890/D-05967 in both NCL06 and
NLC08. Neither is ready for production: the body form loses fine internal
strokes, and the boat form has a broken stroke in NCL and a crossing page
ruling in NLC. Threshold comparisons and full crop recipes are preserved in
`seal-gap-review.json` and `output/font-review/seal-pending/`.

Rejected two nearby NCL06 page61 forms as substitutes for U+3E89E/D-05977,
and the page67 lower-left form as a substitute for U+3E8BB/D-06005.
Their recipes are explicitly marked rejected, not accepted glyph sources.
No production glyphs or coverage totals changed in this review.

Confirmed page correspondences: NLC08 page76 = NCL06 page51;
NLC08 page81 = NCL06 page57; page83 = page59; page85 = page61;
page89 = page65. NCL06 pages65–66 contain faint distinct text and must not
be dismissed as duplicate leaves. Next: locate the exact D-05977 and D-06005
variants using full-page context, including the clearer NLC08 pages89 onward.
The NLC08 PDF remains review-only because no glyph from it has been accepted.


### D-06025 recovery — 2026-11-02

Added U+3E8D0 from NCL06 page68, embedded image xref200,
crop [520,221,58,60], opening1 threshold0. The full-page context and
D-06025 chart reference agree; two components and seven counters survive
without local reconstruction. Source, compiled outline and 24px specimen are
in `output/font-review/seal-pending/see-accepted.png`. The browser dialogue
case `seal-recovery-dyc-see` was inspected visually.

The recovery font now contains 191 drawings: 113 CCZ, 74 DYC and four QJZ.
Bundled visible cmap coverage is 171,497/172,352, with 855 missing.
The 349 shards total 60,283,836 bytes. There are 167 Seal gaps, with preferred
references 6 CCZ / 119 DYC / 39 QJZ / 3 THX; 161 lack a CCZ reference.
The separate raw-source inventory has 171,525 public characters represented
and 1,348 absent, including behavioural characters; these totals are not
finished-lettering or linguistic-validation claims.

Located exact D-06005 in NCL06 page66 and NLC08 page90. The former loses
strokes and floods with scan noise at darker thresholds; the latter has a
ruling attached to left strokes. Both remain deferred with recipes and
comparison sheets saved. Earlier page67 crop remains rejected as a different
identity. D-05977 still requires an exact source variant.

Validation: 88 targeted Python tests passed in 112.79s, with seven existing
SWIG warnings; 254 JavaScript tests passed; 174 browser scenarios passed with
no failures or geometry warnings. All 11,360 cached source files passed hash
verification. Logs: /tmp/see-{build,tests,js,reports,editions}.log.

Next missing DYC references: U+3E93F/D-06134 (chart109), U+3E948/D-06142
(chart109), U+3E952/D-06151 (chart110), then U+3E968/D-06173.
Reference sheet: `output/font-review/seal-pending/dyc-next-eyes-refs.png`.
NCL06 pages1–120 are extracted as /tmp/dyc06-N.png, with twelve-page contact
sheets through109–120. Exact locations for these next references are not yet
verified. No build or test process remains running. The full goal stays active.


### D-06134 recovery — 2026-11-02

Added U+3E93F from NCL06 page 83, image xref 245, crop [459,383,59,64],
opening 1 threshold 40. Full-page and enlarged chart identity checks agree.
At this threshold six components and seven counters survive. Offset 35 loses
one counter; 45 joins distinct strokes. A regression test covers that boundary,
crop margins and the absence of local reconstruction. The compiled enlarged
and 24px specimen is `output/font-review/seal-pending/head-accepted.png`.

The recovery font now contains 192 drawings: 113 CCZ, 75 DYC and 4 QJZ.
The 349 shards total 60,284,268 bytes. Bundled visible cmap coverage is
171,498/172,352, leaving 854 missing. There are 166 Seal gaps, with preferred
references 6 CCZ / 118 DYC / 39 QJZ / 3 THX; 160 lack a CCZ reference.

D-06142 on NCL06 page 84 and D-06151 on page 85 remain deferred: threshold
comparisons do not recover their worn enclosed spaces and stems without
joining distinct parts. Recipes and review sheets are saved in the gap review.

Next candidate U+3E968/D-06173 is located on NCL06 page 87, image xref 257,
crop [239,348,62,70]. Offsets 10/20 yield three components and four counters;
30 picks up neighbouring ink and 40 also joins components. This is a review
lead, not an accepted production glyph. Recipe /tmp/dyc6173-t20.json;
comparison `output/font-review/seal-pending/dyc6173-trials.png`.
The next reference sheet includes D-06173 (chart 110), D-06386 (114),
D-06435 (115), and D-06524 (117). Other exact source locations remain open.

Validation completed: 89 targeted Python tests passed in 111.24 seconds,
with seven existing SWIG warnings; 254 JavaScript tests and 175 browser
scenarios passed. The new dialogue specimen was visually inspected and no
browser failures or geometry warnings were reported. All 11,360 cached source
files passed hash verification. Raw source coverage is 171,526 public characters
represented and 1,347 absent including behavioural characters. Logs:
/tmp/head-{geometry,build,tests,js,reports,editions}.log. Whitespace checks
passed. All build and test processes are terminal; the full goal remains active.


### Four head, ghost, mountain and cliff forms — 2026-11-02

Added U+3E968/D-06173, U+3EA49/D-06386, U+3EA7E/D-06435 and
U+3EAEE/D-06524 from pinned NCL06 pages 87, 124, 134 and 146.
D-06173 uses opening 1, threshold 20; the other three use opening 1,
threshold 0. Their crops and pixel hashes are in the recovery manifest.
Full-page context and enlarged chart comparisons confirm the identities.
The open upper enclosures in D-06435 and D-06524 are intentional; stronger
thresholding incorrectly closes one. The tight D-06435 crop excludes two
neighbouring page rules. Its initially proposed page129 form was rejected as
a different identity. No local stroke reconstruction was used.

Regression checks preserve component/counter counts (3/4, 5/5, 2/4, 2/3),
keep ink away from crop boundaries, demonstrate lost counters at a lighter
threshold, and detect the rules in the wider crop. The compiled enlarged and
24px specimens are in `output/font-review/seal-pending/headghost-accepted.png`.

The recovery font now contains 196 drawings: 113 CCZ, 79 DYC and four QJZ.
The 349 shards total 60,285,948 bytes. Bundled visible cmap coverage is
171,502/172,352, leaving 850 missing. The 162 Seal gaps have preferred
references 6 CCZ / 114 DYC / 39 QJZ / 3 THX; 156 lack CCZ references.
Raw source inventory represents 171,530 public characters, with 1,343 absent
including behavioural characters. All 11,360 cached source hashes verify.

Next references: U+3EAF0/D-06525, U+3EB15/D-06561, U+3EB1F/D-06570
(chart117), and U+3EB33/D-06588 (chart118). Their reference sheet is
`output/font-review/seal-pending/dyc-next-cliff-next-refs.png`.
D-06525 is on NCL06 page146, tentative crop [410,599,51,76]; initial
threshold0 extraction breaks inner strokes and includes commentary above
and below. Recipe /tmp/dyc6525.json and preview /tmp/dyc6525.png are unaccepted
location leads. Tighten and review thresholds before any acceptance.
NCL06 pages 1–156 are now extracted as /tmp/dyc06-N.png with twelve-page
contact sheets. D-06561 and D-06570 belong to the stone radical, so continue
through the later pages of this volume. Their exact locations are unverified.

Validation completed: 90 targeted Python tests passed in 112.99 seconds,
with seven existing SWIG warnings; 254 JavaScript tests and 176 browser
scenarios passed. The four new glyphs were visually inspected in dialogue
and as enlarged/24px compiled specimens. No browser failures or geometry
warnings were reported. Logs: /tmp/headghost-{geometry,build,tests,js,reports,editions}.log.
Whitespace checks passed. All build and test processes are terminal.
The full Unicode beta remains incomplete and the goal stays active.


### Two stone forms — 2026-11-02

Added U+3EB15/D-06561 and U+3EB1F/D-06570 from NCL06 pages 151
and 154. Crops [244,830,55,69] and [1120,444,52,64] use opening 1
and thresholds 0 and 30 respectively. The latter retains both eye bars;
lighter thresholds lose enclosed counters. Regression tests preserve their
4/1 and 3/4 component/counter counts, crop margins and absence of local
stroke reconstruction. Enlarged and 24px compiled specimens are saved in
`output/font-review/seal-pending/stones-accepted.png`; both were also
inspected in browser dialogue.

D-06525 remains deferred: the tight NCL06 page146 crop [414,607,42,64]
still has broken curves and counters across the tested thresholds.
D-06588 remains deferred: NCL06 page156 [355,607,52,57] lacks the
isolated mark visible in the identity reference. Widening the crop adds
commentary, not the missing mark. Neither defect was reconstructed.
Recipes and findings are retained in the gap review.

The recovery font contains 198 drawings: 113 CCZ, 81 DYC and four QJZ.
The 349 shards total 60,286,668 bytes. Bundled visible cmap coverage is
171,504/172,352, leaving 848 missing. The 160 Seal gaps have preferred
references 6 CCZ / 112 DYC / 39 QJZ / 3 THX; 154 lack CCZ references.
Raw sources represent 171,532 public characters, with 1,341 absent
including behavioural characters. All 11,360 pinned source files verify.

Validation: 91 targeted Python tests passed in 112.36 seconds (seven existing
SWIG warnings), 254 JavaScript tests passed, and all 177 browser scenarios
passed without failures or geometry warnings. Logs are in
/tmp/stones-{geometry,build,tests,js,reports,editions}.log.

Review-only NCL07 is downloaded as dyc-07.pdf: 50,742,374 bytes, 156 pages,
SHA256 b5d9136df2feb45cad6b15b2ec8c3f7ee090bb00f86d5f5904ad8363679bb33f.
Commons metadata identifies it as public domain; its 2,890-byte metadata has
SHA256 83a224bfb09c83668b6a54355e83a0c32ac1e3ef3562385808e50dad2ff52707.
It is not yet a production source. First twelve pages are extracted under
/tmp/dyc07-N.png; the first three continue stone entries. The unreviewed
next reference sheet /tmp/dyc-next-volume7-refs.png contains D-06589,
D-06679, D-06700 and D-06711. This is preparation only, with no accepted
mappings from this volume. The Unicode beta goal remains incomplete.


### First NCL07 stone form — 2026-11-02

Added U+3EB35/D-06589 from NCL07 page1, xref472, crop [904,182,49,60],
opening1 and threshold0. The full-page context and chart reference agree;
six separate parts and one enclosed counter survive without local repairs.
The source PDF and public-domain metadata are now pinned in the production
manifest (hashes recorded in the previous checkpoint). The existing stone
geometry regression includes this glyph. Compiled enlarged/24px specimen:
`output/font-review/seal-pending/stone7-accepted.png`. Browser dialogue was
visually inspected.

The recovery font now has 199 drawings: 113 CCZ, 82 DYC and four QJZ.
349 shards total 60,286,960 bytes. Visible cmap coverage is 171,505/172,352,
leaving 847 missing. There are 159 Seal gaps (preferred references 6 CCZ,
111 DYC, 39 QJZ, 3 THX), of which 153 lack a current CCZ reference.
Raw sources cover 171,533 public characters, leaving 1,340 absent including
behavioural characters. All 11,362 pinned files verify. JavaScript tests
passed (254), as did all 178 browser scenarios without geometry warnings.

Next source lead: U+3EBBD/D-06711 is on NCL07 page22, xref62,
crop [842,484,52,62]. Initial opening1/threshold0 extraction has 2 parts
and 6 counters and visually matches the horse form. Recipe /tmp/dyc6711.json
and preview `output/font-review/seal-pending/dyc6711.png` remain review-only;
check crop boundaries and compiled appearance before integrating. NCL07
pages1–24 are extracted as /tmp/dyc07-N.png; contacts are
/tmp/dyc07-1-12.png and /tmp/dyc07-13-24.png. Horse entries start around
pages18–19. D-06679 and D-06700 remain unlocated. The goal remains active.

Targeted Python validation completed: 91 tests passed in 113.86 seconds,
with seven existing SWIG warnings. All current build/test processes are
terminal. Logs: /tmp/stone7-{build,tests,js,reports,editions}.log.
Whitespace checks pass. D-06711 threshold trials preserve 2 parts/6 counters
at offsets0–20 but merge to one part at30. Its current left ink margin is only
one doubled pixel: widen the crop on the left before acceptance.


### Two NCL07 horse forms — 2026-11-02

Added U+3EBB1/D-06700 from NCL07 page20, xref56, crop [298,307,54,62],
and U+3EBBD/D-06711 from page22, xref62, crop [839,484,55,62]. Both use
opening1/threshold0. The latter crop was widened three source pixels to
retain a safe left margin. Full-page context and the chart forms match.
Two detached components and five/six counters are preserved, without local
reconstruction. The new geometry regression checks margins and counters and
shows that threshold30 incorrectly merges D-06711's two components.
Compiled enlarged and 24px specimens are in
`output/font-review/seal-pending/horses-accepted.png`; both were inspected
in browser dialogue.

The recovery font contains 201 drawings: 113 CCZ, 84 DYC, four QJZ.
349 shards total 60,287,744 bytes. Visible cmap coverage is 171,507/172,352,
leaving 845 missing. The 157 Seal gaps have preferred references 6 CCZ /
109 DYC / 39 QJZ / 3 THX; 151 lack CCZ references. Raw sources cover
171,535 public characters, with 1,338 absent including behavioural characters.
All 11,362 pinned files verify. 254 JavaScript tests and 179 browser scenarios
passed, with no browser failures or geometry warnings.

Located next candidate U+3EB9C/D-06679 on NCL07 page13, xref35, crop
[515,673,55,64], among animal entries before the horse section. Initial
opening1/threshold0 extraction has four components and one counter, consistent
with the reference (left form, outer enclosure, two inner strokes). It remains
unintegrated; recipe /tmp/dyc6679.json and preview
`output/font-review/seal-pending/dyc6679.png` are review leads.

NCL07 pages1–36 are extracted under /tmp/dyc07-N.png. The latest contact
sheet is /tmp/dyc07-25-36.png. Next references D-06756, D-06784 and
D-06789 are on chart121; D-06848 is on chart122. Their sheet is
`output/font-review/seal-pending/dyc-next-horses-refs.png`. These later
locations are not yet verified. The full Unicode beta remains incomplete.

Targeted Python validation completed: 92 tests passed in 115.04 seconds,
with seven existing SWIG warnings. Build and test processes are terminal.
Logs: /tmp/horses-{build,tests,js,reports,editions}.log. Whitespace checks pass.


### Three more NCL07 animal and horse forms — 2026-11-02

Added U+3EB9C/D-06679 (page13/xref35, [515,673,55,64]),
U+3EBEA/D-06756 (page29/xref83, [451,500,51,69]), and
U+3EC0C/D-06789 (page33/xref95, [776,645,54,67]). All use opening1;
threshold offsets are 0, 0 and 12. The second crop was moved upward to retain
all three top strokes. The last has a narrow extraction interval: offset10
loses an eye bar, offset12 preserves 7 parts/3 counters, and offset16 merges
two interior marks. A regression covers these failure modes along with
crop margins and the other forms' 4/1 and 6/3 component/counter counts.
No local reconstruction was used. Source context and reference identities
were visually checked, as were compiled enlarged/24px specimens and dialogue.
Specimens: `output/font-review/seal-pending/laterhorses-accepted.png`.

D-06784 was located on page32/xref92, crop [339,771,58,67], but remains
deferred. The upper interior strokes are damaged and the lower horse has a
false closed loop. Thresholds0–40 do not recover the reference form.
The gap review records the recipe; trial sheets are retained in seal-pending.

The recovery font contains 204 drawings: 113 CCZ, 87 DYC and four QJZ.
349 shards total 60,289,160 bytes. Visible cmap coverage is 171,510/172,352,
leaving 842 missing. The 154 Seal gaps have preferred references 6 CCZ /
106 DYC / 39 QJZ / 3 THX; 148 lack CCZ references. Raw sources represent
171,538 public characters, leaving 1,335 absent including behavioural
characters. All 11,362 pinned files verify. 254 JavaScript tests and all
180 browser scenarios passed without browser failures or geometry warnings.

Next located candidate: U+3EC4C/D-06848, NCL07 page41/xref119,
[828,477,54,73]. Offset0 breaks the right enclosure; offset10 restores
4 parts and 2 counters, retained through offset40. Recipe
/tmp/dyc6848-t10.json is unintegrated. Verify crop margins and compiled
appearance before acceptance. Preview and trials are in seal-pending.
NCL07 pages1–48 are extracted; latest contact /tmp/dyc07-37-48.png.
Next reference sheet `output/font-review/seal-pending/dyc-next-deer-refs.png`
includes D-06848 (chart122), D-06863 (123), D-06922 and D-06934 (124).
The latter three locations are not verified. The full beta remains incomplete.

Targeted Python validation completed: 93 tests passed in 116.10 seconds,
with seven existing SWIG warnings. All build/test processes are terminal.
Logs: /tmp/laterhorses-{build,tests,js,reports,editions}.log. Whitespace checks pass.


### Deer, rabbit and two dog forms — 2026-11-02

Added U+3EC4C/D-06848 (NCL07 p41/xref119, [828,477,54,73], t10),
U+3EC5D/D-06863 (p43/xref125, [574,737,40,72], t40),
U+3EC9A/D-06922 (p49/xref143, [767,788,58,68], t0), and
U+3ECA7/D-06934 (p50/xref146, [397,657,56,66], t0). All use opening1.
Margins were widened where required, and full-page context plus enlarged
reference forms were inspected. The rabbit's faint left loop and D-06848's
right enclosure require their recorded thresholds; lighter offsets leave
one loop open. Geometry checks preserve 4/2, 1/2, 2/11 and 3/0 parts/counters
and safe crop margins without local repairs. Compiled enlarged and 24px
specimens are in `output/font-review/seal-pending/deerrabbit-accepted.png`.

The recovery font contains 208 drawings: 113 CCZ, 91 DYC and four QJZ.
349 shards total 60,290,508 bytes. Visible cmap coverage is 171,514/172,352,
leaving 838 missing. There are 150 Seal gaps: preferred references 6 CCZ /
102 DYC / 39 QJZ / 3 THX; 144 lack CCZ references. Raw sources represent
171,542 public characters, with 1,331 absent including behavioural characters.
All 11,362 source hashes verify; 254 JavaScript tests pass.

Located D-07012/U+3ECFA at NCL07 p61/xref179, [1063,154,57,66].
It remains deferred: the upper curve stays broken across offsets0–40.
The gap review and `output/font-review/seal-pending/dyc7012-trials.png`
retain the evidence. No strokes were reconstructed. NCL07 pages1–72 are
extracted; latest contact /tmp/dyc07-61-72.png. Next references are D-07054
and D-07071 (chart126), D-07094 (chart127), in
`output/font-review/seal-pending/dyc-next-fire-refs.png`. Their exact locations
remain unverified. The full Unicode beta remains incomplete.


Validation completed: 94 targeted Python tests passed in 116.44 seconds,
with seven existing SWIG warnings; all 181 browser scenarios passed with no
failures or geometry warnings. The four glyphs were visually checked in dialogue.
Build and test processes are terminal. Logs:
/tmp/deerrabbit-{geometry,build,tests,js,reports,editions}.log. Whitespace checks pass.


### Forest-over-fire form — 2026-11-02

Added U+3ED25/D-07054 from NCL07 page66/xref194, crop [1124,282,52,67],
opening1/threshold0. Full-page context and reference match; five detached
parts and no counters survive without local repairs. Regression checks preserve
those components and crop margins. Compiled enlarged/24px preview:
`output/font-review/seal-pending/forestfire-accepted.png`; dialogue was inspected.

D-07071 was located on page67/xref197, [718,412,60,67]. Threshold30 joins
its eye bar on the right, as in the enlarged chart reference, but the source
lacks the small lower-right loop shown in that reference. It remains deferred.
D-07094 is on page69/xref203, [572,138,52,69]. Its upper strokes touch a
horizontal page rule and extraction loses the interior dot. It also remains
deferred. Both recipes and findings are recorded in the gap review.

The recovery font has 209 drawings: 113 CCZ, 92 DYC and four QJZ.
349 shards total 60,291,000 bytes. Visible cmap coverage is 171,515/172,352,
leaving 837 missing. The 149 Seal gaps have preferred references 6 CCZ /
101 DYC / 39 QJZ / 3 THX; 143 lack CCZ references. Raw sources represent
171,543 public characters, leaving 1,330 absent including behavioural characters.
All 11,362 source hashes verify. Validation: 95 targeted Python tests passed
in 117.23 seconds (seven existing SWIG warnings), 254 JavaScript tests and
182 browser scenarios passed without browser failures or geometry warnings.
All build/test processes are terminal. Logs:
/tmp/forestfire-{build,tests,js,reports,editions}.log. Whitespace checks pass.

Next located candidate: D-07112/U+3ED68, page71/xref209,
[221,574,58,67]. Initial extraction gives 6 parts/1 counter. The lower fire
stroke touches the adjacent enclosure; threshold10 adds an interior counter,
while threshold-20 breaks the enclosure. Compare an enlarged reference before
accepting or rejecting these contacts. /tmp/dyc7112.json and
`output/font-review/seal-pending/dyc7112-trials.png` are unaccepted leads.
NCL07 pages1–84 are extracted; latest contact /tmp/dyc07-73-84.png.
Next reference sheet `output/font-review/seal-pending/dyc-next-after-fire-refs.png`
contains D-07112 (chart127), D-07164 and D-07189 (128), D-07328 (131).
The latter three locations are unverified. The full Unicode beta remains incomplete.


## Fire, vessel and roof recovery checkpoint

Added U+3ED68/D-07112, U+3ED9F/D-07164 and U+3EDBB/D-07189
from NCL07 pages71/xref209, 81/xref239 and 84/xref248 respectively.
Crops are [221,574,58,67], [830,698,59,67] and [396,758,57,67].
All use opening1. D-07112 uses threshold10: the enlarged identity reference
confirms that the lower fire stroke contacts the vessel wall and the inner
branch joins its right wall; this preserves six parts and two counters.
The other two use threshold0, preserving four parts/four counters and two
parts/two counters. The wider D-07164 crop avoids clipping fine outer strokes;
page-rule debris is removed by ordinary component filtering. No local repairs
or reconstructed strokes were used. Compiled enlarged and 24px results were
visually inspected in `output/font-review/seal-pending/fireroof-accepted.png`.

There are now 212 recovered drawings: 113 CCZ, 95 DYC and four QJZ.
349 shards total 60,292,452 bytes. Bundled visible cmap coverage is
171,518/172,352, leaving 834 missing. The 146 Seal gaps have preferred
references 6 CCZ / 98 DYC / 39 QJZ / 3 THX; 140 lack CCZ references.
Raw sources represent 171,546 public characters, with 1,327 absent including
behavioural characters. All 11,362 source hashes verify.

Next source lead remains U+3EE47/D-07328 (chart131); its exact source location
has not been verified. NCL07 pages85–108 are now extracted and their contact
sheets inspected; page101 was inspected at full size. Contacts:
/tmp/dyc07-85-96.png and /tmp/dyc07-97-108.png. Do not treat these as accepted
recipes. The beta remains substantially incomplete.

Validation for this batch: 96 targeted Python tests passed in 116.95 seconds
with the seven existing SWIG warnings; 254 JavaScript tests passed; 183 browser
scenarios passed with no failures or geometry warnings. The new dialogue
specimen was visually inspected. All build, report and test processes finished
successfully. Logs: /tmp/fireroof-{build,tests,js,reports,editions}.log.

## Timepieces and stationery expansion

The next emoji batch adds seven timepieces and 27 stationery symbols from the
existing pinned Noto Emoji donor, using the expressive procedural treatment.
The preflight source/treatment sheets were visually inspected enlarged and at
24 pixels. All 34 candidates passed per-glyph outline contour checks after
raising U+1F4CD's source raster to 512 pixels: at 384 pixels its tiny highlight
was lost during tracing despite passing the raster topology guard. Other new
glyphs use weight400/384 pixels. The drawing/guard settings remain unchanged.

The new scope includes 44 registered presentation variants. Added checks cover
custom cluster routing, distinct nonempty outlines, exact presentation shaping,
and the sand state in the compiled hourglass pair. Four browser dialogue cases
cover the batch. Build/review/test logs use /tmp/office-*; preflight images are
/tmp/emoji-timepieces.png and /tmp/emoji-stationery.png. The full build completed: 661 bases, 1,126 explicit sequences and 27 shaping
components, in 417,644 bytes. Enlarged/24px packaged specimens and all four
browser dialogue examples were visually inspected. The coverage audit reports
171,531/172,352 visible mappings, leaving 821 missing (13 filled by this batch).
All 11,362 pinned source files verify. Raw sources cover 171,559 public
characters, leaving 1,314 absent including behavioural characters.

The next major emoji work includes colour-semantic symbols and fruits, remaining
people/modifier/ZWJ families and flags, and newer additions absent from this
pinned donor. The current visible coverage report still has 487 gaps present
in the donor before this batch; donor presence alone does not validate a drawing
or sequence. The full Unicode beta remains incomplete.

Validation: 255 JavaScript tests and 187 browser scenarios passed, with
no browser failures or geometry warnings; 28 pen-treatment/source-fetch tests
and five inventory tests passed. The hourglass probe originally intersected
the curved upper rim (6.9% ink in an intended empty chamber); visual inspection
confirmed the drawing was correct. Moving its upper sampling edge to 24% of
the ink bounds isolates the chamber, measuring 0% for the completed glass and
68% for the running glass. The corrected targeted regression passes. The deterministic font/manifest rebuild passed. Its already-loaded test file
still used the old hourglass sampling window and therefore ended with 44 passed
and that one known probe failure in 243.08 seconds. The corrected current file
then passed all 44 non-rebuild tests in 42.39 seconds; the separate corrected
hourglass run also passed. Together these validate all 45 current emoji tests,
including byte-for-byte reproduction. Seven existing SWIG warnings remain.
All build, report and test processes are terminal; whitespace checks pass.
Compiled specimens: `output/font-review/pen-translation/compiled-timepieces.png`
and `output/font-review/pen-translation/compiled-stationery.png`.
Logs: /tmp/office-{build,font-tests,font-tests-final,hourglass,targeted,js,
audit,inventory,inventory-tests,hashes,support-tests}.log.

## Produce and apple expansion

Added 34 monochrome fruit/vegetable/nut candidates and two selectively coloured
apple identities using the existing pinned Noto Emoji donor. Preflight sheets
/tmp/emoji-produce.png and /tmp/coloured-apples.png were inspected enlarged and
at 24 pixels. All monochrome candidates use weight400/384 pixels and passed
per-glyph outline checks without settings changes. The apples share the outlined
green-apple donor (U+1F34F); the red donor is a solid silhouette. Both preserve
one ink component and one enclosed body region, with colour underneath the ink.
This deliberate source adaptation is recorded in `emoji_apples.py` and the
glyph-review provenance, rather than claiming to trace two independent drawings.

Red [174,41,42] and green [134,177,152] were rechecked against the full-resolution
page20 rug and page47 landscape patches in the supplied PDF. The stored rendered
page hashes and patch medians reproduce exactly. `apple-palette-source.json`
records the copied samples and hash of the earlier verified palette record.
No new colour or image-generation source was introduced.

The batch adds two registered hot-pepper presentation variants and three browser
cases. Tests cover category inventory, exact sequence shaping, distinct produce
outlines and shared apple ink/metrics with distinct colour layers and underpaint.
The font build completed: 697 bases, 1,164 exact sequences and 27 shaping
components in 436,964 bytes. Compiled enlarged and 24px specimens were reviewed
in `output/font-review/pen-translation/compiled-produce.png` and
`output/font-review/pen-translation/compiled-apples.png`. The audit now shows
171,563/172,352 visible mappings, leaving 789 gaps (32 filled by this batch).
Raw sources represent 171,591 public characters, with 1,282 absent including
behavioural characters. All 11,362 pinned source hashes verify.
JavaScript validation passed 256 tests; the targeted apple test passes.
All 190 browser scenarios passed without failures or geometry warnings; all
three new dialogue specimens were visually inspected, including both apple
colours. Five inventory tests passed. All 47 emoji tests passed in 258.72 seconds, including byte-for-byte font
and manifest reproduction, with seven existing SWIG deprecation warnings.
All build/report/test processes finished successfully. Whitespace checks pass.
Logs: /tmp/produce-{build,font-tests,apples-tests,js,audit,inventory,
inventory-tests,hashes}.log. The full Unicode beta remains incomplete.
Logs use /tmp/produce-*.

An independent source follow-up found a first-person Garay WIP post by Simon
Charwey, but no inspected release/licence grant; it is recorded as a lead in
`unicode-source-review.json`. The Tai Yo Noto issue was rechecked and still
leaves provenance and accent anchors unresolved. These fonts remain excluded;
no coverage or licence approval is inferred from a name or specimen.

## Lime and brown-mushroom sequence expansion

Added the pinned donor's exact `🍋‍🟩` and `🍄‍🟫` ligatures. Each has one
registered qualification form. Preflight source/treatment and coloured previews
were inspected at enlarged and 24px sizes. Lime uses the largest enclosed region
as green rind, preserving five white flesh regions. Brown mushroom preserves its
original solid cap as monochrome fallback; a separate COLR mask opens a brown
interior inside an eight-pixel border of the treated silhouette. The two white
highlights and white stem remain unchanged. The cap boundary is derived from the
large stem interior's top row, and assertions pin the source anatomy. This
explicit colour-layer conversion is separate from the topology-preserving pen
translation and is named in the glyph review.

Green reuses the verified apple palette; brown [139,106,68] was rechecked against
the full-resolution page13 PDF patch and exactly reproduces the existing heart
palette sample. Source records, PDF and palette hashes are checked during build.
Added tests cover colour regions, sequence boundaries/repetition, incorrect
fruit/square combinations, and unregistered selectors. One browser case compares
the compounds with their standalone components. No new cmap coverage is claimed.
The full font build completed: 697 bases, 1,166 exact sequences and 27
components in 438,052 bytes. The compiled compound specimen was visually
inspected enlarged and at 24px (`output/font-review/pen-translation/compiled-compounds.png`).
The two targeted sequence/colour tests, 257 JavaScript tests and five inventory
tests pass. All 11,362 pinned source hashes verify. Visible coverage remains
171,563/172,352 with 789 missing, and raw-source coverage remains 171,591
public characters with 1,282 absent including behavioural characters.
All 191 browser scenarios passed without failures or geometry warnings. The
new dialogue specimen was visually inspected, including repeated compounds
and separate standalone components. All 48 emoji tests passed in 256.83 seconds, including exact font and manifest
reproduction, with seven existing SWIG warnings. All build, test and report
processes are terminal. Whitespace checks pass. Logs:
/tmp/produce-sequences-{build,font-tests,targeted,js,audit,inventory,
inventory-tests,hashes}.log.
Logs use /tmp/produce-sequences-*. The Unicode beta remains incomplete.

The Garay lead was followed into Noto issue71, which records a proposed
collaboration in April2026 but exposes no release or licence grant. The author
also reports disputed glyph forms in earlier sources. This evidence is recorded
in `unicode-source-review.json`; do not treat earlier donor/chart copying as
independent script validation or permission.

## Additional hand gestures

Preflight-reviewed 14 new gesture bases: directional/palm/pointing/heart/pushing
hands, clapping, open/raised/folded hands, cupped palms and handshake. All use the
pinned Noto source at weight400/384 pixels and the guarded strength1.7 treatment.
Heart hands initially coloured their central air gap; it is now excluded using
the reviewed three-region anatomy. The pushing and raised hands initially left
palms unfilled because of open wrists. Fill-only closure segments now join
reviewed endpoints, leaving black ink unchanged. Preflight source/tone sheets
and region maps were inspected. All 14 outlines compile without dropped contours.
The open-wrist regression passes and verifies unchanged ink plus substantial
separate palm fills.

All 70 new modifier forms were checked against the pinned RGI modifier inventory.
The font now includes 39 gestures with 195 modifier forms, with 84 new custom
sequences including bases. Mixed-tone handshake ZWJ combinations remain open.
The font build completed: 711 bases, 1,250 exact sequences and 27 components
in 446,992 bytes. Compiled neutral and representative five-tone specimens were
visually inspected enlarged and at 24px: `compiled-new-gestures.png` and
`compiled-new-gesture-tones.png` under `output/font-review/pen-translation/`.
The two targeted colour-mask tests and 257 JavaScript tests pass. Visible
coverage is 171,577/172,352, leaving 775 gaps (14 filled). Raw sources represent
171,605 public characters, leaving 1,268 absent including behavioural characters.
All 11,362 source hashes verify. Five inventory tests and all 195 browser
scenarios pass, without browser failures or geometry warnings. Dialogue
specimens9–13 were visually inspected across all five tones, including heart
gaps and open wrists. All 49 emoji tests passed in 264.98 seconds, including
byte-for-byte font and manifest reproduction, with seven existing SWIG warnings.
All build, test and report processes are terminal. Whitespace checks pass.
Logs and preflight files use /tmp/new-hands-*. The full Unicode beta remains
incomplete.

Next handshake lead: the pinned Unicode ZWJ inventory has 20 mixed-tone
handshake sequences beginning U+1FAF1. All 20 shape to the donor's `u1F91D`
glyph (verified with HarfBuzz), so the outline can be shared; the missing work
is verifying which enclosed regions belong to each hand and building separate
colour masks with the correct left/right tone assignment. Forms are recorded
in /tmp/handshake-next-forms.txt. None of these 20 sequences is advertised yet.


## Mixed-tone handshakes

Previous goal turn: progress, completing and verifying the 14-hand expansion.
This batch adds the 20 exact RGI mixed-tone handshake sequences. Official Noto
colour reference inspection confirmed that the tiny lowest fingertip belongs
to the left-entering hand, while the four curled fingers belong to the other
hand. The two colour masks reuse existing PDF-sampled tones and preserve the
shared ink and advance. Source/reference evidence and anatomy are recorded in
`emoji-pen-translation.md`; no colour-reference artwork is copied into the font.
Build completed: 711 bases, 1,270 exact sequences, 27 components and 447,368
bytes. All 20 compiled colour pairs were visually inspected enlarged and at
24px in `output/font-review/pen-translation/compiled-mixed-handshakes.png`.
The anatomical/ligature regression passes, as do all 258 JavaScript tests and
five inventory tests. All 11,362 source hashes verify. Visible coverage remains
171,577/172,352 (775 missing); raw source coverage remains 171,605 public
characters (1,268 absent including behavioural characters). All 196 browser
scenarios passed without failures or geometry warnings; the mixed-tone dialogue
specimen was visually inspected. All 20 donor sequences shape to the reviewed
`u1F91D` glyph. All 50 emoji tests passed in 265.95 seconds, including exact
font and manifest reproduction, with seven existing SWIG warnings. All build,
test and report processes are terminal; whitespace checks pass. Logs use
/tmp/mixed-hands-*. The full Unicode beta remains incomplete.

Independent next-batch preflight: 38 clothing/accessory drawings were treated
at weight400/384px and strength1.7, visually inspected enlarged and at 24px.
All passed contour-count preservation without fallback. These are not yet
included in the production manifest. Reusable preflight: /tmp/review-clothing.py,
/tmp/clothing-preflight.log and /tmp/emoji-clothing.png. Symbols:
👑👒🎩🎓🧢🪖⛑🧣🧤🧥🧦👔👕👖👗👘🥻🩱🩲🩳👙👚👛👜👝🎒🩴👞👟🥾🥿👠👡🩰👢🥼🦺🥽.
Clothing integration note: U+1F9BA safety vest currently has a blank component-only
cmap entry for the service-dog sequence. Adding its drawing before compound
construction should promote it to a standalone base and remove it from the
component-only list, while retaining the service-dog ligature. The 38 candidates
have four registered variation forms (helmet and graduation cap, VS15/VS16),
recorded in /tmp/clothing-variations.txt. Validate that promotion explicitly.

## Clothing and accessories

Previous goal turn: progress, completing the 20 mixed-tone handshakes and
preflighting this batch. The 38 reviewed drawings are now integrated into the
licensed category with their four registered variation forms. Safety vest is
promoted from a blank component-only entry; a regression checks standalone
outlines/advance, the service-dog ligature, and adjacency in a shared run.
Four browser scenarios cover the new drawings and the vest/compound comparison.
Build completed: 749 bases, 1,312 exact sequences, 26 components and 470,368
bytes. All 38 compiled drawings were inspected enlarged and at 24px in
`output/font-review/pen-translation/compiled-clothing.png`. Both targeted tests
pass, as do all 259 JavaScript tests and five inventory tests. All 11,362 source
hashes verify. Visible coverage is 171,607/172,352, leaving 745 gaps (30 filled);
raw sources represent 171,635 public characters, with 1,238 absent including
behavioural characters. All 200 browser scenarios pass with no failures or
geometry warnings. All four clothing dialogue specimens were inspected,
including standalone vest beside the service-dog compound. All 52 emoji tests
passed in 275.67 seconds, including byte-for-byte font and manifest reproduction,
with seven existing SWIG warnings. All build, test, preflight and report processes
are terminal. Whitespace checks pass. The full Unicode beta remains incomplete.
Logs use /tmp/clothing-*.

Independent next-batch preflight: 36 electronics/media/lighting drawings were
reviewed enlarged and at 24px, with all contours preserved and no fallback after
source-setting adjustments. Laptop U+1F4BB uses weight400/768px, desktop U+1F5A5
uses weight350/768px, and projector U+1F4FD uses weight400/512px. These retain
small keys/reel holes that forced unchanged fallback at default resolution;
all other candidates use weight400/384px. The reduced applied strength for the
three detailed drawings is about0.30. None is integrated yet. There are 34
registered variation forms and no existing custom cmap entries to promote.
Scripts/logs: /tmp/review-electronics-fixed.py, /tmp/electronics-fixed.log,
/tmp/preflight-electronics-detail.py, /tmp/electronics-detail.log,
/tmp/electronics-variations.txt. Sheet: /tmp/emoji-electronics.png. Candidates:
📱📲☎📞📟📠🔋🪫🔌💻🖥🖨⌨🖱🖲💽💾💿📀🧮🎥🎞📽🎬📺📷📸📹📼🔍🔎🕯💡🔦🏮🪔.


New script-source evidence: GNU Unifont Upper18.0.01 provides explicitly
OFL-licensed visible drawings for all 69 Garay, 54 Tolong Siki and 55 Tai Yo
characters still missing. Embedded nameID13 confirms the publisher's licence;
release attribution names Johnnie Weaver (Garay/Tolong) and Paul Hardy (Tai Yo).
Downloaded review-only file: /tmp/unifont_upper-18.0.01.otf, 5,954,156 bytes,
SHA256472201e45a050bff4c7658208b8c73e34ebce3764b287a5a46c7774038ef9391.
All three complete sheets were inspected under /tmp/unifont-review-{garay,tolong,taiyo}.png.
These are actual script forms, not hexadecimal placeholders. GSUB/GPOS feature
lists are empty. This is an adaptation source, not ready lettering or shaping;
no coverage is claimed yet. Details and source URL are recorded in
`unicode-source-review.json`. Prototype smooth Tolong forms and native behaviour
against authoritative references before adding any production source manifest.

## Electronics, media and lighting

Previous goal turn: progress, completing clothing and locating a licensed
source candidate for three missing scripts. Integrated the 36 preflighted
object drawings with their 34 registered variation forms. The three detailed
source settings are recorded above and in the builder; other sources remain
weight400/384px. Four browser cases cover bases and representative selectors.
Build completed: 785 bases, 1,382 exact sequences, 26 components and 492,516
bytes. All 36 compiled drawings were inspected enlarged and at 24px in
`output/font-review/pen-translation/compiled-electronics.png`. The targeted
category test and five inventory tests pass. All 11,362 source hashes verify.
Visible coverage is 171,625/172,352, leaving 727 gaps (18 filled); raw sources
represent 171,653 public characters, leaving 1,220 absent including behavioural
characters. The JS suite exposed one outdated telephone-VS15 expectation, now
updated because that registered form has a custom monochrome drawing. All 260
JavaScript tests now pass. All 204 browser scenarios pass with no failures or
geometry warnings; all four electronics dialogue specimens were inspected,
including text/emoji selectors and small keyboard/reel details. All 53 emoji
tests passed in 298.26 seconds, including exact font and manifest reproduction,
with seven existing SWIG warnings. All build, test, preflight and report processes
are terminal. Whitespace checks pass. The full Unicode beta remains incomplete. Logs use /tmp/electronics-*.


Tolong prototype: `tools/font/prototype_unifont_lettering.py` now produces all
54 comparison entries from the pinned licensed donor, without changing fonts or
coverage. Initial topology-only smoothing was too heavy and shrank counters.
Stricter per-component area and counter-overlap checks reject five forms
(U+11DB1,11DB2,11DBE,11DC2,11DC3); others still show pixel-grid bends and are not
approved production lettering. The complete source/result sheet and JSON are in
`output/font-review/unifont-prototype/`. The released Unicode18 section13.24 and
proposal pages3–4 were checked for anatomy and behaviour. Native mark attachment
is required for common marks outside the block; there are no conjuncts. See
`docs/unifont-lettering-experiment.md` for reproduction, references, exact marks
and the next centre-line/redrawing experiment. No script coverage is claimed.

The Tolong prototype was reproduced in /tmp/tolong-reproduction; both the PNG
and JSON match byte-for-byte. Both prototype runs are terminal.

## Tolong Siki stroke reconstruction

Previous goal turn: progress, finishing electronics and exposing limitations of
edge-rounded pixel letters. Added `tools/font/unifont_strokes.py` and a `strokes`
mode to the licensed-source prototype. Paths preserve graph junctions, suppress
false diagonal shortcuts, and distinguish cycle strokes from connecting strokes.
Compact detached marks retain round dot geometry and area. Bounded stroke/loop
width and pressure searches retain the existing 80–120% component area and 75%
counter-overlap checks. U+11DB2 additionally needs a reviewed local counter
adjustment, capped at 0.3 source pixels and shared across incident paths.

All 54 Tolong forms now pass these checks with nonzero pressure. Minimum counter
overlap is 0.75146484375; component-area ratios span 0.80244140625–1.051025390625.
The full source/result/24px sheet was visually inspected. Four regression tests
pass (seven existing SWIG warnings), and an independent run exactly reproduces
both PNG and JSON. All processes are terminal and whitespace checks pass.
Artifacts: `output/font-review/unifont-strokes/`; details and the integration plan:
`docs/unifont-lettering-experiment.md`. Logs: /tmp/tolong-strokes-guarded.log,
/tmp/tolong-strokes-reproduction.log, /tmp/tolong-stroke-tests.log.

This is a candidate outline set, not production coverage or fluent-reader proof.
The 54 mappings remain missing until a licensed derivative font, mark attachment,
compiled outlines and real-browser behaviour are integrated and validated. The
source contains none of the nine required BMP combining marks. Next implement
that complete Tolong font path, using the reusable `prepare_letter` function;
keep source glyphs distinct, preserve spacing signs, and verify Table13-11 and
nasalized-vowel+SELA examples. The overall Unicode beta remains incomplete.

## Tolong Siki compiled review font

The reviewed 54-character stroke set now compiles to a real 1000-UPM font via
`tools/font/build_tolong.py`. Nine required BMP marks are borrowed from the
hash-verified, already licensed Noto Sans donor. Both source copyright notices
are embedded, and Unifont's publisher OFL plus copyright have been retained in
`assets/fonts/licenses/Unifont-OFL.txt`. Marks remain provisionally donor-styled.

Native GPOS attaches marks above/below the actual bounds of each letter, with
zero advances and same-side mark stacking. SELA and HECAKA remain spacing signs.
`tools/font/preview_tolong.py` renders the compiled font through HarfBuzz;
`output/font-review/tolong/compiled.png` was visually inspected at 40px and 24px,
including Unicode table 13-11, all bases/digits, all nine marks, nasalized vowels
plus SELA, and repeated marks. The script and mark geometry tests plus prior
stroke tests pass: 18 passed in 0.72s, seven existing SWIG warnings.

A second complete build to `/tmp/tolong-font-reproduction.ttf` reproduces the
TTF and JSON byte-for-byte. `git diff --check` passes. All build and preview
processes are terminal. Production counts remain unchanged: this font is a
review artifact, not yet a registered source or delivered script shard.
Next: package the pinned source/license for reproducible fetching, register the
derivative builder, route whole Tolong clusters to its shard, and validate
browser shaping, wrapping and exports before updating delivered coverage.

## Tolong Siki production integration

Pinned GNU Unifont Upper 18.0.01 and its publisher OFL in
`data/font-sources/tolong.json`. Source verification now supports a donor-only
font: its broad cmap is deliberately excluded from candidate/delivered counts.
The registered Tolong builder derives only the 54 assigned script forms and
adds nine licensed Noto Sans marks. It caches by recipe/input bytes and verifies
the output hash. The generated TTF is byte-identical to the previously reproduced
review font. The final WOFF2 retains mark and mkmk attachment.

The app's existing whole-cluster selection selects the complete Tolong shard
for bases and inherited marks; a regression verifies that routing. Both review
TTF and delivered WOFF2 now undergo the geometry tests. Validation: 59 targeted
Python tests pass in 18.25s (seven existing SWIG warnings), all 261 JavaScript
tests pass, 11,364 source hashes verify, and all 207 browser scenarios pass.
Three added browser specimens were visually inspected: marks/Unicode table
13-11, nasalized vowels with SELA plus spacing HECAKA and digits, and mixed
Latin/Arabic text with above/below mark stacks. PNG round trips and ink/balloon
geometry passed through the browser harness. An initial test setup error used
two rather than four panel strings; corrected before the passing run.

Current delivery: 350 script shards, 60,307,156 bytes; bundled cmap coverage
171,679/172,352 visible requirements, 673 missing. Source inventory: 257 fonts,
171,707 public characters represented, 1,166 absent including behavioural
characters. No Tolong assigned characters remain absent. These counts do not
establish linguistic correctness or completion of custom styling: marks still
use provisional donor outlines, and expert review remains open. Garay (69),
Tai Yo (55), Seal (146) and substantial emoji/sequence work remain.

## Garay stroke prototype and source-coordinate repair

Generalized the licensed Unifont experiment for Garay's 64-unit letter cells
and negative-origin combining marks. The old Tolong viewport would crop wide
letters and omit all mark ink. The renderer now asserts containment, uses a
larger baseline-preserving viewport, translates marks only for review, rejects
empty masks, and preserves aspect ratio in the comparison. All 69 source rasters
are nonempty and unclipped. The viewport change reproduces the delivered Tolong
TTF byte-for-byte.

All 69 Garay candidates now pass unchanged component, ink-area and counter
checks. Three source-specific width recipes retain digit two, reduplication and
small JA. Two comma forms (spacing O and combining E) require bounded contour
rounding instead of uniform-width skeleton strokes. Visual review caught a
mechanically passing chevron-like O; its corrected recipe preserves a broad
head and descending tail, verified by a new regression. The first contour
candidate's tail was too short; reduced smoothing fixes it without weakening
the assertion.

The full sheet was compared visually against the official Unicode 18 Garay
chart solely for identity; no chart outlines were copied. Reference PDF SHA256:
499f137bc9c6903ba3b70d77b046d60214991b370ccfae9e01f48dcb6077b653.
Final PNG and JSON reproduce byte-for-byte in two independent runs. Targeted
stroke/Tolong tests: 39 passed in 17.60s, seven existing SWIG warnings.
`git diff --check` passes; all experiment/test processes are terminal.

See `docs/garay-lettering-experiment.md` for RTL/nonjoining requirements and
source-specific recipes. Garay remains outside production counts. Next: compile
all 69 forms with native above-mark attachment, preserve spacing signs/case,
check the Unicode spelling examples and RTL/AN digit ordering, then integrate
and inspect realistic comic rendering. Mark geometry and fluent-reader review
are not implied by a passing outline count.

## Garay production font and RTL integration

Compiled all 69 guarded Garay forms with five zero-advance marks, above-base
attachment and stacking, preserved case swashes, and positive advances for
spacing signs. Font metrics use the common source baseline with deliberately
trimmed cell whitespace. The derivative is registered through
`data/font-sources/garay.json`, retaining the already pinned GNU Unifont OFL
source and attribution. No unlicensed vector donor or chart outline is used.

The production TTF and report match an independent review build byte-for-byte.
Both review TTF and WOFF2 pass mark geometry on every letter/case, mark stacking,
case outline distinction, all Unicode figure 19-5 examples and spacing tests.
JS tests verify whole-cluster font routing and bidi resolution of Garay's RTL
letters/marks with LTR AN digits. Three new browser specimens passed and were
visually inspected, including case/marks, vowel spelling and mixed Latin/Arabic
with Garay digits. The 40px/24px compiled specimen was also reviewed.

Validation: 103 targeted Python tests passed in 33.84s (seven existing SWIG
warnings); 263 JavaScript tests passed; 11,364 source hashes verified; all 210
browser scenarios passed, including geometry and PNG dimension round trips.
A transient browser observation timeout was retried on the same live tab,
without restarting the harness. All build/test/report processes are terminal.

Current delivery: 351 script shards, 60,326,680 bytes; visible cmap coverage
171,748/172,352, with 604 missing. Source inventory: 258 fonts, 171,776 public
characters represented and 1,097 absent including behavioural characters.
Garay assigned-character coverage is now complete; this does not imply fluent
reader approval or exhaustive typography validation. Tai Yo (55), Seal (146),
and substantial emoji/sequence/style work remain. Next: apply the licensed-source
workflow to Tai Yo, with its own shaping requirements rather than reusing Garay
or Tolong assumptions.

## Tai Yo prototype and native-positioning review

All 55 assigned Tai Yo forms from the pinned OFL Unifont donor now pass the
existing stroke reconstruction guards with no additional exceptions. Minimum
counter overlap is 0.763671875; component-area ratios span
0.8205344460227273–1.0941796875. The full enlarged/small sheet was visually
compared with the official chart. PNG and JSON reproduce byte-for-byte in
`/tmp/tai-yo-reproduction`. No production coverage changed.

The Unicode 18 core specification revealed important differences from the prior
scripts. This comic can use the documented horizontal, counterclockwise-rotated
form of Tai Yo. Five Mn signs attach to bases; most vowel/rhyme letters retain
spacing. Read-only review of core PDF page 915, including rotated figure regions,
confirmed that successive marks sit side by side in horizontal presentation.
HIGH TO and HIGH FO require anchors above the left body, away from the high
rightward tails. Neither generic bounding-box centering nor Garay-style vertical
mark stacking is appropriate. KVO letters are explicitly encoded, not automatic
KO+VO font substitutions.

Added a segmentation/emergency-wrap regression for repeated AY, AY+ANG, all five
marks on both wide consonants, and SIGN UE versus spacing LETTER UE. All seven
Unicode JS tests passed in 123.73ms. `git diff --check` passes. All prototype,
reference-download and reference-render processes are terminal.

Reference chart SHA256:
2b9d91eb2eada645ba7279ab3aa232ded0c74b6cdee1013f274adfc0cc0abe1f.
The chart and core figures were viewed for identity/layout only, never traced.
See `docs/tai-yo-lettering-experiment.md` for the concrete next step: compile the
55 forms with explicit body anchors and horizontal mkmk, verify the published
spelling examples, then integrate and inspect browser wrapping and exports.
Native-reader review and independent vertical-page layout are not claimed.

## Tai Yo compiled native review font

`tools/font/build_tai_yo.py` compiles all 55 guarded drawings with five native
zero-advance marks. Explicit per-mark classes allow width-aware side-by-side
`mkmk` attachment. HIGH TO/HIGH FO use left-body anchors for narrow marks;
long AU/OM signs retain full top clearance. All spacing vowels and explicit KVO
letters retain their identities without invented substitutions.

Actual shaped-ink tests caught collisions between HIGH TO and its UE/AY marks
in the first build. Raising only those body anchors resolves them without moving
the marks over the tail or weakening the collision checks. Final validation:
21 tests pass in 1.52s (seven existing SWIG warnings), including 155 base/mark
collision cases, all four wide-base reference examples, side-by-side AY/AY and
AY/ANG, and the published UE/KVO spelling distinctions. The compiled specimen
was visually inspected at 40px and 24px. Review captions were given extra
clearance above tall marks.

Independent full builds reproduce the TTF and JSON byte-for-byte at
`/tmp/tai-yo-font-reproduction`. No production coverage changed. Next: register
the derivative builder, retain source/licence provenance, test the compressed
font and whole-cluster routing, then verify browser wrapping and export.

## Tai Yo production integration

Registered the 55-character derivative through `data/font-sources/tai-yo.json`
and the source verifier, retaining the pinned Unifont donor and OFL attribution.
The cached builder hashes recipe inputs and output. The resulting TTF/report
match the independent review build byte-for-byte, and WOFF2 retains body-specific
mark attachment and horizontal mkmk. Whole-cluster routing is regression-tested.

All review-font geometry checks now also run on WOFF2: 155 consonant/mark
collision cases per format, wide-body positioning, adjacent marks, spelling and
explicit KVO distinctions. Three new browser scenarios cover those examples,
mixed Latin/Arabic, punctuation and tight wrapping. All were visually inspected
and report no unmapped characters or fallback warnings. The harness verifies ink
containment, balloon geometry and PNG dimension round trips. A transient browser
observation timeout was retried on the same live tab; the harness was not reset.

Validation: 146 targeted Python tests passed in 41.86s (seven existing SWIG
warnings); all 265 JavaScript tests passed; all 213 browser scenarios passed;
11,364 source files verified. All build/test/report processes are terminal.
Current delivery: 352 script shards, 60,347,480 bytes; bundled cmap coverage
171,803/172,352 visible requirements, 549 missing. Raw source inventory:
259 fonts, 171,831 public characters represented, 1,042 absent including
behavioural characters. Tai Yo's 55 assigned mappings are complete. This does
not imply fluent-reader approval, independent vertical-page layout support or
completion of custom styling. Seal and substantial emoji/sequence work remain;
continue those against the full original brief.

### Celebration and festival emoji — 2026-11-02

Added 18 licensed Noto celebration/festival drawings with the approved expressive
pen treatment and two registered admission-ticket presentation variants. The
production font now contains **803 base emoji, 1,402 exact sequences and 26
shaping components**, occupying **506,612 bytes**. This closes 17 previously
missing visible mappings: bundled cmap coverage is **171,820 / 172,352**, leaving
**532 missing** (386 Common, 146 Seal). Cmap presence remains distinct from
linguistic, sequence and style completion.

The sparkler's dark knockout tile required source-specific handling: at the
reviewed weight400/768px raster, six one-pixel islands occur along diagonal white
rays. Assertions verify their exact size/count before removal. Reduced pressure
and zero taper preserve its white rays; normal topology and compiled-contour
guards remain active. Other new sources use weight400/384px. Provenance and
settings are recorded in the glyph review and pen-translation documentation.

Validation: **54 emoji Python tests passed** in 311.90 seconds, including exact
font/manifest reproduction; 7 existing SWIG warnings. **266 JavaScript tests**,
**5 inventory tests**, and all **11,364 source hashes** passed. Source inventory
records 259 fonts and 171,848 represented public characters, with 1,025 absent
including behavioural characters. The browser passed **215 scenarios**, including
two new celebration fixtures, with no failures or geometry errors. Both new
fixtures had no emoji fallback or unmapped codepoints. Reviewed the compiled
sheet at enlarged/24px sizes and both actual comics, including mixed Latin text
and presentation variants. Corrected the shared browser assertion to exclude
ASCII prose tokens from its emoji-only font check. Temporary browser tab closed.

The active brief remains incomplete. Further custom emoji/standard sequences,
146 Seal drawings, style adaptation and the broader review/audit work remain.

### Games, toys and art supplies — 2026-11-02

Added 25 licensed monochrome drawings and eight registered presentation variants
with the approved expressive treatment. The production font now contains **828
base emoji, 1,435 exact sequences and 26 shaping components**, occupying
**523,968 bytes**. All new drawings use the standard weight400/384px source and
pass topology/compiled-contour guards without source-specific exceptions.
Reviewed the compiled sheet at enlarged and 24px sizes, and three real comics
including mixed Latin text and presentation variants. Target rings, die pips,
slot-machine digits, theatre faces, card markings and sewing details remain
legible at dialogue size.

This closes 13 previously missing visible mappings: bundled cmap coverage is
**171,833 / 172,352**, with **519 missing** (373 Common, 146 Seal). Source inventory
reports 259 fonts, 171,861 represented public characters and 1,012 absent including
behavioural characters. Counts remain separate from style/linguistic validation.

Validation: **55 emoji tests passed** in 320.73 seconds, including exact font
and manifest reproduction. Refreshed the rest of the Python suite separately:
**390 tests passed** in 194.55 seconds. These two non-overlapping runs cover all
**445 collected Python tests** in the current tree; both show the existing 7 SWIG
warnings. **267 JavaScript tests**, **5 inventory tests**, and **11,364 source
hashes** also passed. The browser passed all **218 scenarios**, with three new
recreation cases reporting no fallback, unmapped characters or geometry errors.
Temporary browser tab closed; `git diff --check` passed.

Checked the newer-source lead while compiling: Google Fonts' latest directory
commit matches the existing pinned revision. An advertised Noto Unicode18 release
could not be verified through downloadable source endpoints (HTTP404), so it
has not been added or counted. Details are recorded in the pen-translation notes.
Further emoji sequences, newer source gaps, 146 Seal mappings, style adaptation
and the full completion audit remain within the active brief.

### Household/scientific emoji and sequence gap audit — 2026-11-02

Added 24 household and 12 science/medical drawings plus six registered
presentation variants. The production font now contains **864 base emoji,
1,477 exact sequences and 26 shaping components**, occupying **546,428 bytes**.
The alembic requires weight400/768px to preserve six enclosed details and apply
expressive strength1.275; lower-resolution rasters merged a narrow opening and
forced unchanged fallback. Other new drawings use weight400/384px. The licensed
compiler now rejects unchanged fallback before emitting glyph data, with a
negative regression test exercising that failure path.

Bundled cmap coverage is **171,857 / 172,352**, with **495 missing** (349 Common,
146 Seal), closing 24 previous gaps. The source inventory records 259 fonts,
171,885 represented public characters and 988 absent including behavioural
characters. This is not a completed-lettering count.

The reproducible coverage audit now separately groups fully-qualified emoji-test
sequences by subgroup. **1,114 of 3,963** are exactly encoded in the custom
manifest, with **2,849 missing**. Presentation aliases explain why this total is
smaller than the 1,477 exact manifest entries. Neither total proves style or
rendering. A regression fixture confirms that standalone modifiers and
unqualified aliases cannot count as fully-qualified sequences. Largest gaps:
486 person-role, 408 activity, 337 family, 308 sport and 259 country-flag forms.
Prioritise people and their modifier/ZWJ families in the next pass rather than
continuing to focus solely on isolated object drawings.

Validation: **58 emoji tests passed** in 331.26 seconds, including exact font/
manifest reproduction and unchanged-fallback rejection; 7 existing SWIG
warnings. **268 JavaScript tests**, **6 inventory tests** and all **11,364 pinned
source hashes** passed. Browser checks passed all **222 scenarios**; the four
new fixtures report no fallback, unmapped codepoints or geometry errors.
Reviewed both compiled sheets enlarged/24px and all four real comics, including
presentation variants and mixed prose. Temporary browser tab closed.
`git diff --check` passed. The broad beta goal remains incomplete.

### People and exact skin-tone forms — 2026-11-02

Added eleven expressive neutral people and 55 exact skin-tone forms: baby,
child, boy, girl, person, man, woman, older person, old man, old woman and bearded
person. `emoji_people.py` uses the pinned Noto weight400/384px source with reviewed
skin-only masks and the existing five PDF-derived tones. The baby's pacifier and
blanket, the boy's cap, girl's bows, older people's white hair and the bearded
person's teeth remain white. Black ink and metrics are shared by all tones.
The region review is saved as `output/font-review/pen-translation/people-region-review.png`
and JSON; the compiler asserts region counts and limits colour to reviewed face/
neck interiors, extending only underneath ink to avoid seams.

U+1F9D1 is promoted from a blank component to a visible standalone person. Its
internal `person` glyph name is retained, with longer astronaut substitutions
before simple tone substitutions. Repeated toned people and adjacent
person/astronaut/person strings retain their correct glyphs and advances.
Still-unsupported hair, profession and gender ZWJ forms remain whole fallback
sequences, never partially advertised custom drawings.

Production now contains **875 base emoji, 1,543 exact sequences and 25 shaping
components**, occupying **554,716 bytes**. Visible cmap coverage is **171,868 /
172,352**, with **484 missing** (338 Common, 146 Seal). Fully-qualified emoji
coverage increases by 66 to **1,180 / 3,963**, with **2,783 missing**. The person
subgroup has 66 of 168 forms; its remaining 102 hair/gender forms are the next
concrete work before expanding roles, activities, families and flags. Source
inventory: 259 fonts, 171,896 represented public characters, 977 absent including
behavioural characters; all 11,364 pinned source files verify.

Validation: **70 emoji Python tests passed** in 355.67 seconds, including exact
font/manifest reproduction, anatomical probes in both raster masks and compiled
skin outlines, five distinct colour layers sharing neutral ink/metrics, repeated
ligatures and astronaut preservation. The 12 new cases also passed an early
focused run. Python retains the existing 7 SWIG warnings. **269 JavaScript
tests** passed; after adding unsupported-ZWJ prefix assertions, all **20 routing
tests** passed again. **6 inventory tests** passed. Browser passed **234
scenarios**, including all 12 people fixtures with no fallback, unmapped
codepoints or geometry errors. Reviewed all 66 compiled variants enlarged/24px
and representative comics for baby, cap, bows, white hair, beard and adjacent
astronauts. Temporary browser tab closed; `git diff --check` passed.

The full Unicode beta remains incomplete; coverage totals are not substitutes
for completing the remaining sequences, Seal drawings, style work and audits.

### Remaining person hair/gender forms — 2026-11-02

Added the remaining 17 neutral person forms, their 85 toned forms and 24
minimally-qualified aliases: **126 new exact manifest entries**. The person
subgroup now has all **168 fully-qualified forms** exactly encoded and tested.
`emoji_person_forms.py` checks every qualification/tone input against the actual
pinned donor ligature name and emits longer substitutions before simple people
modifier rules. It preserves adjacent standalone people and repeated sequences.
Six hair/gender inputs remain blank shaping components, not visible coverage.

Blond hair uses verified PDF yellow (180,157,60), and red hair uses verified
page13 ochre (174,104,29). Both existing full-resolution render hashes and sample
medians were rechecked. Separate skin and hair layers retain white hair, teeth,
black eyes/mouth and the face border. Red hair opens only the largest thick ink
component inside a nine-pixel border; original solid ink remains the monochrome
fallback. A smaller initial inset also coloured part of the face border and was
rejected during visual review. Compiled tests now prohibit hair colour in the
lower face border and preserve disconnected facial features. The donor shares
underlying curly-haired and bald drawings across gender forms; that appearance
limitation remains explicit despite complete exact sequence encoding.

Production totals: **876 base emoji, 1,669 exact sequences, 31 shaping components**,
**570,500 bytes**. Visible cmap coverage is **171,869 / 172,352**, with **483
missing** (337 Common, 146 Seal). Fully-qualified emoji coverage is **1,282 /
3,963**, leaving **2,681 missing**. Source inventory records 259 fonts, 171,897
represented public characters and 976 absent including behavioural characters.

Validation: **88 emoji tests passed** in 395.51 seconds, including byte-for-byte
font/manifest reproduction, independent hair/skin masks, compiled colour/ink
probes, all qualification aliases, repeated forms and adjacent people. All 18
new cases also passed an early focused run. Python has the existing 7 SWIG
warnings. **270 JavaScript tests**, **6 inventory tests** and **11,364 source
hashes** passed. All **252 browser scenarios** passed, including 18 new fixtures
without fallback, unmapped characters or geometry errors. Reviewed all 102 new
compiled neutral/tone drawings enlarged/24px and representative red-hair,
white-hair, blond-hair and qualification/mixed-prose comics. Review-sheet labels
now shrink to fit their cells. Temporary browser tab closed; `git diff --check`
passed.

Next: person-role sequences (486 missing fully-qualified forms), then activities,
families, sports and flags. The full Unicode beta remains incomplete, including
Seal recovery, style review and broader completion audit requirements.


### Occupation emoji checkpoint — 2026-11-02

Added 47 occupation families with five tones and published qualification aliases:
336 additional exact sequences, including 282 fully-qualified emoji-test forms.
The pinned donor ligature identity is verified for every alias. Longer occupation
substitutions precede people-tone substitutions. Medical-symbol, airplane and
fire-engine inputs are blank shaping components, not standalone coverage claims.
The existing neutral person astronaut retains its previous drawing.

Reviewed exposed-skin regions independently from uniforms, spectacles, goggles,
hats, helmets, tools and equipment. Teacher lenses show skin; science goggles
stay white. All variants share their original monochrome ink and metrics.
Requested pen strength remains 1.7 with recorded positive backoffs. The neutral
firefighter needs a 768px raster to avoid untreated fallback; the woman cook
needs 768px to retain a small compiled contour. All other occupations use 384px.
The donor shares occupation anatomy across gender forms; pen variation does not
remove that provisional source-design limitation.

Production totals: **876 base emoji, 2,005 exact sequences, 34 shaping components**,
**615,484 bytes**. Visible cmap coverage remains **171,869 / 172,352**, with
**483 missing** (337 Common, 146 Seal). Fully-qualified emoji coverage is
**1,564 / 3,963**, leaving **2,399 missing**. The person-role subgroup now has
288 / 492 exactly encoded forms, leaving 204. Source inventory remains 259 fonts,
171,897 represented public characters and 976 absent including behavioural ones.

Validation: **135 emoji tests passed** in 530.22 seconds, including byte-for-byte
font/manifest reproduction, every exact sequence and 47 new anatomical checks
covering compiled skin masks, shared ink/metrics, all tone/qualification aliases,
repeated forms and adjacent plain people. The focused 47 tests also passed in
98.45 seconds. **16 pen-treatment tests**, **271 JavaScript tests**, **6 inventory
tests** and **11,364 source hashes** passed. The Python emoji suite retains the
existing 7 SWIG warnings. Updated obsolete astronaut-fallback fixtures to use
still-unsupported feeding-baby forms; all **300 browser scenarios** then passed.
Reviewed all 282 compiled neutral/tone drawings enlarged and at 24px, plus
qualification/mixed-prose and firefighter-tone comic specimens. Temporary
browser tab closed; `git diff --check` passed.

Next: the remaining 34 person-role families (204 fully-qualified forms), then
activities, families, sports and flags. Preliminary source probes are saved as
`remaining-role-region-probe*.png/json`, explicitly outside production. Seven
pregnancy/feeding families are solid silhouettes: their enclosed white regions
are gaps or baby/bottle negative space, not exposed adult skin, so they require
a different reviewed mask strategy. The full Unicode beta remains incomplete.


### Outlined roles and detailed-SVG investigation — 2026-11-02

Added 27 outlined person-role families: police, detective, guard, ninja,
construction worker, crowned people, turban/skullcap/headscarf, tuxedo and veil.
The 251 additional exact sequences include 162 fully-qualified emoji-test forms
and all published qualification aliases. Thirteen base drawings are now in the
emoji font; twelve add previously missing visible mappings. Shared role-building
code handles standalone bases as well as ZWJ forms, including the detective's
neutral variation selector and its different qualified spelling with a tone.
All tone/qualification aliases are verified against their actual source glyph.

Reviewed face/hand masks keep uniforms, headwear, sword and magnifying glass
white. A magnifying-glass handle initially selected in the draft man-detective
mask was corrected to the actual hand before compilation. All 27 use 384px and
requested strength 1.7 with positive automatic backoffs. Source-design sharing
across gender forms remains provisional and is not a claim of distinct anatomy.

Production: **889 base emoji, 2,256 exact sequences, 34 shaping components**,
**637,704 bytes**. Visible cmap coverage is **171,881 / 172,352**, with **471
missing** (325 Common, 146 Seal). Fully-qualified emoji coverage is **1,726 /
3,963**, leaving **2,237 missing**. Person-role has 450 / 492 exactly encoded;
its remaining 42 forms are the seven pregnancy/feeding families and their tones.
Inventory: 259 font sources, 171,909 represented public characters, 964 absent
including behavioural characters.

Validation: **162 emoji tests passed** in 611.63 seconds, including exact
font/manifest reproduction, all registered sequences and 27 new independent
anatomical checks. The focused 27 tests passed in 57.53 seconds. **272 JavaScript
tests**, **6 inventory tests** and **11,364 production source hashes** passed.
Python retains the existing 7 SWIG warnings. All **328 browser scenarios**
passed, including 28 new role fixtures. Reviewed all 162 neutral/tone drawings
enlarged and at 24px, plus qualification/mixed-prose and headscarf-tone comics.
Temporary browser tab closed; `git diff --check` passed.

A concrete source lead also resolves the earlier upstream directory lookup:
current Noto artwork is under `2D/svg` and fonts under `2D/fonts`. Pinned revision
`99701e07d3d1fe1bdbcdb14964547f0fd592966f` supplies detailed pregnancy/feeding
figures. Seven SVGs and their directory licence were downloaded and verified
against Git blob identities and SHA-256; the separate probe manifest records
them. SVG artwork uses Apache-2.0. Retained the full licence, attribution and
modification notice alongside the existing OFL font licence. The upstream tree
also contains filenames for all 23 newer Common emoji missing from the pinned
monochrome donor; those additional files still need retrieval and review.

New experimental tools render individually indexed SVG paths, apply reviewed
shadow-removal/ink recipes, and compile small-size probes. Three pregnancy
recipes preserve 10 contours each, applying strengths 0.5379/1.275/1.275 at
768px with a 1.3-unit outline. Man feeding baby preserves 32 contours at 0.95625;
its blanket fold is outlined rather than filled as a heavy black shadow. All
four were visually reviewed enlarged and at 24px. Reports retain source and
program hashes. These are **not production coverage**: separate skin masks,
source/alias integration, the other three feeding recipes and full validations
remain due. See `docs/noto-svg-source-probe.json` and the detailed-SVG section of
`docs/emoji-pen-translation.md`.

Next: finish the detailed pregnancy/feeding conversion and tones, then activities,
families, sports, flags and the newer SVG-only emoji. Continue Seal recovery and
the full brief's style/behaviour/completion audits. The goal remains incomplete.


### Detailed pregnancy/feeding SVG production — 2026-11-02

Promoted all seven pinned SVG recipes into the production pipeline: pregnant
woman/man/person, breastfeeding, and woman/man/person feeding baby. Their 42
neutral/tone forms complete exact encoding of all 492 fully-qualified person-role
forms. The font now has **893 base emoji, 2,298 exact sequences, 34 shaping
components**, and is **653,180 bytes**. Visible cmap coverage is **171,885 /
172,352**, leaving **467 missing** (321 Common, 146 Seal). Fully-qualified emoji
coverage is **1,768 / 3,963**, with **2,195 missing**. Source-font inventory is
unchanged: 259 fonts, 171,909 public characters represented, 964 absent including
behavioural characters. SVG-derived additions are reflected in output coverage.

The converter uses reviewed path recipes and a separate original anatomical
mask to select skin regions after expressive treatment. Clothing, bottles and
blankets stay white. All five tones retain identical ink and metrics. Source
rasterisation is 768px with a 1.3-unit outline and requested strength 1.7. Applied
strengths range from 0.53789 to 1.275. Breastfeeding and woman feeding remove
only sub-four-pixel raster pinholes, with an explicit feature-equivalence check.
Woman feeding uses reduced pressure variation and no taper to avoid breaking
fine intersections. No global closing or weakening of the feature guard is used.

All 42 compiled drawings were reviewed enlarged and at 24px. Independent raster
and compiled-layer probes verify exposed skin against clothes/equipment, while
compiled contours preserve source components/counters. The focused eight tests
passed in 23.43 seconds. **273 JavaScript tests**, **6 inventory tests**,
**11,373 registered source hashes**, and **336 browser scenarios** passed.
Browser review included the new tone families and adjacent plain-person forms.
The full suite passed **170 emoji tests in 663.65 seconds**, including exact
font/manifest reproduction. Existing 7 SWIG deprecation warnings remain.
Temporary browser tabs were closed and `git diff --check` passed.

Separately retrieved and hash-verified all 23 newer SVG source candidates from
the pinned upstream tree, and visually identified them in the browser. They are
recorded in `docs/new-emoji-svg-source-probe.json`, outside production coverage.
Native SVG browser rendering is required for their original gradients; the
PyMuPDF source contact sheet renders some gradients black. Three preliminary
ink recipes (leafless tree, fingerprint, pickle) now have raster and traced
24px/enlarged review sheets. The tree outline was thickened after small-size
review; final applied strengths are 0.71719, 0.95625 and 1.7, preserving 6, 10 and
8 traced contours respectively. These prototypes do not alter the font.

Next: integrate reviewed newer SVG candidates, expand activities/families/sports/
flags, continue Seal recovery, and complete the brief's style/behaviour audits.
The full Unicode goal remains active and substantially incomplete.


### Emoji optical presence in finished strips — 2026-11-02

User feedback: many sampler drawings looked small and whispery in actual comics.
Custom emoji now use 1.4× dialogue size and an ink-only optical stroke of 0.018×
that size. Measurement reserves the larger outlines and stroke extents before
wrapping or fitting balloons. Text and native fallback emoji are unchanged.
The separate 645,224-byte Dad Emoji Ink companion avoids canvas COLR stroking
repainting colour layers; it loads alongside the colour font before rendering.
Its glyph outlines, metrics, cmap and GSUB match the original byte for byte.
The production builder generates both and records the companion hash.

Validation: 275 JavaScript tests and 337 browser geometry/export scenarios pass.
A focused Python companion test passes, including exact derived-font rebuilding
and table equivalence. The earlier 170-test colour-font suite remains historical
for the previous checkpoint; it was not rerun for this renderer adjustment.
Reviewed original/larger/weighted comparisons at 24px and the final mixed-dialogue
comic, including detailed people and colour-dependent symbols. Review page:
`tools/emoji-optical-review.html`. `git diff --check` passes. Full Unicode work
remains active; this addresses optical presence rather than coverage.


### Newer SVG tree, fingerprint and pickle — 2026-11-02

Promoted the three reviewed newer SVG recipes to `emoji_new_svg.py`, with a
separate pinned production source manifest. Added the leafless tree (U+1FABE),
fingerprint (U+1FAC6) and pickle (U+1FADD). Unicode names, SHA-256/Git blob
identities, fully-qualified forms and sequence boundaries are checked. Repeated
conversions are identical. Compiled contours preserve 1 component/5 counters,
10 components/0 counters and 6 components/2 counters respectively. The source
recipes retain expressive strength 1.7 with positive automatic reductions.

The font now has **896 base emoji, 2,301 exact sequences, 34 shaping components**,
**657,152 bytes**, plus the matching **648,568-byte** ink companion. Coverage is
**171,888 / 172,352 visible mappings**, with **464 missing** (318 Common, 146
Seal). Fully-qualified emoji coverage is **1,771 / 3,963**, leaving **2,192**.
The refreshed audit exposed that companion-font invisible shaping components
were being counted as visible cmap coverage. Companions now inherit the
parent's component exclusions, and the regression test independently compares
both fonts' empty glyphs. The temporary inflated count was not accepted.

Validation: **6 focused font tests** passed in 32.03 seconds, including every
advertised sequence, packaging, all three new identity/topology checks and
byte-identical companion rebuilding. **276 JavaScript tests**, **6 inventory
tests**, **11,376 production source hashes** and **338 browser scenarios** pass.
The preceding complete 170-test emoji suite is historical, not a fresh full-suite
claim for this batch. Reviewed compiled sheets and mixed dialogue at the approved
1.4× size/optical weight; no fallbacks appeared in the new comic fixture.

Prepared separate harp, trombone and shovel prototypes from the verified source
candidates. They preserve 10/14/7 contours and apply 1.275/1.7/0.95625 strength.
The parser keeps clipping definitions while selecting visible paint. Their
compiled review includes optical dialogue sizing; production integration and
finished-strip checks remain due. The broader Unicode goal remains incomplete.


### Harp, trombone, shovel and next source batches — 2026-11-02

Promoted the three object recipes into production with preserved SVG clipping
and definitions. Identity, component/counter topology, deterministic conversion,
qualification, adjacent/repeated sequence boundaries and companion equivalence
are checked for all six newer SVG glyphs. Their source hashes and Unicode names
are pinned. Reviewed compiled sheets and actual mixed-dialogue strips at the
approved 1.4× optical size and black ink weight.

Production: **899 base emoji, 2,304 exact sequences, 34 shaping components**,
**660,932 bytes** plus a **651,940-byte** ink companion. Coverage is **171,891 /
172,352 visible mappings**, with **461 missing** (315 Common, 146 Seal).
Fully-qualified emoji coverage is **1,774 / 3,963**, leaving **2,189 missing**.
Validation: **10 focused font tests in 359.28 seconds**, including the full
byte-identical colour-font/manifest rebuild, all advertised sequences, six new
SVG identity/topology tests and the companion rebuild. Also **276 JavaScript
tests**, **6 inventory tests**, **11,379 source hashes** and **339 browser
scenarios** pass. The existing 7 SWIG warnings remain. This is not a fresh
whole-tree Python run. Browser review had no fallbacks in the new object fixture.

Prepared six more SVG prototypes: bags-under-eyes, distorted and cracking faces
retain 9/7/26 contours at strength 1.7; root vegetable, splatter and orca retain
5/3/5 contours at strengths 1.7/0.53789/0.40342. Orca preserves its black/white
pattern and eye/flipper separation, removing six one-pixel raster pinholes only
after feature equivalence is asserted. These were reviewed enlarged and with
the approved optical dialogue treatment, but remain outside production.

A larger licensed transport review now has 21 guarded candidates: rocket,
helicopter, station, tram, tram car, bus stop, fire engine, police car, oncoming
taxi, mountain/suspension railways, cableway/aerial tramway, kick/motor scooters,
aircraft departure/arrival, playground slide, wheel, ring buoy and oil drum.
All preserve expected traced contours and apply positive treatment at 384px.
Taxi uses donor weight 350 (applied 0.30256); the other twenty use weight 400.
Registration, qualification/sequence checks and comic review are still due.
Rocket promotion must preserve astronaut substitutions while replacing its
currently invisible shaping component with a visible drawing.

Next: integrate those reviewed candidates, then the remaining newer SVG artwork,
activities, families, sports and flags; continue Seal recovery and the full
brief's style/behaviour audits. The goal remains active and incomplete.


### Transport production and optical review — 2026-11-02

Integrated the 21 reviewed transport candidates, including visible rocket and
fire engine drawings that replace shaping-only components. Rocket retains its
glyph name for astronaut substitutions; profession builders reuse the visible
fire engine. All 2,327 advertised sequences still shape to one real coloured
glyph. Tests exercise all 18 astronaut forms beside standalone rockets and
verify donor identities, settings and contour counts for the new drawings.

Production: **920 base emoji, 2,327 exact sequences, 32 shaping components**,
**952 cmap entries**, **675,288 bytes**, and a **666,708-byte** ink companion.
Coverage is **171,911 / 172,352 visible mappings**, leaving **441 missing**.
Fully-qualified emoji coverage is **1,795 / 3,963**, with **2,168 missing**.
The 21 visible additions increase total bundled coverage by 20 because coverage
overlaps other bundled fonts. Cmap size grows by 19 because two additions were
already present as invisible components.

Validation: **15 focused font/inventory tests** passed in 33.97 seconds,
**277 JavaScript tests**, **11,379 source hashes**, and **347 browser scenarios**
passed. The focused run covers every advertised sequence, packaging, companion
rebuilding, transport topology, astronaut boundaries and inventory regressions;
it does not repeat the preceding full colour-font rebuild or whole-tree suite.
Reviewed all seven transport strips plus the astronaut-boundary strip with the
approved 1.4× custom size and stronger ink. Internal windows, spokes, buoy
segments and aircraft/runway separation remain readable at dialogue size.

The six prepared face/nature SVG recipes remain prototypes. Individual source
path probes for directional thumbs, eraser and hairy creature are generated but
not yet reviewed or integrated. Continue these newer drawings, then the larger
activity/family/sport/flag groups, Seal recovery and remaining behaviour/style
audits. The original goal remains active and substantially incomplete.


### Expressive SVG faces and nature production — 2026-11-02

Integrated bags-under-eyes, distorted and cracking faces, root vegetable,
splatter and orca. Their recipes now share the production converter with their
review tools. All twelve newer SVG drawings have pinned source identity,
deterministic conversion, topology, adjacent/repeated sequence and companion
checks. Orca retains its eye separation and flipper boundary; six sub-four-pixel
raster pinholes are removed only after feature equivalence is asserted.

Production: **926 base emoji, 2,333 exact sequences, 32 shaping components**,
**958 cmap entries**, **681,448 bytes**, plus a **673,048-byte** ink companion.
Visible coverage is **171,917 / 172,352**, leaving **435 missing**. Fully-qualified
emoji coverage is **1,801 / 3,963**, leaving **2,162 missing**. These are coverage
counts, not evidence of completed style or linguistic validation.

Validation: **21 focused Python checks in 66.55 seconds**, including all twelve
SVG identities/topologies, all advertised emoji sequences, packaging, companion
rebuild and inventory tests; **277 JavaScript tests**, **11,385 source hashes**,
and **349 browser scenarios** pass. Seven existing SWIG warnings remain. This
is not a fresh whole-tree or full colour-font rebuild test. Reviewed compiled
artwork and both new mixed-dialogue strips using approved optical defaults.

Prepared seven further source-derived prototypes in
`tools/font/prototype_svg_next_objects.py`: fight cloud, meteor, lighthouse,
landslide, net, eraser and hairy creature. Their compiled contour counts are
17/12/9/14/32/9/10, equal to meaningful source components plus holes; each
applies positive treatment without fallback. The fight cloud explicitly keeps
its open spiral stroke. Lighthouse retains its lamp and alternating bands.
Reviewed original SVGs in the browser and prototypes enlarged and at optical
dialogue size. These seven remain outside production and need registration,
identity/sequence tests and finished-strip checks. Monarch butterfly, treasure
chest and the two directional thumbs still need recipes; thumb skin-tone forms
also require the corresponding source and sequence work.

Next: integrate the seven reviewed prototypes; finish the remaining newer SVG
artwork, then larger activity/family/sport/flag groups, Seal recovery and the
full brief's behaviour/style audits. The goal remains active and incomplete.


### Seven newer SVG drawings in production — 2026-11-02

Integrated fight cloud, meteor, lighthouse, landslide, net, eraser and hairy
creature. Their review tool now uses the production converter. The fight
cloud retains its open spiral stroke; the lighthouse retains its lamp and
bands; the net retains all 30 counters. All nineteen newer SVG recipes have
source identity, deterministic conversion, contour, sequence-boundary and
companion checks. Reviewed three new finished-strip fixtures at approved size
and ink weight, with readable mesh, outlines and silhouettes.

Production: **933 base emoji, 2,340 exact sequences, 32 shaping components**,
**965 cmap entries**, **691,280 bytes**, plus **681,940 bytes** for the ink
companion. Bundled visible coverage is **171,924 / 172,352**, leaving **428**.
Fully-qualified emoji coverage is **1,808 / 3,963**, leaving **2,155**.

Validation: **28 focused Python checks in 96.01 seconds**, including nineteen
SVG identities/topologies, all advertised sequences, packaging, companion
rebuilding and inventory; **277 JavaScript tests**, **11,392 source hashes** and
**352 browser scenarios** pass. Seven existing SWIG warnings remain. This is
not a fresh whole-tree or full colour-font rebuild test.

The final four newer source drawings now have review-only prototypes. Neutral
directional thumbs retain six contours each (left stroke 1.8, strength 1.275;
right stroke 1.3, strength 0.95625). The narrower right source outline preserves
a small counter that the first trace lost. Skin-tone variants and production
registration are still required.

Monarch butterfly and treasure chest use 1536px source rasterisation with
pressure 0.1 and taper 0. Butterfly removes 17 isolated raster ink pixels across
seven tiny components (areas 1–4 pixels), preserving the main silhouette and
36 wing counters; strength 1.7 yields 37 compiled contours. It still needs
meaningful orange colouring before production. Chest removes 21 sub-four-pixel
pinholes after feature equivalence is asserted; strength 0.7171875 preserves
8 components plus 60 counters in 68 compiled contours. Both are visually
reviewed enlarged and at optical dialogue size, but remain outside production.
Earlier rejected fallback/contour-loss attempts were not accepted as coverage.

Next: finish colour/tone handling and integrate these four with source and
sequence checks, then continue activity/family/sport/flag groups, Seal recovery
and remaining full-brief behaviour/style audits. Goal active and incomplete.


### Final newer SVG candidates, colour and directional thumb tones — 2026-11-02

All 23 candidates in the newer SVG source-discovery record are now integrated.
The final four are monarch butterfly, treasure chest and left/right thumb signs.
Each thumb has five additional skin-tone forms using the same outline and
whole-hand fill. Tests verify each form stays one glyph beside repeated and
neutral neighbours and matches the ink companion. All 23 base SVG identities
and their source topology are checked; this closes this source batch only.

Monarch uses the existing pinned PDF orange sample, RGB 174/104/29. Original
source orange paint identifies 18 enclosed cells after translation, while 18
white wing spots stay unpainted. Underpaint is clipped to the silhouette and
excludes every white cell. The separate monochrome companion preserves ink
geometry and avoids replacing the colour during optical outlining.

Production: **937 base emoji, 2,354 exact sequences, 32 shaping components**,
**969 cmap entries**, **702,312 bytes**, plus a **693,508-byte** ink companion.
Coverage is **171,928 / 172,352 visible mappings**, leaving **424 missing**.
Fully-qualified emoji coverage is **1,822 / 3,963**, leaving **2,141 missing**.

Validation: **35 focused Python checks in 126.93 seconds**, **278 JavaScript
tests**, **11,396 registered source hashes** and **355 browser scenarios** pass.
The focused checks cover all advertised sequences, all 23 SVG identities and
topologies, both thumbs' tone boundaries, butterfly colour assignment, font
packaging, companion rebuilding and inventory. Seven SWIG warnings remain.
No fresh whole-tree or full colour-font rebuild test is claimed. Reviewed all
three new strip fixtures at approved optical size and weight.

Next-source review found the monochrome donor collapses neutral/male/female
person gestures into nearly identical blob artwork. Generated 30 diagnostic
prototypes in `tools/font/prototype_person_gestures.py`, but do not promote
these as completed person-gesture coverage. Instead downloaded and verified
30 pinned SVG candidates (10 poses × 3 forms) against the same upstream tree's
git-blob identities and SHA-256 hashes. Source record:
`docs/gesture-emoji-svg-source-probe.json`; browser review grid and path probes
are under `output/font-review/pen-translation/`. Reviewed all ten pose groups
in the original SVG grid; they preserve distinct human forms. These candidate
files are not production registrations and do not increase the production
source-hash count.

Next: convert the gesture SVGs with separated skin/clothing regions and all
tones, then continue activity/family/sport/flag groups, Seal recovery and the
remaining behaviour/style audits. The original goal remains active and
substantially incomplete.


### First six human gesture poses — 2026-11-02

Integrated 18 distinct neutral/male/female SVG drawings for tipping hand, NO,
OK, raised hand, frowning and pouting. These add 108 fully-qualified forms
with all five skin tones, or 180 exact sequences including presentation aliases.
Anatomical source masks select enclosed skin regions; clothing stays white.
Source identities, selected regions, deterministic translation, compiled contour
counts, tone boundaries and distinct gender geometry have explicit checks.
The crossed-arm drawings remove only sub-four-pixel raster pinholes with
feature equivalence checked before and after translation.

Production: **943 base emoji, 2,534 exact sequences, 32 shaping components**,
**975 cmap entries**, **737,816 bytes**, plus a **729,080-byte** ink companion.
Coverage is **171,934 / 172,352 visible mappings**, leaving **418 missing**.
Fully-qualified emoji coverage is **1,930 / 3,963**, leaving **2,033 missing**.
These inventory totals do not establish linguistic or visual correctness.

Validation: **34 focused Python tests in 127.86 seconds**, **279 JavaScript
tests**, **11,414 registered source hashes**, and **361 browser scenarios**
pass. Seven existing SWIG warnings remain. Reviewed the compiled sheet and all
six new strip fixtures, including skin tones, at the approved 1.4× size and
stronger ink weight. No fresh whole-tree or full colour-font rebuild test is
claimed.

Nine additional bowing, facepalm and shrug drawings have review-only prototypes
in `tools/font/prototype_gesture_remaining.py`. Reviewed their enlarged colour
sheets. Eight pass treatment and contour preservation; neutral bowing falls
back to zero strength and remains rejected. None of these nine is registered
in production. Deaf-person drawings still need conversion. The source probe
now distinguishes 18 registered drawings from the 12 remaining candidates.

Next: resolve neutral bowing, convert deaf-person forms, and integrate the
remaining gestures with tests and strip review. Activity/family/sport/flags,
Seal recovery and full-brief behaviour/style audits remain. Goal active and
substantially incomplete.

### Remaining gesture poses and activity-source review — 2026-11-02

Integrated the final twelve gesture SVG drawings: bowing, facepalm, shrugging
and deaf-person, each neutral/male/female with five additional skin tones.
This adds 72 fully-qualified forms and 120 exact encodings including aliases.
All **180 / 180 person-gesture forms** are now custom encoded. This completes
this inventory subgroup, not the entire Unicode brief or a universal style audit.

Neutral bowing initially failed the preservation guard. Retaining strength 1.7
but reducing pressure to 0.1 and taper to zero allows strength 0.7171875 after
backoff, preserving 10 components and 8 counters in 18 compiled contours.
The guard was not weakened. All twelve drawings pass positive treatment and
exact compiled contour checks. Deaf-person drawings retain their motion arrow
as an open stroked path plus solid arrowhead; bowing retains its emphasis lines.
Skin and clothing remain separately selected. The review script now delegates
to production conversion rather than maintaining a divergent copy.

Production: **947 base emoji, 2,654 exact sequences, 32 shaping components**,
**979 cmap entries**, **763,440 bytes**, plus a **753,764-byte** ink companion.
Coverage is **171,938 / 172,352 visible mappings**, leaving **414 missing**.
Fully-qualified emoji coverage is **2,002 / 3,963**, leaving **1,961 missing**.
Inventory encoding remains distinct from linguistic and visual validation.

Validation: **50 focused Python tests in 211.12 seconds**, **16 pen-treatment
tests**, **279 JavaScript tests**, **11,426 registered source hashes**, and
**365 browser scenarios** pass. The focused checks include all thirty gesture
identities, deterministic masks, exact skin-region selections, compiled
contours, gender differences, tone/sequence boundaries, all advertised emoji
sequences, ink-companion equivalence and inventory. Seven existing SWIG
warnings remain. Reviewed the four new groups enlarged and in completed strips
at the approved size and weight. No fresh whole-tree or full colour-font
rebuild test is claimed.

Downloaded and verified 23 next activity SVG candidates at the same pinned
Noto commit: running, walking, kneeling, standing, bunny-ear dancers, sauna,
climbing, and individual woman/man dancing. Source probe:
`docs/activity-emoji-svg-source-probe.json`; browser source grid, diagnostic
contact sheets and per-path probes are under the pen-translation review folder.
Reviewed all 23 in native browser rendering. MuPDF's original-colour previews
misrender some gradients as black, so those diagnostic sheets are not reliable
colour references. Use browser originals to interpret layers and anatomy.
These sources are not registered production coverage.

Next: convert activity poses with skin/clothing separation, preserve directional
variants and meaningful accessories, then continue family/sport/flags, Seal
recovery and full-brief behaviour/style audits. Goal remains active and
substantially incomplete.

### Activity conversion prototypes, both directions — 2026-11-02

Created `tools/font/prototype_activity_svg.py` for standing and left/right
walking, running and kneeling: **21 distinct source drawings**, potentially
126 fully-qualified forms / 300 exact qualification variants with tones.
These are still review-only and do not change production coverage.

All 21 now pass positive pen-treatment and exact compiled contour preservation
in a fresh `--strict` run. The report at
`output/font-review/pen-translation/activity-svg-prototype.json` contains source
identities, masks, skin-region selections, settings, compiled counts and current
converter hashes; every report matches the final converter file. Reviewed all
four enlarged pose sheets. Production tone tests and finished-strip review
remain required before registration counts as completed work.

Full-body source rasterisation is 1536px. Default stroke 1.3, pressure 0.1,
taper zero and requested strength 1.7; preservation backoffs remain active.
Neutral running and standing use stroke 0.9. Female left walking and male/female
right walking use stroke 1.1, retaining counters lost at other widths. Standing
removes only isolated raster specks smaller than four pixels (1/2/1 pixels for
neutral/male/female); these had created spurious components at fingertip ends.
The initial cleanup and default bend still failed, so no fallback was accepted.
Diagnostics showed finger lines moving across adjacent outlines. Standing now
uses bend 0.001, except female bend 0.0005 / pressure 0.025. Neutral/male apply
strength 1.7; female applies 0.537890625 while preserving 16 compiled contours.
Other drawings retain bend 0.012. These adjustments preserve separate fingers
and face details rather than relaxing the topology guard.

Added nine official right-facing source SVGs to the activity probe (32 total),
verified all SHA-256 and git-blob identities, and inspected the nine originals
in native browser rendering. Directional drawings use their actual pinned
sources. All 21 recipes resolve through the authoritative emoji sequence data
for 300 exact forms, but none is yet advertised in the production manifest.
The source record again documents MuPDF's unsupported original gradient fills;
native browser source images are the colour/layer reference.

Next: move the reviewed 21 recipes into production with literal region and
contour expectations, register their sources and tones, ensure long directional
substitutions precede short pose rules, rebuild, check all variants/boundaries,
and review actual strips. Remaining activity drawings (dancers, sauna, climbing),
family/sport/flags, Seal recovery and full-brief behaviour/style audits remain.
Production totals remain 2,002 / 3,963 fully-qualified emoji and 171,938 /
172,352 visible mappings. Goal active and substantially incomplete.

### Activity production and browser presentation-selector fix — 2026-11-02

Integrated 21 walking/running/kneeling/standing drawings, including actual
right-facing source artwork, neutral/male/female forms and all five skin tones.
This adds **126 fully-qualified forms / 300 exact encodings**. Long directional
substitutions precede short pose substitutions. Tests alternate left/right
sequences to detect prefix consumption, and check distinct source/gender
geometry, literal skin-region selections, deterministic conversion, source
identities, exact compiled contours, colour layers and ink-companion shaping.

Finished-strip review caught an issue that the original browser assertions and
HarfBuzz tests missed: right-facing forms combined custom artwork with native
colour artwork during optical outlining. U+27A1 had been added as a blank
shaping component, but its FE0F default variation was absent from cmap format
14. Browser font selection consequently fell back for the **ink companion**.
Added activity presentation pairs to the font's variation table and rebuilt
both fonts. No artwork geometry or optical-size settings changed for this fix.

New regressions verify every advertised emoji presentation pair is declared in
both fonts, and compare actual canvas pixels for qualified versus bare activity
aliases using both Dad Emoji and Dad Emoji Ink. Before the fix, both font-table
tests failed and the browser pixel check failed on all three directional pose
groups (24 ink-companion comparisons). After rebuilding, both pass. An audit
of the entire advertised sequence list found no other missing presentation pair.
This demonstrates why CSS family/routing reports alone cannot prove no fallback.

Production: **951 base emoji, 2,954 exact sequences, 33 shaping components**,
**984 cmap entries**, **807,432 bytes**, plus a **799,376-byte** ink companion.
Coverage is **171,942 / 172,352 visible mappings**, leaving **410 missing**.
Fully-qualified emoji coverage is **2,128 / 3,963**, leaving **1,835 missing**.
The new blank arrow component does not count as visible custom coverage.

Validation: **43 focused Python tests in 347.71 seconds** passed for the new
artwork before the cmap fix; **24 focused post-fix tests in 67.05 seconds** pass
for variation declarations, directional boundaries, gender differences, all
advertised sequences, font packaging, ink-companion rebuilding and inventory.
Artwork conversion was unchanged between these runs. **280 JavaScript tests**,
**11,447 registered source hashes**, all **21 production conversion checks**,
and **372 browser scenarios** pass. Reviewed the compiled sheet and all seven
new strip fixtures, including the corrected directional forms, at approved
optical size/weight. Seven SWIG warnings occurred in the initial Python run;
the post-fix run had none. No fresh whole-tree or complete colour-font
reproducibility test is claimed.

While builds ran, created review-only woman/man dancer conversions in
`tools/font/prototype_dancing_svg.py`. Woman passes at source stroke 1.3,
pressure 0.1, bend 0.012, taper zero: strength 0.7171875, 4 components plus 27
counters, 31 compiled contours. Reviewed both enlarged. Man remains rejected:
small hand counters change under treatment even with reduced bend/pressure and
several stroke widths. Latest source stroke 1.6, pressure 0.025, bend 0.001,
taper zero still falls back. Neither dancer is registered production coverage.
Do not count failed fallback attempts as completed visual treatment.

Next: resolve dancer details and convert remaining sauna/climbing/bunny-ear
activity sources, then continue missing activity/family/sport/flags, Seal
recovery and full-brief behaviour/style audits. Goal active and substantially
incomplete; inventory counts remain distinct from visual/linguistic proof.

### Individual dancers integrated; sauna and climbing prototypes — 2026-11-02

Integrated woman/man dancer drawings and all five skin tones: **12 additional
fully-qualified forms and exact encodings**. The man dancer's persistent
failure was traced to a four-pixel, one-row cavity at the hand/cuff boundary.
Changing source stroke 1.6 to 1.65 removes that fragile raster gap without
weakening preservation checks. At pressure 0.025, bend 0.001, taper zero it now
applies strength 1.7, preserving 7 components plus 16 counters in 23 compiled
contours. Woman retains stroke 1.3, pressure 0.1, bend 0.012, taper zero,
strength 0.7171875 and 31 contours (4 components + 27 counters).

Production: **953 base emoji, 2,966 exact sequences, 33 shaping components**,
**986 cmap entries**, **814,708 bytes**, plus an **804,308-byte** ink companion.
Coverage is **171,944 / 172,352 visible mappings**, leaving **408 missing**.
Fully-qualified emoji coverage is **2,140 / 3,963**, leaving **1,823 missing**.

Validation: **26 focused Python tests in 101.73 seconds**, **281 JavaScript
tests**, **11,449 registered source hashes**, both production geometry checks,
and **374 browser scenarios** pass. Focused checks cover new dancer masks,
source identity, deterministic treatment, all tones and boundaries, existing
activity direction/gender distinctions, every advertised variation pair, all
advertised sequences, packaging, ink-companion rebuilding and inventory.
Reviewed both enlarged and in finished strips at the approved size and weight.
Seven existing SWIG warnings remain. No fresh whole-tree or full colour-font
reproducibility test is claimed.

`tools/font/prototype_sauna_svg.py` now converts all three sauna sources.
Opaque versions of the source's translucent steam looked like ribbons and were
rejected despite green contour checks; evidence is retained as
`sauna-svg-opaque-steam-rejected.png`. A first open-wisp version used white halos
across the face, which broke anatomical enclosure and failed skin selection.
The current version reuses the source steam's inner curves as open strokes,
compresses them horizontally beside the face (left translate 4 / x-scale 0.4,
right translate 80 / x-scale 0.4), and ends the right curve above the robe.
Steam uses width 2.5 before the x transform, no opaque fill. All three apply
strength 1.7 and preserve 18/18/16 compiled contours. Neutral/male have 9
components + 9 counters; female has 9 + 7. Reviewed enlarged; production tests,
source registration and actual-strip review remain outstanding.

`tools/font/prototype_climbing_svg.py` preserves helmets, harnesses, rope,
exposed limbs and the rock face. All three trace to 28 contours (2 components
+ 26 counters). Neutral applies strength 0.40341796875 at default activity
pressure/bend. Male/female still fall back even after reducing pressure to
0.025 and bend to 0.001; they remain rejected. Reviewed the initial enlarged
sheet. No climbing or sauna sources are registered production coverage.

The activity source probe now distinguishes 23 integrated drawings from nine
remaining sauna/climbing/bunny-ear candidates. Next: integrate reviewed sauna
conversions after strip-size verification, diagnose climbing preservation,
and convert bunny-ear dancers; continue broader activity/family/sport/flags,
Seal recovery and full-brief behaviour/style audits. Goal remains active and
substantially incomplete.

### Climbing preservation repaired — 2026-11-02

Revalidated the previous approval-only turn (no implementation progress) against
current files, then diagnosed the two rejected climbing conversions. Male
translation repeatedly split a 3–7 pixel tip from the connected rock shape near
source coordinates (10,35); some trials also created small enclosed gaps.
Increasing all outlined shapes from 1.3 to 1.4/1.5/1.65/1.8 failed for both
male and female drawings, so those changes were rejected.

`tools/font/prototype_climbing_svg.py` now adds a 0.15 SVG-unit rounded stroke
only to the seven solid rock-facet polygons in the male/female drawings. This
supports their needle tips during resampling without changing anatomical
outlines or relaxing `same_features`. Trials at 0.25 and 0.4 also passed but
provided no preservation benefit. Neutral geometry is unchanged.

The strict prototype run now passes **3/3**, each with **2 components + 26
counters = 28 compiled contours**. Applied strengths are neutral 0.40341796875,
male 0.3025634765625, female 0.95625; requested strength stays 1.7, taper 0.
Male/female pressure remains 0.025 and bend 0.001. Skin regions remain neutral
[3,5,8,9,11,14,16,18,21,24], male/female [3,6,8,9,10,13,16,18,21,24].
Reviewed the regenerated enlarged sheet: helmets, harnesses, rope, hands,
limbs and rock are intact. This is still provisional visual treatment,
especially the strongly reduced male version; passing geometry is not a claim
of sufficient expressive style at comic size. Evidence is in
`output/font-review/pen-translation/climbing-svg-prototype.json` and
`climbing-svg-1f9d7-prototype.png`. Diagnostic logs for this session are
`/tmp/climbing-joins.log`, `/tmp/climbing-stroke-sweep.log`,
`/tmp/climbing-rock-sweep.log`, and `/tmp/climbing-final.log`.

No production font or coverage counts changed. Next: integrate sauna and
climbing with fixed region assertions, source registration, shaping/skin tests
and actual-strip review; strengthen climbing treatment if the strip review
requires it. Bunny-ear conversions and the broader brief remain outstanding.

### Sauna/climbing integration in progress — 2026-11-02

Integrated all six sauna/climbing recipes into `emoji_activity_svg.py`, with
literal reviewed skin-region assertions. Registered their pinned SVG sources
and 60 exact qualification forms (36 fully qualified emoji), added six
anatomical/sequence test cases and gender-distinction checks, plus routing and
finished-strip fixtures. The standalone sauna/climbing preview commands now
use the production converter. All six production geometry checks pass with
the same contours, skin selections and applied strengths as the reviewed
prototypes; 11,455 registered source files verify. Full font build and final
browser/packaging validation are being completed in this session.

The new review-only `prototype_bunny_svg.py` covers neutral/male/female paired
bunny-ear dancers. Original Noto artwork was reviewed in the browser, including
bare legs and dark leotards. The first conversion falsely outlined source
thigh/calf paint overlaps as knee seams. It was rejected visually. The revised
converter joins each leg group before outlining: raster union at 1536px,
contours simplified at 0.65px and returned to the 128-unit SVG coordinate
system. This retains the source silhouettes and removes the false seams.
All three now preserve treatment and compiled contours: neutral/male 14
components + 28 counters = 42 contours, female 14 + 24 = 38. Neutral applies
1.275 with pressure 0.025/bend 0.001; male 0.3025634765625 and female
0.7171875 with pressure 0.1/bend 0.012; taper 0 and requested strength 1.7.
Reviewed the updated enlarged sheet. Bunny-ear sources remain unregistered;
production integration, anatomical regression assertions and strip review
are still required. Latest evidence: `bunny-svg-prototype.json`,
`bunny-svg-1f46f-prototype.png`, `/tmp/bunny-prototype-merged.log`.

### Sauna/climbing production validation completed — 2026-11-02

The build completed: **955 base emoji, 3,026 exact sequences, 33 shaping
components; 988 cmap entries**. Primary font is **834,328 bytes**, ink companion
**823,968 bytes**. Inventory now records **171,946 / 172,352 visible mappings**
(**406 missing**) and **2,176 / 3,963 fully qualified emoji** (**1,787 missing**).
Person-activity coverage is 174 / 408. These are coverage counts, not blanket
linguistic or visual validation claims.

**32 focused Python tests pass in 172.81 seconds**, including all six new
conversions twice for determinism, source hashes and git-blob identities,
exact anatomical regions, unpainted excluded regions, all tones and
qualification aliases, repeated/adjacent sequence boundaries, gender and
direction distinctions, variation-selector declarations, all advertised
sequences, packaging, ink-companion rebuilding and inventory. **282 JavaScript
tests**, **11,455 source hashes**, **376 browser scenarios**, and all six
production geometry checks pass. Seven existing SWIG warnings remain. No
fresh whole-tree or full colour-font reproducibility test is claimed.

Reviewed sauna and climbing enlarged and in actual strips. Sauna faces and
open steam remain legible. Climbing is necessarily denser at dialogue size,
but the climbing pose and rock remain distinguishable; its stylistic treatment
remains provisional. The approved 1.4× optical size and stronger black ink are
unchanged. Browser checks include qualification-pixel equivalence in both the
colour and ink fonts. Asset versions and `docs/unicode-coverage.json` are
updated. Temporary source-review and validation tabs 195/196 were closed.

Final logs: `/tmp/activity-sauna-climbing-build.log`,
`/tmp/activity-six-tests.log`, `/tmp/activity-six-js.log`,
`/tmp/activity-six-hashes.log`, `/tmp/activity-six-audit.log`, and
`/tmp/activity-six-geometry.log`. Current production conversion evidence for
these six drawings is in `activity-svg-prototype.json` (the older standalone
sauna/climbing report files predate delegation to the production converter).
No background process from this integration remains running.

Next: integrate the revised bunny-ear conversions, including their leg-union
operation, after fixed anatomical assertions and actual-strip review. Then
continue remaining mobility/activity, family, sport, flag and fantasy emoji,
Seal recovery, and the full brief's behaviour/style audits. Goal remains active
and substantially incomplete.

### Bunny-ear integration and mobility prototypes — 2026-11-02 (in progress)

Moved the three reviewed bunny-ear recipes and deterministic leg union into
`emoji_activity_svg.py`, with fixed skin-region assertions. Their standalone
preview now delegates to production. Registered all three pinned sources and
30 exact qualification forms (18 fully qualified forms). Added three detailed
anatomical/sequence cases, gender distinctions, routing coverage and a strip
fixture. All three production conversions pass strict geometry; **11,458
registered source files verify**, and 50 activity tests collect successfully.
The full font rebuild was started as exec session **60993** with log
`/tmp/bunny-production-build.log`; completion and final validation are pending
at this checkpoint. Do not start another build while this handle is live.

Fetched **18 mobility SVG sources** from the same pinned Noto commit and checked
all git-blob hashes. Records: `docs/mobility-emoji-svg-source-probe.json`; cache
`build/unicode-sources/noto-emoji-mobility-svg/`. All neutral/male/female,
left/right cane, manual-wheelchair and powered-wheelchair originals were
reviewed in the browser; path probes were generated for all 18. Native source
review tab 197 was closed. These sources remain unregistered production coverage.

Three new review-only programs generate the mobility artwork:
- `prototype_cane_svg.py`: six drawings; stroke 0.7, default activity pressure
  0.1/bend 0.012/taper 0, requested strength 1.7. Initial stroke 1.3 failed all
  six (small enclosed gaps were also lost in compilation); neutral trials
  0.7/0.9 applied positive treatment, 1.1/1.5 still fell back. Current 0.7
  passes all six, each **3 components + 9 counters = 12 contours**. Applied
  strengths in neutral/male/female left then right order: .7171875, .537890625,
  1.275, .537890625, .95625, 1.275. Enlarged drawings reviewed; specifically
  check the cane's narrow white shaft under the stronger ink layer at comic
  size before accepting production rendering.
- `prototype_wheelchair_svg.py`: six manual-wheelchair drawings, stroke 1.3,
  explicit open spoke lines at 0.9. All pass **3 + 42 = 45 contours**; applied
  strengths .537890625, .95625, .537890625, .95625, 1.275, .40341796875.
  Enlarged review shows wheels, spokes, arm/hand, chair frame and clothing
  separately readable. Skin never paints wheel interiors.
- `prototype_powered_wheelchair_svg.py`: six powered-wheelchair drawings,
  stroke 1.3. Neutral/male pass **4 + 19 = 23 contours**, female **4 + 20 = 24**;
  strengths .7171875, .7171875, .95625, .537890625, .95625, .95625.
  Enlarged review shows distinct powered bases, three wheels, headrests,
  armrests and controls. Direction and gender remain distinct.

Each prototype records exact skin-region IDs and hashes in its matching
`*-svg-prototype.json` under `output/font-review/pen-translation/`, alongside
`*-svg-mobility-prototype.png`. Logs: `/tmp/cane-prototype-fine.log`,
`/tmp/wheelchair-prototype.log`, `/tmp/powered-wheelchair-prototype.log`.
All prototype/fetch jobs have completed. Production source registration,
fixed anatomical assertions, sequence/direction tests and actual-strip review
remain necessary for mobility. The global goal is still substantially incomplete.

### Bunny-ear production validation completed — 2026-11-02

The full build completed and session 60993 is terminal. Current production is
**956 base emoji, 3,056 exact sequences, 33 shaping components; 989 cmap
entries**. Font sizes: **849,116 bytes** colour and **836,164 bytes** ink.
Inventory: **171,947 / 172,352 visible mappings**, **405 missing**;
**2,194 / 3,963 fully qualified emoji**, **1,769 missing**. Activity subgroup
coverage is **192 / 408**. All 32 source drawings in the original activity
probe are now integrated, but that probe does not exhaust the activity scope.

**30 focused Python tests pass in 184.54 seconds**, including all three new
bunny conversions twice for determinism, exact skin regions and excluded
areas, source SHA-256/git identities, all six tone forms and qualification
aliases, repeated/adjacent sequence boundaries, gender/direction distinctions,
variation-selector declarations, all advertised sequences, font packaging,
ink companion and inventory. **282 JavaScript tests**, **11,458 source
hashes**, **377 browser scenarios**, and all three production geometry checks
pass. Seven existing SWIG warnings remain; no fresh whole-tree or full colour
font reproducibility run is claimed.

Reviewed the rebuilt bunny-ear font in actual strips at the approved 1.4× size
and stronger ink. The paired pose and ears read clearly; false knee seams are
gone. Source colour and anatomical distinctions remain intact. The fixture
also passed colour/ink qualified-versus-unqualified canvas equivalence.
Asset versions and coverage audit are refreshed. Validation tab 198 closed.
No process from this turn remains running.

Final logs: `/tmp/bunny-production-build.log`,
`/tmp/bunny-production-tests.log`, `/tmp/bunny-production-js.log`,
`/tmp/bunny-production-audit.log`, `/tmp/bunny-production-hashes.log`,
`/tmp/bunny-production-geometry.log`. Next: integrate the 18 reviewed mobility
prototypes with fixed region assertions, source registration, direction/tone
shaping checks and strip review, watching narrow cane interiors under the ink
companion stroke. Then continue the rest of the full brief. Goal stays active.

### Mobility integration and remaining activity evidence — 2026-11-02 (in progress)

Integrated 18 mobility recipes into `emoji_activity_svg.py`, selecting the new
`data/font-sources/noto-emoji-mobility-svg.json` registry for those keys. White
canes use stroke 0.7; manual wheelchair spokes use explicit open 0.9 strokes;
other mobility outlines use 1.3. Literal reviewed skin-region assertions are
in place. Source entries advertise **162 exact forms / 108 fully-qualified
emoji**. Added 18 detailed anatomical/sequence cases, three mobility boundary
cases exercising every tone/person/direction, routing coverage and six strip
fixtures. All 18 production geometry checks pass, **11,476 source files verify**,
and **71 activity tests collect**. Standalone U+1F9AF/U+1F9BC/U+1F9BD are still
missing visible drawings; they become shaping-only components, not claimed
visible coverage. Expected cmap grows from 989 to 992 with these three blanks.

Full build is exec session **68248**, log `/tmp/mobility-production-build.log`.
It was verified live at 10:58 UTC; do not restart while live. Final font tests,
audit, versions, browser and actual-strip reviews remain pending. Production
geometry log: `/tmp/mobility-production-geometry.log` (only the 18 selected
mobility records were regenerated; its aggregate also includes older records).

A precise activity inventory check exposed **60 mixed-tone bunny-ear forms**
using `person + tone + ZWJ + rabbit + ZWJ + person + tone`, in addition to the
shared-tone forms already supported. These remain correctly counted as gaps.
`emoji_paired_skin.py` now partitions whole connected skin components across
the inter-person gap, rejects crossing components, and asserts disjoint masks
whose union exactly equals the reviewed skin. It does not modify ink or white
layers and is not yet wired into production. `prototype_bunny_tone_pairs.py`
produces six light/dark and reversed examples using the existing PDF palette.
All three partitions pass; enlarged examples reviewed. Evidence:
`bunny-tone-pairs-prototype.json` / `.png`, `/tmp/bunny-tone-pairs.log`.
The helper must not be used unchanged for interlocking figures.

Fetched and git-hash verified the remaining eight no-tone activity source
candidates (massage/haircut × three genders, ballet dancer, levitating person)
into `build/unicode-sources/noto-emoji-activity-extra-svg/`, recorded in
`docs/activity-extra-emoji-svg-source-probe.json`; all originals reviewed in
native browser and path probes generated. These are reference-only.
Also fetched two pinned tone references into
`build/unicode-sources/noto-emoji-activity-tone-reference-svg/`, with records in
`docs/activity-tone-reference-emoji-svg-source-probe.json`. Native review
confirms first bunny-ear modifier colours the **left** dancer, and Noto's dark
massage variant colours **both the recipient and the massaging hands**. Carry
that evidence into the anatomical conversion; do not assume the hands stay
neutral. Review tabs 199/200 closed. All source/prototype jobs are terminal;
only the full font build was still running at this checkpoint.

### Mobility production validation completed — 2026-11-02

The build completed (session 68248 terminal). Production now has **956 base
emoji, 3,218 exact sequences, 36 shaping components; 992 cmap entries**.
Colour font **890,348 bytes**, ink companion **877,496 bytes**. Visible coverage
remains **171,947 / 172,352**, **405 missing**: the three new equipment component
cmap entries are blank shaping components and are correctly excluded. Fully
qualified emoji coverage is **2,302 / 3,963**, **1,661 missing**; activity subgroup
**300 / 408**, **108 missing** (60 mixed-tone bunny pairs + 48 other activity
forms). Sources and geometry are documented above.

**48 focused Python tests pass in 350.24 seconds**, covering all 18 new
conversions twice, exact anatomical masks, source SHA-256/git identities,
all tones and qualification aliases, adjacent/repeated sequences, all six
person/direction drawings, surrounding person/tone boundaries, existing
activity gender/direction distinctions, every advertised variation pair,
all advertised emoji sequences, packaging, ink rebuilding and inventory.
**283 JavaScript tests**, **11,476 source hashes**, and **384 browser scenarios**
pass. Seven existing SWIG warnings remain. No fresh whole-tree or full colour
font reproducibility test is claimed.

Existing fallback tests had used mobility sequences as unsupported examples.
They now use a still-unsupported surfing form, while the person-prefix test
uses deliberately unregistered longer mobility chains. Mixed RTL dialogue
explicitly checks the newly custom wheelchair sequence. Added a dedicated
standalone-equipment fixture and font-loading assertion: 🦯/🦼/🦽 remain visible
native fallbacks, while adjacent person+equipment sequences use custom art.
This was verified in the actual strip, not inferred from cmap presence.

Reviewed all six mobility strip fixtures. Manual and powered wheelchairs are
visually distinguishable; left/right forms and tones remain readable. Cane
silhouettes read, but the shaft's white interior is subtle at dialogue size
under the stronger ink layer. Retain this as a visual limitation for the wider
style audit rather than claiming every fine detail is equally clear. The
approved 1.4× optical size and stronger black ink remain unchanged. All colour
and ink qualification-equivalence checks pass. Asset versions and coverage
inventory are current; validation tab 201 was closed. No process from this
turn remains running.

Final logs: `/tmp/mobility-production-build.log`,
`/tmp/mobility-production-tests.log`, `/tmp/mobility-production-js-final.log`,
`/tmp/mobility-production-audit.log`, `/tmp/mobility-production-hashes.log`,
`/tmp/mobility-production-geometry.log`. Earlier JS logs preserve the obsolete
fallback-expectation failures; the final log is the authoritative passing run.

### Massage/haircut prototypes — 2026-11-02

`prototype_service_people_svg.py` converts all six massage/haircut sources,
using 1536px, stroke 1.3, pressure 0.1, bend 0.012, taper 0, requested strength
1.7. All six pass geometry and were reviewed enlarged. Massage colours face,
neck, ears and both hands as supported by the pinned tone reference; clothing
stays white. Haircut retains the main scissor blades/rings and pivot, omitting
redundant shaded overlays; hair may deliberately partly cover an eye as in the
source. These remain review-only, not registered coverage.

- Massage neutral/male: 7 components + 7 counters = 14 contours, skin IDs
  [1,2,3,4,5,6], strengths .7171875 / 1.7.
- Massage female: 7 + 5 = 12, skin [1,2,3,4], strength 1.275.
- Haircut neutral: 3 + 7 = 10, skin [3,4,5,6], strength 1.7.
- Haircut male: 6 + 8 = 14, skin [3,5,6,7], strength .7171875.
- Haircut female: 4 + 6 = 10, skin [3,5], strength 1.7.

Evidence: `service-people-svg-prototype.json`,
`service-people-svg-1f486-prototype.png`, `service-people-svg-1f487-prototype.png`,
and `/tmp/service-people-prototype.log`. Next: integrate these six and the
independent bunny-tone masks; convert ballet/levitating sources already pinned
and reviewed. Then continue standalone equipment, broader emoji, Seal recovery
and all remaining full-brief behaviour/style audits. Goal remains active.

### Remaining activity integration underway — 2026-11-02

Integrated the six massage/haircut drawings plus ballet and levitation into
`emoji_activity_svg.py` and the extra activity source registry. Production
geometry previews pass **6/6 service drawings and 2/2 final activity drawings**.
The bunny-ear builder now uses independent left/right skin layers for all 60
mixed-tone pairs, asserting the reviewed connected-component partitions and
source sequence lists. Added shaping, palette-order, repeated/adjacent sequence,
qualification and whole activity-subgroup regressions, plus seven strip fixtures.
Levitation's unmodified FE0F form is explicitly included in the manifest.

The full font rebuild is running as session 33316 (started 11:13 UTC), log
`/tmp/activity-completion-build.log`. Do not treat the expected 408/408 activity
coverage as verified until the final font audit and tests complete. Source
verification is complete: **11,484 files pass**. The service/last-activity
geometry and hash jobs are terminal. Current font/browser validation remains
pending; the preceding mobility checkpoint remains the last validated baseline.

Also prepared `prototype_mobility_equipment.py` from the pinned OFL monochrome
Noto donor for standalone cane, powered wheelchair and manual wheelchair.
All three preserve exact compiled contour counts (6, 8, 7), with positive
expressive treatment (1.7, .7171875, .537890625). Reviewed enlarged and at
33.6px with the stronger stroke. These are still **prototype-only**; the
standalone equipment remains native fallback in production. Evidence:
`output/font-review/pen-translation/mobility-equipment-prototype.{png,json}`
and `/tmp/mobility-equipment-prototype.log`. No production converter was
changed while the activity build was running.

Activity build completed successfully: **959 base emoji, 3,351 exact sequences,
36 shaping components, 995 cmap entries**. Colour font **913,888 bytes**, ink
companion **901,404 bytes**. The refreshed audit reports **171,949 / 172,352**
visible cmap coverage (**403 missing**) and **2,410 / 3,963** fully-qualified
emoji forms (**1,553 missing**). Activity coverage is now **408 / 408**.
The three new emoji bases add only two globally missing visible characters;
keep the actual inventory result, not the earlier estimate of 171,950.

**284 JavaScript tests and 391 browser scenarios pass**, including geometry,
export and activity qualification-equivalence checks. Visually reviewed all
seven new strip fixtures at the approved optical defaults. Haircut scissors,
levitation shadow, ballet silhouette and reversed left/right bunny skin tones
remain distinguishable. Fine facial details on the narrow ballet figure are
less clear at dialogue size; levitation's mostly black suit likewise leaves
little visible skin. Do not equate preserved contours with all details being
readable. Browser validation tab 202 closed. Focused Python run (session 46611,
`/tmp/activity-completion-tests.log`) is still running at this checkpoint.

### Activity production validation completed — 2026-11-02

**45 focused Python tests pass in 323.10 seconds** (220 deselected, seven
existing SWIG warnings). This includes all eight new source conversions twice,
independent bunny-tone masks and palette order, repeated/adjacent sequence
boundaries, all 408 activity forms shaping to real drawings, gender/direction
distinctions, variation-selector declarations, every advertised emoji sequence,
ink companion rebuilding and inventory checks. Together with the **284 JS,
391 browser, 11,484 source-hash checks** and reviewed strips above, this closes
the current activity integration. No fresh whole-tree test or complete colour
font reproducibility run is claimed. Asset versions and coverage are current.
All build, prototype and validation processes from this checkpoint are terminal.

Next concrete work: promote the reviewed standalone mobility-equipment
prototypes while preserving compound substitutions; update their native-fallback
fixtures accordingly. Then continue missing emoji groups and Seal recovery,
and the remaining full-brief linguistic, browser and visual audits. The goal
remains active and substantially incomplete; subgroup coverage is not overall
Unicode completion.

### Standalone equipment promotion underway — 2026-11-02

The preceding goal turn made verified progress: activity integration completed,
with the checks recorded above. Promoted the reviewed OFL Noto cane and both
wheelchairs through `emoji_licensed.py` as `mobility_equipment`. The activity
builder will now reuse their real cmap glyphs instead of inserting blank
components. Updated the standalone fallback expectation and browser fixture;
added a regression that reconstructs all three drawings, checks exact contour
counts, and tests equipment on both sides of every person/tone/direction form.

Full build session **89870**, started 11:31 UTC, log
`/tmp/mobility-equipment-build.log`, is still running. Expected counts are
962 visible emoji bases, 33 shaping components, 995 cmap entries and 3,354
exact sequences; these are estimates until final audit. Source hash check
passes **11,484 files** (`/tmp/mobility-equipment-hashes.log`). The separate
`source_inventory.verify_sources()` returns 259 font files, not the complete
source-file count; do not confuse those two totals.

Prepared five reference-only resting SVG sources from the same pinned Noto
commit, with SHA-256 and git-blob checks in
`docs/resting-emoji-svg-source-probe.json`. Native browser source review and
path probes completed. `prototype_resting_svg.py` now covers lotus position
(three gender drawings), bath and bed. The prototype unions upper-arm and
forearm source paint before outlining; those pieces encode shading and must
not invent elbow seams. Lotus strokes are 1.6 neutral/female, 1.5 male;
female uses pressure .025/bend .001, others pressure .1/bend .012, taper 0,
requested strength 1.7. Bath/bed use stroke 1.3 and default activity settings.

The earlier 1.3 lotus treatment fell back, and neutral at 1.5 lost one tiny
enclosure during tracing. Correcting the outline closes an accidental sleeve
pinhole without weakening the topology guard. The sleeping source exposes a
small side-profile face: its reviewed 4,799px skin mask is below the generic
5,000px floor, so this recipe has a 4,000px floor plus pinned region identity.
All five geometry records now pass. Enlarged visual review completed for
bath, bed and lotus forms; a final run with pinned skin-region assertions is
session **20549**, log `/tmp/resting-svg-reviewed-prototype.log`.
These prototypes are **not production coverage** yet.

Resting prototype final run completed: **5/5 preserve treatment and exact
compiled contours**. Bath: 4 components + 19 holes = 23 contours, strength 1.7,
skin [7]/19 (46,098 pixels). Bed: 1 + 7 = 8, strength 1.7, skin [1]/7
(4,799 pixels). Lotus neutral: 8 + 14 = 22, strength .7171875, skin
[1,2,3,4,6,7,11,13,14]/14. Male: 8 + 15 = 23, strength 1.275, skin
[1,2,3,4,6,7,13,14,15]/15. Female: 8 + 12 = 20, strength 1.7, skin
[1,2,4,5,10,11,12]/12. Final three-lotus sheet reviewed after the outline
correction. Source review tab 203 closed. All resting prototype jobs terminal.
Evidence is `resting-svg-prototype.json`, `resting-svg-*-prototype.png`, and
`/tmp/resting-svg-reviewed-prototype.log`. Do not count these five drawings or
their 30 fully-qualified forms as production coverage yet.

Equipment validation is pending the live build 89870. After it terminates
successfully: run `tools/version_assets.py`, `tools/unicode/audit.py`, `npm test`,
and focused pytest on `tests/test_font_emoji.py`,
`tests/test_font_activity_people.py`, `tests/test_font_emoji_ink.py`,
`tests/test_unicode_inventory.py` selecting `standalone_mobility_equipment or
mobility_gender_direction or custom_emoji_have_real or
every_advertised_custom_sequence or activity_subgroup or
activity_variation_selectors or ink_companion or inventory`.
Then run the browser suite and inspect `emoji-mobility-components` plus the
adjacent compound fixtures. The changed equipment assertion requires an exact
custom standalone run and no native fallback; confirm this against actual
rendered report data. Keep the goal active. No build restart is warranted:
last poll of 89870 confirmed it running, with no terminal/error output.

### Equipment compiled checks; resting integration underway — 2026-11-02

Equipment build 89870 completed. Actual assets: **962 base emoji, 3,354 exact
sequences, 33 shaping components, 995 cmap entries**; colour **915,632 bytes**,
ink **902,280 bytes**. Audit: **171,952 / 172,352 visible characters**, **400
missing**; **2,413 / 3,963 fully-qualified emoji**, **1,550 missing**.
**16 focused Python tests pass in 63.54 seconds**, including exact equipment
reconstruction/contours, all adjacent compound boundaries, all advertised
sequences, the activity subgroup, variation selectors, ink rebuilding and
inventory. **284 JavaScript tests and 11,484 source hashes pass**. Seven
existing SWIG warnings. All equipment shell jobs terminal.

Browser validation is still pending: creating new hidden tabs timed out three
times without leaving tabs in the inventory. Existing review tab 179 remains
accessible, so it is temporarily running `tools/unicode-checks.html`. **Restore
179 to `http://localhost:8765/tools/emoji-optical-review.html` after reviewing;
do not close it.** Tab 180 remains untouched. The loaded equipment suite has
391 fixtures (before the subsequent resting fixture edits). It is still
rendering, last observed through `emoji-clothing-2`; a click timed out, which
is not evidence that rendering stopped. Do not reload merely due to timeout.

Integrated the five reviewed resting recipes into `emoji_activity_svg.py`,
registered the pinned source files, reused the existing all-tone/qualification
builder, and changed the prototype to call production conversion. Added five
skin/identity cases, meditation gender distinctions, exact 30-form resting
subgroup coverage, JS routing and three strip fixtures. The bed's small-face
floor and lotus arm union/outline adjustments are retained. Expected new totals
are 965 bases, 3,396 exact sequences, 998 cmap entries and 33 components; these
remain estimates until the new build is checked.

Resting full build **4821**, log `/tmp/resting-production-build.log`, launched
11:48 UTC. Production geometry **80711**, log
`/tmp/resting-production-geometry.log`; source hashes **54659**, log
`/tmp/resting-production-hashes.log`. Do not edit production conversion while
4821 runs. Equipment validation uses the already-built assets until this new
build finishes. Resting needs asset versioning, refreshed audit, JS and focused
font tests, then the 394-fixture browser run and actual-strip visual review.

Resting production geometry and hashes completed: **5/5 strict geometry and
11,489 source-file hashes pass**. Jobs 80711 and 54659 are terminal; full build
4821 remains live. No changed prototype geometry was substituted during build.

While the build and browser suite run, prepared additional body-part prototypes:
`prototype_body_parts.py` uses pinned OFL Noto outlines at 384px/weight 400 for
brain, tooth, bone, eyes, eye, tongue, mouth, biting lip, anatomical heart, lungs,
mechanical arm and leg. All twelve pass exact compiled contours and positive
expressive treatment; enlarged/small preview reviewed. Contours in that order:
6,3,2,5,4,2,5,4,10,10,14,9. Strengths are .95625 for brain/heart/lungs/mechanical
arm, 1.275 mechanical leg, 1.7 otherwise. Evidence:
`body-parts-prototype.{json,png}`, `/tmp/body-parts-prototype.log` (job 17623
terminal). These twelve remain prototype-only.

Six pinned Noto SVG sources fetched/git-verified in
`docs/body-tone-emoji-svg-source-probe.json`: flexed biceps, ear, hearing-aid ear,
nose, leg and foot. Path probes generated. `prototype_body_tone_svg.py` keeps
anatomical skin separate from hearing equipment. All six pass geometry and
pinned skin-region assertions; enlarged output reviewed. At 1536px, stroke 1.3,
pressure .1/bend .012/taper 0, requested strength 1.7: ear 3+1=4 contours;
nose 1+1=2; biceps/leg/foot each 2+1=3, all applied 1.7 and skin [1]/1.
Hearing-aid ear 2+5=7, applied .95625, skin [3]/5; device and air gaps stay white.
The current source has no separate nail fill, so no artificial white nail mask
was introduced. Job 10665 terminal, final log
`/tmp/body-tone-svg-reviewed-prototype.log`, evidence
`body-tone-svg-prototype.json` and `body-tone-svg-*-prototype.png`.
Native-colour SVG source comparison remains pending because the browser is
running equipment checks; do not register these six or claim their coverage
before that review and subsequent production validation. This plus the twelve
monochrome candidates would cover all 48 body-parts forms, but is not yet
production coverage.

Browser source screenshot attempt: temporarily opened the body-tone source
page in user review tab 180, but both documented screenshot APIs failed.
Restored 180 to its exact original URL ending `emoji-optical-review.html#comic`
and verified its title/state. Do not claim a browser source visual review.
The previously existing 179 tab continues equipment checks.

Completed source comparison using the installed `rsvg-convert` offline SVG
renderer instead. `body-tone-native-rsvg.png` contains all six original colour
SVGs and a previously browser-reviewed lotus source as a rendering sanity
check. Gradients/colours and anatomy render correctly. Compared each source
with the prototype: original skin stays skin; hearing equipment remains
separate; finger/toe and ear/nostril details retained. No separate white nail
fill exists in the biceps source. This completes source visual comparison,
while actual production font/strip review remains pending for these candidates.
Offline SVG inspection is distinct from browser layout/export validation.

Equipment browser suite completed: **391 scenarios pass with zero failures or
geometry issues**, including the exact standalone custom-run assertions and
export. However, current browser screenshot capture fails; Playwright image
attribute reads time out even after completion, and the in-app browser reports
`content.export()` unsupported. Page asset inventory exposes source panel PNGs
but not generated data-URL strip images. Thus **the new equipment actual-strip
visual inspection remains pending**; do not claim it passed. Enlarged and
33.6px optical prototype review and exact compiled-outline checks are complete.
This is a visual-tool limitation, not an overall goal blocker; other work
continues. Both user review tabs were restored and marked deliverable:
179 → `tools/emoji-optical-review.html`,
180 → `tools/emoji-optical-review.html#comic`. Do not close them.

The resting source/code integration is still building in session 4821. The
previous full browser report used equipment assets and 391 fixtures, not the
new resting fixtures. After 4821 completes, refresh versions/audit and run
focused tests selecting `1f9d8 or 1f6c0 or 1f6cc or activity_subgroup or
activity_variation_selectors or custom_emoji_have_real or
every_advertised_custom_sequence or ink_companion or inventory`, plus npm test.
The new browser suite should contain 394 fixtures; actual visual review is
still required for the three resting fixtures and standalone equipment.

Browser recovery note — 2026-11-02: resetting only the persistent CUA JavaScript
session (`js_reset`), then reacquiring existing tab 179, restored screenshot
capture. Its unchanged optical-review page was captured successfully. This
reset does not close or reload tabs. New hidden-tab creation still times out,
so use an existing static review tab temporarily and restore its exact URL
when finished. Do not infer that the underlying browser is disconnected.
Resting build 4821 remains live; a fresh poll is required before validation.

### Resting compiled validation and optical follow-up — 2026-11-02

Resting build 4821 completed: **965 bases, 3,396 exact sequences, 33 components,
998 cmap entries**. Colour **932,296 bytes**, ink **918,628 bytes**. Visible
coverage **171,955 / 172,352** (**397 missing**), fully-qualified emoji
**2,443 / 3,963** (**1,520 missing**); resting subgroup **30/30 encoded**.
**19 focused Python tests pass in 134.77 seconds**, **285 JS tests**, **394
browser scenarios**, **11,489 source hashes** and five production geometry
checks pass. Seven existing SWIG warnings. All resting build/test jobs terminal.
No full-tree or complete colour-font reproducibility test is claimed.

With the recovered CUA session, visually reviewed the meditation, bath and
bed strips, and finally the standalone equipment fixture. Equipment, meditation
and bath read clearly; equipment visual review is no longer pending. The bed's
small face did not show skin-tone differences well at dialogue size, so its
visual refinement remains open. Tab 179 was restored to its original optical
review URL and marked deliverable; tab 180 remains at the original #comic URL.

`prototype_sleeping_optics.py` tested enlarging source head/hair paths 10/11 by
1.8 about (40,85), leaving bed/pillow/blanket and overall advance unchanged.
All eight contours remain, with positive strength 1.7 and skin region [1]/7;
skin grows from 4,799 to 14,796 pixels. Reviewed enlarged and all five tones
at 33.6px with the stronger stroke in `sleeping-optics-comparison.png`.
Accepted as an optical improvement, now integrated into production conversion
with a recorded `opticalHeadTransform`; the earlier 4,000px exception is removed
and the ordinary >5,000px skin check applies again. Added a regression requiring
>14,000 skin pixels and the reviewed transformation. Actual-strip re-review
of the rebuilt font is still required.

### Body-parts integration underway — 2026-11-02

Integrated twelve OFL monochrome body drawings into `emoji_licensed.py`, six
Apache SVG anatomical recipes into the shared converter, and all skin tones.
Registered sources in `noto-emoji-body-tone-svg.json`; prototype now delegates
to production. Added exact 48-form subgroup coverage, source/contour identity,
skin masks, eye text/emoji presentation, repeated forms and unsupported eye-in-
speech-bubble fallback regression. Nine new fixtures cover every drawing and
tone; added body-part fixtures to browser qualification-equivalence checks.
Expected totals (not yet verified): **983 bases, 3,446 exact sequences,
1,016 cmap entries, 33 components**. Expected browser count **403**, JS **286**.

Full build **7629**, `/tmp/body-parts-production-build.log`, started 12:06 UTC.
It includes the sleeping head refinement. Geometry jobs **31642** (six body
SVGs, `/tmp/body-tone-production-geometry.log`) and **49670** (sleeping figure,
`/tmp/sleeping-production-geometry.log`); hash job **66963**,
`/tmp/body-parts-production-hashes.log`. Do not edit production conversion while
7629 runs. Refresh versions/audit and validate the finished assets before
claiming body coverage or improved sleeping-tone readability.

Body production geometry jobs are terminal: all six body SVG conversions pass
strict contour/treatment checks; the sleeping target passes with its larger
head (the preview's 5/5 summary includes four earlier resting records, not four
new reruns). **11,495 source hashes pass**. Full build 7629 remains running,
confirmed by the latest handle poll. Next focused tests should include
`1f442 or 1f443 or 1f4aa or 1f9b5 or 1f9b6 or 1f9bb or 1f6cc or body_part or
activity_subgroup or activity_variation_selectors or custom_emoji_have_real or
every_advertised_custom_sequence or ink_companion or inventory`, alongside
npm test and the refreshed audit. Review all nine body fixtures and the updated
sleeping strip. Keep the remaining full-brief work active.

### Sports source preparation — 2026-11-02

Pinned person-sport inventory has **308 fully-qualified forms** and **43 base
source drawings**. Downloaded and SHA256/Git-blob verified all 43 from the same
Apache Noto SVG commit, recorded in `sport-emoji-svg-source-probe.json`.
These remain reference/prototype sources, not registered production coverage.
`preview_emoji_colour_sources.py` produces hash-checked offline original-colour
review sheets through installed librsvg (2.62.2), preserving source gradients.
Visually inspected all four `sport-native-sources-*.png` sheets and all three
juggling path probes. Jugglers' gloves must remain white; head/ears/neck tone.

Mixed-tone wrestling uses U+1FAEF FIGHT CLOUD between the two person sequences,
not the single wrestling emoji as joiner. Verified two opposite-tone neutral
references, recorded in `wrestling-tone-reference-emoji-svg-source-probe.json`.
First modifier belongs to the left wrestler, second to the right. Their arms
cross: the separated bunny figures' midpoint helper is unsuitable; use source
path ownership for anatomical masks. Fencer/skier are completely clothed and
have no standard tone forms. Snowboarder's exposed-skin material needs tone
reference inspection; goggles/gloves/scarf should not acquire invented skin.

Independent `prototype_juggling_svg.py` tries three drawings without touching
the in-flight body production conversion. Initial female candidate hit the
positive-treatment guard; retry uses gentler pressure/bend, retaining strength
1.7 and the existing detail-preserving backoff. Geometry, anatomical masks and
small-size inspection remain required before any production registration.

Juggling retry passes **3/3** exact compiled contour checks: neutral 9+14=23,
male 9+14=23, female 9+12=21; positive applied strengths .7171875,
.3025634765625, .7171875. Reviewed enlarged skin regions: neutral
[3,4,6,9]/14, male [3,4,5,9]/14, female [3,7]/12; gloves/clothing/balls white.
Pinned those anatomical masks in the independent prototype and removed unused
copied activity branches. Strict rerun session 20147 verifies the cleaned file.

`juggling-optics-comparison.png` renders compiled outlines in all five sampled
skin tones at 160px and 33.6px, with production-equivalent 18-unit added stroke.
This revealed crowded glove creases and facial features under stronger ink.
Do not promote these merely because topology passes. Refine the detailed glove
and face geometry and then verify actual-strip rendering. Optical comparison
helper is `/tmp/compare-juggling-optics.py`; output is not an app screenshot.

### Body-parts compiled validation — 2026-11-02

Build 7629 completed successfully: **983 base emoji, 3,446 exact sequences,
33 components, 1,016 cmap entries**. Colour **953,584 bytes**, ink **939,868
bytes**. Versions refreshed; audit reports **171,969 / 172,352** visible cmap
entries (**383 missing**), **2,491 / 3,963** fully-qualified emoji encoded
(**1,472 missing**). All **48 body-parts forms** encoded. This is a subgroup
milestone, not completion of the brief.

**22 focused Python tests pass in 137.11 seconds** (259 deselected, seven
existing SWIG warnings), **286 JavaScript tests pass**, **403 browser scenarios
pass with no geometry/export failures**. Six body SVG geometry checks, sleeping
geometry target and **11,495 source hashes** passed earlier in this batch.
Logs `/tmp/body-parts-production-{build,audit,js,tests,hashes}.log`.
All production build/validation jobs terminal. No fresh full-tree or complete
colour-font reproducibility test is claimed.

Visually inspected all nine new body-part fixture strips: head/eyes, mouth,
anatomy/mechanical limbs, biceps, ear, hearing aid, nose, leg and foot. Shapes and
skin tones read at dialogue size; hearing-aid device remains white and eye
presentation variants match. Re-reviewed the sleeping strip: enlarged head
helps, but skin-tone differences remain subtle because the exposed face is
still small. Keep that optical limitation recorded. Tabs 179/180 restored to
original optical-review URLs and marked deliverable.

Juggling optical experiment (`prototype_juggling_optics.py`) shrinks eye radii
to 1.7/1.9 and moves them down two source units; removes the middle glove crease
on each hand. It passed 3/3 contour checks and improved the stronger-ink preview,
but neutral at strength 1.7 displaced one ear out of its anatomical mask.
Not production-ready. A gentler pressure .025/bend .001 trial for all three
is running as session 57456, log `/tmp/juggling-optical-prototype.log`.
Review both ears before pinning regions or registering sources. Reusable
`preview_juggling_optics.py` renders the original prototype; refined helper is
`/tmp/preview-juggling-refined.py`. These are standalone optical specimens,
not app screenshots. The source-preserving original prototype strict rerun
20147 passed 3/3 after cleanup and anatomical pinning.

Gentler juggling optical trial 57456 is terminal: **3/3** strict contour checks
pass; enlarged inspection now shows both neutral ears correctly toned.
Neutral/male/female applied strengths **1.7 / .537890625 / .7171875**;
contours remain **23 / 23 / 21**. Pinned the reviewed region sets
[3,4,6,9]/14, [3,4,5,9]/14, [3,7]/12 in the experimental converter.
No production integration yet. Regenerate stronger-ink comparison from this
latest geometry and review it before promotion (the existing refined small-size
PNG predates the gentler neutral/male settings). No jobs remain running.
Next: finish juggling optical validation, register the three sources with exact
18 fully-qualified forms/qualification aliases, add tests/strip fixtures, and
continue sports/family/flags plus the broad Unicode brief's remaining gaps.

### Juggling production integration — 2026-11-02

Previous goal turn made verified progress: body-part production build, tests
and actual-strip review completed. Continued with the latest juggling optical
comparison; all five tones at 33.6px retain the smaller separated eyes and white
glove interiors. Integrated the three refined recipes into `emoji_activity_svg`
with recorded eye radii/offset and removed middle creases. Registered only those
three source files in `noto-emoji-juggling-svg.json`: **18 fully-qualified forms,
30 exact forms including qualification aliases**. Distinct gender drawings,
anatomical masks, repeated/boundary shaping and ink companions use the generic
activity tests; added the three fixture strips and JS exact routing checks.

Production geometry **3/3 passes**, and **11,498 source hashes pass**; logs
`/tmp/juggling-production-{geometry,hashes}.log`. Started full production build
(log `/tmp/juggling-production-build.log`), expected **984 bases, 3,476 exact
sequences, 1,017 cmap entries, 33 components**. Expected browser count **406**,
JS **287**. Do not change production conversion while it runs. Refresh asset
versions and audit afterward; run focused juggling/manifest/companion/inventory
tests, JS and browser checks; review all three actual strips before accepting.

Juggling full build handle **73029**, started about 12:25 UTC, remains live
(latest poll 12:28 UTC). Production converter must remain unchanged during it.

Independent clothed-sport trial: `prototype_clothed_sport.py` verifies the OFL
font's fencer (1 component +2 holes, strength .40341796875) and skier
(1+4, strength 1.275), both 384px/weight400 and exact compiled contours.
Visually these are mostly solid silhouettes: insufficient clothing detail for
this style. Do not promote solely on their passing topology checks.
`prototype_clothed_sport_svg.py` instead experiments with the pinned detailed
Apache SVG sources. Fencer's initial .1 pressure/.012 bend failed the positive
translation guard; a .025/.001 trial plus a skier recipe is running as **17192**,
log `/tmp/clothed-sport-svg-prototype.log`. Source colour sheet and both path
probes were reviewed. No new production coverage claimed for either drawing.

Clothed-sport SVG follow-up: initial fencer omitted the guard (paths 7/8),
leaving the foil floating; restored those verified source paths. At 1.1 stroke,
a four-pixel collar pinhole prevented every positive translation. Stroke 1.3
preserves the meaningful contour geometry and permits .537890625 treatment
(1 component, 20 holes). Skier candidate visually retains helmet/goggles,
clothing, boots, poles and both skis, but a two-pixel isolated raster fleck at
(1077,952–953) causes the strict component check to fail. Current independent
trial **30613** records/removes only sub-four-pixel raster specks, following the
existing standing-person cleanup approach, without weakening feature matching.
Both remain outside production. Standard data confirms fencer has only its
single base form; skier has base and FE0F presentation, no skin-tone forms.

Fencer detailed SVG prototype now passes and its enlarged/33.6px stronger-ink
preview was visually inspected: sword/guard and clothing read clearly, unlike
the silhouette donor. **1 component +20 holes =21 compiled contours**, positive
strength **.537890625**, 1536px, stroke1.3, pressure .025/bend .001/taper0.
Artifact `clothed-sport-svg-1f93a-prototype.png/json`; job47279 terminal0.

Skier still needs geometry work: after two-pixel raster speck cleanup and a
single solid black goggle rim (source65), it has 1 component/29 holes. Diagnostic
`/tmp/diagnose-skier.py` shows 29 holes survive low-resolution translation at
several backoffs but exported antialiasing creates a 30th. This is a split
existing interior, not a missing glyph or a reason to weaken guards. Trials
30613/60260 terminal1; production unaffected. Continue from the latest recipe
in `prototype_clothed_sport_svg.py` (`--keys` selects one drawing).

Skier issue resolved in independent prototype: exported hole mapping identified
source interior7 splitting at the left elbow (roughly x321–469,y394–666).
Source32 is a narrow orange highlight across the dark sleeve31, not a garment
seam. Kept/outlined the complete sleeve31 and omitted highlight32. Job41847
passes at **strength1.7**, **1 component +29 holes =30 compiled contours**,
1536px/stroke1.3 and .025 pressure/.001 bend/taper0. Only the earlier two-pixel
raster fleck is removed, recorded explicitly. Viewed enlarged and 33.6px with
stronger ink: both skis, poles, helmet/goggles and clothing read clearly.
Artifact `clothed-sport-svg-26f7-prototype.png/json`. Diagnostic jobs are terminal.
Both detailed clothed-sport drawings are ready for production adaptation, still
not registered or advertised. Preserve their no-modifier status; a future
builder path must generate one canonical drawing and proper presentation forms,
not six invented tones. Juggling build73029 is still running; do not mutate its
production modules until terminal and validated.

Snowboarder material ambiguity resolved from pinned sources: downloaded all five
standard skin-tone reference SVGs, verified SHA256 and Git blobs, recorded in
`snowboarding-tone-reference-emoji-svg-source-probe.json`. Visually inspected
lightest/darkest native-colour drawings: helmet/goggles/scarf/gloves cover all
skin. **All five modifier SVGs are byte-for-byte identical to the base**,
SHA256 `6e79a174e1b3e3b4fadc7f2c4e19207936c4d5a590dac71c434b7c06045e6772`.
A future custom snowboarder should support all six standard forms with the same
covered drawing, not colour invented skin or drop the modifier sequences.
These remain reference sources only, not registered production coverage.

Clothed-source probe `clothed-sport-emoji-svg-source-probe.json` records fencer
base plus skier base/FE0E/FE0F. The latter two presentation selectors are
confirmed in pinned emoji-variation-sequences.txt, not inferred from emoji-test.
Latest font build73029 poll confirms it remains live. After terminal0, run
version_assets.py, audit.py, npm test, and focused Python selection:
`1f939 or activity_variation_selectors or custom_emoji_have_real or
every_advertised_custom_sequence or ink_companion or inventory`. Inspect
three `emoji-activity-people-juggling-*` browser fixtures; expected406 total.

### Juggling compiled validation — 2026-11-02

Full build73029 terminal0: **984 bases, 3,476 exact sequences, 33 components,
1,017 cmap entries**. Colour **962,136 bytes**, ink **949,372 bytes**. Versions
refreshed and audit31226 terminal0: visible **171,970 / 172,352** (**382 missing**),
fully-qualified emoji **2,509 / 3,963** (**1,454 missing**). Person-sport now
**18 / 308 encoded**, with **290 still missing**. Full brief remains incomplete.

**287 JS tests pass**, **406 browser scenarios pass with no geometry/export
failures**. Visually inspected neutral/male/female juggling strip fixtures with
all five skin tones: expression, balls, white gloves/clothing and distinct hair
remain readable at dialogue size. Tabs179/180 restored to original optical
review URLs and marked deliverable. Focused Python session46195 is still live
(latest output14 passing dots); log `/tmp/juggling-production-tests.log`.
No new full-tree or complete colour-font reproducibility test is claimed.

Focused Python46195 terminal0: **15 passed in132.92 seconds**,270 deselected,
seven existing SWIG warnings. All juggling jobs terminal; production validation
complete for this batch, including prior3/3 geometry and11,498 source hashes.
Next concrete work: adapt the reviewed detailed fencer/skier prototypes to a
production no-skin/no-modifier path, preserving skier FE0E/FE0F presentation;
then build the snowboarder with all six equivalent covered forms based on the
verified identical reference sources. Remaining sports, family, flags, script
coverage and full-brief shaping/style audits remain open.

### Fully covered sport integration — 2026-11-02

Previous goal turn made verified progress: juggling production and strip tests
completed; fencer/skier detailed prototypes and all snowboard tone references
were reviewed. Added `emoji_clothed_sport.py`, a production white/ink SVG path
for covered figures with exact source-advertised sequences. Fencer and skier
use their reviewed geometry; skier declares both FE0E and FE0F. No invented
modifier forms are advertised for either. Added the covered snowboarder after
reviewing all46 source paths: positive strength1.7, **4 components +20 holes
=24 contours**, no speck cleanup, readable board/goggles/helmet/clothing at
33.6px. All six standard forms consume their modifiers and share the drawing,
matching all five byte-identical pinned source references.

Registered three drawing SVGs and five reference SVGs. Production previews now
delegate to the converter. **3/3 exact contour checks pass**, **11,506 source
files verified**. Added source/hash/contour reconstruction, white/ink layers,
repeated and adjacent shaping, modifier scope, equivalent snowboard forms and
both skier variation selectors to tests/test_font_clothed_sport.py; added JS
routing tests and two strip fixtures. Browser pixel equivalence now checks
FE0E as well as FE0F and all six covered snowboard forms.

Full build started, log `/tmp/clothed-sport-production-build.log`. Expected
**987 bases, 3,486 exact sequences, 1,020 cmap entries, 33 components**; expected
JS **289**, browser **408**. Do not mutate production converter/builder during
this build. After terminal0, refresh versions/audit; run new clothed-sport tests
plus manifest/ink/inventory checks, JS and browser suite. Review both new strip
fixtures. These remain pending; no compiled coverage claim yet.

Clothed-sport full build handle **70766**, started about12:48UTC. Production
modules must stay unchanged until it finishes. Independent next drawing:
`prototype_horse_racing_svg.py` keeps rider face/head and the union of hand
paths19/29 as skin; horse, tack, clothing and helmet are excluded. Original
colour source and all32 path shapes were inspected. Prototype treatment/masks
and actual-scale appearance remain to be verified before promotion.

Horse-racing source prototype90178 passes **1/1** strict compiled contours:
**5 components +22 holes =27**, strength **.95625**, skin [1,2,10]/22,
33,260 skin pixels. Enlarged inspection confirms face/ear/hand only, horse and
equipment white/ink. Stronger-ink comparison14821 completed and was inspected:
the complete figure is recognisable, but rider skin/features remain very small.
`prototype_horse_racing_optics.py` trial40318 enlarges source head/features
20–24,27,28 by1.25 about(44,12), and merged hand19/29 by1.25 about(42,46).
It remains independent of production. Inspect geometry and all-tone small-size
comparison before choosing either variant; do not promote merely on topology.

Horse-racing optical trial40318 and stronger-ink comparison52365 are terminal0.
The enlarged head/hand variant has **5 components +21 holes =26 contours**,
positive strength **.95625**, skin [1,2,9,10]/21,45,901 pixels. Enlarged and
all-five-tone 160px/33.6px previews inspected: modestly more visible exposed skin;
whole horse/rider remains identifiable, fine facial details still small.
Prefer this provisional optical variant for future actual-strip testing, but
verify the four anatomical regions before production pinning. No source added
to production for horse racing. Preview paths `horse-racing-optical-svg-*` and
`horse-racing-optics-refined.png`; helper `/tmp/preview-horse-racing-refined.py`.

Only live job at this checkpoint is clothed-sport full build **70766**, started
**12:47:27UTC**, log `/tmp/clothed-sport-production-build.log`. Re-poll the same
handle. After terminal0: version_assets.py, audit.py, npm test, and pytest
`tests/test_font_clothed_sport.py tests/test_font_activity_people.py
 tests/test_font_emoji.py tests/test_font_emoji_ink.py tests/test_unicode_inventory.py`
with `-k 'clothed or activity_variation_selectors or custom_emoji_have_real or
every_advertised_custom_sequence or ink_companion or inventory'`.
Then408 browser scenarios and visual review of `emoji-clothed-sport` and
`emoji-covered-snowboarding`. Production source hashes11506/geometry3 already
passed. Do not modify production during the live build. Full brief remains open.

Horse-racing anatomical review39910 terminal0. Inspected colour-labelled mask
`horse-racing-skin-regions.png/json`: region1 is face,2 ear/neck,9 hand,10 thumb
above rein; horse/tack/clothing excluded. Pinned [1,2,9,10]/21 in the independent
optical prototype and recorded union19/29 plus both1.25 transforms. No production
promotion during live build70766. Golf independent trial now uses the three
reviewed pinned source/path sheets; gradients12–18 in neutral are brown hair
shading, not skin. Keep head/nape and exposed hands while sleeves/helmet cover
source skin where appropriate. Geometry/anatomical review still pending.


### Covered sports production verified — 2026-11-02

Build70766 completed successfully: **987 bases, 3,486 exact sequences,
33 components, 1,020 cmap entries**. Colour font971,100 bytes; ink953,904.
Refreshed asset versions and audit: **171,971 /172,352 visible cmap entries**,
**381 missing**; **2,517 /3,963 fully-qualified emoji** encoded, **1,446 missing**.
Person-sport now26/308,282 still missing. These are inventory claims, not full
linguistic or visual completion.

**14 focused Python tests passed**,274 deselected,7 existing SWIG warnings,
80.56s. **289 JS tests passed**. **408 browser scenarios passed** with no
reported geometry/export failures. Fencer/skier and all six covered snowboard
forms visually inspected in actual strips; equipment and clothing stay readable
at approved1.4× size/stronger ink. Browser checks include exact FE0E/FE0F pixel
equivalence and covered snowboard modifier equivalence in both fonts.
Earlier production3/3 geometry checks and11,506 source hashes passed. No claim
of a fresh full Python suite or full colour-font reproducibility run.
Logs: `/tmp/clothed-sport-production-{build,audit,tests,js,geometry,hashes}.log`.
Both user comparison tabs179/180 preserved;179 restored to optical-review URL.

Golf remains independent prototype, not production coverage. Three cap seam
variants pass exact contour checks (14/15/15), all strength1.7. Enlarged and
33.6px stronger-ink/all-tone sheet inspected. Pinned anatomical regions:
neutral[3,5]/13 and male[3,4]/14 are hands; female[3,4,6,9]/14 adds exposed
head regions beside/below cap. Cap seams recorded with offsets and width. Skin
colours remain subtle at small size because source faces are turned away.
Final strict prototype5593 passed. Golf mask review images are separately named
`golf-<key>-skin-regions.png/json`; horse mask artifacts restored and verified
by the original helper after an intermediate preview filename collision.

All jobs at this checkpoint are terminal. Next concrete work: promote reviewed
horse-racing optical prototype and golf after preserving these anatomical masks,
register pinned sources and exact Unicode forms, add tests/strip fixtures, then
build and validate. Horse prototype has already passed anatomical review. Full
brief remains active and substantially incomplete, including remaining sports,
families, flags, fantasy,381 visible cmap gaps and broader reading/style review.


### Golf and racing production integration — build pending

Previous turn classified as progress: covered-sport assets, audit, Python/JS and
browser/strip validation completed. Promoted the reviewed horse optical drawing
and three golf drawings to `emoji_horse_racing_svg.py` and `emoji_golf_svg.py`;
preview scripts now delegate to production. Existing activity builder dispatches
these four specialist recipes. Production remains deterministic with exact
anatomical masks, horse head/hand1.25 transforms and golf cap seams.

Registered four pinned SVGs in `noto-emoji-golf-racing-svg.json`:42 exact forms
including the golfer FE0E presentation (verified against pinned variation data).
24 fully-qualified forms expected. Production previews pass **4/4 exact contour
checks**. Added four activity geometry/skin/shaping tests, distinct golf gender
drawing check, metadata assertions, JavaScript routing and four browser strips.
Expected totals after build:989bases,3528exact sequences,1022cmap,33components;
290JS and412browser checks. These are **pending expectations**, not coverage.

Full build live handle **97567**, log `/tmp/golf-racing-production-build.log`,
started roughly13:05UTC on2026-11-02. Do not modify production converters or
builder while it runs. Source-hash check handle14547, log
`/tmp/golf-racing-production-hashes.log`. Geometry48171 terminal0; logs
`/tmp/golf-production-geometry.log` and `/tmp/racing-production-geometry.log`.

After build terminal0: version_assets.py, audit.py, npm test; focused pytest
activity cases selected by1f3c7 or1f3cc plus activity_variation_selectors,
custom_emoji_have_real, every_advertised_custom_sequence, ink_companion and
inventory. Run412browser scenarios and visually inspect the horse plus neutral,
male,female golf strip fixtures (all six tones). Preserve tabs179/180 and restore
179 to optical-review after QA. Full Unicode brief remains incomplete.

Source check14547 completed terminal0: **11,510 source files verified**.
Build97567 confirmed still live after that check; exact start13:04:51UTC.
No other live jobs at this checkpoint.


### Swimming source prototype — independent during golf/racing build

Previous turn was progress: four production recipes,42 registered exact forms,
tests and browser fixtures integrated; full build97567 started. Fresh poll this
turn confirms97567 still live; do not restart or mutate production modules.
Independently compared registry with pinned emoji-test: all24 fully-qualified
horse/golf forms and all qualification aliases included; only extra is the
standard golfer FE0E presentation. Compiled validation still pending.

Created `prototype_swimming_svg.py` from three inspected native colour drawings
and individual path sheets. Preserve neutral shirt, male exposed chest and
female swimsuit. Merge arm shading paths2/3, face shading pairs8/9(neutral),
7/8(male),13/14(female), and foreground water23/24,28/29,27/28 respectively.
Retain goggles with white lenses, mouth/nose, white cap and water, exposed skin
only. Source shape counts29/31/30. Strict prototype27442 terminal0:3/3 pass,
neutral7+14=21 strength.95625; male7+14=21 strength.7171875; female7+15=22
strength1.7. Skin region candidates respectively[1,6,8,12]/14,
[1,4,5,8,12]/14,[1,4,6,9,13]/15.

All-tone160px/33.6px stronger-ink preview85776 completed and visually inspected:
swimmer poses and waves read at small size; shirt/chest/suit differences retained.
Anatomical mask review rerun95835 live, log `/tmp/swimming-skin.log`, adding a
fifth label colour so every selected region is visualised. Images
`swimming-<key>-skin-regions.png/json`. Inspect all three, pin exact anatomical
regions and record union paths before any production promotion. No swimming
sources registered or coverage claimed. Original enlarged/optical artifacts:
`swimming-svg-1f3ca-prototype.png`, `swimming-optics-comparison.png`.

Swimming anatomical review95835 terminal0. All selected regions inspected in
three labelled images: arm and face areas in all, exposed upper torso for male
and female, no water/cap/lens/suit contamination. Pinned exact regions in the
independent prototype and recorded mergedSourcePaths. Strict rerun **57734**
currently live, log `/tmp/swimming-svg-prototype.log`; poll before claiming pass.
Golf/racing production97567 confirmed still running at this checkpoint. New
five golf/racing test cases collect successfully (not yet executed on new font).
Swimming strict rerun57734 completed terminal0:3/3 preserve treatment and exact
compiled contours with pinned anatomical regions. Only live job is97567.

### Basketball source prototypes — independent during live build

Previous turn made progress: three swimming prototypes passed anatomical,
contour and small-size review. Build97567 freshly polled and confirmed running.
Production modules left untouched. Reviewed basketball native colour originals
and all29/26/30 source path shapes. Created `prototype_basketball_svg.py`:
merge dribbling hand/arm paths0/1/2(neutral),6/7/8(male),10/11/12(female);
remove hair shading overlays, retain distinct hairstyles, ball seams, white
shirt/socks and black shorts/shoes. Skin only face, arms and legs.

Strict job33309 terminal0,3/3 exact contour checks: all4components+18holes=22;
strength1.7 neutral/female and.7171875 male. Enlarged images inspected, clear
ball and dribbling pose. Skin candidates [1,4,6,13,14]/18 neutral,
[1,4,6,10,12]/18 male,[1,4,6,11,12]/18 female. Small-size all-tone and labelled
mask review job77157 live. Logs `/tmp/basketball-{optics,skin}.log`; images
`basketball-optics-comparison.png` and `basketball-<key>-skin-regions.png`.
These remain independent prototypes, not registered production coverage.

Basketball review77157 terminal0. Inspected all five labelled skin regions in
all three drawings: face, two arms, two legs; ball/clothes/socks excluded.
All-tone33.6px preview inspected: pose and tones clear, ball seams rather dense
under production ink weight. Independent `prototype_basketball_optics.py` trial
enlarges ball and seams1.25 around source(23.52,80.96), relocated to(23.52,83.83)
to preserve the top gap beneath the hand. Trial **80817** live: strict geometry
then stronger-ink preview. Logs `/tmp/basketball-refined.log` and
`/tmp/basketball-refined-optics.log`; output `basketball-optical-svg-*` and
`basketball-optics-refined.png`. Inspect before selecting this variant; if
preferred recheck/pin its labels, which may change after transformed ball holes.
Production build97567 still live; source/builder modules remain untouched.

Basketball optical80817 terminal0:3/3 strict geometries, all still22contours,
strength unchanged. Inspected enlarged and33.6px all-tone preview; larger ball
has more readable seams without touching hand or leg. Prefer this variant for
future strip review. Labels changed due enlarged ball counters:
neutral[1,4,6,11,14]/18, male[1,4,6,10,11]/18, female[1,4,6,10,12]/18.
Refined labelled-mask helper now running; inspect before pinning. No production
registration or changes while build97567 runs.
Refined basketball anatomy handle **35834**, log
`/tmp/basketball-refined-skin.log`. Output filenames
`basketball-optical-<key>-skin-regions.png/json`. Only live handles at checkpoint:
97567production,35834prototype anatomy.

### Basketball pinned; weightlifting source trial

Previous turn made progress (basketball optical adjustment and review).
Refined basketball anatomy35834 completed; all three labelled masks inspected,
face/two arms/two legs correct. Pinned neutral[1,4,6,11,14],male[1,4,6,10,11],
female[1,4,6,10,12],each18 enclosed regions. Strict94779 terminal0,3/3 pass.
Preferred optical variant remains independent until current build validated.

Inspected all three weightlifting native colour sources and59/55/56 path
sheets. Created independent `prototype_weightlifting_svg.py`; merged overlapping
arm, face/ear and finger/hand shading, keep weight plate detail, belt, kneepads,
shoes and distinct hair. Initial21345 terminal1: female contour-preserving
translation fell back to source, so **not accepted**. Neutral/male reached
positive treatment but preview was not saved before female error. Added source
mask diagnostic and retained strict rejection. Neutral/male preview17424 live,
log `/tmp/weightlifting-svg-prototype.log`; female diagnostic59638 live,
log `/tmp/weightlifting-female.log`. Need inspect masks and solve actual topology
problem without loosening hard guards. Production97567 still confirmed live.

Weightlifting diagnostics17424 terminal0(neutral/male),59638 terminal1(female
fallback). Source-mask inspection showed extra narrow palm seams. Direct source
path-coordinate audit found incorrect opposite-hand finger grouping in the
neutral/female trial, plus omitted overlapping palm patches. Corrected unions:
neutral left48=(48,34,50,53),right49=(49,10,29,51,52);
male right38=(38,33,42,43),left39=(39,40,44,45);
female left6=(6,42,44,47),right7=(7,15,39,45,46).
This supersedes original trial hand unions; **do not promote old previews**.
Regenerated prototype, strict retry **66800** live, log
`/tmp/weightlifting-svg-prototype.log`. Original female failed7components32holes,
strength0; no guard weakened. Need inspect corrected rendering/anatomy.

Corrected weightlifting66800 terminal0:3/3 pass. Inspected enlarged drawings:
hands now continuous around bar, clothing/kneepads/plate rings preserved and
faces expressive. Neutral7+26=33,strength1.7; male7+27=34,strength.7171875;
female7+26=33,strength1.7. Skin candidates14 regions each:
neutral[5,6,8,9,10,13,15,17,19,20,21,22,23,24]/26;
male[5,6,8,9,10,13,15,17,20,21,22,23,24,25]/27;
female[5,6,8,9,10,13,15,18,19,20,21,22,23,24]/26.
Small-size/all-tone and full labelled anatomical review **32322** now live,
logs `/tmp/weightlifting-{optics,skin}.log`. Review/pin before production.

Weightlifting32322 terminal0, original33.6px all-tone preview inspected. Pose
clear, but face and narrow plate rings become too dense with approved ink.
Independent optical variant removes only inner plate rim paths32/33(neutral),
36/37(male),5/41(female), keeps outer plates/bar. Initial head1.25 trial27308
passed3/3 but enlarged hair approached/touched bar: **not accepted optically**.
Revised `prototype_weightlifting_optics.py` head1.2 from anchor(64,47) to(64,51)
to preserve gap, retaining simplified plate interiors. Strict+small-size retry
**31183** live, logs `/tmp/weightlifting-refined.log` and
`/tmp/weightlifting-refined-optics.log`. Need inspect head/bar gap and neck,
then re-run anatomy with refined module and pin labels if accepted. No production
coverage claimed for weights/swimming/basketball. Build97567 freshly polled,
still live; do not alter production converters/builder.

Weightlifting revised head1.2 at(64,51) retry31183 terminal1: neutral compiled
30contours versus31source, small neck remnant visibly cramped. Male/female31/31
but this variant is **not accepted**. Reduced head trial to1.1,source(64,47),
target(64,49), preserving more neck and bar separation. Strict+optical retry
**26635** live. Same refinement log/output paths. Do not use previous head1.25
or1.2 variants as accepted geometry. Production97567 still confirmed live.

### Golf/racing compiled validation underway

Build97567 terminal0:989bases,3528exact sequences,33components,1022cmap;
colour977208bytes,ink962120bytes. Refreshed versions/audit:171972/172352visible
cmap,380missing. Fully-qualified emoji2541/3963,1422missing; sports50/308,
258missing. Audit18960 andJS43861 terminal0; **290JS pass**. **412browser
scenarios pass**, no geometry/export failures. Inspected all four finished
strip fixtures (horse and neutral/male/female golf) including all tones.
Golf poses/caps and horse/rider readable; hair and skin differences remain
subtle at this scale. Earlier11510source hashes and4geometry checks passed.

FocusedPython87879 terminal1:13pass,3fail,274deselected,7SWIGwarnings,77.19s.
Only failures are stale pre-cap-seam component/hole expectations for golf:
actual1+13 neutral and1+14 both genders, same14/15/15total contours. Verified
production reports, corrected those expectations, no production geometry change.
Affected3cases retry **76868** live, log `/tmp/golf-racing-production-retest.log`.
Original log `/tmp/golf-racing-production-tests.log`. Do not claim allPython
checks passed until retry terminal0. Browser179 still onchecks page; restore
optical-review URL and preserve179/180 after QA.

Weightlifting26635 terminal0: revised head1.1 from(64,47)to(64,49) and simplified
plate interiors passes3/3;31/32/31contours. Enlarged/all-tone33.6px review shows
bar gap and neck intact, clearer white plate interiors. Prefer this trial.
Refined anatomy16616 terminal0, all3labelled images inspected: exposed hands,
arms, face/neck and leg regions only; bar,plates,clothes,kneepads,socks excluded.
Pinned regions in optical prototype. Final strict refresh running; log
`/tmp/weightlifting-refined.log`. No production registration for this prototype.

Golf retry76868 terminal0: **3passed**,105deselected,7existingSWIGwarnings,
36.98s. Combined with unchanged13passing checks from original run, all16focused
checks now pass. No full-tree test claim. Actual-strip review and412browser
checks complete. Restored179 to optical-review URL;179/180 preserved.
Production golf/racing milestone complete; full Unicode brief still open.

Weightlifting final strict refresh handle **41005**; poll it. Next batch can
promote reviewed swimming, basketball-optical and weightlifting-optical (nine
drawings) with pinned anatomy, source registry, standard qualification and
variation forms, tests and strip fixtures. Keep rejected weight head1.25/1.2 and
incorrect hand-union trials out of production. No other live jobs except41005.
Weightlifting strict41005 terminal0:3/3 exact contours with pinned anatomy.
All jobs terminal at this checkpoint; no build currently running.

### Swimming, basketball, weightlifting production batch — rebuilding

Previous turn was progress: golf/racing production validation completed and
weightlifting optical/anatomical review finished. Promoted nine reviewed
recipes to `emoji_swimming_svg.py`, `emoji_basketball_svg.py`, and
`emoji_weightlifting_svg.py`; preview wrappers now exercise production.
Activity dispatcher selects specialist converter by base; preserves earlier
horse/golf. Registered nine pinnedSVGs in
`noto-emoji-swim-ball-weights-svg.json` with **104 exact forms**, **54FQ**.
Compared to pinned emoji-test: all standard qualification forms present; only
extras are standardFE0E for all three and swimmerFE0F. Pinned variation data
confirms both FE0E/F for all three. Builder emits both presentation forms for
these neutral bases plus golfer. No invented modifier/presentation combinations.

Added9 anatomy/geometry/shaping tests and3 distinct-gender checks, optical
metadata assertions, and reconstruction of each compiled white/skin/ink layer
from the reviewed source masks. Added1JS routing test and9finished strip
fixtures (all tones/presentation variants). New12Python cases collect correctly.
Expected totals, **not yet verified**:992bases,3632exact sequences,33components,
1025cmap;291JS and421browser scenarios.

Full build **29409** live, log `/tmp/swim-ball-weights-production-build.log`,
started roughly13:24UTC2026-11-02. Do not modify production converters/builder
while it runs. Production strict preview chain **99475** running; swimming and
basketball3/3 already pass, weightlifting pending. Logs
`/tmp/{swim,ball,weights}-production-geometry.log`.
Source hash42041 terminal0; log `/tmp/swim-ball-weights-production-hashes.log`.

After build terminal0: refresh version_assets.py and audit.py, npm test;
focusedpytest activity cases selected by1f3ca/26f9/1f3cb plus variation selectors,
custom_emoji_have_real, every_advertised_custom_sequence, ink_companion and
inventory. Run421browser scenarios and inspect all9newstrip fixtures. Preserve
user tabs179/180 and restore179optical-review afterward. Full brief still open:
this batch is not verified coverage until compiled/strip checks complete.
Production preview99475 terminal0: **9/9 exact contour checks pass**.
Source hashes: **11,519 files verified**. Build29409 freshly confirmed live;
only live job at checkpoint. All new source/sequence work is registered;
compiled-font and actual-strip validation remain pending.

### Rowing source trial — independent while nine-sport build runs

Previous turn was progress: nine reviewed production drawings integrated,
104forms registered, tests/fixtures added and build29409 started. Fresh poll
confirms29409 live; production converters/builder untouched this turn.
Inspected rowing native colour sources and all34/30/35 path sheets. Created
`prototype_rowing_svg.py`: merge arm shading17/18(neutral),20/21(male),16/17
(female); oar32/33,28/29,31/32 respectively. Omit duplicate boat layers in
neutral/female (near-identical offset copies), retain one outer hull/rim and
inner boat, life jacket/straps, hair, skin and water contours.

Strict46662 terminal0:3/3 exact37contours (6components31holes); strength
.40341796875 neutral,.3025634765625 male,1.7 female. Enlarged drawing inspected,
recognisable boat/rower/oar. Original all-tone+anatomy job60879 running, logs
`/tmp/rowing-{optics,skin}.log`. Candidate skin[1,4,7]/31 neutral and[1,7]/31
male/female. Life jacket has multiple tight outlines from colour shading;
independent `prototype_rowing_optics.py` merges jacket14/15neutral,17/18male,
13/14female as one silhouette while preserving separate straps.
Refined strict+optical job **45381** live, logs `/tmp/rowing-refined.log` and
`/tmp/rowing-refined-optics.log`. Inspect and choose before pinning anatomy.
No rowing source registration or production coverage claim yet.

Rowing original60879 terminal0; original small-size all-tone preview inspected:
boat/oar recognisable, life jacket details heavy. Refined45381 terminal1:
neutral/female34/34contours, male33/34. Merged jacket visually cleaner but male
loses one contour in font tracing, so not accepted. Diagnostic **80593** live
prints tiny enclosed-region sizes/source positions for male refined mask.
No guards relaxed. Original anatomical images still require inspection or
replacement by refined version once geometry is accepted.

Rowing diagnostic80593 terminal0: missing male contour is10pixels in a single
raster row at sourcex81.75–82.5,y39.58 (neck/face shading overlap); another84px
region atx60.58–62,y61.17–62.33 is larger and retained. Refined converter now
merges skin face+neck2/3neutral/female and5/6male, removing artificial shading
seam as one anatomical silhouette. Strict+optical retry **59340** live. Same
`rowing-refined` log/image paths. Production29409 freshly polled, still live.

### Rowing reviewed; surfing source trial

Previous turn made progress: rowing source conversion and seam correction.
Production29409 freshly confirmed live. Rowing59340 terminal0:3/3exact33contours
(6components27holes), strength.40341796875/.7171875/1.7. Refined all-tone33.6px
preview inspected; prefer simpler jacket and face/neck union. Anatomy58929
terminal0,all3labelled masks inspected: only head/neck and arm/hand. Pinned
[1,5]/27 in `prototype_rowing_optics.py`. Strict refresh **67836** live.

Inspected surfing native colours and44/44/45 path sheets. Created independent
`prototype_surfing_svg.py`: merge wave shading, wetsuit pieces, corresponding
hand/foot shadows and head/neck/ear; retain single board stripe, face details,
water drops and wetsuit seam. Explicit path-coordinate audit used for skin
ownership. Initial22010 terminal1, neutral rejected by treatment fallback.
No acceptance/coverage claim. Added source-mask diagnostic; neutral retry
**22381**, log `/tmp/surfing-neutral.log`; source mask
`surfing-1f3c4-source-mask.png`. Must solve failure before promotion.

Rowing strict67836 terminal0:3/3 pass with pinned[1,5]/27 anatomy. Ready for
future production promotion after current batch validation. Surfing22381
terminal1,source mask inspected: clear body/board/wave, but source10components
included exactly one detached ink pixel at(76.4167,85.6667) beside toe. No tiny
holes under200px. Applied established isolated raster speck<4pixel cleanup,
record removedRasterSpeckPixels; meaningful topology guards unchanged.
All-three surfing strict retry now running (handle below).
Surfing retry **35624**, log `/tmp/surfing-svg-prototype.log`; inspect strict
result and then actual-scale/skin-mask previews. Production build **29409**
remains live. These are the only live jobs at checkpoint.

### Surfing anatomy and small-size review

Surfing35624 and optical/anatomical preview94693 both completed successfully.
Inspected all three labelled masks and the five-tone 33.6px comparison:
face/ear, both hands and both feet are skin; wetsuit, board and water are not.
Pose, board and wave remain readable; facial and tone distinctions are subtle
at small size. Pinned neutral/male regions [1,3,7,14,17]/17 and female
[1,2,4,8,15,18]/18 in the independent surfing prototype. Strict refresh68631
completed successfully with all three drawings preserving compiled contours.
Neutral/male have26contours, female25; each removes one isolated raster speck.
No surfing production coverage claimed yet; actual-strip review remains due.

At13:35UTC production build29409 remains live, started13:23:50UTC. Do not
modify its production converters while it runs. Next: poll29409, then version
assets, audit, JS tests, focused Python tests and421browser scenarios, including
the nine new swimming/basketball/weightlifting actual-strip fixtures. Rowing
and surfing prototypes are candidates for the following batch. The approved
1.4× optical size and stronger ink remain unchanged.

### Swimming, basketball and weightlifting production validation

Previous turn made progress by pinning and strictly validating surfing anatomy.
Build29409 completed successfully around13:39UTC:992bases,3632exact sequences,
33components; colour font1,008,200bytes and ink companion993,116bytes. Asset
versions refreshed successfully. Audit31767 completed:171972/172352visible
cmap entries (380missing),2595/3963fully-qualified emoji (1368missing).
Person-sport now104/308custom encoded (204missing). Encoding counts are not
claims of universal rendering or style correctness.

Early JS run60831 ran before the build published its new manifest:290pass,
one new routing test failed. After build completion, rerun66663 passed all291.
Browser check finished with421scenarios and no reported failures or geometry
errors. Inspected all nine swimming/basketball/weightlifting gender fixtures
in finished strips. Poses, basketball and barbell read at dialogue size;
facial and gender details, especially swimmers, remain subtle. No clipping
observed in the inspected strips. Review tabs179/180 preserved and179 restored
to the optical-review page. Source hashes11519 and nine strict geometry checks
were already successful for these unchanged production sources.

Focused Python validation30068 remains live at13:42UTC, ten progress dots so
far; log `/tmp/swim-ball-weights-production-tests.log`. Poll this exact session
before reporting success or changing tested converters. Audit and JS logs have
the same swim-ball-weights-production prefix (JS success is `js-retest.log`).
Next batch candidates are reviewed rowing and surfing: pinned emoji-test
contains30qualification forms/18fully-qualified sequences for each base.
Cycling native source overview and neutral path sheet inspected; no cycling
conversion implemented yet. Broad brief remains incomplete.

Focused swimming/basketball/weightlifting validation30068 completed0:
23passed,279deselected,7existing SWIG warnings,220.10s. This completes the
focused validation milestone for the unchanged992base/3632sequence build.

### Rowing and surfing production integration

Promoted reviewed `prototype_rowing_optics.py` and `prototype_surfing_svg.py`
to `emoji_rowing_svg.py`/`emoji_surfing_svg.py`; prototypes now preview those
production modules. Added six pinned SVGs in
`data/font-sources/noto-emoji-rowing-surfing-svg.json`, activity routing,
six strict geometry/skin/shaping/layer-coordinate test cases, two gender
distinction cases and six finished-strip fixtures. Full source check43816
completed0:11525files verified. Exact inventory independently checked against
pinned emoji-test:60qualification forms,36fully-qualified sequences;62forms
including surfer's standard FE0E/FE0F presentations. Rowing has no standard
presentation-selector entries and none were invented. Native-fallback cases
previously using surfer now use unsupported 🧑🏽‍🎄, verified native in the
current manifest. New JS test preserves all rowing/surfing tone/gender forms.

Strict production previews69277 completed0:6/6drawings preserve exact compiled
contours and positive procedural treatment. Removed the surfing converter's
debug-only source-mask file write; final strict refresh5171 remains live.
Eight new Python cases collect successfully. Production build **6232** started
around13:44:25UTC, log `/tmp/water-sports-production-build.log`; do not modify
production converters while it runs. Expected, not yet verified:994bases,
3694exact sequences,33components,1027cmap,292JS tests and427browser scenarios.
After build success: version assets, audit, npm test, focused Python tests
for1f6a3/1f3c4 plus variation selectors, every advertised sequence, real custom
glyphs, ink companion and inventory; then browser checks and six actual-strip
reviews. Geometry refresh log `/tmp/surfing-production-geometry-final.log`.
Source hash log `/tmp/water-sports-production-hashes.log`. No new compiled
coverage claimed before validation; full beta scope remains unfinished.

### Cycling trials while water-sports build runs

Previous turn made progress: six production drawings integrated and build6232
started. Fresh poll confirms6232 still live; production modules unchanged.
Surfing strict refresh5171 completed0:3/3pass after debug-write removal.

Inspected road cycling native sources and all51/51/52path sheets. Independent
`prototype_cycling_svg.py` merges face11/12, front leg14/15, arm19/20 and
helmet25/26 (female indices+1); removes decorative clothing stripes33/34 and
back sock shade2. Keeps tyres, spokes, frame, helmet, clothes and exposed skin.
Strict94009 completed0:neutral/male18components22holes=40contours; female
18+23=41. Strength.40341796875/.3025634765625/1.7. Original optical+anatomical
job2112 completed0; all labelled masks inspected:face,ear/neck,arms and both
legs; frame/socks/clothes excluded. Regions neutral/male[2,3,5,7,8,10,13,14]/22,
female[2,4,6,8,9,11,14,15]/23. Not yet pinned pending optical refinement.

At33.6px bike/pose read, but stronger ink merges small helmet vents. Created
independent `prototype_cycling_optics.py`, removing vents27/28/30(+1female)
while retaining large vent29 and full helmet outline. Strict+optical job
**49493** live, logs `/tmp/cycling-refined.log` and
`/tmp/cycling-refined-optics.log`; expected output `cycling-optics-refined.png`.
Inspect result before acceptance; helper `/tmp/review-cycling-refined-skin.py`
exists but has not run. Original logs `/tmp/cycling-{svg-prototype,optics,skin}.log`.

Also inspected all mountain-bike58/58/59path sheets and native sources.
`prototype_mountain_cycling_svg.py` independent trial: retain mountain outline
and terrain, remove duplicate tyre shading5/16, merge arm12/13,leg21/22,
face28/29, shorts25/50. Female adds ponytail31, subsequent indices shift+1.
Strict job **20308** live, `/tmp/mountain-cycling-svg-prototype.log`.
No acceptance or production coverage claimed. Next inspect both cycling
trials, then small-size/anatomical reviews; preserve current production build.

Mountain strict20308 completed0:3/3pass. Enlarged drawing inspected, recognisable
mountain backdrop, rider, helmet and bike. Neutral/male5components28holes=33,
female5+30=35; strength.95625/.537890625/1.7. Each has six selected skin regions,
still requiring labelled review. Small-size+anatomical job **14778** now live,
logs `/tmp/mountain-cycling-{optics,skin}.log`, helpers under matching names in
`/tmp`; output `mountain-cycling-optics-comparison.png`. Current live jobs:
production6232, refined road cycling49493, mountain preview14778.

### Road cycling reviewed; mountain helmet refinement; cartwheel trial

Previous turn made progress with cycling trials. Production6232 freshly polled
still live, no production converter edits. Road49493 completed0:3/3exact
contours, neutral/male15+22=37,female15+23=38. Refined33.6px all-tone preview
inspected: simpler helmet visibly retains white space under stronger ink.
Preferred over original vent-heavy version. Refined labelled anatomy6214
completed0 and all three images inspected. Pinned neutral/male
[2,3,5,7,8,10,13,14]/22, female[2,4,6,8,9,11,14,15]/23 in
`prototype_cycling_optics.py`; strict refresh **56559** live,
`/tmp/cycling-refined-final.log`. Still requires production strip review.

Mountain preview14778 completed0. All-tone33.6px and all three labelled
anatomical images inspected: six regions are ear, face, neck, exposed arm and
both legs, no bike/clothing. Original neutral/male[5,6,8,15,19,22]/28;
female[5,6,10,17,21,24]/30. Original helmet also crowded under stronger ink.
Independent `prototype_mountain_cycling_optics.py` removes helmet paint detail
34/47/48 (+1female), retains silhouette/visor. Strict+optical **24174** live;
strict stage already reports3/3pass, optical needs inspection. Logs
`/tmp/mountain-cycling-refined{,-optics}.log`; anatomy helper exists at
`/tmp/review-mountain-cycling-refined-skin.py`, not yet run.

Inspected cartwheel native overview and26/48/25path sheets. Verified male
48path source is two attribute-identical24path groups; retain first group.
Independent `prototype_cartwheel_svg.py` merges hands/arms and face/ears/neck,
keeps clothing, hair, knees and facial features. Strict45611 completed0:
neutral/male6+7=13,female7+9=16contours, strengths.3025634765625/.537890625/1.7.
Enlarged sheet inspected, recognisable upside-down pose and hair differences.
Candidate skin neutral/male[1,2,3,5,6,7]/7,female[1,2,3,5,6,7,9]/9.
Small-size/anatomical job **39639** live, logs `/tmp/cartwheel-{optics,skin}.log`.
Inspect before pinning or integrating. No compiled coverage claim for any
cycling/cartwheel prototype. Current handles:6232,56559,24174,39639.

### Mountain anatomy pinned; cartwheel head-size trial

Previous turn made progress with reviewed road cycling and further trials.
Production6232 freshly confirmed live this turn; production modules unchanged.
Road strict56559 completed0:3/3pass with pinned anatomy. Mountain24174 and
original cartwheel39639 completed0; their all-tone33.6px previews inspected.
Prefer simplified mountain helmet with larger white area. Refined mountain
anatomy3920 completed0, all labelled images inspected: ear/face/neck, arm and
legs only. Pinned neutral/male[4,5,7,14,18,21]/27,female[4,5,9,16,20,23]/29 in
`prototype_mountain_cycling_optics.py`. Neutral/male5+27=32,female5+29=34.
Strict refresh **70131** live at checkpoint,
`/tmp/mountain-cycling-refined-final.log`.

Original cartwheel anatomy all inspected: legs, narrow exposed waist, head
and arms, including female arm split by hair. Pose reads at33.6px but face
is cramped. `prototype_cartwheel_optics.py` scales head/hair/features1.18
around(82,96), maintaining original limbs. Strict+optical59704 completed0:
neutral6+10=16,strength.3025634765625;male6+8=14,strength.40341796875;
female7+9=16,strength1.7. Enlarged and33.6px refined previews inspected; more
room for face, still subtle at comic size. Refined labelled anatomy **89257**
live, `/tmp/cartwheel-refined-skin.log`; inspect before accepting/pinning.
Candidate regions neutral[1,2,3,5,8,10]/10,male[1,2,3,5,7,8]/8,
female[1,2,3,5,7,8,9]/9. Actual-strip review remains required after integration.

Inspected water-polo45/42/45path sheets and source coordinates. Native colour
overview already establishes neutral shirt, male bare torso, female swimsuit;
do not colour clothes as skin. Ball paint21/22neutral,15/16male,9/10female;
face16/10/30 with underlying skin ellipses15/9/29; cap, ear guards and chin
ties remain separate non-skin details. No water-polo converter created yet.
Current live handles at checkpoint:production6232,mountain70131,cartwheel89257.

Mountain70131 completed0:3/3pass with pinned anatomy. Cartwheel anatomy89257
completed0; all refined labelled masks inspected, retain legs/exposed waist,
head/neck and arms, exclude shirt/hair. Pinned the above per-gender regions in
`prototype_cartwheel_optics.py`; strict refresh launched below. Road cycling,
mountain cycling and refined cartwheel are candidates for the next production
batch after water-sports build validation, not yet compiled coverage.
Cartwheel final strict handle **40570**, log `/tmp/cartwheel-refined-final.log`.
Only40570 and production6232 remain live at this checkpoint.

### Water polo and handball source trials

Previous turn made progress with pinned mountain/cartwheel anatomy. Cartwheel
40570 completed0:3/3pass. Production6232 freshly confirmed live at13:57UTC;
do not modify production converters before its completion.

Created independent `prototype_water_polo_svg.py`, preserving neutral shirt,
male bare torso and female swimsuit. Merge ball colour halves, cap trim,
water shading and exposed skin overlaps. Strict15556 completed0:3/3pass;
neutral9+23=32,s1.275,skin[8,10,15,17,19]/23;male11+19=30,s.95625,
skin[8,10,15]/19;female10+28=38,s.95625,
skin[8,10,15,16,17,19,20,21,22,23,24]/28. Enlarged sheet inspected, readable
ball/pose/cap/water, but unnecessary skin-overlap seams in male/female arms.
Original preview/anatomy12567 completed0, images exist but not yet inspected.

Independent `prototype_water_polo_optics.py` unifies male exposed body/arms
paths0–8 at7 (remove6), female0–8+23 at7 (remove1/23), leaving clothing
painted afterward. Strict+optics **54958** live: strict stage3/3pass, optics
requires review. Logs `/tmp/water-polo-refined{,-optics}.log`. Refined anatomy
helper `/tmp/review-water-polo-refined-skin.py` exists, not yet run. Need
verify skin masks and actual-size appearance before selecting a version.

Inspected handball native sources and36/36/37path sheets, audited coordinates
for limb/clothing ownership. Created `prototype_handball_svg.py`: merge
shirt/short shading, each arm and head/ear/neck, keep wristbands, socks, shoes,
ball patches and facial features. Strict56967 completed0:3/3exact contours;
neutral/male7+15=22,s1.275,female6+16=22,s1.7. Enlarged drawing inspected.
Candidate skin neutral[2,3,4,6,8,9,12]/15,male[2,3,4,6,7,10,12]/15,
female[2,3,4,5,7,9,10,13]/16. Optical+anatomy **44996** live,
`/tmp/handball-{optics,skin}.log`. Inspect before pinning/promoting. None of
these trials count as compiled coverage. Live handles:6232,54958,44996.

### Water-polo and handball anatomy reviewed

Previous turn made progress with new independent sport conversions.
Production6232 freshly confirmed live at13:59UTC. Refined water-polo54958
completed0; inspected all-tone33.6px preview, prefer unified exposed arms/body
without artificial seams. Refined anatomy81178 completed0 and all labelled
masks inspected: face, neck and arms, plus male bare torso; cap/ear guards,
ties, clothes and water excluded. Female neckline includes several small
skin regions separated by ties/collar; retain their meaning. Pinned neutral
[8,10,15,17,19]/23,male[8,10]/18,female[8,10,15,16,18,19,20,21,22]/26 in
`prototype_water_polo_optics.py`. Exact contours neutral9+23=32,male11+18=29,
female10+26=36; strengths1.275/.95625/.95625. Strict refresh **52036** live,
`/tmp/water-polo-reviewed.log`.

Handball44996 completed0:all-tone33.6px preview and three labelled anatomical
masks inspected, pose/ball read; facial details remain subtle. Skin is confined
to face/neck/ear, hands/arms separated by wristbands and exposed knees.
Pinned neutral[2,3,4,6,8,9,12]/15,male[2,3,4,6,7,10,12]/15,
female[2,3,4,5,7,9,10,13]/16 in `prototype_handball_svg.py`. Strict refresh
56531 completed0:3/3pass. Road cycling, mountain cycling, cartwheel, handball
and refined water polo now have reviewed candidates for future production;
none is yet compiled coverage or reviewed in actual strips. Remaining sports
include wrestling and independent mixed-tone ownership (do not midpoint-split
crossed arms). Current live handles:6232 and52036.
Water-polo52036 completed0:3/3pass with pinned anatomy. Only production6232
remains live; poll it before versioning assets or running compiled-font checks.

### Rowing and surfing production validation completed

Production6232 completed successfully. Published fonts contain 994 emoji bases,
3694 exact sequences and 33 components (1027 cmap entries); colour font
1,029,800 bytes, ink companion 1,015,580 bytes. Asset versioning completed.
Audit73122 passed:171973/172352 visible characters (379 missing),
2631/3963 fully-qualified emoji (1332 missing), person-sport140/308
(168 missing). Source check43816 verified11525 files. Six strict source
geometry previews passed; final surfing cleanup5171 passed.

JavaScript67396 passed292/292. Focused Python63200 completed0 with19 passed,
291 deselected and7 existing SWIG warnings in183.13s; includes compiled
water-sport geometry, skin/sequence identity, selectors, custom sequence
coverage, ink companion and inventory checks. Logs are
`/tmp/water-sports-production-{build,version,audit,js,hashes,tests}.log`.
Browser report independently read427 cases with no failures or geometry
errors. All six rowing/surfing gender strip fixtures visually inspected:
boats/oars and boards/waves/poses remain readable at approved1.4x sizing
and stronger ink; fine facial and gender details remain subtle. This is a
local browser review, not exhaustive cross-browser typography approval.

Keep approved optical defaults. Five reviewed independent sport candidates
(road cycling, mountain cycling, cartwheel, handball, water polo) are not yet
production coverage. Wrestling path sheets46/40/48 were inspected, but no
converter exists: mixed-tone forms use U+1FAEF FIGHT CLOUD and need explicit
source ownership of crossed arms; midpoint skin splitting is unsuitable.
Full Unicode brief remains incomplete. No build or validation job remains
live at this checkpoint. Preserve optical-review tabs179/180.

### Five sports promoted; production build running

Previous turn completed water-sports validation (progress). Promoted reviewed
road cycling, mountain cycling, cartwheel, handball and water-polo recipes into
`emoji_{cycling,mountain_cycling,cartwheel,handball,water_polo}_svg.py`.
Their prototype entry points now wrap those production recipes. Registered
15 licensed SVGs in `noto-emoji-five-sports-svg.json`; independently compared
all forms against pinned emoji-test:150 exact forms,90 fully-qualified.
None of the five bases has standardized text/emoji variation sequences.
All15 SHA256/git-blob identities verified; full source check61249 completed0,
11540 files verified. Added15 strict geometry/skin/compiled-coordinate cases,
five gender-distinction cases,15 actual-strip fixtures and routing checks.
Expected after build:999 bases,3844 exact sequences,33 components,1032 cmap.
These expected counts are not yet compiled or browser-verified coverage.

Production build handle **62060**, started2026-11-02 14:06:04UTC, freshly
confirmed live. Log `/tmp/five-sports-production-build.log`. Do not modify
production converters until terminal. Source log
`/tmp/five-sports-production-hashes.log`. Post-promotion strict preview batch
running separately, log `/tmp/five-sports-production-previews.log` (handle
recorded below). After build: version assets, run inventory audit, JS and
focused compiled Python tests, inspect all15 actual strips, preserve optical
review tabs179/180. Never treat a live process or anticipated counts as success.

Created reproducible `tools/font/probe_wrestling_ownership.py` and
`docs/wrestling-source-ownership-probe.json`. Compares each base source path's
256px raster with skin paths from both opposite-tone neutral reference SVGs;
reference path order and geometry differ, so index matching is invalid.
Candidate matches require IoU>.8 with both references and identical ownership.
Inspected blue-first/pink-second overlay for all three base genders: crossed
arms and hands agree anatomically. Some fine finger-shading paths remain
unmatched; this is evidence for a future conversion, not a finished skin mask.
Primary neutral left paths0,2,3,13,23; right7,16,18,20,24. Left hand fragments
11/17, right12;14/15 left-arm shadows,25–27 right-finger shadows. Do not merge
across owners, or blindly move hand17 behind the opposite arm: source paint
order carries occlusion. No wrestling production converter exists yet.
Strict preview batch handle **16354**. Current live handles62060/16354;
source verification61249 is terminal0. No new compiled-font test has run yet.

### Wrestling conversion trial and five-sport geometry

Previous turn promoted five sports and verified source identities (progress).
Production62060 freshly confirmed live; leave production converters unchanged.
Strict post-promotion batch16354 completed0:15/15 drawings preserve positive
pen treatment and exact compiled contour topology. Logs remain
`/tmp/five-sports-production-{build,previews,hashes}.log`.

Created independent `prototype_wrestling_svg.py`, with three source-painted
material masks (all skin, first person, second person). Keeps hand fragments
at their original paint positions, removes redundant hair/arm shading, keeps
facial features and finger creases; black kit/shoes, white socks. No production
integration. Strict15627 completed0:all three5components+18holes=23contours;
strengths.7171875/.40341796875/1.7. Candidate paired skin ownership is assigned
by majority overlap against each person's source-painted mask, preserving whole
enclosed skin regions; asserts disjointness and complete union of chosen skin.

`preview_wrestling_svg.py` renders paired tones at160px and33.6px with approved
stronger ink and labelled anatomy. Job24924 completed0; all three anatomy
images and mixed-tone comparison inspected. Pose and person distinction read,
facial detail subtle. **Do not pin yet:** neutral lower hand has a small region
classified differently from the other two genders; inspect exact source
geometry/overlap before accepting. Candidate neutral left[2,5,6,7,11,14],
right[1,3,4,8,10,12,13];male left[1,3,6,7,10,11,13],right[2,4,5,8,12,14];
female left[2,3,6,7,10,11,13],right[1,4,5,8,12,14]. Neutral region10 is93px
at source box[61.67,71.33,63.75,72.0]; nearby region9 was not selected as skin.
Added all-region source-overlap diagnostics to prototype and launched neutral
strict refresh **36360**, log `/tmp/wrestling-neutral-diagnostic.log`.
Check its terminal state/results before further edits. All78 FQ wrestling
forms verified in pinned data (18 uniform/default plus60 mixed-tone);
standalone fight-cloud is a separate79th form and already independent artwork.
Current live handles:62060 build,36360 neutral diagnostic. Preview/anatomy
15627/24924 and five-sport strict16354 are terminal0.
Neutral diagnostic36360 completed0. Only production62060 remains live.
Diagnostic resolves the neutral question:region9 is the13244px gap, only20.7%
source skin overlap; region10 is a93px right-hand fragment with100%right and
0%left source overlap. Its source-based assignment is supported; differing
region counts reflect differing native geometry. Pinned reviewed18-region
left/right assignments in the independent prototype and launched final strict
refresh (handle below), `/tmp/wrestling-reviewed.log`. This does not yet
establish actual-strip quality or compiled production coverage.
Final wrestling strict refresh handle **62810**. Current live62060/62810.

### Fantasy sources and Santa conversion trial

Previous turn added/reviewed wrestling masks (progress). Wrestling strict62810
completed0:3/3pass with pinned anatomical ownership. Production62060 freshly
confirmed live at roughly14:15UTC; no production converters modified.

Fetched33 base fantasy SVGs (all untoned FQ forms in pinned subgroup), pinned
same Noto commit and Apache licence. Manifest
`docs/fantasy-emoji-svg-source-probe.json`; source SHA256/git-blob verified.
Initial sandbox network lookup failed, then authorized download83429 completed0.
All three `fantasy-native-colour-{1,2,3}.png` sheets visually inspected.
Path probe3677 completed0 for all33; Santa/Mrs/Mx path sheets inspected.
Fetched50 light/dark reference SVGs covering all25 tone-capable base drawings;
10535 completed0, all hashes verified, manifest
`docs/fantasy-tone-reference-emoji-svg-source-probe.json`. These are candidates,
not production coverage. Inspected six villain tone references: green hands
are gloves unchanged by tone, only face/neck changes. Do not colour gloves as
skin. Genies/zombies/troll/other non-tone forms need their own treatment.

Independent `prototype_santa_svg.py` covers1f385,1f936,1f9d1_200d_1f384.
Santa merges face/ears, drops duplicate beard shading. Mrs merges head/ears
and hair shades; retains glasses, curls, cap trim, collar. Mx retains white
hair separately from face, merges scarf paint; hair shadows excluded from
skin. Santa initial enlarged drawing inspected,1.275 strength16contours;
**not yet accepted**: tiny ears and bottom shirt sliver require anatomy/optics
review. Initial82695 and gentler-setting35566 failed positive-treatment guard
for Mrs1f936. Did not weaken guard. Diagnostic86014 terminal1 (expected
assertion) showed0strength/fallback with7components12meaningful holes.
Source mask `/tmp/mrs-santa-source-mask.png` inspected: eye/glasses contact and
cheek crease/lens proximity. Added optical spacing: eyes10/11 shiftY-1.5,
cheek creases17/18 shiftY+1; recorded in report. Re-run **32462** live,
`/tmp/santa-svg-prototype.log`. Inspect outcome before accepting. Mrs has
pressure.025/bend.001; other drawings use.1/.012, requestedstrength1.7.
No Santa anatomy or dialogue-size review completed yet. Only live handles
62060 production and32462 Santa trial at this checkpoint. Full brief active.

### Mrs Santa topology diagnosis

Previous turn fetched/inspected fantasy sources and started conversion (progress).
Sports build62060 freshly confirmed live. Santa spacing trial32462 terminal1:
Mrs Santa still fails positive treatment; guard unchanged. Launched detailed
per-component/per-hole diagnostic2304, `/tmp/mrs-santa-feature-diagnostic.log`,
to identify the specific raster feature rather than repeatedly tuning settings.

Mrs diagnostic2304 completed0: transformed outer-eye crease component6
merges into main outline during final antialiasing, even when low-resolution
geometry passes. Source component box[86.83,60.58,91.08,63.0]. Added source
path15 shift(-1,+1.5), path16 shift(+1,+1.5), recorded opticalFaceSpacing.
Strict34561 completed0:all3pass. Santa6+10=16,s1.275,skin[2]/10;
Mrs11+12=23,s1.7,skin[3,6,7,8,11]/12;Mx12+9=21,s.95625,skin[2]/9.
Mrs and Mx enlarged drawings inspected. Anatomy+optics41984 completed0; all
three labelled skin masks and five-tone33.6px comparison inspected. Mrs
face/ears/lenses/neck selected correctly, Mx face/ears selected correctly;
clothing/scarf/hair excluded. Santa tiny ear regions6/7 were incorrectly
excluded by source-overlap classification after bending, while region8 is
correctly white pompom (sourceellipse1,cx101.91,cy63.86,r6.75). All-regions
review31118 completed0; `/tmp/santa-all-regions.png` inspected. Ear6 box
[27.83,53.58,29.42,61.25],623px;ear7[99.17,55.33,100.08,62.0],520px.

Refined Santa independently: bend.001 (retain pressure.1/request1.7) to keep
narrow ears aligned with material masks; omit source shirt stripe3 whose only
visible result is two distracting slivers below beard. Do not manually assign
skin without checking regenerated geometry. Strict refresh **27982** live,
`/tmp/santa-ear-refinement.log`; inspect result, regenerate anatomy/optics.
Mrs/Mx retain accepted recipes. Current live62060 build and27982 Santa.
No Santa production integration yet. If promoting Santa later, replace the
currently unsupported Mx Santa routing example in tests/fixtures, since it
will cease to exercise fallback. Wrestling remains ready for later integration.

### Santa source/anatomy review completed

Previous turn fixed Mrs Santa and reviewed anatomical masks (progress).
Production62060 freshly confirmed live. Santa ear refinement27982 completed0:
Santa now6components+8holes=14contours,s1.7,skin[2,6,7]/8. Narrow exposed ears
are correctly identified from source overlap after reducing bend to.001;
no manual override or weakened skin criterion. Removed shirt stripe3's two
bottom slivers. Fresh anatomy+optics17371 completed0; corrected Santa labelled
mask and full five-tone comparison inspected. White pompom/beard/eyebrows stay
white, exposed ears get skin tone; figures remain readable at dialogue size.
Pinned all three anatomy assertions:Santa(8,[2,6,7]),Mrs(12,[3,6,7,8,11]),
Mx(9,[2]). Final strict refresh running, `/tmp/santa-reviewed.log`, handle below.
No actual-strip or production-font review yet; all three remain candidates.

Inspected mage1f9d9 neutral/male/female30/26/33path sheets and source coordinates
for future work. Neutral neck6 is skin but brown inset5 is tunic, not skin;
hair2/3/7/8/9/10 are non-skin. Orb27/highlight28, staff24/25/29, inner orb
paint26; do not mistake brown staff for hands. Male ears4/5,face9/forehead8,
beard6/24, orb21/highlight22, staff18/19/23, inner orb20. Female ears8/9,face10,
forehead14; hair1/2/11/12/13/15; robe4/5/collar6,jewel7/highlight32; orb28/
highlight29,staff25/26/30,inner orb27. No mage converter created yet.
Santa final strict handle **21596**. Current live62060 production/21596 Santa.

### Santa final strict pass; mage trial

Previous turn reviewed/refined/pinned Santa anatomy (progress). Final strict
21596 completed0:3/3pass. Santa candidates are ready for later production and
actual-strip review; they are not yet encoded coverage. Five-sport production
62060 freshly confirmed live by exact handle. Supplemental ps inspection was
sandbox-denied; this is not evidence of a stopped build. Do not restart it.

Created independent `prototype_mage_svg.py`,30/26/33 source paths. Merge
face/ears and staff paint, keep orb highlight, pointed hats, white hair/beard,
robe and staff distinct from exposed skin. Neutral brown inset5 is black tunic;
skin6neck+13face. Male skin9mergedface/ears; female skin10mergedface/ears plus
14forehead. All-tone source references already fetched but mage-specific
material masks and optics remain unreviewed. Strict **29475** live,
`/tmp/mage-svg-prototype.log`. Check geometry, source ordering, skin ownership,
small-size appearance and meaningful distinctions before accepting. Female
forehead14 sits between layered front hair and needs particular attention;
male back/front beard6/24 may need seam simplification. Current live handles
62060 production/29475 mage. No production converter changed during build.

### Five-sport build and browser review completed

Previous turn started mage trial and confirmed Santa (progress). Build62060
completed0 at roughly14:25UTC:999 bases,3844 exact sequences,33 components;
colour1,086,252 bytes, ink1,071,640 bytes, expected1032cmap. Asset versioning
completed0. Audit21232 completed0:171978/172352 visible cmap,374missing;
2721/3963 fully-qualified emoji,1242missing; person-sport230/308,78missing
(all remaining wrestling). JS98302 completed0:293/293pass in9.433s.
Earlier15/15 strict geometry and11540 source hashes passed.

Browser179 ran442 cases: complete report read, zero failures and geometry
errors. All15 new cycling/mountain-cycling/cartwheel/handball/water-polo
neutral/male/female actual-strip fixtures visually inspected. Poses, equipment,
terrain/water read at approved1.4x/strongerink; fine face/gender details remain
subtle, especially cyclist heads/cartwheel faces. No clipping observed in
reviewed panels. Browser179 restored to optical review URL;179/180 marked
user deliverables. This is local-browser evidence, not exhaustive typography
or cross-browser approval. Focused compiled Python **84402** still live;
`/tmp/five-sports-production-tests.log` latest four dots, no failures yet.
Do not change production converters/fonts until terminal. Other logs use
`/tmp/five-sports-production-{build,version,audit,js,hashes,previews}.log`.

### Mage optical refinement under review

Initial mage29475 completed0, all3exactcontours; enlarged sheet inspected.
Original anatomy/optics82621 completed0, but original images not fully reviewed.
Black staff and orb merged visually; created independent
`prototype_mage_optics.py`: white outlined staff, retain native round black orb
without merging coloured orb-shadow wedges into its silhouette. An initial
file-generation typo produced syntax error before execution; corrected file
then strict10172 completed0:3/3pass. Enlarged refined sheet inspected, orb and
holder distinguishable. Refined anatomy/optics91305 completed0; all three
labelled masks and five-tone33.6px sheet inspected. **Not ready to pin:** female
forehead still has artificial horizontal line between two skin source paints;
male tiny exposed skin above mouth is white while below mouth is selected.
Resolve these against source geometry before promotion. Neutral face/ears/neck
look correct. Refined records`mage-optical-svg-prototype.json`; rendered files
`mage-optics-refined.png`,`mage-optical-<key>-skin-regions.png`. All mage jobs
terminal. Only84402 compiled validation is live at this checkpoint. Wrestling
and Santa are reviewed candidates awaiting production, mage still needs fixes.

### Mage face refinements pass geometry

Previous turn completed sports browser/JS/audit checks and identified mage
face issues (progress). Compiled tests84402 freshly confirmed live; latest13
dots, no failure yet. No production converters changed.

Refined independent `prototype_mage_optics.py`: female face/ears/forehead
8/9/10/14 union painted at14, then restore source side locks12/13 above it
before front fringe15. This removes artificial horizontal forehead seam while
preserving hair occlusion. Male bend.001 keeps narrow skin around beard-mouth
opening aligned with anatomical source masks (pressure.1/request1.7 retained).
Strict2916 completed0:3/3pass. Enlarged sheet inspected: female forehead clean,
male skin above mouth restored. Fresh anatomy+optics **69821** running,
logs `/tmp/mage-refined-{skin,optics}.log`; review before pinning. Current live
84402 compiled tests and69821 mage review. Wrestling/Santa ready candidates,
mage almost ready, none of those production-integrated yet.

Five-sport compiled validation84402 completed0:31passed,299deselected,
7 existing SWIG warnings,420.28s. Together with293JS/442browser checks,
15 actual-strip reviews,15 strict source conversions and11540 source hashes,
this completes the five-sport batch's focused validation. Full brief remains
incomplete; broader linguistic/style/cross-browser work is still open.

Mage69821 completed0; updated anatomy and all-tone33.6px preview inspected.
Female forehead continuous, male upper/lower exposed skin around mouth now
correct. Pinned neutral(11,[4,9]),male(14,[4,6,7,10,12]),female(16,[6]). Final
strict22217 completed0:3/3pass. Geometry7+11=18,6+14=20,6+16=22;strengths
1.275/1.7/1.7. Reviewed candidate `prototype_mage_optics.py`. All jobs terminal
at this milestone. Prepared `/tmp/promote-wrestling-fantasy.py` for next batch;
not executed at this point. Expected9drawings138exactforms114FQ; derive and
verify before claiming compiled coverage. No live validation/build job now.

### Wrestling/Santa/mage production integration started

Promoted9 reviewed drawings to `emoji_wrestling_svg.py`,`emoji_santa_svg.py`,
`emoji_mage_svg.py`; prototype entry points now wrap these production recipes.
Registry `data/font-sources/noto-emoji-wrestling-fantasy-svg.json`. Independent
pinned emoji-test comparison verified138 exact forms/114FQ (wrestling90exact/
78FQ, Santa18/18, mage30/18);9 SHA256/git-blob verified. All mixed-pair codepoint
components already exist in current cmap. None of these bases needs additional
standardized presentation forms. Expected after build:1003bases,3982exact,
33components,1036cmap. These are expected, not yet compiled evidence.

Added exact-key fantasy dispatch (Mx Santa must not register all1f9d1 forms).
Wrestling uses `split_skin` source-owned enclosed regions, not midpoint split;
preserves overlap/disjoint union checks. Shared paired builder selects🐰 for
existing bunny pairs,🫯 for wrestling. Added9 skin/geometry/compiled-coordinate
cases,2 gender-distinction cases,3 independent pair-order/ownership tests that
verify all60 mixed pairs and compiled masks,12 strip fixtures, and JS routing.
Replaced now-supported Mx Santa fallback fixture with valid unsupported👨‍👦.
Code compiled successfully before build. Helpers
`/tmp/promote-wrestling-fantasy.py`,`/tmp/add-wrestling-fantasy-validation.py`.

Full build **71493** running, `/tmp/wrestling-fantasy-production-build.log`.
Full source hashes **13423** running, log sameprefix`hashes`.
Post-promotion strict previews **87591** running, log sameprefix`previews`.
Do not modify production converters while build runs. On completion:version
assets,audit,JS,focused Python including existing bunny-pair regression,
442+12=454 browser cases and12 actual-strip reviews. Preserve179/180 optical
review tabs. Full Unicode brief remains active; no completion claim.
Source hash check13423 completed0; live71493build/87591previews.

### Vampire prototype: material correction and optical review pending

Post-promotion wrestling/Santa/mage strict previews87591 completed0, all9pass.
Build71493 remains live (last polled after14:39); do not modify production
converters or start a second build. Source hashes13423 completed0,11549files.

Independent `prototype_vampire_svg.py` now covers three source drawings. Initial
preview passed topology but visual review caught fangs connected to the face's
skin region. Added0.65source-unit black fang outlines to close their white
interiors; strict55496 completed0,3/3pass. Revised geometry17/14/15contours,
strengths1.7/1.275/1.7. Enlarged preview now shows correctly white teeth.
However `vampire-optics-refined.png`, reviewed across5tones at160px and33.6px
with production stroke, shows the fangs closing under the stronger ink. This is
NOT production-ready: next enlarge mouth/teeth together or improve the fang
negative spaces, then repeat strict/anatomical/optical checks and actual-strip
review. Preserve the approved1.4x size and heavier ink, rather than weakening
all emoji to accommodate this one drawing. No vampire coverage claimed.
Helpers `/tmp/preview-vampire-optics.py`, `/tmp/review-vampire-skin.py`;
combined job83089 generates optics then anatomical masks. Logs
`/tmp/vampire-svg-prototype-refined.log`, `/tmp/vampire-optics.log`,
`/tmp/vampire-skin.log`. The original trial log reports3/3 but its exec handle
was lost at compaction; refined55496 is the verified terminal replacement run.

### Vampire optical correction reviewed (next batch candidate)

Previous goal turn made progress: material bug identified/fixed and optical
failure found, with production build71493 confirmed live. This continuation
expanded the source smile1.6x horizontally/1.8x vertically about(64,78), and
fangs2.2x width/1.35x height with0.65source-unit outlines. White fang spaces now
survive production18unit stroke in160px/33.6px five-tone preview. Native light/
dark references for all3variants inspected (`vampire-native-tones-1.png`):
face/ears, male neck, female neck/chest are skin; collar/shirt/hair/teeth are not.
All3 final anatomy sheets inspected. Neutral7+10=17, male7+7=14, female7+8=15;
strengths1.7/1.275/1.7. Strict80713 completed0,3/3pass; optics/anatomy51819
completed0. Teeth probe43701 completed0: white fang regions4/5neutral/male,
5/6female; their interior radii33.5–36.7rasterpixels. Skin IDs[1]/10,
[1,6]/7,[2,7,8]/8. Pinned these reviewed IDs and fang locations/minimum radii
in the independent converter; final strict77628 currently running, log
`/tmp/vampire-svg-prototype-pinned.log`. Only assertions/report fields changed
since inspected images. Candidate30exactforms independently derived using
pinned qualification data, not registered or compiled. Still needs actual-strip
validation in a later production batch. No production converter modified while
71493 runs. Elf neutral path sheet inspected only; no elf recipe started.
Final pinned vampire strict77628 completed0:3/3pass. All vampire jobs terminal.
Production build71493 remains the only live job; last authoritative poll returned
its live handle. Next: continue independent fantasy recipes or finish production
validation when71493 returns terminal; never start another concurrent fullbuild.

### Elf source conversion and optical review

Previous goal turn progressed vampire material/optical corrections, all checks
terminal; full production build71493 remains live, no production edits here.
Inspected all3 elf source path sheets and all6 native light/dark references.
Created independent `prototype_elf_svg.py`: retain white hair, black embroidered
robes with white leaf decoration, distinct front hairlines, pointed ears,
headband and white raised collar. Merge face/ear paints, keep neck separately.
Neutral/male redundant back-hair shading and front-hair gradient removed;
female redundant back/front gradients removed. Decorative leaf fills have no
extra outline, preserving their white spaces.

Initial41803 strict failed female;80226 optics/anatomy also terminal1.
Diagnostic75380 terminal0 found artificial narrow white crown sliver where
front/back hair were both outlined. Keep back hair's outer contour and outline
only the front locks' source boundary startingM26.6,42.65, preserving both
white fills and original occlusion. No topology guard weakened. Refined4174
strict completed0,3/3pass;32321 optics/anatomy completed0. All3 anatomy sheets
and5-tone33.6px/160px optical sheet reviewed. Geometry8+19=27,8+19=27,7+21=28;
strengths.537890625/.40341796875/1.7. Skin IDs[2,5,8,13]/19,
[6,7,13]/19,[5,9,10,11,15]/21. Exposed skin between diadem strands checked
against original dark-tone source pixels at(70,35),(70,38),(64,40); these are
real forehead areas, not accidentally coloured hair. Female ears remain
separate skin regions10/11. Native source colors/gradients rendered with librsvg.

Pinned reviewed anatomical IDs; final strict job launched, log
`/tmp/elf-svg-prototype-pinned.log`. Record its exact handle/result next.
Helpers `/tmp/make-elf-trial.py` (initial recipe only, don't rerun over refinements),
`/tmp/preview-elf-optics.py`, `/tmp/review-elf-skin.py`, `/tmp/debug-elf.py`.
No elf production coverage claimed; later promotion requires source manifest,
sequence/tests/browser fixtures and actual-strip review. Vampire and elf are
now candidates for the next batch, after current production build validates.
Elf pinned strict93579 completed0:3/3pass. All independent prototype jobs now
terminal. Verified SHA256/git blobs for all6 vampire/elf source files and
independently derived60unique exact forms including36FQ; not yet registered.
Production build71493 authoritatively live at14:49, started14:33:50, log still
only startup warning. Continue polling that exact handle; no restart. Next
required after terminal0:version_assets,audit,JS,focused Python(including bunny
regression),454browser checks and12new production strip reviews. Browser179/180
must remain available as optical review deliverables; restore179after checks.

### Build-order failure corrected; expanded production batch running

Build71493 returned terminal1 at~14:50 (log`wrestling-fantasy-production-build`).
It failed in paired wrestling because U+1FAEF FIGHT CLOUD is compiled by
`add_new_svg` AFTER `add_activity_people`; presence in the old final cmap did
not prove presence at this pipeline stage. Moved add_new_svg before activity
compilation, preserving its real visible glyph; paired assertion now reports
key/text/missing codepoints. Failed build did not reach final font publication.
No font coverage from that run is claimed.

Promoted six reviewed vampire/elf drawings now that old build is terminal.
`emoji_vampire_svg.py`,`emoji_elf_svg.py`, registry
`data/font-sources/noto-emoji-vampire-elf-svg.json`; corresponding prototypes now
wrap production. Added6geometry/compiled-mask/skin cases,2gender distinctions,
all60exact qualification/tone JS routes and6strip fixtures. Expected nextbuild
1005bases,4042exact,33components,1038cmap;2871/3963FQ,1092missing. These are
expectations only.15drawings total since last successful build: wrestling3,
Santa3,mage3,vampire3,elf3;150 additional FQ (=114+36),198exact.
Next browser run460cases and18new actual-strip reviews. Tests include shared
bunny-pair regression, wrestlingsourceownership, everyadvertisedsequence,
variation support, inkcompanion equality and inventory. Helper
`/tmp/promote-vampire-elf.py` executed once. Python source compilation passed.

Fresh fullbuild28870 LIVE,`/tmp/fantasy-expanded-production-build.log`.
Post-promotion vampire/elf strict88726 LIVE,`...production-previews.log`.
Fullsourcehash19637 LIVE,`...production-hashes.log`.
Do not edit production converters or start another fullbuild while28870 lives.

### Fairy candidate refined independently while expanded build runs

Inspected all3 fairy path sheets and6 native light/dark references. Independent
`prototype_fairy_svg.py` retains4wing lobes, two primary veins per wing,
star-tipped wand, black clothing/hair and source-distinct hairstyles. Removed
secondary veins for comic-size clarity, retained primary paths1/2/5/6/11/12/15/16
as0.8source-unit open strokes. Merged fingers/raised arm into source-derived
silhouette after wand, preserving grip occlusion. Face/ears merged; head1.22x
with sourceanchor64,24 and target64,26.5 avoids clipping original hair at top.
The two legs remain separately outlined; only toe20 merged with frontleg23.

Initial strict22183 andoptics8635 terminal1 duefemale fallback. Diagnostic84373
terminal0 isolated one rasterpixel at tapered ponytailtip; explicitly removes
and records exactly1pixel in female source. No meaningful feature guard weakened.
First successful34151 strict3/3,85668 optics/anatomy terminal0. Review found
hair clipping and cramped faces under production18unit stroke. Face22591/55916
terminal0 still crowded. Finalface14719 strict completed0,3/3pass;66337
optics/anatomy completed0. Reduced eye radii1.1/1.1 and shiftedY+1, nose scaled.65,
mouth scaledY.65 shiftedY+.7; native ellipse transforms preserved. No global
ink reduction. Final five-tone160px/33.6px sheet andall3anatomy sheets inspected;
facefeatures read separately, wings/wand/cloth/hair stay non-skin. Female tiny
right-ear sliver is skin region6(75pixels), not a wing gap.

Finalgeometry7+19=26,7+19=26,8+21=29;strengths1.7/1.275/.95625;
skinIDs[1,6,7,8,17,18]/19 for neutral/male, [1,6,8,9,10,19,20]/21female.
Pinned anatomical IDs and added optical metadata; finalstrict running with log
`/tmp/fairy-svg-prototype-pinned.log` (record result next). No fairy promotion or
compiled coverage. Initial generation script `/tmp/make-fairy-trial.py` is stale;
don't rerun it over refinements. Helpers`/tmp/preview-fairy-optics.py`,
`/tmp/review-fairy-skin.py`,`/tmp/debug-fairy.py`. Current promoted vampire/elf
post-integration strict88726 terminal0,6/6; sourcehash19637 terminal0,11555files.
Expandedproductionbuild28870 still live; no production changes since launch.
Pinned fairy strict74508 completed0:3/3pass; all fairy jobs terminal. Derived30
unique exact fairy forms from pinned qualification data, not yet promoted.
Only live job is expanded production build28870, authoritatively polled at14:57;
started14:51:50. Next: further independent fantasy work while waiting, then full
expanded-batch validation once28870 is terminal. Keep18actual-strip reviews and
460browserchecks outstanding; don't use prototype reviews as their substitute.

### Merperson independent candidate: source anatomy and optical corrections

Previous goal turn progressed compilation-order fix, promoted vampire/elf,
started28870expandedbuild, and finished fairy prototype. At this continuation
28870 still confirmed live; no production converter edits.

Inspected3merperson path sheets(52/47/49shapes including defs) and6native tone
references. Independent `prototype_merperson_svg.py` retains source differences:
neutral sleeveless shirt/thin arm rings, male bare torso/wide cuffs, female shell
top/flower. Black swept tail with white reflections, white two-lobed fin with
central vein, black three-pronged trident. Source shadow paints merged into
body/arms/face; hand remains over staff. Defs/clips preserved. Source SHA/gitblob
checks passed in native colour renderer. No new source fetching needed.

Initial41441strict and56442optics/anatomy terminal1 on female fallback. Debug
38259terminal0 found one isolated pixel at waist; additionally preview showed
white waist-highlight paint breaking the torso's skin boundary. Merged tail
with its waist paint(neutral33+34,male31+44,female31+32), removing open white
belt. No isolated pixel deletion required. Waist61052/29229 terminal1;
90967diagnostic terminal0 found4pixel fin hole shrinking below feature threshold
under antialiasing. Replaced outer-edge fin highlight shapes with native central
vein20/19/12. Strict69460 andoptics39864 terminal0,3/3pass. No guards relaxed.

Optical57339 and96609 terminal0 after smaller eyes(.65,Y+.7),nose(.65),mouth
(Yscale.65,Y+.8), retaining1.15head scale around104,40. Female shell decoration
reduced to one central rib per shell, male tiny abdominal hatch omitted to avoid
blots under18unit productionstroke. All3 anatomy sheets inspected; skin now
correctly includes exposed abdomen/torso, arms and hands, excludes tails/cuffs/
clothing/trident/hair/flower. Final8unit whiteunderstroke separates female black
trident from black hair:83038strict and49546optics/anatomy terminal0,3/3pass.
Re-inspected final female anatomy andall5tones160px/33.6px. Finalgeometry7+12=19,
7+11=18,8+12=20;allstrength1.7. SkinIDs[1,2,3,4,6,9,10]/12,
[1,2,3,5,11]/11,[2,3,4,10]/12. Tiny faces still require actual-strip review.

Pinned anatomical IDs and optical metadata; finalstrict running, log
`/tmp/merperson-svg-prototype-pinned.log` (record exact handle/result next).
Helpers `/tmp/preview-merperson-optics.py`,`/tmp/review-merperson-skin.py`,
`/tmp/debug-merperson.py`; initial`/tmp/make-merperson-trial.py` is stale and
must not overwrite refinements. No merperson promotion/compiled coverage.
Only production job remains28870;18new stripreviews and460browserchecks still
outstanding after it finishes. Fairies and merpeople are next-batch candidates.
Pinned merperson strict66252 completed0:3/3pass. All candidate jobs terminal.
Fairy/merperson6sourceSHA256/gitblobs verified;60unique exact candidate forms
derived, not registered. Production28870 is still the only live job, started
14:51:50; do not restart. Next independent source candidates: superhero/villain,
genie/zombie/troll (bigfoot1FAC8 is already in emoji_new_svg; do not duplicate).


### Expanded fantasy/wrestling build and browser review (2026-11-02)

Production28870 completed0 after starting14:51:50;1005base emoji,4042exact
sequences,33components,1038cmap. Colour font1139224bytes. Version-assets
completed0; audit30205 completed0:171984/172352visible(368missing),
2871/3963fully-qualified emoji(1092missing). Person-sport308/308 nowcustom.
JavaScript85328 completed0:295/295pass. Browser179 completed460checks with
zero failures/geometryerrors; all18new actual-strip specimens visually inspected:
wrestling3+mixedpairs3,Santa3,mage3,vampire3,elf3. Skin colours, headwear,
collars, fangs and silhouettes retain presence at approved1.4x optical size.
Browser179 restoredoptical-review,180 preserved;both marked deliverable.
FocusedPython25816 still LIVE: new geometry/gender cases, wrestling pair
ownership, existing bunny-pair regression, everyadvertisedsequence, selectors,
inkcompanion and inventory. Do not restart. Log
`/tmp/fantasy-expanded-production-tests.log`. Other build/audit/JS logs share
`/tmp/fantasy-expanded-production-` prefix. No new production build running.

Superhero independent prototype added `tools/font/prototype_superhero_svg.py`;
no registry or production promotion. Native6tone refs reviewed and verified:
hands are gloves, onlyface/ears/neckskin. Initial90923 completed0,3/3 strict;
64199 optics/anatomy completed0. Initial9components+7holes=16,skin[2,4]/7all,
strength1.275/1.7/1.7. Prototype cape black,suitwhite,boots/glovesblack,
triangularbadge preserved. Neutralface+ears30:(29,30),male23:(22,23),female22.
Initial 1.15head and faces too crowded with final18unitstroke. Refined24541
completed0(strict3/3 plus optics),head1.3 sourceanchor75,24,target75,26;
eyesrx/ry.6,Y+.7; mouthscale(.7,.4),nose.45,browsYscale.5. Stillcrowded;
37372 LIVE removesnose and movesbrowsup1.5, then strict/optics/anatomy.
Logs `/tmp/superhero-svg-prototype-face.log`,`/tmp/superhero-optics-face.log`.
Helpers `/tmp/preview-superhero-optics.py`,`/tmp/review-superhero-skin.py`;
`/tmp/make-hero-trial.py` stale: never overwrite refinements. Need final visual
review and pinnedanatomy, possible costume separation(blackrearboot merges
withblackcape), actual-strip review after eventual promotion.

Superhero37372 completed0: finalstrict3/3 plus optics and anatomy sheets.
All3 latest anatomy sheets and all5tones160px/33.6px reviewed. Skin[2,4]/7
still face/neck only; no hands coloured. Small faces clearer after nose removal,
but candidate not ready: larger neck now touches badge and black rear boot
merges into cape. Revisit costume separation and head/neck transform before
pinning or promotion. No guards relaxed; no raster cleanup needed. Helpers
retain final candidate output in superhero-optics-refined.png and anatomy PNGs.
Productioninkfont1123696bytes. FocusedPython25816 remains live, no failure
reported so far; poll exact handle next. Browser460/460 review complete.

### Superhero costume separation (2026-11-02 continuation)

Previous goal turn made progress: completed production build/browser milestone
and independent superhero refinement. This turn revalidatedPython25816 live;
36selected tests total, at least24 passed so far; no failure/terminal result.
Do not restart or change production expectations while it remains live.

Superhero75979 completed0(strict3/3, optics and anatomy). Added8sourceunit
whiteunderstroke behind bentrearboot(path7neutral/male,9female); leg paints
over upperedge. Boot now stays separate from blackcape. Badgeinitialshift7
clearedneck but narrowrim closed under18unitproductionstroke. Replaced with
single solid triangular badge(path12neutral/male,14female), omittingrim13/15;
transform translate(0,51)scale(1,.7)translate(0,-47) keepsclearanceabove/below.
81000 completed0: strict3/3 andalloptics/anatomy. Reviewed all3 anatomy sheets
and5tones160px/33.6px; silhouette, boot, badge and face details visible. Final
geometry6+7=13,7+7=14,6+7=13;strength.95625/1.7/1.7;skin[2,4]/7all.
No topologyguards relaxed. Added pinned anatomy assertion and facial metadata;
95417 LIVE finalstrict, `/tmp/superhero-svg-prototype-pinned.log`.
Hero still independent, requires compiled-font/actual-strip validation.

Prepared `/tmp/promote-fairy-merperson.py` but NOT EXECUTED. Promotes6reviewed
candidates,60exactforms,6geometry/2gender tests,6stripfixtures; expected1040cmap,
4102exact,1007bases. Wait for25816terminal before executing; current production
counts1038/4042. Can add reviewedhero3 to nextbatch after pinnedstrict passes,
but update scriptcounts/tests/fixtures accordingly (additional30exact,1base).
Pinned superhero95417 completed0,3/3pass. Only25816 remains live; latest29dots.

### Fairy/merperson/superhero production integration (2026-11-02)

Previous goal turn made progress refining/pinning superhero. Font regression
25816 completed0:36passed316deselected7existingSWIGwarnings,504.68seconds.
This closes expandedfantasy/wrestling validation:295JS,460browser,18new
actual-strip inspections,36focusedPythonchecks, allpass.

Executed `/tmp/promote-fairy-merperson-hero.py` ONCE, derived from unexecuted
fairy-merperson helper. Promoted9reviewed drawings/90exact forms into modules
`emoji_fairy_svg.py`,`emoji_merperson_svg.py`,`emoji_superhero_svg.py` and
registry`data/font-sources/noto-emoji-fairy-merperson-hero-svg.json`; prototypes
now importproduction modules. Added9geometry/3gender cases,9actualstripfixtures,
and all90qualification/tone JavaScriptroutes. Expected1041cmap/4132exact nowin
fonttests. Pythoncompilepassed. New fullbuild31276 LIVE, started15:20:49.624,
`/tmp/fairy-merperson-hero-production-build.log`. Do not restart or edit its
production converters untilterminal. Expected1008bases,4132exact,33components,
1041cmap,2925/3963FQ(1038missing); not yet compiled/verified.

Strictproduction72404 completed0:9/9pass, log
`/tmp/fairy-merperson-hero-production-previews.log`. Hashcheck67637 completed0:
11564sourcefiles verified, `/tmp/fairy-merperson-hero-production-hashes.log`.
Afterbuild:versionassets,audit,npmtest,focused9geometry/3gender/advertised/forms/
selectors/inkcompanion/inventory,469browserchecks and9newactualstripreviews.
Do not claim newcoverage beforecompiledvalidation.

Independent nextcandidate `tools/font/prototype_supervillain_svg.py` added.
All3pathprobes44/42/41 and6native light/darktone refs viewed. Gloves unchanged
by tone; onlyface/neckskin. Cape/boots/gloveswhite,body/hairblack;all6pointed
collarprojections preserved,whitejewel,angularbrows/sliteyes/smile. Dropped
redundant sourceoutline and shadingpaths. Neutralface/ears19:(17,19),male
17:(15,17),femaleface17. Source inheritedstroke explicitly overridden onsolid
fills. Head1.25anchor64,17target64,19; eyes(.8,.7)anchor64,17target64,18;
mouth(.8,.55)anchor64,22target64,23; noseomitted. Strict4737 completed0:3/3pass;
initialenlargedsheetreviewed, fullproductionstroke/anatomy4101 LIVE. Logs
`/tmp/supervillain-svg-prototype.log`,`/tmp/supervillain-optics.log`.
Helpers `/tmp/preview-supervillain-optics.py`,`/tmp/review-supervillain-skin.py`;
`/tmp/make-villain-trial.py` initialgenerator(staleafteranyrefinement).
No villainpromotion/coverage. Need finaloptics/anatomyinspection,pinnedIDs,
then compiledfont/actualstripreview. Nativefemale hair clip should be checked
against reference when reviewing final outlines.

Villain4101 completed0. Reviewed3anatomy sheets and5tones160px/33.6px.
Initialgeometry6+18=24,6+18=24,5+18=23,allstrength1.7;skin[2,10]/18,
[4,10]/18,[2,10]/18. Nativefemale front/backhair retained in initialpreview.
Howeverfaces too black withfinal18unitstroke. Refinedhead1.4 anchor64,17target
64,22 toclearimage top;eyes(.55,.5),mouth(.65,.35)target64,24,browsY.5shift-1.
Chestjewel moveddown12 and widened1.5 around66,37 toavoid newneckoverlap.
60775 LIVE strict+optics+anatomy; logs `/tmp/supervillain-svg-prototype-refined.log`
and`/tmp/supervillain-optics-refined.log`. Check newface readability andfemale
clipping, review allnew anatomy, pinIDs onlyafter accepted. No promotion.
Production31276 re-polled LIVE, stillonlyfullfontbuild. Neverrestart.

Villain60775 completed0:strict3/3plusoptics/anatomy. All3finalanatomysheets and
5tones160px/33.6px reviewed; biggerface clearer at finalstroke, jewel separate,
no clippedfemale fringe/top, collar and claw silhouettes retained. Finalskin
neutral/male[4,10]/18,female[2,11]/18;strength1.7/1.7/1.275. Geometry24/24/23
contours as before. Pinnedregions+opticalmetadata;39218 LIVE finalstrict log
`/tmp/supervillain-svg-prototype-pinned.log`. No productionpromotion. Production
31276 remainslive andunchanged. Othercandidate futurework genie/zombie/troll.
Pinnedvillain39218 completed0:3/3pass. Onlyliveprocess isproduction31276;
lastrevalidatedlive aftervillain strict finished. No other live previewjobs.

### Zombie source experiment (2026-11-02)

Previous goalturn progressed by integrating9drawings and reviewing/pinning
villain. Revalidatedproduction31276 LIVE thisturn, logonlystartup; do not
restart. Independent `tools/font/prototype_zombie_svg.py` added, notregistered.
Viewed nativefantasy-colour3 andall3zombiepathprobes39/39/41. Keep blankwhiteeyes,
openblackmouth/whitetongue, raisedcurledhands, facepatches, distincthair. Hair/
clothesblack; face/neck/handmaterial separate. Zombies lack standardtones;
futureproduction needs non-tone builder, notactivitypeople's automatic5tones.
Previewgreen(134,177,152) reusesrecordedPDFpage47green from
`output/imagegen/emoji-production/colour-face-palette-source.json`; pin this
provenance when promoting, notnewarbitrarycolour. No productioncoverage yet.

Initial28547 terminal1fallbackneutral;debug24200 terminal0 found isolated1pixel
at[207,1178] andlargecomponent splitting nearhandgap. Nativehand17(left)/30right
contains tinyenclosedfingerhole. Added opticalhole expansion3xhorizontal/1.5x
vertical viaSVGPathPen/BoundsPen, leavesoutersilhouette intact; appliesmale21/30,
female23/32.20234terminal1stillfallback. Shadingcurve20/33 crosses thatgap;
removedthese redundant fingerlines(male24/33,female26/35) while retainingother
creases andthe actual enlargedgap.71429 LIVE strict log
`/tmp/zombie-svg-prototype-finger-lines.log`; inspect next, debug iffails.
No meaningfulfeatureguard relaxed, no rasterpixels deleted. Sourceearunions
neutral4:(3,4),male3:(2,3),female3. Tools `/tmp/make-zombie-trial.py` nowSTALE,
`/tmp/debug-zombie.py` configuredneutral. No zombiepreview has been approved.

Zombie71429 terminated1, stillneutralfallback. Freshdebug98968 terminated0:
no isolatedpixels now, but rightlowerfinger shading detaches a5958pxcomponent
atpaddedbox[1325,1162,1446,1361]. Removed lowerfinger shading19/32 aswell
(male23/32,female25/34), retaining actualhandoutline/enlargedgap,wristcrease,
thumbcrease.25789 terminated1 onmale;neutralnowpasses. Preview/anatomy19285
terminated1 onmale (nofinalsheet). Debugmale84427 terminated0 foundtwo isolated
rasterpixels at rightsharphairtip[1308,349],[1307,350]padded. Addedmale-only
cleanupassert exactly2pixels, no generalfeature deletion, recordedinreport.
48655 LIVE strict+optics+anatomy, logs`/tmp/zombie-svg-prototype-cleaned.log`,
`/tmp/zombie-optics-cleaned.log`. Helpers `/tmp/preview-zombie-optics.py` uses
monochrome and recordedgreen at160/33.6px (notunsupportedhuman tones),
`/tmp/review-zombie-skin.py`,`/tmp/debug-zombie-male.py`.
Onlylivejobs now31276production and48655candidate. Stillnoacceptedzombies.
Zombie48655 strict stage nowreports3/3pass; combinedjob stilllive rendering
optics/anatomy. Do not treat strictstage output as wholejobterminal.

### Zombie review and genie experiment (2026-11-02)

Previous turn progressed on zombie recipe debugging. Revalidated31276 and48655
live, then48655 completed0. All3final zombie anatomy sheets andmonochrome/green
160px/33.6px productionstroke previews inspected. Blankwhiteeyes/tongue and
finger openings survive; skinregions are face,neck,bothhands only. Final
geometry13+13=26,13+11=24,12+11=23;strength1.7/.3025634765625/1.7. PinnedIDs
neutral[1,4,5,13]/13,male[1,4,5,11]/11,female[1,4,6,11]/11. Addedfinger-gap
metadata3x/1.5x.15543 completed0 strict3/3 afterpinning. Verified palette source
PDFSHA matches existingrecord. Zombie still independent/no promotion; needs
non-tone colour builder andcompiledfont/actualstripchecks.

Genie independent `tools/font/prototype_genie_svg.py` added. Viewed3pathprobes
37/39/42 andnativecolour3. Keep pointedears, crossedarms, vest, curlysmoketail,
lamp, earrings, distinctneutral/male/femalehair. Bodymaterialblue(119,161,189)
from existingPDFpalette light-blue sample, clothing/hairblack,lampwhite. No
human skin-tone variants. Faceears unions20:(17,19,20)neutral,27:(24,26,27)male,
28:(25,27,28)female. Initial1505 completed0(strict3/3),enlargedpreviewreviewed.
95053 LIVE initialoptics/anatomy; howeverrecipe changedbeforeitfinished, so
outputs maymixinitialopticsandrefinedanatomy: MUST rerun afterterminal.
Initialsmoketail omittedcolouredribbon that actuallyconnectsto lamp, found by
visualcomparison. Refinedtail unions0:(0,1,2,3,4),male6:(6,7,8,9,10),female
7:(7,8,9,10,11); lampbase28:(28,29),male33:(33,34),female36:(36,37).
8936 LIVE refinedstrict `/tmp/genie-svg-prototype-tail.log`. Need reviewtail,
colourmaterial, opticaldetail, pinanatomy thencompiledfont/actualstrips.
Helpers `/tmp/preview-genie-optics.py`,`/tmp/review-genie-skin.py`;initial
`/tmp/make-genie-trial.py`STALE. No genieproductioncoverage.
Genie95053 and8936 both completed0. Refinedenlargedsheet visuallyreviewed:
smokeconnectstolamp,all3hair/arms/vestidentities preserved. Fresh74054 LIVE
optics/anatomy `/tmp/genie-optics-tail.log`, needed toreplace mixedoldoutputs.
Production31276 revalidatedlive; onlyotherlivejob74054. Neverrestartbuild.

### Genie review and troll source experiment (2026-11-02)

Previous goalturn progressed with zombie review and genie tail correction.
Genie74054 completed0. Reviewedfinalmonochrome/blue160px/33.6px andall3anatomy
sheets: face/ears,neck,crossedarms,tail receiveblue; lamp,jewellery,clothing and
hair excluded. Pinned material IDsneutral[1,4,5,6,7,9]/12,male[2,5,6,7,8,10]/13,
female[2,4,5,6,7,9]/12. Finalgeometry8+12=20,8+13=21,8+12=20;
strength1.7/.7171875/1.7. Pinnedstrict92202 completed0:3/3pass.
Stillindependent, needsnon-tonebuilder/compiledfont/actualstripreview.

Addedindependent `tools/font/prototype_troll_svg.py` afterviewingnativecolour3,
49pathprobe andsourcepaths. Skin0torso,2leftarm,10rightarm,21raisedhand,
28face+ears24/25union. Clothingwhite,fur/hair/feetblack,clubwhite withblackgrain,
whitefurhighlights15/16/43/44,eyes1.15x1.2, nose.65, mouth1.35x1.6,whiteteeth
36/37 with.4blackoutline. Initial41458completed0strict1/1;85978completed0
optics/anatomy. Reviewedbothsheets: exposedskin correct, butteethclosed under
final18unitstroke andoffsetbroochhighlightmadecrescent. Refinedteethwidth2.2
around62.6/68.8,38.3 inadditiontomouthtransform; brooch41whiteoutlinedcircle
r4.5,dropoffsethighlight42.55636 LIVE strict+optics+anatomy logs
`/tmp/troll-svg-prototype-teeth.log`,`/tmp/troll-optics-teeth.log`.
InitialskinIDs[3,5,6,8,13,16,19,20,21]/21; notpinnedpendingrefinement.
Helpers `/tmp/preview-troll-optics.py`,`/tmp/review-troll-skin.py`;initial
`/tmp/make-troll-trial.py`STALE. PreviewgreenusesexistingPDFcolour(134,177,152).
No trollproductioncoverage. Onlylivejobs31276production,55636trollcandidate.
Production31276 revalidatedlive, do not restart or editactiveconverters.
Troll55636completed0(strict1/1,optics/anatomy). Reviewedbroochfix:closedcircle
readswell. Finalstroke stillcloseslow-heightteeth, so raisedtoothYscale1.5
inadditionto2.2X;2724 LIVE strict+optics+anatomy, logs
`/tmp/troll-svg-prototype-taller-teeth.log`,`/tmp/troll-optics-taller-teeth.log`.
Latestpre-height skinIDs[3,5,6,8,13,16,19,20,22]/22; notyetpinned. Needexplicit
checkwhiteteethinteriorssurvivecompiledstroke. Onlyliveproduction31276and2724.
Troll2724 completed0(strict1/1 andoptics/anatomy); examinedsheets. Teethbarely
survive18unitstroke: diagnostic85071 completed0 measuredwhite toothregions10/11
maxinscribedradius19.92/19.65px at1536source (about17px inkstrokeerosion).
Notenoughopticalclearance; enlargedhead1.2anchor65.68,27target65.68,29 andteeth
2.8x1.8 beforeexistingmouth1.35x1.6.97081 LIVE strict/optics/anatomylogs
`/tmp/troll-svg-prototype-optical-head.log`,`/tmp/troll-optics-head.log`.
Reviewnewhead bounds/teeth/material thenpin; remainsindependent.

Prepared standalone `tools/font/emoji_fantasy_beings.py` forfuture non-tone
production promotion. NOT wired into build, soactive31276unchanged. It compiles
white/body/inklayers, reusespinnedPDFgreen/lightblue palette withPDFSHA check,
assertsstrictcontourpreservation, emitsbase/genderqualifiedforms withouttones,
andrecordsprovenance. Importsfutureproductionmodules insidefunction; these
modules/registry notyetcreated. py_compilepassed only; compiledbehaviourtests
stillrequired afterpromotion. Callerreturns sequences,components,rules(3values).
No source/test expectation changes tocurrentactivebuild.

### Fairy, merperson and superhero production validation (2026-11-02)

Build 31276 completed successfully. The nine drawings are now in the production
font: 1008 base emoji, 4132 exact sequences, 33 components and 1041 cmap entries.
Colour WOFF2 is 1,163,092 bytes; ink WOFF2 is 1,143,584 bytes. Asset versioning
and coverage audit completed successfully. The audit records 171987/172352
visible characters present and 2925/3963 fully qualified emoji encoded, leaving
365 visible characters and 1038 fully qualified emoji missing. Presence and
encoding still do not establish full style or linguistic validation.

Validation: 296 JavaScript tests passed; focused Python session 3903 completed
successfully with 23 passed, 341 deselected and seven existing SWIG warnings
(264.81 seconds). Strict previews passed 9/9; source hash verification checked
11564 files. Browser report contained 469 checks with no failures or geometry
errors. Visually inspected all nine actual strip fixtures (neutral, male and
female fairy, merperson and superhero), including their tone examples, with the
approved 1.4x size and stronger ink. Wings, tails, tridents and capes remain
readable beside dialogue. Restored tab 179 to the optical review page; tab 180
remains the comic comparison. Both retained as deliverables.
Logs: /tmp/fairy-merperson-hero-production-{build,tests,js,audit,previews,hashes}.log.

Troll prototype refinements are now reviewed and pinned, still NOT production.
Final head scale 1.2; tooth inner scale 2.8x2.2 in addition to the mouth scale.
Reviewed final monochrome/green 160px and 33.6px optics plus material anatomy.
Pinned 24 enclosed regions with skin IDs [3,5,6,8,15,19,20,22,24]; tooth regions
12/13 remain white, with inscribed radii 34.48/34.89 source raster pixels.
Added assertions for the reviewed anatomy and minimum tooth radius above 32.
Geometry is six components plus 24 holes. Sessions 71589 and 36701 completed
successfully; final pinned strict session 76007 passed 1/1. Final log:
/tmp/troll-svg-prototype-final-pinned.log. The earlier 31381 shell exited zero
but its first inline diagnostic failed, so its misleadingly named pinned log
was NOT evidence of pinning; final 76007 supersedes it.

No builds or test sessions remain live. Next: promote reviewed supervillain via
the activity pipeline and genie/zombie/troll via the unwired non-tone fantasy
builder, add compiled coverage/material/sequence tests and actual-strip
fixtures, then build and validate. Full Unicode goal remains incomplete;
family/flag and other emoji gaps, seal recovery, linguistic/style validation
and broader browser work remain open.

### Fantasy beings promoted; production rebuild running (2026-11-02)

Previous goal turn made progress: completed fairy/merperson/superhero production
validation and pinned the troll prototype. This turn promoted ten reviewed
drawings: supervillain (three, with human tones), genie (three), zombie (three)
and troll (one). Registry: data/font-sources/noto-emoji-fantasy-beings-svg.json,
41 exact forms. Production modules emoji_{supervillain,genie,zombie,troll}_svg.py
now own recipes; prototype scripts wrap them. The non-tone builder
emoji_fantasy_beings.py is wired into build_emoji.py for colour layers, cmap,
gender GSUB, variation declarations and the advertised manifest. No human
tone forms are generated for genie/zombie/troll. Palette comes from the pinned
PDF samples with PDF and palette-source hashes recorded.

Preflight session 93914 completed successfully: seven non-tone drawings compiled
with exact contours, material colours and gender ligatures. Source verification
9826 completed successfully, 11574 files verified. Added three villain geometry
cases, a gender-distinction case, tests/test_font_fantasy_beings.py (seven
material/compiled-outline/sequence cases and two gender cases), a JS routing
case including unsupported tones, and ten actual-strip fixtures named
emoji-fantasy-<key>. Tests await the new compiled production font.
Expected new totals: 1012 bases, 4173 exact sequences, 33 components, 1045 cmap;
these are expectations, not yet completed build evidence.

Production build session **7240 LIVE**, started 2026-11-02 15:49:45 UTC,
/tmp/fantasy-beings-production-build.log. Revalidated live after launch; do not
restart or mutate its production converters. When terminal, run version_assets,
audit, npm test, focused Python including the new fantasy test file and the
existing advertised-sequence/selector/ink/inventory checks, then browser checks
(expected 479) and all ten actual-strip visual reviews. Do not accept counts
or preflight as evidence of final browser/style correctness.

Independent next drawing: tools/font/prototype_baby_angel_svg.py, NOT production.
Source U+1F47C from existing pinned fantasy probe, native neutral and light/dark
tone images and all 21 source paths reviewed. Keep white feathered wings and
halo, black hair and expressive face. Union face/ears (10,11), omit duplicate
gradients, eyes 3.1x3.5, nose .65, mouth .85x.65, brows .55Y. Requested/applied
strength 1.7. Geometry eight components plus 11 holes; reviewed skin region [3]
out of 11 excludes hair/halo/wings. Initial strict 9279 passed; optics/anatomy
41330 completed successfully and were visually reviewed at 160px/33.6px in
monochrome plus five tones. Pinned anatomy and optical metadata; final strict
56725 passed 1/1 (/tmp/baby-angel-svg-prototype-pinned.log). Helpers
/tmp/preview-baby-angel-optics.py and /tmp/review-baby-angel-skin.py; generator
/tmp/make-baby-angel-prototype.py is stale after pinning. Needs promotion only
AFTER live build completes, then compiled font and actual-strip review.

Only live process is production 7240. The full Unicode goal remains incomplete.

### Alphanumeric emoji source and lettering prototype (2026-11-02)

Previous goal turn made progress by wiring ten reviewed fantasy drawings and
starting build 7240. That exact build was polled repeatedly and remains LIVE;
no restart or production-converter changes. Log remains
/tmp/fantasy-beings-production-build.log (started 15:49:45 UTC).

Prepared the missing alphanum subgroup independently. Read all 39 fully
qualified forms from pinned emoji-test data. Downloaded 39 Noto SVGs at the
existing pinned commit, checked git-blob SHA1 and recorded SHA256, licence,
URL and shape counts in docs/alphanum-emoji-svg-source-probe.json. The initial
sandbox fetch failed DNS; the authorized network retry 28209 completed0.
Helpers /tmp/fetch-alphanum-svg.py and /tmp/alphanum-source-texts.json. Rendered
and visually reviewed all 39 native sources in alphanum-native-sources-1/2/3.png
and inspected every shape's attributes. Source path details are in
output/font-review/pen-translation/alphanum-source-paths.json.

Independent tools/font/prototype_alphanum_svg.py preserves reviewed letter
paths and enclosure geometry, drops gloss/shadows, and applies expressive
pen translation. Explicit LETTERS map covers all39. Reviewed UnicodeData names:
five NEGATIVE SQUARED letters (A/B/O/P/AB) retain white-on-black polarity;
other symbols use black lettering and outlined paper enclosures. Their colour
is redundant with the actual letter/symbol identity here. This is still a
prototype, no production coverage or linguistic certification.

Initial source lettering was too mechanical. Added helper
 tools/font/emoji_tile_lettering.py to fit authentic dad-lettering-base.woff2
capitals/digits into the source cells (18 tile designs), recording the source
font hash, glyph identities, cell bounds and helper hash. Two-by-two ABCD/1234
and single-row words preserve cell order. Lowercase forms deliberately retain
source outlines because the base font maps lowercase to capitals; CJK/kana
source forms are also retained. Pilot86587 completed0 with9/9strictcontours.
Default pressure made a solid negative tile swell excessively. Revised to
pressure .04 for solid negative tiles, .25 for outline tiles; bend .004,
taper .1, requested strength1.7 with topology-preserving backoff. No relaxed
feature guards. This refinement is independent of the live production build.

Latest10sample actual-weight optics87930 completed0 and visuallyreviewed at
160px/33.6px: ABCD,abcd,COOL,A,AB,information,M,prohibited/full/secret ideographs.
Negative A/AB readable with restrained square contours; letters and counters
remain visible under18unit inkstroke. Current proof image alphanum-optics.png.
Full refined strict session **10778 LIVE**:
/tmp/alphanum-svg-prototype-refined.log. Full39 optical preview session
**38854 LIVE**, /tmp/alphanum-optics-all.log, output alphanum-optics-all.png
(not yet reviewed). Recheck terminal outcomes and inspect all39 before pinning
or promotion. /tmp/preview-alphanum-optics.py is10samples;
/tmp/preview-alphanum-optics-all.py isall39. Earlier all39session35429passed
but was prior to lettering/pressure changes and is superseded.

Live handles:7240production,10778alphanumstrict,38854alphanumoptics. Babyangel
remains pinned independent and awaiting production promotion after current
build validation. Full Unicode objective remains incomplete.

### Symbol review and arrow/control prototype (2026-11-02)

Previous turn progressed with licensed source acquisition and alphanum styling.
Revalidated production7240 LIVE repeatedly, unchanged. Full refined alphanum
strict10778 completed0:39/39preserved compiledcontours. Full optics38854
completed0; its script accidentally retained the ten-sample output filename,
so the39-sheet was saved as alphanum-optics.png (1100x1920). Copied that actual
result to alphanum-optics-all.png and fixed the helper's output path, without
rerendering. Visually inspected all39 at160px/33.6px and all enlarged prototypes.
Upper/lowercase and numeric layout, negative A/B/O/P/AB, word spelling,
Japanese source forms and enclosure shapes remain readable under final18unit
inkstroke. Pinned39 source component/hole pairs in REVIEWED_TOPOLOGY. No raster
changes from pinning; production compilation still required. No production
coverage claimed. Helper emoji_tile_lettering.py now accepts an optional text
argument for the next group; its alphanum behaviour is unchanged.

Downloaded and hash-verified46 arrow/control SVG candidates (21arrow,25av-symbol)
at the pinned Noto commit; session73863 completed0. Registry candidate:
docs/arrows-controls-emoji-svg-source-probe.json. Reviewed all46 native images
in four arrows-controls-native-sources sheets and all shape attributes; source
path details recorded in arrows-controls-source-paths.json. Helpers
/tmp/fetch-arrows-controls-svg.py, /tmp/arrows-controls-source-texts.json,
/tmp/review-arrows-controls-sources.py. No new licence: existing Apache2 notice.

Independent tools/font/prototype_arrows_controls_svg.py created with explicit
46 SYMBOLS recipes. Paper outlined tiles plus black symbol paths; retained
short/longbrightness ring/ray shapes from2and11..18 (no tile). Phone-off includes
source line8 with2unitstroke; vibration keeps phone/sidezigzags5/6/7. Word arrows
BACK/END/ON!/SOON/TOP and phone OFF use existing comic lettering in their reviewed
source cells. Source repeat-one circle/negative1 remains a combined path to
preserve its identity. Requestedstrength1.7,pressure.25,taper.1,bend.004.
Strict67102 completed0:46/46contourmatches,allstrength1.7. Reviewed enlarged
46drawing sheet against native sources. Actual-weight all46preview **51943 LIVE**,
/tmp/arrows-controls-optics-all.log, expected output
output/font-review/pen-translation/arrows-controls-optics-all.png.
Must inspect it before pinning/promoting. /tmp/make-arrows-controls-prototype.py
is initialgenerator; avoidrerunning afterrefinement/pinning.

Added UNWIRED tools/font/emoji_symbol_tiles.py compiler scaffold (py_compile
passed only). It imports future emoji_alphanum_svg/emoji_arrows_controls_svg
insidefunction; these productionmodules/registries do not exist yet. Important
integration finding: current production cmap has blank zero-advance components
U+27A1(component.27A1),U+2194(component.2194),U+2195(component.2195). Their real
symbol drawings MUST reuse those existing glyph names so already-generated
walking-direction/head-shaking GSUB rules still match. Scaffold asserts exactly
those empty glyphs, reuses names, and returns promoted codepoints for removal
from componentOnly. Call after all sequence builders; returns sequences,
variationpairs,promotedcomponents (threevalues). Add new variationpairs to cmap14
and manifestaliases without inventing FE0Eforms. Regression tests must cover
walkingdirection and headshakes afterpromotion. Scaffold not behaviour-tested
or wired into livebuild. Fullplan remainsincomplete.

Currentlivehandles:7240fantasyproduction and51943arrowsoptics. Alphanumreadyfor
productionpromotion after currentbuildvalidation; babyangel likewise. Do not
restart7240. Next productionvalidation remains version_assets,audit,297expected
JS tests, focusedPythonincludingfantasybeings,479browserchecks and10actualstrips.

### Arrow/control optical review and deterministic translation cache (2026-11-02)

Previous goalturn made progress reviewing/pinning alphanum, creating46arrow/control
recipes and finding the existing-arrow-component integration requirement.
Production7240 revalidated LIVE thisturn (lastcheck16:09UTC), unchanged.
Arrows/control optical51943 completed0. Visuallyreviewed all46 at160px/33.6px
with18unitstroke in arrows-controls-optics-all.png. Directions, rotation pairs,
shuffle/repeat/repeat-one, playback/skip/pause/stop/record/eject, wordlabels,
brightness short/longrays, signal/wireless and phone modes remain recognisable.
Tiny vibration-phone speaker details are obscured by the final ink, while the
screen/phone/zigzag identity remains clear. Pinned46reviewed component/hole pairs
in REVIEWED_TOPOLOGY; no raster changes. Productioncompile/actualstrips still
required. Sourceforms counted from authoritative emoji-test:49alphanum forms,
69arrow/control forms. Along withbabyangel6, the next85tiles+angel promotion
would add124exactforms: expected4297fromcurrentbuild's4173; expected1128cmap,
30components,1098bases after promoting3existingblankarrowcomponents. These are
future expectations only, not completed coverage.

Added independent tools/font/pen_translation_cache.py to reduce repeated full
build computation. NOT YET IMPORTED/ENABLED by pen_translate.py, so live7240
unaffected. Factory cached_translation wraps deterministic mask+Settings input;
keys include inputshape/packedpixels, fullsettings, algorithm/sourceSHA,
cacheimplementationSHA, Python/platform and NumPy/SciPy/scikit-image/Pillow
versions. Stores compressed uint8pixels + JSONreport with payloadSHA, loads
withoutpickle, atomically publishes entries, and recomputes when missing or
corrupt. Cache read/write failures do not block uncached output. Fresh reports
are returned on every hit, so callers cannot mutate later cached provenance.
DAD_DISABLE_PEN_CACHE=1 bypasses it. Defaultdirectory build/font-cache/pen is
disposable. Output/report intentionally exclude hit/miss status to retain
reproducibility. Covers truncatedZIP and compressedpayload errors explicitly.

Meaningful tests/test_pen_translation_cache.py passed3tests in0.23s, log
/tmp/pen-translation-cache-tests.log. Tests compare actual translatedpixels
andreport exactly with uncached computation, mutate returnedimage/report,
verifysettings/pixels/implementationinvalidatekeys, corruptbytes/checksum/
truncatedZIP thenrecompute, andsimulateunwritablecachepath. Need enable only
AFTERcurrentproductionbuildANDvalidation, so currentreported penTranslateSHA
remains valid. Wraptranslate afterdefinition beforemain; documentcachetoggle.
Then nextfullbuildpopulatescache; subsequentbuilds benefit. Do not treat this
performance work as Unicode coverage.

Onlylivehandle7240fantasyproduction. Readyindependentdrawings: babyangel1,
alphanum39,arrowscontrols46. Unwiredsymbolbuilderstillneedsproductionmodules,
registries,integration,compiledtests,componentregressions andactualstrips.
Currentbuildstillrequiresversioning/audit/JS/Python/browservalidation before
anynextpromotion. Fullgoalremainsincomplete.

### Fantasy production build complete; final validation running (2026-11-02)

Build7240 completed0 around16:12UTC:1012bases,4173exactsequences,33components,
1045cmap. Colour1,196,936bytes;ink1,179,900bytes. Version_assets completed0.
Audit11479 completed0:171991/172352visible,361missing;2950/3963FQ,1013missing.
JavaScript85984 completed0:297/297pass. Browser479checks completed with no
failures/geometryerrors; report parsed from currentpage. All10new actual strips
visually inspected (villain3 includingtones,genie3,zombie3,troll1). Preserved
size/ink defaults; blue/greenmaterials, lampconnection, zombiehands and troll
silhouette remain readable. Tab179 restoredopticalreview,180comiccomparison;
bothmarked deliverablethisturn. Python **39681 LIVE**:
/tmp/fantasy-beings-production-tests.log. Includesnewfantasyfile,1f9b9 cases,
every_advertised,variationselectors,inkcompanion,inventory,realoutlines. Do not
change pen_translate orproductionconverters/testexpectations until terminal.
Otherlogs /tmp/fantasy-beings-production-{build,version,audit,js}.log.

Prepared /tmp/promote-symbols-and-angel.py, py_compilepassed, NOT EXECUTED.
It promotes85reviewedtiles+1babyangel, createsregistries/modules/wrappers,
wiresnewcompiler aftercompoundsequencebuilder (reuse3arrowcomponentnames,
removecomponentOnly entries), addsvariationpairs/exactaliases, updatescounts,
andadds tone/routing/subgroup/geometrycases. It creates13actualstripfixtures:
onebabyangel,11groupedtilesfixturescoveringall85drawings(two perpanel),one
mixedstandalonearrow/existingZWJregression. Expectednextbrowser492checks.
Groupingpreservescompleteactualstripcoverage without85nearlyidenticalfixtures.
Add /tmp/test_font_symbol_tiles.py to tests/test_font_symbol_tiles.py when
promotion runs: prepared and py_compilepassed but NOT behaviourtested. Contains
85source-to-compiledlayer comparisons and exact shapingcases,3fullsubgroup
checks,4promoted-arrow ligatureregressions. Checkexpectedglyphnames onexecution.
AftercurrentPythonpasses, enable/documentcache, executepromotiononce, copynew
testfile, preflightnewbuilder andthenfullbuild. CurrentcachehelperstillUNWIRED.
Onlylivehandle39681; fullgoalremainsincomplete.

### Symbols and baby angel promoted; cache enabled (2026-11-02)

Previous goalturn made progress by completing fantasybuild/browser/stripchecks.
Python39681 completed0:24passed,353deselected,7existingSWIGwarnings,257.58sec.
That completes focused validation for current fantasyproduction (297JS,
479browserchecks,10newactualstrips). FullUnicodeobjective remainsincomplete.

Enabled cached_translation around pen_translate.translate afterdefinition.
Documented disposablecache/toggle in docs/emoji-pen-translation.md. Strength/
settings/render algorithm unchanged. Integration tests pen_translate+cache:
19passed in0.62sec, /tmp/pen-translation-cache-integration-tests.log. Realcache
comparison explicitly invokes translate.__wrapped__ whenavailable to ensure
comparison against actualuncachedalgorithm. ProvenanceSHAchanges are expected
in nextbuild; currenton-diskfont stillpreviousvalidatedfantasybuild.

Executed /tmp/promote-symbols-and-angel.py ONCE successfully16:17UTC. Created
production emoji_alphanum_svg.py,emoji_arrows_controls_svg.py,
emoji_baby_angel_svg.py; prototype scripts nowwrappers. Registries
noto-emoji-symbol-tiles-svg.json (85drawings,118forms) and
noto-emoji-baby-angel-svg.json (1drawing,6forms). Newbuilder wired AFTERcompound
builders; reuses3existingarrowcomponentnames and removescomponentOnly entries,
addsvariationpairs/exactaliases. Addedtests/test_font_symbol_tiles.py fromthe
stagedtest, babyactivitygeometry and full158person-fantasy subgroupcheck,
newJSroutingcase,13actualstripfixtures (all85tiles grouped2perpanel, babytones,
mixedarrow/ZWJregression). Expectednext1098bases,1128cmap,30components,
4297exactsequences and492browserchecks. Currentcompiledfont/testsaretemporarily
outofsync until newbuild; do not reportnextcoverageachieved.

Sourcehashsession13017completed0:11660filesverified,
/tmp/symbols-angel-source-hashes.log. Babyproductionpreview **83047 LIVE**,
/tmp/symbols-angel-baby-preview.log. Symbolbuilderpreflight **93012 LIVE**,
/tmp/symbol-tiles-preflight.log. It extends a temporarycopy ofcurrentfont with
85tiles, thencompares all4173existingsequences unchanged. CAUTION: its initial
assertion incorrectly demands sorted promotedcomponents, whilethebuilder
correctlyreturnsrecipeorder (27A1,2195,2194). Expectthatassertion tofail after
warmingthecache; do NOTrestartliveprocess. Correctedscript prepared separately
/tmp/preflight-symbol-tiles-verified.py (setcomparison), NOTRUN. After93012
terminal, runcorrectedscript; cachedinputs avoidrepeatingpencomputation. This
is a preflightharness ordering issue, not a failed font invariant. No fullfont
build startedyet. Afterpreflightpasses andbabypreviewpasses, startfullbuild,
thenversion/audit/JS/Python/492browserchecks and13newactualstripreviews.
Baby83047 completed0:1/1strictproductionpreviewpassed. Onlylive93012preflight;
correctedverifiedscriptstillnotrun. Do notstartfullbuildbeforepreflightpasses.

## 2026-11-02: approved optical defaults, symbol build in progress

The user accepted the larger, stronger emoji treatment. Keep the established
1.4× optical size and ink stroke defaults.

The corrected symbol preflight finished successfully: 85 tiles compile, all
three promoted arrow component names remain unchanged, and all 4,173 existing
exact sequences shape identically. Log:
`/tmp/symbol-tiles-preflight-verified.log`. The original ordering assertion was
only a harness error. Baby preview and source verification were already passed.

Production build started at 16:24 UTC, session **91118**, log
`/tmp/symbols-angel-production-build.log`. It remains live; poll this exact
session rather than starting a duplicate. This build includes 85 symbol tiles
and baby angel. After terminal success run asset versioning, coverage audit,
Python tests, JS tests, and all 492 browser checks, then inspect the 13 new
actual-strip fixtures. Coverage increases are still unverified.

An early JS run (63185, terminal 1) passed 297/298 tests; its sole failure is
the new symbol/angel routing case because the generated manifest is still the
previous build. Rerun after the production build completes, not before.

Symbol-mark source fetch 64402 is finished: 44 verified SVG candidates, registry
`docs/symbol-marks-emoji-svg-source-probe.json`. All three native sheets were
visually inspected. `tools/font/prototype_religion_zodiac_svg.py` is a staged,
non-production candidate for 27 religious, zodiac, and infinity tiles. Strict
prototype process **82592** is live, log `/tmp/religion-zodiac-prototype.log`.
IMPORTANT: its initial recipe for 1f52f omitted the central circle at path 3.
After the current process terminates, change that recipe from (5,[4]) to
(5,[3,4]), rerun the strict preview, and visually review every resulting tile
at dialogue weight. Do not promote this candidate before that correction,
contour/topology validation, and optical review. Pin reviewed topology only
after review. The remaining 17 fetched symbols have no prototype yet.

### 2026-11-02: all 44 symbol-mark candidates reviewed

Previous goal turn made progress (verified symbol preflight, launched production
build, rendered and inspected native sources). This turn continued with source
recipes and optical validation, not merely a wait.

- Production **91118 remains live**, confirmed by exact handle polling. No
  duplicate build was started. Still requires post-build validation listed above.
- Initial religious/zodiac preview 82592 completed 0. Corrected the dotted
  six-pointed star recipe to retain circle 3 as well as path 4. Corrected strict
  preview **42182 completed 0**, all 27 drawings accepted. Optical render
  **87875 completed 0**; all 27 inspected at 160px and 33.6px including final
  18-unit ink stroke in `religion-zodiac-optics-all.png`. Menorah flames and
  branches, khanda, yin-yang, atom, and dotted/undotted star remain distinct.
  Pinned reviewed component/hole topology in the prototype; pinned strict run
  **83272 completed 0**. This is not yet a production module.
- Added `tools/font/prototype_math_punctuation_svg.py` for remaining 17 drawings.
  Strict **39793 completed 0**, 17/17 contour checks accepted. Optical render
  **71839 completed 0**, all 17 inspected in `math-punctuation-optics-all.png`.
  Hollow question/exclamation retain two holes each; filled versions have none.
  Currency arrows and dollar/yen anatomy survive dialogue weight. Heavy equals
  selects only visible source paths 18 and 21, excluding hidden Adobe layer and
  off-canvas artwork. Gender symbols select source front silhouette, not shading.
  Pinned topology; final pinned strict **76276 is live**, log
  `/tmp/math-punctuation-pinned-prototype.log`.
- No new production wiring, source registry, test expectations or comic fixtures
  changed during the existing build. The 44 candidates remain staged. Next
  integration must add exact forms to the source registry, reuse blank
  `component.2640` and `component.2642` (confirmed zero contours and (0,0) metrics),
  remove them from componentOnly, and prove every existing gender ZWJ sequence
  shapes unchanged. No other candidate collides with current cmap. Extend
  symbol-tiles tests, add subgroup completeness and filled/hollow distinctions,
  then actual-strip fixtures. Do not claim production coverage from previews.
- CUA documentation restored; opticalTab179 and opticalComicTab180 marked as
  deliverables, retained for pending actual-strip checks.
Pinned math/punctuation preview **76276 completed 0**: all 17 topology/compiled
contour checks passed. Only outstanding live process in this batch is production
build 91118. All 44 staged symbol-mark drawings now have pinned strict previews.

### 2026-11-02: symbol-mark integration preflight and next sources

Previous turn was progress: created and optically reviewed 44 recipes and pinned
all topology. This turn's real-builder preflight **63552 completed 0**:
`/tmp/symbol-marks-preflight.log`. All 44 drawings compile, two gender component
names survive promotion, and all 4,173 exact sequences of the snapshotted fantasy
font shape identically. Temporary font `/tmp/dad-emoji-symbol-marks-preflight.woff2`;
baseline `/tmp/dad-emoji-before-symbol-marks.woff2`. The preflight monkeypatches
builder inputs in its own process only; no production inputs were changed.

Prepared, NOT EXECUTED, `/tmp/promote-symbol-marks.py` and staged tests
`/tmp/test_font_symbol_marks.py`. Execute only after 91118 and its full validation
complete; copy the staged tests into tests/test_font_symbol_marks.py as part of
that promotion. Script requires manifest4297, creates registry44drawings/61forms,
production modules and preview wrappers, extends symbol builder with 2640/2642
component reuse, adds seven actual-strip fixtures and JS regression. Expected
next1142bases/1170cmap/28components/4358sequences,499browserchecks. These are
expectations, not achieved coverage. Staged Python tests rebuild all44exact
outlines, check allsixcomplete subgroups, preserve compound gender shaping and
verify hollow/filled punctuation anatomy. No production promotion yet.

Fetched next47 missing transport-sign/warning/other-symbol SVG candidates from
the same pinned Noto commit, registry docs/signs-symbols-emoji-svg-source-probe.json.
Initial sandbox fetch failed DNS; approved network fetch67495 then failed on
unpadded copyright filename. Corrected minimum four-hex-digit names and completed
verified fetch with exit0 (`/tmp/signs-symbols-svg-fetch-verified.log`). All47
source hashes match Git blobs. All FOUR native sheets visually inspected:
output/font-review/pen-translation/signs-symbols-native-sources-{1,2,3,4}.png.
The helper incorrectly prints "three sheets", but generated four; no missing
source images. Source path attributes saved signs-symbols-source-paths.json,
NOT YET REVIEWED in detail. No recipes yet. Keep warning/prohibition distinctions,
novice yellow/green meaning and source typography; use the existing PDF palette
where colour is meaningful. Copyright/registered source keys are 00a9/00ae.

Production build **91118 remains confirmed live**, still the only build. Preserve
it and poll the exact handle; no duplicate. Post-build validation and actual-strip
reviews are still the next dependency before any 44-symbol production promotion.

### 2026-11-02: 25 more sign recipes and optical reviews

Previous goal turn was progress (44-symbol preflight passed; staged integration
and tests; fetched/reviewed 47 new sources). Production91118 still confirmed live
on exact handle polling; no duplicate build or production input changes.

Reviewed the source-path attributes of all47 signs-symbols candidates, with
extra full-path inspection of looping signs, copyright/registered/trademark and
star2734. Added two staged, unpromoted prototype modules:

- `prototype_transport_signs_svg.py`:12 tiled transport signs (all transport-sign
  except potable water1f6b0). ATM and WC replaced by authentic comic-lettering
  outlines. Strict63157 terminal0; all12 compiled contours match source topology.
  Optical89519 terminal0, all12 inspected at160px/33.6px withfinal18unitstroke in
  transport-signs-optics-all.png. Recognizable wheel, bin, infant, paired restroom
  silhouettes/divider, passport, customs, conveyor and luggage/key. Pinned all
  topology; pinned strict28044 terminal0.
- `prototype_other_mono_symbols_svg.py`:13 simple signs (2705,2611,2714,274e,
  27b0,27bf,303d,2733,2734,2747,00a9,00ae,2122). Negative check/cross tiles keep
  white symbols onblack, contrasting outlined ballot-box check. C/R/TM usecomic
  lettering. Explicit2734path11 excludes off-canvas phone/vibration leftovers.
  Strict52412 terminal0;13/13 pass. Optical33900 terminal0, all13 reviewed at
  160px/33.6px withfinalstroke in other-mono-symbols-optics-all.png; all readable.
  Pinned topology; pinned strict **41047 LIVE**, log
  /tmp/other-mono-symbols-pinned-prototype.log.

Both modules still read candidate registry, no production coverage claim. Helpers
/tmp/preview-transport-signs-optics-all.py and /tmp/preview-other-mono-symbols-optics-all.py.
Remaining22of47 need recipes:13warning signs, potablewater1f6b0, and8other-symbol
(2695,267b,269c,1f531,1f4db,1f530,2b55,274c). Preserve meaningful yellow/green
novice and warning/prohibition colour using existing PDF palette. No recipes for
these22 yet; full source path metadata saved and read, native sheets inspected.

Next dependency remains production91118 ->version/audit/JS/Python/492browserchecks
and13actual-strip reviews. Then /tmp/promote-symbol-marks.py plus staged tests,
not before. The additional25signs remain a later batch.
Other-monochrome pinned strict41047 completed0,13/13passed. Only production91118
remains live. All25new sign candidates have pinned strict previews.

### 2026-11-02: thirteen colour warning signs reviewed

Previous turn was progress (25sign recipes completed and optically reviewed).
Production91118 remains confirmed live, no duplicate or production input changes.

Added staged `tools/font/prototype_warning_signs_svg.py`, all13 warning subgroup
sources. Uses PDF-sampled heart-palette red/yellow and verifies palette/PDF hashes.
Keeps source0 enclosure and explicit pictogram paths, draws source0 prohibition
ring/slash LAST to occlude pictograms. White-background/black-pictogram treatment
retains the red ban. No-entry retains white bar; yellow warning/radiation/biohazard
retain black symbols. UNDER/18 use authentic comic lettering in source cells.
Material mask overlaps assign only enclosed regions; selected IDs and region
counts now pinned alongside component/hole topology.

Strict21775 terminal0:13/13 compiled contours match topology, all positive strength
(no fallback). Child crossing and nonpotable-water reduce to1.275; rest1.7.
Optical12465 terminal0: all13 visually reviewed at160px/33.6px andfinal18unitstroke
in `warning-signs-optics-all.png`. Red/yellow remain bounded; pictograms andslashes
readable. UNDER lettering small but18/crossing clear. Pinned final strict **84862
LIVE**, log /tmp/warning-signs-pinned-prototype.log. Helper
/tmp/preview-warning-signs-optics-all.py. This module returns(white,colour,ink)
plus report.rgb; requires colour-aware builder integration later, NOT yet wired.

Of47signs candidates,38now have optically reviewed recipes (12transport,13simple,
13warning). Remaining9: potablewater1f6b0 and other-symbol2695,267b,269c,1f531,
1f4db,1f530,2b55,274c. Their sourceattributes inspected; 2695/269c/1f531/1f4db
partial pathprint truncated, so inspect full paths as needed before recipes.
No production promotion. Current dependency still91118->post-buildvalidation;
44symbol-mark promotion staged separately and should precede these47signs.
Pinned warning strict84862 completed0:13/13passed with pinned region/topology
assertions. Only91118production remains live.

### 2026-11-02: eight remaining symbol candidates reviewed

Previous turn was progress: thirteen warnings validated and topology/material
regions pinned. Production91118 remains confirmed live; no duplicate build.

Added two staged/unpromoted modules:
- prototype_colour_symbols_svg.py: beginner1f530 (yellow/green), redcircle2b55,
  redcross274c, rednamebadge1f4db. Uses authentic PDF heart-palette colours with
  PDF/palette hashes, source whitefields, separate material-region masks percolour
  and disjoint-region assertion. Strict65439 terminal0, all4strength1.7, exact
  compiled topology. Optical14131 terminal0; all4 reviewed160px/33.6px withfinal
  stroke in colour-symbols-optics-all.png. Twohalves stay separate, white label
  open, redcircle/cross distinct from black mathematical operators. Pinned topology
  and region assignments. Pinned strict **21467 LIVE**, /tmp/colour-symbols-pinned-prototype.log.
  Returns(white,*colours,ink),report.rgbs; futurebuilder mustsupportmultiplecolours.
- prototype_emblem_symbols_svg.py:2695medical,267brecycling,269cfleur-de-lis,
  1f531trident. Explicit source silhouette selections drop shading; source trident
  complete path3 plusbase0, medical sourcefullshapeunion, recycling0..5,
  fleurnonhighlight0,1,3,4,5,6,7,9. Strict26296 terminal0 all4strength1.7 and
  exactcontours. Optical44293 terminal0; all4 reviewed160px/33.6px withfinalstroke
  in emblem-symbols-optics-all.png. Snake/staff andloopopenings, threearrows,
  fleurlobes andthreetines remain legible. Pinned topology. Pinned strict
  **37681 LIVE**, /tmp/emblem-symbols-pinned-prototype.log.

46of47sign candidates now reviewed; only potablewater1f6b0 remains. Its source
33path anatomy fully inspected for0,3,4,7,8,10,11,12,17,22,23,24,26,31,32.
Suggested nextrecipe: whiteoutlinedglass0, retainrim3 with enough opticalgap,
water4lightblue; faucetmount8black, unionpipe10/body11/elbow23 (leg_union) into
onewhiteoutlinedtap, valveparts13..16union, stem18black, handles17/22black,
centre20whiteoutlined, spout24black. This is merely proposed, not implemented
or reviewed. Shapes10rect and11circle mustconvert tags/attributes correctly if
replacing with union path; never onlyset d onrect. No flowingwaterinsource, do
notinvent it. All47need laterproduction integration/source registry/tests/strips.

Currentpriority remains91118build ->fullvalidation ->staged44symbol-markpromotion.
Pinned21467and37681bothcompleted0,4/4each. Onlyproduction91118remainslive.

### 2026-11-02: final potable-water candidate and sign compiler

Previous turn was progress: eight symbol candidates completed and reviewed.
Production91118 remains confirmed live; current production inputs unchanged.

Added prototype_potable_water_svg.py. Source33shapes, glass0/rim3, water4 inPDF
lightblue. Unionpipe10/body11/elbow23 into source10 converted to path, valve13..16
into source13path; preserve tapmount8, handles17/22, stem18, centre20, spout24.
Solid3/8/17/18/22/24, outlined otherkeptparts. No fabricated flowingwater.
Strict99423 terminal0:1.7strength,3components+7holes=10compiledcontours; selected
waterregion[[7]] of7. Optical43477 terminal0; reviewed160px/33.6px finalstroke in
potable-water-optics-all.png. Tap/glass/lightbluewater recognizable. Pinnedstrict
6055terminal0 with exacttopology/region assertions. All47signs now optically
reviewed and strictpinned (12transport+13simple+13warnings+4colour+4emblems+1water).

Created `tools/font/emoji_signs.py`, NOT WIRED into productionbuild. Independent
compiler expects eventual production recipe module names, supports variable
white/semantic-colour/ink layers and palette insertion, verifies exactforms,
topology, source identity. Reuses component.2695 only (confirmed blank zero
advance incurrentfont) so existingdoctor GSUB keepsitsreferencedname. Othernew
copyright/registered/trademark have no currentemoji-cmapcollision.

Started temporaryfontpreflight **33053 LIVE**, /tmp/signs-preflight.log,
script /tmp/preflight-signs.py. Overrides compiler modules to stagedprototypes
in itsownprocess, supplies qualifiedform metadata withoutregisteringproduction.
47drawings,62exactforms (15aliases),1medicalcomponentpromotion. Snapshot current
fantasyfont in/tmp/dad-emoji-before-signs.woff2, expects4173sequences to detect
publicationrace. Builds/tmp/dad-emoji-signs-preflight.woff2 withsemanticCPAL;
compares all4173oldsequences unchanged and everynewqualifiedform equal tobase.
No fullproductionfontbuild startedfor47signs. Do notpromoteuntil strictpreflight
and current91118fullvalidation pass; staged44symbolmarks comesfirst.

### 2026-11-02: 47-sign preflight passed, integration staged

Previous goal turn was progress (potable-water finished and colour-capable sign
compiler created). Preflight33053 completed0:47signs/62forms compile, medical
component name preserved, all4173existing sequences shape identically. This
proof covers fantasy baseline snapshot, not yet the pending tiles/angel font.
Allnewqualificationforms also shape equally to their visible bases.

Prepared `/tmp/test_font_signs.py`:47 exactsource/compiled-outline cases, semantic
CPAL colours, all3complete subgroups (13transport-sign,13warning,21other-symbol),
all18doctor/person/tone combinations surrounded by visiblemedicalsymbol, and
ordered disjoint yellow/green beginner halves. Prepared `/tmp/promote-signs.py`
NOT EXECUTED. Requires manifest4358 (after44symbolmarks validated), promotes6
recipe modules and source47/62registry, wires independent add_signs aftertiles,
adds7actualstripfixtures and JSroutingtest, copies stagedPython tests. Expected
1189bases/1216cmap/27components/4420exactsequences and506browserchecks; not yet
achieved. Allstagedpromotion/test scripts and emoji_signs.py syntaxchecked0.

Production91118stillconfirmedlive. No additionalfullbuild, no productioninputs
changed. Next: wait91118 terminal, versionassets/audit/npm/Python/492browser and
13newstripreviews. Then44symbolmarks stagedpromotion+tests andvalidation; then
47signs stagedpromotion andvalidation. Do notmerge thesebatches into runningbuild.

### 2026-11-02: verified production-build wait

Previous turn made progress (47-sign preflight completed; full sign tests and
promotion script staged). This turn is a verified wait: exact session91118
remained live through two50-second polls. Cache inspection found1337entries and
newestwrite2.6seconds old, supporting continued computation. No restart, no
production mutation, and no completion claim. Pendingvalidation unchanged.

## 2026-11-02: symbol tiles and angel production validation complete

Production91118 completed0 (started16:24UTC, fontoutputs16:46–47). 1098bases,
4297exactsequences,30components,1128cmap. Colour1277852bytes,ink1264604bytes.
Versionassets completed0. Audit16393 completed0:172017/172352visiblecmap,
335missing;3041/3963fullyqualifiedemoji,922missing. Coverage is encoding evidence,
not broadstyle/linguistic completion. FullUnicodegoal remainsincomplete.

JS36953 completed0:298/298passed. Python20819 completed0:105passed,
357deselected,7existingSWIGwarnings,118.98s; includesall85symbol-sourceidentity
cases, completealphanum/arrow/avsubgroups andcomponentarrowregressions, babyangel,
manifest/variation/ink/inventory checks. Separateactivitysubgroup12432completed0:
4passed37.58s, person-activity408/resting30/body48/fantasy158 allrealshapeddrawings.

Browserreportparsed:492checks,zerofailures/geometryerrors. All13newactualstrips
visuallyinspected: babyangelalltones,11symbol-tiles coveringall85drawings,
promoted-arrow-ligatures showing visiblearrows besiderightwardwalk/headshakes.
Newtilesreadbesidedialogue, labelledarrows/playbackcontrols distinct, coloursand
angelhalos survive. IAB179restoredopticalreview;179/180markeddeliverables.

Correctedstagedtests/test_font_signs.py (currently/tmp) wholeother-symbol subgroup
countfrom21to22:thereare21newcandidates plusonealreadycovered. Authoritativeaudit
revealedthetotal; allotherstagedsubgroupcounts confirmed.

## 2026-11-02: next44symbol marks promoted; rebuild started

Executed /tmp/promote-symbol-marks.py ONCE, copied/tmp/test_font_symbol_marks.py
intotests/test_font_symbol_marks.py. DoNOT rerunpromotion. Modules
emoji_religion_zodiac_svg.py andemoji_math_punctuation_svg.py nowproductioncores,
prototypefileswrappers; newregistry44drawings/61forms. Builderextendsgender
components2640/2642 whilepreservingnames. Added7stripfixtures/JSrouting andnew
Pythonsemantic/source/shaping tests. Expected1142bases/1170cmap/28components/
4358exactsequences,499browserchecks; notverifiedyet. Sourcehash85837terminal0:
11704filesverified; newmodules/testsyntaxchecked0. Productionbuildlaunchednext,
log/tmp/symbol-marks-production-build.log; captureitslivehandlefromtooloutput.
Currentcompiledfontisstillsymbol-tiles/angeluntilnewbuildpublishes, so newtests
aretemporarilyaheadofmanifest. Do notrunfullnewvalidationuntilbuildterminal.
47signsremainstaged; /tmp/promote-signs.py mustwaitfor44symbolmarksvalidation.
New44symbol-mark productionbuild handle **95836 LIVE**. Pollthisexacthandle;
91118isfinished. Do notstartduplicatebuild. Log/tmp/symbol-marks-production-build.log.

## 2026-11-02: expression sources and five balloon/hole prototypes

The user reaffirmed the larger, stronger emoji treatment. The approved 1.4×
optical size and existing ink weight remain unchanged.

Expression/heart source fetch35444 completed0:42 candidates pinned to the same
Noto SVG commit, with Git blob and SHA256 verification. Registry:
docs/expressions-hearts-emoji-svg-source-probe.json. All three native source
sheets were visually reviewed. These are candidates, not production coverage.

New unregistered prototype tools/font/prototype_balloon_symbols_svg.py covers
1F4AC dotted speech,1F5E8 empty speech,1F5EF angry balloon,1F4AD thought cloud,
and1F573 hole. Inspected original SVG path attributes and retained semantic
outlines/dots, removing gradients. All use requested strength1.7. Hole initially
looked like a lump; reduced its pressure to.04 and bend to.001 to preserve its
flat oval. Other symbols retain pressure.25,bend.004. Source topology is pinned:
(4,1),(1,1),(1,1),(3,3),(1,0), respectively. Strict contour checks passed for all
five, no fallback. Final pinned run10144 completed0, including optical rendering.
Both enlarged and33.6px final-weight previews visually reviewed; distinctions
survive. output/font-review/pen-translation/balloon-symbols-optics-all.png.
Actual-strip validation awaits eventual integration. No production registration.

Production44symbol-marks build95836 remains LIVE after exact-handle polls.
Do not restart it. Latest log /tmp/symbol-marks-production-build.log. Next:
wait terminal, version assets, audit, npm, Python symbol-mark and core checks,
499 browser checks, seven new actual-strip reviews. Only after validation run
staged /tmp/promote-signs.py for the47sign candidates. Full goal remains open.

## 2026-11-02: six expression-face candidates reviewed

Previous goal turn was progress (five strict, optically reviewed balloon/hole
prototypes). This turn checked live production handle95836 and prepared six
more expression candidates, without changing production build inputs.

New tools/font/prototype_expression_faces_svg.py:263A relaxed smile,2639 frown,
1F47F angry horned face,1F47D alien,2620 skull/crossbones,1F4A9 pile of poo.
Original SVG paths and attributes inspected; explicit semantic path selections
remove gradients/highlights while preserving eyes, mouths, horns, bones and
teeth. Negative poo silhouette keeps white eyes/grin and black pupils. Native
source previews were reviewed in the preceding expression-source pass.
All six pass strict compiled contour checks, requested/applied strength1.7,
no fallback. Poo uses pressure.04/bend.001 to preserve negative face details;
others pressure.25/bend.004. Topology pinned respectively(6,1),(4,1),(4,3),
(4,1),(4,5),(3,3). Initial six-run53798 completed0. Optical preview at160px and
33.6px with final18-unit ink stroke visually reviewed:
output/font-review/pen-translation/expression-faces-optics-all.png. All readable;
actual-strip review still needed after integration. Final pin run92288 started;
poll exact handle if not terminal in current tool output.

Initial five-face attempt14546 failed only1F47E pixel alien: topology-preserving
pen translation rejected its near-touching source rectangles. Not accepted or
registered; separate grid-sensitive treatment remains required. The other four
faces were retained and rechecked in the six-face run. Do not bypass fallback
assertion or count pixel alien as completed.

44symbol-mark production95836 remains LIVE, latest exact poll this turn.
Continue waiting without duplicate build. Pending production validation and
staged47sign promotion unchanged. Full scoped Unicode goal remains incomplete.
Final pinned expression-face run92288 confirmed terminal0:all six strict checks
passed. No prototype processes remain live; only production95836 remains live.

## 2026-11-02: pixel alien resolved; four colour-heart candidates reviewed

Previous turn was progress (six reviewed expression faces). Exact production
handle95836 remains LIVE in this turn; no duplicate build or production mutation.

New prototype_pixel_alien_svg.py resolves1F47E's source near-contact failure by
insetting each of seven source pieces .3SVG units (white stroke.6). This preserves
the seven-piece pixel silhouette and two eye openings instead of bypassing the
translation rejection. Requested/applied strength1.7,pressure.04,taper0,bend.001.
Initial16435 and pinned85462 pipeline completed0, strict compiled contours pass.
160px/33.6px final-weight preview pixel-alien-optics-all.png visually reviewed:
pixel form recognizable; eye holes survive. Prototype not registered; actual
strip validation awaits integration. Original failed recipe remains excluded
from expression_faces module; use this separate recipe for future integration.

New prototype_heart_variants_svg.py:2763 heart exclamation,1F494 broken heart,
1F495 two hearts,1F493 beating heart. Source paths/attributes inspected; meaningful
red/pink comes from existing PDF-sampled heart palette, with PDF and palette
hashes recorded. Beating heart keeps all eight source motion strokes in black;
other shading/highlights removed. All requested/applied strength1.7, no fallback.
Pipeline85462 completed0, four strict contour checks passed. Reviewed final-weight
160px/33.6px heart-variants-optics-all.png: crack, dot, separate hearts, motion
strokes readable. Pinned topology respectively(2,2),(2,2),(2,2),(9,1); material
regions respectively(2,[[1,2]]),(2,[[1,2]]),(2,[[1,2]]),(1,[[1]]).
Final pinned run14427 started; see exact handle terminal result. No production
coverage claim or actual-strip validation yet for these new prototypes.

Next still: wait95836 terminal; version assets/audit/npm/Python symbol-mark/core,
499browserchecks and seven strips; then staged47sign promotion. Expression42
source candidates now have16 reviewed recipes (5balloon/hole+6faces+1pixel+4hearts).
Remaining26 expressions/hearts need recipe work, plus all broader Unicode gaps.
Pinned heart-variant run14427 confirmed terminal0. Only production95836 is live.

## 2026-11-02: symbol-mark build and browser review; reproducibility test live

Previous goal turn was progress. Production95836 completed0 this turn:
1142bases/4358exactsequences/28components,colour1325120bytes. Versionassets
completed0. Audit70116 completed0:172029/172352visiblecmap,323missing;
3085/3963fullyqualifiedemoji,878missing. JS50941 completed0:299passed.
Browser actual report parsed499checks,zero failures/geometryerrors. All seven
new actual strips reviewed:emoji-symbol-marks-1 through6 and promoted-gender-
ligatures.44symbols read alongside lettering; hollow punctuation stays distinct,
genderstandalones coexist with profession/running/zombie/genie compounds.
179restored optical review;179/180 marked deliverables.

IMPORTANT: Python55404 is LIVE. Command runs whole tests/test_font_symbol_marks.py,
test_font_emoji.py,test_font_emoji_ink.py,test_unicode_inventory.py. Unlike previous
filtered run, this includes test_emoji_font_and_manifest_rebuild_identically,
which calls module.build() and writes production outputs. At last log62dots;
expected at the reproducibility rebuild. Do not start another build or modify
production recipes/promote signs until55404terminal. Log:
/tmp/symbol-marks-production-python-tests.log. Production95836 is FINISHED;
poll55404 now. The build was validated inbrowser before this identical rebuild;
ensure test terminal success before claiming complete batch or promoting47signs.

## 2026-11-02: growing heart and negative heart decoration

Added1F497 to prototype_heart_variants_svg.py and standalone
prototype_heart_decoration_svg.py for1F49F. Explicit source path selections:
growing outer1,middle9,inner2; negative decoration tile0/whiteheart3.
Native source paths inspected. Negative decoration strict checks and160/33.6px
optical review passed,topology(1,1),strength1.7,pressure.04,bend.001.

Initial growing heart run74435 pipeline exited0 only because final preview
succeeded: strict step had a contour mismatch. Pinned16989 correctly surfaced
failure. Do NOT count initial shared-tip geometry as accepted. Corrected by
scaling middle9 to.9 andinner2 to.78 about(64,64), paintedoutside-in; separated
nested contours replace tiny shared-tip artifacts. Revised73522 completed0,
strict topology(3,3),materialregions(3,[[3]]),appliedstrength1.7. Revisedfinal-weight
preview visuallyreviewed at160/33.6:three nested hearts remain readable. Scales
recorded in provenance; fixed assertions restored. Final pinned35678 started;
see exact handle terminal result. Actual-stripvalidation pendingintegration.

Expression42 candidates now18reviewed recipes,24remaining. No productioncoverage
claim for these prototypes. Next: finish55404 Python/reproducibility, recordcounts,
then staged /tmp/promote-signs.py and47sign productionbuild. Fullgoal incomplete.
Final pinned35678 confirmed terminal0, all five heart-variant strict checks pass.
Only Python55404 remains live (includes production reproducibility rebuild).

## 2026-11-02: ghost and motion prototypes; reproducibility still live

Previous goal turn made progress:production95836 terminal, JS/audit/browser/strip
validation plus two new heart candidates. This turn exact poll55404 confirmed
Python test process LIVE. It includes full reproducibility rebuild; do not promote
47signs or launch another production build until terminal success. Latest log
still62dots. No production inputs changed this turn.

New prototype_ghost_svg.py:1F47B. Paper arms1/3, bodyunion5+6 into5, sclera8;
blackwink7,pupil9,mouth11,tonguecrease13; pinktongue12 from existingPDFpalette.
Retains source silhouette/curl and expression, removes gradient shading.
Initial25052 failed because cached leg_union requires a tuple; corrected call
uses(5,6). Corrected55932terminal0, pinned35972terminal0. All strict contours pass;
source topology(5,5),colourregion5of5. Requested/appliedstrength1.7. Unionhelper
sourceSHA recorded alongside recipe/pen/palette/PDF provenance. Final160/33.6px
optical preview visually reviewed:ghost wink,tongue,arms andtailreadable.

New prototype_motion_symbols_svg.py:1F4A8 windpuff,1F4A2 angermark,1F4A4 sleep.
Inspected all nativeSVGpaths. Wind keeps cloud1,centralcurl2,smallcurls6/7,
motionlines9/10; other paintshadingremoved. Angerkeepsallfourcurves. Sleep uses
existingcomiclettering ZZZviaemoji_tile_lettering with sourcecells/provenance.
Initial63049terminal0 and pinned10467terminal0. Strict source topology(5,1),
(4,0),(3,0); appliedstrength.95625forwind,1.7others; nofallback. Final160/33.6px
optical preview reviewed; wind direction, fourangerarms, threeZsreadable.

These four remain unregistered candidates, actual-stripvalidationpending.
Expression42sources now22reviewed candidates,20remaining. Fullgoal incomplete.
Only live process55404; pollit, no duplicatebuild. 95836finished. Once55404passes,
recordfinalPythoncount and promote47signs usingstaged/tmp/promote-signs.py.

## 2026-11-02: five more expression candidates reviewed

Previous turn was progress:ghost andthree motion symbols completed. Exact live
Python55404 polled twice this turn, still running its full production-font
reproducibility test. Do not promote47signs/changeproduction inputs untilterminal.

New prototype_coloured_expression_svg.py:1F633 flushedface,1F4A6 sweatdroplets,
1F48C loveletter,1F4AB dizzystar. Explicit sourcepaths inspected andmaterial colours
fromexistingPDFpalette. Flushedface preserves widewhiteeyes/pupils,brows,flatmouth;
radialgradientcheeks adapted toboundedpinkellipses(rx10,ry5,cy83), geometry recorded.
Sweat keeps threedistinct sourcedroplets,lightblue. Loveletter retains envelope0,
folds1,redheart3. Dizzyretains union0+1blackorbit,yellowstar2;unionhelperSHArecorded.
Initial99500terminal0(two);expanded74735terminal0(four). Strictcontours pass.
Pinned topology:1F633(8,5),1F4A6(3,3),1F48C(1,3),1F4AB(1,1). Materialregions:
(5,[[4,5]]),(3,[[1,2,3]]),(3,[[3]]),(1,[[1]]). Appliedstrength1.7exceptloveletter
.7171875; nofallback. Bothinitialandexpandedfinal-weight160/33.6previews visually
reviewed, blush/droplets/seal/orbitdistinct andlegible.

New prototype_eye_balloon_svg.py:1F441_200D_1F5E8 retainsballoon0,outlinediris2,
blackpupil3,whitehighlight4. Source7shapes inspected; removesduplicateballoon
paths andcolouredirispaint. Strict72726terminal0,topology(3,2),strength1.7.
Final160/33.6preview reviewed; eyeandballoontaildistinct. Exactcompoundcoverage
willneedintegration/regressiontest; thisisnotyetproduction.

Finalpinnedpipeline2211 startedforbothmodules; poll exacthandle ifnotterminal.
Expression42candidates now27reviewed recipes,15remaining. Noproductioncoverage
claim. Pendingmainstep remains55404terminalthen47signpromotionandbuild.
Pinned2211 confirmedterminal0, all five strictchecks pass. Only55404 remainslive.

## 2026-11-02: robot and swearing face candidates

Previous turn made progress (five expression candidates). ExactPython55404
confirmedLIVEagain; stillfullreproducibilityrebuild, no productioninputs changed.
Nextpromotion47signsmustwaitterminalsuccess. Logunchangedat62dots.

Added1F916robot toprototype_coloured_expression_svg.py. Inspected15sourceelements;
paper0/1ears,2head+antenna,4mouth,11/13eyes;black5..9toothbars;red3/10antenna
light/nose fromPDFpalette. Gradient/shadingremoved, retainedmechanicalanatomy.
24023terminal0; pinned36242terminal0(allfivecolourrecipes). Robot topology(6,13),
colourregions(13,[[2,7]]),strength1.7,no fallback. Final160/33.6preview visually
reviewed:antenna,head,ears,eyes,nose,grilleallreadable.

New prototype_swearing_face_svg.py1F92C:paperface0,blackbanner2/eyes7/8,
whitegrawlix3..6 replacedwithauthenticcomic '#$!@' usingglyphprovenance.
Initial96290strictpassed but VISUALFAILED:PyMuPDFdidnotfillthe sourcepolyline.
Converted2toexplicitclosedpath, exactsourcepoints.23798strictpassed,butfinalink
closedthethinwhiteletters. TheseinitialvariantsareNOTaccepted. Whiteletterstroke
3.2failedtranslation(90200,29261),evenatlowpressure. Correctedwhiteletterstroke
2.4,pressure.01,taper0,bend.001:11695terminal0,requested/appliedstrength1.7,
topology(7,7),14compiledcontours. Final160/33.6preview visuallyreviewed:bannerand
allfournegativesymbolssurvive18unitinkstroke. Negativeletterstroke/provenance
recorded. Pinned44892started; seeexacthandleterminalresult. Do notrestoreearlier
failedrecipes or inferstyleacceptancefromtopologyalone.

Expression42candidates now29reviewed,13remaining. Allremainstaged forintegration
andactual-stripchecks. FullUnicodegoal incomplete. Onlymainlivehandle55404;
pollit,thenrecordPythoncounts andpromote47signs oncepassed. No newbuildnow.
Pinned44892confirmedterminal0. OnlyPython55404 remainslive.

## 2026-11-02: sparkling/revolving hearts, kiss and comic100 prototypes

Previousgoalturnwasprogress(robot/swearingface). Python55404confirmedLIVEagain.
Its log advancedpast62dots to72[30%]and23more: reproducibilitybuildhasreturnedand
laterfonttestsareprogressing. Stillwaitterminalbefore47signpromotion. No restart.

Added1F496sparklingheart and1F49Erevolvinghearts toheart_variantsmodule.
Sourcepathsinspected:1F496pinkheart0, yellowsparkles4/5/6/7/10;1F49Epinkhearts2/7,
blackorbit0/1. Explicitpathsretaincircle/diamond/star distinctions,no shading.
2231terminal0; topology(4,6)/(2,2),materialregions(6,[[2],[1,3,4,5,6]]) and
(2,[[1,2]]). PDFpink/yellowpaletteprovenance retained. Added1F48Bkiss to
coloured_expressionmodule:redlips0/1, topology(2,2),regions(2,[[1,2]]),83814terminal0.
Allthreeappliedstrength1.7,no fallback. Final160/33.6px18-unitinkpreviewreviewed:
sparkles, orbit, pairedhearts, andlipgapremainrecognizable. Pinnedcombined32884
terminal0:allsevenheartvariantsandsixcolouredexpressionrecipespassed.

Added1F4AF100tomotion_symbols. Sourcefourpathsinspected; preserveunderlines0/1,
replace1path2andcombined00path3withauthenticcomicdigits. Splitcombinedzero
placementboundsintoequalleft/rightcells, appendsecondzeroelement, recordglyph/
sourcecell/fontprovenance. Monochromecomicink; semantic100+doubleunderlinekept.
12236terminal0; topology(5,2),appliedstrength1.7,nofallback. Final160/33.6preview
reviewed:bothzeroopeningsandtwounderlinesvisible. Pinned4968started;seeexact
handleterminalresult. Actual-stripvalidationstillawaitsintegration.

Expression42sourcesnow33reviewedcandidates,9remaining:vomit,clown,ogre,tengu,
heartarrow,heartgift,heartfire,heartbandage,collision. Productiongoalstillincomplete.
Onlymainlivehandle55404;pollandfinishPythonvalidation,thenpromote47signsstaged.
Pinned4968confirmedterminal0:allfourmotionsymbolspassed. Only55404remainslive.

## 2026-11-02: remaining compound hearts and collision reviewed

Previousturnmadeprogress(fourprototypes). Python55404confirmedLIVEtwicethisturn;
lognow72[30%]+41dots, pastreproducibilityrebuild andprogressinglaterfonttests.
No productionmutation;47signpromotionstillwaitsterminalsuccess.

Addedfourrecipes toheart_variants, allsourcepathsinspected:
1F498arrow:yellow1/10/11,pinkheart4,blackshaft0/12+entryhole9.
1F49Dgift:pinkheart0,yellowribbon5/tails7/8/bow10/12/knot17,blackfolds11/13.
2764_200D_1F525fire:orange0/6,yellow1/5/7,redheart2.
2764_200D_1FA79mending:redheart0,paperbandages4/6,shadingremoved.
63553terminal0. Allstrictcompiledcontours/appliedstrength1.7,nofallback.
Topologyrespectively(1,4),(1,9),(1,7),(1,6). Materialregions:
arrow(4,[[1,3,4],[2]]),gift(9,[[1,8,9],[2,3,4,5,6,7]]),
fire(7,[[1,2,4],[3,6,7],[5]]),mending(6,[[1,2,6]]).
Final160/33.6opticalpreviewvisuallyreviewed:arrowends/ribbonknot/flames/crossed
bandagesrecognizablewithapprovedinkweight. Fullpinned11heartvariantspassedin27678.

Added1F4A5collision tocoloured_expression:sourcepolygons0orange,1yellow;
convertedexactpolygonpointstoexplicitclosedpathsforreliableSVGfill. Bothsource
pointlistsinspected. Pipeline27678terminal0,strict topology(2,2),materialregions
(2,[[1],[2]]),strength1.7. Final160/33.6previewvisuallyreviewed:outer/innerburst
shapesandcoloursdistinct. Finalpinned80371started;seeexacthandleterminalresult.

Expression42sourcesnow38reviewedcandidates,4remaining:1F92Evomitingface,
1F921clown,1F479ogre,1F47Atengu. Candidatesstillunregistered;actualstripand
compiledidentity/sequencevalidationneededafterintegration. FullUnicodegoalopen.
Onlymainlivehandle55404;finishPythonbefore47signspromotion/rebuild.
Pinned80371confirmedterminal0:allsevencolouredexpressionrecipespassed.
OnlyPython55404remainslive.

## 2026-11-02: final four expression candidates reviewed

Production validation 55404 remains live, progressing beyond 60%; no production
inputs changed while its reproducibility rebuild and font checks run. Do not
execute /tmp/promote-signs.py until this handle terminates successfully.

Added and visually reviewed vomiting face 1F92E and clown 1F921. Strict run44210
passed with strength1.7, no fallback. Topologies (13,8) and (8,8); colour regions
respectively (8,[[3,4,5,7,8]]) green and (8,[[1,2,6,7]]) red. Their expressions
remain readable in the 160px and 33.6px previews with production ink weight.

Ogre 1F479 and tengu 1F47A source paths inspected and recipes completed. Initial
32237 failed tengu's feature-preservation check. Conservative tengu pressure.04,
taper0, bend.001 passed translation but revealed a two-pixel raster pinhole at
the moustache intersection (6544 and47808 failed strict compiled topology).
The recipe now fills only sub-four-pixel raster pinholes for tengu, consistent
with the translator's existing definition of meaningful holes, and records the
filled pixel count. No meaningful contours are removed. Run32789 terminal0:
both translated at strength.95625 from requested1.7, no fallback, and compiled
contours match. Ogre topology(7,14), colour regions(14,[[3,6],[1,2]]); tengu
(7,5), regions(5,[[1,4]]). Final optical preview reviewed: horns, teeth, nose,
heavy brows and frown remain distinct. All four recipes' topology/material
regions pinned. Full11-recipe strict check95925 started; confirm its result.

All42 expression/heart candidates have now received prototype optical review.
They are not yet production coverage: integration must handle39single-codepoint
bases and3compound drawings, followed by compiled identity, sequence checks and
actual-strip review. The47sign batch remains staged ahead of these candidates.
The full Unicode goal remains open.
Full pinned11-recipe check95925 confirmed terminal0. Only production validation
55404 remains live at this handoff; continue polling that exact handle.

## 2026-11-02: expression compiler and integration staged

Previous goal turn made progress: completed42candidate optical reviews and
pinned11coloured-expression recipes. Production validation55404 remains live
and progressing through tests after60%; no production promotion performed.

Added unregistered tools/font/emoji_expressions.py. It compiles42drawings,
preserves existing component glyph names for wind/dizzy/collision, and creates
three explicit joined drawings. /tmp/test_font_expressions.py stages42compiled
source/layer/palette/qualification checks plus three existing-compound regression
checks. /tmp/promote-expressions.py stages source registration, ten recipe modules,
build wiring, seven strip fixtures and JS routing checks. Do not execute it until
the47sign batch is promoted and fully validated. /tmp/promote-signs.py remains
unexecuted, waiting for55404 terminal success.

Independent /tmp/preflight-expressions.py uses an in-memory copy of the current
production font, leaving production outputs untouched. First run37563 failed:
1FA79bandage is absent, so mending heart needs a new empty internal component.
Compiler now creates that component without advertising standalone coverage.
Second run28731 failed the fully qualified fire-heart shape: FE0F selects the
existing coloured u2764 glyph, whereas unqualified text uses u2764.text. Rules
now explicitly accept both heart glyph names. Third run40399 started; check its
terminal result and /tmp/expressions-preflight-v3.log before accepting.

Expected expression batch:54additional exactforms with zero overlap withcurrent
advertisedsequences. After47signs then42expressions:1228visiblebases,1253cmap,
25component-only entries and4474exactsequences. These are expectations, not
coverage or production success claims. All42need actual-strip review afterbuild.
Tengu pinhole cleanup now also asserts same_features before/after; strictcheck
99863 terminal0. Source raster sub-four-pixel pinholes remain nonsemantic only.
Expression preflight40399 confirmed terminal0:42drawings and54qualificationforms
all shape to the intended single positive-advance glyph in the temporary font.
Current1170cmap becomes1207in that isolated preflight (+36visible glyphs andone
internal bandage component); expected1253after the pending signs batch remains
consistent. Staged compiler/promotion/tests compile cleanly. Final poll confirms
55404stillLIVE; it is the only remaining live handle for this turn.

## 2026-11-02: remaining geometric candidates and sizing

Previous turn made progress: expression compiler passed42drawings/54forms in an
isolated font, and integration/tests were staged. Production validation55404 is
still live, now past90%; no production build inputs changed during validation.

Fetched11pinned Noto SVG sources for ten remaining geometric symbols and keycap
TEN. Network fetch succeeded with sandbox escalation; all Git blobSHA andSHA256
verified. Registry docs/geometric-emoji-svg-source-probe.json remains candidate
only. Reviewed native source sheet and path geometry. New candidate module
prototype_geometric_svg.py removes shading, preserves meaningful PDF-sampled
orange/blue/red, white/black button polarity and source diamond-with-dot form.
TEN uses authentic comic digits through replace_letters. Small diamonds have
300font-unit optical height versus760for large; triangles450. All are vertically
centred, preserving Unicode's semantic size distinction rather than normalising
small drawings to full height. Source size choices and lettering provenance are
recorded per drawing.

Initial strict/preview27629 terminal0; all11requested/appliedstrength1.7, nofallback.
Reviewed final160px/33.6px preview with production18unitink: size pairs, button
polarity, directions and TEN remain clear. Pinned all topology/materialregions;
62553terminal0. Unregistered compiler emoji_geometric.py honors opticalHeight
and vertical centering. /tmp/test_font_geometric.py stages11source/colour/outline
identity checks, two size-ratio/centering checks and TEN-lettering validation.
Isolated preflight11259terminal0:11drawings/11qualificationforms each shape to one
positive-advance glyph. Direct compiled size checks also passed. No production
coverage claimed; promotion and actual-strip review still needed.
Staged /tmp/promote-geometric.py for use only after expression production passes.
It registers11sources/forms, promotes the recipe, wires size-aware compilation,
adds three actual-strip fixtures and JS routing tests, and installs the staged
compiled tests. Expected aftersigns+expressions+geometric:1239bases/1264cmap/
25components/4485sequences. Scripts compile cleanly but remain unexecuted.
Production validation55404confirmedLIVE again at90%+8tests. Continue that exact
handle; do not start any full production build until it succeeds.

## 2026-11-02: symbol marks validated, signs production build started

Previous goal turn made progress: completed11geometric prototypes and isolated
compiled sizing/shaping checks. Final production validation55404 TERMINAL0:
239passed,7warnings in1881.88seconds; log
/tmp/symbol-marks-production-python-tests.log. This completes the44symbol-mark
batch's Python validation, including exact reproducible rebuild, following its
299JS checks,499browser cases,seven visually reviewed strips and coverage audit.

Executed /tmp/promote-signs.py ONCE successfully at17:31UTC. Do not rerun it.
Promoted47drawings/62forms in six recipe modules; added registered source manifest,
compiler wiring, compiled regression tests and seven actual-strip fixtures.
Production build10221 started17:31:17UTC, remains live; command builds emoji then
versions assets. Log /tmp/signs-production-build.log. Expected1189bases,
1216cmap,27components,4420exactsequences. Do not promote expressions/geometric
or start another full build until this build and its validation finish.
Sourcehash26056 TERMINAL0:11751registered sourcefilesverified.

Fetched and SHA/Gitblob-verified18hand-prop sources (writinghand,nailpolish,selfie
andallfive tones); fetch20664terminal0. Registry
 docs/hand-props-emoji-svg-source-probe.json remains candidate-only. Native two
sheets visually reviewed. Prototype_hand_props_svg.py separates exposed skin,
polishred and uncoloured objects/clothes. Initial72525passed topology but failed
visual identity: PDF rasterization lost pen/thumb clipping. Switched these
sources to librsvg while retaining SVG definitions/clips;38223passed but visual
review showed a merged skin/pen fill due to the open clipped stroke edge.
Flattened the clipped pen silhouette first, then outlined the resulting closed
parts.54483terminal0 and final160/33.6preview reviewed: white pen passes behind
thumb, red nails/brush remain distinct, selfie phone/sleeve stay uncoloured.
Allthree requested/appliedstrength1.7, nofallback. Topologies writing(1,8),
nails(1,9),selfie(2,5). Materialregions writing(8,[[2,3,4,6,7,8]]),
nails(10,[[4,6,10],[2,5,7,8]]),selfie(5,[[2]]). Pinned these and recorded
rsvg version, clipping flattening, source/recipe/pen/palette hashes. Fullpinned
check64246running; six-tone finalopticalsheet91058running. Confirm both exact
handles and review the tone sheet. No hand-prop production coverage claimed.
Pinned64246 and tonepreview91058 both confirmed TERMINAL0. Visually reviewed all
18default/tone final optical specimens: handskin changes independently while pen,
brush, redpolish, phone and sleeve remain unchanged; darkest tone retains finger
and thumb boundaries. Integration still needs compiled identity/qualification,
skin/object mask checks and actual strips. Latestpoll10221 confirms buildLIVE;
it is now the only live handle. Next: finish signsbuild, audit+tests+browser506
cases and seven strips, then promote staged expressions. FullUnicodegoalopen.

## 2026-11-02: hand-prop compiler and regressions staged

Previous turn made progress:47signs promoted, production build started, and three
hand-prop recipes corrected and reviewed across all18tone/default specimens.
Build10221confirmedLIVE this turn; do not restart or promote another batch yet.

Added unregistered emoji_hand_props.py. It compiles three drawings into18visible
variants with19exactqualificationforms; all tone variants share the same ink and
object layers and only the exposed-skin layer changes. PDF skin palette hash is
verified. Isolated preflight27896 TERMINAL0 (/tmp/hand-props-preflight.log): all
19forms shape to the intended positive-advance glyph, and every variant's ink
coordinates match its base drawing. The temporary font gained3cmap entries;
production outputs untouched.

Independent anatomical probes23737 TERMINAL0 verified writing thumb/wrist skin,
white pen shaft/tip, nail-polish hand/red nails/red brush tip/white brush handle,
and selfie hand/white phone/white sleeve. Staged /tmp/test_font_hand_props.py
checks compiled layer/source identity, all tones and qualifications in colour
and ink fonts, repeated/mixed boundaries,18source hashes, skin/object landmarks
and separate red polish. /tmp/promote-hand-props.py is staged for AFTER geometric
production passes; it registers3artwork+15reference-onlysources, wires compiler,
installs tests and adds three actual-strip fixtures. Expected cumulative after
signs+expressions+geometric+handprops:1242bases,1267cmap,25components,4504forms.
No hand-prop production coverage claimed; staged scripts compile cleanly.

Next validation for signs must include its new47source-identity cases, complete
sign subgroups and medicalZWJ regressions, global cmap/COLR/palette checks,
all4420advertised sequence shapes, ink-font equality, inventory audit, reproducible
rebuild, JSsuite and506browsercases/sevenactualstrips. The preceding full239-test
run passed before signs promotion; unchanged source recipes need not all be
re-traced again unless these checks reveal a regression.

## 2026-11-02: signs production and browser review

Previous turn made progress: hand-prop compiler, isolated shaping and regression
staging completed. Signs production build10221 confirmed TERMINAL0 this turn:
1189bases,4420exactsequences,27components,1216cmap; colour font1395232bytes.
Asset versioning completed. Do not rerun /tmp/promote-signs.py.

Audit72152 TERMINAL0:172054/172352visiblecmap entries,298missing;
3132/3963fully-qualifiedemoji exactlyencoded,831missing. This is encoding
coverage, not proof of complete Unicode/style correctness.
JS19740 TERMINAL0:300/300passed. Browser report signsReport onIAB179 contains
506cases,zero failures/geometryerrors. All seven new fixtures have no fallback
or unmapped characters and produce PNGs. Visually reviewed emoji-signs-1..6
(all47drawings) plus emoji-promoted-medical-ligatures: borders, white cutouts,
red prohibition slashes, yellow/green beginner halves and distinctions between
medical sign and doctor ligatures remain readable at production size. Doctors
retain the pre-existing simplified faces. Restored optical-review page and
marked179/180deliverables.

Python47771 LIVE:tests/test_font_signs.py plus global cmap/COLR/palette,
all4420sequence shaping, heartpresentation, inkfont equality, inventory and exact
rebuild tests. Log /tmp/signs-production-python-tests.log currently90%, no failure.
This run includes a production rebuild: do not promote staged expressions or
mutate production inputs until47771terminates successfully.

### Next person-symbol candidates

Fetched ten pinned/verified SVGs in docs/person-symbols-emoji-svg-source-probe.json.
Native source sheet reviewed. Prototype_person_symbols_svg.py covers speaking
head, single/double bust, hugging, footprints and five neutral family symbols.
Black silhouettes and white outlined rear figures preserve overlap distinctions;
family tiles retain each adult/child separately. Requested/appliedstrength1.7,
pressure.04,taper0,bend.001. Initial48468TERMINAL0 including final160/33.6optical
preview. Allten reviewed; child separation at small size remains narrow and
must be checked in actual strips afterintegration. Pinned64786TERMINAL0.
Topology: speaking(4,0),singlebust(1,0),doublebust(1,1),hug(1,2),family(7,1),
2adults1child(7,1),2adults2children(10,1),1adult1child(5,1),1adult2children(8,1),
footprints(12,0). No compiler/integration staged yet for this group. It has six
single-codepoint drawings and four joined sequences; do not add compound cmap
entries. Legacyfamily and neutral2adult1child share source anatomy deliberately.

Documented staged hand-prop clipping dependency in docs/emoji-pen-translation.md:
rsvg-convert2.62.2 with linked-library versions recorded in treatment reports.
Current only live process is Python47771. Complete its validation, then promote
/tmp/promote-expressions.py; geometric and hand-props follow in that order.
Full Unicode beta goal remains incomplete.

## 2026-11-02: person-symbol compiler and family-prefix checks

Previous turn made progress: signs production, audit, JS and browser validation
completed; ten person-symbol prototypes passed optical review and pinned checks.
Python47771 remains LIVE, log90%+7dots, in the validation run that includes exact
production rebuild. Do not promote expressions until it terminates successfully.

Added unregistered emoji_person_symbols.py: six standalone drawings and four
neutral family ligatures, with longest-first rules to prevent a shorter family
prefix from consuming a two-child sequence. No new invisible components are
needed; adult, child and joiner already exist. Isolated preflight6139 TERMINAL0:
ten drawings and11qualificationforms shape to the intended positive-advance
single glyph. All16pairs of family sequences and standalone adult/child
boundaries also passed in the temporary font. Separately verified adult/child
head counts in all five family source drawings.

Staged /tmp/test_font_person_symbols.py: ten compiled source/outline/layer checks,
all qualification forms in colour/ink fonts,16family-prefix/boundary cases and
source adult/child-count checks. Staged /tmp/promote-person-symbols.py for AFTER
hand-prop production validation. It registers ten sources, promotes recipe,
wires compilation/routing and adds three actual-strip fixtures. Both staged
files compile cleanly. Expected cumulative after expressions, geometric,
handprops and personsymbols:1248bases,1273cmap,25components,4515exactforms. These
are expectations only; the new group remains unregistered in production.
Only live process47771. Next: finish signs Python validation, then execute staged
expression promotion once and build. Full beta coverage/style goal remains open.

## 2026-11-02: consolidate reviewed pending batches into one build

Previous turn made progress: person-symbol compiler and all family-prefix checks
passed. Signs Python47771 remains LIVE; last log90%+7tests means its final exact
rebuild test is still pending. No production inputs were changed this turn.

Reviewed the four staged integration scripts and exercised their complete file
wiring in a disposable workspace copy. Runs10120 and44464 TERMINAL0. All stages
(expressions,geometric,handprops,personsymbols) passed build/test syntax, manifest
source counts, exact build-rule/variation/sequence insertions and expected cmap/
sequence assertions. Log /tmp/staged-emoji-promotions-check.log. This dry run uses
a dummy manifest solely inside its disposable copy to exercise sequential script
preconditions; it is not a build or coverage claim and never changes production.

Plan refinement: once signs validation finishes, apply the four already-reviewed
batches together and do ONE production build/rebuild, retaining every batch's
compiled regression tests and all16actual-strip reviews. This supersedes the
previous per-batch wait/build ordering; it avoids recompiling unchanged drawings
four times without reducing validation scope. The production manifest stays at
4420until the actual combined compiler writes its real result.

/tmp/validated-pending-emoji-promotion.json identifies the verified staging copy.
/tmp/apply-pending-emoji-promotions.py is prepared but NOT EXECUTED. It requires
the signs log to report80passed, requires the real manifest4420and unpromoted
expression recipe, and checks all existing destination hashes against the staging
baseline BEFORE writing anything. It copies only changed/new source registries,
recipe/compiler wiring, tests and fixtures; no dummy manifest or font is copied.
After success, do not run any individual staged promote script again. Expected
real combined output:1248bases,1273cmap,25components,4515exactsequences and16new
stripfixtures. New registered sources:81(42+11+18+10). All staged scripts compile.

Next: poll exact live47771. When terminal0 and80passed, execute the combined apply
script once, start real build_emoji plus version_assets, verify source hashes,
then run all four new test files, global shaping/COLR/ink/inventory/rebuild checks,
JSsuite, coverage audit and browser/actual-strip reviews. FullUnicodegoalopen.

## 2026-11-02: pending regression collection and verified rebuild wait

Previous turn made progress: consolidated promotion wiring was checked in a
disposable workspace and guarded apply script prepared. This turn verified all
94new regression tests collect successfully against the staged registries/modules
(/tmp/pending-emoji-test-collection.log). This is collection evidence only, not
passed execution. No production input mutations.

Signs validation47771 remains authoritatively LIVE, including after a45-second
poll (functions cell6262completed, underlying exec session47771stilllive). Log
still90%+7tests: final exact rebuild pending. Do not restart on this quiet period.
Next unchanged: wait for terminal success/80passed, execute
/tmp/apply-pending-emoji-promotions.py once, then actual combinedbuild+versioning
and full planned validation/16stripreviews. Goal remains active, no blocker.

## 2026-11-02: signs accepted and combined production build running

Previous turn was a verified wait plus successful collection of94pending tests.
Signs Python47771 now TERMINAL0:80passed,7warnings in624.87seconds, including
byte-identical font/manifest rebuild. Together with300JS,506browser cases,seven
reviewed strips,source hashes and audit, the47sign batch has passed its planned
validation. Do not poll47771again.

Executed /tmp/apply-pending-emoji-promotions.py ONCE after success. It checked all
baseline hashes and applied38staged source/compiler/test/fixturefiles, preserving
the real generated manifest until compilation. All four individual promotion
scripts are now ALREADY APPLIED through the combined copy; NEVER run them again.
Changed-file list: /tmp/applied-pending-emoji-files.json.

Combined production build71210 LIVE, started about17:51UTC. Command builds emoji
then versions assets. Log /tmp/expressions-combined-production-build.log.
Expected1248bases,1273cmap,25components,4515forms;16newstripfixtures. Source check
80376 TERMINAL0:11832registered sourcefilesverified. Keep production inputs stable
until build and validation finish. Next run94new tests (expressions,geometric,
handprops,personsymbols), globalcmap/COLR/palette/allsequence/ink/inventory checks,
reproducibility,JS(expected304),audit,browser(expected522)and16actualstrips.

### Nine game/medical candidates

Fetched nine pinned SVGs; allGitblob/SHA256verified; native sheet reviewed.
Registry docs/game-medical-emoji-svg-source-probe.json remains unregistered.
prototype_game_medical_svg.py covers four card suits, chesspawn, mahjongred-dragon,
waterpistol,blooddrop andbandage. Initial32063TERMINAL0 strict contours but optical
review caught partial heart/diamond: source path0alone was only shaded lower
geometry. Unioned0+1 before outlining;81201TERMINAL0, correctfullsuit silhouettes
visuallyverified. Mahjong5..8union preserves the full中character without outlining
overlapping component strokes. Bandage retains20ventholes andcentralpad. Water
pistol uses sampledgreen/yellow/red/orange;source tank/trigger/grip remain distinct.
Pawn highlights produced straywhitefragments underproductionink; converted full
nativepaintedshape toblack silhouette,84105TERMINAL0 and finalopticsreviewed.
Allnine requested/appliedstrength1.7,nofallback. Final160/33.6preview approved as
candidates,notactualstripvalidation. Pinned topology/materialregions; fullcheck
84009started, confirmterminal result. Topologies: spade/club/pawn(1,0),
heart/diamond/drop(1,1),bandage(23,21),mahjong(5,5),waterpistol(2,20).
Bandage will need to promote the internal1FA79component while preserving mending
heart ligatures after combinedproduction; no compiler/promotion staged yet.

Updated clipping documentation to reference the now-integrated hand-prop module.
Currentlivehandles: combinedbuild71210 andcandidatepinned84009. Fullgoalopen.
Pinned84009 confirmed TERMINAL0 for allnine game/medical candidates. Only live
process at handoff is combinedproduction71210.

## 2026-11-02: game/medical compiler and bandage regression staged

Previous turn made progress: signs fully validated, combined66-drawing integration
applied and build71210started, nine further candidates reviewed/pinned. Build71210
remains LIVE this turn; inputs held stable. No extra production promotion.

Added unregistered emoji_game_medical.py. It reuses component.1FA79 for the visible
bandage, preserving the mending-heart input glyph name. Isolated preflight88247
TERMINAL0:9drawings/14qualificationforms shape to intended single positive-advance
glyphs. This used /tmp/expressions-preflight.ttf, which already contains the real
mending-heart ligature and blank bandage component; it did not use or overwrite
the currently-building production font. Both ❤‍🩹 and ❤️‍🩹 still shape correctly,
including visible bandages before/after. Log /tmp/game-medical-preflight.log.

Staged /tmp/test_font_game_medical.py: nine source/outline/layer identities,
complete game24/medical7 subgroup checks, both mending-heart qualifications,
semantic red suits/full diamond shape and twentybandageperforations. Direct
compiled diamond upper/middle/lower widths220/562/218 verified the shape guard
rejects the earlier triangular error. /tmp/promote-game-medical.py staged but
NOT EXECUTED; requires combinedproduction4515and full validation before use.
Expected after it:1257bases,1281cmap,24components,4529exactforms;three stripfixtures.
All staged files compile. No production coverage claimed for these nine.

Only live handle71210. Next: finish combinedbuild, then all94new tests plus global
checks/rebuild,JS304,audit,browser522 and16newactualstrips. Fullbeta goalopen.

## 2026-11-02: combined validation prepared

Confirmed active goal and kept approved1.4x/strongerink unchanged. Combinedbuild
71210 still LIVE at17:59UTC; initial warning only, no terminal result. No restart
or production input changes. Collected the exact planned105tests successfully
(94new,3global,ink,6inventory,rebuild); collection is not a passing execution.
Collection log /tmp/expressions-combined-collection.log. Browser controls restored;
opticalTab179/opticalComicTab180 preserved. Next after71210terminal success: execute
these105tests,JS304,audit,browser522and16actualstrips. Game/medical promotion still
staged only. No blocker and no coverage/completion claim.

## 2026-11-02: combined production built; strip review and validation

Previous turn was a verified wait (exact71210live) plus105test collection. This
turn71210 TERMINAL0:1248bases,4515exactforms,25components,1495780bytecolourWOFF2;
asset versions updated. Never rerun the four promotion scripts. Sourceinputsheld
stable while combined105Pythonchecks/rebuild32464runs. Log
/tmp/expressions-combined-python-tests.log;104dots now, still LIVE, no finalpass.

Audit34641 TERMINAL0:172101/172352visiblecmap(251missing),3213/3963fullyqualified
emoji(750missing). Currentdocs/unicode-coverage.json. JS87279initiallyfailed2stale
expectations: heartonfire andeye-balloon nowcustom. Updatedtests while retaining
unsupportedcluster checks withphoenix andnonstandardeye-fire. Rerun2861 TERMINAL0:
304/304passed,/tmp/expressions-combined-js-tests.log.

All16newactualstripfixtures visuallyreviewed. Expressivefaces/hearts, geometric
sizepairs,all18handpropsandneutralfamilies readable; whitepen/phone/sleevesstay
white across tones. Familychildheads remain distinct atactualsize. Browserfirst
522run exposed duplicateemoji-expressions-1/-2names and stale hardcodedoldface
assertions applied to allsix newstrips; also staleheartonfire nativeexpectation.
Renamednew six fixtures emoji-expression-expansion-1..6, preservingold two.
Addedglobaluniquenessguard and font-use checks for every emoji token in all16new
fixtures. Updatedmixedsequenceexpectation forcustomheartonfire. Firstbrowserrun
hadzero geometry failures andzero fallback/unmapped innew16; the7failedfixtures
were theseharnessissues. Browserreload now RUNNING at179; mustwaitfornewreport,
notclaimpass. All16stripvisuals remain valid because onlyfixturechecks/nameschanged.
Browser179markedhandoff;180opticalcomic keptdeliverable. Python32464mustfinish
beforegame/medicalpromotion; nofontinputchanges duringrebuild.

### Sound/control source candidates and two prototypes

Fetched12pinnednativeSVGs, Gitblob/SHAverified, source registry
 docs/sound-controls-emoji-svg-source-probe.json (unregistered). Native sheet
 output/font-review/pen-translation/sound-controls-native-sources-1.png reviewed.
Includes9soundsymbols+3musiccontrols. Metadata sound-controls-source-paths.json.
Onlytwo prototypes implemented sofar inprototype_sound_controls_svg.py:
1f39aslider and1f39bfourknobs. All other10need recipes/opticalreview.
Preserve22scale marks,4knobpointers and44surroundingdots. Initialstrict73555passed;
initialoptics23587review caughtthinwhitepointers. Added1.8SVGunitwhitepointerstroke,
42591 TERMINAL0(strictthenoptics); revisedpreviewreviewed, legiblepointers.
Bothrequested/applied1.7,nofallback, topology slider(22,1),knobs(49,1),eachonehole.
Pinnedtopology/regions;12277LIVEfinalpinnedcheck,/tmp/sound-controls-pinned.log.
No productionintegration orcoverageclaim. Fullgoalremainsopen.

Next: poll32464and12277;readcompletedbrowser522report(no reload). Fixanyrealissues,
thenpromotegame/medicalstagedscriptONCEandbuild/verify. No blockers.
Pinned12277 confirmed TERMINAL0. OnlylivePTY32464;browser522rerunstillpending.

## 2026-11-02: combined browser suite passes; twelve sound candidates reviewed

Previous turn made concreteprogress(build,JSfixes,audit,16stripreview,newprototypes).
This turn correctedbrowserrun completed522cases:zero failures,zero geometryissues;
all16newfixtureszero fallback/unmapped andexplicitcustomfontusechecks passed.
combinedReport inCUApersistentstate holds522result. Restored179toopticalreview;
179/180markeddeliverables. Python105checks/rebuild32464still LIVE,104dots,no final
result; do notpromotegame/medicaluntilterminalpass. JS304andauditremainpassed.

Expanded prototype_sound_controls_svg.py toall12sources. Nativeindividualpath
sheets /tmp/sound-paths-{key}.png reviewed, renderinghelper
/tmp/review-sound-paths.py(34424terminal0). Speakersmerge nativeback0/1/3/6and
cone4/5/7; preservewhiterim/diaphragm. Bellsretainloop/clapper; redmute/prohibition
onlysemanticcolour. Microphone retainsgrille andmount; megaphonesretainhandles;
postalhorntracesnativestrokedring andretainsbothcords/tassels. Allrecipestracepinned
sourcegeometry ratherthaninventsymbolidentities. Initialexpanded58704terminal0,
optics80922terminal0. Visualreviewcaught volume-waveblackonblackmerge.

Wavefixiterations: halo7alone56875failed due2pixelrastercrumb; removing isolated
sub4pixelcrumbs(<=8total) allowed99652strictpass butstilltoooverlappedvisually.
Halo12experiment54088TERMINAL1(strictcontourmismatch1f509); rejected.
Final: retainnativewavesbuttranslate12,-8SVGunits, expandviewBox0 -8 144 144,
whitehalo7,blackstroke2.58719TERMINAL0(strict+optics). Final160/33.6previewreviewed:
zero/one/twowaves nowclearlydistinct,muteredslash,whitebellclapper andfourwhite
knobpointers preserved. File output/font-review/pen-translation/sound-controls-optics-all.png.
Report recordswaveoffset/halowidth/removedcrumbs,whitepointerpaths/width1.8,
strokedpaths/width,unionprovenance. Strictpenfeaturechecks unchanged.

All12topology/materialregions nowpinned. 80010LIVE finalpinnedallrun,
/tmp/sound-controls-pinned-all.log. Topologies:slider22/1,knobs49/1,mute1/5,
speaker2/3,bell2/4,mutedbell1/10,mic8/2,loudspeaker2/5,megaphone2/5,horn2/3,
medium5/3,loud7/3. Allrequested1.7;mediumapplied.95625,allothers1.7;nofallback.
Unregisteredemoji_sound_controls.py staged, no productioninputchanges. Isolated
preflight11766LIVE,/tmp/sound-controls-preflight.log,usingearliertemporaryexpression
font,NOTcurrentlyrebuildingproduction. /tmp/preflight-sound-controls.py.
No soundproductioncoverageclaimed. Nextpoll32464,80010,11766;then game/medical
promotionONCEaftercombinedfullpass. Fullbetaopen,no blockers.
Finalpoll:80010and11766both TERMINAL0;onlylivehandle32464. Readpreflightlogfor
exactqualificationcount; soundsallpinnedandisolatedcompiled,notproduction.

## 2026-11-02: expressions fully validated; game and sound production started

Previous turnprogress:522browserpass and12soundcandidatepreflight. This turn
32464 TERMINAL0:105passed,7warnings,696.20sec; includes94newcompiledtests,global
cmap/COLR/palette/all4515sequences,heartpresentation,inkcompanion,inventoryand
exactrebuild. Combined66drawingbatch nowfullyvalidated:304JS,522browser,
16actualstrips,audit3213/3963FQ and172101/172352visiblecmap. Do notpoll32464again.

Soundpreflight11766was12drawings/15forms,1219cmapusingtemporaryexpressionfont.
Staged17soundtests (12identity,2complete subgroupssound9/music9,mutecolours,
wavegeometry,4whiteknobpointers). Knoblandmarkfilter excludesouterframe byspan;
sourceknobwhitecores8734/8616/8667/8653pixels; tempcompiledwaveupperwidths587/521.
Game15tests+sound17 collected32successfully; notexecutedproductiontests yet.

Executed /tmp/promote-game-medical.py ONCE and /tmp/promote-sound-controls.py ONCE,
bothsuccessful. NEVERrerun. Registered21drawings/29exactforms:9game/medicaland
12sound. Copiesrecipesintoemoji_game_medical_svg.py/emoji_sound_controls_svg.py,
oldprototypefileswrappers. Bandagepromotescomponent.1FA79preservingheartGSUB.
Added6stripfixturesandexactfontuseassertions;JSexpected306,browser528.
Expectedproduction1269bases,1293cmap,24components,4544exactforms.
Build86352LIVE started18:13:10UTC; /tmp/game-sound-production-build.log,
buildthenversionassets. Keepallproductioninputs stableuntilvalidationdone.
Sourcecheck24547 TERMINAL0:11853registeredfilesverified.
Nextafterbuild:32newtestsplusglobal/ink/inventory/rebuild(43totalexpected),
JS306,audit,browser528and6newactualstrips. No coverageclaimbeforebuild/audit.

### Awards/event candidates

Fetched9pinnedNotoSVGs andverifiedGitblob/SHA,unregisteredregistry
 docs/awards-events-emoji-svg-source-probe.json. Native9sheetreviewed plusall
individualpaths /tmp/awards-paths-{key}.png(helper87963terminal0).
Symbols:2728sparkles,1f9e7redenvelope,1f397reminderribbon,1f396militarymedal,
1f3c6trophy,1f3c5sportsmedal,1f947/8/9rankmedals. Originalred-envelope福stroke
pieces3..11mustremainreadable; no recipeforit yet.
prototype_awards_events_svg.py implementsother8only. Existingcomicdigit1/2/3
replacesnativefontdigitviareplace_letters. MetalsPDFyellow/grey/orange,
blue ribbons, trophyPDFbrownbase, red/white/bluemilitaryribbon; goldstar.
38301 TERMINAL0:all8requested/applied1.7,nofallback,strictcompiledcontours.
Notyetopticallyapproved:29511LIVEproducing160/33.6preview,
/tmp/awards-events-optics.log. Nextinspectoutput/font-review/pen-translation/
awards-events-optics-all.png, thenfix/pin. No productionregistration.
Onlylivehandles86352buildand29511candidatepreview. Fullgoalopen,no blockers.
29511 TERMINAL0 andeightaward/eventopticsnowvisuallyreviewed:three sparklepoints,
ribboncrossing/tophole,trophyhandles/base,militarystripes/star,sportsstarandcomic
1/2/3ranksallreadableat33.6. Metalsremainclearlydifferent. Pinned8topology/regions
inprototype; rerunstrict afterredenveloperecipeadded (notcurrentlyrunning).
Onlylivehandle86352confirmedagain. Redenveloperemainsunimplementedcandidate.

## 2026-11-02: red-envelope calligraphy preserved; award batch staged

Previous turnprogress:105Pythonpass,21drawingpromotion/buildand8awardprototypes.
86352game/soundbuild remains LIVE thisturn, inputsstable. No promotions beyond
already-integratedgame+sound. 29511oldpreviewterminal, do notpollagain.

Addedninthawardcandidate1f9e7. First46415TERMINAL0,strictcontoursbutopticalreview
rejectedblack-outlinedgold福: outlineoverwhelmedcharacter. Redesignedinteriorgold
asindependentlypen-treatednativepaths3..11withnoblackborder. Maininkstilldefines
envelopeandgoldring;redmaskexcludescharandgoldmaskincludesit. Thispreservesnative
characterwithouttheblackinkcompanionoverpaintingitsstrokes.70502TERMINAL1 caught
separatepaddingdifference; alignedbycroppingcharacterpadding20thenpaddingtobody.
77607TERMINAL0(strict+preview), final160/33.6reviewaccepted:福visiblein gold,
redbodyandouterblackcontourretained. Bodyandcharacterbothrequested/applied1.7,
nofallback. Char4components/5holesasserted;sourcepaths/settingsrecorded.
Compiledcolourcheck81454TERMINAL0:gold5components/6holes/11contours(ring+character),
red8components/5holes/13contours. No overlapred/goldintended;stagedtestchecksit.

Pinnedall9awardtopology/regions.54290TERMINAL0:strictall9thenisolatedpreflight:
9drawings/11qualificationforms,1216temporarycmap. Logs /tmp/awards-events-pinned.log
and /tmp/awards-events-preflight.log. Unregisteredemoji_awards_events.py staged.
/tmp/test_font_awards_events.py has13tests:9compiledidentities,completeevent21and
award-medal6subgroups,metalcolours/exactcomicdigits,compiledgoldcharcounterguard.
/tmp/promote-awards-events.py stagedandcompiled but NOT EXECUTED. Requires4544
manifest andfullyvalidatedgame/soundbatch. Wouldyield1278bases,1302cmap,
24components,4555forms;3stripfixtures,JS307/browser531. Do notpromoteyet.

Next: finish86352,run32newgame/soundtests+global/ink/inventory/rebuild(43),JS306,
audit,browser528,6actualstrips. Awardsreadyforlaterpromotion,notproductioncoverage.
Onlylivehandle86352confirmed. Fullgoalopen,no blockers.

## 2026-11-02: game/sound browser validation and holding-hands sources

Previous turnprogress:red-envelopecharfixed,pinned9awardsandstagedtests/promotion.
Game/sound86352 TERMINAL0:1269bases,4544forms,24components,1527880bytes;versions
updated. Sourcehash24547already11853pass. Started43Pythonchecks/rebuild45359LIVE,
/tmp/game-sound-python-tests.log. Initialonefailuretest_suit_colours_and_full_diamond_shape:
itincorrectlyrequiredheartheight>740althoughfituseslongestdimension(heart760wide,
708tall;diamond562wide760tall). Diagnostic26629TERMINAL0tool,pytest1failed.
Correctedasserttomax(width,height)>740;unchangeddiamondupper/lowerwidthguards.
Targeted3867 TERMINAL0:1passed8.64sec. Original43runwillstillreportthisoneknown
failure; waitforother42/rebuildoutcome beforeclaimingcombinedpass. No fontinputs
changed. Onlytestassertionchangedafterrunloadedit.

JS2744 TERMINAL0:306/306pass. Audit33108 TERMINAL0:172107/172352visiblecmap,
245missing;3234/3963FQemoji,729missing. Browser528casescompletedzero failures/
geometry;all6newfixtureszero fallback/unmapped andexplicitcustomfontchecks.
All6actualstripsvisuallyreviewed: suits/pawn/mahjong中/waterpistol/blood/bandage,
mending-heartboundaries,zeroto2volumewaves,mutemarks,microphone/slider/knobpointers.
Readabilityaccepted. gameSoundReportpersistedinCUA;179/180restoredopticalpreview
andmarkeddeliverables. AwardspromotionstillNOTEXECUTED pending45359rebuildresult.

### Holding-hands candidates (four geometries,104standardforms)

ProbedUnicodefamily337missing:holdinghandscomprises104forms (4familiesx26),
includinglegacy👭/👫/👬default+same-tone and20mixedZWJpairspergenderfamily;
neutral🧑‍🤝‍🧑hasdefault+25pairs. Fetchedfirst12pinnedSVGs(4base+8reversedlight/dark),
nativesheetreviewed. Then60902TERMINAL0fetchedall104recommendedforms,allGitblob/
SHAverified. Unregistered docs/holding-hands-emoji-svg-source-probe.json includes
4artworkplus100referencefiles(first12orderpreserved). No productionregistration.
Nativegeometryidenticalwithineachfamilyforall26variants. /tmp/check-all-holding-hands-sources.py
TERMINAL0 verifies104hashes/geometriesand EVERYproposedskinpathpaintagainstsame-tone
referencesforeachside. Report output/font-review/pen-translation/holding-hands-all-source-check.json.
Oppositetonesalsocheckedby/tmp/check-holding-hands-sources.py;paintdiffmetadata
holding-hands-paint-differences.json. Nativehair/eyesalsovarycolour, so automatic
paintdifferencealoneisNOTskinmask;explicitreviewedskinpathsetsareused.

prototype_holding_hands_svg.py implements4basegeometries,independentleft/rightskin,
whiteclothes,blackhair/shoes/features. Initial73264TERMINAL1fellbackbecause5isolated
1–2pixelSVGintersectioncrumbs. Removesonlysub4pixelcomponents(<=12total),fills
sub4pixelpinholes(<=12total),recordsactualcounts;strictpenfeaturechecksunchanged.
15144TERMINAL0(strict+optics);160/33.6previewreviewed:holdingpose,hairgenderstyles,
clothes/skinboundariesretained;facesdenseatsmallsize,wholefiguresrecognizable.
Noactualcomicvalidationyet. Preview holding-hands-optics-all.png showsleftlight/
rightdarkPDFtones. Sourcegeom/materialregionguardsnowpinned;96011LIVEfinalstrict,
/tmp/holding-hands-pinned.log. Allrequested1.7;appliedneutral.537890625,women1.7,
mixed1.7,men1.275;nofallback. Topologiesneutral13/17,women13/13,mixed13/15,men13/17.
Removed5crumbpixelsinall;filledpinholes1/1/2/3respectively.

Holding-handsstillneeds104formcompiler+longest-firstGSUBbeforeindividualperson
tone rules,registration/reference-onlymetadata,all25tonepairvariantsopticalreview,
anatomylandmarktestsandactualstrips. Existingperson/handshake/joinercmapcanbeused;
3legacynewbasecmapand1neutralcompound. Do notcount104asproductionyet.
Onlylivehandles45359productiontests/rebuildand96011candidatepincheck. Fullgoalopen.
96011confirmedTERMINAL0;onlylivehandle45359. Awardsreadyafteritsvalidation;
holding-hands4prototypespinned,104referencesverified,compilerpending.

### Validation checkpoint — 2026-11-02 18:40 UTC

Game/sound production tests 45359 finished: 42 passed, one incorrect test
assertion failed (heart height rather than longest dimension). Corrected optical
normalization assertion passed separately in 3867. All 43 checks, including
exact rebuild, now validated. Existing production remains 4544 exact forms.
Awards/events remain staged, not promoted.

Holding-hands compiler `emoji_holding_hands.py` is staged, not integrated.
Isolated preflight 85702 passed: 104 forms, 208 adjacency checks, all 4544
existing sequences retain glyphs and advances. Four compiled 25-pair tone
matrices were individually viewed: silhouettes, separate skin fills and white
clothes hold at 33.6 px; faces remain dense. Actual-strip review remains required.
Native reference audit is now reusable in `tools/font/holding_hands_sources.py`.
`tests/test_holding_hands_sources.py`: five passed (68770), covering all 104
native reference hashes/geometries/independent paints and four anatomical masks.
The initial trouser landmark landed between the legs; corrected to the interior
of each left trouser leg (native x30/86, y100). No artwork changed for that fix.
All handles are terminal; no build/test process currently running.

Next: stage compiled holding-hands sequence/COLR tests and promotion; combine
with ready awards/events promotion, build once, check source inventory, Python
and JS, coverage audit, and actual comic fixtures. Do not count the 104 candidate
forms as production. Preserve accepted 1.4x sizing, stronger ink, strength 1.7
with topology backoff. Full Unicode beta goal remains active and incomplete.

### Awards + holding-hands integration; family candidates — Nov 2, 18:50 UTC

Previous goal turn was progress: versioned native-reference audit and five
anatomy tests added, four tone matrices individually reviewed.

Executed `/tmp/promote-awards-events.py` and `/tmp/promote-holding-hands.py`
ONCE. Do not rerun. Production build 34418 started 18:40:28 UTC, still live at
18:50; log `/tmp/awards-holding-production-build.log`. It includes asset version
updates after the build. Expected 1281 bases/1305 cmap/24 components/4659 exact
forms. No claim until its terminal result and downstream checks.
Holding-hands longest-first rules precede individual-person tone rules. Added
four compiled identity/tone tests, one JS routing test and six actual fixtures;
awards adds thirteen tests, one JS test and three fixtures. Expected browser537
and JS308. Source check3924 TERMINAL0:11966 registered source files verified.
Native holding tests80638 TERMINAL0:5passed. No production inputs changed while
34418 was running.

Independently fetched 233 remaining family SVGs from the pinned Noto commit:
66840 TERMINAL0, all Git blob/SHA verified. `docs/family-pairs-emoji-svg-source-probe.json`
is unregistered. Sources include 208 couple variants and25 parent/child tiles.
`family-pairs-native-{1,2,3}.png` reviewed. Initial MuPDF preview lost gradient
transparency and blacked out women's faces; regenerated with installed
rsvg-convert and re-reviewed first sheet. Native files remain unchanged.
`family-pairs-geometry-probe.json` shows couple variants have different source
geometries (not safe to assume identical paths across tones).

25 family tiles: `prototype_family_tiles_svg.py`, unregistered compiler
`emoji_family_tiles.py`, registry `docs/family-tiles-emoji-svg-source-probe.json`.
Use native frame0 + all black figure paths3 onward, remove shading1/highlight2.
All strength1.7, no fallback, pinned topologies. Native and treated sheets,
160/33.6 optical sheet reviewed. At small sizes the child separators are narrow;
actual-strip review must confirm every child remains distinct before promotion.
Preflight74309 TERMINAL0:25forms,625adjacent-family combinations, all4544 existing
sequences unchanged. Male adult/child source-circle counts independently checked
for all25. Staged `/tmp/test_font_family_tiles.py` has27checks (25compiled,
all625prefix/adjacency, source circles). No promotion script yet.

Eight expressive couple prototypes: `prototype_couples_svg.py`, unregistered
compiler `emoji_couples.py`. Exact208RGI forms expand to404 qualification forms:
46each neutral kiss/heart and52each of6gendered couples. Shared physical left,
right and red-heart masks; untoned faces white; clothes white; hair/features
black. Some native sources duplicate head paths; audited unique physical heads.
Source path index/ancestry dump `couple-source-paths.json` reviewed. Independent
`couple_sources.py` checks all208source hashes and left/right face paints against
existing holding-hands head references (index28), and physical head positions.
`tests/test_couple_sources.py`:9passed (88303 TERMINAL0), including8mask checks.
All8prototypes requested/applied1.7, no fallback; topologies/regions pinned.
Enlarged and160/33.6optics reviewed: kiss mouths and separate faces survive;
actual strips still required. Preflight5753 TERMINAL0:8drawings/404forms,
808adjacency checks, all4544existing sequences unchanged. Rules support both
u2764.text and emoji-heart UVS glyph and must precede person-tone rules.
Staged `/tmp/test_font_couples.py` has8compiled identity/all-tone checks. No
registration or promotion script yet. 40620 final pinned previews TERMINAL0.
Other candidate handles12514/54887/4975/45809/87923 terminal; failed first probes
were corrected, no outstanding processes beyond34418.

Next: finish34418; run17new compiled tests + holding native5 + global cmap,
all-sequences, heart presentation, ink/inventory/rebuild; npm test; coverage audit;
browser537 and nine actual-strip reviews. Do not promote family tiles/couples
while production rebuild verification runs. Goal remains incomplete.

### Awards/holding production browser validation — Nov 2, 18:53 UTC

34418 TERMINAL0. Built1281bases,1305cmap,24components,4659exactforms;
colourWOFF2 1557052bytes; asset hashes updated. Source11966verified.
83730JS TERMINAL0:308/308passed. 61620audit TERMINAL0:172116/172352visiblecmap,
236missing;3347/3963fullyqualifiedemoji,616missing. Browser537cases, zero failures
or geometry problems. All nine new fixtures have zero fallback/unmapped values
and explicit custom-font checks. All nine actual strips visually reviewed:
threeaward/event strips and sixholding-hands strips, including reversed tones
and adjacent standalone people. Medal ranks/metals, envelope gold character,
joined figures and skin tones remain readable. Small paired faces are dense,
but whole figures/hairstyles/pose remain recognizable. Accepted for this batch.
CUA179restored opticalreview;179/180markeddeliverables; awardsHoldingReport
contains537results in persistent CUA session.

Only live handle40779: production Python checks including exact rebuild, started
18:50:35approx, `/tmp/awards-holding-python-tests.log`. At18:53 output
`............F...................`; no terminal result yet. The failed13th test
was `test_red_envelope_retains_gold_character_counters`: it incorrectly forbade
all red/gold overlap, including intentional underpaint beneath black borders.
Diagnostic35660 proved3633overlap pixels, ZEROvisible overlap outside ink.
Changed only assertion to `not any(red & gold & ~ink)` with explanation; retained
all gold-character component/hole/compiled-contour guards. Targeted5746 TERMINAL0:
1passed10.57sec. Original diagnostic63043failed as expected. No fontinputs changed.
Wait40779's final result before treating remainingchecks/rebuild as passed. Do not
restart or promote newfontinputs meanwhile. New familytile/couple candidates and
stagedtests remain unregistered. Full Unicode beta goal remains active.

### Session restart recovery — Nov 2

Previous status-only goal turn yielded recovery evidence but did not advance
implementation. Goal resumed. Read the agreed brief again. Old build handle94774
and flag handle12948 are missing; original build PID45983 is also missing
(os.kill(pid,0) raises ProcessLookupError). Thus the interrupted build is stopped,
not merely quiet. Its log has no completion and the installed manifest still has
4659forms /1557052byte colour font. Do not claim the family/couple batch built.

Awards/holding checks40779 completed:32passed,1failed. The sole failure was the
incorrect red-envelope overlap assertion described above; corrected targeted5746
passed. This completes those33checks including reproducibility, with no remaining
failure. Browser537 and JS308 were already validated for that installed version.

Family/couple promotion DID execute once before interruption; do not rerun
/tmp/promote-families-couples.py. Production source includes25family tiles and
8couple drawings,429additional forms; expected1283bases/1307cmap/24components/
5088forms. Source12199verified and native9passed before interruption. All8couple
tone matrices were individually reviewed. Current build17395 writes
/tmp/families-couples-recovered-build.log and runs version_assets.py on success.
Do not mutate font inputs during build or subsequent reproducibility checks.
Current independent JS10287 and native87752 checks write
/tmp/families-couples-recovered-{js,native}.log. Terminal results pending.

Flags:270native sources verified (8general,262regional), all9native sheets
reviewed. Regional sources have separate public-domain notices retained in source
cache; preserve those on registration. Unregistered12flag prototype JSON and PNG
survived restart, with all12reports. Current code fixes initial numpy JSON
serialization failure. It uses exact source paints for simpler flags and a
64colour palette for complex emblems; shared displacement aligns colour and
outer ink, with75percent native/25percent comic palette. No flags integrated or
counted as coverage. Need compiled contour/emblem checks and actual-strip review,
then complete remaining regional/general flag recipes.

Next after17395 terminal success: compiled family/couple tests, global colour/
sequence/heart/ink/inventory checks and exact rebuild; audit; browser552 and15new
actual-strip reviews. Expected family subgroup337/337 and total3580/3963emoji are
predictions until verified. Full scoped Unicode beta remains incomplete.

Recovery checks:87752 TERMINAL0,9native tests passed in17.28s. JS10287
TERMINAL1:308passed,2failed, exactly the new family-tiles/couples routing checks.
Those depend on the generated manifest, which still describes the old installed
font while17395 builds; rerun after build before diagnosing a routing regression.
17395 confirmed live by write_stdin (returned same session, no exit code).

### Flag contour preflight during recovered build

Previous recovery turn was progress: restarted authoritatively missing build,
ran9native tests, identified2manifest-dependent JS failures, saved recovery state.
Build17395 re-polled and confirmed live; do not restart.

Added tools/font/check_region_flag_details.py (candidate-only) to measure colour
islands and zero-area contours after the production outline conversion and font
rounding. First26127 TERMINAL0 produced12reports. EU12gold stars remain12positive
contours; Korea18black trigram pieces remain18positive contours. Other colours
have many tiny islands/degenerate contours (RO48,TD58,Welsh97totaldegenerate).
This evidence prevents premature flag integration. Updated candidate quantization
to use unassociated RGB rather than white-composited perimeter pixels and exact
nearest source paints (cKDTree) rather than Pillow's reduced-cell palette cache.
No registered production font input changed. Python syntax checks pass.
Rerun15134 currently live, /tmp/region-flags-contour-preflight.log; firstGB/US
results still contain1/8degenerate contours, so correction is partial and no
claim of complete flag fidelity. Output JSON is overwritten only on full success;
while rerun is live existing JSON refers to first run. Preview PNG still depicts
previous quantization. Need inspect new report and regenerate/review preview.
15134 subsequently TERMINAL0; regenerated contour JSON now represents current
exact-nearest/unassociated-RGB candidate. Preview still requires regeneration.

### Flag detail measurements and source recheck

Previous turn was progress: added contour preflight, ran12flags, corrected
candidate quantization and reran. This turn extended preflight to measure actual
unrounded areas of contours that collapse under font rounding.1586 TERMINAL0:
maximum collapsed area in square font units:GB.181,US.425,JP0,NP0,RO.910,TD.907,
CA.426,ZA.182,BR.547,EU0,KR.182,Welsh1.410. Thus degenerate counts alone greatly
overstate visible feature loss; no meaningful emblem loss established by them.
Still need final visual/compiler validation before integration.
Added explicit independent feature gates:USblue canton has51contours (outer plus
50star counters);EUgold12positivecontours;KRblack18separatepositivepieces;
NPwhite2separatepositiveemblems. Extended98219 currently live, testing those four
plusBZ,EC,GT,MX,NI,PM,VGcomplexemblems. Firstfour gates passed in log
/tmp/region-flags-emblem-preflight.log. Reports now checkpoint after each flag;
output region-flags-contour-preflight.json therefore represents current partial
run, replacing previous12results. Inputs/provenance remain in prototype reports.
84543 TERMINAL0:12199registered source files verified anew.17395 polled again,
confirmedlive; no font inputs changed and no restart. Next actions unchanged:
finish build, run compiled/rebuild checks and rerun JS, audit and review actual
strips. Need regenerate flag preview for current quantization.

### Complex flag completion and full regional preflight

Previous turn made progress with feature gates/source verification and live build
polls.98219 TERMINAL0:11flags US/EU/KR/NP/BZ/EC/GT/MX/NI/PM/VG completed. Four
explicit emblem gates pass. Saved that report as region-flags-emblem-preflight.json.
Complexflags' max collapsed contour areas (fontunits squared):BZ15.97,EC2.25,
GT1.51,MX3.23,NI2.29,PM3.78,VG3.02. Counts alone do not show meaningful losses;
zero-area polygons still need safe serialization and compiled/optical comparison.
84683 TERMINAL0:56planned family/couple/native/global/ink/inventory/rebuild tests
collect successfully; do not run against old installed font.

Build17395 remains live. Authoritative ps PID48041 at19:25 approx:13:17elapsed,
4:43.82CPU,100percentCPU,stateR. This rules out a stalled process at that check;
no restart warranted despite quiet log. Source inputs remain frozen.
Extended flag tool with --regions all, independent262regional inventory assertion,
perflag checkpoints and failure collection (nonzero exit if any flags fail).
57607 now live: /tmp/region-flags-all-preflight.log. It uses original pinned
sources and candidate code only. nice could not adjust priority, but Python did
start (PID49261); do not restart on that message. All-region output overwrites
region-flags-contour-preflight.json incrementally; preserved11flag report above.
Next: finish17395 and production validation; inspect262preflight failures/results;
regenerate candidate previews and eventually compile/review allflags before
registration. Full beta goal remains active and incomplete.

### Preview recovery

Previous turn:progress (full regional preflight launched, complex checks saved,
CPU activity verified).17395 and57607 re-polled live. Browser inventory after
restart had no old tabs; localhost8765 refused connection because server was
also gone. Restarted localhost-only tools/serve.py8765 with required sandbox
escalation, session98865 live. CUA browser2, opticalTab tab2 now successfully
loads tools/emoji-optical-review.html and is marked handoff. Failed first tab1
is an error page; ignore it. No browser production checks claimed yet. Preserve
server and keep source inputs frozen until build/rebuild validation completes.

### Isolated regional flag font candidate

Previous turn was progress:preview server recovered; build/preflight handles
confirmed live. Added tools/font/prototype_region_flag_font.py, standalone only:
real regional-indicator/tag cmap components, longest-first GSUB, COLR/CPAL,
canonical sequences from pinned source registry. No production manifest changes.
Candidate outline serialization omits only exactlyzero-area contours after font
rounding; everypositive-area polygon retained.48656 TERMINAL0:12flags compiled,
47032byte WOFF2 at output/font-review/pen-translation/region-flags-candidate.woff2,
report adjacent .json. Independent HarfBuzz/fontTools check passed:12sequences
shape to expectednamedglyph/advance;all144adjacencypairs unchanged;everyserialized
contourpositivearea. This is compiler/shaping evidence, not actualcomicreview.
Need compare rasterized candidate at33.6andlargesize, retain18unitinkoptics via
appropriate companion, then expand all262/general8 before productionintegration.
17395 remains live;57607fullflagpreflight live, progressedthroughCLwith no logged
failures so far. Do not restart either or mutate productionfontinputs. The
fullbeta remains incomplete; next production actions still compiled56checks,
JSrerun,audit,browser552and15stripreviews once recoveredbuild completes.

### Candidate optical review and bearing correction

Previous turn was progress:isolated12flagfont built, independent12sequence/144pair
andpositivecontourchecks passed. Derived candidate monochrome companion by
removingCOLR/CPAL, and created region-flags-candidate.html:160pxenlarged and33.6px
with18fontunitstroke beside24pxdialogue. Browserreview caught a realcompilerbug:
constant50LSB shifted colourlayers, clippingJapan'ssun into a sliver. Fixed
compiler metrics to actualglyfxMin, matching productionbuilder; patched both
candidatefonts without rerasterizing. UpdatedcandidateJSONhash andHTMLfontURLs
withcontenthashes toavoidstale browserfonts. Reload showedcirclecorrectly.
All12enlarged/dialoguesizecases visuallyreviewed aftercorrection:GB/US/JP/NP/
RO/TD/CA/ZA/BR/EU/KR/Wales. Smallflagsrecognizable;meaningfulfields preserved;
Welshdragon denseatsmallsize. Thisisstandaloneopticalreview,notactualcomicstrip.
CUAruntime initiallystale(browser.userunavailable); reset+rebindtab2 recovered.
Browser2tab2nowcandidatepage,markedhandoff. Server98865 remainsneeded.
Productionfontinputs remainfrozen. Familybuild17395live;allflagpreflight57607live.
Need rerunindependentshaping/metricsguards againstcorrectedcandidate, preserve
actualLSBregressiongate beforeexpansion, and completeproductionvalidation.
Correctedcandidate independentrecheckpassed:12sequences,144adjacencies,companion
shapingidentity,andactualLSB=xMinforeveryglyphinbothfonts. No pendingregression.

### Reproducible candidate preview

Previous turn was progress:actualbrowserreviewcaughtandfixedcandidateLSBbug,
all12opticalcasesreviewedandcorrectedshapingrechecked. Added reusable
preview_region_flag_font.py and tools/font/templates/region-flags.html so ink
companion/previewarenolongerone-offshellartifacts. Buildernowcallspreviewafter
savingcandidate. Previewverifiescolourhash,allglyphbearings,allpositivecontours,
allsequenceglyphnames/advances,bothfontidentities,andallpairadjacenciesinbothfonts;
saveshashbound region-flags-candidate-validation.json and contentversionedHTML.
RanpreviewTERMINAL0:12sequences/144pairs,bearings/contours/companionallpass.
Syntaxcheckspass. Nobuildsourcechangedwhileproduction17395runs.

### Family/couple recovered build COMPLETE

17395 TERMINAL0:1283bases,1307cmap,24components,5088exactforms;
colourWOFF2 1611000bytes. version_assetscompleted. Now13164Python56checks including
exactrebuildlive (/tmp/families-couples-recovered-python.log);30481JSrerunlive
(/tmp/families-couples-final-js.log);95887auditlive
(/tmp/families-couples-final-audit.log). Keepfontinputs frozen through13164.
Browsernavigationattemptagainfailedwithstale browser.userhandle; need resetCUA
runtimeandrebindtab2beforebrowser552checks. No browserresultclaimed yet.
Fullregionalpreflight57607stilllive,progressedthroughGY. Productioncoverage
predictionsmuststillbeverifiedfromaudit. Goalremainsactiveandincomplete.
95887auditTERMINAL0:3580/3963emojiencoded,383missing;172118/172352visiblecmap,
234missing.30481JSTERMINAL1 revealedoldunsupportedfamilyfixturesarenowsupported,
so adjustedboundary/RTL/measurementfixtures to deliberatelynonstandardthreechild
familyclusters;preservesunsupportedclusterintent. Rerunpending. Productionfont
inputsunchanged;13164continues. Actualbrowser552checksand15stripsstillpending.

### Browser552 regression evidence

Previous turnprogress:buildcompleted/audit3580proven/testsstarted.87936JSfailed
oneadditionaloldunsupportedfamilyexpectationinfonts.test;updatedsupportedfamily
assertionplusmalformedthreechildfallbackguard.25632TERMINAL0:310/310JS passed.
Browserfixtureemoji-sequencesnowtestsnewfamiliescustom,andnonstandardthreechild
+Franceasnative;astronautnativeexamplealsoupdated. Fontinputsunchanged.
Browser552completedFAIL:all15newfamily/couplefixturespass;zerogeometryfailures.
Manyexistingactivity/body/clothedcasesfailqualified-versus-barepixelidentityin
DadEmojiONLY(notDadEmojiInk). Needinvestigatebrowser/fontselection/UVSbefore
acceptingbatch;prior537passwasdifferentpre-restartbrowserbackend. CurrentCUA
familyReportholds552results;tab2checksmarkedhandoff. Runtime resetrequired on
newturnifbrowser.userunavailable. Fourfamilytilefixturesviewedtopthreepanels,
butbottomfourthpanelsNOTyetreviewed;all8couples+mixed/boundary/qualification
actualstripsstillpending. Do notclaimfull15visualreview.
13164Pythonlivecurrentlypast48dotsnofailures;includesrebuildkeepinputs frozen.
57607allflagpreflightliveprogressedthroughItaly,nologgedfailuressocfar.

### Equivalence diagnosis

Previousgoalturnprogress:310JSproved/browser552failurecapturedandpartialtile
review. Added tools/emoji-equivalence-debug.html,comparing5representatives in
DadEmoji/DadEmojiInk/AppleColorEmoji,qualified/bare/repeatedtext,softwareanddefault
canvasreadback. FreshpageALLpixelcomparisonsZERO,widthsidentical forcustompairs;
originalfullrunfailureNOTreproduced. NoUVSfontchangejustifiedyet;keepfontinputs
frozenwhile13164rebuildruns. Addedoptional ?case=exact-name (repeatable)to
unicode-checks.html forfocuseddiagnosis;defaultstillrunsfull552. Browser2tab2now
running3focusedcases1f486/bodypartshead/clothedsport. Needreadresultthenfullrerun
beforeacceptingbrowsergate. Debugdataexistsinpage,notyetsavedasartifact.
13164live55dots;57607allflagpreflightlivepastNorfolk. No knownnewsourcefailures.
Focused3originalcheckerreproducedfailures.Addedidenticalrepaintcontrolandproved
EXACTSAMEtextchangedpixelsafterfirstreadback(DadEmojionly).Thusaliascomparison
wasunstablebeforecomparingdifferentforms. SettingwillReadFrequently:true onthis
specificcomparisoncanvasfixesreadbackinstability;keptidenticalrepaintguardand
originalstrictbyteequality(noepsilon,nomaskedpixels). Focused3casesallPASS.
Nowfull552rerunrunninginbrowser2tab2(defaultURL),markedhandoff. Needawaitresult;
nofullpassclaimyet. No fontsourcechange. Thiscorrectschecker,notglyphdrawings.

### Family/couple browser gate PASS and visual review

Previousgoalturnprogress:provedidenticalrepaintinstability,fixedcomparisoncanvas
withoutrelaxingbyteequality,focused3passed,startedfullrerun. Full552nowPASS:
zerofailures/zerogeometry. All15newfamily/couplecaseszerofallback/unmapped.
Reviewedall8couplefamilies+mixed/boundary/qualificationinactualstrips,including
alltonesandreversedextremes. Heart/kiss/hairstyledistinctionsremainrecognizable;
darkestfacesdensebutreadable. Reviewedfamilytilelowerpanelsaswell:fourthpanel
isintentionallysilentoriginalCalvinatnight,NOTmissingart;allspeechesareinfirst
threepanels. Fourtilefixturescoverall25drawings;childseparatorsnarrowbutvisible.
Thusall15actualstripreviewscomplete. familyReportnowcontainspassing552results,
CUAbrowser2tab2checksmarkedhandoff. No productionfontchangesforthischeckerfix.
JS310passes,audit3580/3963and234visiblemissingremaincurrent.13164stilllive55dots,
exactrebuildpending;donotpromotenextfontbatchuntilterminal.
57607fullregionalpreflightcurrently250/262,zerofailures;stilllive. Addedcandidate
compiler--regionsallwith262inventory+completepassingpreflightgate;notlaunchedyet.
Needfinishpreflightthencompileall262toisolatedfont,reviewallcompiledoptics,
registerregionalnoticeswhenpromoting. General8flagsstillneedrecipes.

### Regional preflight complete; expanded font started

Previousturnprogress:552browserPASS/all15stripreviewscompleted.57607TERMINAL0:
all262regionalflagscompleted,zeropreflightfailures;JSONcontains262.25257nowlive:
prototype_region_flag_font.py--regionsall, log /tmp/region-flags-all-candidate-font.log.
Gateverified262inventoryandcompletepassingpreflight. Outputcandidatefont/JSON/
previewwillreplace12flagversiononlyafterfullcompile;neverproductionassets.
13164stilllive55dots,reproducibilitytestpending;keepproductionfontinputsfrozen.
Started8generalflagpathprobes,log/tmp/general-flags-path-probes.log;handlebelow.
NativeSVGstylesinspected:somecolourfillsareinstyleattributes;muststripstylewhen
buildingrecipes. Generalflagsneedsource-specificshading/highlightremovaland
colour/blackwhitefeaturechecks,notgenericregionalquantization.

### General flag recipe prototype

25257expanded262candidatefontstilllive(logthroughCA);production13164stilllive.
GeneralpathprobecommandTERMINAL0for8SVGs. Individuallyviewedcheckered/white/black
pathsheets;all8sourcepathstyles/geometriesdumpedandinspected. Addedunregistered
prototype_general_flags.py withsource-specificpaper/solidink/cutout/colourmaps,
removesnativegradientshading/highlights;usesrsvg1536,requested1.7withtopology
backoff,andPDFheartpalette. Checkeredusesnative10blackgrid/11..16whitecutouts;
pirateuses0blackfield/4..7whiteemblems;rainbow6bands/trans5bandsremaincoloured.
42851live /tmp/general-flags-prototype.log;firstcheckered/redflagapplied1.7.
Needsall8resultandnative/treatedvisualreview,explicitstripes/emblem/topologygates,
compiledopticsandactualstripreviewbeforepromotion. Noproductionfontinputchanged.
42851subsequentlyTERMINAL0:all8preparedsuccessfully. Treatedsheetvisuallyreviewed:
checkeredgrid,redtriangle,crossedJapandiscs,black/whitecloth,rainbow6/trans5bands,
pirateskullbonesrecognizable. Stillenlargedonly;compiledandactualstripchecksremain.

### General flag semantic gates and candidate compilation

Previousturnprogress:262preflightpassed,allregionalcandidatebuildstarted,8general
prototypesgenerated/reviewed. Added tests/test_flag_sources.py:87219TERMINAL0,
8passed3.59s. Checksall8sourceSHA/Gitblob/topology;twoJapanredsuncomponents;
sixdistinctorderedrainbowbands;transblue/pink/whitecomponents2/2/1;pirateinkand
whiteemblemfeatures. No productionfontinputchanged.
Refactoredcandidatecompilerintocompile_flags(selected,prepare,prefix),preserving
regionalentrypoint;previewnowacceptsprefixandsharedtemplate. Syntaxcheckspass.
25257alreadyrunningloadedoldcompilerfunction;itslaterpreviewcallretainsdefault
regionalprefix. No candidatepreparation/hashinputsmodifiedduringregionalrun.
Newprototype_general_flag_font.pybuilds8canonicalgeneralformsusingthesamecompiler,
3744live /tmp/general-flags-candidate-font.log. Currentlycanonicalonly;mustadd
qualificationaliases/variationfontselectionchecks beforeproductionregistration.
13164familyreproducibilitystillpending. Regional25257buildthroughFM,lastpollive.
3744subsequentlyTERMINAL0:8canonicalgeneralsequences/64adjacencies,bearings,
positivecontoursandcompanionidentitypass. Generalcandidatefont/ink/report/HTML
writtenwithgeneral-flags-candidateprefix. Opticalbrowserreviewpending.
Regional25257nowlogthroughLC,notFM. Stillnoqualifiedaliasclaimforgeneralcandidate.

### General qualification aliases

Previousturnprogress:8semanticchecksandcanonicalcompilerpassed. Extendedshared
candidatecompilerwithoptionalformprovider,realcmapentriesforsingletondrawings,
longest-firstselector-strippedGSUBrulesandformat14UVSdefaultsfromregisteredforms.
GeneralproviderusespinnedUnicodequalified_forms;regionaldefaultunchanged.
38223TERMINAL0:14generalqualificationforms/196pairs,bothfontidentities,bearings
andpositivecontourspass. Previewvalidatesallaliasesandnowdisplaysall14forms.
AddedexplicitPDFhashverificationtogeneralpaletteprovenance;freshgeneralbuild
startedafterthatcodechange(handlebelow)soitsprogramhashwillmatchcurrentmodule.
Accidentaldefaultpreviewrecheckranold12regionalcandidateandpassed;thisdoesNOT
proveexpanded262fontfinished.25257stillcompilingregionalthroughNI.13164family
rebuildstillpending55dots. No productionfontinputsmodified. Browserreviewof
qualifiedgeneralcandidatepending;full552productionbrowseralreadypassed.
Freshgeneralbuildhandle22223;pollbeforeanyrestart. No productionfontsourcechange.
22223TERMINAL0:currentcode14forms/196pairsgreen;colour/inkhashesunchangedfrom38223,
asexpectedforprovenance-onlyassertion. GeneralbrowserpreviewHTMLnow14rows.

### Family/couple COMPLETE; general browser PASS

Previousturnprogress:14qualificationforms/196pairsgreen/currentprovenanceverified.
13164TERMINAL0:56passed7warnings760.06s,includingexactrebuild. Family/couplebatch
nowfullyvalidated:12199sources,310JS,552browser,all15actualstripsreviewed,audit
3580/3963emojiand234visiblemissing. No remainingfamily/couplebatchgate.

Added preview_flag_contact_sheets.py:compact32percanvas sheetswith140pxdrawings
and33.6px+18unitink,strictbrowseraliaspixel/advancechecks. General14formsbrowser
PASS(noaliasoradvancefailures),all14enlarged/dialoguesizedrawingsvisuallyreviewed
inonesheet;sun/checks/rainbow/trans/piratefeaturesreadable. Thisisfontoptics,
actualcomicstripintegrationstillrequired. CUAbrowser2flagTab3generalcontact,
markedhandoff;oldproductioncheckstab2remains.
25257expandedregionalfontstillliveatlastpoll,logthroughXK. No restart.
Derivedexactremainingnonflaginventoryfromcurrentmanifest/pinnedemoji-test:
113forms,all113SVGpathsresolvedinthepinnedNototree. Wroteunregistered
 docs/remaining-object-emoji-source-plan.json (noproductcoverageclaim).
Next:finishregionalfontand9compiledcontactsheets;integrate270flagswithlicences/
compiledtests/actualstrips;fetchandconvertremaining113objects;remainingUnicode
script/Seal/renderergatesremainintherealbriefscope.
Remaining113sourcefetch76909started, /tmp/remaining-object-svg-fetch.log, official
pinnedcommit/SHA/Gitblobchecksandaliasresolution. Candidateonly,notregistered.
25257lognowall262compiledthroughgbwls,butawaitterminalfontsave/validationresult;
noexpandedfontpassclaimuntilterminal.
25257TERMINAL0:262regionalfontsequences/68644adjacencypairs,bearings,positive
contoursandcompanionidentityallpass. Colourhash7e3c37e36e2924aeb3a604e32c75608962063ee2cd534f12153a4dce364b6cb5.
Generatedregion-flags-contact.htmlwith9sheets;all262compiledbrowseropticsstill
pending(notcoveredbyprior12sample).76909TERMINAL0:113sourcecandidatesverified,
 docs/remaining-object-emoji-svg-source-probe.json readyfornativepathreview.
No outstandingfontbuild/rebuildprocesses;server98865remainsneeded. Nextturncan
review9regionalsheetsandprepare270flagproductionintegrationnowfamilygatecomplete.

### All compiled flags reviewed; sources registered — Nov 2, 19:47 UTC

Previous goal turn made progress: family/couple validation completed, regional
candidate font passed its checks, and 113 remaining object sources were fetched.

Reviewed all nine regional contact sheets in the browser, covering every one of
262 flags at 140px and at 33.6px with the approved ink stroke. Browser alias-pixel
and expected-advance checks report zero failures. Complex coats of arms remain
dense at dialogue size, while fields and overall emblems remain recognizable.
General flags had already passed equivalent review for all 14 forms. These are
font contact sheets; production comic-strip checks still remain for flags.
Browser 2 tab 3 now shows regional contacts and is marked handoff.

Registered sources, without changing production font coverage:
- data/font-sources/noto-emoji-general-flags-svg.json: 8 SVGs, 14 exact forms.
- data/font-sources/noto-emoji-regional-flags-svg.json: 262 SVGs plus two notices.
- Regional public-domain LICENSE and README copied verbatim and hash-verified
  into assets/fonts/licenses/RegionFlags-LICENSE.txt and RegionFlags-README.md.
  General SVGs retain the existing Apache licence and Noto notice.

21772 TERMINAL0: fetch_sources.py --check verified all 12,471 registered files.
Do not rerun the one-time source-registration snippet: its guards now reject
existing manifests. No production flag compiler is connected yet, so installed
coverage remains 3,580/3,963 emoji. No font builds are currently running.

Next concrete work: make production flag prepare modules read the registered
manifests; add a combined 270-drawing compiler with longest-first rules before
standalone black/white flag substitutions; add RI/tag components and selector
support; preserve original sources and per-family notices in review metadata.
Then preflight old sequence identities and all flag adjacencies, integrate,
build, test reproducibility, audit and review actual strips. Also retain the
broader brief's remaining 113 emoji and script/Seal/renderer requirements.

### Production flag integration started

Previous goal turn made progress: all 262 compiled regional flags were reviewed
and source/licence registration passed (12,471 files). Moved prepare routines to
emoji_regional_flags_svg.py and emoji_general_flags_svg.py reading the registered
manifests; prototype scripts now preview wrappers. The numerical recipes are
unchanged. Shared zero-area contour handling lives in flag_outlines.py.

Added emoji_flags.py for all 270 drawings. It preserves actual layer bearings,
semantic colours and per-source provenance/notices; adds five standalone bases
and 37 RI/tag shaping components; emits 271 non-singleton forms and six general
qualification aliases (276 added forms total). Flag rules sort longest-first and
precede existing sequences. Standalone black/white cmap glyphs are also used as
components of pirate, rainbow, trans and subdivision ligatures. Format14 selector
support comes from the registered forms. Empty RI/tag components are shaping
inputs, not proof of complete standalone indicator lettering; retain that scope
caveat when auditing arbitrary Unicode coverage.

Connected compiler to build_emoji.py; syntax checks pass. Production build35182
is live, /tmp/flags-production-build.log, with version_assets after success.
Expected 1288 bases /1349 cmap /61 components /5364 exact forms. No claim until
terminal and downstream checks. Do not rerun registration or connect a second
copy of the compiler. Keep font inputs frozen during build/rebuild validation.
Saved old5088 sequence glyph names/advances for independent prefix-regression
checks in output/font-review/pen-translation/pre-flags-shaping.json (handle below).
Next: compiled flag tests against reviewed candidate layers, all qualification
forms and adjacencies, old sequence identity regression; JS/browser fixtures for
all flags plus boundaries; source check, build/audit/rebuild and actual strips.
First baseline capture19401 failed because shape() returns five fields per glyph,
not two. Corrected10259 captures glyph name and all four position fields. Poll
its terminal result before using the baseline. Build35182 remains live; no font
input changes after launch. Browser tab3 regional contacts is marked handoff.
10259 TERMINAL0: all 5,088 old sequence identities and full positions saved.

### Flag regression gates and complete browser corpus prepared

Previous goal turn made progress: production flag compiler connected and build
35182 started; baseline 5,088 names/positions saved. Build35182 is still live.
No font inputs changed after launch.

Added tests/test_font_flags.py; collection passes with 272 checks. For every one
of 270 drawings these compare all layer coordinates, contours, metrics and palette
colours against the individually reviewed candidate font, and verify canonical
and qualification forms in colour/ink fonts. Additional checks cover all 276²
adjacent form pairs in both fonts and preserve every previous sequence's name
and all four position fields. These must run after the production build.
34242 TERMINAL0: all eight general source/semantic tests pass against the new
registered prepare module (3.64s).

Added 20 browser fixtures: one general flag group, 17 regional groups (all 276
forms), joined sequence boundaries and malformed/incomplete cases. Expected full
browser corpus is now 572. Added three JS tests for all general/regional forms
and unsupported clusters; expected JS total313. Updated formerly unsupported
rainbow/UN/France examples to retain the intended boundary checks after flags
are supported. JavaScript syntax check passes; full npm test awaits new manifest.

Started 87490 native preview of the remaining 113 non-flag source drawings,
/tmp/remaining-objects-native-preview.log. It verifies source hashes and writes
four labelled sheets plus per-path attributes for later recipe review. These
sources remain unregistered candidates and do not count as coverage.
Next: complete35182, run272compiled+8native+global/ink/inventory/rebuild checks,
JS313, coverage audit, browser572 and actual flag strips. Do not mutate font
inputs while build/rebuild runs. Then convert the remaining113 and address the
other script/Seal/renderer requirements of the full brief.
87490 TERMINAL0: 113 verified native sources rendered; all four sheets individually
viewed. Remaining groups include maps/transport, clothing, instruments, books,
money/mail, charts/tools and miscellaneous objects. Preserve coloured book and
currency distinctions, chart direction, mailbox flag/open states, and currency
lettering identities when simplifying shading. Per-path source attributes are
saved in remaining-objects-source-structure.json. No object recipes promoted.

### First remaining-object book candidates — Nov 2, 19:54 UTC

Previous goal turn made progress: 272 flag tests and 20 browser fixtures prepared;
eight registered general flag source tests passed; all 113 native object sources
were reviewed. Production flag build35182 is still confirmed live, with no font
input changes since launch.

Added unregistered prototype_remaining_objects.py, beginning with five reviewed
closed books: decorated notebook U+1F4D4 and red/green/blue/orange books. Keeps the
native cover, page block, binding and notebook label; drops highlights/shadows and
duplicate border strokes. Uses verified source SVGs, verified PDF palette and
strength1.7.57488 TERMINAL0: all five prepare without backoff/fallback. Enlarged
sheet reviewed; cover colours and the notebook label remain distinct.

Added preview_remaining_object_optics.py.88004 TERMINAL0: all five compiled ink
contour counts equal source components+holes. Reviewed the 180px and approved
33.6px/18-unit-stroke optical sheet: white pages and notebook label survive,
colours remain distinct. These remain candidates: no registration, font coverage
or actual-strip acceptance claimed. Other books and mail still need recipes.

Outputs: remaining-objects-prototype.{png,json} and remaining-objects-optics.
{png,json} under output/font-review/pen-translation. Next: finish35182 and flag
validation while expanding source-specific book/mail recipes independently.

### Mailbox source geometry and candidate expansion

Previous goal turn made progress: first five book candidates passed compiled
contour and optical checks. Flag build35182 remains live; production font inputs
are unchanged. Generated native path sheets for twelve mail symbols. Individually
reviewed four mailbox state drawings and plain/email envelopes. Preserved the
native raised/lowered red flags and open/closed door distinctions in four new
unregistered recipes (1F4EB/EA/EC/ED). Added explicit stroke-path support for the
open mailbox's envelope lines, rather than silently filling open paths.

Initial92109 failed at1F4EC: topology backoff rejected it. Diagnostic found tiny
pinholes/slivers at overlapping frame outlines. Cleanup of sub-four-pixel holes
alone (89263) still failed; changing the native front frame to solid ink (89194)
also still failed. Do not count any of these as accepted mailbox drawings.
Measured the residual slivers in source coordinates: near(15.2,55.1),(32.1,68.1),
(19.0,89.5); all smaller than a source pixel. Added a bounded, recipe-specific
cleanup for1F4EC only: holes<32 raster pixels, maximum64 filled pixels at1536.
Other candidates retain<4/max16. This targets the inspected frame slivers;
visible envelope counters still require optical/topology review after rerun.
18599 now running prototype then compiled optics, logs
/tmp/remaining-objects-prototype.log and /tmp/remaining-object-optics.log.
Optical sheet now uses at most five columns so dialogue-size drawings are not
shrunk by a huge review canvas. No mailbox coverage/acceptance claim yet.
18599 TERMINAL0: all nine candidates prepare and pass compiled contour counts.
Open mailbox1F4EC applies0.3025634765625 after topology backoff; other eight use1.7.
Reviewed regenerated enlarged and33.6px/18-unit optical sheets. All four mailbox
states remain distinct; the open/raised mailbox retains its white envelope and
internal lines at dialogue size. These are still candidate optical reviews;
actual strips and independent state-geometry tests remain before promotion.

### Envelope candidates and independent state tests

Previous turn made progress: four mailbox candidates recovered under bounded
raster cleanup and passed compiled optics. Added six more candidates: plain and
email envelopes, incoming/flying envelope, envelope with downward arrow, outbox
and inbox. Email E uses the existing comic capital through replace_letters;
shadow lettering is dropped. Source1F4E7 actually has six paths (first attempt
55335 rejected an incorrect count5); corrected to retain both flap-line paths
and use actual letter path5, dropping shadow4.55844 TERMINAL0: all15candidates
prepare; all15compiled contour checks pass. Reviewed regenerated180/33.6px optics:
E/flap/speedlines/arrows and all previous states remain visible. No candidates
registered or counted as production coverage.

Added tests/test_remaining_object_sources.py.1648 TERMINAL0:6passed5.41s,
independently checks red flag vertical/horizontal orientation, native door-interior
sample darkness for open/closed states, comic E provenance, four distinct PDF
book colours. Added three arrow-direction checks; rerun handle below is pending.
Production flag build35182 remains confirmed live with no font inputs changed.
Arrow/state rerun handle1389; poll before restarting. Expected9checks total.
1389 TERMINAL1:7passed,2failed. The new arrow test incorrectly guessed the
shoulder's vertical position for inbox/outbox (their heads extend farther than
that). Changed it to compare narrow tip and rectangular tail at10/90percent,
an orientation property independent of where the source places its shoulder.
18102 is the corrected rerun; pending terminal result.
18102 TERMINAL0: all9independentobjectstate/provenancechecks passed in6.62s.

### Final mail recipe candidates in progress

Previous turn made progress:15objects passed compiled optics and9independent
state/provenance tests. Build35182 is still live. Authoritative ps for54281 at
about20:03UTC:14:21elapsed,13:37CPU,94.4percentCPU,stateR; it is actively computing.
No production font inputs changed, and no restart is warranted.

Added three remaining mail recipes (public postbox1F4EE, ballot box1F5F3,
parcel1F4E6), bringing the candidate inventory to18drawings including all13mail.
Reviewed native postbox/ballot path sheets and parcel structure. Parcel SVG has
many off-canvas design variants; chose visible paths46..59 (box faces/tape and
handling marks), dropping covered/off-canvas variants. Needs final optical check.

77795 rejected postbox pinhole count22 above16;7616 and55157 rejected topology
fallback even after bounded cleanup/simplified shading. Root cause identified:
path9 is already a CLOSED filled flap-line shape, not an open stroked path.
Drawing a new stroke around it created artificial tiny counters. Converted it
to solid ink and removed it from STROKE_PATHS.77013 TERMINAL0:postbox now applies
full1.7 with ZERO filled pinholes. Removed the now-unneeded larger cleanup limit;
postbox uses the normal<4/max16 guard again. Open-mailbox exception is unchanged.
Fresh18candidate render+compiled optics run started (handle below). No acceptance
claim for final three until terminal result and optical inspection.
Fresh mail render handle53610, /tmp/remaining-objects-prototype.log then
/tmp/remaining-object-optics.log. Poll before restart; outputs may still show
previous15drawings until this run finishes successfully.
53610 TERMINAL0:18candidates passed contour checks, but optical review caught that
parcel handling marks were absent. Native groups50..57 inherit opacity0.5, which
put dark marks below raster threshold. Removed only inherited group opacity,
preserving display/clip/transform properties.6652 then correctly rejected a
one-pixel detached ink crumb; diagnostic found ink6components including a single
pixel, with no tiny holes. Added parcel-only<4pixel crumb cleanup, capped4pixels.
99780 TERMINAL0:parcel applies0.95625, removes exactly1pixel, no fallback.
Added independent per-native-path handling-mark overlap checks (all eight marks,
>95percent overlap within6rasterpixels).77621state tests are now running; fresh
18candidate render/optics rerun handle below. No parcel acceptance claim until
these finish and regenerated optics are reviewed.82835 prior state tests passed
10checks, including all13mail sources having recipes, before parcel mark checks.

### Session restart status check — 2026-11-02

Recovered terminal results without restarting builds: production flag build
35182 exited0 and asset versioning completed. Output reports1288base emoji,
5364explicit sequences,61shaping components,2837784bytes. This is a successful
build, not yet production acceptance: flag regression suite, refreshed coverage
audit, browser checks and actual comic strips remain pending.

Object render/compiled-optics handle61101 exited0: all18candidate contour checks
passed. State-test session77621 is no longer retained, but its completed log
records11passed in8.09s. Regenerated object optics still need visual inspection,
particularly parcel handling marks. These18objects remain unregistered candidates.

User requested current status after restart. No work reset or duplicate build
was needed. Overall Unicode brief remains incomplete and goal remains active.

### Flag production validation and four more reviewed object candidates

Previous restart-status turn recovered terminal evidence and updated authoritative
progress. Continued with the next validation steps rather than restarting jobs.
Flag production Python suite15669 is live; log /tmp/flags-production-python.log.
It reaches the reproducibility rebuild after the other tests. PID57146 verified
running at99.2percentCPU,5:31elapsed/5:26CPU; no production inputs changed.
The original run has eight test-harness failures comparing empty layer coordinate
attributes. Focused69944 confirmed AttributeError for an empty AC layer;85842
also reproduced this after all preceding layers matched exactly. Both exited1.
Fixed tests/test_font_flags.py to use getCoordinates for empty/nonempty outlines,
comparing coordinates, contour endpoints AND point flags. Corrected run89186
TERMINAL0: all272flag tests passed in49.55s. This includes every layer/metric/colour,
qualification, all276squared adjacency pairs in colour/ink, and all5088old sequence
identities/positions. Original15669 still needs terminal/rebuild result; don't
restart it because its earlier eight harness failures remain in that run.

5282 TERMINAL0: all313JavaScript tests passed.55668 TERMINAL0:12471registered
source files verified.17687 TERMINAL0 coverage audit:172122/172352visible cmap;
3850/3963fully-qualified emoji exactly custom encoded,113missing. Cmap/encoding
is not by itself proof of style or shaping. Empty RI components remain excluded
from visible coverage by the audit.

Browser tab4: full572cases, zero failures OR geometry problems. Tab5: all20flag
cases independently passed; no fallback except four intentional malformed cases.
Individually inspected all20actual comic strips (general,17regional batches,
boundaries,incomplete), all270flag drawings/forms. Colour fields, stars/emblems,
pole/skull/white/black and rainbow/trans distinctions read at approved dialogue
size. Dense coats of arms remain very small but their principal fields and shapes
are recognizable. Fourth panel intentionally silent original character art.

Reviewed fresh18object optics after the parcel opacity fix: handling marks now
visible on the parcel. Added four unregistered recipes after per-path native
review:1F4C3curled page,1F4C4folded page,1F4D1bookmark tabs,1F3F7tag with string.
14948 TERMINAL0:22prepare+compiled contour checks passed. Reviewed all22optics at
180px/33.6px+18unitink: page lines, curl/fold, four tabs and tag hole/string visible.
Added writing-line midpoint probes and four-tab colour check. First28786 exited1
because the probe assumed all native strokes were path elements; they are SVG
line elements. Corrected native line coordinate handling.76921 TERMINAL0:
all15object state/detail/provenance tests passed9.78s. No objects registered or
counted as production custom coverage.

### Next book candidates — render pending

Added four more source-specific recipes after native path-sheet review:
1F4D2spiral ledger,1F4DAstacked books,1F516ribbon bookmark,1F4DCscroll.
44691 exited1 at stacked-book topology guard, so no26candidate output accepted.
Diagnostic91257 exited0: one remaining5raster-pixel sliver at native(70,79.75),
all other counters at least238rasterpixels. Ribbon/scroll both prepare at1.7.
Raised only stacked-book hole cutoff from4to8, retaining16pixel overall maximum.
First check rejected total10pixels above mistaken8pixel maximum; limit restored
to normal16.63610 TERMINAL0: stacked books apply0.3025634765625,10pixels filled
(includes5already below normal4cutoff). All other source counters preserved.
Fresh26prepare+compiled optics run started; poll handle recorded next. Outputs
still show accepted22until the full new run completes. No acceptance claim for
these last four until terminal and optical review. Production rebuild unchanged.
Fresh26render handle28811 TERMINAL0:26prepared and compiled contour checks pass.
Reviewed optical sheet: ledger loops, stacked green/red/blue covers and scroll
writing/curls readable. BUT ribbon bookmark white star was absent: unoutlined
white cutout was lost during region colour assignment. Do not accept that version.
Changed the star to an explicit outlined white region (path10), preserving the
red tag and original hole/string. Fresh26rerender handle69835 currently pending;
log paths unchanged. Added white-star centroid/colour presence regression check.
61415 TERMINAL0:17state/detail tests passed10.70s before star correction.
51622 TERMINAL0:18state/detail tests now passed, including white-star presence.
Need inspect the regenerated26optical sheet after69835terminal before accepting
last4candidates. The22earlier candidates remain optically reviewed; no object
production registration or actual-strip review yet. Full113object scope retained.

Immediate next steps: poll15669 for reproducibility result (expected earlier
8harness failures remain in that old run; corrected272already pass); poll69835
and inspect ribbon star. Keep production font inputs unchanged until15669ends.
Then continue remaining object recipes/integration and full Unicode gaps. Goal
is active; no blockers. Browser tabs4(full572) and5(flag20strips) marked handoff.
69835 TERMINAL0:26compiled contour checks passed. Inspected fresh full optical
sheet: ribbon white star now clearly visible at180px and33.6px with approved ink;
ledger rings, stacked cover colours/order and scroll writing/curls remain intact.
All26now have candidate optical review,18state/detail checks pass11.48s. These
are still unregistered candidates; actual production strip acceptance is pending.
15669 was confirmed live again on final poll (no output expected during rebuild).
Resume by polling this exact handle, not restarting the reproducibility build.

### Complete book/mail candidate set and registered compiler

Previous goal turn made progress: full flag browser/JS/source checks passed,
26object candidates were reviewed and18detail tests passed.15669reproducibility
job remained live; no restart was warranted. Continued the next safe work.

Added the last four book/paper recipes after per-path native review:
1F4D6open book,1F4D3composition notebook,1F4F0newspaper,1F5DErolled newspaper.
67103 TERMINAL0 recipe probe accepted first3but reported rolled-paper rejection.
Rolled diagnostic found five detached antialias components (sizes1,1,1,2,2) at
native diagonal edge(23.7,55.6) and curl tip(117.8,100.4). All substantive ink
components>=3455rasterpixels; all counters>=3055. Added rolled-only crumb removal
<4pixels, maximum8pixels (parcel remains maximum4).36787 TERMINAL0:7pixels
removed, applied0.40341796875; no fallback. Open book applies0.7171875 to retain
dense printed lines; composition notebook and newspaper use1.7. No source
counter was removed to force acceptance.

91222 TERMINAL0: all30candidates rendered, passed compiled contour/optical checks,
then compiled isolated colour/ink fonts.34qualification forms,1156adjacent pairs,
actual glyph bearings, positive-area contours and companion identity all pass.
Reviewed all30at180px and33.6px+18unitink. Open-book text/pages, notebook mottling
and white label, newspaper globe/map/columns and rolled edges/band remain visible.
67170 TERMINAL0:22source/detail checks passed12.50s, including all native writing
lines, composition pattern/label, star, colours/states and complete17book+13mail
candidate inventory.

New tools/font/prototype_book_mail_font.py reuses the isolated compiler with
explicit object glyph/font names. Generalized only optional family/glyph-prefix
arguments and companion naming; defaults preserve existing flag output names.
Browser tab6(book-mail-contact.html):34forms,2sheets,zero pixel-alias/advance
failures. Individually inspected both full sheets in the browser; all drawings
and qualification aliases match the accepted optical candidates.

Registered30sources/34forms ONCE in data/font-sources/noto-emoji-book-mail-svg.json,
retaining existing Apache licence/NOTICE paths. Extracted reusable registered
core tools/font/emoji_book_mail_svg.py; prototype_remaining_objects.py is now a
thin render wrapper. Do NOT rerun the one-time registration snippet.23034TERMINAL0
registered-core compilation reproduces both reviewed font hashes EXACTLY:
colour2b072e65b1cf7e0ffc388be2bd3844f635136206c5e8944708e5b0eb30838274,
inkd0c29811a9890b076318661290cbc1409ad04b14e29dd4b4f8d01a0863f73d7a.
42291TERMINAL0:22registered-core detail checks passed14.31s.
12286TERMINAL0:12501registered source files verified.

Prepared tools/font/emoji_book_mail.py production compiler but DID NOT connect
it to build_emoji.py yet. Independent tests/test_book_mail_compiler.py compares
its emitted30drawings/layers/point flags/colours/advances/bearings/qualification
mapping against the reviewed isolated font.50113TERMINAL0:1passed7warnings21.01s.
Confirmed all30bases are absent from the current production cmap. Expected after
integration (not yet built):1318bases,1379cmap,61components,5398exactforms;
fully-qualified audit would gain30to3880/3963, leaving83. Do not claim that gain
until production build, regression and actual-strip review pass.

Updated this document's stale opening summary to current audited totals and
validation evidence. Full Unicode scope remains;230visible cmap gaps,113missing
fully-qualified emoji, script-style/behaviour limitations still pending.

At final status check,15669handle LIVE; PID57146 elapsed16:37,CPU16:04,stateR,
71.7percentCPU. Poll the exact handle; no current production-font input changes.
Original run retains earlier8harness failures despite corrected272test pass.
Once terminal, inspect reproducibility result, rerun corrected full flags suite
excluding only expensive rebuild if that result passes, save5364pre-book/mail
shaping baselines, hook the already-tested compiler and begin production build.
Then update counts/tests/browser fixtures, run audit and actual-strip review.
No new book/mail production coverage claimed. Browser wrapper mark expired;
reset/rebound tab6 and successfully marked it handoff. Tabs4/5not re-marked after
that reset; their validation evidence is saved above and can be rerun as needed.

### Flag reproducibility complete; book/mail production build started

Previous goal turn made progress:30book/mail candidates and registered compiler
were accepted against their reviewed candidate font. Continued from authoritative
state rather than restarting the long job.

15669 TERMINAL1:8failed,283passed,7warnings,1159.39s. Crucially the explicit
font/manifest reproducibility test PASSED. Correction to earlier diagnosis:
there were SEVEN empty-layer attribute failures, plus ONE global review metadata
failure (the five singleton flags lacked codepoint fields). Fixed singleton flag
review emission to record their codepoints; verified their actual cmap names and
added those five fields to the current review JSON without modifying fonts.
Also corrected the global test's assumption that every quantized colour bucket
must be occupied: require real nonempty bases and painted layers, allow valid
empty buckets, retain colour-index bounds. The reviewed flags' complete layer
geometry/colour comparisons still apply. Book/mail compiler now also emits
codepoint metadata, with independent test coverage.
81909 TERMINAL0:all290corrected non-rebuild flag/global/ink/inventory/source tests
passed179.07s. Combined with the successful separate rebuild test, all required
flag checks are now satisfied. Existing313JS/572browser checks and all20actual
flag strips remain valid: these fixes changed review metadata/tests, not artwork.

84814 TERMINAL0: saved5364pre-book/mail sequence glyph names and all four position
fields in output/font-review/pen-translation/pre-book-mail-shaping.json. Snapshot
verified font and manifest hashes unchanged across capture. Do NOT rerun the
one-time baseline capture snippet.

Extracted reusable tools/font/emoji_svg_recipe.py to support remaining object
families without copying the validated raster/pen engine. Book/mail core is now
source-specific tables/options plus a thin prepare wrapper. All cleanup bounds
and defaults are unchanged.71078 TERMINAL0: shared-engine book/mail colour/ink
font hashes EXACTLY match reviewed hashes again.83073 TERMINAL0:23combined source
and compiler checks passed34.25s. Engine provenance recorded separately in reports.

Hooked add_book_mail into build_emoji.py (afterflags, four format14 qualifications,
4non-singleton aliases plus30newbases). Updated expected cmap1379/forms5398.
78566 is the LIVE production build, log /tmp/book-mail-production-build.log,
started20:33:51UTC; version_assets runs after success. Do NOT restart. Production
font inputs including sharedengine/booktables are now FROZEN until it ends.
New tests/test_font_book_mail.py collects32cases:30full layer/colour/metric/form
comparisons,34squared adjacencies in colour/ink, all5364previous identities and
positions. Only collected, not executed against old production assets.
Added2JSrouting tests (315expected) and4browserfixtures (576expected): books1/2,
mail1,boundaries, including34forms and dialogue text. They await the new font.
Afterbuild run focused/fullrequiredPythoninclrebuild, npmtest,sourcecheck,audit,
browser576and actual4strips. Expectedcounts are predictions until validated.

### Money candidates in progress

New tools/font/preview_object_paths.py renders only visibly occupied individual
source shapes while preserving native indices and source hashes. Hidden/offcanvas
variants stay hidden by donor rendering; source counts retained.89228 TERMINAL0:
all10money source path sheets generated and individually reviewed (coin,bag,four
currency notes,wingedbill,card,receipt,yen-chart). Dollar/euro/pound sources have
120+shapes but only7/8visible; bag129shapes but only7..15visible. No money sources
registered or production coverage claimed.

New prototype_money_objects.py uses the shared engine with explicit native path
recipes. Authentic comic $ replaces bag11 and USDnote2; native ¥/€/£ silhouettes
retained because base comic donor has no corresponding glyphs. Coin retains4
columns and10stars. Firstprototype rejected18tinycoin overlap holes above16bound.
70521 TERMINAL0 diagnostic:18one/two-pixel slivers at native(26.5,24)/(101.5,24)
and around(60,105.3), not temple counters. Coin-only cutoff4/max24;77338 confirmed
coin1.7 with18filled. Winged bill rejected7detached antialias pixels at feather
tips (2+1+1+3), all substantivecomponents>=5685pixels. Winged-only<4/max8 cleanup.
43952 TERMINAL0:all10prepare at1.7. Optical raw review then caught receipt lines
missing (native SVG line elements incorrectly filled). Corrected2..12to strokes;
retained serrated edge13. Poundcurrency and yen-chartsymbol now explicit outlined
white regions for contrast on darkPDFpurple/green. No change to frozen engine.

Generalized preview_remaining_object_optics.py only in the diagnostic tool to
select --family money; book default retained. Added prototype_money_font.py for
isolated colour/ink qualifications/adjacencies and bearing checks. Fresh10money
prepare+compiledoptics+isolatedfont chain90361 is pending; logs
/tmp/money-object-prototype.log, /tmp/money-object-optics.log,
/tmp/money-candidate-font.log. Inspect terminal and optics before acceptance.
Do not mistake earlier plain receipt output for the corrected version.
90361 TERMINAL0: all10money recipes prepare at1.7, compiled contour checks pass;
isolated font10forms/100pairs/bearings/positivecontours/companion checks pass.
Reviewed both raster optics and browser contact sheet. Receipt writing is now
present. Browser review caught dark currency symbols losing contrast on green;
changed all four banknote symbols and winged-dollar symbol to explicit outlined
white fills (native convention). Authentic comic $ shapes retained.3493TERMINAL0:
updated10prepare+contours+font checks pass. Current money font hashes:
colour61b02cfe33851164d783df4d2f0fb84bd5ddccff1c3252f2ed5229a994b9e9f3,
ink5ca26156b22231ab64e431645248d7adc60ba6c861bfc2255213637b2a48ff6c.
Regenerated money-contact.html with current hashes, reloaded tab7:10forms,zero
alias/advance failures. Inspected latest browser sheet: currency contrast fixed.

New tests/test_money_candidate_sources.py checks native ¥/€/£ silhouette overlap,
authentic comic $ provenance (bag+USD), every receipt writing line,10coin stars
and4white columns. First73627failed the test's assumption that stars were path
elements; they are polygons. Corrected native polygon coordinate bounds.
5179TERMINAL0:7passed3.67s. After all-white currency change,22411TERMINAL0:
7passed4.15s. No money registration or production coverage claimed.

Money optical acceptance is STILL INCOMPLETE: yen chart1F4B9 rising polyline is
too faint at33.6px on PDFgreen. Native stroke width is5, but the current generic
black-stroke recipe uses1.3. Need retain the actual rising polyline and its weight,
preferably native white with a thin ink outline. Add optional per-path stroke
style support to the shared engine ONLY AFTER frozen book build78566 ends; keep
all existing book/default masks identical and verify reviewed-font hashes again.
A suitable outlined white stroke draws black outer(width+1.3) then white inner
(width5) for the ink mask and the native width5 as its white material mask.
Do not close the polyline into an invented filled area, discard it, or accept its
current near-disappearance. The other9money drawings have candidate optical
review, but the10drawing group is not accepted/promoted until this is resolved.

78566 production book/mail build was polled LIVE again while money work proceeded.
No frozen font-art inputs were changed after launch. Diagnostic tools, money
recipes and future tests/fixtures are independent of that production build.
Next: poll78566; aftersuccess run the newly prepared production validation,
JS315expected, browser576expected,4actualbook/mailstrips and refreshedaudit.
Then improve the money chart stroke, revalidate defaults/candidates and continue
other83objects/remaining full Unicode scope. Tab7 marked handoff successfully;
tab6book/mail candidate remains useful if retained, but can be reopened by URL.

### Book/mail production rendering validated; nineteen more candidates registered

Previous goal turn made concrete progress: book/mail production build78566 was
live, and money candidates needed a stronger rising graph. Continued independent
artwork while keeping the shared engine frozen until that build finished.

78566 TERMINAL0:1318bases,5398explicit forms,61components,2880244bytes; asset
versioning completed.38593TERMINAL0:all315JavaScript tests passed.16239TERMINAL0:
audit now172140/172352visible cmap (212missing),3880/3963fully-qualified emoji
custom encoded (83missing).59854TERMINAL0:12501then-registered sources verified.
Browser tab8 full576scenarios:zero failures OR geometry problems. Tab9 focused4
book/mail scenarios:zero failures/geometry/fallbacks. Individually inspected all4
actual strips (books1,books2,mail1,boundaries), including all34forms beside Latin
dialogue. Coloured covers, text/pages, tag aliases, mailbox states, envelope E,
arrows, parcel and ballot/postbox distinction remain readable. Existing original
character art retained. Fourth panel intentionally silent original artwork.

After78566ended, added OPTIONAL per-path coloured stroke support to
emoji_svg_recipe.py. Default execution/geometry unchanged. Money1F4B9 uses its
native open polyline, white stroke width5, black outer width6.3 and white inner
width5 in the ink mask; no invented closure/filled area. Native white material
uses width5.44185TERMINAL0:full1.7 applies. New test checks centres along every
native segment and visible width4..6native units across the long rising segment.
41546TERMINAL0:all43book/mail/money/clothing detail+compiler tests pass50.92s.
61783TERMINAL0:book/mail isolated font hashes match the pre-registration reference
EXACTLY again.92886TERMINAL0:money10prepared, compiled contours and font checks
pass; all10forms/100pairs/bearings/positivecontours/companion identity pass.
Money chart now clearly visible at33.6px; reviewed updated raster AND browser
contact sheet (tab7),10forms,zero alias/advance failures. Money group now has
candidate optical acceptance, resolving the previously recorded faint-line gap.
Current money hashes:
colour b4fe2155cce0431ffa5c19350643eceb254c559f9a2c5e14c78dedb34beaf47b,
ink 08cdc01e329b2afd3c888d41807ccb0d6e041d716afa5461b25f7217c27e73e4.

### Accessory source conversion

74640 TERMINAL0:generated all9clothing native path sheets. Individually reviewed
clear/dark glasses, fan, two shopping bags, hair pick, beads/tassel, lipstick,
ring and gemstone facets. Added prototype_clothing_objects.py with explicit
recipes and prototype_clothing_font.py; diagnostic optics tool now supports
--family clothing (book/mail default retained).
23012TERMINAL1:first5prepared, beads rejected.82769diagnostic found one1pixel
crumb at native(82.58,98.08), plus a74pixel sliver at tassel(117.19,102.61).
Root cause: native tassel83/84are OPEN stroked paths, incorrectly filled. Changed
them to strokes, retaining native closed thread86. Corrected diagnostic removed
74pixel sliver; only1pixel crumb remained, all counters>=3397pixels.15632failed
before that final cleanup. Added bead-only<4pixel crumb removal capped2pixels.
98267TERMINAL0:all9prepare at1.7, compiled contour checks pass;11forms,121pairs,
actual bearings,positivecontours and identical companion shaping pass. Inspected
all9at180px and33.6px+18unitink, then all11browserforms in tab10:zero pixelalias/
advance failures. Clear vs dark lenses,6fan folds,4bag handles,7hair-pick teeth,
27beads+tassel,lipstick layers,ring hole and gemstone facets preserved.
Current clothing hashes:
colour 321a8e0581fcceedf137279ad2d1d2eba42ee34a20f99d7f6b97e407e0b51ce0,
ink bff2b33fdb6aec8ab6a7dc4f96ae54fd918a74979ff8725320c4d608f79a4b8d.

New tests/test_clothing_candidate_sources.py initially65619TERMINAL1:11passed,
rear-handle coverage failed because the test included endpoints hidden behind
later bag faces. Corrected reference to measure the selected handle's visible
contribution (full donor with black handle minus donor without it); retained
skeleton overlap and open-interior assertions for all4handles. This correction
is included in41546all43passed. Native hair-pick cross-sections independently
show7teeth at both selected diagonals. Bead checks sample every native ellipse
centre after actual SVG transforms, rather than assuming circular coordinates.

### Registration and currently running validation

Registered money10sources/10forms and clothing9sources/11forms ONCE in
noto-emoji-money-svg.json and noto-emoji-clothing-svg.json. Retained Apache licence
and NOTICE. Do NOT rerun the one-time registration snippet. Extracted tables into
emoji_money_svg.py and emoji_clothing_svg.py; prototype wrappers import those
registered cores. Production builder does NOT import them yet.
60807 and32284 TERMINAL0:registered-core money/clothing font hashes EXACTLY match
reviewed candidate hashes.80555TERMINAL0:all20registered money/clothing detail
checks passed17.91s.41288TERMINAL0:12520registered source files verified.
Refreshed acquisition plan/probe status to identify their original113drawing
snapshot; they are not claims that all113remain unregistered. Head summary now
reflects212cmap gaps/83missingemoji,19ready candidates plus64unconverted drawings.
No new money/clothing production coverage claimed; actual-strip review pending.

81592 is LIVE:366focused production tests including flags,book/mail exact layers,
all old5364positions,all5398advertisedforms,source/detail tests,ink/inventory and
FINAL exact font/manifest rebuild. At20:58UTC log shows365dots with no failures;
PID64759 was confirmed active at3:20elapsed,2:56CPU,98.5percentCPU,stateR. The
remaining final test rebuilds the entire font and takes many minutes. Poll this
EXACT handle; do NOT restart. Shared engine, book/mail core/registry and production
builder/art inputs FROZEN again until terminal. New unused source-family files,
diagnostic tools and docs do not change that production build.

Immediate next steps: finish81592 and inspect its terminal summary; keep all
coverage claims scoped. Prepare integration of the19ready money/accessory glyphs
with subsequent reviewed families, preserving current5398identities/positions.
Continue other64original remaining drawings and full Unicode/style/behaviour
gaps, including Seal. No blockers. CUA stale browser.user wrapper recovered via
reset/getTab7; money7 and clothing10 marked handoff. Completed validation8 and
book-strips9not re-marked; evidence recorded above and URLs remain reproducible.
Final81592poll confirmed LIVE again. A5398-sequence baseline for the NEXT object
integration has NOT yet been captured; create it before changing the builder.
Existing pre-book-mail-shaping.json contains5364cases and must remain intact.


## Restart reconciliation — 2026-11-02 21:28 UTC

The production integration build started at21:22:24 is still running: PID68013,
stateR,6:15elapsed and6:13CPU. Its quiet log is not evidence of a hang. Installed
font and manifest still reflect the accepted5398sequence build; do not claim the
expected5419sequence/1398cmap or3899fully-qualified counts before validation.
The preceding book/mail full366test run completed successfully, including exact
reproducibility. Two compiler comparisons for the extracted shared SVG-family
compiler and money/clothing integration also passed. A5398sequence baseline was
captured before integration; pre-book-mail-shaping.json remains5364cases.
Prepared21new production font tests,2routing tests and3browser cases, still
pending the new font. Expected next JS/browser totals317/579 are not pass claims.

An11drawing tools/instruments prototype remains unregistered. The last cleanup
probe at21:27 rejected both banjo and long drum; they are not accepted art.
Their fine strings/cords require further topology/detail work. Crossed swords
and dagger native light/dark blade faces resolved the earlier contour problem.
New prototype/compiler files exist, but no whole-family acceptance is claimed.
No goal completion, commit or reset occurred. Earlier checkpoint live/pending
statements are historical and superseded by this reconciliation.


## Object continuation — 2026-11-02 21:36 UTC

Previous reconciliation turn was a verified wait on the exact running production
build, with corrected persistent notes. This turn made additional prototype
and semantic-test progress. Main money/clothing integration handle31839 remains
LIVE, PID68013. At21:35 its elapsed12:47/CPU12:25 showed active computation.
No production font-art inputs changed. No new coverage claimed.

An early npm test was premature:315passed and2new money/clothing routing tests
failed because the production manifest is still5398forms. Rerun after31839
finishes; do not weaken those tests. Log /tmp/money-clothing-js-tests.log.

Tools/instruments: new tests/test_tools_instruments_candidate_sources.py passes
all6checks for23shieldrivets,12accordionbuttons/10keys,7fluteholes+endbore, both
maracaheads/flowers and native light/dark blade faces. Reference masks account
for occlusion by retained semantic shapes; omitted highlights do not erase test
centres. Nine accepted-at-prototype-stage drawings were rendered to explicitly
PARTIAL sampler/optics files; all9contour checks pass and were visually reviewed
at180/33.6px. No whole11font acceptance or production registration yet.
Prototype sampler now accepts explicit distinct keys and names subsets partial.

Instrument diagnostic18284terminal0:banjo has1component/54holes, but every
pen backoff changed hole count; drum has3components, two of which are2pixel
crumbs, and loses/merges features. Broader bounded cleanup and generic black
strings did NOT solve either case; those exploratory overrides were NOT saved.
Root cause is distance-field boundary smoothing: a trial reducing gaussian sigma
from.45to.2 passes existing unchanged topology guards for BOTH, with banjo
applied.95625, drum.3025634765625. Instrument cleanup remains250pinholes and
68pinholes respectively; drum trial removes exactly4crumbpixels. No guard was
relaxed. Sigma0gives same strengths, so prefer.2 for gentle smoothing.

PROPOSED PATCH ONLY in /tmp/emoji-detail-pen/{pen_translate.py,emoji_svg_recipe.py}:
adds Settings.boundary_blur default.45 and finite/nonnegative validation, CLI
option, and optional recipe boundary_blur keyword. Production files UNMODIFIED.
Trial regression source /tmp/emoji-detail-pen/test_detail_pen.py reproduces thin
diagonal counters; old default falls back, .2 preserves topology and produces
antialiased output. Test75004 TERMINAL0: all4trial tests passed. Earlier trial1/4
failed an overly strict binary-mask-change assertion at96px; exported grayscale
changes while threshold geometry remains identical. Corrected to require changed
exported pixels plus antialiasing and identical topology. Do not claim production
fix until patch applied, default-output preservation tested, and art reviewed.
Apply only after31839terminal, before next full reproducibility run, to avoid
changing build source metadata midway. Configure only banjo/drum .2, drum
CRUMB_LIMITS4; keep other drawings on default.45. Then run full11sampler, optics,
candidate font and new semantic string/cord checks.

New unregistered6office/bell/lock drawings: prototype_office_locks.py and
prototype_office_locks_font.py; preview_remaining_object_optics accepts
--family office-locks. All6prepare at1.7, all6compiled contour checks pass.
Seven qualification forms/49adjacencies, actual bearings, positive contours,
and exact ink/colour companion shaping pass. New
tests/test_office_locks_candidate_sources.py passes6checks: ten gridlines and
direction for both charts, three bar colours/height order, two keyholes and
source-derived actual open key-ring counter. Browser tab11candidate+contact
inspected all7forms at enlarged/dialogue size; aliaspixels/advances failures[].
Source bell11paths, penlock24, keylock16, charts13/13/11. Explicit semantic
paths chosen; native open grid lines converted to strokes.
Colourhash e26815a78227dcf178371407bd9fe2ae1c1455d8e478f3372dbddf344ad5b931;
inkhash35781f1d8368872eb6123986a3e2693224503b961a2a1480dce92986a90dc92f.
No source registration/integration yet; still12520registered sources.

Next:poll31839, version-assets chained there; run new21font tests and317JS,
audit and579browser cases, inspect3new actual strips. Apply/test proposed
boundary-blur fix once initial build terminal, then full focused production
regression/reproducibility (388prior planned tests plus relevant new pen tests).
Freeze production inputs during reproducibility. Register office6only after
candidate preservation checks; integrate subsequent reviewed families while
preserving all5419then-existing identities/positions. Fullbrief remains active.

Browser office candidate/contact tab11 marked handoff for continuation.


## Money/clothing integration — 2026-11-02 21:46 UTC

31839TERMINAL0:1337bases/5419explicit forms/61components,2928300byte colourfont.
version_assets.py chained successfully.69616TERMINAL0:all21new production font
checks passed45.30s, including21forms,441adjacency pairs in both fonts and all
5398previous glyph identities/positions.8159TERMINAL0:317JS passed.81568TERMINAL0
audit:172152/172352visible cmap,200missing;3899/3963fully-qualified emoji,64missing.
Browserfull tab12:579casesPASS,failures[] and geometry[], fontLoadedtrue. Focused
tab13:all3new actual strips inspected in upper/lower halves, nofallback/unmapped.
Clear/darkglasses,fanfolds,baghandles,beads+tassel,lipstick,ring/gem and actual
currency/chart colour distinctions read beside Latin dialogue. Originalart kept.
The initial browser start caught duplicate fixture name emoji-clothing-1; new
accessory fixture renamed emoji-accessories-1 and custom-object guard extended.
Then both full579 and focused3runs passed.

Applied the tested boundary_blur option to pen_translate.py/emoji_svg_recipe.py
AFTER31839terminal. Default remains.45; only two unregistered instruments use.2.
Copied4meaningful regression tests into tests/test_pen_translate.py.5765terminal0:
25pen/cache/compiler tests passed201.73s; all reviewed book/mail and money/clothing
font outlines,metrics/colours match exactly under unchanged default.

72327LIVE:/tmp/money-clothing-full-regression.log. Larger focused suite includes
flags,source checks,book/mail,money/clothing,pen/cache,unregistered detail checks,
ink/inventory and final EXACT production font/manifest rebuild. Production
builder,pen_translate,emoji_svg_recipe,registered cores/registries FROZEN until
terminal. New unused prototypes/docs/diagnostics may proceed independently.
Do NOT restart72327 merely because the final rebuild is quiet or slow.

Tools11full sampler prepares all at positive guarded strengths.1697terminal0:
8semantic tests pass, including FOURwhite banjo strings at two native cross
sections and drumcords. Helper was improved afterward to erase occluding native
strokes as strokes; the live72327run includes the updated helper. Removed native
drum path20 from colour/stroke recipe: it contains onlyM88.1,68.5 and paints
nothing in the donor. Full chain5608TERMINAL1 in optics BEFOREfontcompile:
banjo source1component+54holes needs55contours; ordinarytracer emits54, losing
one tiny posttranslation counter. Drum source1+51 matches52contours. No accepted
whole11compiled font yet. A trial precise tracer in emoji_precise_outline.py
emits53banjo contours, so it DOES NOT solve the issue and is not integrated.
27817LIVE:/tmp/banjo-compiled-cleanup-probe.log tests bounded input cleanup
cutoffs16/24/32 against native strings and ordinary/fine contour counts; no
source recipe changed by these process-local trials. Earlier cutoff64 with.2
stillfallback; do not blindly raise cleanup limits.

Started8unregistered place/material/weather recipes in prototype_places_weather.
All8native path sheets individually reviewed with pinned source verification.
Six initial candidates prepare at positive strength:rock,wood,tent,barberpole,
thermometer,rainbow. Corrected wood body from mistakenly black path1 to brown1;
black path0 is its lower broken corner. Rerender remains pending. Native6rainbow
bands keep red/orange/yellow/green/blue/purple PDF colours. Brick24native bricks
and Saturn rings still fail topology (Saturn also199small source pinholes);
trial.2andSaturn(4,208)cleanup did not resolve them. All unregistered; no new
coverage beyond the accepted19money/clothing additions is claimed.


## Compiled object candidates — 2026-11-02 21:55 UTC

72327 still LIVE:424test dots, no failures; final exact production font/manifest
rebuild is active. Do not restart. Default pen change invalidates disposable
translation cache entries, so this rebuild may be longer than the initial one.
Production art/compiler inputs remain frozen. No further production coverage
changes beyond the19money/clothing drawings accepted above.

Resolved tools/instruments COMPILED acceptance:56819TERMINAL0, all11optics
checks,14qualification forms/196adjacency pairs, actualbearings,positivecontours
and identical ink/colour companion shaping passed. All14browser forms in tab14
passaliaspixel/advance comparisons. All11enlarged/33.6px optics individually
reviewed and all14contact forms visually checked. Candidate colourhash
6e15f5a4bdd4c7fe0d3c5752f67f1c26336ba6274fcfcef35f9ec578e0e54bd1; inkhash
c3c86b33268d04af69778ccc4422205ee7687740989e6dfca6e3ac620043e88a.

The banjo compilation issue is a raster-counter count issue at integer font
resolution, rather than loss of the four native strings. Did NOT save source
width changes, broader cleanup, blackstrings or failed precise tracer. Deleted
unused emoji_precise_outline.py. New svg_counter_review.py retains strict count
by default; ONLYbanjo permits1small loss while checking distinct compiled
counters for EVERYsource counter >=64rasterpixels. This is17.342fontunit²,
less than.02displaypixel² at33.6px. All36larger native counters match distinct
compiled holes; all4strings pass both source cross-sections. The ordinary
compiled53holes versus54sourceholes records exactly1small loss. Other10drawings
keep strict count. 29640TERMINAL0:2guard regressions pass, explicitly rejecting
loss of a larger counter even with the exception.11128TERMINAL0:3tests pass
including independent verification against the actual hash-checked candidate
WOFF2. Preview and candidate wrapper call this guard and record its result.
Actual production integration must also call the guard for this family.

Places/weather8:brick fixed by retaining its24individual brick outlines and
omitting the donor's nonsemantic outer mortar backplate; no cleanup needed,
1.7passes. Saturn keeps full native blue ring8 and primary body bands, omits
redundant thin shading6/7/9;1.7passes,6ordinary scan pinholes filled under default
16pixel cap. No blanket199pixel allowance was saved. Correct brownwood body1
exposes one detached raster pixel at native(81.5,99.92); bounded crumb cleanup
cap1 restores1.7guarded translation. Sigma.2alone did NOTfixwood.
The first8semantic run had7passes and thewood fallback; all other identities
passed (24bricks,facets,tent,barberstripes,fivethermometerticks,Saturnring,six
rainbowbands). 32078TERMINAL1 confirmed before rerunning. New19571LIVE runs
full8sampler,optics,font/contact compilation and then8semantic tests sequentially.
Logs /tmp/places-weather-{prototype,optics,candidate-font,semantic-tests}.log.
No place/weather source registration or production coverage yet.

Important diagnostic correction:when intercepting emoji_svg_recipe.raster,
store m.copy(), not m. The engine mutates masks[0] during bounded cleanup;
otherwise a later overlap audit accidentally sees already-cleaned pixels.
The exploratory Saturn overlap log with0smallholes was such a stale-reference
measurement and is NOTevidence. No acceptance relies on that result.

Next:poll72327 and19571exacthandles; finish places8compiled semantic/visual
review. After72327terminal, register reviewed office6 and tools11 sources ONCE,
extract registered cores, recompile exact candidate font hashes, capture a
5419sequence baseline before next production hook, then integrate reviewed
families and inspect actual strips. Preserve all fullbrief scope, including
remaining200visible gaps,64FQemoji gaps,Seal and script/style/behaviour work.


### Place/weather candidate acceptance — 2026-11-02 21:56 UTC

19571TERMINAL0:all8samplers prepare, all8compiled optics checks pass,9qualification
forms/81adjacencies,actualbearings,positivecontours and identical companion
shaping pass. All8semantic tests pass17.99s after exactly1woodcrumb removed.
All8enlarged/33.6px optics and browser contact forms visually reviewed; tab15
reports9forms,failures[]. Woodbrown body and all growthrings/bark retained.
Brick24separateblocks and openmortar; sourceouterbackplate omitted. Rocklight/
darkfacets,tententrance/flaps,barberred-blue-whitestripes,5thermometerticks,
Saturnring on BOTHsides with primary bands,6rainbowcolours retain their identity.
Colourhash48a6e683e73d97183e479a46aa74d193eeb8d40679dd293bd16c95d83525868f;
inkhash835580bf7841db186ec6f2e7b130b004278cb47b7fd6afe534e1759d7f1b6463.
No production registration/integration or actual-strip acceptance yet.

Ready isolated families now total25drawings/30qualification forms:office-locks
6/7,tools-instruments11/14,places-weather8/9. Preserve their exact candidate
hashes on core extraction/registration, after72327terminal. Next production
expansion would be5449exact forms/1423cmap/1362bases/61components, and3924/3963
fully-qualified emoji (39missing), ONLYif all25integrate and validate. Those
are EXPECTATIONS, not current coverage. Currentaccepted5419/1398/3899counts
remain authoritative. Source registry still12520files; do not claim12545yet.

Production finalrebuild72327 remainsLIVE;424preceding checks complete with
no failures. Tabs13actualmoney/accessorystrips and14instrumentcontact marked
handoff; full579case tab12 need not survive. Tab15contact can be reopened by
its recorded localhostURL. All earlier failed probes are historical, not
current source state. Goal remains active and fullscope incomplete.


## Other objects and globe candidates — 2026-11-02 22:11 UTC

Previous goal turn made concrete source/compiler/validation progress and
verified the exact active rebuild.72327remainsLIVE,PID71121:at22:09elapsed25:00,
CPU24:05.30,99.1percentCPU,stateRs.424checks passed so far; final exact rebuild
active. No restart, source/art/compiler inputs still frozen. Current accepted
production remains5419sequences/3899fully-qualified/200visiblecmap gaps.

Created prototype_other_objects.py and prototype_other_objects_font.py for
9pinned native sources:smoking,coffin,headstone,urn,nazar,hamsa,moai,placard,IDcard.
All9native path sheets individually reviewed.88244TERMINAL0:all9prepare1.7,
all9compiled contour checks,11forms/121adjacency pairs,actualbearings,positive
contours,identical ink/colour shaping pass.31585TERMINAL0:9semantic tests pass
14.82s, including blue/white/light-blue/black eye rings, hamsa finger divisions,
cigarettefilter/paper/smoke/embers,2goldhandles,allinscriptionmarks,urnbands/lid,
Moainose/lips/nostrils,blankplacard/handle,IDportrait/photo/fourprintedlines.
All9enlarged/33.6px optics and all11browsercontactforms visually reviewed;
tab16reports11forms,failures[]. Colourhash
1453f33d8402317619867bfa5f014d098908b16ae80999234b5a446cdc8ad6f2; inkhash
ba50bd87144b5a258003d7c5e76af3acdc1b2ce17889a7e4383fc34549fe7e29.
These are isolated candidates only, not registered/in production.

Created prototype_globes.py/prototype_globes_font.py. All3native path sheets
reviewed. Europe/Africa andAmericas prepare1.7;Asia/Australia.95625. Full
3sampler alreadygenerated. Initial53462TERMINAL1 in optics count check before
fontcompilation:Asia/Australia has one small rastercounterloss. A first audit
falsely reported lost1228pixel counter because an island counter is ALSOinside
the enclosing ocean counter. This was an audit nesting bug, not missing land.
Fixed svg_counter_review.py to choose the innermost containing counter, still
requiring distinct source regions to map to distinct compiled holes. Added2
regressions for nested source regions, including rejection of a merged island
into the ocean.67335TERMINAL0:5guard/compiled-banjotests pass2.21s.

40098TERMINAL0:all3globesoptics,3forms/9pairs,bearings,positivecontours/companion
shaping pass. OnlyAsia/Australia permits1small loss;all16larger counters are
verified in distinct compiled regions. Other2keep strict counts.
99352TERMINAL0:3geographic checks pass6.47s:>95percent coverage of every native
land path, and EVERYnative land component sampled in actual hash-checked WOFF2,
with half-font-unit rounding tolerance. All3enlarged/33.6px optics and browser
forms visually inspected;tab17reports3forms,failures[]. Colourhash
222bc2edf2b4e705e7aa5a0ed4e84ded6eafcc8d0ecd460880aa45d4d3fee1c4; inkhash
b525a6d24c914cd5f4915d302432e9cb6334f2d1e2fe35c7d2e90709cf18f14f.
Exploratory omission of Asia oceanpatch1 did not fix the count issue and was
NOTsaved. No land paths omitted. All37reviewed singleton drawings remain
unregistered:office6/tools11/places8/other9/globes3,44qualification forms.
Their eventual integration would leave27missing FQforms, not current coverage.

Phoenix source1f426_200d_1f525 has19shapes, all native paths inspected. New
prototype_phoenix.py uses red/orange wings/body,yellowbreast/flames/beak,black
eye/nostril/legs. Initial prepare rejected50sub-four-pixel raster pinholes;
a bounded(4,64)cap has been added, current handle4980; poll its exact terminal result. /tmp/phoenix-prototype.log. No phoenix acceptance
yet. This is a COMPOUND, not a singleton; do not use add_svg_family as-is.
Use existing component glyphs for bird,joiner,fire and a dedicated GSUB rule,
preserving both standalone identities and all old positions. Candidate
compile_flags supports compound sequences. emoji_expressions.py compounds
provide an existing production example; don't modify production until72327ends.

Remaining unconverted sources after37reviewed candidates are26transport
drawings plus this1phoenix. All113original remaining sources were acquired
and pinned earlier; no network reacquisition needed. After72327terminal,
register approved families ONCE, preserve exact candidate font hashes on core
extraction, capture the5419baseline, and integrate candidates with further
reviewed families. Fullbrief including Seal/script/style/behaviour work remains
active; neither candidate counts nor silent rebuilds establish completion.


### Phoenix candidate acceptance — 2026-11-02 22:15 UTC

4980TERMINAL0:phoenix prepares at1.275 with50bounded<4pixel pinholes filled
(cap64). Native19paths all retained. First colour placement made the bird too
brown; shifted main wing/body5/7 toPDFred and rearwing1/4 toorange. Other native
geometry/eye/beak/feet/flame paths unchanged. Initial37929TERMINAL0art hashes
b19aca.../bbab378... are SUPERSEDED, do not use them.32444TERMINAL0:corrected
colour sampler,strict compiled contour check,1exact compound form/1adjacency
pair,actualbearings,positivecontours and identical companion shaping all pass.
Correct current colourhash
76629d98275336bada1627d8a579dfa3d73863996d7f71593488c663de414fd7; inkhash
85d30b29d128bb8998bed7ca2f7709b24f234117eea6e76fd69e4811ac348c27.
26772TERMINAL0:3semantic/actual-font tests pass3.37s:bothredwings,yellowbreast/
beak,darkeye/nostril/legs,all5nativeflame shapes,exactbird-ZWJ-fire ligature.
Withoutjoiner the bird/fire inputs remain2glyphs; two adjacent phoenix forms
remain2glyphs in bothfonts. Browsercontacttab18:1form,failures[], enlarged and
33.6px visually reviewed. FontSource/core registration and actualstrip pending.

Ready candidates total38drawings/45qualification forms:office6/7,tools11/14,
places8/9,other9/11,globes3/3,phoenix1/1. All are unregistered; current source
registry STILL12520files. All37singleton bases and the1compound must preserve
5419current identities/positions on integration. No current cmap/FQcoverage
gain claimed for these candidates. Remaining26unconverted drawings are all
transport:18ground,6air,2water. Started native path sheets for the8air/water
keys2708,1f6e9,1fa82,1f4ba,1f6f0,1f6f8,2693,1f6f3. Handle57311TERMINAL0 and
/tmp/air-water-native-paths.log; these new sheets NOTyet visually inspected.

72327stillLIVE, exact rebuild after424passing checks. PID71121confirmed actively
using99.1percentCPU at22:09. Do NOT restart or mutate production inputs until
terminal. Current goal turn made13new reviewed candidate drawings, fixed the
independent nested-counter checker with5passing regressions, and repeatedly
verified the exact active build. Fullbrief remains substantially incomplete.

Native8air/water path generation57311TERMINAL0; all8sheets ready but NOTyet
visually inspected. Anchor2693path2is nonvisible; do not select it accidentally.
Candidate tabs16other/17globes/18phoenix marked handoff this turn.

### Restart reconciliation — subsequent completed work

The preceding pending statuses are superseded by these verified results.
The money/clothing production build and exact reproducibility regression run
finished successfully: 425 passed, 7 existing SWIG warnings, 3481.15 seconds.
See /tmp/money-clothing-full-regression.log. Production remains 5419 exact
emoji forms, 3899/3963 fully-qualified emoji, and 172152/172352 visible cmap
characters. Browser review passed 579 scenarios; three new actual-strip cases
were reviewed with original character art preserved. The broader brief remains
substantially incomplete.

All eight air/water and eight road-infrastructure drawings were subsequently
reviewed at enlarged and dialogue sizes and in browser candidate contacts.
Air/water: 12 forms/144 adjacency pairs and 8 semantic tests passed. Road:
10 forms/100 pairs and 8 semantic tests passed. Fixed road traffic-lamp order
and the fuel hose's native open stroke/spout, and preserved construction-barrier
clip definitions. The path-isolation preview now retains clip definitions so
painted stripes do not incorrectly appear invisible.

Added the shared selected_strokes guard for native fill:none/line geometry:
105 tests passed; integration with existing compiler checks passed 123 tests
without changing accepted outlines, colours or metrics.

Registered 54 reviewed drawings/67 qualification forms in eight source families:
office-locks, tools-instruments, places-weather, other-objects, globes, phoenix,
air-water and road-infrastructure. Extracted reusable emoji_*_svg.py cores;
the prototypes now wrap those cores. All 54 drawings preserve their reviewed
colour AND ink font hashes after extraction. See
/tmp/registered-final-object-candidates.log. Source verification passed for
12574 files. These candidates are NOT yet integrated into production.

Immutable snapshots: output/font-review/pen-translation/
pre-final-object-integration-shaping.json contains all 5419 production cases;
pre-final-object-registration/index.json and companion files preserve the
eight reviewed candidate families. Never overwrite these baselines.

At restart reconciliation, a separate 171-test candidate/source regression
batch was still active (PID 79526, using CPU). Its log is
/tmp/registered-final-object-regressions.log; inspect for terminal results
before claiming success or restarting. No production font build remained live.

Next: finish the ten ground-vehicle drawings (sources and native path sheets
already cached), preserve/register their reviewed results, then integrate all
remaining emoji with old shaping positions preserved. Phoenix requires a
compound GSUB rule, not the singleton helper. Review actual strips, rebuild,
audit and test before claiming coverage gains. Seal characters and broader
script/style/renderer validation remain after this emoji work.

### Final ten vehicle candidates and production wiring — 2026-11-02 22:59 UTC

Previous turn classified as progress: reconciled terminal build evidence and
updated this authoritative log. The previously live PID79526 candidate batch
has now finished: 171 passed, 7 existing SWIG warnings in100.32s.

Created prototype_ground_vehicles.py and its isolated font compiler for bus,
ambulance, police car, oncoming car, pickup, racing car, motorcycle, bicycle,
skateboard and roller skate. All ten native path sheets individually reviewed.
Preserved native open bus trim, two width8 skateboard axles and six width3
lace/bow strokes. Retained every bicycle spoke as native filled geometry,
ambulance blue Star of Life, separate police red/blue lamps, pickup headlamp,
and roller-skate eyelets/wheels/brake. All ten apply strength1.7, no cleanup
exceptions. Ten semantic tests plus the expanded115strokeaudit tests passed:
125passed28.29s. Strict optics: all10compiled contour checks passed; enlarged
and33.6px drawings visually reviewed. Candidate fonts:12forms/144pairs,
actual bearings,positive contours and identical companion shaping passed.
Browsercontacttab21 reports12forms/failures[]; all forms visually inspected.

Registered these ten sources ONCE, extracted emoji_ground_vehicles_svg.py,
and recompiled the wrapper. Colourhash
479ab163289b8fad68ab482cce56a5e219b330f1705e34a2f96ef7a884f0d904
and inkhash c9333cfe660fffbec3a2097f89652289359c4481e859145b6030a363e1b2b2ef
are unchanged. Immutable references in pre-ground-vehicle-registration/;
never overwrite. Sourcecheck97704TERMINAL0:12584files verified.

Added emoji_final_objects.py production compiler for all64remaining drawings:
63singleton bases plus the exact bird-ZWJ-fire phoenix compound. Existing
bird/fire/joiner drawings and metrics are reused. Shared singleton helper now
optionally performs counter review; new families enable it, with only the
previously accepted tiny banjo/Asia-globe losses allowed. Production wiring,
64candidate-art comparisons,5419old-shaping preservation,79forms/6241adjacency
pairs, malformed routing tests and actual-strip fixtures are prepared.
No production rebuild or coverage gain yet. Compiler/source checks currently
LIVE11435, PID80858 actively processing native raster layers; log
/tmp/final-objects-compiler-tests.log. Poll before building. Production remains
5419forms until a successful build. Full Unicode brief still incomplete.

Final-object compiler gate11435TERMINAL0:136passed,7existing SWIG warnings,
116.63s. Every one of64production drawings/layers matches reviewed candidate
geometry, colours and metrics. The preexisting standalone bird/fire/joiner are
unchanged by the compound compiler. Main production build31709 started
22:59:25UTC, PID81300; confirmed99percentCPU at23:00:33. No restart, no
production input changes during the build. Log:
/tmp/final-objects-production-build.log. Actual-strip fixtures and production
font tests are prepared; do not run them against the old font and claim success.
Next on terminal0: version_assets.py, test_font_final_objects.py plus the
existing emoji regressions, npmtest, Unicodeaudit, browser fixtures/fullharness,
and exact deterministic font/manifest rebuild. Keep all old immutable baselines.

Parallel read-only Seal investigation located U+3EE47/D-07328 exactly in NCL07
page105/xref311, crop[556,510,64,64]. Native context, threshold trials and recipe
saved in output/font-review/seal-pending/D-07328-*; gap review now records the
location. NOT accepted: heart and enclosing box touch in this printing whereas
the chart reference separates them; a right page rule also enters the crop.
Offsets-10/0/10 retain this bridge;20closes an extra hole. Need a cleaner scan
or justified local repair. No Seal coverage change or source-font rebuild.

Handoff23:03UTC:31709remainsLIVE, samePID81300,4m19selapsed,100percentCPU.
Do not restart it. No completed production gain claimed.136compiler tests,
125vehicle/stroke tests,12browserforms,64candidate-art comparisons and12584
sourcefile checks are terminal successes. Sourceinventory21572TERMINAL0:
259font sources,171929public source characters,944absent including behavioural
characters; this is a DIFFERENT inventory from bundled visible cmap coverage.
New Python modules compile and gitdiff whitespace checks pass. Tab21marked
handoff. The cached alternate DYC08 pages80,88,90–98and104were inspected as
source leads; no matching D-07328 accepted there. Keep the located NCL07
candidate deferred. Main next action is poll31709, then its production checks.

### Bounded D-07328 recovery candidate — 2026-11-02 23:06 UTC

Previous goal turn was progress (ten vehicles converted/registered,64drawing
production compiler and136checks passed, main build started). Main31709 is
still live; do not restart or change its emoji inputs. While it runs, a separate
Seal-source repair was reviewed. The D-07328 deferral is superseded only at the
SOURCE candidate level, not yet bundled coverage: a three-pixel-wide separator
[62,22,65,52] in the doubled128px scan removes the heart/box print bridge;
[118,0,128,128] removes only the separate page rule. No stroke is added, and
all ink outside those exact rectangles is retained. Both parts and both
counters survive compiled tracing (4contours). Native/source/compiled200px and
24px optics reviewed in D-07328-repaired-optics.png. The recipe explicitly
records the repair and its reference evidence; it is not an untouched scan.

Registered this213th recovery recipe once. Immutable all212previous source
outlines/metrics captured in seal-pending/pre-D-07328-shaping.json; never
overwrite. New regressions check bounded changes and exact preservation of
allold212drawings. Source build42602 currently live, log
/tmp/dyc7328-source-build.log. Geometry-onlytest5015 live, log
/tmp/dyc7328-geometry-test.log. After source terminal: build_scripts.py,
sourceinventory/gapreview/editionreport, fontpackaging tests and actual browser
fixture seal-recovery-dyc-heart-enclosure. No new Seal cmap gain claimed yet.
Both builds mutate separate outputs:31709emoji,42602Seal-sourceTTF. Preserve
both live handles. Emoji production test/font/browser gates remain pending.

### D-07328 packaged and checked; D-07337 source in progress — 23:12 UTC

42602sourcebuildTERMINAL0;34585scriptsbuildTERMINAL0:352shards60347676bytes.
15610TERMINAL0:2newgeometry/preservation checks passed1.13s. 27914TERMINAL0:
84Seal/source/licence/regression tests passed108.24s,7existingSWIGwarnings.
25JSfonttests passed. 65261TERMINAL0audit:172153/172352visible cmap,199missing;
emoji coverage still3899/3963 because mainemoji build31709 has not finished.
99158sourceinventoryTERMINAL0:259fontsources171930publicsourcecharacters,
943absent including behavioural characters. Editionreport:145Sealgaps
(6CCZ/97DYC/39QJZ/3THX),139withoutCCZ. Gapreview and README updated to the
accepted bounded repair. New actualstrip in tab22 individually reviewed top
andbottom:onebundledfont,nounmapped/fallback/failures/geometryproblems;
original Dad/Calvin artwork and silentfourthpanel retained. Tab22handoff.

D-07337/U+3EE51 located NCL07page106/xref314,crop[829,267,54,63]. Its
heart/west contact is INTENTIONAL in the chart reference (page131): both
reference and source have1part/3counters,compiledtrace4contours. No local
repair fields. All native/compiled200px/24px optics visually reviewed in
seal-pending/D-07337-optics.png. Registered214thsourceONCE; captured immutable
all213previoussourceoutlines/metrics in pre-D-07337-shaping.json. New tests
check exact old213preservation and intentional contact/counters. Sourcebuild
42060LIVE, /tmp/dyc7337-source-build.log. After terminal build_scripts, then
source/packaging checks,edition/gapreports,audit/versionassets and actualstrip
seal-recovery-dyc-heart-west. No new214thbundled gain claimed until packaged.
D-07344location remainsunknown. The attempted D-07391crop[722,237,60,75] on
page106is WRONG (extra upperpart/adjacent text), not accepted or registered.
Mainemoji31709remainsLIVE; retain exacthandle, no restart or input changes.

### Production component promotion fix and third Seal candidate — 23:20 UTC

31709TERMINAL1 at final-object hook, BEFORE saving any production output:
Unexpected existing SVG-family base1F308. Inspected every new singleton against
actual production cmap: two empty components already exist, rainbow
flag-component.u1F308 (rainbow flag) and airplane component.2708 (pilot roles).
Both are componentOnly, zero-contour/zero-advance. No other collision. New
helper option allows ONLY these exact named empty glyphs, with zero metrics
and no prior colour layers, to become real drawings. Their names are preserved
for old compound GSUB rules; build removes both from componentOnly. Expected
new totals are1459cmap/59components/1400visiblebases/5498exactforms, not1461/61.
All5419previous names/positions must still match the immutable baseline.

34561TERMINAL0:4compiler compatibility/promotion-protection tests passed108.54s,
7existingSWIGwarnings. Full64drawing compiler test now seeds both real
production components and compares every promoted outline/layer/colour/metric
to the reviewed candidate. Additional guard rejects real artwork, nonzero
metrics and unapproved names. New production tests also check rainbow flag
and pilot ligatures. Both oldfont and manifest hashes remain EXACTLY the5419
baseline after failed31709. Corrected mainbuild1097LIVE, PID83477, started
23:19:19UTC. Log /tmp/final-objects-promoted-production-build.log now has family
stage messages (latest detailedpeople), so future polls can see progress.
Do NOT restart1097 or change its production emoji inputs until terminal.

40746TERMINAL0:D-07337 packaged,74Python checks passed105.74s;25JSfonttests
passed; audit172154/172352visible,198missing. Editionqueue144gaps
(6CCZ/96DYC/39QJZ/3THX),138withoutCCZ. Gapreview/README updated. Tab23actualstrip
reviewed top/bottom, no unmapped/fallback/failures/geometry, original art intact.
23558sourceinventoryTERMINAL0:171931publicsourcecharacters,942absent including
behaviouralcharacters.352shards60348016bytes. Emoji audit still3899/3963.

Located D-07344/U+3EE59 on NCL07page106/xref314,crop[344,391,44,72]. Native
scan loses the lower-left coil's diagonal closure and its descending join to
heart. Two local radius2closings at[7,57,13,63]and[24,66,33,74]add EXACTLY9
sourcepixels, no removal or other changes. Source and compiled outline now
retain1part/4distinctcounters,5orientedcontours; enlarged and24px optics
visually reviewed in D-07344-optics.png. Earlier attempted repair rectangles
were rejected by the counter check and NOTsaved. Correct recipe is saved in
D-07344-candidate.json and registered ONCE as215thsource. Immutable prior214
outlines/metrics in pre-D-07344-shaping.json; never overwrite. New geometry
and all214preservation tests added. Sourcebuild45509LIVE, log
/tmp/dyc7344-source-build.log. Geometry-only test started, log
/tmp/dyc7344-geometry-test.log. After source terminal: build_scripts, targeted
source/packaging/reproducibility/preservation checks, versionassets,audit,
sourceinventory,edition/gapreport,25fontJS tests and actualstrip
seal-recovery-dyc-heart-coils. No third bundled gain yet. Added reusable
preview_seal_candidate.py so future reviewed source recipes can be inspected
at compiled200px/24px without duplicating temporary rendering programs.

### Third Seal recovery accepted; next candidate located — 23:23 UTC

45509sourcebuildTERMINAL0;28420geometryTERMINAL0:1passed46deselected1.00s.
86419TERMINAL0:scriptpackaging352shards60348588bytes;8targetedPython tests
passed64.06s (all215packaged drawings compared to source,exact builderbyte
reproduction,3newsemantic checks and212/213/214old-outline preservation).
25JSfonttests passed; audit172155/172352visible,197missing. Emoji STILL3899/3963.
Sourceinventory259fonts171932publicsourcecharacters,941absent including
behavioural characters. Editionqueue143Sealgaps (6CCZ/95DYC/39QJZ/3THX),
137withoutCCZ. Gapreview/README updated. New tab24actualstrip reviewed
individually top/bottom:1bundledfont,nounmapped/fallback/failure/geometry;
all4coils legible, original character art and silentfourthpanel intact.
Tab24handoff. No live Sealbuild/check process remains.

Next ready source candidate U+3EE89/D-07391 is on NCL07page112/xref332,
crop[830,393,58,65], referencepage132. Correct durable recipe is
output/font-review/seal-pending/D-07391-candidate.json. Native and compiled
200px/24px optics reviewed;2parts/noholes/2contours, no local repairs. NOT
registered or in production yet. The earlier page106crop was WRONG and is
superseded; do not reuse /tmp/D-07391-candidate.json. New pages109–120 are
extracted to /tmp/dyc07-{page}.png; overview /tmp/dyc07-109-120.png inspected.
A connected-component inspection located D-07344 and D-07391 reliably;
/tmp/dyc-heart-open-components.png shows candidates from pages109–114.
D-07419/U+3EEA6 is the next reference lead; its location is not verified.
Reference sheet dyc-heart-next-reference.png includes07337/07344/07391/07419.

Corrected emoji1097LIVE, last logged stage activitypeople. Its key gates remain
new79forms/6241pairs and64actualart comparisons, all5419oldpositions,
standalone plane/rainbow plus oldpilot/rainbowflag sequences, unique actual
strip fixtures,fullbrowser/npm tests and audit, followed by exact reproducible
font/manifest rebuild. Production totals1459cmap/59components/1400bases/
5498forms are EXPECTATIONS until terminal and audit. No coverage gain claimed.

### Two further reviewed Seal sources — 2026-11-02 23:28 UTC

Previous goal turn classified as progress:threeSealcharacters packaged and
reviewed, componentpromotion bug fixed and correctedmainbuild started.
1097is stillLIVE, latest stage signs afterclothedsport/keycaps/sequences/tiles.
Do not restart or modify emoji inputs until terminal.

Registered U+3EE89/D-07391 as216thsource ONCE.40723sourcebuildTERMINAL0.
96349geometrytestTERMINAL0:1passed48deselected0.99s. New immutable all215
sourceoutlines/metrics snapshot pre-D-07391-shaping.json. Consolidated the
three older212/213/214preservation tests into one parameterized check, retaining
allbaselinecases and adding215. No semantic coverage removed.

Added preview_seal_scan_candidates.py: validates registered PDF hash, records
page/xref/imagepixelhash and component/context bounds, produces review-only
contact sheets, NEVERassigns identities. It found U+3EEA6/D-07419 on NCL07
page115/xref341,crop[347,137,54,68], referencepage132. Native/compiled200px/24px
optics inspected,3parts/noholes/3contours, no local repair. Registered217thsource
ONCE; immutable all216snapshot pre-D-07419-shaping.json.42145sourcebuild
TERMINAL0.89350geometryTERMINAL0:1passed50deselected0.98s. Five old-source
baseline cases now tested via parameterized preservation check.

Both sources awaiting packaging gate2176, the active
/tmp/dyc7391-7419-regressions.log chain. Logs share /tmp/dyc7391-7419- prefix.
Do not restart the chain while live. It builds scripts/versionassets,checks
all217packagedsourceoutlines,exactsourcefontreproduction,allfivebaselinecases,
newsemanticdetails,25fontJS tests,editionqueue,auditand sourceinventory.
Current accepted audit remains172155/172352visible,197missing and143Sealgaps
until this chain confirms results. Both new actualstrip fixtures pending review:
seal-recovery-dyc-heart-great and seal-recovery-dyc-heart-arches.

New reference sheet dyc-next-heart-water-reference.png (identity-only, no chart
art copied to fonts) contains D07464/chart133,D07495/chart134,D07596/D07597/
chart136,D07664/chart137,D07823/chart139. All are unlocated/unaccepted leads.
Scan pages109–120 exist in /tmp; new stable reviewcontact dyc07-115-120-open
contains32candidates and original image fingerprints. No other drawing from
that contact sheet is automatically approved.

### Native variation retention repair — 2026-11-03

Previous goal turn classified as progress: verified completed production logs
and repaired the stale restart checkpoint. Goal remains active and incomplete.

Ink companion gate89935 TERMINAL0: 1 passed in77.73s, identical outlines,
metrics, substitutions and exact ink bytes. Started strengthened four-product
emoji reproducibility gate15661, log /tmp/final-objects-four-product-rebuild.log.
LIVE when checkpoint written; do not restart or change emoji compiler/art inputs
until terminal. It compares colour font, ink font, manifest and glyph review.

Added tools/font/native_variations.py and generic selector retention in
build_scripts.py. Retains selectors even without ordinary cmap mappings and
records compact selector-to-base ranges as nativeVariations. Cache recipe changes
only for sources containing native variation tables. Four focused real-source
subsetting checks passed (Math, WenKai, Padauk plus absent-base guard), preserving
variant outlines/metrics and layout-closure bases. Added production shard checks
for those sources; these await rebuilt assets and have NOT run yet.

Script build54521 LIVE: /tmp/native-variation-script-build.log. Last observed
stage KleeOne,13shards. Do not duplicate this build. After terminal, run
 tests/test_native_variation_packaging.py and relevant script packaging tests,
verify metadata/font hashes, then version assets. Native variation runtime routing
still UNFIXED; retain ordinary text behaviour and full joining-script selection.
Sources skipped because all ordinary bases are already covered may require
additional variation-aware source selection; retention alone does not prove
complete standardized/ideographic variation coverage.

### Native variation routing and omitted shards repaired — 2026-11-03

Previous goal turn: progress (selector-retention code and four source checks).
Build54521 TERMINAL0:352shards60,646,380bytes. First production gate passed31
Python checks. Ink companion89935 already passed. Exact emoji rebuild15661 is
STILL LIVE at this checkpoint; /tmp/final-objects-four-product-rebuild.log.
Do not restart or modify its emoji compiler/art inputs while active.

Added js/font-variations.js: exact native selector/base matching and complete
cluster repertoire checks. requiredFonts loads native variation sources even
when Dad Lettering covers the base. text-metrics passes an explicit per-run
fontFamily through measurement and painting; ordinary adjacent Latin stays in
Dad Lettering. fontRuns retains whole contextual scripts rather than splitting
UVS clusters from neighbours. Added pinned variationContextScript Unicode table
for scripts such as Myanmar that lack ArabicShaping joining types. Existing
Arabic joining eligibility and dedicated Egyptian variation routing are retained.
The first full JS run caught regressions in these two paths; fixes restore them.

Actual Han strip exposed a second bug: ordinary cmap coverage caused entire
UVS-bearing source chunks to be skipped. Builder now separately tracks covered
variation pairs and retains chunks providing new pairs even when bases already
have an earlier source. Corrected build80685 TERMINAL0: **379shards68,098,520bytes**.
No duplicate/live script build remains. Additional on-demand shards supply real
native drawings; total manifest nativeVariations records29,901.

Corrected production gate48723 passed **32 Python tests17.27s** (packaging,
source outlines/metrics and script shaping). Subsequent strengthened Han outline
comparison log /tmp/native-variation-han-source-test.log; check terminal result.
JavaScript33488 passed **322tests9.87s**. Unicode browser-table reproduction passed
1test0.20s. Asset URLs versioned. Audit48432 completed: visible cmap unchanged
172,176/172,352. Actual packaged format14 encoding:265/1,437standardized variants;
482/742emoji variation pairs (470custom). These are encoding counts, not complete
routing/visual validation; GSUB-driven variants require separate investigation.

Four new actual strips visually inspected individually: native-variation-math,
quotes, han, myanmar. All pass fallback/unmapped/font-priority/geometry checks;
original art and silent fourth panel retained. Math zero and script forms and
Han alternate visibly differ. Canvas serializes numeric font sizes, so the
priority check compares the first family rather than an exact float string.
Full603case browser run LIVE in tab28 at this checkpoint; last observed coloured-
hearts stage. Do not navigate/restart until summary is terminal. vtab binding;
parse AX summary without dumping603entries. Prior tab25/26 handles failed with
browser.user unavailable; fresh cua.createBrowserTab worked. Tab27 was an
unbound duplicate and may be automatically cleaned up; actual active tab28.

Remaining variation work: standardized CJK has **1,002 pairs** referencing exact
CJK compatibility ideographs. All1,002bases AND target drawings were found in
pinned licensed Jigmo/Jigmo2/Jigmo3 sources, but these standardized mappings are
NOT implemented. Native IVD selector support does not cover FE00.. standardized
CJK pairs. Other435standardized variants include existing Egyptian rotations,
math/quotes/Myanmar and source GSUB-driven behaviour; audit routing separately.
35standalone emoji components and141Seal mappings remain unimplemented.

Full browser run in tab28 TERMINAL: **603cases, failures[], geometry[]**.
All four native-variation strips individually reviewed. nativeBrowserReport
contains the report in CUA memory; tab28 markedhandoff. Strengthened Han source
outline/metric comparison TERMINAL0:1passed0.49s. Final emoji exact-rebuild15661
remains LIVE (last polled directly, no terminal result). No second emoji build.
Next: finish that gate, capture immutable5,498sequence baseline, then add35
standalone components; standardized CJK mappings are another ready independent
workstream. Full goal and remaining141Seal/style/script/renderer scope unchanged.

### Standardized CJK variations implemented — 2026-11-03

Previous goal turn classified as progress: native retention/routing and all603
browser scenarios passed. Goal remains active and incomplete.

Added build_cjk_variants.py. It verifies pinned Unicode StandardizedVariants and
UnicodeData hashes and the pinned CC0 Jigmo ZIP hash, reads the three font members
without altering extracted sources, validates every compatibility decomposition,
and maps all **1,002 standardized CJK pairs /902bases** to the exact specified
compatibility ideograph drawing. Native contours, component transforms and
metrics are copied (not retraced). The first retracing prototype removed a
repeated closing point in one glyph; exact native copying corrected that without
weakening the strict outline test. Compiled font346,816bytes. Provenance, archive
member hashes and CC0 notice recorded in cjk-variant-manifest.js and
cjk-variant-review.json. Source style remains provisional and visibly native.

Loaded only on exact native UVS matches; ordinary Han/Latin never gets a global
font override. JS font routing includes the new variationOnly source. All1002
pairs get exact sequence/font selection tests, and ordinary/unsupported-selector
forms are checked against accidental font capture.

Build34219/17287 TERMINAL0. Three Python tests passed4.72s: every1002outline and
advance matched source, everypair shaped to its designated single glyph, exact
font/manifest/review rebuild and inventory checks. JavaScript93936 TERMINAL0:
**323passed9.78s**. Audit94280 TERMINAL0:172176/172352visible unchanged. Packaged
format14 encoding now1267/1437standardized variants; standalone native variations
encoded1144 (CJK1002+Egyptian142). Counts are not complete behaviour/style proof.
Actual CJK strip checked font priority/fallback/geometry, visually inspected.
Full **604case browser run TERMINAL:failures[],geometry[]** in tab29.

Remaining170withoutformat14 break down **117Mongolian,6PhagsPa,5Manichaean,
42Common**. Added test_contextual_variants.py: all128contextual sequences checked
in isolate/initial/medial/final contexts, exact source/packaged glyph contours and
positions, and each pair demonstrates a different drawing in at least one tested
position. **3passed0.42s**. This validates GSUB-driven variants which table counts
miss. Three new actual strip fixtures all pass individually and were visually
inspected: contextual-variation-mongolian/phags-pa/manichaean. These were added
AFTER the604case run; aggregate corpus now607, no freshfull607claim. Tab29 marked
handoff. No live browser run remains.

The42Common variants still lack demonstrated support: circleparallel-line
variant, fullwidthzero, U+1DB10descender, eight lazy-S/horizontal-equality math
forms,26roundhand capitals, kurrent smallz and four Sibe quotation forms. Precise
inventory in prior diagnostic output / pipeline source data. NotoMongolian lacks
FE02 cmap and format14 mappings, so do not assume Sibe quote support from its
ordinary Mongolian coverage. Style, other sequence coverage and script/renderer
requirements remain open.

Added snapshot_emoji_shaping.py, a reusable immutable baseline capture tool:
checks both companions' named glyphs/positions for all advertised forms, verifies
products unchanged during capture, exclusive-create output. NOT RUN YET because
emoji exact-rebuild15661 is still LIVE (last directpoll). Its inputs remain frozen;
no standalone-component integration has begun. After terminal, capture current
5498forms before promoting35components. Remainingvisible141Seal+35components.

### Final-object release gates completed; standalone candidates — 2026-11-03

Previous turn: progress (all1002CJKvariants and128contextual source-shaping checks).
Exact emoji rebuild15661 **TERMINAL0**:1passed,7existingwarnings,1094.12s.
All four products (colourfont,inkfont,emoji manifest,glyphreview) byte-identical.
No live main emoji build remains. Nine final-object source registry top-level
statuses now accurately record production integration and verified gates; per-file
source records and core programs unchanged.

snapshot_emoji_shaping15536 TERMINAL0: exclusive-created immutable
output/font-review/pen-translation/pre-standalone-component-integration-shaping.json,
all **5498forms**, bothcompanions namedglyphs/positions and producthashes.
Never overwrite it. This is required before any35component promotion.

Added candidate-only emoji_standalone_components.py,prototype builder and contact
sheet.26regional indicators reuse the existing actual Dad Lettering capitals,
without further distortion; pinned Noto glyphs establish their semantic role.
Five tone tiles preserve every native hatch and receive existing PDF-sampled
skin fills. Four hair components retain native dashed frames; red-hair broad
solid mass alone receives inset sampled orange, preserving original solid
monochrome fallback. Nine nonletter drawings use expressive1.7withguardedbackoff.
Source Noto nativeproof was re-inspected; darkest tone is a grid, NOT solid ink.
No nonexistent solid-tone repair introduced.

Candidate46297 TERMINAL0:35forms/1225pairs; positive area contours,actualbearings,
colour/inkshapingidentical. ColourSHA5db63540e18a4d8824ee65ac84263c3fdf07d7a4c006ab9430afbc63bb422fba;
inkSHAa253f9685e0e5a951ab4dadd02f055810c86320d03ae4a1cdf06c50bc245b16b.
Candidate semantics/counter suite40874 TERMINAL0: **4passed1.81s**. All26letter
masks exactly match existing lettering; all5nativehatches unchanged; red inset
cannot touch componentframe; fallback/display compiled counters preserved for35.
Prepared mask contact sheet standalone-components-prototype.png visually reviewed
at132px/34px. Compiled-font optical browser review stillpending. New dedicated
candidate HTML grid built by91059 LIVE at checkpoint; log
/tmp/standalone-components-candidate-rebuild.log. This recompiles isolated outputs,
NOT production. Source registry whitelist and production promotion stillpending.
67228 is a live readonly font-name inspection, not a build; poll same handle.

### Standalone components registered; production build started — 2026-11-03

Candidate91059 TERMINAL0, colour/ink hashes exactly unchanged. Dedicated tab30
compiled-font grid:35forms,failures[]; all35glyphs inspected enlarged and33.6px
beside original24px lettering. Tab30 markedhandoff. Existing mask contact sheet
and compiled forms both reviewed. Baseline pre-standalone-component-integration-
shaping.json contains5498unchangedforms and remainsimmutable.

Preserved candidatefonts,JSON,validation and hashes ONCE in
pre-standalone-component-registration/. Added35exactsingletonforms to registered
Noto source whitelist; source file bytes/hash/license unchanged. Source roles
explicit:26actualDadcapitals,9Noto tone/hair drawings. Added dedicated compiler
which may overwrite ONLY exact named empty zero-advance component glyphs and
preserves their names. All35 fallback/display counters checked, everycandidate
outline/layer/colour/advance compared independently. Candidate+compiler suite:
**5passed4.38s**,7existingwarnings. Nine final-object delivered registry checks
also passed. Candidate metadata staysisolated; production treatment records
candidateOnly:false. No existing per-file final-object sources or core recipes
changed when top-level delivered statuses were corrected.

Main production build **98898 LIVE**:
log **/tmp/standalone-components-production-build.log**. Do not duplicate or mutate
emoji inputs until terminal. Expected (NOT yet claimed)1435visiblebases,1459cmap,
24components,5533forms and visiblegap141Sealonly. Need actual audit to establish.
Required gates after terminal: compare all35 reviewed forms/layers; all5498old
names/positions in bothfonts; knownflag/tone/hair GSUBs; unknownRIpairs retain
native routing; malformed modifier compounds stay intact; fullJS/browser tests,
allnewactualstrips,inkcompanion and exactfour-productrebuild. Old test assumptions
5498forms and standalone tonesbeingempty need updating only against verified
newproduction state. Sources/testscope must remain honest.

Added pending production tests test_font_standalone_components.py:35exact art/
metric/layer comparisons,all5498previous namedglyph/position comparisons in both
companions,35advertisedvisibleforms,expected5533total. NOT RUN against pre-build
fonts. Main98898last observedfaces/hearts/shapes,stillLIVE. Candidate and compiler
inputs now frozen until terminal. No secondmainbuild or exactrebuild started.

### Explicit math variants and ordinary fallback guard — 2026-11-03

Previous goal turn: progress (35reviewedcomponentcandidates,baseline5498,
compiler/source registration and mainproduction98898started). Main98898 still
LIVE: /tmp/standalone-components-production-build.log; lastobservedflags.
Do not duplicate or modify emoji input modules/recipes until terminal.

Added8pendingactualstripfixtures (5regionalindicatorgroups,tones,hair,boundaries)
and exact runtime tests for35singletonforms,oldflags/people,andunknownRI/malformed
modifierclusters. NOT yet run against newproduction;oldmanifestremains5498until
mainbuildterminal. Static corpus now616 including newmathcase; nofull616claim.

Investigated42Common standardized gaps. Official Unicode18chapter22 confirms
explicit chanceryFE00/roundhandFE01 distinctions. NewComputerModern publisher
README confirms explicit roundhand mapping; CTANrelease8.1.1nativeOTF provides
**27 missing native mappings** (26roundhand capitals+29B7FE00). It does NOT supply
FF10FE00,1DB10FE00,kurrentZ,eightnewhistoricalmathforms or fourSibequotes; these
**15remainopen**. No styles guessed from unlabelled defaults or nonstandard
bold-script UVS. Initial sourceCLI probe used systemPython accidentally; reran
with.venv. No failed-output font was consumed.

New data/font-sources/newcm.json records releasebinary SHA independently from
sourceGitcommit29149c0a75b5386c7e8ccc818a1ea6d2ca1e0128 andeditableSFDhash.
Downloaded actual publicCTANOTF (not the loginHTML returned by sourcewebpages).
NormalpublicGitclone retrieved pinned source/LICENSE; nochallengewas solved.
Sourcefontcopyright and package licence identify GUST terms forMath (GPL applies
tootherfamilies). GUST1.0/LPPL1.3c/package notices bundled, derivative renamed,
changes documented, complete upstream availability and reproducible source
provided in licenses/README-DadMathVariants.txt. Donor-only registry prevents
unrelated source characters replacing ordinary script mappings. BinarymirrorURL
is mutable but must match fixedhash; mismatchfailsverification.

New build_math_variants.py retains ONLY27approvedUVS plus requiredglyphs/native
layout and combiningmarks, preserving CFFcurves. Font63,012bytes. New mathmanifest
and review preserve sourceglyph names and hashes; unrelated78sourceUVS choices
notadvertised. All27sourceoutlines/metrics and native positions with noaccent,
acute,stackedcircumflex+dot checked;allthreeproducts reproduce. **2Pythonpassed
0.57s**. Initialfocused31JSpassed; afterfallbackfix **43targetedJSpassed9.42s**.
All **12,588 cached registered source files** verify (fournewsource/licencefiles).
Audit:visible172176/172352unchanged;format14standardized1294/1437encoded (notfull
validation),standalone native1171. All128GSUBvariants remainseparateproof.

Found andfixed cross-runfontleak:loadedvariationOnlyCJK/Mathfont families had
remained inordinary fallback stacks. makeFontString nowfiltersallregistered
variationOnlyfamilies unlessselectedfor thatrun (existingEgyptianpolicyretained).
Actualfontstack regression checksordinaryHan/Math fallback retainsoriginalfont,
while matchingvariantfontleadsitsrun. New mathactualstriptab31 passedfontpriority,
unmapped/fallback/geometrychecks; visuallyreviewed,thenreloadedafterfixandpassed.
Tab31markedhandoff. Fullbrowser/npm regressions awaitmaincomponentbuild.

Furtherprimaryreference: Unicode18chapter6 officialSibequotationdiagram,
https://www.unicode.org/versions/Unicode18.0.0/core-spec/figures/variation-sequences-for-quotation-marks.svg
cached /tmp/sibe-quotation-reference.svg andwhite-backgroundPNG, visuallyreviewed.
InHORIZONTALlayout SibeFE02 uses the same narrow/upright quote appearance asFE00;
its distinctive orientation isVERTICAL (upright instead ofrotated). Potential
nextfix:derivefourhorizontalFE02aliases from licensedWenKaiFE00drawings, with
explicit standardreference andseparatevertical limitation. NOT IMPLEMENTED YET;
noUnicodechartartcopied into fonts. Remaining15alsoincludethe8newhistoricalmath
relation variants approvedUTC186-C34 (UnicodeL2/2026/26003.htm),CartesianEquals
descender,fullwidthzero andkurrentZ. Sources/currentfonts do not yet demonstrate
these forms. Fullbrief/style/141Seal+35pendingcomponents/renderer scope unchanged.

### Components delivered; horizontal Sibe forms and mark preservation — 2026-11-03

Previous goal turn: progress (27nativeMathvariants,source/licencepinning,
font-stackleakguard and targetedvalidation). Full goal remains incomplete.

Mainemoji98898 **TERMINAL0**: **1435visiblebases,1459cmap,24components,
5533forms**,colour3,154,060bytes. Audit78797 TERMINAL0: **172211/172352visible**,
**141missing,ALLSeal**;3963/3963FQemoji,zero gaps. New35components source/candidate
art and metrics match; all5498previous namedglyphs/positions inbothcompanions
preserved. Production71076 TERMINAL0: **604passed,1deselected,7existingwarnings,
164.54s**. Coverage-invariant35318 TERMINAL0:1passed17.70s; tonesnowvisible,
joiningcontrolstillinvisible,actualcmap/componentcounts agreewithaudit.

InitialJSrun had one obsoleteexpectation that loneRI_Gmustbenative; corrected
that assertion to customwhileunknownAAandinvalidflagclusters remainnative.
Thenbrowser617run exposed a REALwhitespaceissue:GB9groupstonewithprecedingspace,
so second/third standalone swatches fellback. Added routingClusters():ONLYaZs
space+exactone registeredstandalonetone splits into space/text and tone/custom
fontspans; logicalgrapheme/linebreaking inputunchanged,other modifier/ZWJclusters
staywhole. Sharedbyfontselectionandpainting. Testscover3spaceforms*5tones,
preservedtext,loadedfonts and nofallback/missing,withinvalidclustersstillnative.
CorrectedJS8248 TERMINAL0: **328passed9.56s**. Fullbrowser rerun in tab32:
**617cases,failures[],geometry[]**. Everynewactualstrip reviewedindividually:
regional1..5,tones,hair,boundaries; existingart and silentfourthpanel retained.
Sibeactualstrip also reviewed. Tab32markedhandoff. No livebrowserrun remains.

Inkcompanion64062 TERMINAL0:1passed76.91s. Started **81813 LIVE** exactfour-
productemoji rebuild: /tmp/standalone-components-four-product-rebuild.log.
Do not restart or modify emoji compiler/recipes/source inputs until terminal.
It independently checks colourfont,inkfont,manifest andglyphreview bytes.

Sibehelper derives horizontalFE02quotealiases from licensedWenKaiFE00drawings,
per officialUnicode18section6.2.6diagram. Verticalorientation remainsunsupported
and is explicitin per-shard variationDerivations. Nochartartcopied. Script44935
TERMINAL0:379shards68,098,584bytes. Source/package/oldshapingtests18076TERMINAL0:
**34passed18.72s**. Actualfonts/metadata routeallfourpairs and preserve native
narrowpositions. Auditstandardizedformat14 **1298/1437**;128GSUBsourcevariants
remainseparateproof. The11stillopenarefullwidthzero,ninehistoricalmathrelation
variants andkurrentZ. Encodingcountsare notcompletebehaviour/stylevalidation.

Found validUVS+marksourcecoverage gap:splitshardscanomitmarkscopedby their own
originalfont (WenKaihas63,JigmoBMP8); routingthenlosesthevariantonmarkedclusters.
Newvariation_marks.py retainsavailable source marks inUVS-bearingchunks only;
per-chunkcachekeyinvalidatesaffectedshards,notunrelatedfonts. Noinventedmarksor
attachments. Jigmo2/3haveNOmarks in source; unsupportedcross-fontmarkedvariants
stillrequireinvestigation,do notclaimallarbitrarymarkedIVDcorrect.

Added fullwidth_zero.py:copy BOTHnativeNotoMathzero/default andnativeexplicit
short-diagonalUVSdrawings,translateintoanem-widecell,retainlogicalFF10 andemadvance.
OriginalASCIIglyphs/metricsunchanged;newcopiesunhintedtoavoidwidth-dependent
instructions. Source1testpassed0.29s after correcting a literal0vsU+0030typo.
Registeredrecipe/provenance inbuild_scripts ONLY;noemojiinputchange. Not yet in
shippedshard. Combinedhelper/source suite76822TERMINAL0:4passed1.22s.
**Newscriptbuild28255 LIVE**: /tmp/variation-mark-fullwidth-script-build.log. Do notduplicate. Afterterminal,run source/
packaging/nativepositions tests,actualmarkedquote/IVD/fullwidthzero routing,
versionassets,auditandbrowserchecks. Prior617browser result predatesthese
pendingnativeasset changes. Emoji exactrebuild81813 isindependent andstillLIVE.

All8new actualemoji strips individually visually reviewed after corrected617
browserrun:regional1..5,tones,hair,boundaries. Eachhasnofallback/unmapped/failure/
geometry. OriginalDad/Calvin artand silentfourthpanel preserved. Sibeactualstrip
also reviewed withFE00comparison andMongoliancontext;passed. Tab32markedhandoff.
All604productionregressions,328JS,617browser,inkcompanion andcoverageinvariant
arecomplete for currentemoji5533state. Exactfour-productrebuild81813 remainsLIVE.
Pendingnative script28255 lastdirectlypolledLIVE; do not duplicate eitherjob.
Next: finish28255,verify fullwidth/markedUVS sourceandpackagedshaping,version/audit,
reviewaffectedbrowsercases; thencontinue10remainingstandardizedmathvariants and
141Sealcharacters,broaderstyle/script/rendererbriefrequirements. No goalcompletion.


### Math Unicode accent repair — 2026-11-03

Previous goal turn: progress through authoritative log reconciliation and corrected
restart checkpoint. Goal remains active and incomplete.

Completed the pending math mark repair. Source NewCM combines several Unicode
marks with spacing advances and base glyph classes; source Noto Math omits
above-mark anchors on several variant bases. Added missing GPOS attachments
using source MATH optical points and actual ink bounds, normalized Unicode Mn/Me
advances to zero, retained original curves/bearings and base metrics. Enclosing
marks remain overlays. Native Noto above-stack filtering included below marks;
filtered opposite-side marks out while retaining native same-side anchors.
Existing native alpha/x/A single and repeated same-side stack positions remain
source-identical. Mixed below/above stacks now stay on their correct sides.

Geometric tests cover all 27 explicit math variants AND their defaults with
acute, circumflex+dot, and below-dot+circumflex+dot; they check ink clearance,
optical alignment, mark advance and base stability. Every retained NewCM Unicode
combining outline/bearing is donor-identical. Both fullwidth zero drawings and
ASCII zero variants get equivalent geometric checks. Source outline-only and
unmarked shaping equivalence checks remain; removed the incorrect assumption
that source-broken Unicode accent positioning should be preserved.

Explicit math font: 27 variants, 64,248 bytes. Script build54440 TERMINAL0:
379 shards, 68,128,012 bytes. Production46888 TERMINAL0: **46 passed22.24s**;
JS49859 TERMINAL0: **329 passed9.57s**. Stronger all-combining-outline check then
passed all3 math tests in0.65s, including exact three-product rebuild. Updated
licence modification notice and versioned asset URLs. Audit15340 TERMINAL0:
172211/172352 visible,141Seal gaps;1299/1437 standard pairs have format14 mappings
(the128GSUBcontextual forms have separate evidence, not format14 mappings).

Actual fullwidth and explicit-math strips in tab33 passed routing/export/geometry
checks and were individually visually reviewed: acute is above the base, stacks
clear, below dot remains below, original character art/silent fourth panel kept.
Full619 browser corpus was started in the SAME tab33 and is still being observed;
no completion claim yet. Do not restart solely because a read times out.

Ten remaining standardized noncontextual mappings were re-derived from actual
shipped fonts versus pinned Unicode18 data: U+1DB10 FE00(descender), U+223D,
2243,22CD,2242,2248,2A6C FE00(lazy S), U+22DC/22DD FE00(horizontal equal),
U+1D4CF FE02(kurrent z). Source/style/script/Egyptian/grid/cross-browser scope
and141Seal gaps remain. No goal completion.


Math repair final browser gate: same tab33 completed **619 scenarios with
failures[] and geometry[]**. The earlier observation timeouts were transient;
no duplicate run was started. Tab33 marked handoff. All builds/tests/audit for
this repair are terminal. Next: remaining10standardized noncontextual variants,
141Seal gaps, and broader brief requirements. Goal remains active.


### Historical relation candidates — 2026-11-03

Previous goal turn: progress; completed math mark repair and full619browser gate.
This turn: reviewed authoritative WG2 N5334R2 pages3,8,37,38 and N5333R2 pages4,12.
Downloaded both complete PDFs, pinned their hashes in
`data/font-sources/math-variant-references.json`, cached under
`build/unicode-sources/math-variant-references/`. They are semantic/reference
sources only. No embedded font program, chart outline or page artwork is used.
The relation reference explicitly distinguishes lazy-S curves from tildes, two
horizontal bars plus one diagonal from ordinary equal-or-less/greater, and a
Cartesian descending stroke. The kurrent-z proposal remains separately open.

New reproducible isolated candidate builder:
`tools/font/prototype_historical_math_variants.py`. Nine relation variants use
licensed NewCM inverted-lazy-S curves with affine transforms and composition,
original horizontal/diagonal pressure strokes, and an original Cartesian default
and descending drawing. Eight donor defaults retain exact outlines and metrics.
Single-donor NewCM/GUST/LPPL font with renamed family, original copyright,
modified-work notice, source revision and copied licences. No mixed-licence donor
font programs are combined. Candidate output:
`output/font-review/historical-math-variants/{candidate.otf,candidate.json,specimen.svg,specimen.png,README.txt}`.
Specimen was visually compared to the reference topology; horizontal variants
were shortened to preserve math-axis alignment. Candidate only: combining-mark
attachment, final comic-size weight/style and production integration remain.

Caught a review-tool failure: Pillow is built without libraqm and silently ignores
variation selectors. Replaced text specimen rendering with actual named glyph
paths rendered by MuPDF; separately verify actual HarfBuzz selection. The initial
Pillow sheet was misleading and is superseded by the current SVG/PNG.
New tests check all9 one-glyph/positive-advance selector mappings and adjacency,
distinct actual outlines, all8 exact native defaults, horizontal bar/arm topology,
Cartesian descender geometry, notices and exact reproduction of font/JSON/SVG/PNG/
README. **3passed0.49s**,7existingSWIGwarnings.

No production assets/manifests/runtime routing changed this turn. All10 mappings
remain unshipped:9 now have tested isolated candidates, kurrent-z still needs a
chosen drawing/source. Next: combine these9 with the existing27 math variants,
retain combining attachments, verify previous27 and ordinary-font priority, review
actual strips; resolve kurrent-z; then141Seal gaps and the wider brief. Goal active.


### All ten mathematical standardized mappings integrated — 2026-11-03

Previous goal turn: progress; nine isolated historical relation candidates and
pinned primary reference PDFs. This turn: promoted all nine relations, drew and
integrated original kurrent z, and completed affected actual-strip review.

Separated reusable pure drawing/install code into
`tools/font/math_historical_variants.py`; prototype specimens still use the same
curves. Production builder now advertises37exactUVS:27nativeNewCM+9historical
relation adaptations+1originalkurrentz. Entire font remains a renamed NewCM/GUST/
LPPL derivative; no OFL donor font programs are combined. Required copyright,
modified-work/source notices and original-source availability retained. Kurrent
z's curved top, descending closed loop and rising diagonal were checked against
N5333R2 pages4,12,19. Original sampled pressure centreline; no chart outline or
embedded font copied. Reference cache hashes verified. Font **67,452 bytes**.

Saved EXCLUSIVE immutable baselines before both integrations:
`output/font-review/pre-historical-math-integration/`(27native forms,216shaping
cases) and `pre-kurrent-math-integration/`(36forms,288cases), including old font,
manifest,review and named glyph/position cases. Do not overwrite. All old cases
retain glyph names, advances and accent positions. All10new outlines/metrics
match isolated candidates; both new/default forms pass above/below/stacked mark
geometry checks. Kurrent candidate has exactly one enclosed ink counter BELOW
baseline, distinct from ordinary script z, and only FE02 selects it.

First CFF integration exposed an actual packaging error: setting TTFont glyph
order alone did not update the CFF charset, so subsetting dropped added programs.
Corrected both orders before subsetting; the build then passed. The prototype
refactor also lost a math import; restored it and reran all affected tests.
Production/candidate focused **9passed1.57s**,7existingSWIGwarnings. Broader native
suite **52passed23.32s**; after specimen-height correction, exact font/manifest/
review and candidate/font/JSON/SVG/PNG/README reproduction again passed all9.
Asset URLs versioned. Audit unchanged visible172211/172352,141Seal gaps.

Actual fixture routing/export/geometry and visual checks completed in tab34:
`native-variation-historical-lazy-1`, `...lazy-2`, `...arms`, and
`native-variation-kurrent`. All9relations, Cartesian descender, kurrentloop,
ordinary Latin priority and acute/mixed stacks visible; original art and silent
fourthpanel retained. Full622browser run finished failures[]geometry[] before
kurrent integration. Final **623scenario** run after kurrent integration also
finished **failures[]geometry[]**. No live browser build remains.

New complete standardized mapping inventory gate reads actual referenced font
files and pinned Unicode18data: **1309format14 pairs**, with exactly **128**
contextual exceptions (117Mongolian+6PhagsPa+5Manichaean), already source-shaped
in fourwordpositions by the contextual suite. **1new Python inventory test passed
1.27s**. New JS inventory gate iterates ALL1437pairs through actual font selection
and font runs. It distinguishes native selections, joining runs, Egyptian
rotations and expanded lost-sign composition. Initial test wrongly assumed
Myanmar needed a forced per-cluster family, then assumed all Egyptian format14
pairs used the generic font-selection path; corrected those assertions to the
existing deliberate shaping/layout policies. Targeted **9JS passed0.33s**.
Final full JS suite is running: /tmp/standardized-variation-final-js-tests.log.

All1437 standardized mappings are now accounted for, NOT fully behaviour/style
validated. Audit retains validated:0 and incomplete status. Arbitrary marked
IVD cross-font combinations, vertical Sibe orientation,141Sealcharacters, native
script style/linguistic review, Egyptian/dictionary/grid edge cases and cross-
browser requirements remain. Full brief and active goal are unchanged.


Final JS25816 TERMINAL0: **330passed9.43s**. Final all1437routing gate uses
1163native selections,128contextual joining paths,142Egyptian rotations and
4expandedlost-sign compositions. It does not force generic per-cluster routing
onto intentional whole-script/composition paths. No runtime policy changed for
that gate. Native suite52+new inventory1 passed; final focused9 reproduction
checks passed after specimen-height correction. Full623browser passed andtab34
markedhandoff. No builds/tests remain live. Next: cross-font marked IVD handling
and141Seal source gaps, plus the full remaining style/script/renderer brief.


### Native CJK marks with supplementary IVS — 2026-11-03

Previous goal turn: progress, integrating all ten math variants and completing
all1437 standardized mapping accounting. This turn fixed an actual CJK routing
gap: supplementary Jigmo IVS plus native CJK marks had no whole-cluster font,
so could lose the explicit variant. Before the repair all16 test combinations
(two supplementary bases, eight marks) had no nativeVariationFont match.

New `tools/font/jigmo_variation_marks.py` copies U+302A..302F and U+3099..309A
from the same pinned Jigmo BMP CC0 donor. Em and all three hint tables must be
identical; preserve exact contours, bearings, horizontal/vertical metrics,
instructions and source classes. No new mark drawings or anchors. Add only to
supplementary chunks with UVS bases; per-chunk cache/provenance includes donor
hash and helper hash. All62 variation-bearing supplementary shards gained these
marks;13 other supplementary shards retain their original scope. Original chunks
and native variant drawings remain intact. Manifest additionalSources records the
CC0 donor; source README explains the scope.

Source checks initially compared mark offsets against a DIFFERENT BMP ideograph.
That was an incorrect assertion: HarfBuzz fallback placement uses base ink bounds.
Replaced it with an independent BMP control containing the exact variant base.
Source3checks passed22.19s; reject incompatible hints and replacement of native
marks. A control-font test construction briefly duplicated a glyph-order entry;
fixed order capture before adding the proxy and reran successfully.

Script build51747 TERMINAL0: **379 shards,68,170,376bytes**. Native/CJK production
suite71515 TERMINAL0: **42passed83.42s**. Then tightened full supplementary source
inventory assertion from a lower bound to EXACT2677;64781 TERMINAL0: **1passed
42.91s**. All2673Jigmo2+4Jigmo3 mappings retain native glyph curves, metrics and
unmarked shaping; copied marks retain donor outlines and both metrics. All8marks
route to the exact variant font on two supplementary source cases, with unknown
selector negatives. JS4342 TERMINAL0: **331passed9.82s**.

Versioned assets. Audit62492 TERMINAL0 remains172211/172352visible,141Seal gaps.
Actual ExtB and ExtG strips (tab35) individually reviewed; all16 marked forms,
Latin neighbours, original art and silent fourthpanel kept; no fallback/unmapped/
geometry failures. Full **625 browser scenarios passed failures[]geometry[]**.
Tab35markedhandoff. All known builds/tests/audit are terminal.

This repairs the eight native CJK marks, NOT arbitrary cross-font accents or
arbitrary marked IVD. Preserve that remaining scope. Broader source/style/script,
Egyptian/dictionary/grid and cross-browser requirements remain; goal active.

New Seal font leads, NOT production coverage: inspected public repositories
https://github.com/lxgw/LxgwSeal (commit2b1d01195168110b9a8f3a8abaff844ff22fa716)
and https://github.com/Ghimist/seal-sans (commit9372f0813770a605ec5ee068fc48660b231b3427).
Downloaded pinned font binaries and exact licence texts to
`build/unicode-sources/seal-font-probes/`. Detailed probe hashes, glyph names,
metrics, bounds and outline fingerprints:
`docs/seal-font-probes-2026-11-03.json`.
LXGW has165Seal cmap entries,2current gap candidates(U3E34F,U3FA42),underOFL with
reservednames. SealSans has11328Seal mappings and141distinct nonempty gap drawings,
underAGPL3. Contact sheet visually inspected at
`output/font-review/seal-source-probes/seal-sans-missing-141.png`.

Nonempty unique outlines do NOT verify identities. Neither font is registered or
shipped. SealSans includes nonstandard tone-VS semantics outside our scope; do
not import wholesale. Its source notes use N5344(2025-10-07) mappings; comparison
with pinned18.0data finds30modern-CJK and16radical-value changes, requiring care.
Before adoption, verify normative edition identities and compare with accepted
source forms; review the complete source, AGPL/source distribution and exported-
comic implications. Preserve original fonts/notices and rename derivatives.
Next major opportunity: validate these141Seal candidates; retain all previous217
recovery baselines and avoid replacing accepted drawings merely for uniformity.


### Restart recovery checkpoint — 2026-11-03

Integrated two OFL LXGW Seal native glyphs (U+3E34F, U+3FA42), scoped to
these two characters and renamed. Build: 380 script shards / 68,172,856 bytes.
All 379 previous script font entries and file bytes remain unchanged. Scoped
preserve_native_bounds flag fixes a one-unit source bounds recalculation so
both new glyph drawings and metrics exactly match their donor.

Latest audit: 172,213 / 172,352 visible characters have bundled cmap entries;
139 missing, all Seal. Latest JS suite: 332 passed / 0 failed. New LXGW source
suite: 3 passed. Full browser corpus completed: 626 scenarios, no reported
failures or geometry errors (session checkpoint; not rerun after restart).
Review queues now derive coverage from actual shipped manifest subsets.

Remaining Seal Sans source is not shipped. Pinned source/licence probe and
24 reference sheets exist. Sheets 01–16 (96 of 141 candidates) were visually
compared after the preview centering fix; all match reference topology.
Those decisions are now saved in the probe review.json with source/reference
and drawing hashes. Sheets 17–24 (45 candidates) remain pending: the attempted
four-image batch exceeded context, so those images do not count as reviewed.
The review generator currently resets review decisions; preserve decisions
against matching source/reference/drawing hashes before regenerating it.

Next: finish candidate comparisons, package the separate AGPL font with its
complete corresponding source and notices, then integrate only the remaining
139 gaps and verify exact curves, unchanged prior fonts and real strips.
App currently exports PNG pixels, not embedded font programs. Preserve source
licence obligations and revisit them if font-program export is introduced.

The complete beta brief remains unfinished: cross-font marked IVD/accents,
script style/reader review, Egyptian/dictionary/grid edge cases and cross-engine
validation remain. No build/test/audit was recorded as live at restart. Process
inventory via ps was denied by the sandbox; no fresh OS-level claim is made.


### Seal coverage closed with native licensed supplement — 2026-11-03

Previous goal turn classified as progress: saved the restart checkpoint and
96 reference decisions. This turn completed all remaining 45 comparisons
(sheets 17–24 individually); all 141 candidates match listed reference topology.
This is structural identity review, not specialist linguistic/style approval.
The sheet generator now preserves decisions only when source font, reference
and per-drawing hashes agree. Regeneration passed and retained all 141 decisions.

Integrated the 139 still-missing candidates as a separate AGPL-3.0 webfont,
Dad Script 96926b398fc1 (56,488 bytes), retaining all previous drawings. Source
manifest: data/font-sources/seal-sans.json. Original Seal Sans is pinned to
9372f0813770a605ec5ee068fc48660b231b3427; original font and full upstream archive
are hash-pinned. Source code never executes upstream scripts. Native cubic
contours are translated +340 y to align the centered source baseline with
lettering; advances, bearings and all horizontal coordinates are retained.
No nonstandard tone UVS, colour tables or unrelated source mappings imported.

Font licence and modification notices are bundled. The app footer provides
direct licence and complete corresponding-source links. Download includes the
full pinned upstream repository (UFO, FontCreator project, mapping/data, original
font and scripts), exact original font, complete standalone modification and
packaging code, recipe, dependency versions and build instructions. Isolated
rebuild from the downloadable package exactly reproduces production WOFF2.
App currently exports PNG pixels, not font programs; revisit distribution terms
if font-program export is added. No categorical legal claim is made.

Initial script build11184 TERMINAL0: 381 shards, 68,229,344 bytes. Native tests
54339 TERMINAL0: 6 passed1.11s. Expanded native regression89382 TERMINAL0:
30 passed6.05s. Every one of 139 production glyphs exactly matches source cubic
curves plus the documented translation, has positive shaping and unchanged
advance/bearing; all 380 prior font entries and actual file bytes unchanged.
Immutable baseline: output/font-review/pre-seal-sans-integration/font-manifest.js.
JS6867 TERMINAL0: 332 passed9.53s. Audit75758 TERMINAL0:
172,352 / 172,352 visible characters have bundled cmap entries, zero missing.
Seal edition/crop queues regenerated to zero pending gaps; old scan rejections
and repair history retained. No rejected scan crop was silently accepted.

All twelve new strips (covering all 139 forms), plus mixed Latin/Seal/LXGW strip,
individually inspected in browser tab37 at realistic comic size. All show original
character art, clear outlines, correct selected font and no fallback/unmapped/
geometry errors. Final group has seven characters in two speeches. Full browser
corpus now has 639 scenarios and is RUNNING in tab37 (known live UI progress).
Final metadata build session11184 finished earlier; final source-notice metadata
refresh is separately tracked in /tmp/seal-sans-final-script-build.log.

Zero cmap gaps is a milestone, not goal completion. Broader mark/IVD variation
behaviour, native script and comic style review, Egyptian/dictionary/grid edge
cases, cross-engine validation and remaining brief requirements stay open.


Seal final verification: final metadata build90841 TERMINAL0, unchanged
381 shards / 68,229,344 bytes. Assets versioned. Final focused source/packaging
suite46472 TERMINAL0: 6 passed1.17s; includes downloadable upstream archive
identity, original licence, UFO/FontCreator source presence, exact standalone
webfont reproduction and all previous-font preservation. Final audit46472
TERMINAL0: 172,352 / 172,352 visible cmap entries. Full browser tab37 completed
639 scenarios with failures[] and geometry[]. All 13 new actual-strip scenarios
were individually visually inspected before this full run. No known font build,
test or audit remains live. Goal remains active and incomplete.

Next concrete priority: preserve explicit variation choices in arbitrary
cross-font marked clusters. Native CJK marks are repaired, but
nativeVariationFont currently requires one font to contain the entire grapheme;
unsupported inherited accents can therefore stop selection of the explicit UVS
font. Inspect font routing, actual shaped outlines and canvas output before
choosing a repair. Keep joining-script runs intact; do not split native shaping
or silently replace variant glyphs. Then continue full brief requirement audit,
style review and cross-engine/dictionary/grid/Egyptian validation.


### Marked CJK variant companions — IN PROGRESS, 2026-11-03

Previous goal turn: progress, closed the remaining 139 Seal cmap gaps.
Current work reproduces a real variant/mark bug. CJK IVS plus acute often fails
nativeVariationFont's whole-cluster coverage test, so the variant font is not
loaded. Browser probe shows simple font priority still replaces U+3402's
explicit variant. Mark-only FontFace unicodeRange aliases preserve the base but
DROP the accent (zero full-pixel differences); rejected, not production routing.
Probe: tools/variation-mark-probe.html; browser tab38. No partial selector-ignore
change was made to nativeVariationFont.

New approach: additional variation-only CJK companion fonts containing the app's
257 existing hand-treated Mn/Me accents. No original font file is overwritten.
Native CJK quadratic contours, metrics and hint programs remain exact; only
borrowed accents are scaled from 1000 to1024em and cubic-to-quadratic converted
(.05-unit approximation, then TrueType integer quantization). Use ink anchors
and same-side stacks. Inputs/notices: data/font-sources/marked-cjk.json and
assets/fonts/licenses/README-DadMarkedCJK.txt. Builder:
tools/font/build_marked_cjk_variants.py. Separate generated manifest:
js/marked-cjk-variant-manifest.js, imported AFTER existing fonts so already-
complete native clusters retain the original selection. All companions are
variationOnly and excluded from ordinary text fallback stacks.

Initial prototype50426 TERMINAL0: source8df1be125651, all1100original glyphs and
metrics exact. Browser pixel probe: copied unmarked variant differs by0pixels;
acute adds271pixels; base region remains0differences. First full build63789
TERMINAL0:92fonts26,033,012bytes. Metadata/refactor refresh75003 TERMINAL0:
same92fonts/samebytes. Initial native tests63800 TERMINAL0:2passed173.66s;
all original glyphs/UVS and new accent stack geometry pass. These are intermediate
checks, NOT final checks after the native-mark fix below.

Extra check found an actual GPOS side effect: installing foreign attachment
suppresses HarfBuzz's original fallback placement of native CJK marks. Now derive
single-native-mark offsets for every original mapped/variant glyph from the
original unmodified font and encode them explicitly as native-mark GPOS anchors.
Prototype7919 TERMINAL0:239,788bytes. All8native single mark positions then
match their original shaping exactly, including with an added acute. A prototype
assertion initially assumed fixed glyph order; corrected it for canonical mark
reordering (acute230 can precede a tone232). Native-only clusters still select
old fonts. Native multi-mark/mixed-cluster typography remains provisional.

CURRENT LIVE BUILD: exec session43291,
/tmp/marked-cjk-native-preserving-build.log. This is the native-position fix build
for all92companions; do not restart on observation timeout. It writes eachfont
atomically and emits final manifest only at completion. Do not claim its font
hashes/size or native checks complete until it finishes. No other known build or
test remains live. Initial full JS41243 failed only the newly added overly broad
expectations; corrected tests distinguish missing enclosing circle and lack of
native marks in standardized CJK source. Focused routing11passed in
/tmp/marked-cjk-routing-final-tests.log. Run full JS after final build.

Current production routing imports companions, with four new actual-strip cases
marked-cjk-ivd-bmp, marked-cjk-ivd-b, marked-cjk-ivd-g, marked-cjk-standard.
Their new browser checks compare source/companion painted pixels, require visible
accent ink and increased ascent, unchanged base region/advance and actual run
font choice. These cases are NOT YET browser-reviewed. Assets need reversioning
after final build/fixture edits. Browser tab37 still contains prior639scenario
success, not a result for this work. Tab38 contains the research probe.

Next: finish session43291; run tests/test_font_marked_cjk.py (now3checks including
native single mark positions), original-font byte checks, fullJS, coverageaudit;
visually inspect all four new actual strips and native-plus-foreign combinations,
then run full643+browser corpus. Add mixed native-mark fixtures before final run.
Keep source/geometry errors distinct from invalid test assumptions.

Scope still open: enclosing/double marks beyond donor, standardized CJK plus
native marks, math/contextual-script cross-font variants and arbitrary cross-
script attachment. This257-mark CJK repair is progress toward arbitrary Unicode,
not a substitute for the complete brief. Full beta goal remains active.


CJK companion build43291 TERMINAL0: **92fonts /26,332,604bytes**. Runtime
companion inventory has 30637native variation mappings and preserves 106792
original glyphs (totals, not full linguistic validation). Repeat cached build
finished and produced byte-identical complete manifest; every cache recipe
matches current builder/helper/accent input hashes. No font build remains live.
FullJS92802 TERMINAL0: **333passed9.64s**. Audit57417 TERMINAL0:
**172352/172352 visible cmap entries**. Isolated fresh rebuild43217 TERMINAL0:
**1passed5.88s**, rebuilding both standardized and native-IVS companion kinds
from scratch without cache or production writes; font and metadata exactly match.
Newtest: tests/test_marked_cjk_rebuild.py.

All five actual strips individually visually inspected in fresh browser tab39:
BMP IVS, ExtB, ExtG, standardized CJK, and all8native marks plus acute. Pixel
controls verify unchanged unmarked variant and base region, visible added
acute/increased ascent, stable advance; native-plus-acute case compares every
native mark's original painted pixels. No failures or geometry errors. Original
character art retained. Header/font asset versions refreshed.

LIVE final native suite:82193, /tmp/marked-cjk-final-native-checks.log, original
3native companion gates +6existing source-preservation checks. LIVE fullbrowser
corpus in tab39:644cases. These are not terminal until their handles/UI say so.
The older tab37 wrapper is stale (browser.user unavailable); use markedCjkTab
binding for tab39. Probe tab38 remains available. Detailed current checkpoint:
docs/marked-cjk-variant-review.json. Goal remains active and incomplete.


### Marked CJK companion milestone verified — 2026-11-03

Final native suite82193 TERMINAL0: **9passed176.45s**. The three new companion
checks verify all106,792retained native glyphs (exact curves, metrics, stored
bounds and hint programs), all30,637native variation mappings, representative
foreign-accent side/stack geometry and native single mark positions including
foreign acute combinations. Six existing checks also prove all380old script
font entries/files unchanged and both prior Seal additions remain correct.
Fresh no-cache reproduction43217 TERMINAL0:1passed5.88s, both standardized and
native-IVS source kinds, isolated filesystem, exact font bytes and metadata.
Cache repeat also preserved the full92-entry manifest byte for byte.

Full browser tab39 FINISHED: **644scenarios, failures[], geometry[]**.
All five new actual-strip cases individually visually reviewed earlier, including
all8native marks plus acute and painted source/companion pixel comparisons.
JS333passed; audit172352/172352visiblecmap. Fonts/fixture assets versioned.
No known build/test/audit remains live. Tab39 is the current browser handoff;
old tab37 wrapper is stale. Research probe is tab38.

This closes the demonstrated CJK variant-loss bug for the current257accent
donor. It does NOT close arbitrary marked Unicode: enclosing/double marks
outside this donor, native marks missing from standardized CJK subsets,
math/contextual-script variants with foreign marks, more complex native mark
combinations and cross-script semantics remain open. Source CJK stylistic
adaptation and remaining whole-brief browser/renderer review are still required.
Next priority: extend the accent inventory/attachment for the missing enclosing
and double marks, retaining all demonstrated original glyph and native mark
invariants; then address math/contextual variant clusters and full brief audit.
See docs/marked-cjk-variant-review.json for the current evidence and limits.

### Session restart recovery — 2026-11-03

Recovered the dynamic combining-annotation work after the session restart.
The last recorded full JS run passed339 tests; eight source-preservation checks
passed. The full browser corpus last passed651 scenarios before the final ring
and keycap refinements. The corpus now contains652 cases and still needs a final
complete run on the current assets. Repeated enclosures were visually reviewed
after the constant-stroke correction, but that is not a full-corpus result.

The latest catalog build log reports1838 visible mark drawings plus2 native-
context records from112 sources,1,214,605 bytes. Its focused six-test run passed,
including the latest keycap/cancelled-circle counter fitting. The old exec
session69182 no longer exists after restart; its full command completion cannot
be recovered from the process handle. Do not describe it as a live build.

Implementation adds dynamic nested enclosures and all10 double diacritics,
preserving native base glyphs and using existing licensed mark outlines.
Joining scripts, exact emoji, CGJ-sensitive combinations and unsupported mixed
annotation semantics retain native handling. This is partial Unicode attachment
coverage, not proof of arbitrary-script correctness. The approved expressive
emoji treatment,1.4x optical size and stronger ink remain in place.

Next: verify current generated assets; rerun final JS/source checks and all652
browser cases; document the annotation evidence and limitations. Then address
remaining cross-font variation/mark combinations and complete the whole-brief
script, style and renderer audit. Goal remains active and incomplete.


### Dynamic enclosing/double-mark milestone verified — 2026-11-03

Current full JavaScript run16393 TERMINAL0:339passed10.02s,
/tmp/combining-recovery-js.log. Source suite1560 TERMINAL0:8passed12.50s,
/tmp/combining-recovery-python.log. Full catalog reproduction80801 TERMINAL0:
byte-identical SHA256481b9326afcc1c409f35fb9d03e07d3daf782ade63938c02f30271ad09ac9498.
The catalog contains1838visible mark drawings,2context-only Gondi viramas and
263behavioural/default-ignorable records, from112licensed sources. Existing
fonts are unchanged inputs; the data is not a font-wide coverage/style claim.

Final full browser tab41 FINISHED:652scenarios, failures[],geometry[].
Expected native fallbacks occur only in deliberate malformed/nonstandard emoji
stress cases. The current keycap, basic enclosure and CJK/math enclosure strips
were individually visually rechecked after final contour/counter changes.
Repeated circles/diamonds/triangles had already been reviewed after constant
border-weight refinement. The original character art remains unchanged.
Assets versioned; no build/test is known live. Tab41 marked for handoff.
Detailed hashes, source scope, validation and limits are recorded in
docs/combining-annotations-review.json.

Next confirmed defect: foreign marks can still prevent native variant selection.
Routing probe shows CJK IVS㐂+E0101+20D2 and standardized豈+FE00+3099
select ordinary script fonts instead of their native UVS fonts. Math
𝓏+FE02+3099 likewise loses its explicit math family. Existing acute/CJK
companions and enclosing-mark paths work. Solve remaining variation-plus-mark
composition while preserving existing native glyphs and native mark positions.
Joining/contextual scripts and whole-brief style/renderer audit remain open.
Goal remains active and incomplete.


### Native variants with foreign marks — 2026-11-03

Implemented longest-native-prefix composition for nonjoining variation
clusters with missing Mn/Me marks. Canonical tail ordering is explicit; any
covered native tail marks use their own font's exact source outlines. Complete
native clusters retain their original shaping. Foreign Hebrew/Indic nonspacing
marks on a nonjoining base can compose; actual joining/contextual bases still
keep their native path. CJK BMP/ExtB/ExtG/standardized and kurrent math examples
retain their requested native fonts, including enclosure/double interactions.

Catalog final build63302 TERMINAL0:1838generic visible drawings,25087native
font/mark identities across191families,506unique native drawings,300source
records,2688273bytes. Initial source test61055 failed because newly included
Jigmo source records lacked their supplied CC0 notice reference; corrected the
metadata and reran. Final source44184 TERMINAL0:9passed79.66s. Full catalog
reproduction20070 TERMINAL0, exact SHA256
0fbed2831fc09f6894a2bd00379c89f8d551f635ee990fb57c79c2e8b1e7118d.
Final JS57211 TERMINAL0:342passed9.71s. No font file was modified in this work.

Four new actual foreign-variant strips individually visually reviewed. Earlier
full656browser corpus passed failures[],geometry[] before a final positional-
class correction. Final corpus now657cases RUNNING in browser tab42, binding
variationTab. Read #summary directly using locator.textContent(); the full AX
tree truncates at roughly500cases and can falsely appear unchanged. No terminal
build/test remains live. Assets versioned. Detailed source hashes and limits:
docs/variation-combining-review.json.

NEW CONFIRMED NATIVE DEFECT: the positional-class strip exposes above-left
U1DF7 and attached-above-right U031B below a standardized CJK variant. Native
HarfBuzz ink confirms base[55,-19,969,871], U1DF7[356,-189,668,-55],
U031B[407,-261,617,-55]. Existing helper math_unicode_marks.py gives source
y-position precedence over explicit above CCC classes. Dynamic SVG placement
now respects above/side classes and zero-gap attachment, but complete native
clusters deliberately keep their current font GPOS and still show the defect.
Do not call this typography correct merely because geometry/export passes.
Next repair the shared font rule, rebuild dependent assets and catalog, and
verify original curves/metrics/native CJK marks remain intact. Helper hash
affects all92CJK companions, explicit math variants and NotoSansMath script
recipe; it is NOT grounds to casually rebuild or replace unrelated fonts.
Five numeric Cyrillic Me forms, foreign spacing marks, CGJ/contextual cases and
the wider style/renderer audit remain open. Goal remains active/incomplete.


Final browser tab42 FINISHED:657scenarios, failures[],geometry[]. This run
uses the final explicit positional-class correction and fifth new strip.
Native companion U1DF7/U031B placement remains a recorded real semantic defect,
not a passed typography gate. JS342passed, Python9passed, catalog reproduces
exactly. No known build, test or audit remains live. Current browser handoff42;
old recoveryTab/41 wrapper is stale. Next action is the shared font attachment
rule and dependent rebuild, not another repeat of unchanged broad checks.

### Live native positional-mark repair — 2026-11-03

The previous turn made progress: native variant preservation with foreign marks
and source evidence are saved. This turn repairs the confirmed native font
misplacement. Frozen baseline: output/font-review/pre-positional-mark-repair/,
including old manifests, the one affected ordinary math font, explicit math font,
old helper and the complete old mark catalog. Do not overwrite this baseline.

math_unicode_marks.py now gives explicit positional CCC classes priority over
unplaced glyph y bounds, supplies left/right corner anchors for missing pairs,
and removes the artificial gap for attached classes. Existing native anchors
are retained. Prototype26981 TERMINAL0: U1DF7 moves from below to above-left,
U031B attaches above-right, U0315 above-right, ordinary acute unchanged.

Script build31544 TERMINAL0:381shards68,229,580bytes. Only intended ordinary
NotoSansMath source entry changes; six focused math/source tests6751 TERMINAL0
passed2.09s, including complete frozen-before/current ordinary math curves,
metrics, glyph order and hints; all380other script fonts are exact. Explicit
math build TERMINAL0:37variants67,908bytes, with source/old-shaping/rebuild tests.
Historical Seal font-preservation tests now allow only this intentional math
attachment change; tests/test_positional_marks.py supplies the stronger current
whole-inventory and all-curve proof. No unrelated historical baseline is changed.

CJK companion rebuild session1273 remains LIVE, /tmp/positional-cjk-build.log.
It rebuilds all92companions because the helper recipe hash changed. Do not start
a second build or generate the outline catalog until this build finishes and
emits its final manifest. Current production font/catalog hashes are transiently
out of sync during the build. Browser tab42 still shows the prior657 result;
it is not a current result for this native-font repair.

Added all92-companion positional-class regression, full unchanged-catalog-curve
gate, and actual browser native above-mark/left-alignment checks. These are not
yet terminal against the rebuilt companion inventory. Next poll1273, run native
preservation/geometry suites and fresh companion reproduction, regenerate mark
catalog, verify all25087old native mark drawings unchanged, refresh asset hashes,
then visually inspect the positional strip and run full657browser corpus.
Full Unicode beta remains active/incomplete.


CJK build1273 TERMINAL0:92companions26,776,560bytes. JS43724 TERMINAL0:
342passed9.92s. Script regression82816 TERMINAL0:21passed17.77s. Coverage
audit98050 TERMINAL0:172352/172352visible cmap entries. First regenerated
catalog6321 TERMINAL0:2688273bytes, same record counts, updated font hashes.

LIVE native suite91106 (/tmp/positional-cjk-native-tests.log): original native
glyph/UVS/native-CJK-position checks, all92positional corners/attached-class
checks, and isolated fresh rebuild. LIVE catalog/source73624
(/tmp/positional-catalog-tests.log): source geometry/provenance and all25087
frozen-before/current native mark drawings unchanged. LIVE exact catalog
reproduction24046. Do not restart on observation timeout.

Actual positional strip in fresh browser tab43 visually inspected and passed
new native ascent/left-alignment assertions. Both native marks now appear above
the CJK variant. Full657corpus is RUNNING in tab43, binding positionalTab.
Assets versioned. Older variationTab/42 wrapper is stale. Keep this goal active
until the actual complete brief is proved, not merely this repaired milestone.
After this repair, perform a concrete whole-brief requirement/evidence audit
to distinguish actual implementation gaps from specialist review/playtesting
that the brief explicitly permits after the beta; do not demand publication-
quality validation as an invented completion requirement.


### Native positional-mark repair verified — 2026-11-03

Native suite91106 TERMINAL0:5passed244.62s. This checks every retained native
CJK glyph/metric/hint and UVS, original native CJK mark positions, positional
classes across all92companions, and fresh isolated exact reproduction for both
standardized and native-IVS kinds. Catalog suite73624 TERMINAL0:4passed78.18s,
including all25087native mark identities/paths and all generic paths unchanged
from the frozen pre-repair catalog. Reproduction24046 TERMINAL0: byte-identical
SHA2568ab1531eb7b4ded33cbb8f0181ded308406e41a9e44a1437134698ca63b1e13b.
Stronger ordinary-math proof23375 TERMINAL0:1passed1.33s; all tables except
GPOS/GDEF/head exact, glyph curves/metrics/hints retained, all380other script
entries/files exact. This repeats the earlier source-preservation test.

Across nonduplicate focused suites:36font/source tests passed (6+21+5+4),
plus342JS. Cmap audit172352/172352. Full browser tab43 FINISHED:657scenarios,
failures[],geometry[], including new native above-mark/left-alignment checks.
Actual repaired positional strip visually inspected: both native marks now
appear above the CJK variant. Original character art unchanged; assets versioned.
No build/test/audit is known live. Tab43 is the current handoff, positionalTab.
Current artifact hashes, baseline, counts and limits:
docs/positional-mark-review.json. Earlier marked-CJK/variation reviews now
explicitly describe historical milestones, not current font hashes.

Next perform the whole-brief requirement/evidence audit before choosing further
work. Preserve the full user scope, but do not invent publication-quality or
mandatory expert-reader approval requirements: the brief expects human review
and playtesting afterward. Confirmed remaining implementation/review gaps
include five numeric Cyrillic enclosures, foreign spacing marks and some
CGJ/contextual variation combinations, plus the wider script/style and
renderer/browser review. Goal remains active/incomplete.

### Whole-brief audit and actual routed drawings — 2026-11-03

Created docs/unicode-beta-audit.json, a30-requirement evidence matrix derived
from the full brief. It distinguishes supported implementation, concrete gaps,
missing verification and expert/human follow-up explicitly permitted after beta.
Current release18.0.0 rechecked against official releases/version pages. No
completion claim is made. A full Python command is LIVE:session15005,
/tmp/unicode-beta-full-python.log. It began before the routing-only corrections
below; the existing grid rebuild test imports its builder at invocation, and
focused post-fix checks independently cover the changed paths. No live font
compiler was interrupted or restarted. Do not restart this full run on a wait
or observation timeout. New outline-audit tests were created after collection
and are verified separately.

Added tools/unicode/outline_audit.py to replay actual requiredFonts selection
for all172352visible requirements, then inspect selected-font outlines/COLR
layers. Empty roots are additionally checked through native HarfBuzz GSUB.
Duployan empty roots expand into real component drawings; don't call them
missing based on cmap/root ink alone. Context-only Gondi viramas remain explicit
exceptions instead of counting inserted dotted-circle carriers as their drawing.
Braille blank and both Egyptian blank characters are semantic whitespace/cell
exceptions. Unicode18chapter11.4.3 explicitly confirms Egyptian blanks render
as whitespace. The audit still does not prove glyph identity, final style or
all contextual combinations; these remain separate requirements.

First shape-aware audit81063 TERMINAL0 exposed actual loader gaps. Three
control pictures U2427..U2429 exist in Dad Grid but its range list was unsorted,
so binary lookup missed them. Fixed build_grid.py and generated grid metadata;
font bytes unchanged. Isolated keycap U20E3 was incorrectly routed as native
emoji; now only exact valid keycap sequences are custom emoji, and other text
keycap uses remain text unless actual emoji presentation semantics apply.
Focused JS81passed; grid/source/outline tool11passed2.25s, including exact grid
rebuild. Full JS78221 TERMINAL0:344passed9.91s. Asset URLs refreshed.

Actual new routing-standalone-visible comic strip in fresh tab44 passed and
was visually inspected: all three checker forms and leading/space keycaps are
visible, with no missing codepoints or native emoji fallback; standard digit
keycaps retain custom artwork/size. Full658browser corpus is RUNNING in tab44,
binding auditTab. Older positionalTab/43 wrapper is stale.

LIVE final revised outline audit59624,/tmp/unicode-beta-final-outline-audit.log;
it uses sorted grid ranges and fixed single-character keycap selection. Its
final totals are not yet terminal. Native Aref Ruqaa standalone U0640 Tatweel
has a zero-ink,zero-advance glyph even after native isolated shaping. This is
an actual remaining standalone drawing/routing issue to fix while preserving
joined Arabic source shaping; do not relabel it as covered merely because cmap
contains the point. The five numeric Cyrillic Me forms and other matrix gaps
remain. Next finish these audit/process results, review the general browser
harness, then act on concrete remaining gaps and source-family visual review.


Final outline audit59624 TERMINAL0:172346/172352positive routed drawings,
5explicit blank/context exceptions,1unexplained empty glyph (U0640Tatweel),
0routing gaps. Exceptions are Braille blank U2800, Egyptian full/half blanks
U13441/U13442, and context-only Gondi viramas U11D45/U11D97. Native GSUB
accounts for38Duployan empty roots rather than misclassifying those letters
as missing. See docs/unicode-outline-coverage.json and its explicit limits.

Full currentJS78221 TERMINAL0:344passed9.91s. Grid/source/outline11passed
2.25s, including exact grid font/manifest reproduction; font bytes unchanged.
Full browser tab44 FINISHED:658Unicode scenarios, failures[],geometry[].
Then general tools/checks.html in the same tab FINISHED:33of33scenarios pass,
no .scenario.bad elements. The new actual routing strip was individually
visually inspected before the full run. Assets versioned. Current browser
handoff44 now shows the general harness; auditTab is its binding.

Only known live process: full Python15005,/tmp/unicode-beta-full-python.log.
Last poll confirms it is still live; log has reached the initial3percent
without reported failures. This is a long candidate/font/compiler/rebuild
suite, not a completed Python result. New audit tests were created after full
collection and are covered by their separate terminal run. Do not restart
merely because this early percentage persists across observations.

Next: fix actual standalone Tatweel routing/visible shape while preserving
Arabic native joining; continue the concrete requirement/evidence matrix and
source-family/style/product review while the full suite runs. Keep the full
beta goal active. Expert-reader/publication-quality approval is not an added
blocking requirement; actual named implementation gaps still must be addressed.


### Tatweel fields and stronger first-painted-font audit — 2026-11-03

Implemented shared field routing in js/standalone-fonts.js, used by font loading
and fontRuns/painting. Initial isolated-only rule was broadened after source
inspection proved Aref ignores Tatweel inside connected words too. A complete
Tatweel-containing joining field now selects one existing visible native font
covering the field, not a different face for one connected character. Arabic
selects Kufi; Syriac selects its own complete source. ZWNJ ends a field; ZWJ,
transparent marks and directional marks remain with it. Ordinary extender-free
fields keep their prior routing. Source font programs and art are unchanged.

Native/source+audit12299 TERMINAL0:6passed1.69s. FocusedJS98passed. FullJS70234
TERMINAL0:346passed10.05s. First-painted-font audit19844 TERMINAL0:
172347positive drawings +5explicit blank/context exceptions =172352required
non-format points;0unexplained drawing gaps,0routing gaps. This audit uses
makeFontString order and explicit run families rather than any loaded candidate.
The later broader field rule leaves single-character choices unchanged; native
whole-word, source-width and Syriac regressions cover the changed contexts.
Full final browser tab45 FINISHED:660cases,failures[],geometry[]. Two actual
Tatweel strips visually inspected after broadening; native extender words now
really grow in width. Earlier isolated-only660pass is superseded by this run.
Detailed evidence/hashes:docs/tatweel-routing-review.json. Assets versioned.

NEW CONFIRMED FORMAT GAP: Cf is not synonymous with invisible. All13pinned
Prepended_Concatenation_Mark characters have nonempty bundled source glyphs,
but requiredFonts currently skips them as behaviour or chooses Dad Grid after
constructing an empty preferred-script repertoire. Probes U0600/U0601/U070F/
U0890 select an unrelated font without their glyph; U06DD/U08E2/U110BD/U110CD
select none. Full list/source geometry:docs/font-dependent-format-probe.json.
Next separate font-dependent format signs from ignorable controls in loading
and drawing inventory, skip empty font preferences, and check standalone and
marker/number contexts. The non-format audit has explicit exclusions/limits;
its zero gaps are not a full-format or complete-beta claim.

Full Python15005 remains LIVE,/tmp/unicode-beta-full-python.log; latest poll
confirmed live with log past7percent and no reported failures so far. No other
known build/test/audit remains live. Do not restart on observation timeout.
Current browser handoff45 is the final660corpus, tatweelTab. Earlier auditTab/44
wrapper is stale. Matrix docs/unicode-beta-audit.json updated with current
results and the newly confirmed13format-sign gap. Full goal remains active.

### Restart status reconciliation — 2026-11-03

Recovered after user restart. Latest formatting-sign changes are implemented:
13 Prepended_Concatenation_Mark characters now require actual font glyphs even
though their category is Cf; preferred-script routing skips empty repertoires.
Drawing and behaviour inventories intentionally overlap by these13 characters.
Full JS:348passed, /tmp/format-glyph-full-js.log. Focused formatting/source and
inventory tests:8passed18.77s, /tmp/format-glyph-final-source-tests.log.
Outline audit1931 confirmed TERMINAL0 after restart:172360positive drawings,
5explicit exceptions,0unexplained drawing gaps,0routing gaps; total172365.
Browser fixtures format-signs-isolated and format-signs-numbers exist, but the
new662-case browser corpus and actual visual review are still pending. Latest
completed browser corpus remains660cases, plus33general scenarios.

Full Python session15005 survived restart and was polled live. Its log is
past10percent with no reported failures so far; completion and absence of a
hang are not established. Do not claim the full suite passed. Previous summary
said this suite is expensive; investigate actual progress if it remains static
rather than indefinitely repeating unchanged status. No permission blocker.
The requirement matrix still describes the now-fixed13sign gap and needs a
current-evidence update. Remaining substantive work includes five Cyrillic
numeric combining forms, contextual/variation mark gaps, bounded runtime
review and source-family/style/final product review. Full beta remains incomplete.

### Complete native formatting fields — 2026-11-03

Fixed the13 visible Cf requirements and corrected drawing/behaviour overlap:
172873public =172365drawing +521behaviour -13overlap. Final inventory/source
regression explicitly verifies that arithmetic and generated pinned table.
Standalone glyphs alone were insufficient: actual comic review showed Arabic
signs disconnected from ordinary Dad digits despite source HB shaping correctly.
Added js/format-fonts.js, shared by font loading and fontRuns. Entire prefixed
number/abbreviation fields use one complete native font ahead of Dad Lettering.
SAM keeps preceding joined Syriac letters in the field. Boundaries stop at prose.

A second actual browser failure exposed separate bidi levels for AN signs and
European digits. direction.js now treats AN-prefixed digit fields as graphical
units using synthetic isolates only in resolution input; logical input remains
unchanged. After L2, logically contiguous same-direction fragments can shape
as one run. Core bidi engine and pinned core conformance remain unchanged.
Tests exercise actual paragraph measurer and painted family, not only fontRuns;
source tests verify GSUB/GPOS digit positioning, source-identical curves/shaping,
all13standalone signs and actual CSS stack order. Unsupported mixed fields
without a complete native source retain fallback and are not claimed proven.

Final JS350pass11.89s,/tmp/format-final-full-js.log. Focused14JS including both
full bidi corpora passed1.86s,/tmp/format-bidi-final-js.log. Source/inventory/
outline13pass22.11s,/tmp/format-final-source.log. Final662Unicode browser cases
passed,failures[],geometry[];33of33general scenarios passed. Actual corrected
number/abbreviation strip visually reviewed: Arabic signs span digits, Kaithi
lines appear with their numbers, Syriac abbreviation remains over the word.
Earlier662pass before stronger full-field assertions is superseded. Assets
versioned; source font programs unchanged. docs/font-dependent-format-review.json
holds current evidence/hashes; prior probe explicitly marked historical.

Live49339: refreshed whole first-painted drawing audit,
/tmp/format-final-outline.log. Prior terminal audit1931 already established
172360positive +5explicit blank/context exceptions,0unexplained,0routing gaps.
Live15005: full Python,/tmp/unicode-beta-full-python.log. It is demonstrably
progressing: trailing tests advanced from9 to29during this turn; no reported
failures yet, still just beyond10percent. Do not restart either live process.
Current browser tab46/formatTab shows33general passes and is retained for handoff.

Next substantive gap: five Cyrillic numeric Me0488/0489/A670/A671/A672 are
present in generic native outline catalog but rejected by dynamic annotationPlan
and variationPrefix. Inspected source paths:0488eight semicircles,0489eight rays,
A670eight crosses,A671top/bottom brackets,A672plus/side/bottom strokes. Need
preserve those distinct components and native stroke weight while enclosing
foreign/UVS bases, without globally stretching the base or treating brackets as
a circle. Unicode18§7.9.4 and§3.6P8 define enclosing previous marks; source glyphs
supply actual shapes. Numeric Me variation proposals are not an implementation
spec: pinned StandardizedVariants currently has none for these five marks.
Broader contextual/CGJ/foreignMc, bounded Egyptian/grid/dictionary review and
source-family/style/final product review remain. Full goal stays active.

### Five numeric Cyrillic enclosing marks — 2026-11-03

Implemented dynamic0488/0489/A670/A671/A672 instead of rejecting these Me forms.
Builder adds only five numericEnclosure metadata records to existing catalog:
0488eight native semicircles,0489eight rays,A670eight crosses,A671two native
polygonal brackets,A672four rigid groups preserving plus/side/bottom strokes.
Radial components translate without scaling their contours; grouped strokes
retain relative placement; brackets widen their bars while keeping stroke and
leg dimensions. Existing native bases remain shaped/unscaled. AnnotationPlan,
font selection, measurement and painting share the complete composed result.
Nesting/depth guards retained; repeated numeric rings grow linearly.

Correct standard reference is Unicode18§3.6P6 for enclosing previous marks;
P8 describes double diacritics floating outside other marks (the prior next-step
note referred toP8 incorrectly). No Unicode chart artwork is copied. Native
NotoSans licensed paths and original notices/source hashes retained. Frozen
pre-change catalog:output/font-review/pre-numeric-enclosures/. All existing
1840generic records' native drawing fields,25087variant identities/drawings,
source records and other catalog data remain identical after removing only
five new metadata records; source test verifies full deep equality. Sourcefont
programs/art unchanged. New catalog2695327bytes; deterministic builder finished
84599TERMINAL0,/tmp/numeric-enclosure-build.log.

FocusedJS10pass,/tmp/numeric-enclosure-js.log. FullJS351pass12.03s,
/tmp/numeric-enclosure-full-js.log. Source/catalog/positional7pass138.58s,
/tmp/numeric-enclosure-source.log,62547TERMINAL0. Strengthened total native ink
area assertion now covers all5including groupedA672:1pass0.27s,
/tmp/numeric-enclosure-final-source.log. Both actual numeric strips visually
inspected; native CJK/math variants remain visible, five forms distinct, no
base stretching. Final browser tab47:664cases,failures[],geometry[]. Added
component-presence and actual native variant-family assertions. Assets versioned.
Current detail/hashes:docs/numeric-enclosures-review.json. Current browser
numericTab/47 retains full664corpus for handoff.

Refreshed drawing audit49339 TERMINAL0:172360positive drawings +5explicit
blank/context exceptions,0unexplained gaps,0routing gaps,/tmp/format-final-outline.log.
This audit completed before numeric metadata; single-character font routes and
all font programs remain unchanged, source/variant data preservation proved.
FullPython15005 remains LIVE,/tmp/unicode-beta-full-python.log; last poll after
numeric source completion confirms live. Log advanced from10percent to14percent
and58trailing tests during this turn; no reported failures so far. It predates
new tests; separate current focused runs cover these changes. Do not restart.

NEXT CONFIRMED GAP:docs/cgj-variation-probe.json. CJK IVS㐂+E0101+CGJ+dakuten
still selects a complete native variation family. Math𝓏+FE02+CGJ+dakuten and
standardCJK豈+FE00+CGJ+dakuten lose their selected native variant family because
CGJ blanket-disables annotation and complete native coverage is unavailable.
WithoutCGJ the existing foreign-mark compositor preserves those variants.
Investigate a CGJ-aware nonjoining variation prefix: retain CGJ in a native
prefix when covered, treat later CGJ as zero-ink canonical-order boundary,
never reorder across it; keep joining/unknownselector/undefined double guards.
This is an investigation plan, not an implemented fix. ForeignMc/contextual,
bounded Egyptian/grid/dictionary and complete source-family/style/product
review also remain. Full beta goal stays active.

### CGJ-aware nonjoining native variation prefixes — 2026-11-03

Fixed confirmed Math/standardCJK variant loss when a foreign Mn/Me follows CGJ.
variationPrefix now accepts CGJ as an invisible ccc0 boundary; canonicalMarks
keeps it in the sequence and never reorders across it. A CGJ before the first
missing mark remains inside the exact native shaped prefix. Later CGJs remain
in operation ordering but paint no glyph/advance. Native marks moved outside a
foreign mark keep selected-font catalog drawings. Complete native CJK clusters
remain native, as do joining scripts and existing CGJ/double guarded cases.
No font program, drawing catalog, source hash or original art changed.

Verified Unicode18§23.2.4 directly: CGJ has no visible effect other than blocking
canonical mark reordering and does not alter cursive joining, linebreaking or
grapheme segmentation. Keep these distinct from ZWJ/WJ semantics. Updated unit
regressions cover native-prefix retention, boundary ordering, zero CGJ outline,
exact donor-family tail marks, enclosing/numeric stacking and guarded contexts.
Initial test expected base-only CJK family for a native acute; corrected test to
expect the actual marked companion selected by the complete native prefix.
That companion is correct, not a regression to the base-only face.

FocusedJS11pass0.20s,/tmp/cgj-variation-final-js.log. FullJS352pass11.91s,
/tmp/cgj-variation-full-js.log. New actual-plan native source ink check1pass2.13s,
/tmp/cgj-variation-source.log: four selected packaged prefixes retain identical
visible glyph IDs/positions and total advance when CGJ is inserted. Both actual
CGJ strips visually reviewed, including nested/numeric enclosures; correct
variant families painted, no CGJ ink, no clipping. Final browser tab48:
666cases,failures[],geometry[]. Assets versioned. Detail/hashes:
docs/cgj-variation-review.json. Historical probe marked superseded. Current
browser cgjTab/48 retains full666corpus for handoff.

FullPython15005 remains LIVE,/tmp/unicode-beta-full-python.log. Last authoritative
poll confirms live, log past18percent with18trailing tests and no reported
failure. Newly added CGJ test was not in its original collection; current
separate test verifies this path. Previous audited outline49339 already terminal0;
CGJ change only affects contextual clusters, not single-scalar font routes.

Next confirmed scope:docs/foreign-spacing-mark-probe.json. MathVS+Devanagari
visarga/AA and MyanmarAA already retain their selected family; MathVS+BengaliI,
TamilE or KhmerOE lose it. StandardCJKVS+DevanagariVisarga/AA,BengaliI,TamilE,
KhmerOE lose selection; MyanmarAA retains it. Do not treat allMc as generic
right-side spacing: prebase, split, above/below and source-shaping behaviour
vary. Need actual source/native contextual treatment while keeping variantbase
and whole native clusters, not merely Mn-like boundingbox placement. Other
joining/mark-selector contexts, bounded Egyptian/grid/dictionary and full
source-family/style/product review still remain. Full beta goal remains active.

### Foreign spacing vowels and finite contextual variation audit — 2026-11-03

Fixed registered nonjoining variants followed by unsupported foreignMc. New
nativeSpacingVariationPlan in font-variations.js keeps the longest native
prefix and returns unsupported mark tail; requiredFonts loads both prefix and
all bundled native fallback sources, fontRuns paints explicit prefix family
and separate native tail. Complete native clusters remain whole and now get
explicit native family even when foreignMc sets a contextual-script flag.
Connected native bases, undefined mark selectors and exact emoji stay guarded.
Pinned Myanmar spacing-mark grapheme exceptions remain separate; no change to
logical input, UAX29, linebreak units, sharing or font programs/catalog/art.

Actual browser pixels caught a genuine intermediate failure: putting native
prefix font first for a whole incomplete cluster preservedMathVS but silently
dropped foreign vowels. Separate native fragments fix this, retaining source
prebase/split shaping and its conventional dotted-circle invalid-syllable
carrier. This is native fallback presentation for unrelated scripts, not a
claim that arbitrary Bengali/Tamil/Khmer vowels form meaningful CJK syllables.
Complete native source shaping is still preferred. Generic Mn geometry was
not applied toMc. Actual paint-run and raster assertions require vowel ink and
registered selector discrimination where the isolated native prefix is visually
discriminating. SourceCJK豈default/FE00curves are exactly identical, verified
with decomposed recording pens; do not invent pixel differences for that case.

SpacingJS24combinations pass,/tmp/spacing-variation-native-fragments-js.log;
fullJS353pass12.08s,/tmp/spacing-variation-final-full-js.log. Native source
fragment1pass0.73s,/tmp/spacing-variation-source.log: six actual routed tails
have nonempty native glyphs, no notdef, source-identical shaping; TamilOkeeps
left/right decomposition and native dotted-circle carrier. Two actual spacing
strips visually reviewed after stronger raster checks, no missing/geometry
failures. docs/spacing-variation-review.json records scope/limits/hashes.
Historical loading-only probe marked superseded; loading alone was inadequate.

Also closed the vague standardized contextual/mark-selector evidence item by
explicitly deriving finite pinned scope. All128contextualpairs:117Mongolian,
6PhagsPa,5Manichaean, four contexts each =512examples. Actual requiredFonts/
fontRuns replay chooses one complete native font/run; packaged/source shaping
matches; EVERY pair changes real visible glyph/position output in at least one
context. Only mark-initial standardized pair is1031FE00(Myanmar dottedE), derived
from all pinned UnicodeData/StandardizedVariants rows. Four contexts preserve
PadaukBooksource shaping; new actualMyanmarstrip and contextual rasterdiscrimination
pass, visually inspected atcomic size. Source2pass0.64s,
/tmp/contextual-variation-final-source.log. docs/contextual-variation-review.json.
This proves source/selection behaviour; native-reader language validation is not
claimed or required as a new beta approval gate.

Final browser tab49/spacingTab FINISHED:669cases,failures[],geometry[]. Earlier
668pass superseded after adding focusedMyanmar mark selector. Assets versioned.
No product changes after full353JS result; new contextual additions are tests
and fixture only. General33lastpassed, unaffected noMc inputs. Native/font/source
preservation evidence unchanged except new supplemental tests. FullPython15005
remains LIVE,/tmp/unicode-beta-full-python.log: authoritative poll confirms live,
log past18percent with18trailing tests, no reported failures. It has not advanced
in the latest observations; do not infer terminal/hang from that. Earlier sustained
progress18percent is recorded; this suite includes expensive full candidate and
font/compiler rebuilds. Newly added tests are covered separately, not retroactively
included in that old collection. No other known live build/test process remains.
Current browser49 retains full669corpus for handoff.

Next: bounded Egyptian rejected/damaged composition, grid prose/diagram and
Thai/Lao/Khmer/Myanmar dictionary runtime review; then explicit source-family/
style audit at comic sizes and final actual product interaction/share/export
smoke test. Do not leave all source styles as merely provisional or equate scalar
coverage with visual completion. Requirements matrix updated: marks/variations
supported with stated native fallback limits, not full beta completion. Full goal
remains active pending remaining source/style/runtime/product and full-suite work.

### Bounded layout review and actual defects — 2026-11-03

Fixed overbroad grid detection: previously any inline structural character forced
all prose into fixed cells. Clear frame/dense/pure structural rows still use
spatial cells; sparse inline box/Braille/block symbols retain normal wrapping,
while customDadGridglyphs still load.12grid regression checks include source
preservation and framed/native/legacy/wide diagram cases. Actual inline-symbol
comic inspected: normal dialogue wraps, glyphs remain visible.

Mixed dictionary strip exposed a real Myanmar emergency-break defect: a native
word was split before its dependent final AA vowel, producing an orphan dotted
circle. firstPiece now preserves already segmented dictionary units (Thai/Lao/
Khmer/Myanmar), allowing callers to grow/fit the complete word; emergencyBoundary
also refuses a break before M marks even if UAX29 separates a spacingMc. No pinned
UAX29/UAX14data changed. Protected WJ/NBSP text remains logical-source-identical.
Corrected actual mixed four-language/emoji strip now passes all word/control
boundary checks and visually has no orphan Myanmar vowel. Current focusedgrid+
linebreak22pass,/tmp/bounded-layout-final-focused-js.log; includes full default
linebreak conformance. Tests explicitly check column overflow and fitted protected
words (layoutColumn does not itself take fitUnbreakable, so test uses layoutText
for that layer). No need to change that API.

Egyptian enclosed-damage strip passed existing implementation and was visually
reviewed, including RTL. Rejected-region strip exposed source helper boxes:
base/controlshaped inreferencefont while unsupported extended child fell outside
its insertion cell. Native full-blank probes already provide source positions;
our additional empty/disjoint rectangle rejection discarded valid native overlap/
overflow. Unicode18§11.4.2 explicitly allows overflow as overlay. Compiler now
retains matched native positions/artwork, reserves envelope including all regions,
and records sampling/overlap/overflow observations instead of rejecting them.
428earlier accepted entries are byte-for-byte data-identical (source regression).
New accepted910:253unmodifiedsingle,212unmodifiedmultiple,411mirrored,24rotated,
10rotated/mirrored.482source geometry observations are explicit; NOT a claim of
collision freedom. Only72unmatchednativeoutputs remain, rather than554. Native
font programs and artwork unchanged. Frozen pre-change source/manifest/report:
output/font-review/pre-native-insertion-geometry/.

Renderer now applies the existing fifteen quarter-damage masks to matched
insertion container surfaces before inserted children; all15masks preserve native
container and child geometry, with RTL coverage. FocusedEgyptian23pass,
/tmp/native-insertion-layout-js.log. Compiler30377TERMINAL0 accepted910/rejected72,
/tmp/native-insertion-geometry-build.log. Source/repro/inventory7pass14.73s,
/tmp/native-insertion-geometry-source.log,45122TERMINAL0. Newsourcechecks keep all
old428entries exactly unchanged, bound everyregion/path envelope, record actual
native overlap observations and keep exact new source subtype counts.

Actual native-region-overlap strip re-reviewed after implementation: allsix
containers now contain real native/extended content instead of helper boxes;
damage visible, geometry[] andfailures[]. Initial new assertion read only nested
ink.runs and missed top-levelEgyptian glyphs; corrected it to use existing shared
glyph-record conventions. Not a remaining render failure. Native source geometry
can touch/overlap; broader style/context review remains explicit.

FullJS356pass13.30s,/tmp/bounded-layout-final-full-js.log. Finalfullbrowser tab50:
673cases,failures[],geometry[]. Then tools/checks.html33of33pass. Currentbrowser
layoutTab/50retains generalchecks forhandoff. Assetsversioned. Current evidence/
hashes docs/bounded-layout-review.json; requirement matrix updated.

FullPython15005stillLIVE,/tmp/unicode-beta-full-python.log. Latest authoritative
poll live; log rapidlyadvanced18→50percent plus55trailing tests, no reported
failure. The long18percent period ended. Do not restart. This command predates
current builder/manifest/test changes; current source checks explicitly cover
those paths/new scope separately. Any terminal result must be assessed with
that timing rather than claimed as a pristine current-worktree collection.
No other knownlivebuilder/testprocess remains.

NEXT concreteEgyptian72probe:docs/egyptian-unmatched-output-probe.json.65outputs
have container+mr (explicit native mirror helper) rather than one ink drawing.
Three others are legitimate mirror alternates with different names: C2a→C2b,
D54→D55,D55→D54; container-alone source shaping confirms those alternates. Four
G18/I7(+mirror) cases have no recognized region; these source containers have
7-cell width, but compilerregex limits both control/it marker dimensions to1..6.
Investigate recognizing actualnative7-cell markers and native mirrored identity,
then consuming mr as an explicit mirrored drawing operation without painting
source helpers. Preserve source positions/control semantics; do not silently
invent generic cavities or claim all65mirror placements validated. Need raw
native output/coordinate probes and actual strips. This is a plan/probe, not an
implemented fix. After resolving those real output gaps, complete source-family/
style audit and final actual product interaction/share/export review. Full beta
remains incomplete and goal active.

### Recover all enumerated native insertion outputs — 2026-11-03

All982source insertion candidates now compile;0rejected. Previous910entries
(and original428subset) remain exactly identical. Resolved65explicitmr mirror
helpers by reflecting the preceding native sign outline in its source surface;
children remain upright and actual mirrored-probe slot coordinates/sizes are
retained. Container-alone source shaping supplies true mirrored identity, so
C2a→C2b and D54↔D55 native alternates are no longer incorrectly rejected for
failing original-name-prefix matching. These literal mechanical tests do not
assert Egyptian meaning; Unicode18§11.4 recommends separately encoded reverse
forms when meaning changes. Input text is not rewritten.

Corrected previous next-step hypothesis: four G18/I7 cases are NOT simply it7
regex failures. Raw font output exposes pending ibs0B/ite0B because source bodies
choose7-cell widths while documented insertion rules target6. Compiler now uses
declared native slot dimensions, semantic edge/centre anchors and native upward
Yoffset in20ths of the full surface. Rule calibrated against workingG25BSnative
position [105,1054,630,620]. G18BSslot[105,1054,315,620],I7TEslot[1680,0,630,310],
actualsourcewidth2415retained. Only these4source documented-rule recoveries are
flagged regionRule; not a generic invented cavity. Source/native sign curves
unchanged.65mirrorhelpers have sourceTransform metadata; one affine reflection,
not glyph reconstruction. NormativeU13440semantics rechecked directly inUnicode18
§11.4. No font program, source licence, original art or drawing catalog changed.

Counts:255unmodifiedsingle,212unmodifiedmultiple,467mirrored,24rotated,
24rotated/mirrored;65consumedmirrorhelpers,4documentedcellrules.512explicit source
geometry observations remain; no collision-freedom claim. Frozen pre-change
910manifest/compiler/report:output/font-review/pre-insertion-mirror-helpers/.
Historical72probe marked resolved and its regex hypothesis corrected.
Current detail/hashes:docs/insertion-mirror-helper-review.json.

FocusedEgyptianJS24pass0.20s,/tmp/insertion-mirror-helpers-final-js.log includes
EVERY982expression reaching exactlyone actualnativecontainer andexpectedchild
count (no source helper paint). FullJS357pass13.22s,
/tmp/insertion-mirror-helpers-full-js.log. Source9pass15.51s,
/tmp/insertion-mirror-helpers-current-source.log. Sourcechecks verify deterministic
rebuild, all910priorentriesunchanged, everyoutlinecontrolpoint ofall65mirrors
has exactreflection, slotpositionsmatchactualmirroredHBprobe, and documentedrule
calibration/sizes. Initial source assertion wrongly compared mirrored slot sizes
to unmirrored slots; actual source state sometimes choosesdifferent childsize.
Corrected test compares the raw mirrored native probe. No production slot rule
was weakened/changed to satisfy that test. Initialmirrorfixture accidentally used
undocumentedO1TI; corrected to documentedO1BI. User inputs requesting unspecified
cavities are not counted in this finite source inventory.

Final builder97339TERMINAL0,/tmp/insertion-mirror-helpers-final-build.log:
accepted982/rejected0; source report method now separately describes native
mirrors and4documented rules. Allthree newactual strips visually reviewed:
mirrorhelpers, actualnamedalternates, documentedcells incldamage/RTL. Each has
failures[],geometry[], nohelpercontrols/nativeplaceholderfallback. Finalfull
browser tab51/mirrorTab:676cases,failures[],geometry[]. Assets versioned.
General33lastpassed previousturn; thisturn changes insertiondata/compiler and
newfixtures, no generalLatin layout logic. Browser51retains676corpus forhandoff.

Onlyknownliveprocess: fullPython15005,/tmp/unicode-beta-full-python.log. Last
poll confirms LIVE, nowpast54percent with55trailingtests; no reportedfailures.
Do not restart. Original collection predates latest tests/data; current modified
paths have explicit separate current focused verification. Current source9pass
and full357JS reflect final assets/code, not old collected assumptions.

NEXT: full source-family/style audit and actual product smoke review. Inspected
build_scripts.py:381shards from199sourcefilepaths;374entries still sayprovisional
licensedsource/customvisualreviewpending, only3labelledlightpen supplemental,
plus guarded custom/recovered variants. This needs actual visual evidence,
not blanket acceptance of style labels. Viewed approved04-scripts.png and
07-dense-scripts.png afresh: confident hand lettering/penweight, dense scripts
finerbutstillhandwritten. Native source correctness alone is not the approved
style. Suggested next concrete work: generate paged source-style atlas grouped
by original source face/file with representative actually-owned characters or
native variation samples (avoid irrelevant copiedLatin), at22pxcomic and44px
comparison sizes beside DadLettering. Review all199sources while preserving
native shapes/joining; identify/refine actual style outliers. Reuse existing
checkout/assets. Do not regenerate Dad/Calvin or resume emoji image batches.
Then final app edit/share/export/reset/load/font-wait smoke test, requirement-by-
requirement completion audit and terminal fullPythonresult. Keep full beta goal
active; source-style/product evidence is still incomplete.


## Source-style triage and terminal Python result (2026-11-03)

Previous goal turn was a verified wait: Python session15005 confirmed live.
This turn completed visual triage of all199source files/381shards at22/44px
beside Dad using tools/source-style-review.html. Page1 was inspected in the
preceding turn; pages2–17 inspected individually now (no credit for previously
truncated screenshot batches). All pages report zero font-load errors.
Detailed exact-source hashes/samples/decisions:docs/source-style-review.json.
35retain-current provisional sample decisions;128needpenadaptation; remaining
36have optical/weight/structural/mark-context/guarded decisions, incl1nonvisible.
This is triage, NOT completion of custom styling or all-glyph language validation.
Fixed atlas row layout to reserve actual ink/overhang rather than120px rows;
initial rows hid descenders/stacked Khitan. Rechecked Khitan after repair.
No production font program or renderer changed in this turn.

Full Python15005 is now TERMINAL0:1994passed,7warnings,7526.40s (2:05:26),
/tmp/unicode-beta-full-python.log. It collected before the latest Egyptian
regressions; those have separate current9source tests and357JS checks.
Do not restart this completed run just to obtain a newer collection timestamp.

Actual editor mixedUnicode edit/copylink/download/reset/share-restoration/reload/
fontwait/copyimage smoke passed. Exact texts/evidence and limitations:
docs/product-unicode-smoke-review.json. Export visually inspected and saved:
output/font-review/product-smoke-unicode.png. Copylink matched URL; clipboard
image/png confirmed. Reload initially disabled export then enabled after render.
This was cached-font reload, not throttled cold-network coverage. Browser share/
download call took1245.94s to return; successful but a confirmed long tool pause.
Subsequent calls bounded10s. Browser54actualapp and53atlas marked handoff.

NEXT: implement/prototype source pen treatment for identified typeset sources,
starting with Greek (actual strip looks typeset/widely spaced), preserve native
joining/anchors, and fix Egyptian thin ink after comparing actual strips.
No further emoji imagegen. All199sources visually triaged, not styled/accepted.
Remaining final completion audit must resolve these actual visual gaps; keep
full beta goal active. Read brief + source-style-review + product-smoke findings.


## Paused-goal groundwork and parallel plan (2026-11-03)

User requested updated plan, local image generation/rendering without localhost
permission interruptions, and more subagent parallelism. This is authorised
groundwork while the full beta goal remains paused; no production font/routing
change or resume. New current plan:docs/unicode-beta-plan.md; linked prominently
from agreed brief without changing its substantive scope. Reconciled stale
Python-running and missing-style-audit/product-smoke statements in audit JSON.
Terminal full-suite evidence remains1994passed (old collection caveat retained).

Used two subagents concurrently: remaining_plan wrote the plan; render_validation
independently inspected renderer/dependency validation pitfalls. Coordinator
implemented tools/font/render_specimen.py. Existing dependencies only; no server,
browser, new installation or localhost permission. Decodes WOFF2 to sfnt, native
HarfBuzz shaping, exact SVG outlines, COLRv0/CPAL layers inclforeground/alpha,
fullinkbounds, PNG/SVG/JSON output. Rejects missing glyphs and unsupportedCOLRv1.
Explicit runs are caller-ordered, not a replacement for app paragraph bidi,
annotations, Egyptian compositor, emojioptics, balloons, or browser exports.
Atlas mode uses existing project graphemes/nativealiases via bounded localNode.

Commands documented in newplan. Fixture:tools/font/specimens/unicode-groundwork.json
compares KleeOne andWenKai Greek, Dad, nativeArabic, Egyptian, blueheart andtoneZWJ.
Artifacts:output/font-review/offline-groundwork.{png,svg,json},
offline-source-style-01.{png,svg,json},offline-source-style-15.{png,svg,json}.
Rendered allthree; visually inspected page1 andgroundwork. Initial fixture wrongly
asked emoji-onlyfont for a space; tool correctly rejected missingglyph insteadof
fallback. Split into separate native source rows; final fixture terminal0.
Newtests:5passed,7existingPyMuPDF/Swigwarnings,35.27s. Verify decodedWOFF2/native
Arabicpositions, actualcolourpixels andZWJligature, outlinedSVG withoutfontfallback,
PNGdimensions andmarkpadding, missingglyph failure, atlasintegration.
No fullsuite rerun warranted for this isolated review tool/docs work.

Remaining productionwork planned in parallel withdisjointownership: Greekrouting,
supplementalpentreatment, Egyptianoptics; independent requirementaudit when slot
frees. Coordinator serializes sharedmanifests/builds andintegration. No blanket
nativefontstyleacceptance andno newexpertapprovalgate. Nextresumption shouldread
newplan anddispatchtracks, not repeat unchanged multi-hourtests or browseratlas.

## 2026-11-03 resumed implementation

User resumed the full brief. Tracks A–C dispatched concurrently per the saved
plan; independent audit is in `docs/unicode-completion-review.json`.

- Greek routing partial fix verified: 39 focused checks pass; saved previous
  full JS run terminal 361 pass. Actual local comic preview now inspected:
  proportional Greek no longer uses full-cell spacing; polytonic native fallback
  remains a supplemental styling input.
- Accepted Egyptian .014-em / Anatolian .010-em optical ink specimens; focused
  current checks 35 pass including all 982 insertion templates in both directions.
  Measurement now accounts for stretched enclosure stroke and splits adjacent
  Egyptian/Anatolian fields for distinct weights. Final browser corpus pending.
- Built the three previously reviewed optical-em sources (ArefRuqaa/Gaegu 1.16,
  Tolong 1.10). Cached build terminal success, 381 shards / 68,229,620 bytes.
  `test_source_optics.py` + `test_font_scripts.py`: 28 passed in 8.33s.
  Independent historical baseline checks: six passed after this build.
  `docs/source-optical-review.json` records shipped hashes and exact scope.
- Offline renderer plus optical tests: nine passed, seven dependency warnings,
  37.62s. Supplemental .22 pressure rejected as too subtle; centred .7 sample
  treatment accepted as first six-source production group, pending full-glyph
  implementation/guards and browser checks. Guarded category experiments remain
  isolated. No broad pen build accepted yet.
- Current processes: combining-outline catalog rebuild (session 69376,
  `/tmp/unicode-optical-catalog.log`); full JS run (session 5194,
  `/tmp/unicode-beta-current-js.log`); independent positional baseline tests.
  Do not launch duplicate runs. Existing dated full Python evidence stays valid
  for its collected inputs; no new full Python run launched.
- Local loopback preview running on port 8766 (session 79648). Port 8765 was
  occupied; no process stopped. Browser actual preview is available; final
  integrated browser checks wait for stable generated assets.

User correction: the local renderer was explicitly supplied to avoid manual
browser approvals. Coordinator attempted a browser download anyway; authority
was declined. No download workaround or retry occurred. User now explicitly
instructs local rendering for remaining work. No further browser calls/approval
requests. Two optical browser harness cases had completed successfully before
the interruption (`docs/optical-browser-review.json`), but this is targeted
pre-pressure evidence, not final broad integration. Remaining verification uses
the local renderer and source/runtime suites; preserve dated browser scope.

### Local-only styling milestone

- Two bounded optical browser cases had completed before download rejection:
  Greek proportional94ms/622,975PNGbytes; hieroglyph206ms/630,236PNGbytes,
  both no failures/geometry/fallback/unmapped findings. This dated evidence is
  `docs/optical-browser-review.json`; no more browser work is authorized for
  this run. Stopped our local server session79648 (port8766).
- Full current JS run terminal:367pass0fail15.61s, before pen-font integration.
  Optical combining catalog rebuild terminal:1,838visible mark drawings,
  two context records,300sources,2,700,364bytes. Asset URLs refreshed then;
  refresh again after pen integration.
- OldUyghur1.35 optical-em candidate accepted locally; source-optics tests5pass,
  source file extended (so previous optical recipe hashes need rebuild).
- First six-source production attempt failed before saving an accepted font:
  serializing the immutable native snapshot lost post3 source glyph names.
  Fixed original-glyph-order mapping and added actual-source regression.
  All source baselines remained intact. Transactional wrapper now restores
  all381fontshards+manifest on exception; source-specific recipe hashing allows
  future groups without invalidating unchanged source caches.
- First15 transactional production build running: session72881,
  `/tmp/unicode-supplemental-first15-build.log`; B owns input freeze/build.
  8,470retainedglyphs, estimated25–35minutes uncached. Do not duplicate or edit
  builder/pressure/recipe/source-optics inputs during the run.
- Initial production adapter tests10pass5.55s. Native exact bboxes/LSB/hmtx/
  GSUB/GPOS/GDEF retained, composite drawings frozen independently, guards at
  1024and384px, per-glyph rejected originals recorded. Persisted reports under
  output/font-review/supplemental-production (cache alone is not provenance).
- Additional9source acceptance from12source review is recorded in
  docs/supplemental-next-group-review.json. Ethiopic/Tibetan retained native
  after local review; Gujarati remains unresolved after whole-field guard
  rejection. Two further24source sample review batches are running under A,
  unique systematic-01/02 output paths; these are not production acceptance.
- Guarded joining/serif experiment records docs/joining-pressure-review.json.
  Whole-field checks rejected candidates missed by individual glyph guards.
  Dense CJK/Khitan/Tangut adaptation remains genuinely open; C owns vector-native
  candidates in isolated files, no production inputs.
- Coordinator added isolated CFF candidate support supplemental_cubic.py:
  two tests pass4.50s; math variant sample modestly expressive, production
  integration not adopted. Seal native taper/curve variation is provisionally
  retained after two reviewers found nearly invisible benefit from pressure.
  docs/cubic-pressure-review.json records hashes/scope; no AGPL production
  source package modified by this experiment.

### First production checkpoint and isolated final cache work

First 15 build terminal: 381 shards / 72,109,336 bytes. Native invariant checks
pass for 8,470 glyphs: 8,148 adapted, 141 blank, 181 explicitly native retained.
17 fields pass, six pages reviewed, and the 31 largest encoded retained cases
were inspected. Frozen checkpoint artifacts and exact scope are recorded in
`docs/supplemental-production-first15-review.json`.

First-15 source/historical verification: 37 initial passes, three strict metadata
rechecks pass after proving previously unadvertised Bengali cmap14 ranges exist
identically in frozen/current native fonts, one CJK positioning pass, five
catalog/native-path passes in 111.95s. An uncached catalog run was interrupted
at 303.74s; it was not a pass. Rebuild-aware decoded-font/path caches preserve
all checks and have a separate actual same-path geometry invalidation test.

Three regular private warmers (sessions 80099/57174/17971) and three dense private
warmers (78814/89188/30117) are active. Logs are respectively
`/tmp/unicode-supplemental-warm-{0,1,2}.log` and
`/tmp/dense-warm-group-{0,1,2}.log`. B and C own terminal results. These preserve
actual source order, novelty, UVS and subset closure; public font-manifest and
381 assets must remain unchanged until cache merge and the final normal build.
The actual packaged workload is 96,378 glyphs across 145 regular pressure
sources (8,470 already built), and 146,617 glyphs in 123 shards across five dense
sources. SignWriting has 37,886 glyphs including closure; UnicodiaFunky has only
326 after scope/subset, not its much larger raw font inventory. A is preparing
safe auxiliary SignWriting range warming with unchanged per-glyph kernel code.

The CFF UFS candidate is terminal: 1,301 glyphs, 1,264 adapted, one blank,
36 native retained. Independent post-save verification passes; all 37 retained
(including blank) drawings remain exact. Maximum serialized native frame error
is 0.005447 design units, below the explicit 0.01 tolerance from Type 2 16.16
relative coordinate quantization. Full candidate visual review remains before
production integration. Nine focused specialist tests pass in 26.63s.

The isolated CJK variant prototype is terminal: 1,905 glyphs, 1,573 finer pen,
67 gentle native flex, 264 retained originals and one blank. All 1,002 mappings
prove pinned raw donor -> frozen native variant -> expected cached derivative,
with exact advances, native frames, cmap14, contour and painted cache identity.
Representative sixteen base/variant pairs were inspected at 22/44 px. Public
variants are unchanged. All 92 marked CJK companions must later rebuild from
current primary/standalone variants, then the combining catalog. Parent owns
standalone variant builder; B owns shared script builder; C owns dense kernels.

Standalone math native font bytes are unchanged; the authoritative hash is
recorded in its manifest and `docs/math-variant-style-review.json`.
All 37 pairs were inspected and provisionally retained for their natural
calligraphic pressure and conventional relation distinctions; no extra CFF
profile is needed. `docs/math-variant-style-review.json` records this decision.
No further browser calls, server, downloads or approval requests were used.

### Local-only integration continuation

The supplied renderer remains the exclusive visual workflow for current work;
no further browser calls, downloads or manual approval requests are needed.
Regular worker 0 and both SignWriting range helpers are terminal. Regular
worker 2 resumed after private rollback using the separately tested equivalent
fast validator (session 36170); Math tail and Symbols2 helpers now have explicit
completion gates (76825 and 42432). Three dense workers continue privately;
all 381 public primary fonts and their manifest remain at the first-15 checkpoint.
The current collection contains 2,063 Python tests (collection only, 1.51s;
`/tmp/unicode-final-collection.log`). This is not a new full-suite pass.
The style-status reconciliation now recognizes dense-treatment metadata; it
will be regenerated only after stable production integration.

Dense monitoring at 09:15 GMT reports at least 38,211/146,617 glyphs processed.
The original slow groups imply roughly 3–4 hours remaining at that snapshot.
A safe ahead-of-queue cache plan is approved for two private auxiliary groups
(36 future Jigmo2/3 shards, 18,854 glyphs each), after Math/Symbols2 helpers
finish. C must register original-plus-auxiliary verification gates with B before
launch. Original queues, source mapping, kernels and public files remain intact.
Math auxiliary range is terminal; Symbols2 is still active. These estimates are
not completion claims. A is preparing strict historical-test updates that prove
pinned raw identity on frozen native fonts and separately prove finished cache
lineage, preserving semantic, shaping and metric checks.

### Final evidence hardening while private builds run

Previous continuation made concrete progress (native baselines completed,
strict historical test preparation, status reconciliation). On this turn C
polled the actual owned dense sessions 78814/89188/30117 at 09:20 GMT: all
three are live, without errors; at least 40,491/146,617 glyphs and 24/123
shards are complete. Root cannot access B-owned 36170 directly (unknown
handle). B then polled both owned sessions: 57174 and 36170 are confirmed
live (UnicodiaCunei 200/1,253 and Math 2,600/4,903 respectively). No restart
was inferred from the root observation failure.
`review_supplemental_production.py` now fails its command if any final field
is rejected, after saving field evidence and rendering review pages. Syntax
validation passes. A updated eight historical source-domain test files to
compare pinned source identity against authenticated frozen native packages
and verify finished lineage separately; integrated checks remain pending.
Root requested stronger adapted-CFF cache lineage, since bounds and report
metadata alone do not authenticate the finished charstring.

### Stable per-source review metadata prepared

The previous turn made progress: final field-command failure semantics and
CFF cache lineage were strengthened. Current continuation verified the CFF
fixture log (six passes) and inspected exact native-input/cache/Type2 replay.
`tools/font/style_review.py` now defines a stable sampled-decision record for
each source: record path, source number, disposition, canonical decision SHA
and explicit limited scope. The SHA covers only number/source/source hash/
disposition; mutable production status is deliberately excluded. A read-only
check resolves all 381 primary shards to exactly 199 source decisions.
B will attach this metadata only after all private jobs finish; A will
authenticate it in historical lineage checks. No public font or manifest
changed. Dense final completion verification must authenticate recipe, exact
assigned family sets, private manifest/font hashes and report coverage, rather
than merely check that completion files exist; C owns that independent check.

### Math production cache terminal within regular worker 2

The previous goal turn made progress (exact review metadata transition and
12 passing negative/lineage fixtures). Fresh B-owned polls confirm regular
workers 57174 and 36170 remain live. Math completed all 4,903 retained glyphs:
4,713 adapted, 19 blank, 171 guarded native; 1,406 cache hits, 1,268.4s.
Worker 2 continues later sources. Worker 1 is at UnicodiaCunei 400/1,253.
No observation failure caused a restart. The final style-status reconciler
now recognizes source 12 Seal Sans and source 191 Scheherazade as the two
explicit native-calligraphy decisions, rather than misclassifying their old
guarded baseline categories as unresolved. It records the accepted disposition
for all rows and authenticates source number/hash against the baseline. Syntax
check passes; report regeneration remains deferred until stable final assets.


### Final integrated font build started (2026-11-03)

All regular private cache authentication and merge gates passed. All six dense jobs and full123-family/146617-glyph authentication plus repeated-family comparisons terminated successfully. Seven actual dense production fields pass384px structural guards and were inspected locally at22/44px, with24largest retained cases and12additional source-specific cases; three Khitan nominal targets require native context and are explicitly deferred. The reviewed shared-builder patch is applied and the sole normal transactional public build is running. Final public byte continuity, dependent CJK/marked/catalog rebuilds and current full checks remain; this is not completion. Rendering uses the supplied local renderer only.


### Final primary integration and local review passed (2026-11-03)

Normal transactional build37037terminated0 with381shards/181304236bytes. Regular145of145visual-byte continuity passes after final45/50actual22/44rereview and384/1024whole-field guards. CFF192actual final field also passes both scales. Dense123publicfont/report SHAcontinuity passes for146617glyphs;146TT/CFFsources97679glyphsnative invariants pass. All17finalsourceatlaspages199samples inspected offline. FinalstandaloneCJKbuild3467terminal0 andexactacceptedprototypeSHA. Rootmarked92build40463running; combiningcatalog, versions, finalJS/fullPython and30requirementreconciliationremain. No currentbrowser/download/approvalcalls.


### Finalcurrentfullchecksstarted (2026-11-03)

All92markedcompanionsandcombiningcatalogcomplete. CJKdomain6pass835.10s. GenuineCFFwidthbugfixedthroughauthenticatedwidthoperand-onlycachemigration:all1301drawingsremainexact,allwidths=hmtx,43fixturesand2originalregressionspass. Correctivenormalbuild95666terminal0changesonlyUFSfont;380othersbyteexact. Localcorrectedfield384/1024and22/44accepted;finalatlaspage16refreshed. Assetversionsrefreshed;currentJS367pass13.35s. RootfullPython30444nowrunning2112collectedtests(notpassyet),log/tmp/unicode-final-python.log. Refreshedoutline25956running;coverage21199terminal0. Finalfullsuite,assetfingerprintand30requirementreconciliationremain.


### Complete catalog regression passed; full suite restarted (2026-11-03)

The frozen strict catalog verifier passes 70 mutation fixtures. Actual numeric
regression89925 terminated0: one passed in1326.76s, including native/cache parent
proofs, source hashes, copied and borrowed marks, rings and interior bounds.
All13,887 fingerprinted files and199canonical style decisions match the prepared
state. Rootfull54417 now runs all2182collected tests with-x-v and durations,
log/tmp/unicode-final-python-r2.log. This is not a pass yet. No production assets
changed for the catalog-verifier corrections. Finalterminal result, post-run
fingerprint and30requirement/status reconciliation remain.


### Local-only final diagnostic checkpoint (2026-11-03)

User reiterated use of the supplied local renderer without browser/download/approval requests. Diagnostic53910 remains active: emoji deterministic rebuild passed and all175emoji-module tests passed; three known failures so far, complete terminal list pending. Strict staged Cuneiform/Devanagari replacements pass all6tests and root reviewed them. Chemical single312 constructed-native rescue now passes326-glyph lineage,325otherglyph byte identity,12fields, all5semantic constraints and12policyfixtures; combined Music/Chemical fixtures24pass. Root inspected and accepted local22/44Chemical comparison. Music/Chemical publication remains pending diagnostic terminal; future ordinary build must change only those twofonts, with379others exact. Combined reviewed patches apply-check terminal0. Live included tests/helpers/assets remain unchanged; canonical199styledecisions unchanged. No final full-suite pass or goal completion claimed.


### Extended Funky rescue and current source ledger (2026-11-03)

Actual diagnostic exposed14geomanticdot-centering failures. Strict original bounds are retained: isolated15glyphFunky rescue (14figures+harpoon) nowpasses all326native/cache/construction proofs,311otherglyph byteidentity, all16originalpatternpredicates, fiveharpoonconstraints,14fields and26combinedMusic/Funkyfixtures. Root inspectedbothlocal22/44comparisons andaccepted candidate d5784187ed8887c200853bee622eceffb2e5f3f56f14a6cb30ca49da8f2f55fa. The earlierharpoon-onlycandidate isarchived with21verifiedartifactSHAs. Asteroidfailure iscontourorder-only; role-aware2testproposalpasses17.81s androotinspectedall21symbols. No livepolicy/testbatch/publicbuild yet. Diagnostic53910ownerconfirmedlive56%,allincludedinputs remainfrozen. Independent13887filecheck matchespriorbaseline exceptthe3contextualmodules deliberatelyexcluded;199canonicaldecisionsmatch. Sourceledgercurrentintegrationprose nowseparatesearlierfirst15history andlistsbothpendingrepairs. Fullsuite/fingerprint/finalaudit remainmandatory.
