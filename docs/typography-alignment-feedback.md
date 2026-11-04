# Sampler typography refinements — 2026-11-04

The sampler feedback identified real placement and spacing problems as well as
intentional paragraph breaks in the input. This follow-up supersedes the older
alignment/style specimens for these specific cases.

- **Above/below accents:** the extended Latin font now attaches marks to the
  upper or lower fifth of the letter's ink profile. This follows the lean of
  handwritten A, O, V and other letters. Original unaccented outlines and
  advances are unchanged; precomposed and decomposed forms remain equivalent.
- **Line spacing:** use the requested line height as a minimum, growing it only
  for ink that needs more room. The previous calculation added Latin spare
  leading to already-tall native lettering. Empty/whitespace measurements no
  longer inflate the envelope, and a blank paragraph uses one ordinary line.
  Existing explicit blank paragraphs in the examples are retained.
- **Emoji:** each complete emoji sequence receives its own vertical offset,
  centring its actual ink on the lettering's cap-height centre. The existing
  1.4× scale and ink weight remain. Measurement reserves the shifted ink;
  ZWJ sequences, flags and skin-tone sequences stay intact.
- **Greek:** a dedicated handwritten companion keeps WenKai's native letter
  forms and supplies missing polytonic compositions using Noto's native accent
  arrangements. Both source copyrights and OFL notices are retained. All 233
  extended Greek characters match their canonical decompositions in shaping.
- **Cyrillic:** proportional WenKai lettering replaces Klee's fine, full-cell
  forms. A small optical ink expansion, also used for Greek, is included in
  measured bounds. Other alphabets and native combining clusters stay intact.
- **Editing fields:** line height is explicit. They still use browser UI fonts;
  the offline specimens do not establish the behaviour of a particular browser's
  native textarea/font fallback.

At a 40px text size, native specimen measurements for the actual sample words
and graphemes give these speech-envelope heights. These are font/layout
measurements, not browser screenshots.

| Sample | Previous painted line | New painted line | Previous blank row | New blank row |
| --- | ---: | ---: | ---: | ---: |
| Vietnamese | 67.44px | 55.68px | 67.44px | 44px |
| Hebrew | 59.81px | 48.05px | 59.81px | 44px |
| Thai | 66.56px | 54.80px | 66.56px | 44px |
| Korean | 62.02px | 50.26px | 62.02px | 44px |

Review artifacts: `output/font-review/alignment-feedback/review.png`, its SVG
and JSON, and `native-spacing.json`. They use local HarfBuzz shaping and actual
outlines, with runtime-equivalent optical scale, weight and baseline offsets;
they do not execute the complete browser comic renderer.

Validation: 373 JavaScript checks pass. The original lettering/font checks,
new Greek and optical-anchor checks, page/version checks and both independent
CJK companion rebuild cases pass. All 257 copied accent drawings and advances
are identical; companion donor provenance was refreshed, and the two actual
fresh rebuilds reproduce the existing companion binaries. No full multi-hour
Python run was used for this follow-up.

## Second sampler review

The first spacing correction still reserved the speech's tallest glyph envelope
for every wrapped line. Lines now compact to their own measured ink after
wrapping and balancing, with a minimum ordinary line height and a check that
their full boxes remain clear of the artwork. A blank paragraph adds half an
ordinary line of separation. The source paragraph breaks remain intact. This
applies to Vietnamese, Hebrew and mixed-direction speech as well as other prose;
rectangular diagrams retain their grid spacing.

The A's above-mark attachment now follows its uppermost 5% rather than its upper
fifth, bringing the ring toward its apex. Joined Æ/Œ advances now use their
actual ink width plus the reference E's right bearing, instead of fixed widths.
Their CFF widths and horizontal metrics agree. Greek capital kappa uses the
comic's reference K, fitted to the native Greek capital height while retaining
the Greek advance. Other existing native Greek letters remain unchanged.

An opening balloon can join the top border only when it also reaches the right
border. Short opening speech receives room for a complete floating upper curve.
Regression checks cover short Latin and Greek greetings and retained top/right
attachments for broad balloons.

Second-review evidence: `output/font-review/sampler-followup/review.png` (viewed),
its SVG/JSON, and `donor-continuity.json`. All 257 copied accent drawings and
advances remain identical; the 92 marked CJK companion provenance entries were
updated. The local specimen covers the ring, Æ spacing and capital kappa; it
does not execute the browser's comic or textarea rendering.

Final checks for this review: **376 JavaScript tests pass in 14.5 seconds**, and
**25 focused Python font, Greek, optical-anchor, page and version tests pass in
28.3 seconds**. Hard limits were 30 and 40 seconds respectively. Receipts are
`output/font-review/sampler-followup/js-checks.json` and `python-checks.json`.
The original multi-hour Python suite was not rerun.
