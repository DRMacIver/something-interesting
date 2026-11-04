"""Supplemental Arabic marks attach inside a complete native font."""
import sys
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape,ROOT
from test_font_arabic import entry
from test_font_cuneiform import outline
sys.path.insert(0,str(ROOT/'tools/font'))
from arabic_marks import ABOVE,BELOW,POINTS,bounds


def test_scaled_source_outlines_and_zero_advances():
    e=entry();font=TTFont(ROOT/e['file']);donor=TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf')
    scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
    assert len(POINTS)==15
    for cp in POINTS:
        actual=outline(font,cp);original=outline(donor,cp)
        assert actual[0] and actual[2]==0
        assert all(abs(a-b*scale)<2 for a,b in zip(actual[1],original[1])),hex(cp)
    assert (ROOT/e['additionalSources'][0]['licence']).is_file()


def test_marks_attach_and_stack_over_different_native_bases():
    e=entry();p=ROOT/e['file'];font=TTFont(p)
    for base in ['ب','م','ك']:
        base_box=outline(font,ord(base))[1]
        base_advance=sum(g[1] for g in shape(p,base))
        for cp in POINTS:
            result=shape(p,base+chr(cp)*2,True)
            assert len(result)==3 and all(g[0] for g in result)
            assert sum(g[1] for g in result)==base_advance
            marks=[g for g in result if g[1]==0];assert len(marks)==2
            box=outline(font,cp)[1]
            placed=sorted([(box[1]+g[4],box[3]+g[4]) for g in marks])
            assert placed[1][0]>placed[0][1],(base,hex(cp),placed)
            reference=shape(p,base+chr(0x652 if cp in ABOVE else 0x650),True)
            ref=next(g for g in reference if g[1]==0)
            ref_box=bounds(font,font.getGlyphOrder()[ref[0]])
            # Native kaf positions its accent beside the tall ascender. Preserve
            # the host's actual optical anchor, not a rectangular clearance rule.
            edge=placed[0][0] if cp in ABOVE else placed[1][1]
            expected=ref_box[1 if cp in ABOVE else 3]+ref[4]
            if cp == 0x10ef9:
                expected += box[1]-box[3]+font['head'].unitsPerEm/4
            assert abs(edge-expected)<=1,(base,hex(cp),edge,expected)
            assert all(0<(box[0]+box[2])/2+g[3]<base_advance for g in marks)


def test_lam_alef_and_existing_word_shaping_remain_native():
    e=entry();p=ROOT/e['file']
    for text in ['مَرْحَبًا بالعالم','ب𐻂ب','لا','بࢗ ب𐻺 ب𐻻 ب𐻼']:
        assert shape(p,text)==shape(ROOT/e['source'],text)
    for cp in POINTS:
        result=shape(p,'لا'+chr(cp),True)
        assert len(result)==2 and all(g[0] for g in result)
        assert sum(g[1] for g in result)==sum(g[1] for g in shape(p,'لا',True))
        assert any(g[1]==0 and g[3]!=0 for g in result)


def test_legacy_browser_aliases_select_identical_glyphs_and_positions():
    e=entry();p=ROOT/e['file'];font=TTFont(p)
    table=next(t for t in font['cmap'].tables if t.format==14)
    assert len(table.uvsDict)==37
    for i,cp in enumerate(sorted(POINTS)):
        alias=chr(0x652 if cp in ABOVE else 0x650)+chr(0xe0100+i)
        for base in ['ب','ك','لا']:
            native=shape(p,base+chr(cp)*2,True)
            compat=shape(p,base+alias*2,True)
            # Variation selectors may survive as invisible zero-advance spaces.
            compat=[g for g in compat if g[0]!=font.getGlyphID('space')]
            assert compat==native,(hex(cp),base,compat,native)


def test_crown_surrounds_the_top_of_its_attested_base_letters():
    # Unicode 18 §9.2.9 lists alef, dal, thal, reh, zain, lam and waw.
    e=entry();p=ROOT/e['file'];font=TTFont(p)
    crown=outline(font,0x10ef9)[1]
    for base in 'ادذرزلو':
        base_box=outline(font,ord(base))[1]
        shaped=shape(p,base+'\U00010ef9',True)
        mark=next(g for g in shaped if g[1]==0)
        low,high=crown[1]+mark[4],crown[3]+mark[4]
        assert low<base_box[3]<high,(base,low,high,base_box)


def test_vowel_accents_do_not_pull_crown_away_from_the_base():
    e=entry();p=ROOT/e['file'];font=TTFont(p)
    crown_id=font.getGlyphID(font.getBestCmap()[0x10ef9])
    for base in 'ادذرزلو':
        original=next(g for g in shape(p,base+'\U00010ef9',True) if g[0]==crown_id)
        for accent in ['\u064e','\u064f','\u0651']:
            marked=next(g for g in shape(p,base+'\U00010ef9'+accent,True) if g[0]==crown_id)
            assert marked==original,(base,accent,original,marked)
            native=shape(p,base+'\U00010ef9'+accent,True)
            alias=shape(p,base+'\u0652\U000e010e'+accent,True)
            alias=[g for g in alias if g[0]!=font.getGlyphID('space')]
            assert alias==native
