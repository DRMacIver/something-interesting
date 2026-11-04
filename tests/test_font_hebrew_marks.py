"""Hebrew heavy points keep native positions and zero-advance mark semantics."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest,shape,ROOT
from test_font_cuneiform import outline


def pair():
    e=next(e for e in manifest()['fonts'] if 'NotoRashiHebrew' in e['source'])
    return e,TTFont(ROOT/e['file'])


def positioned(font,path,text,cp):
    target=font.getBestCmap()[cp];cursor=0
    for gid,advance,_,x,y in shape(path,text,True):
        name=font.getGlyphName(gid)
        if name==target:
            b=outline(font,cp)[1]
            return (b[0]+cursor+x,b[1]+y,b[2]+cursor+x,b[3]+y)
        cursor+=advance
    raise AssertionError((text,target))


def test_heavy_points_follow_native_anchors_on_every_hebrew_base():
    e,font=pair();path=ROOT/e['file']
    assert 'Losketch' in font['name'].getDebugName(0)
    assert 'Open Font License' in font['name'].getDebugName(13)
    for cp,old in [(0x5c8,0x5b0),(0x5c9,0x5bc)]:
        new_ink,old_ink=outline(font,cp),outline(font,old)
        assert new_ink[0] and new_ink[2]==0
        assert new_ink[1][2]-new_ink[1][0]>old_ink[1][2]-old_ink[1][0]
        assert font['GDEF'].table.GlyphClassDef.classDefs[font.getBestCmap()[cp]]==3
        for base in range(0x5d0,0x5eb):
            a=positioned(font,path,chr(base)+chr(cp),cp)
            b=positioned(font,path,chr(base)+chr(old),old)
            assert abs((a[0]+a[2]-b[0]-b[2])/2)<=.5,(hex(base),hex(cp),a,b)
            if cp==0x5c8:assert abs(a[3]-b[3])<=.5
            else:assert abs((a[1]+a[3]-b[1]-b[3])/2)<=.5
            assert sum(g[1] for g in shape(path,chr(base)+chr(cp)))==sum(g[1] for g in shape(path,chr(base)))


def test_combined_points_preserve_other_native_marks_and_existing_hebrew():
    e,font=pair();path=ROOT/e['file']
    old='שְּׁ';new='ש׈׉ׁ'
    assert positioned(font,path,old,0x5c1)==positioned(font,path,new,0x5c1)
    for text in ['שָׁלוֹם','בְּרֵאשִׁית','אֱלֹהִים','לְשׁוֹן']:
        assert shape(ROOT/e['source'],text)==shape(path,text)
    assert all(g[0] for g in shape(path,new))


def test_all_assigned_hebrew_characters_have_bundled_mappings():
    from test_unicode_inventory import audit
    scripts=audit.properties(audit.DATA/'Scripts.txt')
    required={cp for cp in audit.inventory() if scripts.get(cp)=='Hebrew'}
    m=manifest();covered={cp for e in m['fonts'] for a,b in e['ranges'] for cp in range(a,b+1)}
    covered.update(cp for a,b in m['baseRanges']+m['behaviouralRanges'] for cp in range(a,b+1))
    assert required<=covered
