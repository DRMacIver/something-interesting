"""Alternate BA preserves its diagonal and inherits BA, not RA, shaping."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline

ALT = '\U00011df1'
DRAW = '\u09ac\U000e0150'


def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSansBengali-Regular.ttf'))
    return e, TTFont(ROOT / e['file'])


def named(font, path, text):
    return [(font.getGlyphName(gid), *p) for gid, *p in shape(path, text, True)]


def test_alternate_ba_has_distinct_native_diagonal_and_ba_metrics():
    e, f = pair()
    if e.get('supplementalTreatment'):
        from font_baseline_checks import assert_pressure_glyph_lineage
        native=TTFont(ROOT/'output/font-review/supplemental-production-baselines'/e['file'].split('/')[-1])
        # The documented shared isolated form is proved on exact native input.
        # Name-seeded ink can vary while preserving that same native letterform;
        # require both painted glyphs to be their actual approved derivations.
        assert outline(native,0x11DF1)==outline(native,0x9F0)
        assert_pressure_glyph_lineage(e,[0x11DF1,0x9F0])
        assert outline(f,0x11DF1)[1:]==outline(f,0x9F0)[1:]
    else:
        assert outline(f,0x11DF1)==outline(f,0x9F0)
    assert outline(f, 0x11DF1)[0] != outline(f, 0x9AC)[0]
    assert outline(f, 0x11DF1)[2] == outline(f, 0x9AC)[2] > 0
    assert f['GDEF'].table.GlyphClassDef.classDefs[f.getBestCmap()[0x11DF1]] == 1
    assert shape(ROOT / e['file'], ALT, True) == shape(ROOT / e['file'], DRAW, True)


def test_vowels_and_documented_conjuncts_follow_ba_not_ra():
    e, f = pair(); p = ROOT / e['file']
    old, new = f.getBestCmap()[0x9AC], f.getBestCmap()[0x11DF1]
    # L2/22-268R page 3: Cu, Cuu, rCa, Cra, Cru, Cya, Cda, Cdha, mCa, CCa.
    patterns = ['{}ু', '{}ূ', 'র্{}', '{}্র', '{}্রু', '{}্য', '{}্দ', '{}্ধ', 'ম্{}', '{}্{}']
    patterns += ['{}' + chr(cp) for cp in [0x9BE, 0x9BF, 0x9C0, 0x9C3, 0x9C4, 0x9C7, 0x9C8, 0x9CB, 0x9CC, 0x981, 0x982]]
    for pattern in patterns:
        ordinary = named(f, p, pattern.replace('{}', 'ব'))
        alternate = named(f, p, pattern.replace('{}', DRAW).replace('ো', 'ো').replace('ৌ', 'ৌ'))
        normalized = [(old if n == new else n, *pos) for n, *pos in alternate]
        assert normalized == ordinary, (pattern, ordinary, alternate)
    for suffix in ['ু', 'ূ', 'ি', 'ে', 'া']:
        assert any(g[0] == new for g in named(f, p, DRAW + suffix))
    assert named(f, p, DRAW + '্দ') != named(f, p, 'ৰ্দ')


def test_original_bengali_and_assamese_keep_source_shaping():
    e, _ = pair()
    for text in ['বাংলা ভাষা', 'বু বূ ব্র ব্রু ব্দ ব্ধ ম্ব ব্ব', 'ৰ ৰু ৰূ ৰ্ক কৰ্', 'শব্দ']:
        assert shape(ROOT / e['source'], text) == shape(ROOT / e['file'], text)


def test_alternate_ba_inherits_native_rules_across_consonant_contexts():
    e, f = pair(); p = ROOT / e['file']
    old, new = f.getBestCmap()[0x9AC], f.getBestCmap()[0x11DF1]
    consonants = [chr(cp) for cp in range(0x995, 0x9BA) if cp in f.getBestCmap()]
    for consonant in consonants:
        for pattern in ['{}্' + consonant, consonant + '্{}', 'র্{}্' + consonant]:
            for vowel in ['', 'ি', 'ু', 'ে']:
                ordinary = named(f, p, pattern.replace('{}', 'ব') + vowel)
                alternate = named(f, p, pattern.replace('{}', DRAW) + vowel)
                assert [(old if n == new else n, *pos) for n, *pos in alternate] == ordinary, (pattern, vowel)
