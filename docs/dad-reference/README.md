# Dad reference library

Every panel in *The Indispensable Calvin and Hobbes* (the local scan,
`calvin-and-hobbes.pdf`) in which Calvin's dad appears, catalogued so that
drawings of him can be based on how Watterson actually drew him rather than
on one panel. Crops are cut from the scan's full-resolution 1-bit ink layer
(with its solid blacks) and are in `crops/`; `index.json` describes each.

## How it was made

1. Every page was rendered at 110 dpi.
2. A workflow of small-model agents (Claude Haiku, 13 pages each) listed
   every panel with Dad in it: pose, facing, visible parts, size and a
   note.
3. Panels with Dad sitting, kneeling, crouching, bending or lying with his
   legs or feet visible were checked again by Claude Sonnet. It confirmed
   it was Dad, described how his legs, seat and feet are drawn, said what
   each is useful for as a reference, rated it 0–3 and drew a tighter box.

`verified: true` entries passed that second check (61, two rejected). The
rest (239) come from the first pass only. A spot check of 12 of those found
9 correct, 2 wrong (Mom, Calvin) and 1 unclear, so treat them as ~80% right.

## Coverage

300 panels on 82 pages. Poses: standing 111, sitting chair 102, other 35, bending 17, walking 11, sitting floor 10, lying 5, crouching 5, kneeling 3, running 1.

Verified panels useful for: sleeves 52, hands at rest 46, sitting legs 35, shoes 23, crouching legs 7, kneeling or floor legs 2, none 2.

## Best references (verified, quality 2–3)

| Panel | Pose | Facing | Useful for | Quality |
|---|---|---|---|---|
| p8 #1 | kneeling | three quarter left | kneeling or floor legs, shoes, sleeves, hands at rest | 3 |
| p87 #1 | sitting chair | three quarter right | sitting legs, shoes, hands at rest, sleeves | 3 |
| p109 #2 | sitting chair | three quarter left | sitting legs, shoes, hands at rest, sleeves | 3 |
| p109 #3 | sitting chair | three quarter left | sitting legs, shoes, hands at rest, sleeves | 3 |
| p109 #4 | sitting floor | front | sitting legs, shoes, hands at rest, sleeves | 3 |
| p152 #1 | sitting chair | three quarter left | sitting legs, shoes, hands at rest, sleeves | 3 |
| p54 #1 | sitting chair | three quarter left | sitting legs, shoes, sleeves | 2 |
| p95 #14 | sitting chair | front | sitting legs, shoes, hands at rest, sleeves | 2 |
| p101 #1 | sitting chair | three quarter left | sitting legs, shoes, hands at rest | 2 |
| p107 #9 | crouching | three quarter right | crouching legs, shoes, sleeves | 2 |
| p108 #5 | crouching | right | crouching legs, shoes, sleeves | 2 |
| p109 #5 | sitting chair | left | sitting legs, shoes, hands at rest, sleeves | 2 |
| p110 #10 | sitting floor | three quarter right | sleeves, hands at rest | 2 |
| p110 #11 | sitting floor | right | sitting legs, shoes, hands at rest, sleeves | 2 |
| p110 #12 | sitting floor | front | sitting legs, hands at rest, sleeves | 2 |
| p113 #6 | kneeling | left | kneeling or floor legs, hands at rest | 2 |
| p113 #9 | crouching | three quarter left | crouching legs, hands at rest | 2 |
| p115 #1 | sitting floor | three quarter left | sitting legs, hands at rest, sleeves | 2 |
| p115 #2 | sitting chair | left | sitting legs, shoes, hands at rest, sleeves | 2 |
| p115 #3 | sitting chair | left | sitting legs, sleeves, hands at rest | 2 |
| p115 #4 | sitting chair | left | sitting legs, shoes, hands at rest | 2 |
| p115 #6 | sitting floor | left | sitting legs, sleeves, hands at rest | 2 |
| p115 #7 | sitting chair | left | sitting legs, shoes, hands at rest, sleeves | 2 |
| p116 #1 | sitting chair | three quarter right | sitting legs, shoes, hands at rest, sleeves | 2 |
| p116 #3 | sitting chair | left | sitting legs, hands at rest, sleeves | 2 |
| p123 #5 | sitting chair | front | sitting legs, shoes, hands at rest, sleeves | 2 |
| p127 #5 | sitting chair | three quarter left | sitting legs, hands at rest, sleeves | 2 |
| p127 #8 | sitting chair | front | sitting legs, hands at rest, sleeves | 2 |
| p137 #1 | sitting chair | three quarter left | sitting legs, hands at rest, sleeves | 2 |
| p137 #2 | sitting chair | three quarter left | sitting legs, hands at rest, sleeves | 2 |
| p137 #3 | sitting chair | front | sitting legs, sleeves, hands at rest | 2 |
| p137 #4 | bending | unclear | shoes, hands at rest, sleeves | 2 |
| p151 #3 | sitting chair | left | sitting legs, shoes, hands at rest, sleeves | 2 |
| p151 #5 | sitting chair | left | sitting legs, sleeves, hands at rest | 2 |
| p152 #2 | sitting chair | three quarter left | sitting legs, hands at rest, sleeves | 2 |
| p168 #1 | sitting chair | three quarter left | sitting legs, shoes, hands at rest, sleeves | 2 |
| p175 #3 | sitting chair | left | sitting legs, hands at rest, sleeves | 2 |
| p175 #11 | bending | left | crouching legs, sleeves | 2 |
| p235 #7 | sitting chair | left | sitting legs, sleeves | 2 |
| p235 #8 | sitting chair | left | sitting legs, hands at rest, sleeves | 2 |
| p237 #3 | crouching | left | crouching legs, sleeves, hands at rest | 2 |

## Measurements and parts kit

`style.md` gives measurements of Dad across 77 of these drawings (proportions, part sizes and line weights in head widths) and describes the parts kit in `parts/` (`parts.json`), cut from them using the joint and part marks in `annotations.json`.
