"""Equal harpoon retention is bound to pinned hand-ink construction."""
import copy,hashlib,json,shutil
from pathlib import Path
import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
import chemical_source_preservation as policy
import font_baseline_checks as checks
import supplemental_adapter as pressure
from chemical_symbols import repair_isolobal
from alphabet_ink import adapt as alphabet_ink
from fontTools import subset

REPO=Path(__file__).resolve().parent
while not (REPO/'tools/font/alphabet_ink.py').exists():REPO=REPO.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def seed_code(root):
    for name in ('alphabet_ink.py','chemical_symbols.py'):
        target=root/'tools/font'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/'tools/font'/name,target)
    target=root/'data/font-sources/unicodia.json';target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/'data/font-sources/unicodia.json',target)


def test_policy_restores_complete_named_component_closure(tmp_path,monkeypatch):
    monkeypatch.setattr(policy,'ROOT',tmp_path);monkeypatch.setattr(checks,'ROOT',tmp_path);seed_code(tmp_path)
    order=['.notdef','part','mapped','unrelated'];fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order)
    glyphs={}
    for name in order:
        pen=TTGlyphPen(None);pen.moveTo((0,0));pen.lineTo((100,0));pen.lineTo((100,100));pen.closePath();glyphs[name]=pen.glyph()
    pen=TTGlyphPen(glyphs);pen.addComponent('part',(1,0,0,1,10,0));glyphs['mapped']=pen.glyph()
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics({name:(200,0) for name in order});fb.setupHorizontalHeader(ascent=800,descent=-200);fb.setupCharacterMap({**{cp:'mapped' for cp in policy.CODEPOINTS},65:'unrelated'});fb.setupNameTable(dict(familyName='Chemical closure',styleName='Regular'));fb.setupOS2();fb.setupPost();font=fb.font
    source=tmp_path/'native'/policy.SOURCE;source.parent.mkdir(parents=True);shutil.copyfile(REPO/'build/unicode-sources/unicodia/UnicodiaFunky.ttf',source);native=copy.deepcopy(font)
    report=tmp_path/'kernel.json';report.write_text(json.dumps(dict(records=[dict(gid=i,glyph=n,status='adapted') for i,n in enumerate(order)],counts={'adapted':4})))
    def adapt(font,source):
        for name in order:
            p=TTGlyphPen(None);p.moveTo((0,0));p.lineTo((10,0));p.lineTo((10,10));p.closePath();font['glyf'][name]=p.glyph()
        return {'report':'kernel.json'}
    result=policy.apply(font,source,adapt);metadata=result['sourcePolicy']
    assert metadata['codepoints']==policy.CODEPOINTS and metadata['namedGlyphs']==[]
    assert checks.source_policy_closure(native,metadata,native.getGlyphOrder())=={1,2}
    for name in ('part','mapped'):assert font['glyf'][name].compile(font['glyf'])==native['glyf'][name].compile(native['glyf'])
    assert font['glyf']['unrelated'].compile(font['glyf'])!=native['glyf']['unrelated'].compile(native['glyf'])
    assert result['counts']=={'adapted':2,'native-retained-guard':2}


@pytest.fixture
def native_case(tmp_path,monkeypatch):
    monkeypatch.setattr(policy,'ROOT',tmp_path);monkeypatch.setattr(checks,'ROOT',tmp_path);seed_code(tmp_path)
    source=tmp_path/'native'/policy.SOURCE;source.parent.mkdir(parents=True);shutil.copyfile(REPO/'build/unicode-sources/unicodia/UnicodiaFunky.ttf',source)
    font=TTFont(source,recalcTimestamp=False)
    options=subset.Options();options.layout_features=['*'];sub=subset.Subsetter(options=options);sub.populate(unicodes=[*policy.CODEPOINTS,0x1f8d8]);sub.subset(font)
    repair_isolobal(font);construction=policy.construction(source);alphabet_ink(font,{cp for a,b in construction['scope'] for cp in range(a,b+1)})
    frozen=tmp_path/'output/font-review/supplemental-production-baselines/chemical.ttf';frozen.parent.mkdir(parents=True);font.save(frozen)
    token=':chemical-repair:'+sha(tmp_path/'tools/font/chemical_symbols.py')+':alphabet-ink:'+json.dumps(construction['scope'],separators=(',',':'))+':'+sha(tmp_path/'tools/font/alphabet_ink.py')
    before=dict(source=source.relative_to(tmp_path).as_posix(),sourceSha256=sha(source),file='assets/fonts/scripts/chemical.ttf',sha256=sha(frozen),bytes=frozen.stat().st_size,recipe='1'+token,style='native hand-inked fixture',family='Chemical Fixture')
    recipe=pressure.recipe_hash(policy.SOURCE);relative=Path('output/font-review/supplemental-production')/('0'*64+'-'+recipe+'.json');(tmp_path/relative).parent.mkdir(parents=True)
    def adapt(font,source):
        records=[dict(gid=i,glyph=name,status='adapted',vectorChecks=True,changedPixels=1) for i,name in enumerate(font.getGlyphOrder())]
        for name in font.getGlyphOrder():
            glyph=font['glyf'][name]
            if glyph.numberOfContours>0:
                for i,(x,y) in enumerate(glyph.coordinates):glyph.coordinates[i]=(x+1,y)
        report=dict(method=pressure.RECIPES['method'],recipeSha256=recipe,settings=pressure.SOURCES[policy.SOURCE],resolution=pressure.RECIPES['resolution'],glyphs=len(records),counts={'adapted':len(records)},nativeEmUnchanged=font['head'].unitsPerEm,nativeBoundsPreserved=True,records=records)
        (tmp_path/relative).write_text(json.dumps(report));return {k:v for k,v in report.items() if k!='records'}|{'report':str(relative)}
    treatment=policy.apply(font,source,adapt);output=tmp_path/before['file'];output.parent.mkdir(parents=True);font.save(output)
    after=dict(before,sha256=sha(output),bytes=output.stat().st_size,recipe=before['recipe']+':supplemental-pressure:'+recipe+':chemical-source-preservation:'+policy.policy_hash(),supplementalTreatment=treatment,style='smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional')
    return tmp_path,before,after


def test_strict_helper_authenticates_raw_constructor_named_body_and_metrics(native_case):
    root,before,after=native_case
    assert checks.reviewed_supplemental_change(before,after)


@pytest.mark.parametrize('mutation',['body','metric','geom_body','geom_metric','constructor_hash','repair_hash','raw_pin','target_codepoint','policy_flag','policy_hash','closure','constructor_recipe'])
def test_strict_helper_rejects_unreviewed_chemical_policy_changes(native_case,mutation):
    root,before,after=copy.deepcopy(native_case);path=root/after['file'];report_path=root/after['supplementalTreatment']['report'];report=json.loads(report_path.read_text());metadata=report['sourcePolicy']
    if mutation in {'body','metric','geom_body','geom_metric'}:
        font=TTFont(path);name=font.getBestCmap()[0x1cee0 if mutation.startswith('geom_') else 0x1f8d1]
        if mutation in {'body','geom_body'}:x,y=font['glyf'][name].coordinates[0];font['glyf'][name].coordinates[0]=(x+1,y)
        else:advance,lsb=font['hmtx'][name];font['hmtx'][name]=(advance+1,lsb)
        font.save(path);after.update(sha256=sha(path),bytes=path.stat().st_size)
    elif mutation=='constructor_hash':metadata['sourceConstruction']['sha256']='0'*64
    elif mutation=='repair_hash':metadata['sourceConstruction']['chemicalSha256']='0'*64
    elif mutation=='raw_pin':(root/before['source']).write_bytes((root/before['source']).read_bytes()+b'unpinned change')
    elif mutation=='target_codepoint':metadata['codepoints']=[0x1f8d2]
    elif mutation=='policy_flag':
        gid=metadata['glyphs'][0]['gid'];report['records'][gid]['sourcePolicy']=False
    elif mutation=='policy_hash':metadata['sha256']='0'*64
    elif mutation=='closure':metadata['glyphs']=[]
    else:
        assert ':alphabet-ink:' in after['recipe']
        after['recipe']=after['recipe'].replace(':alphabet-ink:',':unreviewed-ink-constructor:')
    report_path.write_text(json.dumps(report));after['supplementalTreatment']={k:v for k,v in report.items() if k!='records'}|{'report':str(report_path.relative_to(root))}
    with pytest.raises(AssertionError):checks.reviewed_supplemental_change(before,after)
