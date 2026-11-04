"""Historical exemptions reject unreviewed sources and stale cubic evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest
from fontTools import subset
from fontTools.ttLib import TTFont

import font_baseline_checks as checks
import supplemental_adapter
import supplemental_cubic_adapter as cubic

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def cubic_fixture(tmp_path_factory):
    root=tmp_path_factory.mktemp('cubic-baseline')
    font=TTFont(ROOT/'assets/fonts/dad-math-variants.woff2',recalcTimestamp=False)
    options=subset.Options();options.layout_features=['*']
    sub=subset.Subsetter(options=options);sub.populate(text='ℋℋ\ufe01ℐℐ\ufe01');sub.subset(font)
    path=root/'assets/fonts/scripts/fixture.woff2';path.parent.mkdir(parents=True)
    font.save(path)
    frozen=root/'output/font-review/supplemental-production-baselines'/path.name
    frozen.parent.mkdir(parents=True);shutil.copyfile(path,frozen)
    before=dict(family='Dad Cubic Fixture',file=str(path.relative_to(root)),source='native/UFSZeroExt.otf',sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,recipe=1,ranges=[[8459,8459]],style='bounded native cubic fixture')
    with pytest.MonkeyPatch.context() as m:
        m.setattr(cubic,'ROOT',root);m.setattr(cubic,'CACHE',root/'build/font-cache/cubic-pressure')
        m.setattr(supplemental_adapter,'baseline',lambda source:None)
        result=cubic.apply(font,before['source'])
    font.flavor='woff2';font.save(path)
    after=dict(before,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,recipe='1:supplemental-cubic-pressure:'+cubic.recipe_hash(before['source']),supplementalTreatment=result)
    return root,before,after


def test_reviewed_cubic_baseline_requires_native_cff_and_content_addressed_report(cubic_fixture,monkeypatch):
    root,before,after=cubic_fixture;monkeypatch.setattr(checks,'ROOT',root)
    assert checks.reviewed_later_change(before,after)


def test_cubic_baseline_does_not_exempt_unreviewed_source(cubic_fixture,monkeypatch):
    root,before,after=cubic_fixture;monkeypatch.setattr(checks,'ROOT',root)
    with pytest.raises(AssertionError):
        checks.reviewed_later_change(dict(before,source='native/Unreviewed.otf'),dict(after,source='native/Unreviewed.otf'))


def test_cubic_baseline_rejects_stale_recipe_and_displaced_report(cubic_fixture,monkeypatch):
    root,before,after=cubic_fixture;monkeypatch.setattr(checks,'ROOT',root)
    stale=copy.deepcopy(after);stale['supplementalTreatment']['recipeSha256']='0'*64
    with pytest.raises(AssertionError):checks.reviewed_later_change(before,stale)
    displaced=copy.deepcopy(after);displaced['supplementalTreatment']['report']='output/font-review/unkeyed.json'
    with pytest.raises(AssertionError):checks.reviewed_later_change(before,displaced)


def test_source_policy_exempts_exact_native_component_closure_only():
    from source_preservation import policy_hash
    font=TTFont(ROOT/'build/unicode-sources/unicodia/ArchaicCuneiformNumerals.ttf')
    names=set()
    def visit(name):
        if name in names:return
        names.add(name)
        for child in font['glyf'][name].getComponentNames(font['glyf']):visit(child)
    visit(font.getBestCmap()[0x1262d])
    policy=dict(module='tools/font/source_preservation.py',sha256=policy_hash(),codepoints=[0x1262d],glyphs=[dict(gid=font.getGlyphID(name),glyph=name) for name in sorted(names,key=font.getGlyphID)])
    assert checks.source_policy_closure(font,policy) == {font.getGlyphID(name) for name in names}
    missing=copy.deepcopy(policy);missing['glyphs']=missing['glyphs'][:-1]
    with pytest.raises(AssertionError):checks.source_policy_closure(font,missing)
    unrelated=copy.deepcopy(policy);unrelated['codepoints']=[0x1262e]
    with pytest.raises(AssertionError):checks.source_policy_closure(font,unrelated)


def test_native_evidence_cache_invalidates_on_same_path_rebuild(tmp_path):
    import os
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    builder=FontBuilder(1000,isTTF=True)
    builder.setupGlyphOrder(['.notdef','A']);builder.setupCharacterMap({65:'A'})
    empty=TTGlyphPen(None);pen=TTGlyphPen(None)
    pen.moveTo((0,0));pen.lineTo((400,0));pen.lineTo((400,700));pen.lineTo((0,700));pen.closePath()
    builder.setupGlyf({'.notdef':empty.glyph(),'A':pen.glyph()})
    builder.setupHorizontalMetrics({'.notdef':(500,0),'A':(500,0)})
    builder.setupHorizontalHeader(ascent=800,descent=-200)
    builder.setupNameTable(dict(familyName='CacheFixture',styleName='Regular'))
    builder.setupOS2(sTypoAscender=800,sTypoDescender=-200,usWinAscent=800,usWinDescent=200)
    builder.setupPost();builder.setupMaxp()
    path=tmp_path/'native.ttf';builder.save(path)
    old=checks.evidence_drawing(path,'A');stat=path.stat()
    font=TTFont(path)
    glyph=font['glyf']['A']
    for i,(x,y) in enumerate(glyph.coordinates):glyph.coordinates[i]=(x+10 if x>0 else x,y)
    font.save(path)
    os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns+1_000_000))
    current=checks.evidence_drawing(path,'A')
    assert old['path'] != current['path']
    assert current['bounds'][2] == pytest.approx(old['bounds'][2]+.01)


def test_cubic_lineage_rejects_same_geometry_unapproved_charstring(cubic_fixture,monkeypatch):
    root,before,after=cubic_fixture;monkeypatch.setattr(checks,'ROOT',root)
    report=json.loads((root/after['supplementalTreatment']['report']).read_text())
    row=next(row for row in report['records'] if row['status']=='adapted')
    path=root/after['file'];original_bytes=path.read_bytes()
    try:
        font=TTFont(path,recalcTimestamp=False)
        cs=font['CFF '].cff.topDictIndex[0].CharStrings[row['glyph']]
        old_bounds=cubic.bounds(font,row['glyph'])
        cs.decompile()
        # Empty move changes neither bounds nor drawn segments. A permissive
        # same-frame check would accept this unrelated Type2 program.
        cs.program[-1:-1]=[0,0,'rmoveto']
        font.save(path)
        assert cubic.bounds(TTFont(path),row['glyph'])==old_bounds
        changed=copy.deepcopy(after);changed['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();changed['bytes']=path.stat().st_size
        with pytest.raises(AssertionError):checks.reviewed_later_change(before,changed)
    finally:path.write_bytes(original_bytes)


def test_source_style_review_rejects_altered_decision_hash():
    from style_review import review_for_source
    rows=json.loads((ROOT/'docs/unicode-style-dispositions.json').read_text())['sources']
    source=rows[0]['source'];before={'source':source};after=dict(before,styleReview=review_for_source(source))
    assert checks.authenticated_review_metadata(before,after)==(before,before)
    forged=copy.deepcopy(after);forged['styleReview']['decisionSha256']='0'*64
    with pytest.raises(AssertionError):checks.authenticated_review_metadata(before,forged)
    forged=copy.deepcopy(after);forged['styleReview']['disposition']='unreviewed forged decision'
    with pytest.raises(AssertionError):checks.authenticated_review_metadata(before,forged)


def test_style_review_accepts_only_exact_pending_style_transition():
    from style_review import review_for_source
    source=json.loads((ROOT/'docs/unicode-style-dispositions.json').read_text())['sources'][0]['source']
    review=review_for_source(source)
    before={'source':source,'style':'native; custom visual review pending'}
    expected='sampled source style disposition: '+review['disposition']+'; native identities and guarded exceptions retained'
    after=dict(before,style=expected,styleReview=review)
    assert checks.authenticated_review_metadata(before,after)==(before,before)
    wrong=dict(after,style=expected+' changed')
    assert checks.authenticated_review_metadata(before,wrong)[1]['style']!=before['style']
    already_reviewed=dict(before,style='recorded native calligraphy')
    assert checks.authenticated_review_metadata(already_reviewed,after)[1]['style']!=already_reviewed['style']


def test_cubic_native_sfnt_allows_only_exact_packaged_or_prewoff2_bit11(cubic_fixture):
    import io
    root,before,_=cubic_fixture
    native=TTFont(root/'output/font-review/supplemental-production-baselines'/Path(before['file']).name,recalcTimestamp=False)
    original_flags=native['head'].flags
    assert original_flags & 0x800
    def digest(flags):
        font=copy.deepcopy(native);font.flavor=None;font.recalcTimestamp=False;font['head'].flags=flags
        output=io.BytesIO();font.save(output);return hashlib.sha256(output.getvalue()).hexdigest()
    assert checks.authenticate_cubic_native_sfnt_hash(native,digest(original_flags))==original_flags
    assert checks.authenticate_cubic_native_sfnt_hash(native,digest(original_flags & ~0x800))==original_flags & ~0x800
    assert native['head'].flags==original_flags
    # A different head bit cannot be excused as WOFF2 serialization state.
    with pytest.raises(AssertionError):checks.authenticate_cubic_native_sfnt_hash(native,digest(original_flags ^ 0x20))
    with pytest.raises(AssertionError):checks.authenticate_cubic_native_sfnt_hash(native,'0'*64)
