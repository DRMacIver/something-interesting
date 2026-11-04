"""Check source insertion metadata before any coordinate adaptation."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('insertion_review',ROOT/'tools/font/review_egyptian_insertions.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


def test_inventory_keeps_every_pinned_alternative_and_reports_unmapped_variants():
    report=builder.build()
    source=builder.literal_assignment(builder.CACHE/'insertions.py','insertions')
    assert report['signs']==len(source)==188
    assert report['areas']==sum(len(cells) for controls in source.values() for cells in controls.values())==328
    assert report['mapped_signs']==185
    rows={r['source_glyph']:r for r in report['entries']}
    assert rows['F4']['codepoints']==[0x13102]
    assert rows['I10']['codepoints']==[0x13193]
    assert any(a['control']==0x13433 and a['container_cell']==[6,6] and a['insertion_cell']==[5,4] for a in rows['I10']['areas'])
    assert any(a['control']==0x13433 and a['offset_axis']=='y' and a['offset_twentieths']==2 for a in rows['G25']['areas'])
    assert report['coordinate_system']['hfu']==315
    assert report['coordinate_system']['vfu']==310
    assert json.loads((ROOT/'docs/egyptian-insertion-review.json').read_text())==report


def test_source_loading_does_not_execute_python(tmp_path):
    path=tmp_path/'metadata.py'
    path.write_text("raise RuntimeError('source must not run')\ninsertions={'A': {'ts': {66:'22'}}}\n")
    assert builder.literal_assignment(path,'insertions')=={'A':{'ts':{66:'22'}}}
