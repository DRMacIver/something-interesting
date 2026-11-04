"""Private warm markers must authenticate real native mapping and payloads."""
import copy,hashlib,io,json,sys
from pathlib import Path
import pytest
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import verify_dense_warm as verify
import dense_native_adapter as adapter
from test_dense_skeleton import fixture_font


def dump(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data))
def font_manifest(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text('export default '+json.dumps(data)+';\n')


@pytest.fixture
def warm(tmp_path,monkeypatch):
    monkeypatch.setattr(verify,'ROOT',tmp_path);monkeypatch.setattr(adapter,'ROOT',tmp_path)
    public=tmp_path/'js/font-manifest.js';monkeypatch.setattr(verify,'PUBLIC',public)
    original=tmp_path/'assets/fonts/scripts/test.woff2';original.parent.mkdir(parents=True)
    native=TTFont(io.BytesIO(fixture_font()),recalcTimestamp=False);native.flavor='woff2';native.save(original)
    family='Dad Script test';source='build/unicode-sources/jigmo/extracted/Jigmo.ttf'
    base={'family':family,'file':original.relative_to(tmp_path).as_posix(),'source':source,'sha256':verify.sha(original),'bytes':original.stat().st_size,'recipe':1}
    font_manifest(public,{'fonts':[base]})
    work=tmp_path/'warm/group-0';target=work/'fonts/test.woff2';target.parent.mkdir(parents=True)
    cache=tmp_path/'build/font-cache/dense-native'
    derived=TTFont(original,recalcTimestamp=False)
    treatment=adapter.apply(derived,tmp_path/source,cache_dir=cache,report_dir=work/'reports')
    derived.flavor='woff2';derived.save(target)
    row={'family':family,'source':source,'sourceName':'Jigmo.ttf','file':base['file'],'sha256':base['sha256'],'glyphs':2,'cmapKey':verify.cmap_key(native.getBestCmap()),'originalRecipe':1}
    group={'index':0,'glyphs':2,'shards':[row]};kernel=adapter.recipe_hash()
    plan={'publicManifestSha256':verify.sha(public),'publicAssets':{base['file']:base['sha256']},'denseRecipeSha256':kernel,'denseShards':[row],'groups':[group],'sharedGlyphCache':cache.relative_to(tmp_path).as_posix()}
    dump(tmp_path/'warm/plan.json',plan)
    entry=base|{'file':target.relative_to(tmp_path).as_posix(),'sha256':verify.sha(target),'bytes':target.stat().st_size,'recipe':verify.synthetic_recipe(1,kernel),'denseTreatment':treatment}
    private=work/'manifest.js';font_manifest(private,{'fonts':[entry]})
    complete={'status':'private dense cache warm complete; public assets unchanged','index':0,'denseRecipeSha256':kernel,'families':[family],'counts':{family:treatment['counts']},'privateManifestSha256':verify.sha(private)}
    dump(work/'complete.json',complete)
    return tmp_path/'warm',work,group,kernel,complete


def test_authenticates_actual_font_report_cache_and_unique_native_union(warm):
    result=verify.verify_plan(warm[0])
    assert result['verifiedFamilies']==1 and result['expectedDenseFamilies']==1
    assert result['verifiedGlyphs']==2
    assert sum(result['counts'].values())==2


@pytest.mark.parametrize('field,value',[
    ('index',2),('denseRecipeSha256','0'*64),('families',['alien']),('counts',{}),('privateManifestSha256','0'*64),
])
def test_rejects_false_completion_markers(warm,field,value):
    root,work,group,kernel,complete=warm;bad=copy.deepcopy(complete);bad[field]=value
    with pytest.raises(ValueError):verify.authenticate_complete(bad,group,kernel,work/'manifest.js')


def test_rejects_changed_native_metrics_even_with_updated_self_hashes(warm):
    root,work,group,kernel,complete=warm
    private=verify.manifest(work/'manifest.js');entry=private['fonts'][0]
    target=verify.ROOT/entry['file'];font=TTFont(target,recalcTimestamp=False)
    name=font.getBestCmap()[72];advance,lsb=font['hmtx'][name];font['hmtx'][name]=(advance+1,lsb);font.save(target)
    entry['sha256']=verify.sha(target);entry['bytes']=target.stat().st_size
    font_manifest(work/'manifest.js',private);complete['privateManifestSha256']=verify.sha(work/'manifest.js');dump(work/'complete.json',complete)
    with pytest.raises(ValueError,match='Native hmtx bytes differ'):verify.verify_plan(root)


def test_rejects_truncated_glyph_report_coverage(warm):
    root,work,group,kernel,complete=warm
    entry=verify.manifest(work/'manifest.js')['fonts'][0];path=verify.ROOT/entry['denseTreatment']['report']
    report=verify.read(path);report['records'].pop();dump(path,report)
    with pytest.raises(ValueError,match='every actual native glyph'):verify.verify_plan(root)
