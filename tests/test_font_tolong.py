"""Compiled Tolong review font: mark geometry and spacing, not just cmap."""
from pathlib import Path
import json
import io
import pytest
import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT/'output/font-review/tolong/DadTolongReview.ttf'
ABOVE = {0x303,0x306,0x307,0x308,0x304}
BELOW = {0x330,0x324,0x323,0x331}


@pytest.fixture(scope='module', params=['review', 'packaged'])
def font(request):
    if request.param == 'review':
        return TTFont(PATH)
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if e['source'].endswith('/DadTolong.ttf'))
    return TTFont(ROOT/entry['file'])


def shaped(font, text):
    stream=io.BytesIO(); font.flavor=None; font.save(stream)
    hfont = hb.Font(hb.Face(stream.getvalue()))
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hfont, buf)
    result=[]; cursor=0
    gs=font.getGlyphSet()
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        assert info.codepoint != 0
        name=font.getGlyphName(info.codepoint)
        pen=BoundsPen(gs); gs[name].draw(pen)
        box=pen.bounds
        if box:
            box=(box[0]+cursor+pos.x_offset,box[1]+pos.y_offset,
                 box[2]+cursor+pos.x_offset,box[3]+pos.y_offset)
        result.append((name,pos.x_advance,box))
        cursor+=pos.x_advance
    return result


def test_repertoire_and_real_outlines(font):
    expected={int(l.split(';')[0],16) for l in
              (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
              if 0x11DB0<=int(l.split(';')[0],16)<=0x11DEF}
    assert len(expected)==54
    assert set(font.getBestCmap()) == expected|ABOVE|BELOW|{32}
    for cp in expected|ABOVE|BELOW:
        assert font['glyf'][font.getBestCmap()[cp]].numberOfContours>0


@pytest.mark.parametrize('mark', sorted(ABOVE|BELOW))
def test_marks_attach_centered_and_clear_every_letter(font,mark):
    for cp in range(0x11DB0,0x11DD9):
        base, accent=shaped(font, chr(cp)+chr(mark))
        assert accent[1]==0 and base[1]==500
        b,a=base[2],accent[2]
        assert abs((a[0]+a[2])-(b[0]+b[2]))<=2
        if mark in ABOVE:
            assert 54<=a[1]-b[3]<=56
        else:
            assert 54<=b[1]-a[3]<=56


@pytest.mark.parametrize('mark',[0x303,0x324])
def test_repeated_marks_stack_without_colliding(font,mark):
    base,first,second=shaped(font,chr(0x11DB0)+chr(mark)*2)
    assert first[1]==second[1]==0
    if mark in ABOVE:
        assert second[2][1]-first[2][3]>=54
    else:
        assert first[2][1]-second[2][3]>=54


def test_both_sides_and_spacing_signs(font):
    for sign in (0x11DD9,0x11DDA):
        result=shaped(font,chr(0x11DB0)+'\u0324\u0303'+chr(sign))
        assert [r[1] for r in result]==[500,0,0,500]
        assert result[1][2][3]<result[0][2][1]
        assert result[2][2][1]>result[0][2][3]
        assert result[-1][2][0]>=500


def test_tracing_keeps_components_and_counters(font):
    review=json.loads(PATH.with_suffix('.json').read_text())
    for record in review['glyphs']:
        cp=int(record['codepoint'][2:],16)
        contours=font['glyf'][font.getBestCmap()[cp]].numberOfContours
        assert contours==len(record['componentAreaRatios'])+len(record['counterOverlap'])
