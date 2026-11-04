# Programmatic emoji pen treatment

The user found that generated batches drift back toward vector-style drawings,
even with actual comic references. `tools/font/pen_translate.py` is an opt-in,
deterministic prototype for changing stroke finish on existing monochrome art.
It does not generate new expressions. Following the user's preference for the
expressive examples, `emoji_faces.py` applies requested strength 1.7 during font
compilation, with a stable seed per codepoint and recorded reductions. The
standalone CLI still defaults to strength 1.

## Review

`output/font-review/pen-translation/comparison.png` compares four source drawings
with two requested strengths, enlarged and at 24 pixels. Each image reports its
actual applied strength; fragile details can reduce it. The JSON review records
settings, stroke-radius estimates, reductions and fallback status.

## Use

From the repository root:

```sh
.venv/bin/python tools/font/pen_translate.py \
  output/imagegen/emoji-production/faces-playful-v1.png \
  output/font-review/pen-translation/example.png \
  --box 768 350 1152 650 --strength 1 --seed 18

.venv/bin/python tools/font/preview_pen_translate.py
.venv/bin/python -m pytest tests/test_pen_translate.py -q
```

The crop box is left, top, right, bottom in source pixels. Omit it for a single
icon. Pass a different output path: source overwrite is rejected. The output is
a padded, antialiased grayscale PNG and a JSON sidecar recording the input hash,
crop, settings, applied strength, and program hash. Existing monochrome glyph
tracing can consume the result after visual review.

Controls:

- `--strength`: overall requested effect, 0 to 2; default 1.
- `--seed`: repeatable phase selection; default 17.
- `--bend`: gentle deformation relative to drawing size; default 0.012.
- `--pressure`: stroke-width variation relative to typical stroke radius;
  default 0.45.
- `--taper`: thinning near detected narrow stroke endpoints; default 0.25.

## Method

The program converts ink to a signed distance field. Smooth, spatially
correlated displacement bends the shapes slightly. A second smooth field changes
stroke width, with endpoint tapering inferred from the skeleton. It renders at
higher resolution and downsamples to keep edges smooth. There is no independent
pixel noise, edge distress, or image-generation call.

Each candidate must retain one-to-one overlapping ink components, their enclosed
holes, and bounded component areas (50–180% of source). Scan pinholes of fewer
than four pixels do not count as meaningful holes. Border checks prevent
clipping. If a check fails, strength decreases; if no candidate passes, the
program returns the original mask and explicitly reports fallback. These are
geometric safeguards, not proof of linguistic or expressive equivalence.

## Limits and next decisions

This is a procedural finish, not a learned model of Watterson's drawing. It can
vary width and geometry consistently, but cannot decide how to redesign a smile
or whether a brow communicates the intended emotion. Some line-weight changes
are barely visible at 24 pixels. Dense details force conservative settings.

The original drawings and their expression design remain important. The user preferred the expressive comparison. Production face glyphs now use
that treatment; their compiled outlines can be reviewed with
`tools/font/preview_emoji_faces.py`. Style preference is not independent approval
of every glyph. Colour-semantic
emoji need their layers handled separately; the prototype accepts monochrome
input only and does not preserve a colour palette. The production face compiler traces the treated black mask and builds its
white underlayer from the enclosed contours. Licensed object and animal outlines also use this guarded treatment;
category-specific source settings and applied strengths are recorded in the
production glyph review.

## Hand gestures and skin modifiers

`tools/font/emoji_gestures.py` applies the same strength-1.7 treatment to 25
licensed Noto hand gestures. Each base has five exact Unicode skin-modifier
ligatures. The variants share the neutral black outline and metrics; only a
separate skin layer changes colour, using the existing PDF-derived five-tone
palette. The fill extends beneath the black strokes to avoid white
antialiasing seams between independently traced edges. Neutral drawings
remain monochrome.

A largest-interior fill is insufficient for hands: folded fingers often form
separate enclosed regions. The reviewed masks therefore fill all skin regions
while keeping the OK-sign circle and small gaps between crossed/pinched fingers
white. The pinched-fingers donor has an open wrist; the compiler closes the fill
mask between two pinned endpoints without adding an ink stroke. These choices
are specific to the pinned source and must be reviewed if that source changes.

Reproduce the compiled specimens with `preview_emoji_faces.py --category gestures`
and `--category gesture-tones`. Tests check exact Unicode modifier membership,
unchanged variant ink, shared metrics, palette indices and air-gap preservation.

The four selectively coloured donor faces also paint colour underneath their
final ink layer. Their largest enclosed region receives colour; every other
enclosed region remains white. Tests check the source masks and compiled layer
overlap, so future contour changes cannot silently reintroduce pale seams or
colour the teeth, sweat and ice details.

## Timepieces and stationery

The licensed-object path now includes seven timepieces and 27 stationery
symbols. The clock-face ticks force conservative automatic reductions;
pen tips, calendar lettering, folder openings and hourglass sand remain part
of the source geometry. The round pushpin uses a 512-pixel source raster to
retain its small highlight through outline simplification; the remaining
new drawings use 384 pixels. The compiled hourglass regression checks that
only the running hourglass retains sand in its upper chamber.

## Produce and apple colour

The licensed path adds 34 fruit, vegetable and nut symbols. Red and green
apples share a single treated outline from the green-apple donor, because the
red donor is a solid silhouette. The body receives red or green sampled from
the comic PDF; the shared black ink paints last. Provenance records this source
adaptation, and regression checks enforce shared outlines/metrics, distinct
sampled colours, and underpaint overlap. No new generated raster is involved.

## Coloured produce sequences

`emoji_sequence_colour.py` handles lime rind colour and the brown-mushroom cap
for their exact registered sequences. The mushroom donor's monochrome cap is
solid; its COLR rendering exposes a brown interior inside the treated contour,
while preserving white highlights and stem. This is an explicit colour-layer
conversion after pen treatment. The monochrome fallback remains the original
solid drawing, and the review record names that difference. The largest stem
hole locates the cap boundary; topology and white-region tests reject changed
source anatomy instead of colouring unrelated regions.

The gesture inventory now includes 39 bases, adding directional and pushing
hands, heart hands, clapping, open/raised/folded hands, cupped palms and handshake.
Heart hands leave the enclosed heart white. Pushing hands and raised hands need
fill-only wrist closures at reviewed source endpoints; the black ink is unchanged.
The original 25 gestures retain their existing mask rules. Five uniform skin-tone
variants are supported for each new base. Twenty mixed-tone handshake ZWJ sequences now use separate colour layers.
The shared handshake outline and metrics remain unchanged. The first modifier
colours the left-entering hand: its large palm and lowest small fingertip.
The second colours the upper thumb/right wrist and four curled fingers.

Region identity was visually checked against the official Noto colour artwork:
https://github.com/googlefonts/noto-emoji/blob/99701e07d3d1fe1bdbcdb14964547f0fd592966f/2D/svg/emoji_u1faf1_1f3fb_200d_1faf2_1f3ff.svg
(review-only SVG SHA256: c7a49092e8c85b37a033f85170a7ebded74ce32fb99dbbb7d696e565183234ed).
The reference is not copied into the font. Drawings remain derived from the
pinned OFL monochrome donor; colours use the existing PDF-sampled skin palette.
Anatomical probes check all seven interior regions in both raster masks and
compiled outlines. Unsupported equal-tone ZWJ forms are not advertised; the
five uniform-tone handshake modifier sequences remain supported separately.

## Clothing and accessories

The clothing category adds 38 reviewed Noto drawings at weight400/384px,
including hats, garments, footwear, bags and protective clothing. All retain
source components and counters after strength1.7 treatment and tracing.
The safety vest is promoted from a blank service-dog component to a standalone
custom drawing; compound construction reuses that cmap entry for the existing
service-dog ligature. Registered helmet/graduation-cap variation forms are
included. Review compiled output with `preview_emoji_faces.py --category clothing`.

## Electronics, media and lighting

36 objects use the same expressive treatment. Fine keyboards require larger
source rasters: laptop weight400/768px, desktop weight350/768px. The film
projector uses weight400/512px to preserve reel openings. The automatic guard
reduces treatment to about0.30 for these drawings while retaining each source
component and counter. Other objects use the default weight400/384px. Registered
presentation forms remain exact; use `preview_emoji_faces.py --category electronics`
for the enlarged/24px compiled review sheet.

## Celebration and festival drawings

Eighteen celebration drawings use the same expressive treatment: ribbons, gifts,
jack-o-lantern, Christmas tree, fireworks, sparkler, firecracker, balloon, party
popper, confetti, Tanabata and pine decorations, dolls, carp streamer, wind chime,
moon-viewing ceremony and two tickets. Admission tickets also include both
registered presentation selectors.

The sparkler donor is a white knockout drawing in a dark tile. At weight400 and
768px, its raster has six isolated single-pixel antialiasing fragments along
white diagonals. A source-specific assertion checks that exact structure before
removing those fragments; the tile and white rays remain. Broad solid ink uses
pressure0.02 and no endpoint taper, as with the existing new-moon treatment.
All other celebration sources use weight400/384px and the default pen settings.
The normal topology and compiled-contour checks still apply after preparation.

## Games, toys and art supplies

Twenty-five recreation drawings reuse the pinned monochrome donor at
weight400/384px: target, yo-yo, kite, billiards, crystal ball, wand, gamepad,
joystick, slot machine, die, jigsaw, teddy bear, piñata, mirror ball, nesting
dolls, joker and flower cards, theatre masks, framed picture, palette, thread,
needle, yarn, knot and circus tent. All pass the normal topology and compiled
contour checks with the default expressive settings. Eight registered selectors
accompany theatre masks, gamepad, joystick and framed picture. No additional
colour palette or source-specific raster adjustment is introduced.

### Newer donor source investigation (2026-11-02)

The Google Fonts commits API for `ofl/notoemoji` returned the already pinned
revision `8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5`; it does not resolve the
23 missing newer emoji. The Noto Emoji GitHub release page advertises a Unicode
18 release, but API requests for its `v2026-09-24-unicode18_0/fonts` directory
and the default `fonts` directory both returned HTTP404 in this environment.
The corresponding Fuchsia mirror tag could not be opened through web retrieval.
No new font, hash or production coverage is claimed from that release listing.
Continue source investigation separately from the verified existing donor.

## Household and scientific objects

Twenty-four household drawings and twelve science/medical objects use the
existing pinned monochrome donor and expressive treatment. Six registered
presentation variants cover the bed, sofa and alembic. The alembic needs
weight400/768px to retain all six enclosed details: at 384/512px, source
rasterisation merges a narrow opening and no expressive candidate passes.
The higher resolution preserves the tube and permits applied strength1.275.
Other drawings use weight400/384px and the default treatment settings.

The licensed-object compiler now rejects an unchanged fallback immediately.
Previously, the post-build tests rejected zero applied strength; the compiler
now checks the same production requirement before emitting any outlines.

## People and skin-tone layers

`tools/font/emoji_people.py` adds eleven neutral people and their 55 exact
skin-tone sequences: baby, child, boy, girl, person, man, woman, older person,
old man, old woman and bearded person. All use the pinned Noto weight400/384px
outline and expressive treatment. The five existing PDF-derived skin colours
are reused; neutral faces remain monochrome.

Connected regions were visually reviewed in the treated ink. Only the baby's
face is skin: pacifier and both blanket regions remain white. The boy's three
cap panels and girl's two bows remain white. Older people's white hair is kept
separate from the face. The bearded person's face and neck are skin, while the
teeth remain white. Region counts are asserted, and the skin mask extends three
pixels under black ink while excluding every non-skin white region. Every tone
shares the neutral glyph's black outline, advance and layering geometry.

U+1F9D1 becomes a visible standalone drawing while keeping its existing internal
`person` glyph name. Longer astronaut substitutions precede the new simple tone
substitutions, so adjacent standalone people cannot consume the astronaut's
modifier or joiner. Anatomical probes test both raster masks and compiled skin
outlines, alongside ligature order and repeated/adjacent shaping.

## Remaining person hair and gender forms

`emoji_person_forms.py` compiles the remaining 17 neutral person forms, their
85 skin-tone forms and the 24 registered minimally-qualified aliases. Drawings
come from actual donor ligatures, with every tone/qualification form verified
to resolve to the same donor drawing as its neutral family. Longer substitutions
precede simple people-tone rules. Hair/gender inputs remain shaping components,
not standalone visible coverage claims.

Blond hair uses the verified page17 yellow sample (180,157,60); red hair uses the
page13 ochre/orange sample (174,104,29), both from `heart-palette-source.json`.
The full-resolution render hashes and sampled medians were rechecked. These are
provisional hair colours drawn from the approved comic palette. White hair stays
white; curly hair and beards retain black ink. The red-haired donor's solid hair
is opened only inside the largest thick ink component, at a nine-pixel inset.
This retains the face border and disconnected eye/mouth features. The original
complete solid ink remains the monochrome fallback. Skin, hair fill and final
ink are independent layers shared across the five tones.

The monochrome donor deliberately uses `personWithCurlyHair` for all three
curly-haired gender forms, and `personBald` for all three bald forms. Exact
sequence identity is retained, but these groups share the donor's underlying
appearance. This is a source-design limitation, not proof of visually distinct
gender representation; retain it in subsequent typography review.

## Occupation forms

`emoji_professions.py` extends the same requested strength 1.7 to 47 occupation
families: health workers, students, teachers, judges, farmers, cooks, mechanics,
factory workers, office workers, scientists, technologists, singers, artists,
pilots, firefighters, and the man/woman astronaut forms. The existing neutral
person astronaut stays on its earlier drawing. Five tones and qualification
aliases give 336 additional exact sequences, representing 282 fully-qualified
forms. Every alias must shape to its family's actual pinned donor ligature.

Exposed-skin masks were reviewed separately from uniforms and equipment. Teacher
spectacles allow the skin colour through; science goggles, hats, helmets,
stethoscopes, tools, computers, microphones, palettes and space suits stay white.
The region review records source coordinates for independent compiled-layer
checks. The neutral firefighter and woman cook use 768px source rasters: 384px
respectively forced an untreated fallback and lost a small compiled contour.
The builder rejects untreated fallback and missing compiled components/counters.

The donor shares occupation drawings across gender forms. Stable sequence seeds
vary their pen treatment, but do not create distinct gender-specific anatomy.
This remains a provisional source-design limitation for visual review.

## Detailed SVG source experiment

The upstream Noto Emoji repository now stores artwork under `2D/svg` and built
fonts under `2D/fonts`; the earlier `/fonts` lookup could not find these relocated
files. Pinned revision `99701e07d3d1fe1bdbcdb14964547f0fd592966f` has detailed
pregnancy and baby-feeding SVGs. Seven candidates and the directory licence were
downloaded and verified against their Git blob identities. The probe manifest
is `docs/noto-svg-source-probe.json`; these files are not production coverage.
The SVG directory explicitly uses Apache-2.0, unlike the OFL font directory.
The full Apache licence and an attribution/modification notice are retained as
`NotoEmoji-SVG-Apache-2.0.txt` and `NotoEmoji-SVG-NOTICE.txt` under
`assets/fonts/licenses/`; the existing font licence remains separate.

`prototype_emoji_svg.py` converts the pinned pregnant-woman drawing using a
reviewed path recipe: remove fill-only shadows, preserve hair/facial/finger ink,
and add black outlines to white clothing and skin regions. It is not a generic
anatomical classifier; each additional drawing needs a reviewed recipe. At
384px the guard rejects all treatment attempts. At 768px, a 1.8-unit SVG stroke
preserves three components and seven counters at applied strength 0.4034 from
requested 1.7; a 2.2-unit stroke backs off further to 0.3026. Further review selected a finer 1.3-unit outline at 768px to keep fingers
clearer. This applies strengths 0.5379, 1.275 and 1.275 respectively to the
woman, man and neutral pregnancy figures, preserving three components and seven
counters in each. Skin-tone layers, compiled geometry and production integration
remain unfinished. The experiments are explicitly labelled as such.

The pinned recursive upstream tree also includes SVG filenames for all 23 newer
Common emoji absent from the monochrome donor: landslide, lighthouse, harp,
trombone, meteor, eraser, net, treasure chest, shovel, leafless tree, fingerprint,
hairy creature, monarch butterfly, orca, root vegetable, pickle, splatter, bags
under eyes, distorted face, cracking face, fight cloud and both directional
thumbs. File presence is only a source lead, not accepted drawing or coverage
proof; download, identity, licence, conversion and visual checks are still due.


`preview_emoji_svg_paths.py` renders individually indexed painted paths for the
seven detailed candidates, after verifying their source hashes. This supports
reviewed anatomical recipes without guessing from path colours alone. The
conversion prototype now has separate recipes for all three pregnancy figures
and man feeding baby. It removes inline fill styles before applying ink/white
fills and supports polygons as well as paths. The feeding recipe still needs
further small-size and colour-mask review; the other three feeding drawings
need recipes. None of these detailed experiments is registered in the font.


`preview_detailed_svg_prototype.py` traces and renders the four current detailed
recipes without modifying the font. The three pregnancy outlines preserve all
10 expected contours each; man feeding baby preserves 32 after treating the
blanket fold as an outline rather than a large black shadow. The compiled probe
was reviewed enlarged and at 24px. Reports retain source, recipe and program
hashes; these limited checks still do not establish finished production glyphs.


## Detailed SVG production conversion

The seven pregnancy/feeding drawings from the experiment above now have
production recipes in `emoji_svg.py`, registered in
`data/font-sources/noto-emoji-svg.json`. `emoji_detailed_people.py` builds their
42 neutral/skin-tone forms. The prototype command delegates to the same
converter. Earlier experiment-only statements describe the preceding checkpoint.

Each recipe identifies retained outlines, solid hair/facial/finger ink, and
exposed-skin paths. The converter rasterises at 768px with 1.3-unit outlines,
requests expressive strength 1.7, and reduces treatment until the feature guard
passes. Skin selection uses overlap with a separately rendered anatomical mask;
reviewed region counts and identities are asserted. Clothing, bottles, caps and
blankets remain white. All tones share the same ink contours and metrics.

Breastfeeding and woman-feeding source rasters contain sub-four-pixel pinholes
at path intersections. Only these tiny holes are filled, with an explicit
feature-equivalence check; strokes are never closed globally. Woman feeding
also needs pressure variation reduced to 0.1 and taper disabled. Its bend
strength still reaches 0.7172. The other applied strengths are 1.275 for neutral
feeding, 0.95625 for breastfeeding, 0.53789 for pregnant woman, 1.275 for pregnant
man/person, and 0.95625 for man feeding. All seven retain their expected compiled
component/counter contour counts. Independent anatomical probes check coloured
skin and white equipment in both raster masks and compiled layers.


## Newer SVG source candidates

All 23 newer SVGs mentioned above have now been downloaded from the same pinned
revision, checked against Git blob identities and SHA-256, and visually
identified in the browser. `docs/new-emoji-svg-source-probe.json` records them;
they are not yet registered production sources. The HTML specimen under
`output/font-review/pen-translation/new-svg-source-candidates.html` preserves
native SVG gradients. PyMuPDF renders some of those gradients black, so the
PNG source contact sheet is not an accurate colour reference.

`prototype_new_emoji_svg.py` provides preliminary ink recipes for leafless tree,
fingerprint and pickle. The tree keeps all four branch/trunk silhouettes as
white outlined shapes. Fingerprint removes the coloured background and keeps
all eleven ridge paths. Pickle retains the body and five dark interior details,
omitting highlight paint. At 768px the recipes apply strengths 0.71719, 0.95625
and 1.7 respectively, without fallback. The initial tree outline was too thin
in compiled small-size review; its SVG stroke is now 2.2 units, and pickle uses
1.8 units. Raster and traced specimens were reviewed enlarged and at 24px;
compiled contour counts are 6, 10 and 8, preserving the measured components and
counters. These experiments do not modify the font; identity tests and
production integration remain due.


Production validation for the seven detailed SVG families passed: 170 emoji
font tests (including byte-identical font/manifest rebuild), 273 JavaScript
tests, 6 inventory tests and 336 browser scenarios. All 42 neutral/tone glyphs
were reviewed in compiled sheets; browser specimens exercise tones and adjacent
plain-person sequences. This validates the current batch, not the whole
Unicode brief or every source design choice.


## Optical size and weight in comic dialogue

After the user found sampler drawings small and whispery in finished strips,
custom emoji now render at 1.4 times the dialogue font size. Measurement uses
that same size for wrapping, line height, balloon fitting and exports. Ordinary
text and system fallback emoji retain their existing size. A black stroke of
0.018 times the enlarged font size adds optical weight, with half the stroke
width included in all measured ink extents and round joins to prevent spikes.

Canvas stroking of a COLR font can paint its colour layers again, changing their
appearance. `build_emoji_ink.py` therefore derives a separately named monochrome
companion by removing only COLR/CPAL and renaming the font. All outlines,
metrics, cmap and GSUB data remain identical. The font loader waits for both
fonts before rendering and retries failed companion loads. Colour is painted
with Dad Emoji; the stroke uses Dad Emoji Ink. The companion adds 645,224 bytes
on first custom-emoji use and is cached thereafter. The production builder
regenerates it and records its content hash in the emoji manifest.

`tools/emoji-optical-review.html` compares original size, enlarged size, and
enlarged size plus black optical weight. Review covered faces, tools, animals,
plants, detailed people, skin tones and colour-dependent symbols at dialogue
size. `emoji-dialogue-scale` in the full browser harness exercises mixed speech
in actual panels. A companion test verifies byte-identical geometry/shaping and
reproduction; loader tests ensure exports cannot race companion loading.


## New SVG object preparation

`emoji_new_svg.py` promotes the reviewed leafless tree, fingerprint and pickle
recipes to a registered production source manifest. It preserves the original
recipe geometry and deterministic feature-guarded treatment. The CLI prototype
now delegates to that converter. Additional source candidates remain separate.

`prototype_svg_objects.py` prepares harp, trombone and shovel without modifying
the font. It retains clipping definitions while removing unselected visible
paint, avoiding accidental interpretation of definition paths as painted ink.
Harp keeps its frame, strings and tuning pins; trombone keeps tubing, braces,
bell and bell opening; shovel keeps blade, shaft, grip and blade crease. At
768px they apply strengths 1.275, 1.7 and 0.95625, with 10, 14 and 7 traced
contours respectively, matching measured components plus counters. Review sheets
show enlarged outlines and the approved 1.4× size with 0.018-em optical stroke
at 24px dialogue size. Production registration, independent tests and finished
comic review remain due for these three prototypes.


The tree/fingerprint/pickle production batch passed six focused font tests
(including all 2,301 advertised sequences), 276 JavaScript tests, six inventory
tests and 338 browser scenarios. Compiled sheets and mixed comic dialogue were
visually reviewed with the approved optical size/weight. The source registry
now verifies 11,376 files. The twenty other newer SVG candidates remain open.


## Harp, trombone and shovel production

The three object recipes are now production entries in `emoji_new_svg.py` and
`noto-emoji-new-svg.json`. The converter preserves SVG definitions and clipping
references while selecting visible paint; the earlier tree/fingerprint/pickle
recipes continue through the same path. Harp, trombone and shovel retain 10,
14 and 7 contours, with applied strengths 1.275, 1.7 and 0.95625. The compiled
sheet and actual comic fixture were reviewed with the approved optical defaults.

Separate face prototypes now cover face with bags under eyes, distorted face
and cracking face. They retain 9/7/26 contours and apply strength 1.7, with the
half-closed eyes, eye bags, exaggerated eyes and cracks preserved. Nature
prototypes cover root vegetable, splatter and orca. The vegetable retains a
source shadow and root marks as solid ink. Orca keeps its black/white pattern,
with a white outline around the tiny black eye and a white flipper boundary;
six one-pixel raster pinholes are filled only after a feature-equivalence
assertion. The resulting five traced contours match its meaningful components
and counters. These source-specific treatments still need production tests.
These six SVG experiments do not count toward coverage.

`prototype_transport_expansion.py` reviews 21 remaining licensed transport
symbols, including aircraft, rail variants, scooters, wheel, ring buoy and oil
drum. The oncoming taxi needs donor weight 350 to preserve its roof checkerboard
while allowing positive treatment; the others use weight 400. These are source/
compiled candidates only, pending registration, sequence rules and finished-strip
checks. Promoting rocket requires retaining the astronaut ligatures while making
the currently blank rocket shaping component a visible standalone drawing.


The harp/trombone/shovel production batch passed ten focused font tests,
including exact colour-font/manifest rebuilding and all 2,304 advertised
sequences; 276 JavaScript tests, six inventory tests, 11,379 source hashes and
339 browser scenarios also pass. The twenty-one transport candidates all now
retain their expected contours with positive treatment at 384px. The taxi uses
weight 350 and applied strength 0.30256; the other twenty use weight 400.

### Reproducible local cache

`pen_translate.translate` caches its deterministic pixel result and original
report under `build/font-cache/pen/`. Keys include the input mask and settings,
translation and cache implementation hashes, Python/platform, and NumPy, SciPy,
scikit-image and Pillow versions. Cache hits return fresh reports and identical
pixels; they do not add machine-specific hit/miss fields to glyph provenance.
Entries use checksummed, compressed arrays without pickle and atomic writes.
Missing, corrupt or unwritable cache entries fall back to computation.

The cache is disposable. Set `DAD_DISABLE_PEN_CACHE=1` when an explicitly
uncached verification is needed. The first build still computes each new
input; subsequent builds reuse unchanged treatments. This does not replace
source checks, contour checks, compiled-font tests or actual-strip review.

### Clipped hand-object sources

The hand-prop converter (`tools/font/emoji_hand_props_svg.py`) needs
`rsvg-convert` on `PATH`. It was reviewed with librsvg 2.62.2; its version and
linked-library versions are recorded in each treatment report. This is a build
and review dependency, not a browser dependency. Its production output remains subject to compiled-font and actual-strip checks.

The writing hand uses SVG clipping to put the pen behind the thumb. Converting
that SVG through PDF lost the overlap during visual review. The converter uses
librsvg, rasterizes the clipped pen alone, and traces its visible silhouette
before adding the ink outline. This closes the pen's boundary at the thumb and
prevents the skin fill from leaking into its shaft. Skin, polish and uncoloured
objects remain separate masks. Reference tone drawings are retained alongside
the base sources; they do not count as additional custom artwork by themselves.
