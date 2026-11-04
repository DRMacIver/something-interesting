"""Independent semantic-detail checks for unregistered money candidates."""
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_money_objects import prepare
from emoji_svg_recipe import raster
STRUCTURE={e['key']:e for e in json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())}


@pytest.mark.parametrize('key,index',[('1f4b4',5),('1f4b6',6),('1f4b7',6)])
def test_yen_euro_and_pound_keep_their_native_currency_silhouettes(key,index):
    (_, *materials, ink),r=prepare(key)
    painted=ink.copy()
    if 'white' in r['colourNames']:painted|=materials[r['colourNames'].index('white')]
    covered=ndi.binary_dilation(painted,iterations=6)
    root=ET.fromstring((ROOT/r['source']['path']).read_bytes())
    parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
    for i,e in enumerate(shapes):
        if i!=index:parents[e].remove(e)
        else:
            e.attrib.pop('style',None);e.set('fill','#111111');e.set('stroke','none')
    native=np.pad(raster(root),r['padding'])
    assert native.sum()>100
    assert np.count_nonzero(native&covered)/native.sum()>.95


@pytest.mark.parametrize('key',['1f4b0','1f4b5'])
def test_dollars_use_the_authentic_comic_currency_glyph(key):
    _,r=prepare(key)
    record=r['lettering']
    assert [e['character'] for e in record['letters']]==['$']
    font=TTFont(ROOT/record['path'])
    assert record['letters'][0]['glyph']==font.getBestCmap()[ord('$')]


def test_receipt_keeps_every_native_writing_line():
    (_,ink),r=prepare('1f9fe')
    for index in range(2,13):
        a=STRUCTURE['1f9fe']['shapes'][index]['attributes']
        x=round((float(a['x1'])+float(a['x2']))/2*12)+r['padding']
        y=round((float(a['y1'])+float(a['y2']))/2*12)+r['padding']
        assert ink[y-16:y+17,x-16:x+17].any(),index


def test_coin_retains_ten_stars_and_four_white_columns():
    (paper,yellow,ink),r=prepare('1fa99')
    for index in [*range(16,24),28,29,54,57,60,63]:
        shape=STRUCTURE['1fa99']['shapes'][index]
        if shape['tag']=='polygon':
            points=np.fromstring(shape['attributes']['points'].replace(',',' '),sep=' ').reshape(-1,2)
            x0,y0=points.min(axis=0);x1,y1=points.max(axis=0)
        else:
            pen=BoundsPen(None)
            parse_path(shape['attributes']['d'],pen)
            x0,y0,x1,y1=pen.bounds
        x=round((x0+x1)/2*12)+r['padding'];y=round((y0+y1)/2*12)+r['padding']
        if index<30:assert ink[y-3:y+4,x-3:x+4].mean()>.8,index
        else:
            assert paper[y,x] and not yellow[y,x] and not ink[y,x],index


def test_yen_chart_preserves_the_complete_native_white_five_unit_stroke():
    (_, *materials, ink),r=prepare('1f4b9')
    white=materials[r['colourNames'].index('white')]&~ink
    points=np.fromstring(STRUCTURE['1f4b9']['shapes'][2]['attributes']['points'].replace(',',' '),sep=' ').reshape(-1,2)
    assert points[-1,1]<points[0,1]
    for a,b in zip(points,points[1:]):
        for t in [.2,.5,.8]:
            x,y=np.rint((a+(b-a)*t)*12+r['padding']).astype(int)
            assert white[y-2:y+3,x-2:x+3].mean()>.9
    # Sample across the long rising segment, away from joins and the ¥.
    a,b=points[-2:];centre=(a+b)/2;direction=b-a
    normal=np.array([-direction[1],direction[0]])/np.linalg.norm(direction)
    offsets=np.linspace(-7,7,337)
    samples=np.rint((centre+offsets[:,None]*normal)*12+r['padding']).astype(int)
    width=white[samples[:,1],samples[:,0]].sum()*(offsets[1]-offsets[0])
    assert 4<width<6,width
    assert r['strokeStyles'][2]=={'width':5,'colour':'white'}
