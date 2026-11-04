"""Semantic marks in the remaining object candidates."""
import json,sys
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_other_objects import prepare,RECIPES
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


def test_nazar_keeps_distinct_blue_white_light_blue_and_black_rings():
    for i,c in [(0,'blue'),(2,'paper'),(3,'light blue'),(4,'black')]:assert_centres('1f9ff',[i],c)
    _,r=candidate('1f9ff')
    colours=dict(zip(r['colourNames'],r['rgbs']))
    assert np.linalg.norm(np.array(colours['blue'])-colours['light blue'])>30


def test_hamsa_keeps_the_eye_and_two_internal_finger_divisions():
    for i,c in [(0,'blue'),(1,'paper'),(2,'light blue'),(3,'black')]:assert_centres('1faac',[i],c)
    (_, *_, ink),r=candidate('1faac');p=r['padding']
    native=native_shape('1faac',18)
    assert ndi.label(native[40*12,45*12:85*12])[1]==2
    assert ndi.label(ink[40*12+p,45*12+p:85*12+p])[1]==2


def test_cigarette_keeps_filter_paper_both_smoke_curls_and_red_embers():
    assert_centres('1f6ac',[1],'paper')
    assert_centres('1f6ac',[3],'orange')
    assert_centres('1f6ac',[0,15],'grey')
    (_, *materials, ink),r=candidate('1f6ac')
    red=materials[r['colourNames'].index('red')]&~ink
    assert red.sum()>100
    ys,xs=np.nonzero(red)
    coal=native_shape('1f6ac',12);cy,cx=np.nonzero(coal)
    assert xs.mean()<cx.max()+r['padding']
    assert cy.min()+r['padding']<ys.mean()<cy.max()+r['padding']


def test_coffin_keeps_both_gold_side_handles():
    assert_centres('26b0',[12,13],'yellow')


def test_headstone_keeps_all_native_inscription_marks():
    assert_centres('1faa6',range(5,13),'black')


def test_urn_keeps_all_three_native_decorative_bands_and_its_lid():
    assert_centres('26b1',[2,3,4],'red')
    assert_centres('26b1',[8],'yellow')


def test_moai_keeps_nose_lips_nostrils_and_lit_front_face():
    assert_centres('1f5ff',[6,7,8,10,11],'black')
    assert_centres('1f5ff',[12],'white')


def test_placard_keeps_a_blank_white_board_and_wooden_handle():
    assert_centres('1faa7',[5],'paper')
    assert_centres('1faa7',[0],'brown')


def test_identification_card_keeps_portrait_photo_frame_and_four_text_lines():
    assert_centres('1faaa',[2,3],'blue')
    assert_centres('1faaa',[1],'paper')
    assert_centres('1faaa',range(4,8),'black')
