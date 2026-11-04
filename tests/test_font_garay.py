"""Garay native shaping: real mark geometry, case, spelling and direction."""
import json
import io
from pathlib import Path
import pytest
import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'output/font-review/garay/DadGaray.ttf'
MARKS=set(range(0x10D69,0x10D6E))


@pytest.fixture(scope='module',params=['review','packaged'])
def font(request):
    if request.param=='review':return TTFont(PATH)
    m=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    e=next(e for e in m['fonts'] if e['source'].endswith('/DadGaray.ttf'))
    return TTFont(ROOT/e['file'])


def shape(font,text,direction=None):
    stream=io.BytesIO();font.flavor=None;font.save(stream)
    hfont=hb.Font(hb.Face(stream.getvalue()));buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties()
    if direction:buf.direction=direction
    hb.shape(hfont,buf)
    out=[];cursor=0;gs=font.getGlyphSet()
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        assert info.codepoint
        name=font.getGlyphName(info.codepoint);pen=BoundsPen(gs);gs[name].draw(pen);box=pen.bounds
        if box:box=(box[0]+cursor+pos.x_offset,box[1]+pos.y_offset,box[2]+cursor+pos.x_offset,box[3]+pos.y_offset)
        out.append(dict(name=name,advance=pos.x_advance,box=box,cluster=info.cluster))
        cursor+=pos.x_advance
    return out


def test_complete_repertoire_and_no_lost_contours(font):
    expected={int(l.split(';')[0],16) for l in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
              if 0x10D40<=int(l.split(';')[0],16)<=0x10D8F}
    assert len(expected)==69 and set(font.getBestCmap())==expected|{32}
    review=json.loads(PATH.with_suffix('.json').read_text())
    for record in review['glyphs']:
        cp=int(record['codepoint'][2:],16);g=font['glyf'][font.getBestCmap()[cp]]
        assert g.numberOfContours==len(record['componentAreaRatios'])+len(record['counterOverlap'])


@pytest.mark.parametrize('mark',sorted(MARKS))
def test_all_marks_attach_above_each_case_without_advance(font,mark):
    for cp in list(range(0x10D50,0x10D66))+list(range(0x10D70,0x10D86)):
        result=shape(font,chr(cp)+chr(mark))
        base=next(g for g in result if g['name']==f'u{cp:X}')
        accent=next(g for g in result if g['name']==f'u{mark:X}')
        assert accent['advance']==0 and base['advance']>0
        b,a=base['box'],accent['box']
        assert abs(a[0]+a[2]-b[0]-b[2])<=2
        assert 54<=a[1]-b[3]<=56


def test_marks_stack_and_stay_with_their_own_base(font):
    result=shape(font,chr(0x10D73)+chr(0x10D69)*2+chr(0x10D74)+chr(0x10D6A))
    assert [g['cluster'] for g in result]==[3,3,0,0,0]
    marks=sorted([g['box'] for g in result if g['name']=='u10D69'],key=lambda b:b[1])
    assert marks[1][1]-marks[0][3]>=54


def test_case_swashes_are_real_distinct_outlines(font):
    for upper in range(0x10D50,0x10D66):
        a=font['glyf'][font.getBestCmap()[upper]];b=font['glyf'][font.getBestCmap()[upper+32]]
        assert a.compile(font['glyf'])!=b.compile(font['glyf'])
        assert a.yMax>b.yMax


@pytest.mark.parametrize('sequence',[(0x10D73,),(0x10D73,0x10D69),(0x10D73,0x10D69,0x10D4D),
    (0x10D74,0x10D69),(0x10D74,0x10D69,0x10D4D),(0x10D74,0x10D69,0x10D4D,0x10D4D),
    (0x10D74,),(0x10D74,0x10D4D),(0x10D74,0x10D4D,0x10D4D)])
def test_unicode_figure_19_5_retains_input_spelling(font,sequence):
    result=shape(font,''.join(map(chr,sequence)))
    assert len(result)==len(sequence)
    assert sorted(g['name'] for g in result)==sorted(f'u{cp:X}' for cp in sequence)
    assert sum(g['advance'] for g in result)==sum(font['hmtx'][f'u{cp:X}'][0] for cp in sequence)


def test_letters_rtl_digits_ltr_and_spacing_signs(font):
    letters=[0x10D70,0x10D71,0x10D72]
    assert [g['name'] for g in shape(font,''.join(map(chr,letters)))]==[f'u{cp:X}' for cp in letters[::-1]]
    digits=list(range(0x10D40,0x10D4A))
    # The UBA resolves AN digit runs to an even embedding level; feed that run
    # direction to the shaper as the app does, rather than reversing digits.
    assert [g['name'] for g in shape(font,''.join(map(chr,digits)),'ltr')]==[f'u{cp:X}' for cp in digits]
    for cp in (0x10D4D,0x10D4E,0x10D4F,0x10D6E,0x10D6F,0x10D8E,0x10D8F):
        assert font['hmtx'][f'u{cp:X}'][0]>0
