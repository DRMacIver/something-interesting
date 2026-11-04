"""Flaming-bird identity and exact compound shaping."""
import json,sys
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_phoenix import prepare,RECIPES
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


KEY='1f426_200d_1f525'


def test_phoenix_keeps_red_wings_yellow_breast_beak_and_dark_eye():
    assert_centres(KEY,[5,7],'red')
    assert_centres(KEY,[13,18],'yellow')
    assert_centres(KEY,[14,15,16,17],'black')


def test_phoenix_keeps_every_native_flame_tongue():
    (_, *materials, ink),r=candidate(KEY)
    colours=dict(zip(r['colourNames'],materials))
    flame=ndi.binary_dilation(ink|colours['yellow']|colours['orange'],iterations=4)
    for index in [8,9,10,11,12]:
        native=np.pad(native_shape(KEY,index),r['padding'])
        assert native.sum()>100,index
        assert (native&flame).sum()/native.sum()>.95,index
    assert r['filledRasterPinholePixels']==50 and r['appliedStrength']>0 and not r['fallback']


def test_compiled_phoenix_requires_the_bird_joiner_fire_sequence():
    import hashlib
    from fontTools.ttLib import TTFont
    from test_font_scripts import shape
    folder=ROOT/'output/font-review/pen-translation'
    report=json.loads((folder/'phoenix-candidate.json').read_text())
    path=folder/'phoenix-candidate.woff2';assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
    font=TTFont(path);entry=report['flags'][0]
    assert entry['sequence']=='🐦‍🔥' and len(report['flags'])==1
    for fontpath in [path,folder/'phoenix-candidate-ink.woff2']:
        glyph=shape(fontpath,'🐦‍🔥',True)
        assert len(glyph)==1 and font.getGlyphName(glyph[0][0])==entry['glyphName'] and glyph[0][1]>0
        assert shape(fontpath,'🐦‍🔥🐦‍🔥',True)==glyph+glyph
        separate=shape(fontpath,'🐦🔥',True)
        assert len(separate)==2 and all(g[0]!=glyph[0][0] for g in separate)
