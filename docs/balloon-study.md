# How Watterson letters dialogue

A study of the speech balloons in *The Indispensable Calvin and Hobbes*,
made to decide how the generator should draw them. It's based on looking
closely at a spread of pages from across the book (pages 31, 76, 121, 166,
211 and 247 in particular, at full scan resolution) and on measuring the
space around about 750 blocks of lettering from every third page.

Measurements are in units of the lettering's capital height ("cap"), which
is about 47 pixels at the scan's resolution and is the same unit the
generator uses for text size.

## The balloon is usually not a closed shape

The single most important thing, and the one the generator got most wrong:
in the great majority of daily-strip panels **the balloon hangs from the
panel border**. The text sits at the top of the panel, and the only line
Watterson draws is one curve that leaves the border, passes under the
text, and goes back into the border. The panel's own border is the top of
the balloon, and often one or both of its sides.

The common forms, roughly in order of frequency:

- **Corner balloon**: text in a top corner. The line leaves the top border,
  curves down and round under the text, and runs into the side border.
  (The original panel 1 of the record strip; "HOW'S YOUR MATH COMING?";
  "THERE! A FULL PITCHER OF…".)
- **Hanging balloon**: text along the top but clear of both sides. Two
  sides come down from the top border and are joined by a curve under the
  text. ("GOOD. VISUALIZE BEING THE ONLY…"; "SO HERE I AM, NOT BEING
  ENTERTAINED.")
- **Full-width balloon**: text across the whole top. The line runs from one
  side border to the other under the text, turning up into the borders at
  each end. (The original panel 2: "COMPARE A POINT ON THE…".)
- **Two speakers**: two hanging or corner balloons side by side at the top,
  in speaking order from left to right, their outlines meeting or slightly
  overlapping between them. ("DID CALVIN GET ON THE BUS?" / "I DIDN'T
  SEE.")
- **Free-standing balloon**: a closed shape, used when the text has to sit
  lower in the panel, typically over busy art. A fat, rounded outline
  hugging the text ("IT WORKS! THE MUCK MONSTERS…"; "FORTIFIED WITH
  CHLOROPHYLL…"). Short remarks get something close to an oval
  ("DEFINITELY HOSTILE."; "YEAH…").
- **No balloon**: lettering loose on open white space, with a single short
  pen stroke towards the speaker. Used where the panel is plain enough not
  to need one. (The original panel 3; "THE WALLS NEED PAINTING…"; "BUT WE
  DON'T HAVE A TV ANYMORE.")

## Where the text goes

- Dialogue starts at the **top of the panel**. Measured gap from the top of
  the lettering to the line above it (border or balloon): median **0.45
  cap** (middle half 0.28–0.63).
- Lines are **left-aligned** with a straight left edge, ragged right.
  Short remarks are often centred. The rag is gentle: line lengths are
  fairly even, and he doesn't leave a lone short word on a line or strand
  the end of a sentence on its own beside the art.
- Text runs nearly the full width of the panel when it needs to, keeping
  about **0.7 cap** from the side borders (median 0.72 on the left, more on
  the ragged right).
- With two speakers, the first speaker's text is on the left (or higher).
- A speaker's balloon sits on their side of the panel where possible, but
  the strong preference is for the top of the panel over being next to
  their head.

## The outline

- Gap from the bottom of the lettering to the balloon line below it:
  median **0.65 cap** (middle half 0.52–1.06).
- The line is a single confident pen stroke, about two thirds the weight
  of the lettering, with no wobble, but **never ruler-straight**: even the
  sides of a boxy balloon bow out slightly, and where a curve meets a
  straighter run there's no corner, just a continuous change of direction.
- It **follows the overall shape of the text in smooth curves**: where the
  last lines are shorter, the outline sweeps in under them in a long curve
  rather than stepping, and the corners are generously rounded (a radius
  of roughly one cap). It never has sharp corners or straight diagonal
  cuts, and it isn't a box.
- Where it meets the panel border it simply runs into it.
- Corners are round, close to circular arcs, and small balloons are
  rounder still: Calvin's three-line "THAT SEEMS REDUCTIVE"-sized balloons
  are nearly as round as they are boxy.
- When the art pushes a balloon aside, it tucks into the far corner of the
  panel rather than pressing up against the speaker: in the original panel
  1 the balloon sits in the top right corner, hanging from both borders,
  leaving room for a short tail to Dad's face.

## Tails

- A **straight narrow wedge**: two lines meeting at a point, about **0.4
  cap** wide where it leaves the balloon and around a cap long (rarely more
  than 1.3). (An earlier version of these notes said tails curve; in this
  strip they don't, and curved ones looked droopy.)
- It leaves the balloon from the part of the outline that gives it the
  clearest path towards the speaker, usually the bottom edge, sometimes
  the side (the original panel 1's tail leaves the balloon's left side,
  pointing at Dad's nose).
- It **points at the speaker's mouth or face**, so its direction alone says
  who is talking, and it **stops short of them**, typically half a cap to
  a cap away. There's always a **clear line of sight** from its tip to the
  face: it goes round heads rather than pointing through them. In the
  original panel 2 Dad's tail comes down beside his head, angled towards
  his face, rather than straight down at his scalp; Calvin's "YEAH…" tail
  comes down to the left of his hair, towards the front of his face,
  rather than onto his hair. A tail that stops at the art, or points
  through it, reads as pointing at that bit of the art.
- Loose lettering gets a single short stroke instead, in the same
  direction.

## What this means for the generator

1. Put dialogue at the top of the panel, 0.45 cap below the border and
   0.7 cap in from the sides, left-aligned.
2. Shape the balloon as a smooth rounded outline around the text, with
   0.65 cap below the last line, ~0.7 cap at the sides and ~0.45 cap above,
   corners rounded at about one cap, and shorter lines swept under in
   curves where the art leaves room.
3. Where the balloon comes within reach of a panel edge, let it run into
   the border instead of drawing a line alongside it, so most balloons
   hang from the top border as Watterson's do.
4. Draw tails as straight narrow wedges, 0.4 cap at the base and up to
   1.3 cap long, from whichever point of the balloon gives the clearest
   path towards the speaker's face, with a clear line of sight to it,
   stopping short of the art.
5. Bow every edge of a balloon slightly, and join curves and straighter
   runs smoothly.
6. Break lines to keep their lengths even, avoiding lone short words, and
   don't strand a last line on its own beside the art.
7. Keep loose lettering with a pen stroke for the panel that has it in the
   original (panel 3).
