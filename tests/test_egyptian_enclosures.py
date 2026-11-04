"""Native enclosure components preserve their distinct ends and strip geometry."""
import importlib.util
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
spec=importlib.util.spec_from_file_location('enclosure_builder',ROOT/'tools/font/build_egyptian_enclosures.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


def test_enclosure_components_are_reproducible_and_retain_native_distinctions():
    manifest=builder.build()
    assert json.loads((ROOT/'js/egyptian-enclosure-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))==manifest
    entries=manifest['entries']
    assert len(entries)==16
    assert entries['1343C']['sourceGlyph']=='QC6'
    assert entries['1343E']['sourceGlyph']=='QW6'
    assert entries['1343C']['path']!=entries['1343E']['path']
    assert entries['13379']['sourceGlyph']=='cbL'
    assert entries['1337A']['sourceGlyph']=='ceL'
    assert entries['13286']['sourceGlyph']=='cwbL'
    assert entries['13287']['sourceGlyph']=='cweL'
    for entry in entries.values():
        x0,y0,x1,y1=entry['bounds']
        assert x1>x0 and y1>y0 and entry['advance']>0
        assert y0<0 and y1>manifest['contentHeight']
    # Strips overlap adjacent advances slightly so connected outlines have no seam.
    for cp in ['1343C','1343E']:
        e=entries[cp]
        assert e['bounds'][0]<0 and e['bounds'][2]>e['advance']
