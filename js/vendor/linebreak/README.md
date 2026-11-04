# Line breaking

Adapted from https://github.com/cto-af/linebreak at the revision recorded in
`upstream.json`, under the accompanying MIT licence. That manifest also records
hashes of the original downloaded source files.

The rule/state engine is retained. `LineBreak.js` and `EastAsianWidth.js` are
local adapters to generated Unicode 18.0.0 range tables; line-break classes use
string identifiers. Host Unicode regular expressions were replaced with pinned
general-category and extended-pictographic lookups. This avoids depending on the
browser's ICU data version. The retained LB12a rule already implements revision
57's exclusion of BA from the exception before GL.

`tests/linebreak.test.mjs` checks all 19,346 cases in the pinned Unicode 18
LineBreakTest corpus. This proves default break opportunities for that corpus,
not dictionary segmentation, font shaping, bidi layout or visual style.

The comic's higher-level tailoring is in `js/line-breaks.js`: preserve grapheme
clusters and explicit spacing, expand tabs to four-column stops, render soft
hyphens only at selected breaks, and allow protected emergency word splitting.
