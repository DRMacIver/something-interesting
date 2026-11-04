Dad Marked CJK companions — modified 2026-11-03

CJK forms: Jigmo family, CC0. See Jigmo-CC0.txt.
Added accents: the app's hand-treated licensed combining marks, from Google
Noto (Copyright 2022 The Noto Project Authors) and Unicodia Funky (Copyright
2021–2026 Mikhail Merkuryev; Google Noto). See Noto-OFL.txt and
Unicodia-LICENSE-Funky.txt. Fonts renamed and distributed under SIL OFL 1.1.
The original CJK programs remain in their existing independent font assets.

Source drawings, source hashes, derivative names and attachment recipes are
recorded in js/marked-cjk-variant-manifest.js and data/font-sources/marked-cjk.json.
Build with tools/font/build_marked_cjk_variants.py after the ordinary script,
standardized CJK variant and extended lettering builds. No artwork is generated.

Native CJK curves, bearings, advances, vertical metrics, instructions and UVS
remain unchanged. Newly added accents are scaled from 1000 to 1024 em, converted
from CFF cubic curves to quadratic curves (0.05-unit approximation tolerance,
then TrueType integer point quantization) and attached using glyph ink bounds.
Explicit above/below/side classes take priority over the source drawing origin.
Missing-pair corner anchors use the appropriate left/right bounds; attached
classes have no artificial separation. Existing native anchors remain intact.
Native CJK single-mark positions are recorded from original HarfBuzz fallback
and encoded in GPOS; native-only clusters keep the original fonts. These companions
are requested only when the original variant font lacks a requested accent.

Coverage is limited to the app's existing 257 Mn/Me accent drawings. Other
Unicode marks, math/contextual-script variants and arbitrary cross-script
linguistic attachment remain separate work. Source CJK styling and specialist
reader review remain provisional.
