"""Pinned Jurchen/Tangut drawings survive restricted CFF packaging."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_cuneiform import outline
from test_font_scripts import manifest, shape, ROOT
from test_unicode_inventory import audit
from font_baseline_checks import pinned_packaging_font


def test_scoped_font_preserves_real_outlines_and_excludes_other_repertoires():
    e = next(e for e in manifest()['fonts'] if '/ufs/' in e['source'])
    source, packaged = TTFont(ROOT/e['source']), TTFont(ROOT/e['file'])
    native = pinned_packaging_font(e)
    scripts = audit.properties(audit.DATA/'Scripts.txt')
    expected = {cp for cp in source.getBestCmap() if scripts.get(cp) in {'Jurchen', 'Tangut'}}
    import json
    source_entry=next(s for s in json.loads((ROOT/'data/font-sources/ufs.json').read_text())['files'] if s['path']==e['source'])
    honorifics={cp for a,b in source_entry['honorific_ranges'] for cp in range(a,b+1)}
    baseline={cp for a,b in source_entry.get('baseline_symbol_ranges',[]) for cp in range(a,b+1)}
    supplemental={cp for a,b in source_entry.get('supplemental_script_ranges',[]) for cp in range(a,b+1)}
    standalone={cp for a,b in source_entry.get('standalone_symbol_ranges',[]) for cp in range(a,b+1)}
    assert set(packaged.getBestCmap()) == expected | honorifics | baseline | supplemental | standalone
    assert len(expected) == 1119
    for cp in expected:
        drawing = outline(packaged, cp)
        assert drawing[0] and drawing[1] is not None and drawing[2] > 0, hex(cp)
        original = outline(source, cp)
        assert outline(native, cp)[:2] == original[:2], hex(cp)
        assert all(abs(a-b)<=.01 for a,b in zip(drawing[1],outline(native,cp)[1])),hex(cp)
        assert drawing[2] == (1000 if cp in {0x17D0B, 0x180DF} else original[2])
        if cp in {0x17D0B, 0x180DF}:
            assert original[2] == 0
            name = packaged.getBestCmap()[cp]
            assert packaged['CFF '].cff.topDictIndex[0].CharStrings[name].width == 1000
    text = ''.join(map(chr, sorted(expected)))
    original, derived = shape(ROOT/e['source'], text), shape(ROOT/e['file'], text)
    assert len(original) == len(derived)
    for before, after in zip(original, derived):
        assert after == (before[0], before[1] or 1000, *before[2:])
    assert sum(g[1] for g in derived) == sum(g[1] for g in original) + 2000
    assert all(g[0] for g in shape(ROOT/e['file'], text))
    assert packaged['CFF '].cff.fontNames == [e['family'].replace(' ', '')]


def test_every_assigned_jurchen_and_tangut_character_has_a_bundled_mapping():
    scripts = audit.properties(audit.DATA/'Scripts.txt')
    required = {cp for cp in audit.inventory() if scripts.get(cp) in {'Jurchen','Tangut'}}
    assert len({cp for cp in required if scripts[cp]=='Jurchen'}) == 965
    assert len({cp for cp in required if scripts[cp]=='Tangut'}) == 7061
    bundled = {cp for e in manifest()['fonts'] for a,b in e['ranges'] for cp in range(a,b+1)}
    assert required <= bundled
