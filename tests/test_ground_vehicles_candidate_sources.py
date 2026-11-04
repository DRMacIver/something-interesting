"""Structural ground-vehicle details must survive their native conversion."""
import json,sys
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_ground_vehicles import prepare,RECIPES,STROKE_PATHS
from emoji_svg_recipe import raster
STRUCTURE={e['key']:e for e in json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())}


@lru_cache(maxsize=10)
def candidate(key):return prepare(key)


def native_shape(key,index,stroke=False,visible=True):
    root=ET.fromstring((ROOT/STRUCTURE[key]['source']['path']).read_bytes())
    parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
    _,paper,ink,cutouts,colours=RECIPES[key]
    selected=set(paper)|set(ink)|set(cutouts)|set(colours)|STROKE_PATHS.get(key,set())
    for i,e in enumerate(shapes):
        parent=e;definition=False
        while parent in parents:
            parent=parents[parent]
            if parent.tag.split('}')[-1] in {'defs','clipPath','mask','pattern'}:definition=True;break
        if definition and i!=index:continue
        if i!=index and (not visible or i<index or i not in selected):parents[e].remove(e);continue
        style=dict(rule.split(':',1) for rule in e.get('style','').split(';') if ':' in rule)
        width=e.get('stroke-width',style.get('stroke-width','1'))
        e.attrib.pop('style',None);e.attrib.pop('opacity',None)
        colour='#111111' if i==index else '#ffffff'
        e.set('fill',colour);e.set('stroke','none')
        if (stroke and i==index) or (i!=index and i in STROKE_PATHS.get(key,set())):
            e.set('fill','none');e.set('stroke',colour);e.set('stroke-width',width)
    return raster(root)


def assert_centres(key,indices,colour,radius=2):
    (paper,*materials,ink),r=candidate(key)
    if colour=='black':paint=ink
    elif colour=='paper':
        paint=paper&~ink
        for m in materials:paint&=~m
    else:paint=materials[r['colourNames'].index(colour)]&~ink
    for index in indices:
        native=native_shape(key,index);assert native.sum()>100,(key,index)
        y,x=np.unravel_index(ndi.distance_transform_edt(native).argmax(),native.shape)
        x+=r['padding'];y+=r['padding']
        assert paint[y-radius:y+radius+1,x-radius:x+radius+1].mean()>.8,(key,index,colour)


def test_bus_keeps_two_headlamps_mirrors_tyres_and_windshield():
    assert_centres('1f68d',[19,20],'paper')
    assert_centres('1f68d',[0,1,4,5],'black')
    assert_centres('1f68d',[15,16],'light blue')


def test_ambulance_keeps_all_three_star_of_life_bars_and_beacon():
    assert_centres('1f691',[14,15,16],'blue')
    assert_centres('1f691',[10,11],'red')
    assert_centres('1f691',[18],'light blue')
    assert_centres('1f691',[4,6],'grey')


def test_police_keeps_distinct_red_blue_beacons_and_both_headlamps():
    assert_centres('1f694',[13],'blue')
    assert_centres('1f694',[14],'red')
    assert_centres('1f694',[7,8],'yellow')
    assert_centres('1f694',[0,1,2,3],'black')


def test_car_keeps_both_headlamps_windscreen_and_mirrors():
    assert_centres('1f698',[10,12],'paper')
    assert_centres('1f698',[14],'light blue')
    assert_centres('1f698',[5,6],'red')
    assert_centres('1f698',[0,1,7],'black')


def test_pickup_keeps_open_bed_headlamp_window_and_two_wheels():
    assert_centres('1f6fb',[2],'black')
    assert_centres('1f6fb',[12],'paper',radius=1)
    assert_centres('1f6fb',[15],'light blue')
    assert_centres('1f6fb',[5,6],'grey')


def test_racecar_keeps_two_tyres_hubs_and_both_wings():
    assert_centres('1f3ce',[14,17],'grey')
    assert_centres('1f3ce',[6,10],'grey',radius=1)
    assert_centres('1f3ce',[1],'red')


def test_motorcycle_keeps_open_wheels_windscreen_and_exhaust():
    assert_centres('1f3cd',[1,2],'black')
    assert_centres('1f3cd',[11],'light blue',radius=1)
    assert_centres('1f3cd',[12],'grey')
    assert_centres('1f3cd',[17,18],'red')


def assert_skeleton(key,index,colour,stroke=False):
    (_, *materials, ink),r=candidate(key)
    paint=ink if colour=='black' else materials[r['colourNames'].index(colour)]|ink
    native=np.pad(skeletonize(native_shape(key,index,stroke=stroke)),r['padding'])
    assert native.sum()>10,(key,index)
    assert (native&ndi.binary_dilation(paint,iterations=6)).sum()/native.sum()>.95,(key,index)


def test_bicycle_keeps_every_spoke_both_tyres_frame_and_pedals():
    for i in [0,1,*range(3,12),*range(15,26),13,26]:
        assert_skeleton('1f6b2',i,'black')
    assert_skeleton('1f6b2',32,'blue')
    assert_skeleton('1f6b2',38,'grey')
    assert_centres('1f6b2',[30,31],'black',radius=1)


def test_skateboard_keeps_two_native_width_axles_wheels_and_eight_bolts():
    for i in [0,1]:assert_skeleton('1f6f9',i,'grey',stroke=True)
    assert_centres('1f6f9',[4,7,10],'red')
    assert_centres('1f6f9',list(range(14,22)),'grey',radius=1)


def test_roller_skate_keeps_all_five_laces_bow_both_wheels_and_brake():
    for i in range(7,13):assert_skeleton('1f6fc',i,'yellow',stroke=True)
    assert_centres('1f6fc',[18,22],'orange')
    assert_centres('1f6fc',[19,23],'black')
    assert_centres('1f6fc',[20],'grey')
