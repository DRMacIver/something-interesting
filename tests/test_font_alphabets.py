"""Alphabet adaptation must preserve case, modifier scale and baseline meaning."""
import json
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_cuneiform import outline
from test_font_scripts import manifest, shape, ROOT
from test_unicode_inventory import audit


def pair():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    data=json.loads((ROOT/'data/font-sources/unicodia.json').read_text())
    scope=next(s for s in data['files'] if s['path']==e['source'])
    points={cp for a,b in scope['ink_ranges'] for cp in range(a,b+1)}
    # Symbols have separate semantic geometry tests, including the deliberate
    # repair to the source isolobal arrow. Keep this test on letter adaptation.
    for key in ('chemical_symbol_ranges', 'geomantic_ranges', 'asteroid_ranges', 'chess_annotation_ranges', 'shatranj_ranges'):
        points.difference_update(cp for a,b in scope.get(key,[]) for cp in range(a,b+1))
    return e,TTFont(ROOT/e['source']),TTFont(ROOT/e['file']),points


def test_all_supplemental_letters_have_real_ink_and_preserved_advances():
    e,source,derived,points=pair()
    assert len(points)==240
    changed=0
    for cp in points:
        original,actual=outline(source,cp),outline(derived,cp)
        assert actual[0] and actual[1] is not None and actual[2]>0,hex(cp)
        assert actual[2]==original[2],hex(cp)
        assert all(abs(a-b)<=4 for a,b in zip(actual[1],original[1])),hex(cp)
        changed += actual[0]!=original[0]
    assert changed==240
    text=''.join(map(chr,sorted(points)))
    assert shape(ROOT/e['source'],text)==shape(ROOT/e['file'],text)
    assert all(g[0] for g in shape(ROOT/e['file'],text))


def test_case_and_modifier_distinctions_survive_ink_adaptation():
    _,_,font,_=pair()
    for capital,small in [(0x1c89,0x1c8a),(0xa7cc,0xa7cd),(0xa7ce,0xa7cf),(0xa7da,0xa7db)]:
        a,b=outline(font,capital),outline(font,small)
        assert a[0]!=b[0]
        if capital != 0xa7da:  # Lowercase lambda has a native ascender.
            assert a[1][3]>b[1][3]
    raised,lowered=outline(font,0x1e030),outline(font,0x1e051)
    assert raised[1][1]>300
    assert lowered[1][1]<0<lowered[1][3]<300
    assert raised[2]==lowered[2]


def test_all_assigned_latin_and_cyrillic_characters_have_bundled_mappings():
    scripts=audit.properties(audit.DATA/'Scripts.txt')
    required={cp for cp in audit.inventory() if scripts.get(cp) in {'Latin','Cyrillic'}}
    m=manifest()
    bundled={cp for e in m['fonts'] for a,b in e['ranges'] for cp in range(a,b+1)}
    bundled.update(cp for a,b in m['baseRanges'] for cp in range(a,b+1))
    assert required<=bundled


def test_cyrillic_mark_attaches_and_stacks_in_native_font():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSans-Regular.ttf'))
    font=TTFont(ROOT/e['file'])
    mark=outline(font,0x1e08f)
    assert mark[0] and mark[2]==0
    for base in ['а','А']:
        result=shape(ROOT/e['file'],base+'\U0001e08f\U0001e08f')
        assert len(result)==3 and all(g[0] for g in result)
        assert result[1][1]==result[2][1]==0
        box=outline(font,ord(base))[1]
        first_y=mark[1][1]+result[1][4]
        second_y=mark[1][1]+result[2][4]
        assert first_y>box[3]
        assert second_y>mark[1][3]+result[1][4]
        center=(mark[1][0]+mark[1][2])/2+result[0][1]+result[1][3]
        assert abs(center-(box[0]+box[2])/2)<100
    assert shape(ROOT/e['source'],'Привет мир')==shape(ROOT/e['file'],'Привет мир')
