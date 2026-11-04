"""Every new Seal drawing retains its native curves, identity and source offer."""
import hashlib
import json
import subprocess
import sys
from zipfile import ZipFile

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from native_sfnt_loader import evidence_ttfont as TTFont

from font_baseline_checks import reviewed_later_change
from test_font_scripts import ROOT, manifest, shape


def spec():
    return json.loads((ROOT/'data/font-sources/seal-sans.json').read_text())


def test_all_139_seal_drawings_preserve_native_curves_and_advances():
    config = spec()
    entry = next(e for e in manifest()['fonts'] if e['source'].endswith('/DadSealSans-Regular.otf'))
    original = TTFont(ROOT/config['files'][0]['path'])
    font = TTFont(ROOT/entry['file'])
    points = {cp for a,b in config['include_ranges'] for cp in range(a,b+1)}
    assert len(points) == 139 and set(font.getBestCmap()) == points
    assert not {'COLR','CPAL','GSUB','GPOS'} & set(font.keys())
    assert all(t.format != 14 for t in font['cmap'].tables)
    assert font['head'].unitsPerEm == original['head'].unitsPerEm == 1024
    source_glyphs, result_glyphs = original.getGlyphSet(), font.getGlyphSet()
    drawings = set()
    for cp in sorted(points):
        a,b = original.getBestCmap()[cp], font.getBestCmap()[cp]
        pa,pb = DecomposingRecordingPen(source_glyphs), DecomposingRecordingPen(result_glyphs)
        source_glyphs[a].draw(TransformPen(pa,(1,0,0,1,0,340)))
        result_glyphs[b].draw(pb)
        assert pa.value == pb.value, hex(cp)
        assert pa.value
        drawings.add(repr(pb.value))
        assert font['hmtx'][b] == original['hmtx'][a], hex(cp)
        assert shape(ROOT/entry['file'],chr(cp)) == shape(ROOT/config['files'][0]['path'],chr(cp)), hex(cp)
    assert len(drawings) == 139
    review=json.loads((ROOT/config['review']).read_text())
    assert len(review['characters'])==141
    assert all(r['review']!='pending' for r in review['characters'])
    assert points <= {r['codepoint'] for r in review['characters']}


def test_all_380_previous_script_fonts_are_unchanged():
    previous=json.loads((ROOT/'output/font-review/pre-seal-sans-integration/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    old={e['family']:e for e in previous['fonts']}
    current={e['family']:e for e in manifest()['fonts']}
    assert len(old)==380 and len(current)==381
    for family,entry in old.items():
        # Later attachment repair is independently checked against its frozen
        # baseline, with exact curves/metrics and all other font files retained.
        if entry['source'].endswith('/NotoSansMath-Regular.ttf'):continue
        if reviewed_later_change(entry,current[family]):continue
        assert current[family]==entry, family
        assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()==entry['sha256']


def test_source_download_rebuilds_identical_production_font(tmp_path):
    config=spec()
    entry=next(e for e in manifest()['fonts'] if e['source'].endswith('/DadSealSans-Regular.otf'))
    with ZipFile(ROOT/config['source_package']) as package:
        assert hashlib.sha256((ROOT/config['source_package']).read_bytes()).hexdigest()==entry['correspondingSourceSha256']
        for name in ['build_seal_sans.py','seal-sans.json','SealSans-Regular_v1.otf','requirements.txt','LICENSE','README.txt']:
            (tmp_path/name).write_bytes(package.read(name))
        assert package.read('LICENSE')==(ROOT/config['licence']).read_bytes()
        archive=next(e for e in config['files'] if e['path'].endswith('.zip'))
        assert hashlib.sha256(package.read('upstream.zip')).hexdigest()==archive['sha256']
    with ZipFile(ROOT/archive['path']) as upstream:
        prefix='seal-sans-'+config['commit']+'/'
        assert upstream.read(prefix+'SealSans-Regular_v1.otf')==(ROOT/config['files'][0]['path']).read_bytes()
        assert upstream.read(prefix+'LICENSE')==(ROOT/config['licence']).read_bytes()
        assert any('.ufo/glyphs/' in n and n.endswith('.glif') for n in upstream.namelist())
        assert any(n.endswith('.fcp') for n in upstream.namelist())
    subprocess.run([sys.executable,str(tmp_path/'build_seal_sans.py'),'--source',str(tmp_path/'SealSans-Regular_v1.otf'),'--spec',str(tmp_path/'seal-sans.json'),'--output',str(tmp_path/'native.otf'),'--woff2',str(tmp_path/'rebuilt.woff2')],check=True)
    assert (tmp_path/'rebuilt.woff2').read_bytes()==(ROOT/entry['file']).read_bytes()
    font=TTFont(ROOT/entry['file'])
    assert 'Ghimist' in font['name'].getDebugName(0)
    assert 'GNU Affero' in font['name'].getDebugName(13)
    assert '2026-11-03' in font['name'].getDebugName(10)
    assert config['source_package'] in (ROOT/'index.html').read_text()
