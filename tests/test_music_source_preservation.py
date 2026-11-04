"""Named low-four tremolo policy is bound to pinned native construction."""
import copy,hashlib,json,shutil
from pathlib import Path
import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
import music_source_preservation as policy
import font_baseline_checks as checks
import supplemental_adapter as pressure
from music_tremolos import add_marks

REPO=Path(__file__).resolve().parent
while not (REPO/'tools/font/music_tremolos.py').exists():REPO=REPO.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def seed_code(root):
    for name in ('music_tremolos.py','music_mark_rules.py'):
        target=root/'tools/font'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/'tools/font'/name,target)


def test_policy_restores_complete_named_component_closure(tmp_path,monkeypatch):
    monkeypatch.setattr(policy,'ROOT',tmp_path);monkeypatch.setattr(checks,'ROOT',tmp_path);seed_code(tmp_path)
    order=['.notdef','part','u1D25B_low','unrelated'];fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order)
    glyphs={}
    for name in order:
        pen=TTGlyphPen(None);pen.moveTo((0,0));pen.lineTo((100,0));pen.lineTo((100,100));pen.closePath();glyphs[name]=pen.glyph()
    pen=TTGlyphPen(glyphs);pen.addComponent('part',(1,0,0,1,10,0));glyphs['u1D25B_low']=pen.glyph()
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics({name:(200,0) for name in order});fb.setupHorizontalHeader(ascent=800,descent=-200);fb.setupCharacterMap({65:'unrelated'});fb.setupNameTable(dict(familyName='Music closure',styleName='Regular'));fb.setupOS2();fb.setupPost();font=fb.font
    source=tmp_path/'native'/policy.SOURCE;source.parent.mkdir(parents=True);font.save(source);native=copy.deepcopy(font)
    report=tmp_path/'kernel.json';report.write_text(json.dumps(dict(records=[dict(gid=i,glyph=n,status='adapted') for i,n in enumerate(order)],counts={'adapted':4})))
    def adapt(font,source):
        for name in order:
            p=TTGlyphPen(None);p.moveTo((0,0));p.lineTo((10,0));p.lineTo((10,10));p.closePath();font['glyf'][name]=p.glyph()
        return {'report':'kernel.json'}
    result=policy.apply(font,source,adapt);metadata=result['sourcePolicy']
    assert metadata['codepoints']==[] and metadata['namedGlyphs']==['u1D25B_low']
    assert checks.source_policy_closure(native,metadata,native.getGlyphOrder())=={1,2}
    for name in ('part','u1D25B_low'):assert font['glyf'][name].compile(font['glyf'])==native['glyf'][name].compile(native['glyf'])
    assert font['glyf']['unrelated'].compile(font['glyf'])!=native['glyf']['unrelated'].compile(native['glyf'])
    assert result['counts']=={'adapted':2,'native-retained-guard':2}


@pytest.fixture
def native_case(tmp_path,monkeypatch):
    monkeypatch.setattr(policy,'ROOT',tmp_path);monkeypatch.setattr(checks,'ROOT',tmp_path);seed_code(tmp_path)
    source=tmp_path/'native'/policy.SOURCE;source.parent.mkdir(parents=True);shutil.copyfile(REPO/'build/unicode-sources/noto/NotoMusic-Regular.ttf',source)
    font=TTFont(source,recalcTimestamp=False);add_marks(font)
    frozen=tmp_path/'output/font-review/supplemental-production-baselines/music.ttf';frozen.parent.mkdir(parents=True);font.save(frozen)
    token=':music-tremolos:'+sha(tmp_path/'tools/font/music_tremolos.py')+':'+sha(tmp_path/'tools/font/music_mark_rules.py')
    before=dict(source=source.relative_to(tmp_path).as_posix(),sourceSha256=sha(source),file='assets/fonts/scripts/music.ttf',sha256=sha(frozen),bytes=frozen.stat().st_size,recipe='1'+token,style='native constructed fixture',family='Music Fixture')
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
    after=dict(before,sha256=sha(output),bytes=output.stat().st_size,recipe=before['recipe']+':supplemental-pressure:'+recipe+':music-source-preservation:'+policy.policy_hash(),supplementalTreatment=treatment,style='smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional')
    return tmp_path,before,after


def test_strict_helper_authenticates_raw_constructor_named_body_and_metrics(native_case):
    root,before,after=native_case
    assert checks.reviewed_supplemental_change(before,after)


@pytest.mark.parametrize('mutation',['body','metric','constructor_hash','rules_hash','raw_pin','target_name','policy_flag','policy_hash','closure','constructor_recipe'])
def test_strict_helper_rejects_unreviewed_music_policy_changes(native_case,mutation):
    root,before,after=copy.deepcopy(native_case);path=root/after['file'];report_path=root/after['supplementalTreatment']['report'];report=json.loads(report_path.read_text());metadata=report['sourcePolicy']
    if mutation in {'body','metric'}:
        font=TTFont(path);name='u1D25B_low'
        if mutation=='body':x,y=font['glyf'][name].coordinates[0];font['glyf'][name].coordinates[0]=(x+1,y)
        else:advance,lsb=font['hmtx'][name];font['hmtx'][name]=(advance+1,lsb)
        font.save(path);after.update(sha256=sha(path),bytes=path.stat().st_size)
    elif mutation=='constructor_hash':metadata['sourceConstruction']['sha256']='0'*64
    elif mutation=='rules_hash':metadata['sourceConstruction']['rulesSha256']='0'*64
    elif mutation=='raw_pin':(root/before['source']).write_bytes((root/before['source']).read_bytes()+b'unpinned change')
    elif mutation=='target_name':metadata['namedGlyphs']=['u1D25B']
    elif mutation=='policy_flag':
        gid=metadata['glyphs'][0]['gid'];report['records'][gid]['sourcePolicy']=False
    elif mutation=='policy_hash':metadata['sha256']='0'*64
    elif mutation=='closure':metadata['glyphs']=[]
    else:
        after['recipe']=after['recipe'].replace(':music-tremolos:',':unreviewed-music-constructor:')
    report_path.write_text(json.dumps(report));after['supplementalTreatment']={k:v for k,v in report.items() if k!='records'}|{'report':str(report_path.relative_to(root))}
    with pytest.raises(AssertionError):checks.reviewed_supplemental_change(before,after)
