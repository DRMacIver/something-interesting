"""Dense finishing must preserve native stroke graph, metrics and cached output."""
import io
import sys
from pathlib import Path
import numpy as np
import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from dense_skeleton_kernel import reink_candidates,validate_reconstruction
from dense_skeleton_adapter import apply
from dense_native_adapter import apply as native_apply
from supplemental_pressure import shaped


def test_complete_native_skeleton_and_counter_survive_reinking():
    mask=np.zeros((96,128),dtype=bool)
    mask[10:70,15:20]=True;mask[10:15,15:65]=True
    mask[65:70,15:65]=True;mask[10:70,60:65]=True
    mask[80:83,100:108]=True  # Independent short meaningful stroke.
    mask=np.kron(mask,np.ones((4,4),dtype=bool))
    candidates=list(reink_candidates(mask,7))
    assert candidates
    result,record=candidates[0]
    assert record['skeletonRetained']
    assert record['branchesPruned']==0
    validate_reconstruction(mask,result)
    assert result[320:332,400:432].any()


def fixture_font():
    builder=FontBuilder(1000,isTTF=True);builder.setupGlyphOrder(['.notdef','H'])
    blank=TTGlyphPen(None);pen=TTGlyphPen(None)
    for x0,y0,x1,y1 in [(50,0,90,700),(350,0,390,700),(90,320,350,360)]:
        pen.moveTo((x0,y0));pen.lineTo((x1,y0));pen.lineTo((x1,y1));pen.lineTo((x0,y1));pen.closePath()
    builder.setupGlyf({'.notdef':blank.glyph(),'H':pen.glyph()})
    builder.setupHorizontalMetrics({'.notdef':(500,0),'H':(500,50)})
    builder.setupHorizontalHeader(ascent=800,descent=-200)
    builder.setupCharacterMap({72:'H'})
    builder.setupNameTable({'familyName':'DenseTest','styleName':'Regular','uniqueFontIdentifier':'DenseTest','fullName':'DenseTest','psName':'DenseTest'})
    builder.setupOS2(sTypoAscender=800,sTypoDescender=-200,usWinAscent=800,usWinDescent=200)
    builder.setupPost();builder.setupMaxp()
    data=io.BytesIO();builder.font.save(data);return data.getvalue()


@pytest.mark.parametrize('finish',[apply,native_apply])
def test_dense_cache_reuses_geometry_without_changing_native_shaping_or_bbox(tmp_path,finish):
    raw=fixture_font();font=TTFont(io.BytesIO(raw));before=shaped(font,'HH')
    native_box=tuple(getattr(font['glyf']['H'],a) for a in ['xMin','yMin','xMax','yMax'])
    report=finish(font,'Jigmo.ttf',cache_dir=tmp_path,glyph_names={'H'})
    assert shaped(font,'HH')==before
    assert tuple(getattr(font['glyf']['H'],a) for a in ['xMin','yMin','xMax','yMax'])==native_box
    assert report['layoutTablesUnchanged']==['hmtx']
    assert report['glyphs']==1
    warm_font=TTFont(io.BytesIO(raw))
    warm=finish(warm_font,'Jigmo.ttf',cache_dir=tmp_path,glyph_names={'H'})
    assert warm['cacheHits']==1
    assert warm_font['glyf']['H'].compile(warm_font['glyf'])==font['glyf']['H'].compile(font['glyf'])


def test_displaylist_masks_match_source_raster_at_fractional_phases():
    from dense_display_raster import GlyphRaster
    from supplemental_pressure import raster
    font=TTFont(io.BytesIO(fixture_font()));cached=GlyphRaster(font,'H')
    for size in (384,1024):
        expected,frame=raster(font,'H',size);actual,other=cached(size)
        assert other==frame and np.array_equal(actual,expected)
        left,top,scale=frame
        for dx,dy in ((.25,.75),(.5,.5),(.75,.25)):
            viewport=(left+dx,top+dy,scale,expected.shape[1],expected.shape[0])
            expected,_=raster(font,'H',viewport=viewport);actual,_=cached(viewport=viewport)
            assert np.array_equal(actual,expected)


def test_zero_area_native_outline_stays_blank_without_attempting_flex(tmp_path):
    font=TTFont(io.BytesIO(fixture_font()));line=TTGlyphPen(None)
    line.moveTo((50,0));line.lineTo((50,700));line.closePath();font['glyf']['H']=line.glyph()
    report=native_apply(font,'Jigmo.ttf',cache_dir=tmp_path,glyph_names={'H'})
    assert report['counts']=={'native-blank':1}
    assert report['nativeBoundsPreserved']


def test_native_variation_mapping_and_shaping_survive_dense_finish(tmp_path):
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
    font=TTFont(io.BytesIO(fixture_font()))
    variation=CmapSubtable.newSubtable(14);variation.platformID=0;variation.platEncID=5
    variation.language=0;variation.cmap={};variation.uvsDict={0xfe00:[(0x48,None)]}
    font['cmap'].tables.append(variation)
    before=font['cmap'].compile(font);positions=shaped(font,'H\ufe00')
    native_apply(font,'Jigmo.ttf',cache_dir=tmp_path,glyph_names={'H'})
    assert font['cmap'].compile(font)==before
    assert shaped(font,'H\ufe00')==positions


def test_production_report_records_native_input_and_relative_profile(tmp_path):
    font=TTFont(io.BytesIO(fixture_font()))
    report=native_apply(font,ROOT/'Jigmo.ttf',cache_dir=tmp_path/'cache',glyph_names={'.notdef'},report_dir=tmp_path/'reports')
    assert report['source']=='Jigmo.ttf'
    assert report['sourceProfile']=='Jigmo.ttf'
    assert report['nativeEmUnchanged']==1000
    assert len(report['nativeInputSha256'])==64
    assert not {'records','seconds','cacheHits'}&report.keys()
    import json
    detail=json.loads(Path(report['report']).read_text())
    assert detail['nativeInputSha256']==report['nativeInputSha256']
    assert detail['counts']=={'native-blank':1}
    assert detail['records'][0]['status']=='native-blank'
    assert not {'seconds','cacheHits'}&detail.keys()
