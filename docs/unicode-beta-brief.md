# Unicode typography beta: agreed brief

Completed implementation plan: [unicode-beta-plan.md](unicode-beta-plan.md)
(updated 2026-11-04). The agreed beta is complete and ready for human playtesting.
The plan and audit record actual staged verification, local PNG/SVG rendering,
and explicit practical limits. This brief remains the agreed scope and visual
baseline.

This is the persistent handoff for the proposed goal, agreed with the user in
the design conversation on 2026-11-01. Read this before planning or continuing
Unicode work. This file records intent; it does not start goal mode or claim
implementation is complete.

## Objective and scope

Bring the project's typography and renderer to a very solid beta for arbitrary
pasted Unicode text, with an unreasonable commitment to the comic's visual style
and no user configuration. Human review and playtesting are expected afterward;
publication-quality correctness for every script is not the beta requirement.

- Verify the current released Unicode standard when implementation begins and
  pin its version and authoritative data files. Do not assume the version from
  earlier conversation research remains current.
- Cover public-use assigned characters and applicable standardised sequences,
  including emoji sequences and variation behaviour. Define the inventory
  precisely from that release's data; distinguish visible glyphs from controls
  and formatting behaviour. Private-use and unassigned characters have no
  standard drawings: handle them gracefully without inventing semantics.
- Include renderer changes: shaping, bidirectional and mixed-direction text,
  grapheme handling, line breaking, combining marks, emoji, measurement,
  balloon sizing and exported comics. A font-only change is insufficient.
- Reuse and adapt appropriately licensed fonts and shaping resources where
  useful. The user explicitly permits this. Retain required licences and
  attribution, record provenance, and check modification/redistribution terms.
- Use the supplied PDF and image generation for the visual treatment. Generated
  specimen images are style references, not authoritative glyph inventories or
  evidence that a script is rendered correctly.
- Make provisional decisions autonomously and report uncertainties afterward.
  Routine design choices do not require further specimen approval. Seek input
  only for genuine blockers that cannot be resolved provisionally.

## Approved visual directions

Specimens and their generation prompts are in
`output/imagegen/unicode-prototypes/`. See also `design-decisions.json` there.

| Area | Reference | Decision |
| --- | --- | --- |
| Accents | `01-accents.png` | Approved. Same hand-lettered pen character as existing lettering. |
| Emoji | `02-emoji-v2.png` | Approved. Familiar conventional emoji shapes in expressive monochrome ink; do not turn emoji into Calvin. |
| Zalgo | `03-zalgo-v2.png` | Approved. Marks overlap and obscure base letters and neighbouring marks. Do not reserve a clear corridor around the base letters. |
| Egyptian hieroglyphs | `05-hieroglyphs.png` | Approved visual direction; still verify actual sign identities and forms. The sample balloon is not an Egyptian translation. |
| Math | `06-math.png` | Approved visual direction. Preserve symbol and alphabet distinctions. |
| Dense scripts | `07-dense-scripts.png` | Visually accepted. User cannot read these scripts and delegates correctness checks. Prefer finer strokes where needed at dialogue size. |
| Colour-dependent emoji | `08-colour-emoji.png` | Selective colour chosen; exact colours in this comparison are provisional. |

`04-scripts.png` supplies an additional general script style study. Early emoji
and Zalgo sheets are superseded by v2. Do not accidentally build from rejected
variants.

For emoji where colour carries meaning, match colours as closely as possible
to coloured pages of `calvin-and-hobbes.pdf`. PDF pages 13, 17, 20, 26, 35 and 47
(one-based) were visually inspected as useful references. Sample relevant
full-resolution pages during asset creation; preserve meaningful distinctions.
Keep hand-inked outlines. No further palette choice is needed from the user.

Subsequent user feedback on the production emoji: the lines were too clean and
did not look hand drawn. Treat variable pen pressure, irregular contours and
freehand facial features as required style criteria; edge roughness alone is
insufficient. Revisit existing emoji as well as new sheets against this feedback.
The user also rejected `faces-v2.png`. Future emoji generation must include
actual PDF art close-ups as image references, rather than relying on style
names in text or previously generated images alone.

Other delegated directions:

- Preserve native joining, letterforms, mark placement and reading order.
- Keep box drawing, block elements, Braille and text diagrams structurally
  accurate while adapting their appearance to the handwritten style.
- Preserve meaningful distinctions among mathematical bold, italic, script,
  fraktur, monospace, fullwidth and enclosed characters.
- Evaluate lettering at realistic comic size as well as enlarged specimens.

The user criticised generated character faces as too clean and generic,
especially Calvin's, also Dad's. Preserve existing character art wherever
possible. If new character art is necessary, use close-up original PDF
references and explicitly check facial shapes and expressions.

## Validation and honest completion

Build a reproducible pipeline and a versioned coverage audit. Track character
coverage, sequence support, shaping, visual treatment and browser rendering
separately. Ordinary system-font fallback does not count as completed custom
lettering. A placeholder or merely present cmap entry is not proof of correct
rendering. Record any remaining gaps explicitly.

Use authoritative Unicode data and trustworthy script/font references for
validation. Include automated inventory and regression checks, representative
whole-sentence and mixed-script examples, combining-mark stress cases, emoji
sequence checks, layout/export checks, and visual inspection at realistic sizes.
Maintain a review corpus for the user's later playtesting. Report limitations
and provisional decisions without presenting linguistic validation as more
complete than it is.

The aim remains full scoped coverage. Do not silently shrink it to common
scripts or declare completion because fallbacks prevent missing-glyph boxes.
If the beta has genuine unresolved gaps, identify their scope and severity.

## Starting observations (not a finished implementation plan)

- The app is currently static and backend-free; preserve automatic operation.
- Existing lettering is built by `tools/font/build_font.py` from extracted PDF
  glyphs and generated symbol art. See README for extraction/build details.
- `js/comic.js` uppercases input in several places. This must be reviewed for
  semantic preservation, including mathematical alphabets and native scripts.
- `js/layout.js` has whitespace-based splitting and fixed line-height assumptions
  requiring review for arbitrary scripts and extreme combining marks.
- The existing PDF lettering/balloon study is `docs/balloon-study.md`.
- Project checks documented in README: `npm test`, `uv run pytest`, browser
  checks via `tools/checks.html`, and asset hash updates via
  `tools/version_assets.py` when referenced assets change.
- No Unicode implementation changes have been made during this design phase.
  Generated prototypes and this brief are preparatory assets only.

## Continuity during the goal

Keep a persistent implementation plan/progress record alongside this brief.
Record the pinned release, source/licence manifest, completed work, checks and
their outcomes, unresolved gaps, provisional decisions and next concrete steps.
Update it at meaningful milestones so continuation does not depend on recalling
the entire conversation. This brief is the agreed baseline, not a progress log.

### Emoji stroke refinement

The user rated `faces-reference-study-v1.png` "OK to decent" but found its lines
a bit too rough. Preserve that reference-grounded direction while reducing
jagged edges, scratch texture and artificial contour breaks. Aim for confident,
fluid strokes with natural pressure variation. The user approved `faces-reference-study-v2.png` ("Yeah these look OK").
Use this as the production style reference: smooth expressive ink with natural
line-weight variation, using actual comic close-ups in subsequent generations.

### Procedural styling experiment

The user subsequently judged the expanded emoji batches too vector-like and
asked whether a program could automate the translation. Investigate repeatable
stroke treatment on existing drawings instead of continuing image-generation
batches by default. `docs/emoji-pen-translation.md` describes the first opt-in
prototype. The user then rated the programmatic examples "pretty good" and
preferred the expressive ones. Use the expressive setting (requested strength
1.7), retaining automatic reductions that preserve fine details, for the face
glyph treatment. This preference does not remove the need for visual checks.


### Emoji presence in finished comics

The user found many sampler emoji too small and whispery in actual strips.
Judge size and ink weight beside dialogue lettering in finished comics, not
only enlarged sampler sheets. Custom emoji need greater optical size and
stronger ink while retaining readable internal details and meaningful colour.

The user approved the 1.4× custom-emoji size and stronger ink in finished strips
("Yeah, that seems much better"). Keep these optical defaults and judge future
drawings in actual comic strips as well as enlarged specimens.
