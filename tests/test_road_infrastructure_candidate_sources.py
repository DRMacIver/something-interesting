"""Road, rail and traffic-device details from independent native references."""
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
from prototype_road_infrastructure import prepare,RECIPES,STROKE_PATHS
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


def test_motorway_keeps_two_outer_lines_ten_lane_dashes_and_down_arrows():
    (_, *materials, ink),r=candidate('1f6e3')
    white=~ink
    for name,m in zip(r['colourNames'],materials):
        if name!='white':white&=~m
    for index in range(6,18):
        native=np.pad(native_shape('1f6e3',index),r['padding'])
        assert native.sum()>100,index
        assert (native&ndi.binary_dilation(white,iterations=4)).sum()/native.sum()>.95,index
    assert_centres('1f6e3',[28,29],'white')


def test_railway_keeps_six_sleepers_and_both_metal_rails():
    # The vanishing-point sleeper retains a 3x3 core; a 5x5 sample crosses
    # its black edge after pressure treatment. All six centres must survive.
    assert_centres('1f6e4',range(20,26),'brown',radius=1)
    (_, *_, ink),r=candidate('1f6e4')
    for index in [26,27]:
        native=native_shape('1f6e4',index)
        boundary=native&~ndi.binary_erosion(native)
        boundary=np.pad(boundary,r['padding'])
        assert (boundary&ndi.binary_dilation(ink,iterations=4)).sum()/boundary.sum()>.95,index


def test_fuel_pump_keeps_display_bars_oil_drop_and_red_nozzle():
    assert_centres('26fd',[4,5,8],'black')
    assert_centres('26fd',[3,7],'paper')
    assert_centres('26fd',[14],'red')
    (_, *materials, ink),r=candidate('26fd')
    grey=materials[r['colourNames'].index('grey')]
    # The native hose is an open six-unit stroke, not a filled figure-eight.
    native=np.pad(skeletonize(native_shape('26fd',0,stroke=True)),r['padding'])
    assert native.sum()>100
    assert (native&ndi.binary_dilation(grey,iterations=6)).sum()/native.sum()>.95
    assert r['strokeStyles'][0]=={'width':6,'colour':'grey'}
    assert_centres('26fd',[12],'grey')


def test_red_beacon_keeps_its_white_flash():
    assert_centres('1f6a8',[2],'red')
    assert_centres('1f6a8',[5],'white')


@pytest.mark.parametrize('key,order,axis',[('1f6a5',['green','yellow','red'],1),('1f6a6',['red','yellow','green'],0)])
def test_traffic_lights_preserve_native_colour_order(key,order,axis):
    (_, *materials, ink),r=candidate(key)
    colours=dict(zip(r['colourNames'],materials));positions=[]
    for colour in order:
        ys,xs=np.nonzero(colours[colour]&~ink)
        assert len(xs)>100
        positions.append([ys.mean(),xs.mean()][axis])
    assert positions==sorted(positions)
    assert len(set(map(tuple,r['rgbs'])))==4


def test_stop_sign_keeps_the_native_red_octagonal_face():
    (_,red,ink),r=candidate('1f6d1')
    native=np.pad(native_shape('1f6d1',0),r['padding'])
    assert (native&ndi.binary_dilation(red|ink,iterations=4)).sum()/native.sum()>.99
    ys,xs=np.nonzero(red)
    assert .98<np.ptp(xs)/np.ptp(ys)<1.02


def test_barrier_keeps_clipped_black_stripes_yellow_boards_and_both_flashes():
    (_, *_, ink),r=candidate('1f6a7')
    # These polygons are invisible if their native clip definitions disappear.
    for index in [*range(17,23),*range(26,32)]:
        native=np.pad(native_shape('1f6a7',index),r['padding'])
        assert native.sum()>100,index
        assert (native&ndi.binary_dilation(ink,iterations=4)).sum()/native.sum()>.98,index
    assert_centres('1f6a7',[15,24],'yellow')
    assert_centres('1f6a7',[9,14],'white')
