"""Kawi nukta retains native syllable bodies and separates its above dots."""
import sys
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT, shape, manifest
sys.path.insert(0,str(ROOT/'tools/font'))
from kawi_nukta import add_mark


@pytest.fixture(scope='module')
def built(tmp_path_factory):
    f=TTFont(ROOT/'build/unicode-sources/noto/NotoSansKawi-Regular.ttf')
    add_mark(f,TTFont(ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'))
    path=tmp_path_factory.mktemp('kawi')/'nukta.ttf';f.save(path)
    return f,path


def test_nukta_keeps_native_bodies_across_vowels_repha_and_conjuncts(built):
    f,path=built
    for cp in range(0x11F12,0x11F34):
        for prefix in ['',chr(0x11F02),chr(0x11F26)+chr(0x11F42)]:
            for suffix in ['',*[chr(c) for c in range(0x11F34,0x11F3B)],chr(0x11F3E),chr(0x11F01),chr(0x11F36)+chr(0x11F01),chr(0x11F00)]:
                original=prefix+chr(cp)+suffix
                text=prefix+chr(cp)+chr(0x11F5A)+suffix
                expected=shape(path,original,True);actual=shape(path,text,True)
                normalized=[];seen=0
                for gid,*position in actual:
                    name=f.getGlyphName(gid)
                    if name=='nuktakawi':
                        assert position[0]==0;seen+=1;continue
                    if name.startswith('nuktakawi_'):
                        name=name[len('nuktakawi_'):];gid=f.getGlyphID(name);seen+=1
                    assert gid
                    normalized.append((gid,*position))
                assert seen==1,(text,actual)
                assert normalized==expected,(text,normalized,expected)


def test_three_and_four_dots_have_clearance_and_native_bodies_survive(built):
    f,_=built
    for name in f.getGlyphOrder():
        if not name.startswith('nuktakawi'):continue
        g=f['glyf'][name];coords,ends,_=g.getCoordinates(f['glyf'])
        if name in ['nuktakawi','nuktakawi.four']:
            assert len(ends)==(3 if name=='nuktakawi' else 4)
            continue
        host=name[len('nuktakawi_'):]
        count=4 if 'anusvara' in host else 3
        contour_bounds=[];start=0
        for end in ends:
            points=coords[start:end+1]
            contour_bounds.append((min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)))
            start=end+1
        dots=contour_bounds[-count:];body=contour_bounds[:-count]
        assert len(dots)==count
        if body:assert min(b[1] for b in dots)>=max(b[3] for b in body)+69
        for i,a in enumerate(dots):
            for b in dots[i+1:]:
                assert a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1]


def test_packaged_nukta_and_older_kawi_shaping(built):
    f,path=built
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSansKawi-Regular.ttf'))
    delivered=ROOT/e['file'];packaged=TTFont(delivered)
    assigned=set(range(0x11F00,0x11F11)) | set(range(0x11F12,0x11F3B)) | set(range(0x11F3E,0x11F5B))
    assert len(assigned)==87 and assigned <= packaged.getBestCmap().keys()
    for cp in range(0x11F12,0x11F34):
        for suffix in ['',chr(0x11F36),chr(0x11F36)+chr(0x11F01),chr(0x11F38)]:
            text=chr(0x11F02)+chr(cp)+suffix
            assert shape(ROOT/e['source'],text)==shape(delivered,text)
            new=chr(0x11F02)+chr(cp)+chr(0x11F5A)+suffix
            assert shape(path,new)==shape(delivered,new)
