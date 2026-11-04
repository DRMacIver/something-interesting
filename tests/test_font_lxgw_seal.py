"""Only the two reference-reviewed Seal gaps use the new OFL donor."""
import hashlib
import json

from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from font_baseline_checks import reviewed_later_change
from test_font_scripts import ROOT,shape

POINTS={0x3e34f,0x3fa42}


def test_two_seal_drawings_keep_source_curves_metrics_and_notices():
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    entries=[e for e in manifest['fonts'] if e['source'].endswith('/LXGWSeal-Regular.ttf')]
    assert len(entries)==1
    entry=entries[0];font=TTFont(ROOT/entry['file']);source=TTFont(ROOT/entry['source'])
    assert set(font.getBestCmap())==POINTS
    assert font['name'].getDebugName(1)==entry['family']
    assert entry['family'].startswith('Dad Script ')
    for record in font['name'].names:
        if record.nameID in {1,3,4,6,16}:assert 'LXGW' not in record.toUnicode()
    assert font['name'].getDebugName(0)==source['name'].getDebugName(0)
    assert 'SIL Open Font License' in font['name'].getDebugName(13)
    assert (ROOT/'assets/fonts/licenses/LXGWSeal-OFL.txt').read_bytes()==(ROOT/'build/unicode-sources/lxgw-seal/OFL.txt').read_bytes()
    for cp in POINTS:
        a,b=shape(ROOT/entry['source'],chr(cp),True),shape(ROOT/entry['file'],chr(cp),True)
        assert len(a)==len(b)==1 and a[0][1:]==b[0][1:]
        assert b[0][1]>0
        gs,actual=source.getGlyphSet(),font.getGlyphSet()
        pa,pb=DecomposingRecordingPen(gs),DecomposingRecordingPen(actual)
        gs[source.getGlyphName(a[0][0])].draw(pa);actual[font.getGlyphName(b[0][0])].draw(pb)
        assert pa.value==pb.value and pa.value


def test_existing_script_fonts_remain_byte_identical_after_two_gap_addition():
    baseline=ROOT/'output/font-review/pre-lxgw-seal-integration/font-manifest.js'
    old=json.loads(baseline.read_text().split('export default ',1)[1].rstrip(';\n'))
    current=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    before={e['family']:e for e in old['fonts']};after={e['family']:e for e in current['fonts']}
    assert len(before)==379 and len(after)>=380
    for family,entry in before.items():
        # A later intentional positional-mark repair changes only this font's
        # attachment data. test_positional_marks verifies every curve/metric
        # and the exact unchanged inventory for all other current fonts.
        if entry['source'].endswith('/NotoSansMath-Regular.ttf'):continue
        if reviewed_later_change(entry,after[family]):continue
        assert after[family]==entry,family
        assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()==entry['sha256'],family


def test_seal_review_queue_counts_only_shipped_subsets():
    import sys
    sys.path.insert(0,str(ROOT/'tools/font'))
    from review_seal_editions import build_report
    report=build_report()
    assert report['missing']==0
    assert not {'3E34F','3FA42'}&{r['codepoint'] for r in report['candidates']}
    assert all(p.startswith('assets/fonts/scripts/') for p in report['sourceHashes'] if p.endswith('.woff2'))
