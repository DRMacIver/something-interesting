# Pinned Unicode inputs

These files are the final Unicode 18.0.0 data, downloaded from Unicode's
versioned public directory. Its `ReadMe.txt` explicitly identifies it as final.
The release overview still had a draft notice at retrieval; the final data and
published UAX #29 revision 49 independently establish the pinned release.

`sources.json` records each upstream URL and SHA-256 digest. The UCD files were
extracted unchanged from `https://www.unicode.org/Public/18.0.0/ucd/UCD.zip`;
the three emoji inventory/test files were downloaded separately. The Unicode
licence is retained in `LICENSE.txt`. Do not update sources silently.

Verify inputs with `python tools/unicode/sources.py`. Rebuild browser tables
with `python tools/unicode/build_tables.py`. Generate the font coverage report
with `python tools/unicode/audit.py` using the project's Python environment.

The audit excludes private use and surrogate code points. It distinguishes
controls, separators and default-ignorables from visible characters, and
inventories standardised, named and emoji sequences separately. Counts of cmap
entries are only an initial coverage check, not glyph quality or shaping proof.
