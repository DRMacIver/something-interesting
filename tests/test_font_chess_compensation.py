"""The placement of infinity in the two chess annotations stays contrastive."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, ROOT, shape
from test_font_cuneiform import outline


def contours(font, cp):
    glyph=font['glyf'][font.getBestCmap()[cp]]
    points,ends,_=glyph.getCoordinates(font['glyf']);start=0;boxes=[]
    for end in ends:
        p=points[start:end+1];start=end+1
        boxes.append((min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)))
    return boxes


def test_infinity_above_and_below_preserve_bar_order_counters_and_advance():
    for cp,above in [(0x2b96,True),(0x2bf9,False)]:
        e=next(e for e in manifest()['fonts'] if any(a<=cp<=b for a,b in e['ranges']))
        font=TTFont(ROOT/e['file']);boxes=contours(font,cp)
        assert len(boxes)==5
        bars=[b for b in boxes if b[2]-b[0]>600 and b[3]-b[1]<80]
        assert len(bars)==2
        bars.sort(key=lambda b:b[1]);assert bars[0][3]+60<bars[1][1]
        loops=[b for b in boxes if b not in bars]
        outer=max(loops,key=lambda b:b[2]-b[0]);holes=[b for b in loops if b!=outer]
        assert len(holes)==2
        for hole in holes:
            assert outer[0]<hole[0]<hole[2]<outer[2]
            assert outer[1]<hole[1]<hole[3]<outer[3]
        if above: assert outer[1]>bars[-1][3]+70
        else: assert outer[3]+60<bars[0][1]
        assert outline(font,cp)[2]==766
        assert shape(ROOT/e['file'],chr(cp))==shape(ROOT/e['source'],chr(cp))
        if above:
            source=TTFont(ROOT/e['source']);a,b=outline(source,cp),outline(font,cp)
            assert a[0]!=b[0]
            assert max(abs(x-y) for x,y in zip(a[1],b[1]))<=4


def test_shatranj_white_black_pairs_keep_piece_identity_and_fill_distinction():
    from fontTools.pens.areaPen import AreaPen
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    font=TTFont(ROOT/e['file']);source=TTFont(ROOT/e['source']);areas=[]
    for cp in range(0x1fa54,0x1fa58):
        a,b=outline(source,cp),outline(font,cp)
        assert a[2]==b[2]>0
        assert a[0]!=b[0] and b[1]
        assert max(abs(x-y) for x,y in zip(a[1],b[1]))<=4
        assert len(contours(source,cp))==len(contours(font,cp))
        glyphs=font.getGlyphSet();pen=AreaPen(glyphs)
        glyphs[font.getBestCmap()[cp]].draw(pen);areas.append(abs(pen.value))
        assert shape(ROOT/e['source'],chr(cp))==shape(ROOT/e['file'],chr(cp))
    # Filled black pieces must not become outlines or duplicate the white pair.
    assert areas[2]>areas[0]*1.5 and areas[3]>areas[1]*1.5
    assert len({repr(outline(font,cp)[0]) for cp in range(0x1fa54,0x1fa58)})==4
