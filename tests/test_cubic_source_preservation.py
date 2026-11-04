"""A full-field cubic exception retains exact native Type2 ink, not fallback."""
import copy
import hashlib
import json
from pathlib import Path
import sys

from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import cubic_source_preservation as policy


def test_cubic_policy_restores_only_approved_native_charstring(tmp_path,monkeypatch):
    font=TTFont(ROOT/'output/font-review/supplemental-production-baselines/1a10ab6b39c1.woff2')
    original=font['CFF '].cff.topDictIndex[0].CharStrings
    name=font.getBestCmap()[0x18f6c];other=font.getBestCmap()[0x558]
    before=policy.charstring_bytes(original[name]);untouched=policy.charstring_bytes(original[other])
    report=tmp_path/'report.json'
    def adapt(f,source):
        top=f['CFF '].cff.topDictIndex[0]
        top.CharStrings[name]=copy.deepcopy(top.CharStrings[other])
        assert policy.charstring_bytes(top.CharStrings[name])!=before
        rows=[dict(gid=gid,glyph=n,status='adapted') for gid,n in enumerate(f.getGlyphOrder())]
        report.write_text(json.dumps(dict(records=rows,counts={'adapted':len(rows)},method='test-cubic-kernel')))
        return dict(report='report.json')
    monkeypatch.setattr(policy,'ROOT',tmp_path)
    result=policy.apply(font,'UFSZeroExt.otf',adapt)
    actual=font['CFF '].cff.topDictIndex[0].CharStrings
    assert policy.charstring_bytes(actual[name])==before
    assert policy.charstring_bytes(actual[other])==untouched
    metadata=result['sourcePolicy']
    assert metadata['codepoints']==[0x18f6c]
    assert metadata['glyphs']==[dict(gid=font.getGlyphID(name),glyph=name,charstringSha256=hashlib.sha256(before).hexdigest())]
    written=json.loads((tmp_path/result['report']).read_text())
    protected=[row for row in written['records'] if row.get('sourcePolicy')]
    assert len(protected)==1 and protected[0]['status']=='native-retained-guard'
    assert sum(written['counts'].values())==len(font.getGlyphOrder())
