"""Chemical arrow distinctions survive the pen treatment and subsetting."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, ROOT
from test_font_cuneiform import outline

POINTS=[0x1CEF0,*range(0x1F8D0,0x1F8D9)]


def fonts():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    return TTFont(ROOT/e['source']),TTFont(ROOT/e['file'])


def contours(f,cp):
    glyph=f['glyf'][f.getBestCmap()[cp]]
    points,ends,_=glyph.getCoordinates(f['glyf'])
    start=0;result=[]
    for end in ends:
        result.append(list(points[start:end+1]));start=end+1
    return result


def test_distinct_drawings_metrics_and_small_ink_deformation():
    source,font=fonts();drawings=[]
    for cp in POINTS:
        before=outline(source,cp);after=outline(font,cp)
        assert before[2]==after[2]>0
        assert before[0]!=after[0]  # Adaptation was actually applied.
        assert max(abs(a-b) for a,b in zip(before[1],after[1]))<=4
        assert len(contours(source,cp))==len(contours(font,cp))
        drawings.append(after[0])
    assert all(a!=b for i,a in enumerate(drawings) for b in drawings[i+1:])
    assert len(contours(font,0x1CEF0))==3  # Two white regions around the bar.
    assert len(contours(font,0x1F8D8))==2  # Dependent lobe retains its counter.


def test_harpoon_lengths_and_directions_remain_semantically_distinct():
    _,f=fonts()
    for cp in range(0x1F8D1,0x1F8D6):
        cs=sorted(contours(f,cp),key=lambda p:sum(y for x,y in p)/len(p))
        bottom,top=cs
        width=lambda p:max(x for x,y in p)-min(x for x,y in p)
        bw,tw=width(bottom),width(top)
        if cp==0x1F8D1:assert abs(bw-tw)<=6
        elif cp in (0x1F8D2,0x1F8D4):assert tw>1.6*bw
        else:assert bw>1.6*tw
        # The upper barb points to the side where its high endpoint lies;
        # the lower barb uses the low endpoint on the opposite side.
        top_tip=max(top,key=lambda p:p[1])[0]
        bottom_tip=min(bottom,key=lambda p:p[1])[0]
        center=567
        if cp in (0x1F8D1,0x1F8D2,0x1F8D3):
            assert top_tip>center and bottom_tip<center
        else:assert top_tip<center and bottom_tip>center


def test_isolobal_arrow_has_both_heads_and_a_dependent_lobe():
    _,f=fonts();outer,hole=contours(f,0x1F8D8)
    # Both heads reach above/below the shaft near their respective ends.
    for points in [[(x,y) for x,y in outer if x<270],[(x,y) for x,y in outer if x>860]]:
        assert max(y for x,y in points)>485
        assert min(y for x,y in points)<205
    assert min(y for x,y in outer)<-55
    assert max(y for x,y in hole)<290 and min(y for x,y in hole)<0
