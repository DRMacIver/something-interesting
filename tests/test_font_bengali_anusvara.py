"""Historical above-anusvara stays attached and clears documented hosts."""
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen
from test_font_scripts import manifest, shape, ROOT


def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSansBengali-Regular.ttf'))
    return e, TTFont(ROOT / e['file'])


def drawing(base):
    return base.replace('ো', 'ো').replace('ৌ', 'ৌ') + 'ঁ' + chr(0xE0152 if any(c in base for c in 'িীৌৗ') or 'র্' in base or 'ৰ্' in base else 0xE0151)


def boxes(font, path, text):
    cursor = 0; result = []
    for gid, advance, _, x, y in shape(path, text, True):
        name = font.getGlyphName(gid)
        pen = BoundsPen(font.getGlyphSet()); font.getGlyphSet()[name].draw(pen)
        if pen.bounds:
            a, b, c, d = pen.bounds
            result.append((name, (cursor + x + a, y + b, cursor + x + c, y + d)))
        cursor += advance
    return result


def test_ring_is_zero_advance_and_clears_consonants_vowels_conjuncts():
    e, f = pair(); p = ROOT / e['file']
    assert 'Losketch' in f['name'].getDebugName(0)
    assert f['hmtx'][f.getBestCmap()[0x11DF0]][0] == 0
    for base in ['ক', 'খ', 'ত', 'ম', 'স', 'অ', 'আ', 'কা', 'কি', 'কী', 'কু', 'কূ', 'কে', 'কৈ', 'কো', 'কৌ',
                 'র্ক', 'র্কি', 'ক্ষ', 'ক্ষি', 'ক্র', 'ক্রি', 'ন্তি', 'ট্টি', 'থি']:
        text = drawing(base); shaped = boxes(f, p, text)
        name, ring = shaped[-1]
        assert shape(p, text, True)[-1][1] == 0
        assert sum(g[1] for g in shape(p, text)) == sum(g[1] for g in shape(p, base)), base
        for _, other in shaped[:-1]:
            if min(ring[2], other[2]) > max(ring[0], other[0]):
                assert ring[1] >= other[3] + 10, (base, ring, other)
        assert all(g[0] for g in shape(p, text))


def test_existing_bengali_remains_unchanged_and_new_mark_is_distinct():
    e, f = pair(); p = ROOT / e['file']
    for text in ['কঁ কাঁ কিঁ কীঁ', 'বাংলা ভাষা', 'কো কৌ র্কি ক্ষি', 'বং কং']:
        assert shape(ROOT / e['source'], text) == shape(p, text)
    from test_font_cuneiform import outline
    assert outline(f, 0x11DF0)[0] != outline(f, 0x981)[0]
    assert outline(f, 0x11DF0)[0] != outline(f, 0x982)[0]


def test_all_assigned_bengali_have_bundled_mappings():
    from test_unicode_inventory import audit
    scripts = audit.properties(audit.DATA / 'Scripts.txt')
    required = {cp for cp in audit.inventory() if scripts.get(cp) == 'Bengali'}
    m = manifest()
    covered = {cp for e in m['fonts'] for a, b in e['ranges'] for cp in range(a, b + 1)}
    covered.update(cp for a, b in m['baseRanges'] + m['behaviouralRanges'] for cp in range(a, b + 1))
    assert required <= covered
