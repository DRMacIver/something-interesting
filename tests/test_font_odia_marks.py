"""Historical Kui dots attach to documented consonant and vowel hosts."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_hebrew_marks import positioned
from test_font_cuneiform import outline


def pair():
    e = next(e for e in manifest()['fonts'] if 'NotoSansOriya' in e['source'])
    return e, TTFont(ROOT / e['file'])


def alias(cp):
    return '\u0b55' + chr(0xE0140 + cp - 0xB53)


def test_dots_preserve_native_consonant_attachment_and_advances():
    e, f = pair(); p = ROOT / e['file']
    assert 'Losketch' in f['name'].getDebugName(0)
    for cp in (0xB53, 0xB54):
        assert outline(f, cp)[0] and outline(f, cp)[2] == 0
        assert f['GDEF'].table.GlyphClassDef.classDefs[f.getBestCmap()[cp]] == 3
    for base in [chr(cp) for cp in range(0xB15, 0xB3A) if cp in f.getBestCmap()] + ['କ୍କ', 'ନ୍ତ']:
        a = positioned(f, p, base + alias(0xB53), 0xB53)
        b = positioned(f, p, base + '\u0b55', 0xB55)
        assert abs((a[0] + a[2] - b[0] - b[2]) / 2) <= .5
        assert abs(a[1] - b[1]) <= .5
        assert sum(g[1] for g in shape(p, base + alias(0xB53))) == sum(g[1] for g in shape(p, base))


def test_documented_vowel_hosts_have_centered_dots_and_clearance():
    e, f = pair(); p = ROOT / e['file']
    for base, host, cp in [('କା', 0xB3E, 0xB53), ('କି', 0xB3F, 0xB53), ('କେ', 0xB47, 0xB53),
                           ('ଅ', 0xB05, 0xB54), ('ଆ', 0xB06, 0xB54), ('ଏ', 0xB0F, 0xB54)]:
        text = base + alias(cp)
        a, b = positioned(f, p, text, cp), positioned(f, p, text, host)
        assert abs((a[0] + a[2] - b[0] - b[2]) / 2) <= 1
        assert 72 <= a[1] - b[3] <= 74
        assert sum(g[1] for g in shape(p, text)) == sum(g[1] for g in shape(p, base))
        assert all(g[0] for g in shape(p, text))
    assert outline(f, 0xB54)[1][2] - outline(f, 0xB54)[1][0] > 2 * (outline(f, 0xB53)[1][2] - outline(f, 0xB53)[1][0])


def test_existing_odia_shaping_is_unchanged():
    e, _ = pair()
    for text in ['ଓଡ଼ିଆ ଭାଷା', 'କା କି କେ', 'କ୍କ ନ୍ତ', 'କ୕ ଅ୕ କା୕ କେ୕']:
        assert shape(ROOT / e['source'], text) == shape(ROOT / e['file'], text)
