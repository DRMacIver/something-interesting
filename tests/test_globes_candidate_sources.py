"""Continents and islands survive translation and the actual globe fonts."""
import hashlib,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
from fontTools.ttLib import TTFont
from fontTools.pens.pointInsidePen import PointInsidePen
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_globes import prepare
from emoji_svg_recipe import raster
from svg_counter_review import review_counters
LAND={'1f30d':[1,2,3,4,6],'1f30e':[2,3],'1f30f':[2,*range(5,17)]}


def native_land(source,index):
    raw=(ROOT/source['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
    for i,e in enumerate(shapes):
        if i!=index:parents[e].remove(e)
        else:
            e.attrib.pop('style',None);e.set('fill','#111111');e.set('stroke','none')
    return raster(root)


@pytest.fixture(scope='module')
def candidate_font():
    folder=ROOT/'output/font-review/pen-translation'
    report=json.loads((folder/'globes-candidate.json').read_text())
    path=folder/'globes-candidate.woff2'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
    return TTFont(path),{e['region']:e for e in report['flags']}


@pytest.mark.parametrize('key',LAND)
def test_every_native_land_component_remains_visible_in_its_correct_globe(key,candidate_font):
    font,entries=candidate_font;entry=entries[key]
    (paper,*materials,ink),r=prepare(key)
    land=ink.copy();land_indices=[]
    for i,name in enumerate(r['colourNames']):
        if name in {'green','white'}:land|=materials[i];land_indices.append(i+1)
    covered=ndi.binary_dilation(land,iterations=4)
    ys,xs=np.nonzero(paper);x0,y0=xs.min(),ys.min()
    factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
    layers=font['COLR'].ColorLayers[entry['glyphName']]
    glyphs=[font['glyf'][entry['glyphName']],*[font['glyf'][layers[i].name] for i in land_indices]]
    components=0
    for index in LAND[key]:
        native=native_land(r['source'],index)
        assert native.any(),(key,index)
        padded=np.pad(native,r['padding'])
        assert (padded&covered).sum()/native.sum()>.95,(key,index)
        labels,n=ndi.label(native)
        for label,sl in enumerate(ndi.find_objects(labels),1):
            sy,sx=sl;local=np.pad(labels[sy,sx]==label,1)
            y,x=np.unravel_index(ndi.distance_transform_edt(local).argmax(),local.shape)
            y+=sy.start-1+r['padding'];x+=sx.start-1+r['padding']
            point=((x-x0)*factor+50,760-(y-y0)*factor)
            found=False
            # Integer font rounding can move a tiny island by half a unit.
            for dx in [-.5,0,.5]:
                for dy in [-.5,0,.5]:
                    for glyph in glyphs:
                        pen=PointInsidePen(font['glyf'],(point[0]+dx,point[1]+dy))
                        glyph.draw(pen,font['glyf'])
                        found|=pen.getResult()
            assert found,(key,index,label,point)
            components+=1
    assert components>=len(LAND[key])
    actual=review_counters(ink,(x0,y0,factor),font['glyf'][entry['glyphName']],max_small_losses=1 if key=='1f30f' else 0)
    assert actual==entry['penTreatment']['fontCounterReview']
    if key=='1f30f':assert actual['largeCountersChecked']==16 and actual['smallCounterLosses']==1
