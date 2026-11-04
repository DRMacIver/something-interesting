"""A retained connector must keep its complete native component graph."""
import json
from pathlib import Path
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import source_preservation as policy


def drawing(font,name):
    gs=font.getGlyphSet();pen=DecomposingRecordingPen(gs);gs[name].draw(pen);return pen.value


def test_policy_restores_native_component_closure_not_only_parent(tmp_path,monkeypatch):
    font=TTFont(ROOT/'build/unicode-sources/unicodia/ArchaicCuneiformNumerals.ttf')
    name=font.getBestCmap()[0x1262d];before=drawing(font,name)
    report=tmp_path/'report.json'
    def adapt(f,source):
        records=[]
        for gid,n in enumerate(f.getGlyphOrder()):
            g=f['glyf'][n]
            if not g.isComposite() and g.numberOfContours:
                for i,(x,y) in enumerate(g.coordinates):g.coordinates[i]=(x+3,y)
            records.append(dict(gid=gid,glyph=n,status='adapted'))
        report.write_text(json.dumps(dict(records=records,counts={'adapted':len(records)},method='test-kernel')))
        return dict(report='report.json')
    monkeypatch.setattr(policy,'ROOT',tmp_path)
    result=policy.apply(font,'ArchaicCuneiformNumerals.ttf',adapt)
    assert drawing(font,name)==before
    assert len(result['sourcePolicy']['glyphs'])>1
    written=json.loads((tmp_path/result['report']).read_text())
    guarded=[r for r in written['records'] if r.get('sourcePolicy')]
    assert guarded and all(r['status']=='native-retained-guard' for r in guarded)
    assert sum(written['counts'].values())==len(written['records'])
