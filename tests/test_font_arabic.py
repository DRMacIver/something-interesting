"""Arabic fallback must retain native joining and mark positioning."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from font_baseline_checks import pinned_packaging_font

ADDED = [0x88f,0x897,0xfbc6,0xfbc7,0xfd90,0xfd91,*range(0x10ec2,0x10ec8),0x10ed0,0x10efa,0x10efb,0x10efc]


def entry():
    return next(e for e in manifest()['fonts'] if e['source'].endswith('/ScheherazadeNew-Regular.ttf'))


def test_new_arabic_glyphs_preserve_real_source_outlines():
    e=entry();source=TTFont(ROOT/e['source']);font=TTFont(ROOT/e['file'])
    for cp in ADDED:
        assert outline(font,cp)[1] is not None
        assert outline(font,cp)==outline(source,cp)


def test_extended_arabic_contextual_forms_survive_packaging():
    e=entry();p=ROOT/e['file']
    for cp in [0x88f,0x10ec2,0x10ec3,0x10ec4,0x10ec6,0x10ec7]:
        text='ب'+chr(cp)+'ب'
        assert shape(p,text)==shape(ROOT/e['source'],text)
        joined=shape(p,text,True)
        isolated=shape(p,chr(cp),True)
        assert all(g[0] for g in joined)
        assert len(joined)==3 and joined[1][0]!=isolated[0][0],hex(cp)


def test_new_combining_marks_attach_with_zero_advance():
    e=entry();p=ROOT/e['file'];font=TTFont(p)
    for cp in [0x897,0x10efa,0x10efb,0x10efc]:
        text='ب'+chr(cp)
        result=shape(p,text,True)
        assert shape(p,text)==shape(ROOT/e['source'],text)
        assert all(g[0] for g in result)
        assert sum(g[1] for g in result)==sum(g[1] for g in shape(p,'ب',True))
        assert outline(font,cp)[2]==0
        if cp == 0x10efc:  # The overlay is drawn over the base at zero offset.
            base,mark=outline(font,0x628)[1],outline(font,cp)[1]
            assert min(base[2],mark[2])>max(base[0],mark[0])
            assert min(base[3],mark[3])>max(base[1],mark[1])
        else:
            assert any(g[1]==0 and (g[3]!=0 or g[4]!=0) for g in result)


def test_standalone_honorifics_preserve_drawings_and_positive_advances():
    import json
    from test_unicode_inventory import audit
    e=next(e for e in manifest()['fonts'] if '/ufs/' in e['source'])
    data=json.loads((ROOT/'data/font-sources/ufs.json').read_text())
    scope=next(s for s in data['files'] if s['path']==e['source'])
    points={cp for a,b in scope['honorific_ranges'] for cp in range(a,b+1)}
    assert len(points)==29
    source,font=TTFont(ROOT/e['source']),TTFont(ROOT/e['file'])
    native=pinned_packaging_font(e)
    scripts=audit.properties(audit.DATA/'Scripts.txt');categories=audit.inventory()
    for cp in points:
        assert scripts[cp]=='Arabic' and categories[cp]=='So'
        actual=outline(font,cp)
        assert actual[0] and actual[1] is not None and actual[2]>0
        assert outline(native,cp)==outline(source,cp)
        assert actual[2]==outline(native,cp)[2]
        assert all(abs(a-b)<=.01 for a,b in zip(actual[1],outline(native,cp)[1]))
        assert shape(ROOT/e['file'],chr(cp))==shape(ROOT/e['source'],chr(cp))
    assert 0x10ed9 not in font.getBestCmap()  # Crown letters need native joining.
    assert 0x10ecb not in font.getBestCmap()  # Marks need native attachment.


def test_baseline_symbols_are_spacing_drawings_not_combining_marks():
    e=next(e for e in manifest()['fonts'] if '/ufs/' in e['source'])
    source,font=TTFont(ROOT/e['source']),TTFont(ROOT/e['file'])
    native=pinned_packaging_font(e)
    for cp in [0x10ec9,0x10eca]:
        actual=outline(font,cp)
        assert outline(native,cp)==outline(source,cp)
        assert actual[2]==outline(native,cp)[2]
        assert all(abs(a-b)<=.01 for a,b in zip(actual[1],outline(native,cp)[1]))
        assert actual[2]>0 and actual[1][3]<200
        assert len(shape(ROOT/e['file'],chr(cp)*2))==2
        assert sum(g[1] for g in shape(ROOT/e['file'],chr(cp)*2))==2*actual[2]
    assert outline(font,0x10ec9)[0]!=outline(font,0x10eca)[0]
