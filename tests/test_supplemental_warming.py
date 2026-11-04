"""Isolated warmers must keep complete builder flow and public assets intact."""
import hashlib
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import warm_supplemental as warm


def digest(data):return hashlib.sha256(data).hexdigest()


def test_warmer_routes_only_outputs_and_enabled_recipes(tmp_path,monkeypatch):
    public=tmp_path/'js/font-manifest.js';public.parent.mkdir()
    fonts=tmp_path/'assets/fonts/scripts';fonts.mkdir(parents=True)
    entries=[]
    for name in ('Old','New'):
        data=(name+' original').encode();file=fonts/(name+'.woff2');file.write_bytes(data)
        entry=dict(source='sources/'+name+'.ttf',file=file.relative_to(tmp_path).as_posix(),sha256=digest(data),family=name)
        if name=='Old':entry['supplementalTreatment']=dict(recipeSha256='hash-Old.ttf')
        entries.append(entry)
    public.write_text('export default '+json.dumps(dict(fonts=entries))+';\n');original=public.read_bytes()
    monkeypatch.setattr(warm,'ROOT',tmp_path);monkeypatch.setattr(warm,'PUBLIC_MANIFEST',public)
    monkeypatch.setattr(warm.adapter,'SOURCES',{'Old.ttf':{},'New.ttf':{}})
    monkeypatch.setattr(warm.adapter,'recipe_hash',lambda name:'hash-'+Path(name).name)
    monkeypatch.setattr(warm.adapter,'CACHE',tmp_path/'public-cache')
    monkeypatch.setattr(warm.builder,'OUT',fonts);monkeypatch.setattr(warm.builder,'MANIFEST',public,raising=False)
    monkeypatch.setattr(warm.builder,'SUPPLEMENTAL_SOURCES',{})
    monkeypatch.setattr(warm.builder,'CUBIC_SOURCES',{'UnintegratedCubic.otf':{}})
    original_verify=warm.builder.verify_sources;calls=[]
    monkeypatch.setattr(warm.builder,'apply_supplemental',lambda font,path:calls.append(str(path)))
    output=tmp_path/'warm';output.mkdir()
    plan=dict(publicManifestSha256=digest(original),alreadyApplied=['Old.ttf'],groups=[dict(index=0,sources=[dict(name='New.ttf',recipeSha256='hash-New.ttf')])],publicAssets={e['file']:e['sha256'] for e in entries})
    (output/'plan.json').write_text(json.dumps(plan))
    def build():
        assert warm.builder.verify_sources is original_verify,'Source order/coverage computation must stay intact'
        assert set(warm.builder.SUPPLEMENTAL_SOURCES)=={'Old.ttf','New.ttf'}
        assert warm.builder.CUBIC_SOURCES=={},'Independent cubic stage must remain disabled in TT warmers'
        assert warm.builder.MANIFEST!=public and warm.builder.OUT!=fonts
        warm.builder.apply_supplemental(None,Path('sources/New.ttf'))
        with pytest.raises(RuntimeError,match='unexpectedly missed'):
            warm.builder.apply_supplemental(None,Path('sources/Old.ttf'))
        private=json.loads(warm.builder.MANIFEST.read_text().split('export default ')[1].rstrip(';\n'))
        for entry in private['fonts']:
            assert entry['file'].startswith('warm/group-0/fonts/')
            if entry['source'].endswith('New.ttf'):
                (tmp_path/entry['file']).write_bytes(b'new styled private')
                entry['supplementalTreatment']=dict(recipeSha256='hash-New.ttf')
        warm.builder.MANIFEST.write_text('export default '+json.dumps(private)+';\n')
    monkeypatch.setattr(warm.builder,'build',build)
    warm.run(output,0)
    assert calls==['sources/New.ttf']
    assert public.read_bytes()==original
    assert (fonts/'Old.woff2').read_bytes()==b'Old original'
    assert (fonts/'New.woff2').read_bytes()==b'New original'
    assert (output/'group-0/complete.json').exists()


def test_merge_requires_identical_duplicate_cache_content(tmp_path,monkeypatch):
    monkeypatch.setattr(warm,'assert_public_unchanged',lambda plan:None)
    monkeypatch.setattr(warm.adapter,'CACHE',tmp_path/'merged')
    plan=dict(groups=[dict(index=0),dict(index=1)])
    (tmp_path/'plan.json').write_text(json.dumps(plan))
    for index,content in [(0,b'candidate A'),(1,b'candidate B')]:
        group=tmp_path/f'group-{index}';cache=group/'glyph-cache';cache.mkdir(parents=True)
        (group/'complete.json').write_text('{}');(cache/'same-key.glyf').write_bytes(content)
    with pytest.raises(AssertionError,match='Cache collision differs'):warm.merge(tmp_path)


def test_merge_waits_for_declared_auxiliary_warmers(tmp_path,monkeypatch):
    monkeypatch.setattr(warm,'assert_public_unchanged',lambda plan:None)
    (tmp_path/'plan.json').write_text(json.dumps(dict(groups=[],auxiliaryCompletions=['aux-range/complete.json'])))
    with pytest.raises(AssertionError,match='Auxiliary warmer has not completed'):warm.merge(tmp_path)
