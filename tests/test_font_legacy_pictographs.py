"""Disunified terminal pictographs retain text identities and internal detail."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, ROOT, shape
from test_font_cuneiform import outline


def test_ten_text_pictures_preserve_counters_detail_and_equal_spacing():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/KreativeSquare.ttf'))
    font=TTFont(ROOT/e['file']);source=TTFont(ROOT/e['source'])
    points=[*range(0x1ccfa,0x1ccfd),*range(0x1ceba,0x1cec0),0x1fbfa]
    assert set(font.getBestCmap())==set(points)
    # Saucer windows, hollow nose/glass, office windows, tree openings and
    # strawberry seeds must survive subsetting and the smooth pen deformation.
    counts=[1,4,2,2,10,3,1,1,15,1]
    drawings=[]
    for cp,count in zip(points,counts):
        a,b=outline(source,cp),outline(font,cp)
        assert a[2]==b[2]==720
        assert a[0]!=b[0] and b[1] is not None
        assert max(abs(x-y) for x,y in zip(a[1],b[1]))<=4
        glyph=font['glyf'][font.getBestCmap()[cp]]
        assert len(glyph.getCoordinates(font['glyf'])[1])==count,hex(cp)
        drawings.append(repr(b[0]))
    assert len(set(drawings))==10
    assert 'COLR' not in font and 'CBDT' not in font and 'SVG ' not in font
    text=''.join(map(chr,points))
    assert shape(ROOT/e['source'],text)==shape(ROOT/e['file'],text)
