"""Caudate forms remain distinct, with above-mark attachment and native casing."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from test_font_bengali_anusvara import boxes


def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSansGlagolitic-Regular.ttf'))
    return e, TTFont(ROOT / e['file'])


def test_caudate_identity_case_and_marks():
    e, f = pair(); path = ROOT / e['file']
    assert 'Shafarik Project Authors' in f['name'].getDebugName(0)
    for cp, reference in [(0x2C2F, 0x2C1D), (0x2C5F, 0x2C4D)]:
        new, old = outline(f, cp), outline(f, reference)
        assert new[0] != old[0]
        assert new[1][1] < 0 <= old[1][1]  # The tail survives below the baseline.
        assert new[1][3] == old[1][3]
        assert 0 < new[2] < old[2]  # Narrow tailed form, not the ordinary broad form.
        for mark in ['\u0303', '\u0483', '\u0305', '\u0484', '\u0487']:
            text = chr(cp) + mark
            result = shape(path, text, True)
            assert all(g[0] for g in result) and len(result) == 2
            assert result[1][1] == 0
            b = [box for _, box in boxes(f, path, text)]
            assert b[1][1] > b[0][3], (text, b)
            assert abs((b[0][0] + b[0][2]) / 2 - (b[1][0] + b[1][2]) / 2) < 90
    assert outline(f, 0x2C2F)[1][3] > outline(f, 0x2C5F)[1][3]


def test_old_glagolitic_and_full_block_coverage():
    e, f = pair(); path = ROOT / e['file']
    assert all(cp in f.getBestCmap() for cp in range(0x2C00, 0x2C60))
    for text in ['Ⱍⱍ', 'Ⱍ̃ ⱍ҃', 'ⰀⰁⰂⰃ ⰰⰱⰲⰳ', 'ⱍⱃⱐⰲⱐ']:
        assert shape(ROOT / e['source'], text) == shape(path, text)


def test_browser_mark_aliases_preserve_glyphs_and_native_positions():
    e, f = pair(); path = ROOT / e['file']
    for cp in range(0x2C00, 0x2C60):
        for i, mark in enumerate([0x483, 0x484, 0x487]):
            original = chr(cp) + chr(mark)
            drawing = chr(cp) + '\u0303' + chr(0xE0170 + i)
            # HarfBuzz retains an invisible variation-selector glyph. Compare
            # actual non-space drawings and positions, including advances.
            a = shape(path, original, True); b = shape(path, drawing, True)
            space = f.getGlyphID(f.getBestCmap()[0x20])
            b = [g for g in b if not (g[0] == space and g[1] == 0)]
            assert a == b, (original, a, b)
