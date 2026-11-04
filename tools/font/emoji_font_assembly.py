"""Fast web packaging of already-compiled TrueType glyph records."""
from types import SimpleNamespace
from unittest.mock import patch
from fontTools.ttLib import woff2


def save_webfont(font,path):
    # Optional WOFF2 glyf transforms decode/re-encode every point in Python.
    # Untransformed WOFF2 preserves the compiled SFNT glyph records verbatim.
    # Brotli quality 5 is lossless; it changes compression ratio, not artwork.
    font.flavor='woff2'
    font.flavorData=woff2.WOFF2FlavorData(transformedTables=set())
    native=woff2.brotli
    compressor=SimpleNamespace(MODE_FONT=native.MODE_FONT,
        compress=lambda data,**kwargs:native.compress(data,quality=5,**kwargs))
    with patch.object(woff2,'brotli',compressor):
        font.save(path)
