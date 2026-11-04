"""Complete all-GID pressure proofs reuse only their exact immutable inputs."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import pytest
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
import font_baseline_checks as checks
import supplemental_adapter as pressure


@pytest.fixture
def small_pressure(tmp_path,monkeypatch):
    root=Path(__file__).resolve().parents[1]
    entries=json.loads((root/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))['fonts']
    entry=copy.deepcopy(next(e for e in entries if e['file'].endswith('/24035b96a3ea.woff2')))
    frozen=Path('output/font-review/supplemental-production-baselines')/Path(entry['file']).name
    paths=[Path(entry['file']),Path(entry['source']),Path(entry['supplementalTreatment']['report']),frozen,frozen.with_suffix('.json')]
    for relative in paths:
        target=tmp_path/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/relative,target)
    report=json.loads((root/entry['supplementalTreatment']['report']).read_text());native=TTFont(root/frozen);native.setGlyphOrder([r['glyph'] for r in report['records']]);gs=native.getGlyphSet();files=[]
    for row in report['records']:
        if row['status']!='adapted':continue
        name=row['glyph'];pen=SVGPathPen(gs);gs[name].draw(pen);t=entry['supplementalTreatment']
        key=hashlib.sha256(json.dumps([t['recipeSha256'],t['settings'],native['head'].unitsPerEm,native['hmtx'][name],name,pen.getCommands()],sort_keys=True).encode()).hexdigest()
        for suffix in ('.json','.glyf'):
            target=tmp_path/'cache'/(key+suffix);target.parent.mkdir(exist_ok=True);shutil.copyfile(pressure.CACHE/(key+suffix),target)
        files.append(tmp_path/'cache'/(key+'.glyf'))
    assert files
    monkeypatch.setattr(checks,'ROOT',tmp_path);monkeypatch.setattr(pressure,'CACHE',tmp_path/'cache')
    return entry,files


def test_complete_proof_runs_once_but_returns_fresh_fonts(small_pressure,monkeypatch):
    entry,files=small_pressure;calls=[];original=checks.assert_pressure_glyph_lineage
    def lineage(*args,**kwargs):calls.append(kwargs.get('codepoints',args[1] if len(args)>1 else None));return original(*args,**kwargs)
    monkeypatch.setattr(checks,'assert_pressure_glyph_lineage',lineage)
    first=checks.pinned_packaging_font(entry);second=checks.pinned_packaging_font(entry)
    assert first is not second and calls==[None]
    cp=next(iter(first.getBestCmap()));checks.assert_pressure_glyph_lineage(entry,[cp])
    assert calls==[None,[cp]],'Subset checks must not use the complete-proof memo'


def test_complete_pressure_cache_mutation_rejects_even_restored_mtime(small_pressure):
    entry,files=small_pressure;checks.pinned_packaging_font(entry)
    path=files[0];stat=path.stat();data=path.read_bytes();glyph=Glyph(data=data)
    actual=TTFont(checks.ROOT/entry['file']);glyph.expand(actual['glyf']);x,y=glyph.coordinates[0];glyph.coordinates[0]=(x+1,y)
    path.write_bytes(glyph.compile(actual['glyf'],recalcBBoxes=False));os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    with pytest.raises(AssertionError):checks.pinned_packaging_font(entry)


def test_combining_font_cache_observes_ctime_and_inode(tmp_path,monkeypatch):
    import test_combining_outlines as catalog
    from test_dense_skeleton import fixture_font
    source=tmp_path/'font.ttf';source.write_bytes(fixture_font());monkeypatch.setattr(catalog,'ROOT',tmp_path)
    first=catalog.font('font.ttf');first['head'].unitsPerEm=777;stat=source.stat();raw=source.read_bytes()
    source.write_bytes(raw);os.utime(source,ns=(stat.st_atime_ns,stat.st_mtime_ns));second=catalog.font('font.ttf')
    assert first is not second and second['head'].unitsPerEm==1000
    replacement=tmp_path/'replacement';replacement.write_bytes(raw);os.utime(replacement,ns=(stat.st_atime_ns,stat.st_mtime_ns));replacement.replace(source)
    assert catalog.font('font.ttf') is not second
