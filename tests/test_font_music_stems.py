"""Special stem drawings survive contextual substitutions and attachment."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline


def test_special_stems_preserve_native_shaping_and_distinct_ornaments():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoMusic-Regular.ttf'))
    path = ROOT / e['file']; font = TTFont(path)
    drawings = []
    for cp, contours in [(0x1D25F, 4), (0x1D280, 2), (0x1D281, 2)]:
        drawings.append(outline(font, cp)[0])
        assert outline(font, cp)[2] == 0
        for head in [0x1D157, 0x1D158, 0x1D159, 0x1D15A, 0x1D15B, 0x1D15C, 0x1D15D]:
            for suffix in ['', '\U0001d16e', '\U0001d172', '\U0001d250', '\U0001d169', '\U0001d25b', '\U0001d25c', '\U0001d16e\U0001d169', '\U0001d17b']:
                text = chr(head) + chr(cp) + suffix
                expected = shape(path, chr(head) + '\U0001d165' + suffix, True)
                actual = shape(path, text, True)
                assert len(actual) == len(expected), text
                changes = 0
                for a, b in zip(actual, expected):
                    assert a[1:] == b[1:], (text, a, b)
                    assert a[0]
                    if a[0] != b[0]:
                        glyph = font['glyf'][font.getGlyphName(a[0])]
                        assert len(glyph.getCoordinates(font['glyf'])[1]) == contours
                        reference = font['glyf'][font.getGlyphName(b[0])]
                        assert len(reference.getCoordinates(font['glyf'])[1]) == 1
                        changes += 1
                assert changes == 1, text
    assert all(a != b for i, a in enumerate(drawings) for b in drawings[i + 1:])


def test_original_stems_remain_unchanged():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoMusic-Regular.ttf'))
    for head in range(0x1D157, 0x1D15E):
        for suffix in ['', '\U0001d16e', '\U0001d169', '\U0001d17b']:
            text = chr(head) + '\U0001d165' + suffix
            assert shape(ROOT / e['source'], text) == shape(ROOT / e['file'], text)
