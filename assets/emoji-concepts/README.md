# Hand-drawn emoji concepts

## Completed production set

All sixteen selected designs are integrated into the normal `Dad Emoji` colour
font and its existing ink counterpart. The temporary adventure companion fonts
and routing have been removed. The sampler comic **An entirely ordinary
afternoon** includes all sixteen.

Final choices retain the original sheet except for the accepted second snow
goon, CLI box, cleaned Hobbes face and source-art upside-down Hobbes. `production-review.json`
records source hashes, per-glyph artifact keys and final font hashes.
`production-review.png` / `.svg` show the actual compiled outlines at large and
dialogue sizes. Hobbes appears only for 🐯 and 🐅.

The [build pipeline](../../docs/emoji-build-pipeline.md) separates cached drawing
preparation from main-font assembly. Run
`.venv/bin/python tools/font/build_emoji.py`, then
`.venv/bin/python tools/emoji/render_adventure_review.py` and
`.venv/bin/python tools/version_assets.py`. Existing reviewed vector glyphs are
prepared inputs; new drawings use disposable per-glyph caches. One edited atlas
cell invalidates one glyph. The warm full-font build takes about two seconds.

The first front-half 🐅 drawing was `hobbes-front-v1.png`: a close crop of the approved
pounce, retaining the head and reaching paws with the rear torso fading away.
The original full pounce is retained in `hobbes-cleanup-v1/pounce.png`.
The new drawing has slightly thinner contours, and the renderer applies a
0.006em optical stroke instead of the usual 0.018em. Grey rear-edge layers are
retained in the colour font. The edit used the authorized `gpt-image-2` CLI;
the exact prompt is `hobbes-front-v1-prompt.txt`.

`selected-sources.json` records active replacements and optical settings
separately from the preparation recipe. Changing a selected source therefore
does not invalidate unrelated glyphs. The front-half replacement reused fifteen
glyph artifacts, compiled one, and rebuilt the main font pair in 2.6 seconds.

Both Hobbes drawings use a 1024-pixel preparation ceiling, retaining source resolution during
preparation and use fitted curved outlines, converted to native TrueType
quadratics. The earlier 384-pixel polygon tracing made their high-contrast ink
look jagged and low-resolution. That tracing-only pass kept the selected PNG
artwork, proportions, lighter pounce stroke and rear fade unchanged. Curve fitting is enabled only for
the two Hobbes entries in `selected-sources.json`. The before/after compiled
font review is `output/font-review/hobbes-sharpness/comparison.png`; every one
of the other 10,194 glyph records is byte-identical to the preceding build.

The compact redraw `hobbes-compact-v2.png` was rejected: it changed the
anatomy and no longer resembled Watterson's Hobbes. It is retained only as a
rejected experiment. The front-half pounce and subsequent mechanical arm-shortening
study are retained as experiments; neither is the current 🐅 artwork.

The previous 🐅 candidate is `hobbes-upside-down-v1.png`, extracted from the bottom-right
panel of PDF page 246. `tools/emoji/extract_upside_down_hobbes.py` renders both
PDF layers, selects the figure, removes the blue background and neighbouring
shoe, and normalizes scan whites and dark ink. Its original orange fills remain.
No image generation or anatomy changes are applied. The speech balloon hides
the tail tip in the source; the extraction does not invent a continuation.
`hobbes-upside-down-v1.json` records the PDF hash and extraction coordinates.
The existing 1.4× scale and 0.006em optical stroke are retained. 🐯 continues to
use the previously approved face at 1.4× scale and 0.018em stroke.
`output/font-review/hobbes-upside/comparison.png` compares compiled outlines
with the preceding pounce at large and inline dialogue sizes.

The standing 🐅 trial is `hobbes-standing-254-v1.png`, from the top-left panel
of PDF page 254. `tools/emoji/extract_standing_hobbes.py` selects the original
standing figure and normalizes the grey scan paper to white and ink to black.
The source panel cuts off his right arm, and that original cutoff is retained;
no continuation is drawn. Selection coordinates and source hash are recorded in
the accompanying JSON. The upside-down source and its font preview remain
available for comparison. The compiled-font comparison is
`output/font-review/hobbes-standing/comparison.png` (upside-down left,
standing right, followed by the unchanged face).

The selected 🐅 is now `hobbes-upside-down-v2.png`: the user preferred the
page-246 upside-down silhouette at emoji size. The standing pose remains an
alternative. `tools/emoji/clean_upside_down_hobbes.py` applies a conservative
mechanical cleanup to the original extraction: tiny scan pinholes are closed,
ink edges are lightly smoothed and contracted, and residual blue background
fringes are removed. Anatomy and placement are unchanged. The additional
optical stroke is reduced from 0.006em to 0.002em, retaining the 1.4× scale.
The source PNG/hash and cleanup settings are recorded in its JSON.
`output/font-review/hobbes-clean/comparison.png` compares the previous
upside-down extraction (left) with the cleaned version (right).

Current focused validation is recorded in `validation.json`; historical
exploration and rejected candidates are retained below.

## Original concept sheet

Generated with the built-in imagegen tool. The exact prompt is in `prompt-v1.txt`.
`sprite-sheet-v1.png` is a transparent, 4 × 4 concept sheet, not a production
atlas or a font asset. Cell positions describe reading order; the drawings still
need individual cleanup, optical sizing and small-size review before integration.

| Row | Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- | --- |
| 1 | ☃️ Snow goon | ⛄ Snow goon | 🦖 Tyrannosaur | 🦕 Sauropod |
| 2 | 🚀 Rocket | 🛸 Flying saucer | 👽 Alien | 👾 Space monster |
| 3 | 🪐 Ringed planet | ☄️ Comet | 📦 Cardboard contraption | 💣 Bomb |
| 4 | 🐅 Hobbes | 🐯 Hobbes face | 🐉 Dragon | 💀 Skull |

Prioritise snowmen, dinosaurs and space creatures: these offer the strongest
expressive alternatives to generic emoji. Rockets and the cardboard contraption
extend the imaginary-adventure theme. The planet, comet, bomb, dragon and skull
round out the sheet and can follow after the first group.

Character rule: no Calvin or other named Calvin and Hobbes characters. Hobbes
is permitted only for tiger emoji. The two tiger cells are the only named
character designs on this sheet.

## Reference-guided follow-up

- `hobbes-variants-v1.png`: nine variants (six full-body poses, three portraits),
  generated using direct Hobbes crops from PDF pages 4 and 12 as input images.
  The colour seated reference supplied colouring and face proportions; the
  black-and-white standing reference supplied silhouette and ink structure.
- `snow-goon-and-box-v2.png`: a snowman built from snowballs with twig arms,
  and a plain battered cardboard box without machinery. These are replacement
  candidates for the second snow goon and the contraption in the first sheet.
- Exact prompts are saved beside each image. Both sheets used built-in imagegen
  with transparent backgrounds. The original sheet is retained unchanged.

PDF reference crops remain locally in `tmp/pdfs/hobbes-reference/`, alongside
`references.json` recording page numbers and clip rectangles. They are ignored
working material. The Hobbes generation used `colour-seated.png` (page 4) and
`standing.png` (page 12); it did not use the earlier generated Hobbes designs as
character references. The new portraits still need a visual choice by the user
before any font integration.

## Original-art extraction

The generated Hobbes variants were rejected for character fidelity. Use
`hobbes-source-v1/sprite-sheet.png` for the next review instead. It contains
three original poses and three corresponding face crops, extracted directly
from the PDF's high-resolution ink masks on pages 12, 183 and 251. It contains
black source ink on transparency, including transparent interiors, suitable for
monochrome lettering. `sprite-sheet-white-preview.png` displays the same sheet
on white for convenient viewing. Individual transparent sprites and exact page,
crop and clipping provenance are in the same directory. Rebuild with
`.venv/bin/python tools/emoji/extract_hobbes.py`. The extraction removes adjacent
panel lines and scenery, without generating, reposing or reconstructing Hobbes.
These remain review cutouts, not final integrated font glyphs.

The revised snow goon in `snow-goon-and-box-v2.png` was accepted. Its box was
still considered too battered. `box-clean-v3.svg` and its transparent PNG are a
simple programmatic box study based on the open-flap box geometry seen on PDF
pages 183 and 251: straight sides, intact flaps, plain cardboard colour, no
machinery or distress. This is a reconstructed vector study, not extracted
original linework. Imagegen rejected the attempted reference-guided box request,
so no new generated box sheet is claimed.

## Happier original face

The middle source-art Hobbes (page 183) was the preferred candidate; the other
two source poses were rejected. `hobbes-source-v2/face-comparison.png` places
that retained face beside a gentler smiling original face from PDF page 4.
The latter is also saved separately as `happy-face.png`. Both use original ink,
not a generated or redrawn expression. The white preview is for viewing;
transparent sprites remain available. Exact source crop and silhouette points
are recorded in `hobbes-source-v2/provenance.json` and use the `extract` function
in `tools/emoji/extract_hobbes.py`.

For clarity, imagegen's earlier box error was `moderation_blocked`, category
`other`. It did not identify a particular prompt phrase or image feature, and
no specific explanation for the rejection is established.

## Broad grin

`hobbes-source-v3/grinning-face.png` extracts the much broader open-mouth smile
from the "Hooray, Saturday" strip on PDF page 129. Both eyes are visible, though
the head is in slight three-quarter view rather than fully frontal. The source
expression is retained without generation or redrawing. Arms and surrounding
artwork are clipped away; exact provenance is saved beside the PNG. The white
preview is a viewing copy of the transparent black-ink sprite.

## Middle-strip selections

`hobbes-source-v4/face.png` and `pounce.png` are the user's selections from
page 129's middle strip: face from panel 3, action pose from panel 2. They are
extracted from a composite render of both PDF layers, rather than the high
resolution ink mask alone. Grey scan paper is removed while intermediate dark
stroke coverage is retained. Interiors remain transparent. Each has a white
preview and provenance; rebuild with
`.venv/bin/python tools/emoji/extract_hobbes_action.py`.

The source pounce includes an impact burst interrupting the waist and a tail
that reaches the panel boundary. These source limitations are retained, with
no invented continuation or reconstructed anatomy. Nearby lettering, other
characters and scenery are clipped away. The cutouts remain review candidates.

## CLI box revision

`box-cli-v1.png` is a new box candidate generated with the explicitly authorized
imagegen CLI (`gpt-image-2`, high quality, 1024 × 1024, opaque white background).
The two PDF box crops from pages 183 and 251 were supplied as references.
The drawing uses intact flaps, sparse creases, warm cardboard colour and
slightly irregular ink, without the previous machinery or battered surfaces.
The exact unaugmented prompt is `box-cli-v1-prompt.txt`; the original API output
also remains in `output/imagegen/box-cli-v1.png`. Generation took 88 seconds.
