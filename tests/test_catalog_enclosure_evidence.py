"""Catalog derived rings/counters remain bound to exact frozen/current ink."""
import copy
import hashlib
import json

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

import font_baseline_checks as checks
from build_combining_outlines import native_drawing


def save_ring(path,inner_left,extra_hole=False):
    builder=FontBuilder(1000,isTTF=True);builder.setupGlyphOrder(['.notdef','ring'])
    builder.setupCharacterMap({0x20df:'ring',0x20e3:'ring',0x20e0:'ring'})
    empty=TTGlyphPen(None);pen=TTGlyphPen(None)
    # Opposite winding preserves an actual counter; current ink changes its size.
    pen.moveTo((0,0));pen.lineTo((1000,0));pen.lineTo((1000,1000));pen.lineTo((0,1000));pen.closePath()
    pen.moveTo((inner_left,200));pen.lineTo((inner_left,800));pen.lineTo((800,800));pen.lineTo((800,200));pen.closePath()
    if extra_hole:
        x=inner_left/10
        pen.moveTo((x,20));pen.lineTo((x,100));pen.lineTo((120,100));pen.lineTo((120,20));pen.closePath()
    builder.setupGlyf({'.notdef':empty.glyph(),'ring':pen.glyph()})
    builder.setupHorizontalMetrics({'.notdef':(1000,0),'ring':(1000,0)})
    builder.setupHorizontalHeader(ascent=1000,descent=-200)
    builder.setupNameTable(dict(familyName='RingEvidence',styleName='Regular'))
    builder.setupOS2(sTypoAscender=1000,sTypoDescender=-200,usWinAscent=1000,usWinDescent=200)
    builder.setupPost();builder.setupMaxp();path.parent.mkdir(parents=True,exist_ok=True);builder.save(path)


@pytest.fixture
def ring_rows(tmp_path,monkeypatch):
    monkeypatch.setattr(checks,'ROOT',tmp_path)
    relative='assets/fonts/scripts/ring.ttf';current=tmp_path/relative
    frozen=tmp_path/'output/font-review/supplemental-production-baselines/ring.ttf'
    save_ring(frozen,200);save_ring(current,220)
    manifest={'fonts':[dict(family='Enclosure fixture',file=relative,source='native/ring.ttf',sha256=hashlib.sha256(current.read_bytes()).hexdigest(),supplementalTreatment={'method':'fixture-native-pressure'})]}
    (tmp_path/'js').mkdir();(tmp_path/'js/font-manifest.js').write_text('export default '+json.dumps(manifest)+';\n')
    rows=[]
    for path in (frozen,current):
        font=checks.evidence_font(path);rows.append(dict(**native_drawing(font.getGlyphSet(),'ring',1/1000),**checks.enclosure_evidence(path,'ring',0x20df),glyph='ring',source=0,ccc=0,category='Me'))
    assert rows[0]['ring']!=rows[1]['ring']
    return rows[0],rows[1],relative


def test_source_derived_ring_change_is_verified(ring_rows):
    before,after,source=ring_rows
    checks.assert_drawing_equal_or_optical(before,after,source,0x20df)


@pytest.mark.parametrize('mutation',['outer_path','counter_path','counter_missing','outer_area','counter_area','counter_bounds','source','ccc','glyph','before_area','classification'])
def test_ring_mutations_are_not_a_historical_exemption(ring_rows,mutation):
    before,after,source=copy.deepcopy(ring_rows);codepoint=0x20df
    if mutation=='outer_path':after['ring']['outer']['path']+='M0 0L1 1Z'
    elif mutation=='counter_path':after['ring']['inner']['path']+='M0 0L1 1Z'
    elif mutation=='counter_missing':after['ring'].pop('inner')
    elif mutation=='outer_area':after['ring']['outer']['area']+=.01
    elif mutation=='counter_area':after['ring']['inner']['area']*=-1
    elif mutation=='counter_bounds':after['ring']['inner']['bounds'][0]+=.01
    elif mutation=='source':after['source']=1
    elif mutation=='ccc':after['ccc']=230
    elif mutation=='glyph':after['glyph']='other'
    elif mutation=='before_area':before['ring']['outer']['area']+=.01
    elif mutation=='classification':codepoint=0x1234
    with pytest.raises(AssertionError):checks.assert_drawing_equal_or_optical(before,after,source,codepoint)


def test_ring_derived_record_cannot_be_dropped(ring_rows):
    before,after,source=copy.deepcopy(ring_rows);after.pop('ring')
    with pytest.raises(AssertionError):checks.assert_drawing_equal_or_optical(before,after,source,0x20df)


@pytest.fixture(params=[0x20e0,0x20e3])
def content_rows(tmp_path,monkeypatch,request):
    monkeypatch.setattr(checks,'ROOT',tmp_path);cp=request.param
    relative='assets/fonts/scripts/holes.ttf';current=tmp_path/relative
    frozen=tmp_path/'output/font-review/supplemental-production-baselines/holes.ttf'
    save_ring(frozen,200,True);save_ring(current,220,True)
    manifest={'fonts':[dict(family='Enclosure fixture',file=relative,source='native/holes.ttf',sha256=hashlib.sha256(current.read_bytes()).hexdigest(),supplementalTreatment={'method':'fixture-native-pressure'})]}
    (tmp_path/'js').mkdir();(tmp_path/'js/font-manifest.js').write_text('export default '+json.dumps(manifest)+';\n')
    rows=[]
    for path in (frozen,current):
        font=checks.evidence_font(path);rows.append(dict(**native_drawing(font.getGlyphSet(),'ring',1/1000),**checks.enclosure_evidence(path,'ring',cp),glyph='ring',source=0,ccc=0,category='Me'))
    assert rows[0]['contentBounds']!=rows[1]['contentBounds']
    return rows[0],rows[1],relative,cp


def test_source_derived_counter_bounds_change_is_verified(content_rows):
    before,after,source,cp=content_rows
    checks.assert_drawing_equal_or_optical(before,after,source,cp)


@pytest.mark.parametrize('mutation',['move','drop','replace_classification','before'])
def test_derived_counter_bounds_remain_exact(content_rows,mutation):
    before,after,source,cp=copy.deepcopy(content_rows)
    if mutation=='move':after['contentBounds'][0]+=.001
    elif mutation=='drop':after.pop('contentBounds')
    elif mutation=='replace_classification':after['ring']={'outer':{},'inner':{}};after.pop('contentBounds')
    else:before['contentBounds'][0]+=.001
    with pytest.raises(AssertionError):checks.assert_drawing_equal_or_optical(before,after,source,cp)


@pytest.mark.parametrize('field',['source','licence','copyright','file','sha256'])
def test_ring_catalog_does_not_exempt_source_metadata(ring_rows,field):
    before_row,after_row,relative=ring_rows
    old_source=dict(file=relative,sha256='frozen source hash',source='native/ring.ttf',licence='fixture licence',copyright='fixture author')
    current=json.loads((checks.ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))['fonts'][0]
    before=dict(sources=[old_source],marks={str(0x20df):before_row},variationMarks={},variantDrawings=[])
    after=dict(sources=[dict(old_source,sha256=current['sha256'])],marks={str(0x20df):after_row},variationMarks={},variantDrawings=[])
    checks.assert_catalog_equal_or_optical(before,after)
    forged=copy.deepcopy(after);forged['sources'][0][field]='unreviewed mutation'
    with pytest.raises(AssertionError):checks.assert_catalog_equal_or_optical(before,forged)
