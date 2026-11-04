# Font sources

The JSON manifests pin upstream repository commits, Git blob hashes, SHA-256
hashes, download URLs and build-cache locations. Font files are cached under
`build/unicode-sources/`; they are not all served to users. Licences needed for
redistribution are copied into `assets/fonts/licenses/`.

- Noto: SIL Open Font License 1.1, from `fonts/LICENSE`. The distribution
  repository's code licence is not the font licence.
- Google Fonts handwriting candidates: each family's own OFL notice.
- LXGW WenKai: OFL, including reserved font names. Rename modified derivatives
  to the project's family names; do not assume its limited name-use exception
  permits arbitrary outline changes under the original name.
- Jigmo: font data is CC0, as documented in its `documents/LICENSE.txt` and
  release archive. Its repository build scripts have a separate MIT licence.
- `dad-lettering-base.woff2` is a preserved snapshot of this project's original
  PDF-derived lettering, used as a reproducible input to the extension builder.
  Its provenance remains the supplied comic, not Noto. External font licences
  do not provide rights to the original comic artwork.

`python tools/font/source_inventory.py` verifies cached source hashes, extracts
font files from the verified Jigmo archive, and reports coverage gaps. The
source report is deliberately separate from the delivered-font audit: these
sources have not all been adapted, bundled, shaped or visually validated.

`python tools/font/extend_latin.py` builds the separate extended font from the
original snapshot and pinned Noto combining marks. Original outlines, advances,
kerning and contextual substitutions are preserved. This first derivative
adds canonical Latin compositions and mark/mkmk positioning, plus provisional
donor outlines for several non-decomposable letters. Further visual work remains.

`python tools/font/preview_sources.py` draws handwriting candidates through
HarfBuzz. It does not rely on Pillow having a working RAQM installation.

`python tools/font/fetch_sources.py` restores a missing cache from the pinned
URLs, verifying both SHA-256 and Git blob hashes before accepting each file.
Use `--check` for an offline verification. UniHieroglyphica is also pinned under
its OFL; the Reserved Font Name is replaced in derivatives.

`python tools/font/build_scripts.py` packages provisional script fonts into
WOFF2 assets and generates `js/font-manifest.js`. All OpenType layout features
are retained during subsetting. Large ideograph repertoires are divided into 1024-character
pieces with layout closure; joining/compositional repertoires stay together. Rotated, vertical,
unjoined and UI-specific source variants are excluded from the horizontal
comic's default selection. Each derivative has a new family name and keeps
source copyright/licence notices. Verified existing output shards can be reused
on subsequent builds; delete the generated script assets and manifest to force
a clean rebuild after changing subsetting or naming rules.

The browser selects these assets automatically from the input, waits for loading
before measuring, and enables image export only after the current input is
rendered. Bundling a source does **not** imply its comic styling, every sequence,
or every script's layout has passed review. Those are separate beta gates.


Kaiyuan Small Seal is pinned under OFL in `kaiyuan.json`. `fetch_sources.py`
restores its verified archive using only manifest-listed regular members.
`build_seal.py` validates each SVG against Unicode SealSources before compiling
it; `docs/seal-source-review.json` records upstream review status. Most signs
have automated alignment only and still need historical/visual review.

Noto Gurung Khema and Ol Onal are compiled from pinned `.glyphs` sources using
`build_glyphs.py` and the fontmake version in `uv.lock`. The builder verifies
source hashes, rejects executable filter custom parameters, uses local compiler
output directories and renames derivatives. No upstream build scripts run.
Kedebideri and Kanchenjunga use pinned Google Fonts binaries and family OFLs.
The Kirat Rai derivative adds canonical ccmp composition via
`canonical_composition.py`; its recipe includes the helper hash to invalidate
cached output when those rules change. Tests compare full and partial canonical
decompositions using pinned Unicode data and actual HarfBuzz glyph identities.


Microsoft Egyptian Text (`egyptian-text.json`) supplies core Egyptian sign
composition, ahead of the coverage-only UniHieroglyphica source. The pinned
reference font is published under OFL; retain both its directory license and
embedded notices (including Microsoft layout logic, James P. Allen outline
attribution and STIX Latin notices). Upstream test sequences are cached for
review, not executed. Shaping tests compare the derived and source font and
check that joiners actually change arrangement. Extended-A composition and
exhaustive format-control/variation behavior remain incomplete.

`unicodia.json` pins two OFL sources from Mercury13/Unicodia. Daarage supplies
Tulu-Tigalari; Funky is restricted with `include_ranges` to the author's 26
Sidetic letters. Other Funky scripts have explicitly uncertain provenance or
upstream quality warnings and are not packaged by this source entry. Retain
`Unicodia-LICENSE-Funky.txt` and the complete OFL in
`Unicodia-LICENSE-Daarage.txt`. Derivative names replace both SFNT and CFF names.
The Tulu derivative adds missing canonical independent-vowel compositions;
its recipe hashes `canonical_composition.py`. Original conjunct and positioning
tables are retained. The upstream Daarage development notes identify imperfect
KTt, KTTh, KTRY and KTV conjuncts and an extreme stacked-cluster overlap; those
remain review gaps, not claims of finished linguistic validation. Sources:
https://github.com/Mercury13/unicodia/tree/dcbe251036833331f0a8f66c186a315751db24f9/Font-Source/Tulu2

The same Unicodia pin also carries `ArchaicCuneiformNumerals.ttf` and the
Noto-derived `UnicodiaCunei.ttf`, under their separate retained OFL notices.
The first supplies all 311 Unicode 18 archaic numerals; the second adds twelve
tenû numeric signs. Keep original relative sizes: Unicode chart glyphs for
higher numbers are sometimes reduced to fit the chart cells, which is not an
instruction to squeeze their text-font widths. Tests compare every new outline
and advance to the pinned sources. Authoritative repertoire and author sources:
https://unicode.org/Public/18.0.0/charts/nameslist/12550/
https://github.com/eggrobin/archaic-numerals

`ufs.json` pins the direct author's UFSZero Ext font and per-font licence records.
The author distinguishes its OFL font assets from Apache-licensed module code in
`docs/LICENSES.md` and explicitly lists UFSZeroExt as an OFL font in
`font-source/font-sources.toml`; both records are pinned alongside the font.
Retain `UFSZeroExt-OFL.txt`, `UFSZeroExt-NOTICE.txt` and embedded copyright.
Only assigned Unicode 18 Jurchen/Tangut mappings are accepted. Other repertoires
and draft/unassigned mappings are excluded. The similarly named Unicodia cache
candidate is not used. The derivative repairs two zero-advance Tangut letters
(U+17D0B, U+180DF) to the source's 1000-unit ideograph cell width; outlines and
bearings remain intact. Its recipe hashes `ideograph_metrics.py`.

BabelStone Pseudographica (the existing Unicodia pin) supplies 901 additional
legacy-computing and related non-emoji symbols to `build_grid.py`: 741 structural
pieces and 160 standalone forms. `structural_ranges` alone triggers grid layout;
standalone pictures, arrows and outlined letters remain ordinary prose.
`build_target: grid` prevents a redundant generic-script derivative. Its full
OFL notice is retained, and the custom font is renamed Dad Grid. Source cells
(x=0..1024, y=-224..800) become 600×1000 font cells. For legacy constructions the
renderer restores square cells, while ordinary box drawings retain text-cell
proportions. Occasional 1–2-unit source endpoint overshoots snap to shared
boundaries. Blocks and joining pictures retain rigid geometry; standalone forms
and line/large-type pieces receive subtle internal pen variation. The source's
nonstandard Prince emblem at U+1F934 and emoji artwork remain excluded.
Upstream constructed-character examples and mapping caveats:
https://www.babelstone.co.uk/Fonts/Pseudographica.html

The base-lettering builder also accepts 39 assigned general combining marks
from the pinned Unicodia Funky source, retaining Noto/Mikhail Merkuryev OFL
attribution. They are normalized to the existing cap height and supplied with
zero advances and base/mark stacking anchors. `script_exclude_ranges` prevents
these base-lettering additions from leaking into the Sidetic derivative.
Four side-parenthesis marks use separate anchor classes and sit beside voicing
marks at the same vertical level. The current 170-unit side clearance is a
provisional optical choice for the lettering's voicing-ring size, not a claim
of exhaustive phonetic typography review.

`python tools/font/build_egyptian_variants.py` derives a small standalone
rotation font from the pinned UniHieroglyphica source and Unicode 18's
`StandardizedVariants.txt`. It implements all 142 registered rotations with
clockwise affine transforms, preserving source side margins and centre height.
The derivative is renamed Dad Egyptian Variants and retains the existing
UniHieroglyphica OFL attribution. The four expanded lost-sign variants are not
rotations and are outside this builder. `docs/egyptian-variant-review.json`
records each angle, transform, source hash and advance.

Registered variation sequences select this derivative through the app's font
routing and Egyptian composition path. `js/egyptian-layout.js` additionally
places basic quadrats, applies explicit and directional mirroring, and renders
editorial blanks, lost signs and damage. This is renderer behavior, not shaping
implemented by the derivative itself. Insertions, enclosures, vertical columns,
native-reader review and custom sign styling remain incomplete.

References: Unicode `L2/24-238` explains clockwise rotations and approximate
angle conventions; Microsoft's `EgyptianOpenType/eot.md` describes the existing
core-sign composition font and its three-level OpenType model. Neither source
establishes completed composition support for the extended repertoire.

## Egyptian insertion metadata

`python tools/font/review_egyptian_insertions.py` inventories the pinned Microsoft
EgyptianOpenType `insertions.py` and `config.py` without executing their code.
It verifies their hashes, matches source glyph names against the pinned font,
and records all 328 alternative insertion cells for 188 source glyphs in
`docs/egyptian-insertion-review.json`. Three glyphs are font-only variants without
a direct cmap entry. The metadata is MIT licensed; its notice is retained in
`assets/fonts/licenses/egyptian-insertion-tools-MIT.txt`. The font remains OFL.

These cells are specific to Egyptian Text's sizing model (315 horizontal and
310 vertical font units per cell). They must not be applied directly to
UniHieroglyphica outlines. The report preserves cell sizes and optional offsets
in twentieths for later coordinate adaptation; it is not a claim of insertion
renderer support. Actual source glyph variants, bearings, shaping offsets and
collision checks must be accounted for when consuming the data.


`python tools/font/build_egyptian_insertions.py` shapes a full-blank insertion
probe to recover contextual container outlines and insertion cells together.
The renderer consumes `js/egyptian-insertion-manifest.js`; the build report is
`docs/egyptian-insertion-build.json`. Currently 217 single-control and 109 ordered multi-control unmodified
combinations pass cell bounds checks and a 10×10 interior-point collision screen.
Separate native probes additionally accept 90 mirrored, 11 registered rotated
and one rotated/mirrored combination. Rotation candidates require both a Unicode
standardized-variant entry and a native format-14 cmap mapping. This also recovers
font-only rotated names such as D28o from their registered Unicode sequences.
Every ordered subset of the documented controls is probed jointly; marker order
is verified and overlapping insertion regions are excluded. The report retains
554 rejected probes: 370 sampled ink intersections, 54 out-of-cell regions,
58 overlapping region combinations and 72 native probe mismatches. These retain
native fallback. Sparse sampling does not prove collision freedom. Native-reader
review, extended or damaged containers, excluded combinations and custom sign
style remain open. Nested inserted groups and horizontal RTL are supported.


## Egyptian enclosure components

`python tools/font/build_egyptian_enclosures.py` verifies the pinned Egyptian
Text source and shapes blank probes to extract 14 contextual enclosure ends and
the plain/walled connecting strips. `js/egyptian-enclosure-manifest.js` retains
the OFL paths, source glyph names, bounds and advances. The renderer tiles strips
(with their native overlap) and scales the last span uniformly across tiles;
ends keep their original aspect ratio. It supports nested content, absent ends,
extended signs and RTL reflection. No arbitrary sign outlines are substituted
for enclosure ends. Vertical composition and native-reader/style review remain
pending. Rules and example sequence follow Unicode 18 section 11.4.2:
https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-11/

## Standalone UFS symbols

The pinned, font-specifically OFL UFS source additionally supplies 133 assigned
standalone mathematical, musical, geometric and punctuation symbols. Their
explicit scope is `standalone_symbol_ranges` in `ufs.json`; script letters and
new combining music marks are not included in this addition. `alphabet_ink.py`
now handles both quadratic TrueType and cubic CFF outlines, preserving advances
and applying a small smooth pen variation. CFF charstrings retain their source
private dictionaries and width semantics. Existing shaping features remain in
the subset. Tests verify nonempty outlines, bounds within four source units,
preserved advances/shaping output, and distinct related symbols. Specialist
notation and final comic-style review remain pending.

## Hebrew heavy points

`hebrew_marks.py` imports U+05C8 and U+05C9 from the pinned UFS source into the
complete Noto Rashi Hebrew font, consuming them outside the generic UFS subset.
Cubic outlines are converted within 0.5 font units and made zero-advance marks.
Their origins are aligned to the native sheva/dagesh drawings, and the native
mark classes/anchors are copied. Sheva keeps the reference's upper clearance;
dagesh keeps its interior center. Bases without an anchor inherit the source's
fallback placement. Existing Hebrew outlines and shaping remain unchanged.
The derivative embeds the donor copyright as well as retaining the OFL notices.
These are typographically heavier forms with separate encoded meanings; they
are not normalized to ordinary sheva/dagesh. See Unicode 18 section 9.1:
https://unicode.org/versions/Unicode18.0.0/core-spec/chapter-9/

## Noto Emoji music drawings

`noto-emoji.json` pins the Google Fonts Noto Emoji variable font and OFL licence
at revision `8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5`. Scope is twelve reviewed
monochrome music/instrument emoji only. `build_target: emoji` keeps this source
out of script sharding; cmap presence elsewhere in the source is not delivered
coverage. `emoji_licensed.py` renders weight 400, applies the preferred expressive
procedural treatment and traces the result into Dad Emoji's two colour layers.
Colour-dependent source drawings are not automatically imported. Both pinned
presentation variants for headphones and radio are included.

Dad Emoji includes modified OFL outlines and is distributed under OFL 1.1 with
the retained copyright/licence in `assets/fonts/licenses/NotoEmoji-OFL.txt`.
The derivative keeps its own family name and embeds copyright and OFL metadata.

The reviewed Noto Emoji scope additionally includes the 24 clock faces U+1F550
through U+1F567. Their 48 standardized text/emoji variants use the same adapted
monochrome drawings. A regression renders each compiled glyph and measures ink
in the expected hour/minute directions, including the between-hour positions
for half-hours. Fine tick marks trigger conservative procedural-strength
reductions; applied values are recorded per glyph, never assumed to be 1.7.

The transport scope adds 24 road, rail and water vehicles, plus eight pinned
presentation variants. Most use weight 400 at 384px before tracing. Locomotive
U+1F682 uses weight 350 at 512px to preserve small wheel openings; ship U+1F6A2
uses weight 400 at 768px for its small windows. These explicitly recorded source
settings let the existing topology guard pass without relaxing it. Source weight
and raster resolution are included in each glyph's provenance record.

The tool/hardware scope adds 24 drawings and 20 pinned presentation variants.
They retain recognizable monochrome identities, including open/closed padlocks,
key teeth, linked chains and saw teeth. The clamp U+1F5DC uses weight 400 at
768px to preserve its fine screw-thread openings through treatment; all other
new tools use the default weight 400 at 384px. A compiled-raster regression
checks that only the locked padlock encloses space inside its upper shackle.

The expression scope adds 45 monochrome-compatible faces: affectionate and
hand-gesture expressions, several other emotions, nine cats and the three
see/hear/speak-no-evil monkeys. Existing approved face drawings are retained.
Colour-dependent hot/cold/nauseated faces are not included in this scope.
Star-struck U+1F929 uses weight 400 at 768px for the star-eye tips; fearful
U+1F628 and anxious U+1F630 use weight 350 at 512px for their fine forehead
hatching. All other new expressions use the default source settings. The dotted
face keeps its twelve separate perimeter dashes and three central features;
this is checked in the final compiled raster, not inferred from its glyph name.

The compound-emoji scope adds nine donor ligatures and their fourteen exact
qualification forms from the pinned Unicode emoji-test inventory: face in clouds,
face exhaling, spiral eyes, horizontal/vertical head shaking, black cat, service
dog, polar bear and broken chain. `emoji_sequences.py` shapes the pinned donor
with HarfBuzz and requires each form to select the same single real glyph before
applying expressive treatment. The donor glyph name and every advertised form
are recorded. Source `include_sequences` is distinct from standalone ranges.

The derivative uses explicit GSUB ligatures and default variation mappings for
sequence components. Eleven newly needed cmap components have empty, zero-width
outlines and are marked `componentOnly`; neither standalone routing nor visible
coverage may claim them as completed drawings. Qualification handling does not
advertise arbitrary selector insertions, text-selector variants or adjacent
unjoined characters. Black cat retains a black body and polar bear a white face.

The mammal scope adds all 63 standalone mammal symbols in the pinned emoji
inventory, plus six standardized presentation variants for dog, cat and chipmunk.
Previously component-only cat, dog and bear codepoints now have real standalone
drawings. Their compound forms retain separate ligatures. Boar U+1F417 uses
weight 400 at 512px; giraffe U+1F992 uses weight 350 at 512px. Orangutan U+1F9A7
uses weight 400 at 512px with fixed seed 129448, shifting the pressure field away
from fine enclosed details. These source settings are recorded in provenance;
all retain the same feature-preservation guard. The other mammals use defaults.

Compiled-raster checks preserve the heavy black cat versus outlined cat and
heavy bear versus white polar bear. Dog, guide dog and service dog remain three
distinct drawings. Paw prints keep two pads and eight detached toes.

The next animal scope adds 20 birds and 42 amphibian/reptile/marine/invertebrate
symbols, plus ten standardized presentation variants. It covers the standalone
animal drawings available in the pinned donor; the newer orca U+1FACD and
monarch butterfly U+1FACC are absent and are not claimed as supported. The black
bird compound adds a tenth donor ligature, retaining a filled black body distinct
from the ordinary outlined bird.

Peacock U+1F99A uses a 768px raster; crocodile U+1F40A, spouting whale U+1F433
and blowfish U+1F421 use 512px. All use weight 400 and the unchanged preservation
guard. Other new animals use the default 384px raster. Compiled-raster checks
verify the black-bird distinction and all twelve open sectors of the spider web.

Spider U+1F577 also uses 512px: its 384px treatment preserved raster topology,
but polygon tracing dropped one small opening. The higher-resolution source
preserves it in the compiled outline. Both licensed builders now assert that
tracing retains at least the source's meaningful components plus holes, so a
raster-only pass cannot silently approve a drawing that loses details later.

The plant scope adds 28 flowers, trees, leaves, nests and mushroom, plus four
standardized presentation variants for rosette and shamrock. Leafless tree
U+1FABE is absent from the pinned donor and remains outside this scope. Cherry
blossom U+1F338 uses weight 400 at 512px; its finer sampling passes treatment and
compiled-contour checks. The other plants use weight 400 at 384px. These are
monochrome drawings; a future brown-mushroom compound still needs its own
colour/shape review and is not implicitly advertised by the generic mushroom.

Plant regressions rasterize the compiled font. Eroding the clover interiors at
two depths isolates three shamrock leaves versus four clover leaves. The reviewed
nest-with-eggs drawing retains two separate enclosed eggs above its bowl; the
empty nest has none. These supplement general contour and variant checks.

Four colour-dependent faces (enraged, nauseated, hot and cold) use the same
expressive donor-outline treatment with selective face fills. The colour record
`output/imagegen/emoji-production/colour-face-palette-source.json` pins the PDF,
page renders, patch coordinates and median RGB values. Red comes from page 20's
rug; light green from page 47's landscape wash; the previously reviewed orange
and light blue samples are reused. No arbitrary tint is applied.

`emoji_colour_faces.py` colours only the largest enclosed white face region,
leaving other enclosed details on a white underlayer and painting ink last.
Hot-face sweat/tongue and cold-face teeth/frost therefore retain white details.
Compiled-layer raster checks require the colour to stay inside the underlayer,
retain substantial white details in hot/cold faces, and match the pinned palette.

The sports batch adds 27 explicitly selected balls, rackets, sticks, nets and
other equipment. All use weight 400 and a 384-pixel donor raster, with the same
strength-1.7 treatment and automatic topology-preserving reductions. The
reviewed monochrome source distinguishes baseball from softball by opposite ink
polarity; a compiled-raster regression preserves that distinction. Eight pinned
text/emoji variation forms are included. Medals, people and their modifier/ZWJ
forms are outside this batch and are not implicitly advertised.

The prepared-food batch adds 51 reviewed monochrome drawings, from bread and
cooked dishes through rice, noodles and dumplings. Waffle, tamale and pot of food
use a 512-pixel raster to keep details through contour simplification. Falafel
and green salad use weight 350 at 512 pixels to preserve fine interior openings;
the other drawings use weight 400 at 384 pixels. All retain the standard
strength-1.7 request, deterministic seeds and topology-preserving reductions.
The pinned variation file defines no presentation pairs for this selection.
Fruit colour distinctions and additional food sequences are not inferred from
these monochrome entries.

The dining batch adds 41 sweets, drinks and tableware drawings. The three
ice-cream forms, cake forms, drink containers and utensils retain their distinct
source silhouettes. Ice cream in a bowl uses weight 350 at 512 pixels to keep
fine details with nonzero guarded pen treatment; all other drawings use weight
400 at 384 pixels. Six pinned presentation variants cover hot beverage,
cocktail glass and fork/knife with plate. The selected sources are monochrome;
no colour-dependent variants or unreviewed sequences are inferred.

The sky/weather batch adds 43 drawings and 48 pinned presentation forms. Fog and
snowflake were previously blank compound components; they now have real
standalone drawings while existing compound ligatures remain intact. The new
moon uses pressure .02 and no endpoint taper: the skeleton radius of a solid
disk is not a pen-stroke radius, and the default pressure made its outline too
lumpy. The bend field and requested strength 1.7 remain. The Milky Way uses
weight 400 at 512 pixels, pressure .2 and bend .006 to preserve small white stars.
Both exceptions are recorded in the per-glyph settings and retain all guards.

Compiled-raster regressions check the new moon's roundness, the decreasing dark
area from new to full moon, and opposite dark sides in waxing/waning phases.

The new-moon face has an explicit `dark-face-inversion` source transformation:
its closed border defines a dark disk, with the five interior face components
preserved as white features. It uses pressure .15 and no taper. This keeps it
visibly distinct from the white full-moon face; the compiled font checks both
ink contrast and the five feature openings.

Three Yangqin tempo signs (U+16FF4..U+16FF6) are constructed from the pinned OFL
WenKai Suzhou glyphs. The U+3026 baseline is retained with its single upright
removed at verified contour junctions; the two/three uprights come from
U+3022/U+3023, and the cross from U+3024. They fit the original short, raised
U+3026 register and retain its 1000-unit advance. Existing source glyphs are
unchanged. The builder hashes `yangqin_signs.py` into the WenKai shard recipe.
`docs/yangqin-source-review.json` records the source and primary proposal review.
The PDF supplies structural reference only; no PDF font outlines are extracted.

### Vietnamese reading marks

`tools/font/vietnamese_marks.py` constructs U+16FF0/U+16FF1 from uniformly
scaled U+4E87/U+21FE8 in the pinned WenKai source, retaining its OFL licence.
Positive advances reserve space on the right across fallback shards. The
Unicode proposal's pages 4–5 identify these forms; no proposal or BabelStone
outline is copied. `docs/vietnamese-mark-source-review.json` records the
references, hashes and observed specialist-font behaviour. This generic
side placement is provisional: historical base-specific mergers and vertical
positions still require implementation and fluent-reader review.

### East Syriac Malankara

Hendo Academy / Binu George's version 1.0 is pinned by archive and member
hashes in `malankara.json`. Its supplied OFL 1.1 licence, including the
reserved font name, is retained in `assets/fonts/licenses/EastSyriacMalankara-OFL.txt`.
The derivative uses the generated Dad Script family name. Native Syriac
forms, vowels and joining controls are kept together so Malayalam Syriac
text can select a single font. The source remains a provisional calligraphic
style and does not cover every Syriac character. The restrictive Serto
Antioch donor remains excluded. `fetch_sources.py` restores only named,
hash-verified regular ZIP members; it does not unpack arbitrary paths.

### Hand gesture modifiers

The pinned Noto Emoji source now includes 25 reviewed hand gestures and their
125 exact Unicode skin-modifier pairs. `emoji_gestures.py` treats the neutral
ink once and shares it across all five tones. Skin masks include separate
finger regions, exclude reviewed air gaps, and close the pinched-fingers wrist
only for colour fill. The palette remains the existing PDF-sampled skin palette;
no new colour approximation or source font was introduced. See the compiled
`gestures` and `gesture-tones` specimens and per-glyph production review.

### Buildings and places of worship

The Noto Emoji scope includes 24 buildings, fountains and places of worship.
The same expressive pen treatment retains each donor's identifying architecture,
lettering and religious symbols. The synagogue uses weight 350 at 512 pixels to
preserve its small star; the Kaaba uses 512 pixels with reduced pressure and no
taper to preserve white ornament inside its broad solid body. The topology guard
is unchanged. Source settings and applied strengths are recorded per glyph;
registered text/emoji presentation variants share the monochrome drawing.

### Landscapes and travel places

The same pinned Noto Emoji donor supplies 32 landscapes, city views, landmarks,
leisure attractions, maps and compass drawings. The desert, derelict house,
sunset, bridge at night, Ferris wheel and two maps use 512-pixel source rasters;
the bridge, wheel and world map additionally use weight 350 to retain fine
cables, spokes and islands. The other drawings use the standard 400/384 source
settings. All retain the same topology/contour safeguards and strength-1.7
request with recorded automatic reductions. No new palette or licence source
is introduced. Registered presentation sequences share the monochrome drawing.

### Recovered Seal scan drawings

`seal-recovery.json` pins the public-domain Wikimedia page thumbnails for two hundred twelve recovered drawings by hash,
records source edition/page/CCZ sequence, corrected crop bounds, and the licence
metadata returned by Wikimedia. The source locations came from Kaiyuan's
`inferred` and unassigned/rejected crop records, but were independently checked against the official
Unicode 18 chart. The chart is an identity reference only; none of its artwork
is traced or bundled. U+3E34F's proposed crop was rejected because it lacks the
reference form's lower component.

`build_seal_recovery.py` deskews the scans, thresholds and cleans the reviewed
crops, removes a pencil line across U+3F5F1's lower stems, and traces the scan
outlines into a deterministic font. The new font's OFL is retained as
`assets/fonts/licenses/DadSealRecovery-OFL.txt`. The original Kaiyuan source
files and their approval statuses are unchanged. Scan wear and print texture
remain; these provisional native forms still need specialist and style review.
`preview_seal_recovery.py` compares the public scans with compiled outlines and
24-pixel specimens. `docs/seal-gap-review.json` records the remaining 141 gaps.

The second recovery batch covers U+3D4B8, U+3DD2A, U+3DDF2 and U+3DDF3.
The latter two retain their distinct upper-right components. Reviewed pencil
remnants in U+3DDF3 are removed through explicit crop-local cleanup regions
in the source recipe; its glyph strokes are retained.

The next two recoveries, U+3F623 / C-09577 and U+3F625 / C-09579, share
an already pinned page with U+3F622. Corrected crop bounds exclude the column
rule and retain the full right-hand components. Their identities were compared
with the official chart; only historical scan pixels enter the font.
`review_seal_candidates.py` records remaining unassigned crops between known
CCZ neighbours in `docs/seal-crop-candidates.json`. Its reading-order heuristic
only prioritizes manual review; it never assigns a crop to a character.

A further three reviewed crops recover U+3F482 / C-09172, U+3F4F1 / C-09281
and U+3F5CD / C-09494 from pinned pages 31, 36 and 48 of book 7. U+3F510 /
C-09311 matches the reference identity but remains excluded: worn middle
strokes break under tracing, and raising the global threshold merges unrelated
strokes and paper noise. It needs a better source or documented reconstruction.
The shortlist carries prior review outcomes to avoid repeating that failed path.

Book-4 recoveries add U+3E1D1 / C-04492, U+3E298 / C-04689, U+3E2A5 /
C-04702 and U+3E4ED / C-05274. Per-crop cleanup removes a page rule touching
the upper stem tips in C-04702 and reconnects a short scan-wear break in
C-05274's left outer stem using a local radius-3 closing. Tests retain the
reviewed component/hole counts and constrain the repair to its recorded area.

Book 7 page 51 supplies U+3F603 / C-09546, U+3F604 / C-09547 and U+3F605 /
C-09548. Original candidate crops omit or split off left components. Locally
reviewed bounds include each complete compound. The C-09546 recipe clears a
top page rule; all three retain both enclosed left shapes in a regression.

U+3F27D / C-08671 and U+3F27E / C-08672 were found by full-page inspection
on the left half of book 7 page 4 after rejecting their shared right-half
proximity candidate. The first is a headword with one base bar; the second is
an inline form with two. Both identities were compared with the official
reference and the bar distinction is regression-tested. U+3F79D / C-09949
comes from page 73; its crop excludes an adjacent-text speck.

Further book-4 recoveries add U+3E0F4 / C-04272, U+3E1E5 / C-04512,
U+3E1E6 / C-04513 and U+3E56E / C-05401. Bounded closings restore a cup join
and an inner descending stroke in the first two; tests preserve the separate
bottom circle, enclosed spaces and exact repair bounds. U+3E377 / C-04908's
proximity crop was explanatory text. Its correct inline form was found on the
same page, but worn loops and connections do not trace faithfully, so it remains
excluded with its location recorded for future source review.

Book-5 recoveries cover U+3EA3A / C-06607, U+3EA3B / C-06608, U+3EA59 /
C-06637 and U+3EB6D / C-06904. The C-06637 proximity crop was a volume heading
on page 60; the correct headword was manually located on page 59. A bounded
closing restores the lower divider in C-06608's left cross-in-circle component;
a regression retains its four enclosed spaces and limits all repair pixels.
The three contributing pages carry book-5 public-domain metadata evidence.

Book-6 recoveries add U+3ED77 / C-07410, U+3EE93 / C-07687, U+3EFD3 /
C-08000 and U+3F1EE / C-08528 from four pinned pages. The C-08528 proximity
candidate was a column rule; its correct inline drawing was located lower on
the same page. Corrected crops retain whole strokes, and a clear rectangle
removes a top-rule speck from C-08000. No new stroke reconstruction is used.

The last unreviewed proximity candidates recover U+3D66B / C-01617,
U+3ED3A / C-07351, U+3ED3B / C-07352 and U+3EEB2 / C-07717 from three
pinned pages. C-07352 was located in the adjacent column; corrected C-07717
bounds retain its left component. A bounded radius-3 closing repairs one short
break in C-07351's left outer stroke, with a regression constraining added ink.
The two remaining proximity candidates are the previously deferred worn scans.
The candidate report now also preserves 66 neighbour search windows without
unassigned crops, enabling broader page review without repeating those scans.

Full-page searches on already pinned scans add U+3D7A9 / C-01933, U+3E1E3 /
C-04510, U+3EE98 / C-07692 and U+3EEB5 / C-07720. All four match their
chart identities and use ordinary cleanup without reconstructed strokes.
U+3EEB4 / C-07719 was located but remains deferred for worn, disconnected ink.
Review outcomes are retained for empty search windows as well as crop candidates.

Direct comparison of the compiled original source with the reference exposed
two wrong upstream mappings: U+3EEB3 / C-07718 contains only the right component
of C-07719, and U+3EEB6 / C-07721 duplicates C-07720. `build_seal.py` explicitly
excludes both until their correct drawings are recovered. Upstream files and
statuses remain untouched; the exclusions appear in the source-review report.

Correct drawings for U+3EEB3 / C-07718 and U+3EEB6 / C-07721 were located
on book 6 page 46 and added to the recovery font. Corrected crop bounds preserve
the final stem without including text below it. Their wrong original outlines
remain excluded. Full-page review also recovers U+3E0F2 / C-04270, U+3E4EA /
C-05271, U+3F283 / C-08677 and U+3F8FD / C-10293 on already pinned scans.

The original U+3E4E9 / C-05270 outline was a damaged crop of C-05271.
It is now excluded from the original source and replaced by its correct drawing
in the adjacent column. C-05270's page rule is cleared explicitly, and bounded
closings reconnect short worn sections in C-05270/C-05271. A regression preserves
their distinct interior spaces, limits repair pixels and checks the retained
roof stem. Source cmap exclusions and routing to the recovery font are tested.

Further page searches recover U+3D766 / C-01868, U+3D88A / C-02159 and
U+3E21F / C-04569. Four newly pinned scans include their three pages and the
reviewed but deferred U+3DCE1 / C-03248 page. C-03248 sits beside the binding;
expanded crop bounds find the complete area, but shadow merges its thin left
strokes, so the drawing is excluded. Its location and review evidence are in
the gap report.

C-01868 uses a reviewed Otsu offset of +10 (the default remains +20) to avoid
including page-edge shadow while retaining fine spaces. A small bounded closing
repairs its interior bar; a regression preserves two bowl spaces, three ink
components, and the blank area above the drawing. A clear rectangle removes a
pencil fragment beside C-02159. C-04569 uses the standard cleanup unchanged.

Four more pinned book-4 pages supply U+3E25E / C-04632, U+3E394 / C-04936,
U+3E53F / C-05355 and U+3E5AD / C-05462. The original U+3E25D / C-04631
outline was actually C-04632. Its correct adjacent-column drawing is added to
the recovery font and the wrong original mapping is excluded. All five drawings
were checked against the reference identities.

A bounded radius-3 closing reconnects worn parts of C-05355's dense interior;
regressions retain eleven enclosed spaces and limit added ink. C-05462's clear
rectangles remove preceding-text fragments and a pencil spur while preserving
its four ink components and three spaces. Other crops use standard cleanup.

Page-boundary searches locate U+3E332 / C-04840 inline near the end of book 4
page 52 and U+3EA8A / C-06684 at the start of book 5 page 63. Book-5 pages 6
and 33 add U+3E69B / C-05697 and U+3E888 / C-06183. All six reviewed page
images are pinned, including the two boundary pages used to locate the drawings.

The original U+3E69A / C-05696 outline depicts C-05697. Its correct adjacent
headword is added to recovery and the wrong original mapping is excluded.
Bounded closings reconnect short breaks in C-06684's two vertical stems and
C-05696's body; regression tests retain separate components, internal spaces
and unmodified surrounding ink. C-05696's crop also clears page-rule fragments.

The book-six water batch adds U+3EBF8, U+3F15C, U+3F15E and
U+3F161–U+3F163 from two pinned pages. Bounded cleanup removes page rules
and pencil marks while retaining printed component contacts and internal spaces.
The slightly lower threshold for U+3F15E excludes the adjacent column rule.
No glyph strokes were reconstructed in this batch.

A further six-drawing batch recovers U+3EEAF, U+3EEB0, U+3EF2C and
U+3EFC5, and replaces misidentified upstream U+3EEB1 and U+3EFC6. The latter
original crops depicted C-07714 and C-07986 respectively. Correct replacements
come from their neighbouring columns, independently verified against the chart.
A lighter threshold preserves the separate lobes of U+3EF2C; a bounded local
closing repairs a worn notch in U+3EFC6’s long water stem.

The book-six page-93 fish cluster adds U+3F214–U+3F217 and U+3F21D, and
corrects U+3F218. Its old compiled glyph contained part of C-08566 plus a
page rule; the replacement is complete C-08570. Nearby U+3F219–U+3F21C
were checked against their references and retained. Only top page rules are
cleared in this batch; the dense interiors and printed connections survive.

The alternate 1873 CCZ copy in `gzdd-1873.pdf` supplies seventeen drawings
from the leaf absent between the NLC book-seven page-18 neighbours. Wikimedia
identifies this as a facsimile of the Guangdong Sun Yat-sen Library copy in
《廣州大典》; its public-domain metadata and PDF are pinned. PDF page 260,
image object 5721, contains the historical leaf. Each recipe pins its decoded
pixel hash, image dimensions and stencil polarity. Extraction verifies that
object belongs to the recorded page before inversion and twofold resampling.
The gentler opening radius preserves the thinner printed strokes; existing
JPEG recipes retain their original processing. Local clearing removes only
two detached margin fragments. Four damaged forms (U+3F38D–U+3F38F and
U+3F391) remain excluded with their exact source locations recorded.

The book-seven page-7 gate cluster adds U+3F2B8 and U+3F2BB and corrects
U+3F2B9 and U+3F2BA. Those original mappings depicted C-08730 and a
truncated C-08733 respectively. Widened crops preserve both complete outer
stems and the distinct interiors; no local cleanup or reconstruction is used.

Two further inline thread forms, U+3F60E and U+3F711, are recovered from
book-seven pages 53 and 66. Their natural open loops remain open. Page 44
locates U+3F576, but its worn upper strokes cannot yet be recovered reliably;
the pinned scan and review record retain it as a gap.

The remaining four unreviewed CCZ locations yielded U+3F7EC, U+3FB65,
U+3FB66 and U+3FB72. Book-eight licence metadata and pages are pinned.
U+3FB65 uses threshold offset 10 to keep its two components separate and
a bounded radius-three closing to repair its worn middle loop (14 added
pixels). The other three require no local repair. Remaining CCZ gaps have
explicit deferrals; cleaner scans or reconstruction are still needed.

The alternate 1873 copy also recovers U+3DCE1, U+3EEB4 and U+3F576
from embedded images on PDF pages 97, 226 and 273. U+3DCE1 has a recorded
four-pixel-wide separation of a lower stem ink contact (103 pixels removed).
The other two require no local reconstruction. U+3F510 remains damaged,
and the alternate copy repeats the U+3E34F identity mismatch.

`review_seal_editions.py` routes remaining gaps to real source editions using
Unicode 18 UAX #60. TH-Y identifiers enumerate forms from other editions and
are not evidence of a historical THX drawing. Records now support an explicit
`sourceProperty` (default CCZ for existing records), validated against the
pinned source database. The first DYC-only form, U+3D007 / D-00007, comes from
NCL-00920 volume 01 of the 1815 original edition. The PDF and public-domain
metadata are pinned, with an embedded-image pixel hash and exact crop bounds.

U+3D055 / D-00081 is also recovered from NCL-00920 volume 01, page 24,
embedded image 68, without local reconstruction. The adjacent annotation on
D-00015 and a variant crown on D-00098 keep those candidates deferred.

A second original-1815 DYC copy, NLC892-312002095908-313315, supplies
U+3D010 and U+3D087 from pages 18 and 36. Embedded scan images are 5232×4789;
the PDF, metadata and decoded pixels are pinned. A detached thin page ruling
between U+3D010's bars is explicitly removed without altering either bar.
U+3D087 needs no local repair. The similar U+3D06C candidate remains deferred
because its interior crown bar is disconnected at both ends after rule removal.

U+3D0A8 / D-00155 and U+3D122 / D-00260 use NCL volume 01 pages 37
and 53. Comparison with NLC pages 42 and 57 confirms the component forms
and small stroke separations. These authentic printed forms retain those
separations without reconstructing the reference font's joins. No local
cleanup or repair is applied. Exact stroke topology is a source variation;
identity review includes component placement and enclosed-space structure.

U+3D182 / D-00353 and U+3D198 / D-00373 use NCL volume 01 pages 63 and
67, cross-checked against NLC pages 67 and 71. Tight crops preserve the loops,
fine bars and full grass components without local repair. U+3D198's top crop
excludes a detached fragment of the preceding text character.

The first QJZ-only forms, U+3D025 / K-00035, U+3D02C / K-00041 and
U+3D062 / K-00094, come from the 1839 Qi Junzao edition, Commons file
NLC892-411999011197-102941. The public-domain PDF and metadata are pinned.
Recipes identify the main embedded scan images on pages 16 and 19, with
exact decoded-pixel hashes; a separate PDF watermark overlay is not part
of the source image. Tight crops exclude neighboring marks without local
reconstruction. The explicit kSEAL_QJZSrc property prevents using a TH-Y
enumeration alias or another edition's sequence as identity evidence.

U+3D08B / K-00131 uses QJZ page 22, embedded image 265. Its interior fork,
three lower enclosed spaces and right component match the QJZ reference.
The clean printed form requires no local reconstruction and replaces the
previously deferred DYC source choice for this codepoint.

U+3D21C / D-00503 uses NCL volume 01 page 81, image 239. Cross-checking
NLC page 85, image 259 confirms the full grass crowns and separate strokes.
The NCL crop avoids the NLC copy's vertical page ruling through the right
component. No local reconstruction or cleanup is applied.

U+3D2A6 / D-00640 uses NLC volume 01 page 100, image 304, on a leaf absent
between NCL pages 95 and 96. Explicit rectangles remove exposed ruling ends
and a detached speck. The opt-in fillSmallHoles recipe removes enclosed ink
pits of at most 20 doubled pixels; the four meaningful counters remain intact.
This repair does not connect separate strokes or alter open spaces.

U+3D355 / D-00800 and U+3D37A / D-00834 use NCL volume 01 pages 113
and 118, images 335 and 350. The bird components and ten enclosed spaces
of D-00800, and the detached inner bar of D-00834, are preserved without
local reconstruction or cleanup. Crops exclude neighboring text and rulings.

U+3D40D / D-00981 and U+3D414 / D-00986 use NCL volume 01 page 130,
image 386; U+3D46B / D-01063 uses page 138, image 410; U+3D4A0 / D-01115
uses page 142, image 422. No local repair is applied. The small printed
pen lift below D-00986's left crown is retained, along with its four lower
loops. Source hashes, exact edition identities and crop coordinates are pinned.

U+3D4D5 / D-01166 uses NCL volume 01 page 151, image 449. The printed
variant labelled 邁或從萬 retains its walking component, four enclosed cells
and curled lower stroke without local repair. The neighbouring primary form
is not substituted. Source image, crop and edition identity are pinned.

U+3D54F / D-01284 and U+3D5B4 / D-01371 use NCL volume 02, PDF pages
2 and 10 (images 2 and 26). The 1815 public-domain scan and Commons metadata
are pinned by hash. Four upper cells of the walking variant and the tooth
component with its separate curved right stroke survive without local repairs.

U+3D6CF / D-01636, U+3D775 / D-01800 and U+3D7D0 / D-01880 use
NCL volume 02 PDF pages 39, 54 and 62 (images 113, 158 and 182). No local
repair is applied. D-01880 uses threshold offset 0 to preserve the open gap
between its two lower hands; the default offset would fuse their tips.

U+3D893 / D-02072, U+3D8BF / D-02115, U+3D8EF / D-02163 and
U+3D8F3 / D-02167 use NCL volume 02 pages 85, 89 and 95 (images 251,
263 and 281). The first two use threshold offset 0 to preserve narrow gaps.
All four are printed variants, not substitutions of their primary headwords.
No local reconstruction or cleanup is applied.

U+3D951 / D-02257, U+3D9C4 / D-02367 and U+3DA15 / D-02441 use
NCL volume 02 pages 107, 121 and 130 (images 317, 359 and 386). Printed
contacts and pen lifts remain intact, including the central dot inside the
ancient eye form. No local repair is applied. D-02357 remains deferred because
its upper eye enclosure is broken in this scan.

Four DYC bird variants U+3DADD, U+3DADF, U+3DAEA and U+3DB03 use
NCL volume 03 pages 1, 2 and 5, with pinned PDF and Commons metadata.
Crops exclude page rules and preserve the two distinct crests, interior
head marks and paired hanging loops without local reconstruction.

U+3DB6D / D-02772 and U+3DBA2 / D-02821 use NCL volume 03 pages 21
and 27. The latter removes detached commentary above its right component;
both genuine components remain intact. D-02790 and D-02819 remain deferred
because annotations touch their right-hand strokes.

U+3DD51 / D-03239 uses NCL volume 03 page 88, image 260. Its reviewed
minimumComponentArea 20 preserves the genuine central dot; default 70 would
discard it. All other recipes retain their original cutoff. No local repair.

U+3DD63, U+3DD65, U+3DDA4 and U+3DDA5 use NCL volume 03 pages 89,
90, 98 and 99 (D-03256, D-03258, D-03320 and D-03321). Crops exclude
adjacent commentary and rules. Original pen lifts remain; no local repair.

U+3DDCE, U+3DDFC and U+3DE16 use NCL volume 03 pages 104, 110 and
115 (D-03356, D-03401 and D-03426). No local repair; original gaps retained.
The last uses threshold offset 20 to retain fine stem crossbars.

U+3DE79 / D-03520 and U+3DEE5 / D-03625 use NCL volume 03 pages 129 and
138. The latter uses minimumComponentArea 30 to retain the enclosed food bar.
No local repair.

U+3DF72 / D-03759 uses NCL volume 04 page 8, embedded image 20.
The public-domain PDF and metadata are pinned. Its two parts and lower
counter survive without local repair.

U+3E0E7 / D-04123 uses the independently scanned NLC volume06 page48,
embedded image148. Its PDF and public-domain metadata are pinned. Threshold
20, component cutoff200 and enclosed-pit limit100 preserve eight substantial
counters and the printed lower-left interior pen lift.

U+3E02A / D-03937 and U+3E073 / D-04008 use NLC volume06 pages20 and28,
images64 and88. Tight crops and bounded cleanup retain the two enclosed
marks in D-03937 and all five separate parts of D-04008.

U+3E096, U+3E197, U+3E1BC and U+3E1E7 use NCL volume04 pages58,96,102
and108. Tight crops exclude commentary; no local stroke repair is used.

U+3E2E7, U+3E2FD and U+3E310 use NCL volume05 pages2,9 and12. The public-domain
PDF and metadata are pinned. D-04633 uses threshold30 to retain faint printed
connections and its circular enclosure, without local reconstruction.

U+3E33B and U+3E386 use NCL volume05 pages19 and31. D-04751 uses threshold20
to preserve the left enclosed strokes. D-04737 on page29 remains too worn.

U+3E3B1, U+3E3B3 and U+3E3C7 use NCL volume05 pages37,38 and41. U+3E377
uses the clearer NLC volume07 page25; this resolves the worn CCZ and NCL
versions. The alternate PDF and public-domain metadata are pinned.

U+3E452, U+3E462, U+3E51F and U+3E542 use NCL volume05 pages66,69,95 and100.
D-05139 retains its full top stroke with bounded removal of a detached commentary
mark; D-05173 is the rice-bearing variant on page100.

U+3E57F, U+3E5A1 and U+3E605 use NCL volume05 pages105,108 and120.
D-05267 excludes a detached commentary dot through its crop bounds. D-05278
remains deferred: both inspected copies have unresolved stroke damage.

U+3E76D and U+3E7B8 use NCL volume 06 pages 17 and 27. The public-domain
PDF and metadata are pinned. Threshold -10 keeps D-05711 upper stems separate;
threshold 20 preserves the faint right foot of D-05765. No local repairs.

U+3E7ED and U+3E85A use NCL volume 06 pages 36 and 49, opening 1 and
threshold 0. D-05817 excludes the bottom page rule and retains its right arm.
D-05768 and D-05789 remain deferred after review of both NCL and NLC copies.

U+3E8D0 uses NCL volume 06 page68, opening1 and threshold0, preserving
the two components and seven counters of D-06025 without local reconstruction.

U+3E93F uses NCL volume06 page83, opening1 threshold40, retaining six
components and seven counters. Threshold35 loses a counter and45 merges
separate strokes. D-06142 and D-06151 await clearer sources.

U+3E968, U+3EA49, U+3EA7E and U+3EAEE use NCL06 pages87,124,134,146.
D-06173 uses threshold20; the other three use0. All use opening1 without
local reconstruction. Open upper enclosures in D-06435/D-06524 are intentional.

U+3EB15 and U+3EB1F use NCL06 pages151 and154, opening1 with thresholds
0 and30 respectively. D-06570 retains both internal eye bars. D-06525 and
D-06588 remain deferred because of broken strokes or a missing reference mark.

U+3EB35/D-06589 uses pinned public-domain NCL07 page1, opening1 and
threshold0, preserving six separate parts and one counter without repair.

U+3EBB1 and U+3EBBD use NCL07 pages20 and22, opening1/threshold0.
Two detached components and five/six counters are preserved without repairs.

U+3EB9C, U+3EBEA and U+3EC0C use NCL07 pages13,29,33 with opening1
and thresholds0,0,12. The last preserves all eye bars and four separate interior marks.
D-06784 remains deferred because of damaged upper strokes and a false lower loop.

U+3EC4C, U+3EC5D, U+3EC9A and U+3ECA7 use NCL07 pages41,43,49,50,
opening1 and thresholds10,40,0,0. Faint enclosures and dense interior details
are preserved with margins, without local stroke reconstruction.

U+3ED25/D-07054 uses NCL07 page66, opening1/threshold0, preserving
five detached components without local reconstruction. D-07071 and D-07094
remain deferred for a missing reference loop or attached page ruling.

U+3ED68, U+3ED9F and U+3EDBB use NCL07 pages71, 81 and 84.
D-07112 preserves its intentional fire/vessel contact and inner counter at
threshold10; the other two preserve their detached parts at threshold0.

### Timepieces and stationery

The pinned OFL Noto Emoji source supplies seven timepieces and 27 stationery
symbols, with the expressive strength-1.7 treatment and unchanged topology
safeguards. The fine clock-face ticks automatically reduce applied strength;
calendar lettering, pen tips, folder openings and hourglass sand remain source
features. All use weight400; the round pushpin uses 512 pixels to preserve its tiny
highlight, and the others use 384 pixels. Forty-four registered text/emoji
presentation variants share their monochrome drawings. Compiled specimens are
produced with `preview_emoji_faces.py --category timepieces` and `--category stationery`.

### Fruit, vegetables and coloured apples

Thirty-four fruit, vegetable and nut drawings use the pinned Noto Emoji donor
at weight400/384 pixels, with the same guarded expressive treatment. Two more
apple identities share the donor's outlined green-apple shape; its solid red
silhouette is deliberately not used. The red and green body fills reproduce
the PDF's page20 rug and page47 landscape samples. The shared ink and metrics
preserve the apple form while colour carries the Unicode red/green distinction.
The colour extends under the ink to avoid antialiasing seams. The shared outline
source and palette hashes are recorded explicitly in the glyph review and
`apple-palette-source.json`. Registered hot-pepper presentation variants share
the monochrome drawing. Lime sequence support is described below.

### Lime and brown mushroom sequences

The pinned donor supplies exact `🍋‍🟩` and `🍄‍🟫` ligatures. Their complete
Unicode qualification inventories each contain one sequence. The lime colours
only its largest enclosed rind, retaining five white interior regions. The brown
mushroom keeps the donor's solid cap in monochrome fallback; its COLR cap opens
an eight-pixel inset inside the treated silhouette and paints it brown, retaining
the two source highlights and white stem. The cap boundary is derived from the
large stem interior; assertions pin the expected anatomy. The black outer
contour remains in the final ink layer. Green and brown reuse verified PDF
palette records with recorded hashes. This does not permit other fruit/square
combinations or arbitrary variation selectors.

### Additional hand gestures and modifiers

Fourteen additional Noto hand gestures bring the reviewed gesture inventory to
39 bases with 195 exact modifier sequences (plus the independently drawn thumbs-up
family). The new heart-shaped air gap is excluded from skin; three open-wrist
sources use fill-only closure lines at reviewed endpoints. Original ink remains
byte-for-byte identical to the deterministic pen treatment. All source outlines
use weight400/384 pixels and retain the unchanged topology guards. The five
existing PDF-derived skin tones are reused. Twenty exact mixed-tone handshake ZWJ combinations additionally reuse the
handshake outline with two reviewed colour masks. The first hand includes the
small lowest fingertip; the second includes the four curled fingers. The pinned
review-only Noto colour reference and its hash are recorded in
`docs/emoji-pen-translation.md`. Production artwork remains the OFL font donor.

### Clothing and accessories

The same pinned OFL Noto font supplies 38 clothing/accessory drawings, each at
weight400/384px with expressive guarded pen treatment. Four registered variation
forms accompany helmet and graduation cap. Safety vest becomes a standalone
base while remaining the same input component of the service-dog sequence.
No new source file or palette is introduced.

### Electronics, media and lighting

36 further drawings and 34 registered variation forms use the same pinned OFL
Noto source. Reviewed raster exceptions: laptop400/768px, desktop350/768px,
projector400/512px; all others400/384px. The source settings preserve keyboard
keys and reel openings under the unchanged topology guard. No source or palette
file is added.

### Celebration and festival drawings

Eighteen drawings and two admission-ticket presentation variants reuse the
pinned OFL Noto Emoji donor. The sparkler uses weight400/768px, with six asserted
single-pixel raster fragments removed and reduced pressure for its solid tile.
Other drawings use weight400/384px. Source preparation is recorded in the glyph
review; no source or palette file is added. See `docs/emoji-pen-translation.md`.

### Games, toys and art supplies

Twenty-five drawings and eight registered presentation variants reuse the
pinned OFL Noto Emoji donor at weight400/384px. They use the standard expressive
pen treatment with no source-specific changes. The production review records
applied strengths and contour preservation for each drawing.

### Household and scientific objects

Twenty-four household and twelve science/medical drawings reuse the pinned OFL
Noto Emoji donor. All use weight400/384px except the alembic, whose narrow tube
requires 768px to preserve all six enclosed details. Six registered variation
forms accompany bed, sofa and alembic. The existing preservation guards remain
active; no source or palette file is added.

### People and exact skin tones

Eleven people and 55 exact skin-tone forms reuse the pinned OFL Noto Emoji donor
at weight400/384px. Reviewed masks distinguish face/neck skin from white hair,
headwear, bows, teeth, the baby's pacifier and blanket. All tones reuse the
existing PDF-derived palette and share the neutral ink/metrics. U+1F9D1 is
promoted from a blank astronaut input to a visible person; the existing
astronaut forms retain their longer substitutions. No new source file is added.

### Person hair and gender sequences

The remaining 17 neutral person families, 85 toned forms and 24 minimally-qualified
aliases reuse actual ligatures in the pinned OFL Noto font. The compiler checks
every form against its donor glyph name. Blond/red hair use existing verified
PDF yellow/ochre samples, with separate skin and hair masks; white hair remains
white. Original monochrome red-hair ink is retained as fallback. Six hair/gender
inputs are blank shaping components, excluded from visible cmap coverage.

U+3EE47/D-07328 uses NCL07 page105/xref311. A documented three-pixel
separator removes a printing bridge between the heart and enclosing box;
a separate rectangle removes only the page rule. No ink is added. Compiled
source optics retain two parts and two counters.

U+3EE51/D-07337 uses NCL07 page106/xref314, preserving the intentional
heart/west contact and all three counters without local repairs.

U+3EE59/D-07344 uses NCL07 page106/xref314. Two bounded closings add
nine source pixels to reconnect the lower-left coil and its descending heart
join; all four counters and every earlier recovered drawing are preserved.

U+3EE89/D-07391 and U+3EEA6/D-07419 use NCL07 pages112 and115.
The first retains two separate parts and the second three parts, both without
local repairs. Source identities and enlarged/24px compiled forms are reviewed.


Supplementary Jigmo variation shards retain the BMP companion's eight native
CJK combining marks (U+302A..U+302F, U+3099..U+309A), from the same pinned CC0
archive. `tools/font/jigmo_variation_marks.py` verifies identical em and hint
tables before copying exact outlines, metrics, classes and instructions. Only
chunks containing UVS bases receive the marks; per-shard additionalSources
records their provenance. No new mark drawings or anchors are invented. This
repairs those native CJK combinations, not arbitrary cross-font accents.
