"""Range warming must reproduce complete native kernel caches without publishing."""
import hashlib
import io
import json
from pathlib import Path
import sys
import threading
import time

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import supplemental_adapter as adapter
from warm_supplemental_range import AtomicCachePath,enumeration_proof,isolated_apply,range_apply,SIGNWRITING
from test_dense_skeleton import fixture_font


def composite_fixture():
    font=TTFont(io.BytesIO(fixture_font()))
    pen=TTGlyphPen(font.getGlyphSet());pen.addComponent('H',(1,0,0,1,0,0))
    font['glyf']['C']=pen.glyph();font['hmtx']['C']=font['hmtx']['H']
    font.setGlyphOrder(list(font['glyf'].glyphs))
    for table in font['cmap'].tables:
        if table.isUnicode():table.cmap[67]='C'
    data=io.BytesIO();font.save(data);return data.getvalue()


def public_fingerprints():
    path=ROOT/'js/font-manifest.js';manifest=json.loads(path.read_text().split('export default ',1)[1].rstrip(';\n'))
    return {str(path):hashlib.sha256(path.read_bytes()).hexdigest(),**{e['file']:hashlib.sha256((ROOT/e['file']).read_bytes()).hexdigest() for e in manifest['fonts']}}


def test_two_ranges_have_identical_full_kernel_cache_records_and_drawings(tmp_path):
    before=public_fingerprints();kernel=adapter.apply.__code__;recipe=adapter.recipe_hash(SIGNWRITING)
    raw=composite_fixture();native=TTFont(io.BytesIO(raw));assert native['glyf']['C'].isComposite()
    count=len(native.getGlyphOrder());assert count==3
    complete=isolated_apply(tmp_path/'full-reports',tmp_path/'full-cache')
    assert complete.__code__ is kernel
    full=complete(TTFont(io.BytesIO(raw)),SIGNWRITING)
    full_detail=json.loads((tmp_path/'full-reports'/full['report']).read_text())
    partials=[]
    for start,stop in [(0,1),(1,3)]:
        report_root=tmp_path/f'range-{start}-{stop}'
        partial=range_apply(report_root,tmp_path/'split-cache',start,stop,expected_glyphs=count)
        assert partial.code_object is kernel
        font=TTFont(io.BytesIO(raw));result=partial(font,SIGNWRITING)
        # The compound outside range0 still traverses the unchanged full freeze.
        assert not font['glyf']['C'].isComposite()
        detail=json.loads(Path(result['report']).read_text());partials+=detail['records']
        assert detail['partialWarm']['completeSourceCoverage'] is False
        assert detail['partialWarm']['nativeGlyphs']==count
        assert detail['partialWarm']['selectedGlyphs']==stop-start
        assert [r['gid'] for r in detail['records']]==list(range(start,stop))
    assert partials==full_detail['records']
    full_files={p.name:p.read_bytes() for p in (tmp_path/'full-cache').iterdir()}
    split_files={p.name:p.read_bytes() for p in (tmp_path/'split-cache').iterdir()}
    assert full_files==split_files
    assert adapter.apply.__code__ is kernel
    assert adapter.recipe_hash(SIGNWRITING)==recipe
    assert enumeration_proof()['enumerateCalls']==1
    assert public_fingerprints()==before


def test_auxiliary_cache_reader_waits_for_legacy_json_publication(tmp_path):
    path=tmp_path/'record.json';path.write_text('{')
    def finish():
        time.sleep(.03);path.write_text('{"status":"native-blank"}')
    thread=threading.Thread(target=finish);thread.start()
    assert json.loads(AtomicCachePath(path).read_text())=={'status':'native-blank'}
    thread.join()
    AtomicCachePath(path).write_text('{"status":"adapted"}')
    assert json.loads(path.read_text())=={'status':'adapted'}
    assert list(tmp_path.glob('.range-cache-*'))==[]
