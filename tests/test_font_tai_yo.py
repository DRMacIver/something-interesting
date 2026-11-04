"""Tai Yo horizontal layout: body anchors, adjacent marks and spelling identity."""
import json
import io
from pathlib import Path
import numpy as np
import pymupdf
import pytest
import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'output/font-review/tai-yo/DadTaiYo.ttf'
MARKS={0x1E6E3,0x1E6E6,0x1E6EE,0x1E6EF,0x1E6F5}


@pytest.fixture(scope='module',params=['review','packaged'])
def font(request):
    if request.param=='review':return TTFont(PATH)
    m=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    e=next(e for e in m['fonts'] if e['source'].endswith('/DadTaiYo.ttf'))
    return TTFont(ROOT/e['file'])


def shape(font,points):
    buf=hb.Buffer();buf.add_str(''.join(map(chr,points)));buf.guess_segment_properties()
    stream=io.BytesIO();font.flavor=None;font.save(stream)
    hb.shape(hb.Font(hb.Face(stream.getvalue())),buf)
    gs=font.getGlyphSet();out=[];cursor=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        assert info.codepoint
        name=font.getGlyphName(info.codepoint);p=BoundsPen(gs);gs[name].draw(p)
        x=cursor+pos.x_offset;y=pos.y_offset;b=p.bounds
        out.append(dict(name=name,advance=pos.x_advance,x=x,y=y,
                        box=(b[0]+x,b[1]+y,b[2]+x,b[3]+y) if b else None))
        cursor+=pos.x_advance
    return out


def mask(font,glyph):
    gs=font.getGlyphSet();pen=SVGPathPen(gs);gs[glyph['name']].draw(pen)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="380" viewBox="-400 -1600 2200 1900"><rect x="-400" y="-1600" width="2200" height="1900" fill="white"/><path fill="black" transform="scale(1 -1) translate({glyph["x"]} {glyph["y"]})" d="{pen.getCommands()}"/></svg>'
    doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
    pix=pdf[0].get_pixmap(alpha=False)
    return np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n).max(axis=2)<128


def test_all_assigned_drawings_and_contours_survive(font):
    expected={int(l.split(';')[0],16) for l in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
              if 0x1E6C0<=int(l.split(';')[0],16)<=0x1E6FF}
    assert len(expected)==55 and set(font.getBestCmap())==expected|{32}
    for record in json.loads(PATH.with_suffix('.json').read_text())['glyphs']:
        cp=int(record['codepoint'][2:],16)
        assert font['glyf'][font.getBestCmap()[cp]].numberOfContours==len(record['componentAreaRatios'])+len(record['counterOverlap'])


@pytest.mark.parametrize('mark',sorted(MARKS))
def test_marks_attach_without_advance_or_base_ink_collision(font,mark):
    for base in range(0x1E6C0,0x1E6DF):
        b,m=shape(font,[base,mark])
        assert b['advance']>0 and m['advance']==0
        assert not (mask(font,b)&mask(font,m)).any(),(hex(base),hex(mark))


@pytest.mark.parametrize('base',[0x1E6CD,0x1E6D5])
@pytest.mark.parametrize('mark',[0x1E6EE,0x1E6EF])
def test_wide_consonants_use_left_body_not_tail(font,base,mark):
    b,m=shape(font,[base,mark]);box=b['box'];accent=m['box']
    assert (accent[0]+accent[2])/2 < (box[0]+box[2])/2-80
    if base==0x1E6CD:
        assert accent[1]<box[3]-200
        assert accent[3]<box[3]+80


@pytest.mark.parametrize('base,marks',[(0x1E6C5,[0x1E6EE,0x1E6EE]),(0x1E6DC,[0x1E6EE,0x1E6EF])])
def test_figure_16_9_marks_are_adjacent_not_stacked(font,base,marks):
    b,first,second=shape(font,[base]+marks)
    assert first['advance']==second['advance']==0
    assert 54<=second['box'][0]-first['box'][2]<=56
    assert abs(second['box'][1]-first['box'][1])<=1
    assert not (mask(font,b)&(mask(font,first)|mask(font,second))).any()


@pytest.mark.parametrize('points',[
    [0x1E6D6,0x1E6E3],[0x1E6C6,0x1E6E3],
    [0x1E6D1,0x1E6E2,0x1E6CF],[0x1E6D4,0x1E6E2,0x1E6CF],
    [0x1E6C5,0x1E6EE,0x1E6E9,0x1E6CF],
    [0x1E6C0,0x1E6D9],[0x1E6C1,0x1E6D9],[0x1E6DD],[0x1E6DE],
])
def test_published_spelling_and_explicit_kvo_remain_distinct(font,points):
    result=shape(font,points)
    assert [g['name'] for g in result]==[f'u{cp:X}' for cp in points]
    assert [bool(g['advance']) for g in result]==[cp not in MARKS for cp in points]
