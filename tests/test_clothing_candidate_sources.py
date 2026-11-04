"""Native detail checks for unregistered clothing/accessory candidates."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import pytest
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_clothing_objects import prepare
from emoji_svg_recipe import raster
STRUCTURE={e['key']:e for e in json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())}


def native_shape(key,index,stroke=False,visible=False):
    raw=(ROOT/STRUCTURE[key]['source']['path']).read_bytes()
    root=ET.fromstring(raw)
    parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
    for i,e in enumerate(shapes):
        if i!=index:
            if not visible:parents[e].remove(e)
        else:
            style=dict(rule.split(':',1) for rule in e.get('style','').split(';') if ':' in rule)
            width=e.get('stroke-width',style.get('stroke-width','1'))
            e.attrib.pop('style',None)
            e.set('fill','none' if stroke else '#111111')
            e.set('stroke','#111111' if stroke else 'none')
            if stroke:e.set('stroke-width',width)
    painted=raster(root)
    if visible:
        # The rear handle is partly covered by later bag faces. Compare
        # its visible contribution, not the isolated hidden endpoints.
        without=ET.fromstring(raw);p={c:a for a in without.iter() for c in a}
        elements=[e for e in without.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
        p[elements[index]].remove(elements[index])
        painted&=~raster(without)
    return painted


@pytest.mark.parametrize('key,dark',[('1f453',False),('1f576',True)])
def test_clear_and_dark_lenses_remain_distinct(key,dark):
    (_, *_, ink),r=prepare(key)
    for index in [0,1]:
        ys,xs=np.nonzero(native_shape(key,index))
        x=round(xs.mean())+r['padding'];y=round(ys.mean())+r['padding']
        darkness=ink[y-8:y+9,x-8:x+9].mean()
        assert darkness>.95 if dark else darkness<.05


@pytest.mark.parametrize('index',[0,6,10,17])
def test_shopping_bags_keep_all_four_open_handles(index):
    (_, *_, ink),r=prepare('1f6cd')
    native=np.pad(skeletonize(native_shape('1f6cd',index,stroke=True,visible=True)),r['padding'])
    assert native.sum()>100
    assert (native&ndi.binary_dilation(ink,iterations=6)).sum()/native.sum()>.95
    pen=BoundsPen(None)
    parse_path(STRUCTURE['1f6cd']['shapes'][index]['attributes']['d'],pen)
    x0,y0,x1,y1=pen.bounds
    x=round((x0+x1)/2*12)+r['padding']
    y=round((y0+(y1-y0)*.25)*12)+r['padding']
    assert ink[y-3:y+4,x-3:x+4].mean()<.1


def test_beads_keep_every_native_bead_and_the_tassel():
    (_, *materials, ink),r=prepare('1f4ff')
    colours=dict(zip(r['colourNames'],materials))
    for index in [*range(0,78,3),79]:
        ys,xs=np.nonzero(native_shape('1f4ff',index))
        x=round(xs.mean())+r['padding'];y=round(ys.mean())+r['padding']
        assert colours['brown'][y,x] and not ink[y,x],index
    assert colours['yellow'].sum()>1000


def test_hair_pick_preserves_all_seven_native_teeth():
    (_,ink),r=prepare('1faae')
    p=r['padding'];ink=ink[p:p+1536,p:p+1536]
    native=native_shape('1faae',1)
    for diagonal in [30,50]:
        x=np.arange(1536);y=x-diagonal*12;valid=(y>=0)&(y<1536)
        assert ndi.label(native[y[valid],x[valid]])[1]==7
        assert ndi.label(ink[y[valid],x[valid]])[1]==7


def test_fan_preserves_each_of_six_native_fold_strips():
    (_, *_, ink),r=prepare('1faad')
    covered=ndi.binary_dilation(ink,iterations=6)
    for index in range(5,11):
        native=np.pad(native_shape('1faad',index),r['padding'])
        assert native.sum()>100
        assert (native&covered).sum()/native.sum()>.95,index


def test_ring_band_keeps_its_large_open_counter():
    (_, *materials, ink),r=prepare('1f48d')
    ys,xs=np.nonzero(native_shape('1f48d',1))
    x=round((xs.min()+xs.max())/2)+r['padding']
    y=round((ys.min()+ys.max())/2)+r['padding']
    assert not ink[y-12:y+13,x-12:x+13].any()
    assert not any(mask[y,x] for mask in materials)


@pytest.mark.parametrize('key',['1f48d','1f48e'])
def test_gemstone_facets_keep_blue_and_white_contrast(key):
    (_, *materials, _),r=prepare(key)
    colours=dict(zip(r['colourNames'],materials))
    assert colours['white'].sum()>100 and colours['blue'].sum()>100
    assert len(set(map(tuple,r['rgbs'])))==len(r['colourNames'])
