"""Structural flight/watercraft details must survive their native conversion."""
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
from prototype_air_water import prepare,RECIPES,STROKE_PATHS
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


def assert_centres(key,indices,colour):
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
        assert paint[y-2:y+3,x-2:x+3].mean()>.8,(key,index,colour)


def test_jet_keeps_cockpit_and_four_cabin_windows():
    assert_centres('2708',[22,26,27,28,29],'black')


def test_small_plane_keeps_four_windows_and_the_propeller():
    assert_centres('1f6e9',[13,14,15,16],'black')
    (_, *materials, ink),r=candidate('1f6e9')
    assert r['removedRasterCrumbPixels']==3 and r['settings']['boundary_blur']==.45
    metal=materials[r['colourNames'].index('grey')]|ink
    native=np.pad(native_shape('1f6e9',19),r['padding'])
    assert (native&ndi.binary_dilation(metal,iterations=6)).sum()/native.sum()>.95


def test_parachute_keeps_all_eight_filled_cord_paths_and_helmet():
    (_, *_, ink),r=candidate('1fa82')
    for index in [0,1,6,7,11,12,13,14]:
        native=np.pad(skeletonize(native_shape('1fa82',index)),r['padding'])
        assert native.sum()>10,index
        assert (native&ndi.binary_dilation(ink,iterations=6)).sum()/native.sum()>.95,index
    assert_centres('1fa82',[10],'blue')
    assert r['filledRasterPinholePixels']==21
    assert len(set(map(tuple,r['rgbs'])))>=6


def test_seat_keeps_white_headrest_and_both_armrests():
    assert_centres('1f4ba',[14],'paper')
    assert_centres('1f4ba',[15,16],'grey')


def test_satellite_keeps_both_solar_grids_and_all_three_dish_spokes():
    (_, *_, ink),r=candidate('1f6f0')
    for index in [3,4,5,6,16,17,18,19,30,31,32]:
        native=np.pad(skeletonize(native_shape('1f6f0',index,stroke=True)),r['padding'])
        assert native.sum()>10,index
        assert (native&ndi.binary_dilation(ink,iterations=6)).sum()/native.sum()>.95,index


def test_saucer_keeps_five_bright_lights_pilot_and_beam():
    assert_centres('1f6f8',[24,26,28,30,33],'white')
    assert_centres('1f6f8',[15],'green')
    assert_centres('1f6f8',[6,13],'light blue')


def test_anchor_keeps_its_real_open_top_ring():
    (_,grey,ink),r=candidate('2693')
    native=native_shape('2693',0,visible=False)
    hole=ndi.binary_fill_holes(native)&~native
    assert hole.sum()>1000
    y,x=np.unravel_index(ndi.distance_transform_edt(hole).argmax(),hole.shape)
    y+=r['padding'];x+=r['padding']
    assert not ink[y-4:y+5,x-4:x+5].any() and not grey[y,x]


def test_passenger_ship_keeps_six_portholes_two_windows_and_red_funnel():
    assert_centres('1f6f3',range(17,25),'black')
    assert_centres('1f6f3',[6],'red')
    assert_centres('1f6f3',[14],'blue')
