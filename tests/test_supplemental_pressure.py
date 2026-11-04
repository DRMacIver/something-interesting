"""Pressure experiments must retain native layout and reject lost details."""
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from supplemental_pressure import candidate, pressure, shaped
from prototype_unifont_lettering import validate_reconstruction


def test_pressure_changes_width_without_losing_counter_or_detached_mark():
    y,x=np.mgrid[:220,:220]
    mask=((x-100)**2+(y-110)**2<70**2)&((x-100)**2+(y-110)**2>48**2)
    mask[8:20,95:107]=True
    after,record=pressure(mask,.45,17)
    assert record['changedPixels']>10
    validate_reconstruction(mask,after)
    again,_=pressure(mask,.45,17)
    assert np.array_equal(after,again)


def test_join_guard_preserves_boundary_pixels():
    mask=np.zeros((120,160),bool);mask[45:70,10:150]=True
    protected=np.ones((1,160));protected[:,:30]=0;protected[:,130:]=0
    after,_=pressure(mask,.45,10,protected)
    assert np.array_equal(after[:,:30],mask[:,:30])
    assert np.array_equal(after[:,130:],mask[:,130:])


def test_native_bengali_layout_and_tables_survive_sample_transformation(tmp_path):
    review=json.loads((ROOT/'docs/source-style-review.json').read_text())
    row=next(s for s in review['sources'] if s['number']==32)
    source=ROOT/row['fonts'][0]['file'];output=tmp_path/'pressure.ttf'
    report=candidate(source,row['sample'],output)
    before=TTFont(source);after=TTFont(output)
    assert report['shapingUnchanged']
    assert any(g['status']=='candidate' and g['changedPixels'] for g in report['glyphs'])
    assert shaped(before,row['sample'])==shaped(after,row['sample'])
    for tag in ('GPOS','GSUB','GDEF','hmtx'):
        if tag in before: assert before[tag].compile(before)==after[tag].compile(after)
    assert before['head'].unitsPerEm==after['head'].unitsPerEm


def test_production_adapter_is_cached_and_retains_native_layout(tmp_path,monkeypatch):
    import supplemental_adapter as adapter
    from fontTools import subset
    review=json.loads((ROOT/'docs/source-style-review.json').read_text())
    row=next(s for s in review['sources'] if s['number']==32)
    f=TTFont(ROOT/row['fonts'][0]['file'],recalcTimestamp=False)
    sub=subset.Subsetter();sub.populate(text=row['sample']);sub.subset(f)
    f.flavor=None
    import io
    raw=io.BytesIO();f.save(raw)
    before=shaped(f,row['sample'])
    monkeypatch.setattr(adapter,'CACHE',tmp_path/'cache')
    monkeypatch.setattr(adapter,'baseline',lambda source:None)
    # Cache path is normally repo relative; make temporary output recordable.
    monkeypatch.setattr(adapter,'ROOT',tmp_path)
    report=adapter.apply(f,'NotoSansBengali-Regular.ttf')
    assert report['counts']['adapted']>0
    assert shaped(f,row['sample'])==before
    second=TTFont(io.BytesIO(raw.getvalue()),recalcTimestamp=False)
    repeated=adapter.apply(second,'NotoSansBengali-Regular.ttf')
    assert repeated==report
    assert second['glyf'].compile(second)==f['glyf'].compile(f)


def test_native_phantom_origin_and_attachment_frame_are_preserved(tmp_path,monkeypatch):
    import supplemental_adapter as adapter
    from fontTools import subset
    review=json.loads((ROOT/'docs/source-style-review.json').read_text())
    row=next(s for s in review['sources'] if s['number']==26)
    f=TTFont(ROOT/row['fonts'][0]['file'],recalcTimestamp=False)
    sub=subset.Subsetter();sub.populate(text=row['sample']);sub.subset(f)
    original={name:((g.xMin,g.yMin,g.xMax,g.yMax),f['hmtx'][name]) for name in f.getGlyphOrder() if (g:=f['glyf'][name]).numberOfContours}
    monkeypatch.setattr(adapter,'CACHE',tmp_path/'cache');monkeypatch.setattr(adapter,'ROOT',tmp_path);monkeypatch.setattr(adapter,'baseline',lambda source:None)
    report=adapter.apply(f,'NotoSansArmenian-Regular.ttf')
    assert report['nativeBoundsPreserved']
    for name,(bounds,metric) in original.items():
        g=f['glyf'][name]
        assert (g.xMin,g.yMin,g.xMax,g.yMax)==bounds
        assert f['hmtx'][name]==metric
        assert f['hmtx'][name][1]-g.xMin==metric[1]-bounds[0]


def test_raw_native_post3_source_names_survive_production_snapshot(tmp_path,monkeypatch):
    import supplemental_adapter as adapter
    from fontTools import subset
    review=json.loads((ROOT/'docs/source-style-review.json').read_text())
    row=next(s for s in review['sources'] if s['number']==26)
    f=TTFont(ROOT/row['source'],recalcTimestamp=False)
    sub=subset.Subsetter();sub.populate(text=row['sample']);sub.subset(f)
    # Native source/subsetter retains names in memory while post3 deliberately
    # drops them on serialization. The immutable snapshot must retain ID/name
    # correspondence to target hmtx, GSUB and GPOS tables.
    f['post'].formatType=3
    names=list(f.getGlyphOrder());layout=shaped(f,row['sample'])
    monkeypatch.setattr(adapter,'CACHE',tmp_path/'cache');monkeypatch.setattr(adapter,'ROOT',tmp_path);monkeypatch.setattr(adapter,'baseline',lambda source:None)
    report=adapter.apply(f,'NotoSansArmenian-Regular.ttf')
    assert report['counts']['adapted']>0
    assert list(f.getGlyphOrder())==names
    assert shaped(f,row['sample'])==layout


def test_source_recipe_hash_ignores_unrelated_later_groups(monkeypatch):
    import supplemental_adapter as adapter
    name='NotoSansArmenian-Regular.ttf';original=adapter.recipe_hash(name)
    monkeypatch.setitem(adapter.SOURCES,'Unrelated.ttf',dict(amount=.3,category='future-group'))
    assert adapter.recipe_hash(name)==original
    monkeypatch.setitem(adapter.SOURCES,name,dict(amount=.4,category='changed'))
    assert adapter.recipe_hash(name)!=original
