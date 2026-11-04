Dad Combining Outlines — modified 2026-11-03

Native nonspacing mark drawings exported for dynamic canvas composition.
The catalog now also retains 25,087 font/mark identities across 191 native
variation families, with 506 unique normalized drawings. Geometry is shared
without merging source glyph identity or provenance. All 300 source records
retain their source font hash and notices; Jigmo CC0 notices are explicitly
linked where its original name table has no licence text.
The effective derivative name is Dad Combining Outlines. Original author,
copyright, licence, licence URL, source glyph and source font SHA-256 are
retained per drawing/source in js/combining-outline-manifest.js. Original
fonts and their supplied licences remain in assets/fonts/licenses/ and the
pinned data/font-sources manifests. Source notices missing from three fonts'
name tables are included verbatim from their supplied OFL files in the catalog.

Build: tools/font/build_combining_outlines.py, after the ordinary script and
extended lettering builds. Coordinates are normalized to one em, flipped to
canvas coordinates and serialized to six decimal places. No reference chart
artwork is copied. Hand-treated accents retain the existing app drawings;
handwritten WenKai forms supply the circle and square enclosures. Other
marks retain their licensed native source forms, with style review provisional.

There are 1,840 non-default-ignorable Mn/Me records, with 1,838 nonempty paths.
Two Gondi virama records are empty native context glyphs; they remain on the
native shaping path. 263 default-ignorable marks are separately classified as
behaviour, including variation selectors; they are not invented drawings.

Renderer transforms fit enclosures around preceding base/mark ink and span
double marks across two bases. Simple rings transform their outer and inner
contours separately to retain border weight as they grow. Keycap fitting uses
the actual writing surface rather than the decorative recess. Native base glyphs are shaped with their font
and retain their size; they are not stretched. The paths do not replace native
joining or contextual script shaping. Unsupported interactions, CGJ-sensitive
combinations, emoji bases and bounded pathological inputs keep native handling.
For nonjoining variation clusters with a missing mark, the supported native
prefix stays shaped intact. Following marks are placed in canonical order;
native marks in that tail retain their exact selected-font outline. Their
position is geometric when a foreign mark interrupts native shaping, not a
claim of complete native linguistic attachment. All complete native clusters
keep their original shaping path.
The complete Unicode beta and broader script/style validation remain open.
