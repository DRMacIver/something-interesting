"""Stress/unstress retain native note attachment and distinct contours."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from test_font_hebrew_marks import positioned


def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoMusic-Regular.ttf'))
    return e, TTFont(ROOT / e['file'])


def test_articulations_follow_native_note_centers_and_clearance():
    e, f = pair(); p = ROOT / e['file']
    assert 'Losketch' in f['name'].getDebugName(0)
    bases = [chr(cp) for cp in range(0x1D15A, 0x1D165)]
    bases += ['\U0001d158\U0001d165', '\U0001d158\U0001d165\U0001d16e',
              '\U0001d157\U0001d165\U0001d16d', '\U0001d158\U0001d165\U0001d172']
    for cp in (0x1D127, 0x1D128):
        assert outline(f, cp)[0] and outline(f, cp)[2] == 0
        assert f['GDEF'].table.GlyphClassDef.classDefs[f.getBestCmap()[cp]] == 3
        for base in bases:
            a = positioned(f, p, base + chr(cp), cp)
            b = positioned(f, p, base + '\U0001d17b', 0x1D17B)
            assert abs((a[0] + a[2] - b[0] - b[2]) / 2) <= .5
            assert abs(a[3] - b[3]) <= .5
            assert sum(g[1] for g in shape(p, base + chr(cp))) == sum(g[1] for g in shape(p, base + '\U0001d17b'))
            assert all(g[0] for g in shape(p, base + chr(cp)))
    assert len({repr(outline(f, cp)[0]) for cp in (0x1D127, 0x1D128, 0x1D17B)}) == 3


def test_original_music_and_canonical_note_decompositions_are_preserved():
    e, f = pair(); p = ROOT / e['file']
    for text in ['\U0001d11e\U0001d15f\U0001d17b', '\U0001d158\U0001d165\U0001d16e', '\U0001d15f\U0001d17c\U0001d17d']:
        assert shape(ROOT / e['source'], text) == shape(p, text)
    for cp in (0x1D127, 0x1D128):
        assert shape(p, '\U0001d15f' + chr(cp), True) == shape(p, '\U0001d158\U0001d165' + chr(cp), True)
