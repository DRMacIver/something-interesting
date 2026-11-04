"""Semantic details in the unregistered tools/instruments candidates."""
import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_tools_instruments import prepare,RECIPES,STROKE_PATHS
from emoji_svg_recipe import raster
SOURCES={Path(e['path']).stem.removeprefix('emoji_u'):e for e in json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']}


@lru_cache(maxsize=16)
def candidate(key):
    return prepare(key)


def native_shape(key,index,stroke=False):
    source=SOURCES[key];raw=(ROOT/source['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
    _,paper,ink,cutouts,colours=RECIPES[key]
    selected=set(paper)|set(ink)|set(cutouts)|set(colours)|STROKE_PATHS.get(key,set())
    for i,e in enumerate(shapes):
        if i<index or i not in selected:parents[e].remove(e)
        else:
            style=dict(rule.split(':',1) for rule in e.get('style','').split(';') if ':' in rule)
            width=e.get('stroke-width',style.get('stroke-width','1'))
            e.attrib.pop('style',None);e.attrib.pop('opacity',None)
            e.set('fill','#111111' if i==index else '#ffffff');e.set('stroke','none')
            if (stroke and i==index) or (i!=index and i in STROKE_PATHS.get(key,set())):
                e.set('fill','none');e.set('stroke','#111111' if i==index else '#ffffff');e.set('stroke-width',width)
    return raster(root)


def assert_material_centres(key,indices,colour):
    (paper, *materials, ink),report=candidate(key)
    if colour=='black':painted=ink
    elif colour=='white' and colour not in report['colourNames']:
        painted=paper&~ink
        for mask in materials:painted&=~mask
    else:painted=materials[report['colourNames'].index(colour)]&~ink
    for index in indices:
        native=native_shape(key,index)
        assert native.sum()>100,(key,index)
        y,x=np.unravel_index(ndi.distance_transform_edt(native).argmax(),native.shape)
        y+=report['padding'];x+=report['padding']
        assert painted[y-2:y+3,x-2:x+3].mean()>.8,(key,index,colour)


def test_shield_keeps_all_twenty_three_white_rivets():
    assert_material_centres('1f6e1',[*range(5,17),*range(29,40)],'white')


def test_accordion_keeps_twelve_white_buttons_and_ten_black_keys():
    assert_material_centres('1fa97',range(33,45),'white')
    assert_material_centres('1fa97',range(20,30),'black')


def test_flute_keeps_seven_finger_holes_and_the_end_bore():
    assert_material_centres('1fa88',[3,4,6,8,10,12,14,16],'black')


def test_maracas_keep_both_heads_and_both_flower_details():
    assert_material_centres('1fa87',[3,17],'green')
    assert_material_centres('1fa87',[8,9,10,22,23,24],'black')


@pytest.mark.parametrize('key,dark,light',[('1f5e1',[2],[3]),('2694',[0,9],[1,10])])
def test_blades_preserve_native_light_dark_faces(key,dark,light):
    assert_material_centres(key,dark,'black')
    (_, *_, ink),report=candidate(key)
    for index in light:
        native=native_shape(key,index)
        y,x=np.unravel_index(ndi.distance_transform_edt(native).argmax(),native.shape)
        y+=report['padding'];x+=report['padding']
        assert ink[y-2:y+3,x-2:x+3].mean()<.2


def test_banjo_preserves_all_four_strings_in_two_neck_cross_sections():
    (_, *materials, ink),r=candidate('1fa95')
    assert r['settings']['boundary_blur']==.2 and r['appliedStrength']>0 and not r['fallback']
    white=materials[r['colourNames'].index('white')]&~ink
    spec=json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())
    shapes=next(e['shapes'] for e in spec if e['key']=='1fa95')
    lines=[np.fromstring(shapes[i]['attributes']['points'].replace(',',' '),sep=' ').reshape(-1,2)[:2] for i in [23,24,25,26]]
    direction=np.mean([b-a for a,b in lines],axis=0)
    normal=np.array([-direction[1],direction[0]])/np.linalg.norm(direction)
    for t in [.3,.6]:
        points=np.array([a+(b-a)*t for a,b in lines]);centre=points.mean(axis=0)
        projected=(points-centre)@normal
        offsets=np.linspace(projected.min()-.6,projected.max()+.6,400)
        xy=np.rint((centre+offsets[:,None]*normal)*12+r['padding']).astype(int)
        assert ndi.label(white[xy[:,1],xy[:,0]])[1]==4,t


def test_drum_retains_native_cords_and_does_not_invent_a_move_only_mark():
    (_, *materials, ink),r=candidate('1fa98')
    white=materials[r['colourNames'].index('white')]&~ink
    assert r['settings']['boundary_blur']==.2 and r['appliedStrength']>0 and not r['fallback']
    assert r['removedRasterCrumbPixels']<=4
    assert 20 not in STROKE_PATHS['1fa98']
    for index in [11,14,21,23,24,28,29]:
        native=np.pad(native_shape('1fa98',index,stroke=True),r['padding'])
        assert native.sum()>100,index
        assert (native&ndi.binary_dilation(white,iterations=6)).sum()/native.sum()>.9,index
