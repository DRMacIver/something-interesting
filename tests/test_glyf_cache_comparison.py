"""Exact GLYF fast path keeps every original geometry fallback decision."""
import copy
import io
import pytest
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from font_baseline_checks import assert_cached_glyf_drawing
from test_dense_skeleton import fixture_font


@pytest.mark.parametrize('case',['simple','composite','bbox','coordinates','component-offset','instructions'])
def test_byte_equality_or_exact_geometry_fallback(case,monkeypatch):
    font=TTFont(io.BytesIO(fixture_font()));table=font['glyf']
    pen=TTGlyphPen(font.getGlyphSet());pen.addComponent('H',(1,0,0,1,30,0));component=pen.glyph();table['composite']=component;component.recalcBounds(table)
    native=component if case in {'composite','component-offset'} else table['H']
    data=native.compile(table,recalcBBoxes=False);expected=Glyph(data=data);expected.expand(table);actual=copy.deepcopy(native)
    if case=='bbox':actual.xMin-=1
    elif case=='coordinates':actual.coordinates[0]=(actual.coordinates[0][0]+1,actual.coordinates[0][1])
    elif case=='component-offset':actual.components[0].x+=1
    elif case=='instructions':actual.program=Program();actual.program.fromBytecode(b'\xb0\x00')
    def drawing(glyph):
        pen=RecordingPen();glyph.draw(pen,table);return pen.value
    old=drawing(expected)==drawing(actual);before=drawing(actual)
    calls=[];original=Glyph.draw
    def draw(*args,**kwargs):calls.append(1);return original(*args,**kwargs)
    monkeypatch.setattr(Glyph,'draw',draw)
    if old:assert_cached_glyf_drawing(data,actual,table,case)
    else:
        with pytest.raises(AssertionError):assert_cached_glyf_drawing(data,actual,table,case)
    assert len(calls)==(0 if case in {'simple','composite'} else 2)
    assert drawing(actual)==before,'Compile must not change drawing geometry'
