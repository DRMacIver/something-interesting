"""Every geomantic figure retains its exact four-row dot identity."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest,ROOT
from test_font_cuneiform import outline


def test_all_sixteen_patterns_have_separate_dots_and_centered_rows():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    f=TTFont(ROOT/e['file']);source=TTFont(ROOT/e['source']);patterns=[]
    for index in range(16):
        cp=0x1CEE0+index;glyph=f['glyf'][f.getBestCmap()[cp]]
        pts,ends,_=glyph.getCoordinates(f['glyf']);dots=[];start=0
        for end in ends:
            p=pts[start:end+1];start=end+1
            dots.append((min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)))
        rows=[]
        for row,y in enumerate([720,480,240,0]):
            cells=[b for b in dots if abs((b[1]+b[3])/2-y)<4]
            expected=1 if index & (1 << (3-row)) else 2
            assert len(cells)==expected,(hex(cp),row,cells)
            centers=sorted((b[0]+b[2])/2 for b in cells)
            target=[375.5] if expected==1 else [165.5,585.5]
            assert all(abs(a-b)<4 for a,b in zip(centers,target))
            rows.append(len(cells))
        assert len(dots)==sum(rows)
        for i,a in enumerate(dots):
            for b in dots[i+1:]:
                assert a[2]+40<b[0] or b[2]+40<a[0] or a[3]+40<b[1] or b[3]+40<a[1]
        before,after=outline(source,cp),outline(f,cp)
        assert before[2]==after[2]==751
        assert before[0]!=after[0]
        assert max(abs(a-b) for a,b in zip(before[1],after[1]))<=4
        patterns.append(tuple(rows))
    assert len(set(patterns))==16
