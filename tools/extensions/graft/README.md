# Grafting whole-scene drawings onto the scans

Panels 2 and 3 of the strip are close-ups: Watterson's crop ends at Dad's
chest. Completing them into full scenes needs the rest of Dad, Calvin and
the record player drawn. This directory does that in two halves:

- an image model draws the **whole scene**, freely, from the close-up;
- code **fits that drawing to the scan**, keeps the scan pixel for pixel,
  and gives the rest the scan's ink.

Nothing here draws anatomy in code, and nothing asks the image model to
keep pixels fixed. Both were tried at length and neither works (see
"What didn't work" below).

## Steps

```sh
# 1. candidates: whole-scene drawings from Codex's image generation
uv run tools/extensions/graft/generate.py 2 output/extension-candidates/raw --count 6

# 2. graft each onto the scan, with a fit report beside it
uv run tools/extensions/graft/run.py 2 output/extension-candidates/panel2 output/extension-candidates/raw/p2-*.png

# 3. a contact sheet, best fit first
uv run tools/extensions/graft/sheet.py output/extension-candidates/panel2 output/extension-candidates/sheet-panel2.png
```

Once a drawing is chosen for each panel it goes in `picks/` and is named in
`build.py`, which builds `assets/full-panels/` from the picks:

```sh
uv run tools/extensions/graft/build.py
uv run tools/extensions/reconstruction-v2/build_review.py
```

The comic editor uses the same drawings: `editor.py` cuts its panel
extensions (`tools/extensions/panelN-SIDE.png`) from the exports, and
`tools/build_assets.py` builds the editor's panels from those:

```sh
uv run tools/extensions/graft/editor.py
uv run tools/build_assets.py calvin-and-hobbes.pdf
uv run tools/version_assets.py
```

`generate.py` needs the `codex` CLI. Each image takes a few minutes; four
run at once. The scans come from `../reconstruction-v2/locked-N.png`.

## What the graft does (`graft.py`)

1. **Register.** Finds the scale, turn and shift at which the candidate
   lies over the scan: correlation over a range of scales, then a chamfer
   fit. Each separate figure in the scan (Dad; Calvin's head) then gets a
   fit of its own, and the two are blended by nearness, because the model
   draws each figure at its own size.
2. **Flow.** Measures how the candidate still differs from the scan inside
   the crop (optical flow) and bends it to agree, fading the bend out with
   distance from the crop.
3. **Snap.** Slides the candidate along each edge of the crop so its lines
   leave the crop exactly where the scan's do. A solid black the candidate
   draws too large is slid further, so the crop does not cut it off flat;
   that is kept only when it measurably helps, since a wrong match tears
   the drawing.
4. **Re-ink.** Thins or thickens the candidate's lines to the scan's
   measured weight, cuts them to the scan's 1-bit grid, and smooths them
   with `build_assets.smooth`, the same treatment the scan had.

The scan is pasted back last, untouched.

## The fit report

Every graft writes numbers beside its image, and `sheet.py` ranks by them:

| | |
|---|---|
| `fit_warped` | mean distance between scan ink and candidate ink inside the crop, in scan px. Under 1 is a faithful redrawing; over 5 is a drawing of something else. |
| `seam` | export px along the crop's edge with ink on one side and paper on the other. Lines crossing squarely add almost nothing; a black cut off flat adds its length. |
| `edges_lost`, `edges_extra` | lines that stop, or start, at the crop's edge. Calvin's shirt stripes inflate these in panel 2. |
| `weight_scan`, `weight_before`, `weight_after` | typical line width of the scan, and of the candidate before and after re-inking. |
| `scale` | how much the candidate was enlarged. Near 1 means the model matched the placement image. |

These replace a critic. They say whether a candidate agrees with
Watterson where he can be checked; they do not say whether the drawing
is good. That is judged by eye, from the sheet.

## Fixing a flaw

Regenerate; don't repair. Describe to the model what it got wrong and
make more candidates. The prompts in `prompts/` record what that has
taught so far:

- say what each thing at the crop's edge *is* (the black at panel 2's
  corner is trousers; the white above it is shirt, so the hem is low);
- name what must not be duplicated (the C on Calvin's head is his ear);
- say where the record is (on the turntable), or it floats;
- give sizes against his head, and an enlarged picture of the part
  (`legs-reference.png`): asked only for "long legs", panel 2's thigh came
  out 1.7 head widths from seat to knee where panel 1's Dad needs about 2;
  told "twice his head", it came out 2.0. The same words overshoot in
  panel 3's three-quarter view (2.3 to 2.5), so that prompt says 1.75.
  Shoes stay about 0.8 head widths long whatever is asked, against
  Watterson's 1.15;
- ask for the pose the scan allows: in panel 2 the black under Dad's
  forearm rules out a raised knee, and candidates crouching on their feet
  fit about three times worse than kneeling ones.

## Redrawing one part (`patch.py`)

When a whole candidate is right except for one part, show the model that
region of the grafted panel and ask it to redraw only that part
(`prompts/shoe-edit.txt` is the one used for Dad's shoe; `REGION`,
`LENGTH` and `OUTNAME` are filled in by hand). Give it Watterson's own
drawings of the part as a second image: for the shoe, a sheet of panel 1's
shoes and side views from `docs/dad-reference/parts/shoe/`. `patch.py`
then takes from the redraw only the place where its ink really moved, and
re-inks it; the rest of the panel is untouched. Where the redrawn part
reaches the crop, its lines are slid to meet the scan's exactly, since a
redraw has not been through the graft's own joining (the hem of panel 2's
sleeve arrived thinner and lower than the scan's line).

When the model keeps misreading a place, stop describing it and show it:
erase the wrong strokes from the region, mark the lines that are missing
in red, and ask the model to ink exactly those
(`prompts/sleeve-hem.txt`, `picks/p2-sleeve-hem-guide.png`). All five
redraws made that way followed the guide.

## Checking that a drawing reads

Ask the model to describe the picture, not to rate it. Show it the whole
figure without saying what it is meant to be, and ask what each part is
and whether anything is drawn twice, missing or unidentifiable. Do the
same for the scan before extending it, to learn what Watterson's lines
at the crop's edge are. A sleeve in panel 2 that measured well and joined
the scan to the pixel was described as "a very large sleeve" beside a
second one, with a muddle beneath: which is what it was.

```sh
uv run tools/extensions/graft/patch.py PANEL.png EDIT.png OUT.png X0 Y0 X1 Y1 --protect <scan box>
```

## What didn't work

Recorded so it isn't tried again. Details are in `docs/dad-practice/` and
the git history of `../reconstruction-v2/`.

- **Outpainting** ("keep these pixels, fill the blank part"): the model
  cannot hold pixels fixed, so its output never lined up with the scan.
- **Drawing Dad in code** from splines and measured proportions: three
  rounds, over a hundred agents, never better than 5/10 by its own critic.
- **Transplanting pieces of the scan** (a rotated hand, a flipped shoe):
  the joins never read as one drawing.
- **Hill-climbing on a critic's score**: the score moves by half a point
  to a point on the same image, which is as much as each change gained.
- **Repairing a generated drawing part by part in code**: parts that won
  on their own lost when the whole figure was judged.
- **Watterson's own panel 1 shoe, turned over and tucked behind the knee**
  (tried twice, in code): a walking shoe at 1.15 head widths is taller than
  a kneeling man's folded legs, and upside down it reads as a hook. The
  same shoe mirrored but left upright, with the model tidying only the
  join, does work: see `shoe.py`.
- **Redrawing panel 2's sleeve left of the crop** (four rounds: a tidied
  join, a tube, a boxy sleeve, a new arm): the scan already holds that
  sleeve's front edge and most of its hem, so every new sleeve was a
  second one beside it. The first graft had it right apart from a clumsy
  join; the fix was one hem line and a fold.
- **Having the model redraw the shoe from Watterson's examples**: right
  marks, but soft, tapering shapes that barely read as shoes.
