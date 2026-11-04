"""Native identities and colour distinctions in place/material/weather art."""
import json,sys
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_places_weather import prepare,RECIPES
from emoji_svg_recipe import raster
STRUCTURE={e['key']:e for e in json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())}


@lru_cache(maxsize=10)
def candidate(key):return prepare(key)


def native_shape(key,index):
    root=ET.fromstring((ROOT/STRUCTURE[key]['source']['path']).read_bytes())
    parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
    _,paper,ink,cutouts,colours=RECIPES[key]
    selected=set(paper)|set(ink)|set(cutouts)|set(colours)
    for i,e in enumerate(shapes):
        if i<index or i not in selected:parents[e].remove(e)
        else:
            e.attrib.pop('style',None);e.attrib.pop('opacity',None)
            e.set('fill','#111111' if i==index else '#ffffff');e.set('stroke','none')
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


def test_brick_wall_preserves_all_twenty_four_separate_bricks_and_open_mortar():
    (paper,*materials,ink),r=candidate('1f9f1')
    assert r['sourceComponents']==24
    for i in range(25,49):assert_centres('1f9f1',[i],'red' if i%3 else 'brown')
    x=round(43.4*12)+r['padding'];y=round(10*12)+r['padding']
    assert not ink[y-2:y+3,x-2:x+3].any()
    assert not any(m[y,x] for m in materials)


def test_wood_keeps_brown_bark_and_native_growth_rings():
    assert_centres('1fab5',[1],'brown')
    (_, *materials, ink),r=candidate('1fab5')
    for i in [9,11,12,13]:
        native=np.pad(native_shape('1fab5',i),r['padding'])
        assert native.sum()>100
        assert (native&ndi.binary_dilation(ink,iterations=6)).sum()/native.sum()>.9,i


def test_rock_keeps_light_and_dark_native_facets():
    assert_centres('1faa8',[1,4,6],'black')
    assert_centres('1faa8',[2,3,5],'white')


def test_tent_keeps_roof_front_flap_and_dark_entrance():
    for i,c in [(0,'black'),(1,'orange'),(2,'red'),(3,'brown')]:assert_centres('26fa',[i],c)


def test_barber_pole_keeps_both_red_stripes_blue_and_white():
    assert_centres('1f488',[1,3],'red')
    assert_centres('1f488',[2],'blue')
    assert_centres('1f488',[0],'paper')


def test_thermometer_keeps_all_five_ticks_and_red_mercury():
    assert_centres('1f321',range(5,10),'black')
    assert_centres('1f321',[3],'red')


def test_saturn_ring_extends_beyond_both_sides_of_the_planet():
    (_, *materials, ink),r=candidate('1fa90')
    colours=dict(zip(r['colourNames'],materials))
    by,bx=np.nonzero(colours['blue']&~ink);py,px=np.nonzero(colours['yellow']&~ink)
    assert bx.min()<px.min() and bx.max()>px.max()
    assert np.corrcoef(bx,by)[0,1]>.7
    assert .85<np.ptp(px)/np.ptp(py)<1.15


def test_rainbow_keeps_all_six_native_bands_in_their_original_colour_order():
    _,r=candidate('1f308')
    colours=['red','orange','yellow','green','blue','purple']
    assert r['colourNames']==colours and len(set(map(tuple,r['rgbs'])))==6
    for index,colour in enumerate(colours):assert_centres('1f308',[index],colour)
