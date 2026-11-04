"""Native Dives Akuru shaping and Myanmar digit identity survive packaging."""
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from test_unicode_inventory import audit
from font_baseline_checks import pinned_packaging_font


def entry(name):
    return next(e for e in manifest()['fonts'] if e['source']=='build/unicode-sources/unicodia/'+name)


@pytest.mark.parametrize('name,script', [('NotoSerifDivesAkuru-Regular.ttf','Dives_Akuru'),('PadaukBook-Regular.ttf','Myanmar')])
def test_complete_script_has_real_native_outlines(name,script):
    e=entry(name);font=TTFont(ROOT/e['file'])
    scripts=audit.properties(audit.DATA/'Scripts.txt')
    required={cp for cp in audit.inventory() if scripts.get(cp)==script}
    assert required<=font.getBestCmap().keys()
    for cp in required:
        assert outline(font,cp)[1] is not None,hex(cp)


@pytest.mark.parametrize('name,text', [
    ('NotoSerifDivesAkuru-Regular.ttf','\U0001190c\U00011935\U00011930\U0001193b'),
    ('NotoSerifDivesAkuru-Regular.ttf','\U0001190c\U0001193e\U0001190c'),
    ('NotoSerifDivesAkuru-Regular.ttf','\U00011941\U0001190c\U00011932'),
    ('PadaukBook-Regular.ttf','မြန်မာစာ'),
    ('PadaukBook-Regular.ttf',''.join(map(chr,range(0x116d0,0x116e4)))),
])
def test_packaged_native_shaping_is_preserved(name,text):
    e=entry(name)
    assert shape(ROOT/e['file'],text)==shape(ROOT/e['source'],text)
    assert all(g[0] for g in shape(ROOT/e['file'],text))


def test_dives_split_vowel_and_conjunct():
    e=entry('NotoSerifDivesAkuru-Regular.ttf');p=ROOT/e['file']
    assert shape(p,'\U0001190c\U00011938',True)==shape(p,'\U0001190c\U00011935\U00011930',True)
    conjunct=shape(p,'\U0001190c\U0001193e\U0001190c',True)
    assert len(conjunct)<3
    font=TTFont(p)
    assert 0x11939 not in font.getBestCmap()


def test_digit_sets_preserve_their_distinct_drawings_and_advances():
    for name,starts in [('NotoSerifDivesAkuru-Regular.ttf',[0x11950]),('PadaukBook-Regular.ttf',[0x116d0,0x116da])]:
        e=entry(name);source=TTFont(ROOT/e['source']);font=TTFont(ROOT/e['file']);native=pinned_packaging_font(e)
        for start in starts:
            drawings=[]
            for cp in range(start,start+10):
                actual=outline(font,cp)
                assert outline(native,cp)==outline(source,cp)
                assert actual[1:]==outline(native,cp)[1:]
                assert actual[2]>0
                drawings.append(repr(actual[0]))
            assert len(set(drawings))==10
