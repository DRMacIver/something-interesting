"""Explicit positional classes beat the donor drawing's unplaced origin."""
import hashlib
import json

from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from font_baseline_checks import catalog_batch, pinned_packaging_font, reviewed_later_change, assert_drawing_equal_or_optical, assert_added_native_variant_families
from test_font_scripts import ROOT
from math_mark_checks import positioned_ink

BASELINE=ROOT/'output/font-review/pre-positional-mark-repair'


def manifest(path):
    return json.loads(path.read_text().split('export default ',1)[1].rstrip(';\n'))


def test_all_cjk_companions_respect_above_corners_and_attached_classes():
    entries=manifest(ROOT/'js/marked-cjk-variant-manifest.js')['fonts']
    assert len(entries)==92
    for entry in entries:
        selector,ranges=next(iter(entry['nativeVariations'].items()))
        sequence=chr(ranges[0][0])+chr(int(selector))
        path=ROOT/entry['file'];font=TTFont(path)
        for cp,align,attached,above in [(0x1df7,'left',False,True),(0x31b,'right',True,True),(0x315,'right',False,True),(0x1dce,'center',True,True),(0x301,'center',False,True),(0x327,'center',True,False)]:
            rows=positioned_ink(font,path,sequence+chr(cp))
            assert len(rows)==2 and rows[1][2]==0,(entry['family'],cp,rows)
            base,mark=rows[0][1],rows[1][1]
            clearance=mark[1]-base[3] if above else base[1]-mark[3]
            # Integer OpenType anchors can round each of two curve extrema.
            assert clearance>=-1.01,(entry['family'],cp,rows)
            if attached:assert abs(clearance)<=1.01,(entry['family'],cp,rows)
            else:assert clearance>0,(entry['family'],cp,rows)
            if align!='center':
                target=base[0] if align=='left' else base[2]
                assert abs((mark[0]+mark[2])/2-target)<=1,(entry['family'],cp,rows)


def test_only_the_intended_math_script_font_changes_and_its_drawings_stay_exact():
    old=manifest(BASELINE/'font-manifest.js')['fonts']
    current={e['family']:e for e in manifest(ROOT/'js/font-manifest.js')['fonts']}
    assert len(old)==len(current)==381
    changed=[]
    for entry in old:
        now=current[entry['family']]
        if entry==now:
            assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()==entry['sha256']
            continue
        # Compose the historical GPOS-only repair before authenticating the
        # later native-pressure finish; neither step may waive source ink.
        if not entry['source'].endswith('/NotoSansMath-Regular.ttf') and reviewed_later_change(entry,now):continue
        changed.append(entry['family'])
        assert entry['source'].endswith('/NotoSansMath-Regular.ttf')
        frozen=BASELINE/entry['file'].split('/')[-1]
        assert hashlib.sha256(frozen.read_bytes()).hexdigest()==entry['sha256']
        assert hashlib.sha256((ROOT/now['file']).read_bytes()).hexdigest()==now['sha256']
        before=TTFont(frozen);after=pinned_packaging_font(now)
        assert before.keys()==after.keys()
        for tag in before.keys():
            if tag not in {'GlyphOrder','GPOS','GDEF','head'}:
                assert before.getTableData(tag)==after.getTableData(tag),tag
        assert before.getGlyphOrder()==after.getGlyphOrder()
        assert before.getBestCmap()==after.getBestCmap()
        assert before['hmtx'].metrics==after['hmtx'].metrics
        if 'vmtx' in before:assert before['vmtx'].metrics==after['vmtx'].metrics
        bg,ag=before.getGlyphSet(),after.getGlyphSet()
        for name in before.getGlyphOrder():
            a,b=DecomposingRecordingPen(bg),DecomposingRecordingPen(ag)
            bg[name].draw(a);ag[name].draw(b)
            assert a.value==b.value,name
            if 'glyf' in before:
                for field in ['xMin','yMin','xMax','yMax']:
                    assert getattr(before['glyf'][name],field,None)==getattr(after['glyf'][name],field,None)
                if hasattr(before['glyf'][name],'program'):
                    assert before['glyf'][name].program.getBytecode()==after['glyf'][name].program.getBytecode()
        for tag in ['fpgm','prep','cvt ']:
            if tag in before:assert before.getTableData(tag)==after.getTableData(tag)
    assert changed==['Dad Script 6b5f778a9ecc']


@catalog_batch
def test_attachment_repair_does_not_change_any_catalog_mark_drawing():
    before=manifest(BASELINE/'combining-outline-manifest.js')
    after=manifest(ROOT/'js/combining-outline-manifest.js')
    assert before['marks'].keys()==after['marks'].keys()
    for cp,old in before['marks'].items():
        new=after['marks'][cp]
        fields = ['path','bounds','ccc','category','glyph']
        assert_drawing_equal_or_optical({k:old[k] for k in fields},{k:new[k] for k in fields},before['sources'][old['source']]['file'],int(cp))
    assert_added_native_variant_families(before,after)
    count=0
    for family,old in before['variationMarks'].items():
        new=after['variationMarks'][family]
        assert old['marks'].keys()==new['marks'].keys(),family
        for cp,row in old['marks'].items():
            other=new['marks'][cp]
            assert row['glyph']==other['glyph'],(family,cp)
            source_file = before['sources'][old['source']]['file']
            a = dict(before['variantDrawings'][row['drawing']],glyph=row['glyph'])
            b = dict(after['variantDrawings'][other['drawing']],glyph=other['glyph'])
            assert_drawing_equal_or_optical(a,b,source_file,int(cp))
            count+=1
    assert count==25087
