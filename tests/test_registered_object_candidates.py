"""Registered source extraction preserves the exact visually reviewed fonts."""
import hashlib,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'output/font-review/pen-translation'
INDEX=json.loads((FOLDER/'pre-final-object-registration/index.json').read_text())
INDEX.update(json.loads((FOLDER/'pre-ground-vehicle-registration/index.json').read_text()))


@pytest.mark.parametrize('family',INDEX)
def test_registered_object_family_preserves_reviewed_fonts_and_provenance(family):
    expected=INDEX[family]
    for suffix,key in [('', 'colourSha256'),('-ink','inkSha256')]:
        path=FOLDER/(family+'-candidate'+suffix+'.woff2')
        archive='pre-ground-vehicle-registration' if family=='ground-vehicles' else 'pre-final-object-registration'
        reference=FOLDER/archive/path.name
        assert path.read_bytes()==reference.read_bytes()
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected[key]
    manifest=json.loads((ROOT/f'data/font-sources/noto-emoji-{family}-svg.json').read_text())
    assert manifest['license']=='Noto-SVG-Apache-2.0'
    assert all((ROOT/notice).is_file() for notice in manifest['notices'])
    report=json.loads((FOLDER/(family+'-candidate.json')).read_text())
    assert len(manifest['files'])==len(report['flags'])==expected['drawings']
    assert sum(len(e['include_sequences']) for e in manifest['files'])==expected['forms']
    core=ROOT/('tools/font/emoji_'+family.replace('-','_')+'_svg.py')
    core_hash=hashlib.sha256(core.read_bytes()).hexdigest()
    sources={e['path']:e for e in manifest['files']}
    for entry in report['flags']:
        treatment=entry['penTreatment'];source=treatment['source']
        assert treatment['programSha256']==core_hash
        assert source==sources[source['path']]
        assert source['include_sequences']==entry['qualificationForms']
        assert source['build_target']=='emoji-artwork' and source['licenseFamily']==manifest['license']
        assert treatment['appliedStrength']>0 and not treatment['fallback']
