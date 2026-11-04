"""Side marks reserve ink space even in a separate fallback font shard."""
from pathlib import Path
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape

ROOT = Path(__file__).resolve().parents[1]


def test_compiled_vietnamese_marks_keep_spacing_and_distinct_outlines():
    drawings = []
    for cp in (0x16FF0,0x16FF1):
        entry = next(e for e in manifest()['fonts'] if any(a<=cp<=b for a,b in e['ranges']))
        path = ROOT/entry['file']; font = TTFont(path)
        name = font.getBestCmap()[cp]; glyph = font['glyf'][name]
        run = shape(path,chr(cp),True)
        assert len(run) == 1 and run[0][0] != 0
        advance = run[0][1]
        assert 0 < glyph.xMin < glyph.xMax < advance < 500
        assert 200 < glyph.yMin < glyph.yMax < 700
        assert run[0][3:] == (0,0)
        assert glyph.numberOfContours > 0
        drawings.append(glyph.compile(font['glyf']))
    assert drawings[0] != drawings[1]
