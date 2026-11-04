Dad Math Variants is a maintained derivative of NewCMMath-Regular.otf from
NewComputerModern 8.1.1 (2026-06-22), copyright 2019-2026 Antonis Tsolomitis.
The upstream author does not provide support for this derivative.

Changes: renamed family and PostScript names; retained 27 native standardized
variation sequences, added nine historical relation variants, an original kurrent
z drawing and their required
glyphs, combining marks and native
layout closure; converted the subset from OTF to WOFF2. Native outlines and
existing positioning rules are retained. Missing Unicode mark attachment uses
source MATH optical accent points and glyph bounds; combining glyph classes
and same-side stacking are corrected for plain-text rendering. Combining mark
advances are normalized to zero; their original outlines and bearings remain.
No unrelated
UVS is advertised. The additional repair source is tools/font/math_unicode_marks.py.

Historical relations use licensed NewCM inverted-lazy-S curves with affine
transforms and composition, plus original pressure strokes for horizontal and
diagonal arms and the Cartesian default/descender. The semantic references are
WG2 N5334R2 pages 3, 8, 37 and 38; no font programs, chart outlines or page artwork
are extracted from that document. Source: tools/font/math_historical_variants.py.
The kurrent-z form is an original curved-top, descending-loop and rising-diagonal
pen drawing, referenced to WG2 N5333R2 pages 4, 12 and 19. No chart artwork or
embedded font program is used for that drawing.

Derivative source: tools/font/build_math_variants.py and
data/font-sources/newcm.json in this project. The manifest records each exact
input hash, source repository revision and original-source availability.

Complete unmodified upstream package and documentation:
https://ctan.org/pkg/newcomputermodern
https://mirrors.ctan.org/fonts/newcomputermodern.zip
https://git.gnu.org.ua/newcm.git

Original binary and editable source:
https://mirrors.ctan.org/fonts/newcomputermodern/otf/NewCMMath-Regular.otf
https://git.gnu.org.ua/newcm.git (revision
29149c0a75b5386c7e8ccc818a1ea6d2ca1e0128, sfd/NewCMMath-Regular.sfd)

Licence: GUST Font License 1.0 incorporating LPPL 1.3c; supplied alongside
this file as NewCM-GUST.txt and NewCM-LPPL.txt. NewCM-Package-License.txt
identifies which upstream fonts use these terms; the GPL exceptions for other
NewCM families are not used by this derivative.

Derivative manifest:
assets/fonts/dad-math-variants.woff2
js/math-variant-manifest.js
docs/math-variant-review.json
tools/font/build_math_variants.py
data/font-sources/newcm.json

Positional attachment refinement, 2026-11-03: explicit positional combining
classes take priority over unplaced source glyph coordinates. Missing corner
anchors use the appropriate glyph edge; attached classes have no artificial
gap. Original drawings, metrics and existing native anchors are retained.
