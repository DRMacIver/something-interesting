"""Duployan policy retains exact mapped/contextual native component closure."""
import copy,json,sys,hashlib
from pathlib import Path
import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/font'))
import duployan_source_preservation as policy
import font_baseline_checks as checks


def fixture_font():
    order=['.notdef','part','mapped','dupl.Dot.rel1','other']
    fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order)
    glyphs={}
    for name in order:
        p=TTGlyphPen(None);p.moveTo((0,0));p.lineTo((100,0));p.lineTo((100,100));p.closePath();glyphs[name]=p.glyph()
    p=TTGlyphPen(glyphs);p.addComponent('part',(1,0,0,1,10,0));glyphs['mapped']=p.glyph()
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics({name:(200,0) for name in order});fb.setupHorizontalHeader(ascent=800,descent=-200);fb.setupCharacterMap({0x1bc63:'mapped',65:'other'});fb.setupNameTable({'familyName':'Policy Fixture','styleName':'Regular','psName':'PolicyFixture'});fb.setupOS2();fb.setupPost();return fb.font


def test_policy_restores_native_component_closure_and_contextual_dot(tmp_path,monkeypatch):
    monkeypatch.setattr(policy,'ROOT',tmp_path);font=fixture_font();native=copy.deepcopy(font)
    records=[dict(gid=i,glyph=n,status='adapted') for i,n in enumerate(font.getGlyphOrder())]
    report=tmp_path/'kernel.json';report.write_text(json.dumps({'records':records,'counts':{'adapted':5}}))
    def adapt(font,source):
        for name in font.getGlyphOrder():
            p=TTGlyphPen(None);p.moveTo((0,0));p.lineTo((10,0));p.lineTo((10,10));p.closePath();font['glyf'][name]=p.glyph()
        return {'report':'kernel.json'}
    result=policy.apply(font,policy.SOURCE,adapt);metadata=result['sourcePolicy']
    assert {r['glyph'] for r in metadata['glyphs']}=={'mapped','part','dupl.Dot.rel1'}
    for name in ['mapped','part','dupl.Dot.rel1']:
        assert font['glyf'][name].compile(font['glyf'])==native['glyf'][name].compile(native['glyf'])
    assert font['glyf']['other'].compile(font['glyf'])!=native['glyf']['other'].compile(native['glyf'])
    assert checks.source_policy_closure(native,metadata,native.getGlyphOrder())=={1,2,3}
    forged=copy.deepcopy(metadata);forged['namedGlyphs']=['other']
    with pytest.raises(AssertionError):checks.source_policy_closure(native,forged,native.getGlyphOrder())
    forged=copy.deepcopy(metadata);forged['glyphs']=forged['glyphs'][:-1]
    with pytest.raises(AssertionError):checks.source_policy_closure(native,forged,native.getGlyphOrder())
    assert result['counts']=={'adapted':2,'native-retained-guard':3}
    assert Path(result['report']).name=='kernel-duployan-preserve-'+policy.policy_hash()+'.json'


def test_policy_requires_original_contextual_glyph_names():
    font=fixture_font();font.setGlyphOrder(['.notdef','part','mapped','wrong','other'])
    with pytest.raises(ValueError,match='pristine native glyph names'):
        policy.apply(font,policy.SOURCE,lambda *_:None)


def test_strict_policy_helper_rejects_mutated_native_contextual_dot(tmp_path,monkeypatch):
    import supplemental_adapter as pressure
    from fontTools.ttLib import TTFont
    monkeypatch.setattr(policy,'ROOT',tmp_path);monkeypatch.setattr(checks,'ROOT',tmp_path)
    font=fixture_font();frozen=tmp_path/'output/font-review/supplemental-production-baselines/fixture.ttf';frozen.parent.mkdir(parents=True);font.save(frozen)
    before=dict(source='native/'+policy.SOURCE,file='assets/fonts/scripts/fixture.ttf',sha256=hashlib.sha256(frozen.read_bytes()).hexdigest(),bytes=frozen.stat().st_size,recipe=1,style='native fixture',family='Fixture')
    raw=tmp_path/before['source'];raw.parent.mkdir(parents=True);font.save(raw)
    before['sourceSha256']=hashlib.sha256(raw.read_bytes()).hexdigest()
    recipe=pressure.recipe_hash(policy.SOURCE)
    report_path=Path('output/font-review/supplemental-production')/('0'*64+'-'+recipe+'.json');(tmp_path/report_path).parent.mkdir(parents=True)
    def adapt(font,source):
        report=dict(method=pressure.RECIPES['method'],recipeSha256=recipe,settings=pressure.SOURCES[policy.SOURCE],resolution=pressure.RECIPES['resolution'],glyphs=5,counts={'adapted':5},nativeEmUnchanged=1000,nativeBoundsPreserved=True,records=[dict(gid=i,glyph=n,status='adapted',vectorChecks=True,changedPixels=1) for i,n in enumerate(font.getGlyphOrder())])
        (tmp_path/report_path).write_text(json.dumps(report));return {k:v for k,v in report.items() if k!='records'}|{'report':str(report_path)}
    treatment=policy.apply(font,policy.SOURCE,adapt)
    output=tmp_path/before['file'];output.parent.mkdir(parents=True);font.save(output)
    after=dict(before,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),bytes=output.stat().st_size,recipe='1:supplemental-pressure:'+recipe+':duployan-source-preservation:'+policy.policy_hash(),supplementalTreatment=treatment,style='smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional')
    assert checks.reviewed_supplemental_change(before,after)
    mutated=TTFont(output);glyph=mutated['glyf']['dupl.Dot.rel1'];glyph.coordinates[0]=(1,1);mutated.save(output)
    after.update(sha256=hashlib.sha256(output.read_bytes()).hexdigest(),bytes=output.stat().st_size)
    with pytest.raises(AssertionError):checks.reviewed_supplemental_change(before,after)
