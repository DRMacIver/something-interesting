"""Native probes retain matched artwork/positions, including source overlap."""
import importlib.util
import json
import sys
import re
import uharfbuzz as hb
import pytest
from pathlib import Path
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
spec=importlib.util.spec_from_file_location('insertion_builder',ROOT/'tools/font/build_egyptian_insertions.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


@pytest.fixture(scope='module')
def built():
    return builder.build()


def test_native_probe_inventory_is_reproducible_and_geometrically_bounded(built):
    manifest,report=built
    assert report['accepted']==982
    assert report['unmodified_single']==255
    assert report['unmodified_multiple']==212
    assert report['rejected']==[]
    assert len(report['sourceGeometryWarnings'])==512
    assert report['consumedMirrorHelpers']==65
    assert report['documentedCellRules']==4
    assert json.loads((ROOT/'js/egyptian-insertion-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))==manifest
    for key,entry in manifest['entries'].items():
        x,y,w,h=entry['region'];width=entry['width'];height=entry['height']
        assert min(x,y)>=0 and min(w,h)>0,key
        assert x+w<=width and y+h<=height,key
        x0,y0,x1,y1=entry['pathBounds'];dx,dy=entry['pathOffset']
        assert x0+dx>=0 and y0+dy>=0,key
        assert x1+dx<=width and y1+dy<=height,key
    # Independent values from the shaped I10 and F4 reference examples.
    assert manifest['entries']['13193-13433']['region']==[105,620,1575,1240]
    assert manifest['entries']['13102-13432']['region']==[105,0,945,930]


def test_collision_screen_detects_obstructed_and_empty_regions():
    square='M0 0H100V100H0Z'
    assert builder.sampled_ink_hits(square,[0,0,100,100])==100
    assert builder.sampled_ink_hits(square,[110,0,100,100])==0


def test_existing_accepted_templates_are_unchanged_and_native_observations_are_explicit(built):
    manifest,report=built
    before=json.loads((ROOT/'output/font-review/pre-native-insertion-geometry/egyptian-insertion-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert len(before['entries'])==428
    for key,entry in before['entries'].items():assert manifest['entries'][key]==entry,key
    recent=json.loads((ROOT/'output/font-review/pre-insertion-mirror-helpers/egyptian-insertion-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert len(recent['entries'])==910
    for key,entry in recent['entries'].items():assert manifest['entries'][key]==entry,key
    assert len(manifest['entries'])+len(report['rejected'])==982
    assert all('sourceGeometryWarnings' in manifest['entries'][r['key']] for r in report['sourceGeometryWarnings'])
    assert next(r for r in report['sourceGeometryWarnings'] if r['key']=='13010-1343B')['sampledInkHits']==13


def test_multiple_insertion_regions_preserve_logical_control_order(built):
    manifest,_=built
    entries=manifest['entries']
    forward=entries['13193-13433-13434'];reverse=entries['13193-13434-13433']
    assert forward['regions']==[[105,620,1575,1240],[1050,0,945,310]]
    assert reverse['regions']==list(reversed(forward['regions']))
    assert forward['path']==reverse['path']
    for key,entry in entries.items():
        regions=entry.get('regions',[entry['region']])
        assert len(regions)==len(entry['controls'])
        assert key=='-'.join(f'{cp:X}' for cp in entry['container']+entry['controls'])
        for i,(x,y,w,h) in enumerate(regions):
            assert x>=0 and y>=0 and x+w<=entry['width'] and y+h<=entry['height']
        overlap=any(min(x+w,bx+bw)>max(x,bx) and min(y+h,by+bh)>max(y,by)
            for i,(x,y,w,h) in enumerate(regions) for bx,by,bw,bh in regions[i+1:])
        assert overlap==('native insertion regions overlap' in entry.get('sourceGeometryWarnings',[]))


def test_modifiers_retain_registered_native_glyphs_and_separate_region_checks(built):
    manifest,report=built
    assert (report['mirrored'],report['rotated'],report['rotated_mirrored'])==(467,24,24)
    entries=manifest['entries']
    assert entries['13020-13440-13433']['sourceGlyph']=='A28R'
    # Native mirroring uses the separately named J7a alternate, not an R suffix.
    assert entries['13413-13440-1343A']['sourceGlyph']=='J7a'
    assert entries['13093-FE01-13439']['sourceGlyph']=='D28o'
    assert entries['131F9-FE01-13440-1343B']['sourceGlyph']=='N11oR'
    # The mirrored snake uses its separately shaped native drawing/region,
    # including its observed intersection; never reuse the unmodified path.
    assert '13193-13433' in entries
    assert entries['13193-13440-13433']['path']!=entries['13193-13433']['path']
    registered=set()
    for line in (ROOT/'data/unicode/18.0.0/StandardizedVariants.txt').read_text().splitlines():
        if not line.startswith('#') and 'EGYPTIAN HIEROGLYPH' in line and 'rotated' in line:
            registered.add(tuple(int(c,16) for c in line.split(';')[0].split()))
    for entry in entries.values():
        c=entry['container']
        if len(c)>1 and 0xFE00<=c[1]<=0xFE06:assert tuple(c[:2]) in registered


def test_explicit_mirror_helpers_reflect_every_native_control_point_without_moving_slots(built):
    manifest,_=built;entries=manifest['entries'];checked=0
    raw=(builder.CACHE/'eot.ttf').read_bytes();font=TTFont(builder.CACHE/'eot.ttf');native=hb.Font(hb.Face(raw))
    for entry in entries.values():
        if 'sourceTransform' not in entry:continue
        container=[cp for cp in entry['container'] if cp!=0x13440]
        plain=entries['-'.join(f'{cp:X}' for cp in container+entry['controls'])]
        a,b=RecordingPen(),RecordingPen();parse_path(plain['path'],a);parse_path(entry['path'],b)
        assert len(a.value)==len(b.value)
        for (op,points),(other,reflected) in zip(a.value,b.value):
            assert op==other
            for (x,y),(rx,ry) in zip(points,reflected):
                assert abs(rx-(entry['sourceTransform'][4]-x))<.000001
                assert abs(ry-y)<.000001
        # Compare against the actual mirrored native probe, not the plain
        # source's slots: its native state can select different child sizes.
        def slots(row):
            dx,dy=row['pathOffset']
            return [[x-dx,y-dy,w,h] for x,y,w,h in row.get('regions',[row['region']])]
        text=''.join(map(chr,entry['container']))+''.join(chr(cp)+'\U00013441' for cp in entry['controls'])
        buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(native,buf)
        expected=[];cursor=0
        for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
            match=re.fullmatch(r'it([1-6])([1-6])',font.getGlyphName(info.codepoint))
            if match:expected.append([cursor+pos.x_offset,1860-pos.y_offset,int(match[1])*315,int(match[2])*310])
            cursor+=pos.x_advance
        assert slots(entry)==expected
        checked+=1
    assert checked==65
    assert entries['1305C-13440-13432']['sourceGlyph']=='C2b'
    assert entries['130BB-13440-13432']['sourceGlyph']=='D55'
    assert entries['130BD-13440-13434']['sourceGlyph']=='D54'


def test_documented_cell_fallback_is_calibrated_by_native_offset_and_keeps_slot_sizes(built):
    manifest,_=built;entries=manifest['entries'];inventory=builder.review()
    g25=next(r for r in inventory['entries'] if r['source_glyph']=='G25')
    assert builder.documented_region(g25,0x13433,2100,1860,inventory['coordinate_system'])==entries['1315C-13433']['region']==[105,1054,630,620]
    for key in ['13154-13433','13154-13440-13433']:
        assert entries[key]['region']==[105,1054,315,620]
        assert entries[key]['width']==2415
    for key in ['1318F-13434','1318F-13440-13434']:
        assert entries[key]['region']==[1680,0,630,310]
        assert entries[key]['width']==2415
