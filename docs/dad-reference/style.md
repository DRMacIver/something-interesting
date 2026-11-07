# How Watterson draws Dad: measurements across the book

Measured on 77 of the reference drawings in this folder (standing, walking,
sitting, crouching and kneeling), not on one panel. Sonnet agents marked
each drawing's head width, joints and part boxes on gridded copies
(`annotations.json`). Every mark was drawn back over its crop and checked
by eye. Head widths and part boxes are reliable. Joints in sitting poses are
rough, so only medians over many drawings are used.

All sizes are in **head widths (Hw)**: the width of his head at the eyes,
from the back of the head to the front of his glasses. In these crops a
head is typically 150–190 scan pixels wide.

## Parts (from part boxes; reliable)

| Part | Long side | Short side | Panel 1 alone |
|---|---|---|---|
| Shoe | 0.94 Hw (IQR 0.69–1.13) | 0.42 Hw (0.35–0.52) | 1.0 × 0.5 |
| Hand | 0.65 Hw (0.50–0.76) | 0.51 Hw (0.37–0.59) | — |
| Shirt sleeve | 1.22 Hw (0.85–1.57) | 0.68 Hw (0.51–0.97) | 1.3 × 0.8 |
| Knee | 0.65 Hw (0.55–0.75) | 0.48 Hw (0.40–0.57) | — |
| Seat | 1.00 Hw (0.85–1.22) | 0.57 Hw (0.50–0.74) | — |
| Trouser leg | 1.62 Hw (1.24–2.03) | 0.96 Hw (0.72–1.30) | — |

## Bones (from joint marks; noisy, medians)

| Bone | Upright | Seated or low | Panel 1 alone |
|---|---|---|---|
| Shoulder–elbow | 0.99 Hw | 1.05 Hw | 1.6 |
| Elbow–wrist | 0.74 Hw | 0.61 Hw | 0.86 |
| Wrist–fingertips | 0.54 Hw | 0.43 Hw | 0.28 |
| Shoulder–hip (torso) | 1.88 Hw | 1.69 Hw | 2.0 |
| Hip–knee | 1.37 Hw | 1.17 Hw | 1.45 |
| Knee–ankle | 1.13 Hw | 0.90 Hw | 1.34 |

Panel 1's long-legged, long-armed Dad sits at the top of the book's range.
Seated and low poses shorten every bone, partly by foreshortening. The
upper arm especially varies (0.8–1.4 Hw), and the agents tended to mark the
shoulder low.

## Line

On thin strokes (excluding solid blacks):

| Stroke | Width | At panel 2's scale (Hw 493 px) |
|---|---|---|
| Typical outline | 0.04 Hw (IQR 0.04–0.04) | about 20 px |
| Thin detail (25th percentile) | 0.03 Hw | about 15 px |
| Heavy contour (90th percentile) | 0.08 Hw (0.07–0.11) | about 40 px |

## Things the library shows

- **Black trousers**, sitting or crouching: a single flat silhouette, broken
  by a clearly rounded knee and a cuff where the leg meets the shoe (pages
  54, 87, 108, 152, 168, 235, 237). White marks are few, short and tapered,
  sitting in folds at the knee or seat.
- **A sole turned towards us** is drawn as a plain rounded oval with one
  line across it for the heel. There is no tread and no inner rim (pages 8,
  95, 123, 127, 151; `parts/shoe/`).
- **Shoes in side view** are long rounded ovals with a scooped opening, a
  couple of lace marks and the trouser cuff over the heel.
- **Kneeling** (pages 8, 113, 175): seat on or above the heels, soles turned
  up behind, the near knee down in front. Page 175 shows the back shoe
  sole-up behind a black-trousered knee.
- **Hands** are four-fingered, with simple rounded fingers and separations
  drawn in from the tips (`parts/hand/`).

## Parts kit

`parts.json` and `parts/<kind>/` hold cut-outs of every marked part:

| Part | Cut-outs |
|---|---|
| Hand | 107 |
| Sleeve | 97 |
| Trouser leg | 94 |
| Shoe | 77 |
| Seat | 58 |
| Knee | 52 |

Each records its source crop, box, side (near or far), orientation note,
the head width it was drawn at (to scale it) and the facing. They can be
posed onto a skeleton with `drawn_legs.transplant`.
