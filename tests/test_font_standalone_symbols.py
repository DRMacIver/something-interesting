"""Standalone symbol additions preserve metrics and meaningful distinctions."""
import json
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_cuneiform import outline
from test_font_scripts import manifest,shape,ROOT


def pair():
    record=next(e for e in json.loads((ROOT/'data/font-sources/ufs.json').read_text())['files'] if 'standalone_symbol_ranges' in e)
    entry=next(e for e in manifest()['fonts'] if e['source']==record['path'])
    points={cp for a,b in record['standalone_symbol_ranges'] for cp in range(a,b+1)}
    return entry,TTFont(ROOT/record['path']),TTFont(ROOT/entry['file']),points


def test_standalone_symbols_have_real_ink_preserved_advances_and_bounded_adaptation():
    entry,source,font,points=pair()
    assert len(points)==133
    changed=0
    for cp in points:
        original,actual=outline(source,cp),outline(font,cp)
        assert actual[0] and actual[1] is not None and actual[2]>0,hex(cp)
        assert actual[2]==original[2],hex(cp)
        assert all(abs(a-b)<=4 for a,b in zip(actual[1],original[1])),(hex(cp),actual[1],original[1])
        changed+=actual[0]!=original[0]
    assert changed==133
    text=''.join(map(chr,sorted(points)))
    assert shape(ROOT/entry['source'],text)==shape(ROOT/entry['file'],text)
    assert all(g[0] for g in shape(ROOT/entry['file'],text))
    assert 'Open Font License' in font['name'].getDebugName(13)


def test_mathematical_musical_and_orientation_distinctions_remain_distinct():
    _,_,font,_=pair()
    groups=[range(0x1db00,0x1db1d),range(0x1d1eb,0x1d1f7),
            [0x1cedd,0x1cede,0x1cedf],[0x1f7f4,0x1f7f5],[0x2e60,0x2e61,0x2e62,0x2e63]]
    for points in groups:
        points=list(points)
        assert len({repr(outline(font,cp)[0]) for cp in points})==len(points)
    # The italic historical ligature retains descender ink and its own drawing.
    assert outline(font,0x1d6a6)[1][1]<0
