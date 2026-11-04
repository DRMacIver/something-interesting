"""Cubic production candidates preserve curves on rejection and native layout."""
import io
from pathlib import Path
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import supplemental_cubic_adapter as adapter
from supplemental_pressure import shaped


def test_cubic_cache_preserves_native_layout_bounds_and_output_kind(tmp_path,monkeypatch):
    f=TTFont(ROOT/'assets/fonts/dad-math-variants.woff2',recalcTimestamp=False)
    text='ℋℋ\ufe01ℐℐ\ufe01'
    options=subset.Options();options.layout_features=['*']
    sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(f)
    f.flavor=None;stream=io.BytesIO();f.save(stream)
    old=TTFont(io.BytesIO(stream.getvalue()),recalcTimestamp=False)
    monkeypatch.setattr(adapter,'ROOT',tmp_path);monkeypatch.setattr(adapter,'CACHE',tmp_path/'cache')
    # Exercise same accepted kernel against a bounded native cubic fixture.
    monkeypatch.setattr(adapter,'SOURCES',{'fixture.otf':{'amount':.45,'category':'test-native-cubic'}})
    before=shaped(f,text);boxes={n:adapter.bounds(f,n) for n in f.getGlyphOrder()}
    report=adapter.apply(f,'fixture.otf')
    assert report['counts']['adapted']>0
    assert 'CFF ' in f and 'glyf' not in f
    assert shaped(f,text)==before
    for name,box in boxes.items():
        other=adapter.bounds(f,name)
        if box:assert all(abs(a-b)<adapter.BOUNDS_TOLERANCE for a,b in zip(box,other))
        else:assert other is None
    repeated=adapter.apply(old,'fixture.otf')
    assert repeated==report
    assert old['CFF '].compile(old)==f['CFF '].compile(f)
